import asyncio
import json
import time
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from ._utils import _extract_docstring, _poll_fuction_async


@dataclass
class ProcessingConfig:
    """Configuration object for tool call processing."""

    verbose: bool = False
    verbose_time: bool = False
    clean_messages: bool = False
    use_async_poll: bool = False
    max_chained_calls: int = 5


class FrameworkConstants:
    """Constants for supported frameworks."""

    OPENAI = "openai"
    OLLAMA = "ollama"
    OTHER = "other"
    SUPPORTED_FRAMEWORKS = [OPENAI, OLLAMA, OTHER]


class ToolCaller:
    def __init__(
        self,
        model: Optional[str] = None,
        framework: Optional[Union[str, FrameworkConstants]] = None,
        config: ProcessingConfig = ProcessingConfig(),
    ):
        self._list_tools = []
        self._async_list_tools = []
        self._tools = []
        self._list_supported_framework = FrameworkConstants.SUPPORTED_FRAMEWORKS
        self._framework = framework
        self._config = config
        self._model = model

        if self._framework is None:
            self._framework = FrameworkConstants.OPENAI

        if self._framework not in FrameworkConstants.SUPPORTED_FRAMEWORKS:
            supported_frameworks = ", ".join(FrameworkConstants.SUPPORTED_FRAMEWORKS)
            raise ValueError(
                f"Invalid framework '{self._framework}'. Use one of the following: {supported_frameworks} or None"
            )

    def tool(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        self._list_tools.append(wrapper)
        return wrapper

    def async_tool(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        self._async_list_tools.append(wrapper)
        return wrapper

    def get_tools(self) -> list[dict]:
        tools = self._list_tools + self._async_list_tools
        self._tools = []
        for tool in tools:
            tool_info = _extract_docstring(tool)
            self._tools.append({"type": "function", "function": tool_info})
        return self._tools

    def get_model(self) -> str:
        if self._model is None:
            raise ValueError("Model not defined, please define a model when creating the ToolCaller instance")
        return self._model

    def get_name_async_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._async_list_tools}

    def get_name_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._list_tools}

    def get_map_tools(self) -> dict[str, Callable]:
        return {f"{func.__name__}": func for func in self._list_tools + self._async_list_tools}

    def register_tool(self, function: Callable):
        self._list_tools.append(function)
        self._tools.append({"type": "function", "function": _extract_docstring(function)})

    def register_tool_async(self, function: Callable):
        self._async_list_tools.append(function)
        self._tools.append({"type": "function", "function": _extract_docstring(function)})

    def register_list_tools(self, list_tools_for_register: List[dict[Callable, str]]):  # type: ignore
        """
        EXEMPLO:

        list_tools_for_register = [{"function": Callable, "type": "sync"},
                                   {"function": Callable, "type": "async"}]
        """
        for tool in list_tools_for_register:
            if tool["type"] == "sync":  # type: ignore
                self.register_tool(tool["function"])  # type: ignore
            elif tool["type"] == "async":  # type: ignore
                self.register_tool_async(tool["function"])  # type: ignore
            else:
                raise ValueError("Invalid tool type. Use 'sync' or 'async'.")

    async def process_tool_calls_async(
        self,
        response: Any,
        messages: List[Dict[str, Any]],
        llm_call_fn: Callable,
        model: Optional[str] = None,
    ) -> Any:  # type: ignore
        """
        Processes tool_calls from an LLM response, executing the required tools and updating the messages.
        Compatible with any framework (OpenAI, Ollama, etc.) as long as a call function (llm_call_fn) is provided.

        Example usage of llm_call_fn:
        llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
            model=model, messages=messages, tools=tools
        )

        Args:
            response: initial model response
            messages: chat message list
            tool_caller: instance of the ToolCaller class
            model: model name
            llm_call_fn: function that makes the model call (e.g., lambda model, messages, tools: ...)
            config (optional): ProcessingConfig object with all settings
            verbose: if True, shows detailed logs (deprecated, use config)
            verbose_time: if True, shows execution time logs (deprecated, use config)
            clean_messages: if True, cleans messages after processing (deprecated, use config)
            use_async_poll: if True, executes asynchronous tools in parallel (deprecated, use config)
            max_chained_calls: maximum number of allowed chained calls (deprecated, use config)
        Returns:
            Last model response after processing all tool_calls
        """

        if self._config.verbose:
            print(f"[PROCESS] Framework: {self._framework}\n")

        if self._framework == FrameworkConstants.OPENAI:
            return await _openai_process_tool_calls_async(
                response=response,
                messages=messages,
                model=model if model is not None else self.get_model(),
                llm_call_fn=llm_call_fn,
                config=self._config,
                tools=self.get_tools(),
                available_tools=self.get_map_tools(),
                async_tools_name=self.get_name_async_tools(),
            )

        elif self._framework == FrameworkConstants.OLLAMA:
            return await _ollama_process_tool_calls_async(
                response=response,
                messages=messages,
                model=model if model is not None else self.get_model(),
                llm_call_fn=llm_call_fn,
                config=self._config,
                tools=self.get_tools(),
                available_tools=self.get_map_tools(),
                async_tools_name=self.get_name_async_tools(),
            )

    def process_tool_calls(
        self,
        response: Any,
        messages: List[Dict[str, Any]],
        llm_call_fn: Callable,
        model: Optional[str] = None,
    ) -> Any:  # type: ignore
        """
        Processes tool_calls from an LLM response, executing the required tools and updating the messages.
        Compatible with any framework (OpenAI, Ollama, etc.) as long as a call function (llm_call_fn) is provided.

        Example usage of llm_call_fn:
        llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
            model=model, messages=messages, tools=tools
        )

        Args:
            response (required): initial model response
            messages  (required): chat message list
            tool_caller (required): instance of the ToolCaller class
            model (required): model name
            llm_call_fn (required): function that makes the model call (e.g., lambda model, messages, tools: ...)
            config (optional): ProcessingConfig object with all settings
            verbose (optional): if True, shows detailed logs (deprecated, use config)
            verbose_time (optional): if True, shows function execution time logs (deprecated, use config)
            clean_messages (optional): if True, cleans messages after processing (deprecated, use config)
            use_async_poll (optional): if True, executes asynchronous tools in parallel (deprecated, use config)
            max_chained_calls (optional): maximum number of allowed chained calls (deprecated, use config)
        Returns:
            Last model response after processing all tool_calls
        """

        if self._config.verbose:
            print(f"[PROCESS] Framework: {self._framework}")

        if self._framework == FrameworkConstants.OPENAI:
            return _openai_process_tool_calls_sync(
                response=response,
                messages=messages,
                model=model if model is not None else self.get_model(),
                llm_call_fn=llm_call_fn,
                config=self._config,
                tools=self.get_tools(),
                available_tools=self.get_map_tools(),
                async_tools_name=self.get_name_async_tools(),
            )

        elif self._framework == FrameworkConstants.OLLAMA:
            return _ollama_process_tool_calls_sync(
                response=response,
                messages=messages,
                model=model if model is not None else self.get_model(),
                llm_call_fn=llm_call_fn,
                config=self._config,
                tools=self.get_tools(),
                available_tools=self.get_map_tools(),
                async_tools_name=self.get_name_async_tools(),
            )


def _openai_process_tool_calls_sync(
    response: Any,
    messages: List[Dict[str, Any]],
    model: str,
    llm_call_fn: Callable,
    config: ProcessingConfig,
    tools: List[Dict],
    available_tools: dict[str, Callable],
    async_tools_name: set[str],
):
    start_time_process = time.time() if config.verbose_time else None
    chain_count = 0

    while True:
        if not hasattr(response.choices[0].message, "tool_calls") or not response.choices[0].message.tool_calls:
            if config.verbose:
                print("[LLM] No tool_calls detected. Processing completed.")
                if chain_count > 0:
                    print(f"[INFO] Total chained calls: {chain_count}")

            if config.verbose_time:
                end_time_process = time.time()
                print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")  # type: ignore

            if config.clean_messages:
                response = response.choices[0].message.content
            return response

        if config.verbose:
            print(f"[LLM] Tool_calls detected: {response.choices[0].message.tool_calls}")
        messages.append({"role": "assistant", "content": response.choices[0].message.content})

        chain_count += 1
        if chain_count > config.max_chained_calls:
            if config.verbose:
                print(f"[WARNING] Maximum number of chained calls reached: {config.max_chained_calls}")
            messages.append({
                "role": "system",
                "content": (
                    f"The maximum number of chained calls ({config.max_chained_calls}) has been reached. "
                    "Please provide an answer based on the results obtained so far."
                ),
            })
            response = llm_call_fn(model=model, messages=messages, tools=tools)
            continue

        async_poll_list = []
        tool_results = []

        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name

            try:
                tool_args = json.loads(tool_call.function.arguments)

                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")

                start_time = time.time() if config.verbose_time else None

                if tool_name in async_tools_name:
                    if config.use_async_poll:
                        async_poll_list.append({"tool_id": tool_call.id, "tool_name": tool_name, "args": tool_args})
                        if config.verbose:
                            print(f"[TOOL] Adding {tool_name} to async_poll_list")
                        continue
                    else:
                        tool_result = asyncio.run(available_tools[tool_name](**tool_args))
                else:
                    tool_result = available_tools[tool_name](**tool_args)

                if config.verbose_time and not config.use_async_poll:
                    end_time = time.time()
                    print(f"[TOOL] Execution time: {end_time - start_time} seconds")  # type: ignore

                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Result: {tool_result}")

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                })

            except Exception as e:
                tool_result = f"Error executing tool '{tool_name}': {e}"

                if config.verbose:
                    print(f"[ERROR] {tool_result}")

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                })

        if config.use_async_poll and async_poll_list:
            if config.verbose:
                print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")

            async_results = asyncio.run(
                _poll_fuction_async(
                    avaliable_tools=available_tools,
                    list_tasks=async_poll_list,  # type: ignore
                    framework="openai",
                )
            )
            tool_results.extend(async_results)

        messages.extend(tool_results)
        response = llm_call_fn(model=model, messages=messages, tools=tools)


def _ollama_process_tool_calls_sync(
    response: Any,
    messages: List[Dict[str, Any]],
    model: str,
    llm_call_fn: Callable,
    config: ProcessingConfig,
    tools: List[Dict],
    available_tools: dict[str, Callable],
    async_tools_name: set[str],
):
    start_time_process = time.time() if config.verbose_time else None
    chain_count = 0

    while True:
        if not response.message.tool_calls:
            if config.verbose:
                print("[LLM] No tool_calls detected. Processing completed.")
                if chain_count > 0:
                    print(f"[INFO] Total chained calls: {chain_count}")

            if config.verbose_time:
                end_time_process = time.time()
                print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")  # type: ignore

            if config.clean_messages:
                return response.message.content

            return response

        if config.verbose:
            print(f"[LLM] Tool_calls detected: {response.message.tool_calls}")

        chain_count += 1
        if chain_count > config.max_chained_calls:  # type: ignore
            if config.verbose:
                print(f"[WARNING] Maximum number of chained calls reached: {config.max_chained_calls}")
            messages.append({
                "role": "system",
                "content": (
                    f"The maximum number of chained calls ({config.max_chained_calls}) has been reached. "
                    "Please provide an answer based on the results obtained so far."
                ),
            })
            response = llm_call_fn(model=model, messages=messages, tools=tools)
            continue

        async_poll_list = []
        tools_results = []

        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = tool_call.function.arguments
                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")

                start_time = time.time() if config.verbose_time else None

                if tool_name in async_tools_name:
                    if config.use_async_poll:
                        async_poll_list.append({"tool_name": tool_name, "args": tool_args})
                        if config.verbose:
                            print(f"[TOOL] Adding {tool_name} to async_poll_list")
                        continue
                    else:
                        tool_result = asyncio.run(available_tools[tool_name](**tool_args))
                else:
                    tool_result = available_tools[tool_name](**tool_args)

                if config.verbose_time and not config.use_async_poll:
                    end_time = time.time()
                    print(f"[TOOL] Execution time: {end_time - start_time} seconds")  # type: ignore

                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Result: {tool_result}")

                tools_results.append({"role": "tool", "content": str(tool_result), "name": tool_name})

            except Exception as e:
                tool_result = f"Error executing tool '{tool_name}': {e}"

                if config.verbose:
                    print(f"[ERROR] {tool_result}")

                tools_results.append({"role": "tool", "content": str(tool_result), "name": tool_name})

        if config.use_async_poll and async_poll_list:
            if config.verbose:
                print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")

            async_results = asyncio.run(
                _poll_fuction_async(
                    avaliable_tools=available_tools,
                    list_tasks=async_poll_list,  # type: ignore
                    framework="ollama",
                )
            )
            tools_results.extend(async_results)

        messages.append(response.message)
        messages.extend(tools_results)
        response = llm_call_fn(model=model, messages=messages, tools=tools)


async def _openai_process_tool_calls_async(
    response: Any,
    messages: List[Dict[str, Any]],
    model: str,
    llm_call_fn: Callable,
    config: ProcessingConfig,
    tools: List[Dict],
    available_tools: dict[str, Callable],
    async_tools_name: set[str],
):
    start_time_process = time.time() if config.verbose_time else None
    chain_count = 0

    if config.use_async_poll:
        async_poll_list = []

    while True:
        if not hasattr(response.choices[0].message, "tool_calls") or not response.choices[0].message.tool_calls:
            if config.verbose:
                print("[LLM] No tool_calls detected. Processing completed.")
                if chain_count > 0:
                    print(f"[INFO] Total chained calls: {chain_count}")

            if config.verbose_time:
                end_time_process = time.time()
                print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")  # type: ignore

            if config.clean_messages:
                response = response.choices[0].message.content
            return response

        if config.verbose:
            print(f"[LLM] Tool_calls detected: {response.choices[0].message.tool_calls}\n")
        messages.append({"role": "assistant", "content": response.choices[0].message.content})

        chain_count += 1
        if chain_count > config.max_chained_calls:  # type: ignore
            if config.verbose:
                print(f"[WARNING] Maximum number of chained calls reached: {config.max_chained_calls}\n")
            messages.append({
                "role": "system",
                "content": (
                    f"The maximum number of chained calls ({config.max_chained_calls}) has been reached. "
                    "Please provide an answer based on the results obtained so far."
                ),
            })
            response = await llm_call_fn(model=model, messages=messages, tools=tools)
            continue

        tool_results = []
        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")

                start_time = time.time() if config.verbose_time else None

                if tool_name in async_tools_name:
                    if config.use_async_poll:
                        async_poll_list.append({"tool_id": tool_call.id, "tool_name": tool_name, "args": tool_args})
                        if config.verbose:
                            print(f"[TOOL] Adding {tool_name} to async_poll_list")
                        continue
                    else:
                        tool_result = await available_tools[tool_name](**tool_args)
                else:
                    tool_result = available_tools[tool_name](**tool_args)

                if config.verbose_time and not config.use_async_poll:
                    end_time = time.time()
                    print(f"[TOOL] Execution time: {end_time - start_time} seconds")  # type: ignore

                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Result: {tool_result}")

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                })

            except Exception as e:
                tool_result = f"Error executing tool '{tool_name}': {e}"

                if config.verbose:
                    print(f"[ERROR] {tool_result}")

                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                })

        messages.extend(tool_results)

        if config.use_async_poll and async_poll_list:
            if config.verbose:
                print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")

            async_results = await _poll_fuction_async(
                avaliable_tools=available_tools,
                list_tasks=async_poll_list,  # type: ignore
                framework="openai",
            )
            messages.extend(async_results)

        response = await llm_call_fn(model=model, messages=messages, tools=tools)


async def _ollama_process_tool_calls_async(
    response: Any,
    messages: List[Dict[str, Any]],
    model: str,
    llm_call_fn: Callable,
    config: ProcessingConfig,
    tools: List[Dict],
    available_tools: dict[str, Callable],
    async_tools_name: set[str],
):
    start_time_process = time.time() if config.verbose_time else None
    chain_count = 0

    if config.use_async_poll:
        async_poll_list = []

    while True:
        if not response.message.tool_calls:
            if config.verbose:
                print("[LLM] No tool_calls detected. Processing completed.")
                if chain_count > 0:
                    print(f"[INFO] Total chained calls: {chain_count}")

            if config.verbose_time:
                end_time_process = time.time()
                print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")  # type: ignore

            if config.clean_messages:
                return response.message.content

            return response

        if config.verbose:
            print(f"[LLM] Tool_calls detected: {response.message.tool_calls}")

        chain_count += 1
        if chain_count > config.max_chained_calls:  # type: ignore
            if config.verbose:
                print(f"[WARNING] Maximum number of chained calls reached: {config.max_chained_calls}")
            messages.append({
                "role": "system",
                "content": (
                    f"The maximum number of chained calls ({config.max_chained_calls}) has been reached. "
                    "Please provide an answer based on the results obtained so far."
                ),
            })
            response = await llm_call_fn(model=model, messages=messages, tools=tools)
            continue

        async_poll_list = []
        tool_results = []

        for tool_call in response.message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = tool_call.function.arguments
                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")

                start_time = time.time() if config.verbose_time else None

                if tool_name in async_tools_name:
                    if config.use_async_poll:
                        async_poll_list.append({"tool_name": tool_name, "args": tool_args})
                        if config.verbose:
                            print(f"[TOOL] Adding {tool_name} to async_poll_list")
                        continue
                    else:
                        tool_result = await available_tools[tool_name](**tool_args)
                else:
                    tool_result = available_tools[tool_name](**tool_args)

                if config.verbose_time and not config.use_async_poll:
                    end_time = time.time()
                    print(f"[TOOL] Execution time: {end_time - start_time} seconds")  # type: ignore

                if config.verbose and not config.use_async_poll:
                    print(f"[TOOL] Result: {tool_result}")

                tool_results.append({"role": "tool", "content": str(tool_result), "name": tool_name})

            except Exception as e:
                tool_result = f"Error executing tool '{tool_name}': {e}"

                if config.verbose:
                    print(f"[ERROR] {tool_result}")

                tool_results.append({"role": "tool", "content": str(tool_result), "name": tool_name})

        if config.use_async_poll and async_poll_list:
            if config.verbose:
                print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")

            async_results = await _poll_fuction_async(
                avaliable_tools=available_tools,
                list_tasks=async_poll_list,  # type: ignore
                framework="ollama",
            )
            tool_results.extend(async_results)

        messages.append(response.message)
        messages.extend(tool_results)
        response = await llm_call_fn(model=model, messages=messages, tools=tools)
