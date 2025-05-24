import json
import re
from typing import Callable, Any, Optional, Dict, List, Union
import asyncio
import time

def extract_docstring(func: Callable) -> Dict[str, Any]:
    """
    Extrai informações de descrição e parâmetros de uma docstring.

    Args:
        func: Função da qual a docstring será extraída.

    Returns:
        dict: Dicionário contendo name, description e parameters em formato JSON Schema.
    """
    doc = func.__doc__
    func_name = func.__name__
    
    if not doc:
        return {
            "name": func_name,
            "description": "",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }

    # Inicializa a estrutura do resultado
    result = {
        "name": func_name,
        "description": "",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }

    # Divide a docstring em linhas
    lines = doc.strip().split('\n')
    current_section = "description"
    param_name = None

    # Regex para identificar seções
    param_pattern = re.compile(r'^\s*(Args|Parameters):\s*$')
    return_pattern = re.compile(r'^\s*(Returns|Return):\s*$')
    param_def_pattern = re.compile(r'^\s*(\w+)\s*[:(]([^):]*)[):]?\s*:?\s*(.*)$')

    for line in lines:
        line = line.strip()

        # Verifica se é seção de parâmetros
        if param_pattern.match(line):
            current_section = "parameters"
            continue
        # Verifica se é seção de retorno
        elif return_pattern.match(line):
            current_section = "returns"
            continue

        # Processa linhas com base na seção atual
        if current_section == "description":
            if line:
                result["description"] += line + " "
        elif current_section == "parameters":
            param_match = param_def_pattern.match(line)
            if param_match:
                param_name, param_type, param_desc = param_match.groups()
                param_type = param_type.strip() if param_type else "string"
                result["parameters"]["properties"][param_name] = {
                    "type": param_type,
                    "description": param_desc.strip()
                }
            elif param_name and line:  # Continuação da descrição do parâmetro
                result["parameters"]["properties"][param_name]["description"] += " " + line
        # Ignora seção returns

    # Limpa espaços extras
    result["description"] = result["description"].strip()
    for param in result["parameters"]["properties"]:
        result["parameters"]["properties"][param]["description"] = result["parameters"]["properties"][param]["description"].strip()

    return result

def process_tool_calls(
    response: Any, messages: List[Dict[str, Any]],
    async_tools_name: List[str], 
    available_tools: Dict[str, Callable],
    model: str, llm_call_fn: Callable, 
    tools: List[Dict[str, Any]], 
    verbose: bool = False,
    verbose_time: bool = False,
    clean_messages: bool = False
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
    Returns:
        Última resposta do modelo após processar todos os tool_calls
    """
    start_time_process = time.time() if verbose_time else None
    while True:
        tool_calls = getattr(response.choices[0].message, 'tool_calls', None)
        if tool_calls:
            if verbose:
                print(f"[LLM] tool_calls detectados: {tool_calls}")
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            
            for tool_call in tool_calls:
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
    clean_messages: bool = False
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
    Returns:
        Última resposta do modelo após processar todos os tool_calls
    """
    start_time_process = time.time() if verbose_time else None
    while True:
        tool_calls = getattr(response.choices[0].message, 'tool_calls', None)
        if tool_calls:
            if verbose:
                print(f"[LLM] tool_calls detectados: {tool_calls}")
            messages.append({"role": "assistant", "content": response.choices[0].message.content})
            for tool_call in tool_calls:
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

            response = await llm_call_fn(model=model, messages=messages, tools=tools)
        else:
            if verbose:
                print("[LLM] Nenhum tool_call detectado. Fim do processamento.")
            if verbose_time:
                end_time_process = time.time()
                print(f"[PROCESSO] Tempo de execução total: {end_time_process - start_time_process} segundos")
            if clean_messages:
                response = response.choices[0].message.content
            return response
