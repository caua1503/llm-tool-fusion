from functools import wraps
from typing import Callable, Any, List, Dict
import asyncio
import time
import json
from ._utils import extract_docstring

class ToolCaller:
    def __init__(self):
        self._list_tools = []
        self._async_list_tools = []
        self._tools = []

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
            tool_info = extract_docstring(tools[x])
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
    
    def register_tool(self, function: Callable, tool_type: str = "sync"):
        if tool_type == "sync":
            self._list_tools.append(function)
        elif tool_type == "async":
            self._async_list_tools.append(function)
        else:
            raise ValueError("Invalid tool type. Use 'sync' or 'async'.")
        self._tools.append({
            "type": "function",
            "function": extract_docstring(function)
        })
        
        
def process_tool_calls(
    response: Any, messages: List[Dict[str, Any]],
    async_tools_name: List[str], 
    available_tools: Dict[str, Callable],
    model: str, llm_call_fn: Callable, 
    tools: List[Dict[str, Any]],
    verbose: bool = False,
    verbose_time: bool = False,
    clean_messages: bool = False,
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
        async_tools_name (obrigatorio): lista de nomes de ferramentas assíncronas
        available_tools (obrigatorio): dict nome->função das ferramentas
        model (obrigatorio): nome do modelo
        llm_call_fn (obrigatorio): função que faz a chamada ao modelo (ex: lambda model, messages, tools: ...), como esta na descrição do exemplo
        tools (obrigatorio): lista de ferramentas (no formato OpenAI)
        verbose (opicional): se True, exibe logs detalhados
        verbose_time (opicional): se True, exibe logs de tempo de execução das funções
        clean_messages (opicional): se True, limpa as mensagens após o processamento
        max_chained_calls (opicional): número máximo de chamadas encadeadas permitidas
    Returns:
        Última resposta do modelo após processar todos os tool_calls
    """
    start_time_process = time.time() if verbose_time else None
    chain_count = 0
    
    while True:
        # Verifica se existem tool_calls diretamente
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            if verbose:
                print(f"[LLM] tool_calls detectados: {response.choices[0].message.tool_calls}")
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            
            # Incrementa o contador de chamadas encadeadas
            chain_count += 1
            if chain_count > max_chained_calls:
                if verbose:
                    print(f"[AVISO] Número máximo de chamadas encadeadas atingido: {max_chained_calls}")
                messages.append({
                    "role": "system",
                    "content": f"The maximum number of chained calls ({max_chained_calls}) has been reached. Please provide an answer based on the results obtained so far."
                })
                response = llm_call_fn(model=model, messages=messages, tools=tools)
                continue
            
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    if verbose:
                        print(f"[TOOL] Executando: {tool_name}, Args: {tool_args}")

                    start_time = time.time() if verbose_time else None
                    tool_result = asyncio.run(available_tools[tool_name](**tool_args)) if tool_name in async_tools_name else available_tools[tool_name](**tool_args)
                    
                    if verbose_time:
                        end_time = time.time()
                        print(f"[TOOL] Tempo de execução: {end_time - start_time} segundos")

                    if verbose:
                        print(f"[TOOL] Resultado: {tool_result}")

                except Exception as e:
                    tool_result = f"Erro ao executar tool '{tool_name}': {e}"

                    if verbose:
                        print(f"[ERRO] {tool_result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                })
            response = llm_call_fn(model=model, messages=messages, tools=tools)
        else:
            if verbose:
                print("[LLM] Nenhum tool_call detectado. Fim do processamento.")
                if chain_count > 0:
                    print(f"[INFO] Total de chamadas encadeadas: {chain_count}")
            if verbose_time:
                end_time_process = time.time()
                print(f"[PROCESSO] Tempo de execução total: {end_time_process - start_time_process} segundos")
            if clean_messages:
                response = response.choices[0].message.content
            return response

async def process_tool_calls_async(
    response: Any, 
    messages: List[Dict[str, Any]], 
    async_tools_name: List[str], 
    available_tools: Dict[str, Callable], 
    model: str, 
    llm_call_fn: Callable, 
    tools: List[Dict[str, Any]], 
    verbose: bool = False,
    verbose_time: bool = False,
    clean_messages: bool = False,
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
        async_tools_name: lista de nomes de ferramentas assíncronas
        available_tools: dict nome->função das ferramentas
        model: nome do modelo
        llm_call_fn: função que faz a chamada ao modelo (ex: lambda model, messages, tools: ...), como esta na descrição do exemplo
        tools: lista de ferramentas (no formato OpenAI)
        verbose: se True, exibe logs detalhados
        verbose_time: se True, exibe logs de tempo
        clean_messages: se True, limpa as mensagens após o processamento
        max_chained_calls: número máximo de chamadas encadeadas permitidas
    Returns:
        Última resposta do modelo após processar todos os tool_calls
    """
    start_time_process = time.time() if verbose_time else None
    chain_count = 0
    
    while True:
        # Verifica se existem tool_calls diretamente
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            tool_results = []
            if verbose:
                print(f"[LLM] tool_calls detectados: {response.choices[0].message.tool_calls}")
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            
            # Incrementa o contador de chamadas encadeadas
            chain_count += 1
            if chain_count > max_chained_calls:
                if verbose:
                    print(f"[AVISO] Número máximo de chamadas encadeadas atingido: {max_chained_calls}")
                messages.append({
                    "role": "system",
                    "content": f"O número máximo de chamadas encadeadas ({max_chained_calls}) foi atingido. Por favor, forneça uma resposta baseada nos resultados obtidos até agora."
                })
                response = await llm_call_fn(model=model, messages=messages, tools=tools)
                continue
                
            for tool_call in response.choices[0].message.tool_calls:
                tool_name = tool_call.function.name
                
                try:
                    tool_args = json.loads(tool_call.function.arguments)
                    if verbose:
                        print(f"[TOOL] Executando: {tool_name}, Args: {tool_args}")
                    
                    start_time = time.time() if verbose_time else None
                    tool_result = await available_tools[tool_name](**tool_args) if tool_name in async_tools_name else available_tools[tool_name](**tool_args)

                    if verbose_time:
                        end_time = time.time()
                        print(f"[TOOL] Tempo de execução: {end_time - start_time} segundos")

                    if verbose:
                        print(f"[TOOL] Resultado: {tool_result}")

                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": json.dumps(tool_result),
                    })
                    
                except Exception as e:
                    tool_result = f"Erro ao executar tool '{tool_name}': {e}"

                    if verbose:
                        print(f"[ERRO] {tool_result}")


            messages.extend(tool_results)
            response = await llm_call_fn(model=model, messages=messages, tools=tools)
        else:
            if verbose:
                print("[LLM] Nenhum tool_call detectado. Fim do processamento.")
                if chain_count > 0:
                    print(f"[INFO] Total de chamadas encadeadas: {chain_count}")
            if verbose_time:
                end_time_process = time.time()
                print(f"[PROCESSO] Tempo de execução total: {end_time_process - start_time_process} segundos")
            if clean_messages:
                response = response.choices[0].message.content
            return response        