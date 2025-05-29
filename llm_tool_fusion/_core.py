from functools import wraps
from typing import Callable, Any, List, Dict
import asyncio
import time
import json
from ._utils import _extract_docstring, _poll_fuction_async

class ToolCaller:
    def __init__(self, framework: str = None):
        self._list_tools = []
        self._async_list_tools = []
        self._tools = []
        self._list_supported_framework = ["openai", "ollama"]
        self._framework = framework

        if self._framework == None:
            self._framework = "openai"

        if self._framework not in self._list_supported_framework:
            supported_frameworks = ", ".join(self._list_supported_framework)
            raise ValueError(f"Invalid framework. Use one of the following: {supported_frameworks} or None")
        
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

    def get_tools(self) -> list[str]:
        x = 0
        tools = self._list_tools + self._async_list_tools
        self._tools = []
        for tool in tools:
            tool_info = _extract_docstring(tools[x])
            self._tools.append({
                "type": "function",
                "function": tool_info
            })
            x += 1
        return self._tools

    def get_name_async_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._async_list_tools}
    
    def get_name_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._list_tools}
    
    def get_map_tools(self) -> dict[str, Callable]:
        return {f"{func.__name__}": func for func in self._list_tools + self._async_list_tools}
    
    def register_tool(self, function: Callable):
        self._list_tools.append(function)
        self._tools.append({
            "type": "function",
            "function": _extract_docstring(function)
        })
    
    def register_tool_async(self, function: Callable):
        self._async_list_tools.append(function)
        self._tools.append({
            "type": "function",
            "function": _extract_docstring(function)
        })
    def register_list_tools(self, list_tools_for_register: List[dict]):
        """
        EXEMPLO:
        
        list_tools_for_register = [{"function": Callable, "type": "sync"}, 
                                   {"function": Callable, "type": "async"}]
        """
        for tool in list_tools_for_register:
            if tool["type"] == "sync":
                self.register_tool(tool["function"])
            elif tool["type"] == "async":
                self.register_tool_async(tool["function"])
            else:
                raise ValueError("Invalid tool type. Use 'sync' or 'async'.")
            

    def get_framework(self) -> str:
        return self._framework
        
        
def process_tool_calls(
    response: Any, 
    messages: List[Dict[str, Any]],
    tool_caller: ToolCaller,
    model: str, llm_call_fn: Callable, 
    verbose: bool = False,
    verbose_time: bool = False,
    clean_messages: bool = False,
    use_async_poll: bool = False,
    max_chained_calls: int = 5
    ) -> List[Dict[str, Any]]:
    """
    Processa tool_calls de uma resposta de LLM, executando as ferramentas necessárias e atualizando as mensagens.
    Compatível com qualquer framework (OpenAI, LangChain, Ollama, etc.) desde que forneça uma função de chamada (llm_call_fn).

    Exemplo do uso de llm_call_fn:
    llm_call_fn = lambda model, messages, tools: client.chat.completions.create(model=model, messages=messages, tools=tools)

    Args:
        response (obrigatorio): resposta inicial do modelo
        messages  (obrigatorio): lista de mensagens do chat
        tool_caller (obrigatorio): instância da classe ToolCaller
        model (obrigatorio): nome do modelo
        llm_call_fn (obrigatorio): função que faz a chamada ao modelo (ex: lambda model, messages, tools: ...), como esta na descrição do exemplo
        verbose (opicional): se True, exibe logs detalhados
        verbose_time (opicional): se True, exibe logs de tempo de execução das funções
        clean_messages (opicional): se True, limpa as mensagens após o processamento
        use_async_poll (opicional): se True, executa as ferramentas assíncronas em paralelo
        max_chained_calls (opicional): número máximo de chamadas encadeadas permitidas
    Returns:
        Última resposta do modelo após processar todos os tool_calls
    """
    tools = tool_caller.get_tools()
    framework = tool_caller.get_framework()
    available_tools = tool_caller.get_map_tools()
    async_tools_name = tool_caller.get_name_async_tools()

    start_time_process = time.time() if verbose_time else None
    chain_count = 0

    if verbose:
        print(f"[PROCESS] Framework: {framework}")

    if framework == "openai":
        while True:
            if not hasattr(response.choices[0].message, 'tool_calls') or not response.choices[0].message.tool_calls:
                if verbose:
                    print("[LLM] No tool_calls detected. Processing completed.")
                    if chain_count > 0:
                        print(f"[INFO] Total chained calls: {chain_count}")
                
                if verbose_time:
                    end_time_process = time.time()
                    print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")
                
                if clean_messages:
                    response = response.choices[0].message.content
                return response
                
            if verbose:
                print(f"[LLM] Tool_calls detected: {response.choices[0].message.tool_calls}")
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            
            # Incrementa o contador de chamadas encadeadas
            chain_count += 1
            if chain_count > max_chained_calls:
                if verbose:
                    print(f"[WARNING] Maximum number of chained calls reached: {max_chained_calls}")
                messages.append({
                    "role": "system",
                    "content": f"The maximum number of chained calls ({max_chained_calls}) has been reached. Please provide an answer based on the results obtained so far."
                })
                response = llm_call_fn(model=model, messages=messages, tools=tools)
                continue
            
            # Lista para armazenar ferramentas assíncronas quando use_async_poll=True
            async_poll_list = []
            tool_results = []
            
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if verbose and not use_async_poll:
                        print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")

                    start_time = time.time() if verbose_time else None
                    
                    if tool_name in async_tools_name:
                        if use_async_poll:
                            # Armazena para execução em paralelo
                            async_poll_list.append({
                                "tool_id": tool_call.id,
                                "tool_name": tool_name,
                                "args": tool_args
                            })
                            if verbose:
                                print(f"[TOOL] Adding {tool_name} to async_poll_list")
                            continue
                        else:
                            # Executa individualmente
                            tool_result = asyncio.run(available_tools[tool_name](**tool_args))
                    else:
                        # Executa ferramenta síncrona
                        tool_result = available_tools[tool_name](**tool_args)
                    
                    if verbose_time and not use_async_poll:
                        end_time = time.time()
                        print(f"[TOOL] Execution time: {end_time - start_time} seconds")

                    if verbose and not use_async_poll:
                        print(f"[TOOL] Result: {tool_result}")

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                    })

                except Exception as e:
                    tool_result = f"Error executing tool '{tool_name}': {e}"

                    if verbose:
                        print(f"[ERROR] {tool_result}")

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                    })
            
            # Executa ferramentas assíncronas em paralelo se use_async_poll=True
            if use_async_poll and async_poll_list:
                if verbose:
                    print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")
                
                async_results = asyncio.run(_poll_fuction_async(
                    avaliable_tools=available_tools, 
                    list_tasks=async_poll_list, 
                    framework=framework
                ))
                tool_results.extend(async_results)
            
            messages.extend(tool_results)
            response = llm_call_fn(model=model, messages=messages, tools=tools)

    elif framework == "ollama":
        while True:
            if not response.message.tool_calls:
                if verbose:
                    print("[LLM] No tool_calls detected. Processing completed.")
                    if chain_count > 0:
                        print(f"[INFO] Total chained calls: {chain_count}")
                
                if verbose_time:
                    end_time_process = time.time()
                    print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")
                
                if clean_messages:
                    return response.message.content
                
                return response

            if verbose:
                print(f"[LLM] Tool_calls detected: {response.message.tool_calls}")
            
            # Incrementa o contador de chamadas encadeadas
            chain_count += 1
            if chain_count > max_chained_calls:
                if verbose:
                    print(f"[WARNING] Maximum number of chained calls reached: {max_chained_calls}")
                messages.append({
                    "role": "system",
                    "content": f"The maximum number of chained calls ({max_chained_calls}) has been reached. Please provide an answer based on the results obtained so far."
                })
                response = llm_call_fn(model=model, messages=messages, tools=tools)
                continue

            # Lista para armazenar ferramentas assíncronas quando use_async_poll=True
            async_poll_list = []
            tools_results = []
            
            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = tool_call.function.arguments
                    if verbose and not use_async_poll:
                        print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")
                    
                    start_time = time.time() if verbose_time else None
                    
                    if tool_name in async_tools_name:
                        if use_async_poll:
                            # Armazena para execução em paralelo
                            async_poll_list.append({
                                "tool_name": tool_name,
                                "args": tool_args
                            })
                            if verbose:
                                print(f"[TOOL] Adding {tool_name} to async_poll_list")
                            continue
                        else:
                            # Executa individualmente
                            tool_result = asyncio.run(available_tools[tool_name](**tool_args))
                    else:
                        # Executa ferramenta síncrona
                        tool_result = available_tools[tool_name](**tool_args)

                    if verbose_time and not use_async_poll:
                        end_time = time.time()
                        print(f"[TOOL] Execution time: {end_time - start_time} seconds")

                    if verbose and not use_async_poll:
                        print(f"[TOOL] Result: {tool_result}")

                    tools_results.append({
                        "role": "tool", 
                        "content": str(tool_result), 
                        "name": tool_name
                    })

                except Exception as e:
                    tool_result = f"Error executing tool '{tool_name}': {e}"

                    if verbose:
                        print(f"[ERROR] {tool_result}")

                    tools_results.append({
                        "role": "tool", 
                        "content": str(tool_result), 
                        "name": tool_name
                    })
            
            # Executa ferramentas assíncronas em paralelo se use_async_poll=True
            if use_async_poll and async_poll_list:
                if verbose:
                    print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")
                
                async_results = asyncio.run(_poll_fuction_async(
                    avaliable_tools=available_tools, 
                    list_tasks=async_poll_list, 
                    framework=framework
                ))
                tools_results.extend(async_results)

            messages.append(response.message)
            messages.extend(tools_results)
            response = llm_call_fn(model=model, messages=messages, tools=tools)

async def process_tool_calls_async(
    response: Any, 
    messages: List[Dict[str, Any]], 
    tool_caller: ToolCaller,
    model: str, 
    llm_call_fn: Callable, 
    verbose: bool = False,
    verbose_time: bool = False,
    clean_messages: bool = False,
    use_async_poll: bool = False,
    max_chained_calls: int = 5
    ) -> List[Dict[str, Any]]:
    """
    Processa tool_calls de uma resposta de LLM, executando as ferramentas necessárias e atualizando as mensagens.
    Compatível com qualquer framework (OpenAI, LangChain, Ollama, etc.) desde que forneça uma função de chamada (llm_call_fn).

    Exemplo do uso de llm_call_fn:
    llm_call_fn = lambda model, messages, tools: client.chat.completions.create(model=model, messages=messages, tools=tools)

    Args:
        response: resposta inicial do modelo
        messages: lista de mensagens do chat
        tool_caller: instância da classe ToolCaller
        model: nome do modelo
        llm_call_fn: função que faz a chamada ao modelo (ex: lambda model, messages, tools: ...), como esta na descrição do exemplo
        verbose: se True, exibe logs detalhados
        verbose_time: se True, exibe logs de tempo
        clean_messages: se True, limpa as mensagens após o processamento
        max_chained_calls: número máximo de chamadas encadeadas permitidas
    Returns:
        Última resposta do modelo após processar todos os tool_calls
    """
    tools = tool_caller.get_tools()
    framework = tool_caller.get_framework()
    available_tools = tool_caller.get_map_tools()
    async_tools_name = tool_caller.get_name_async_tools()

    start_time_process = time.time() if verbose_time else None
    chain_count = 0

    if use_async_poll:
        async_poll_list = []

    if verbose:
        print(f"[PROCESS] Framework: {framework}\n")

    if framework == "openai":
        while True:
            if not hasattr(response.choices[0].message, 'tool_calls') or not response.choices[0].message.tool_calls:
                if verbose:
                    print("[LLM] No tool_calls detected. Processing completed.")
                    if chain_count > 0:
                        print(f"[INFO] Total chained calls: {chain_count}")
                
                if verbose_time:
                    end_time_process = time.time()
                    print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")
                
                if clean_messages:
                    response = response.choices[0].message.content
                return response

            if verbose:
                print(f"[LLM] Tool_calls detected: {response.choices[0].message.tool_calls}\n")
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            
            # Incrementa o contador de chamadas encadeadas
            chain_count += 1
            if chain_count > max_chained_calls:
                if verbose:
                    print(f"[WARNING] Maximum number of chained calls reached: {max_chained_calls}\n")
                messages.append({
                    "role": "system",
                    "content": f"The maximum number of chained calls ({max_chained_calls}) has been reached. Please provide an answer based on the results obtained so far."
                })
                response = await llm_call_fn(model=model, messages=messages, tools=tools)
                continue

            tool_results = []
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                    if verbose and not use_async_poll:
                        print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")
                    
                    start_time = time.time() if verbose_time else None
                    
                    if tool_name in async_tools_name:
                        if use_async_poll:
                            # Armazena para execução em paralelo
                            async_poll_list.append({
                                "tool_id": tool_call.id,
                                "tool_name": tool_name,
                                "args": tool_args
                            })
                            if verbose:
                                print(f"[TOOL] Adding {tool_name} to async_poll_list")
                            continue
                        else:
                            # Executa individualmente
                            tool_result = await available_tools[tool_name](**tool_args)
                    else:
                        # Executa ferramenta síncrona
                        tool_result = available_tools[tool_name](**tool_args)

                    if verbose_time and not use_async_poll:
                        end_time = time.time()
                        print(f"[TOOL] Execution time: {end_time - start_time} seconds")

                    if verbose and not use_async_poll:
                        print(f"[TOOL] Result: {tool_result}")

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                    })

                except Exception as e:
                    tool_result = f"Error executing tool '{tool_name}': {e}"

                    if verbose:
                        print(f"[ERROR] {tool_result}")

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                    })

            messages.extend(tool_results)
            
            # Executa ferramentas assíncronas em paralelo se use_async_poll=True
            if use_async_poll and async_poll_list:
                if verbose:
                    print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")
                
                async_results = await _poll_fuction_async(
                    avaliable_tools=available_tools, 
                    list_tasks=async_poll_list, 
                    framework=framework
                )
                messages.extend(async_results)
            
            response = await llm_call_fn(model=model, messages=messages, tools=tools)

    elif framework == "ollama":
        while True:
            if not response.message.tool_calls:
                if verbose:
                    print("[LLM] No tool_calls detected. Processing completed.")
                    if chain_count > 0:
                        print(f"[INFO] Total chained calls: {chain_count}")
                
                if verbose_time:
                    end_time_process = time.time()
                    print(f"[PROCESS] Total execution time: {end_time_process - start_time_process} seconds")
                
                if clean_messages:
                    return response.message.content
                
                return response

            if verbose:
                print(f"[LLM] Tool_calls detected: {response.message.tool_calls}")
            
            # Incrementa o contador de chamadas encadeadas
            chain_count += 1
            if chain_count > max_chained_calls:
                if verbose:
                    print(f"[WARNING] Maximum number of chained calls reached: {max_chained_calls}")
                messages.append({
                    "role": "system",
                    "content": f"The maximum number of chained calls ({max_chained_calls}) has been reached. Please provide an answer based on the results obtained so far."
                })
                response = await llm_call_fn(model=model, messages=messages, tools=tools)
                continue

            # Lista para armazenar ferramentas assíncronas quando use_async_poll=True
            async_poll_list = []
            tool_results = []
            
            for tool_call in response.message.tool_calls:
                tool_name = tool_call.function.name
                try:
                    tool_args = tool_call.function.arguments
                    if verbose and not use_async_poll:
                        print(f"[TOOL] Executing: {tool_name}, Args: {tool_args}")
                    
                    start_time = time.time() if verbose_time else None
                    
                    if tool_name in async_tools_name:
                        if use_async_poll:
                            # Armazena para execução em paralelo
                            async_poll_list.append({
                                "tool_name": tool_name,
                                "args": tool_args
                            })
                            if verbose:
                                print(f"[TOOL] Adding {tool_name} to async_poll_list")
                            continue
                        else:
                            # Executa individualmente
                            tool_result = await available_tools[tool_name](**tool_args)
                    else:
                        # Executa ferramenta síncrona
                        tool_result = available_tools[tool_name](**tool_args)

                    if verbose_time and not use_async_poll:
                        end_time = time.time()
                        print(f"[TOOL] Execution time: {end_time - start_time} seconds")

                    if verbose and not use_async_poll:
                        print(f"[TOOL] Result: {tool_result}")

                    tool_results.append({
                        "role": "tool", 
                        "content": str(tool_result), 
                        "name": tool_name
                    })

                except Exception as e:
                    tool_result = f"Error executing tool '{tool_name}': {e}"

                    if verbose:
                        print(f"[ERROR] {tool_result}")

                    tool_results.append({
                        "role": "tool", 
                        "content": str(tool_result), 
                        "name": tool_name
                    })
            
            # Executa ferramentas assíncronas em paralelo se use_async_poll=True
            if use_async_poll and async_poll_list:
                if verbose:
                    print(f"[PROCESS] Executing {len(async_poll_list)} async tools in parallel")
                
                async_results = await _poll_fuction_async(
                    avaliable_tools=available_tools, 
                    list_tasks=async_poll_list, 
                    framework=framework
                )
                tool_results.extend(async_results)

            messages.append(response.message)
            messages.extend(tool_results)
            response = await llm_call_fn(model=model, messages=messages, tools=tools)
