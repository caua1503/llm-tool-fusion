import os
import sys
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from llm_tool_fusion._core import ToolCaller, process_tool_calls
import types
import json

def test_tool_registration_and_listing():
    caller = ToolCaller()

    @caller.tool
    def foo(x: int) -> int:
        """Soma 1 ao valor
        Args:
            x (int): valor de entrada
        Returns:
            int
        """
        return x + 1

    @caller.async_tool
    def bar(y: int) -> int:
        """Multiplica por 2
        Args:
            y (int): valor de entrada
        Returns:
            int
        """
        return y * 2

    # Testa nomes
    assert 'foo' in caller.get_name_tools()
    assert 'bar' in caller.get_name_async_tools()

    # Testa mapeamento
    tool_map = caller.get_map_tools()
    assert callable(tool_map['foo'])
    assert callable(tool_map['bar'])
    assert tool_map['foo'](2) == 3
    assert tool_map['bar'](3) == 6

    # Testa get_tools (estrutura do dicionário)
    tools = caller.get_tools()
    assert isinstance(tools, list)
    assert any(t['function']['name'] == 'foo' for t in tools)
    assert any(t['function']['name'] == 'bar' for t in tools)

    # Testa registro manual
    def baz(z: int) -> int:
        """Triplica
        Args:
            z (int): valor
        Returns:
            int
        """
        return z * 3
    caller.register_tool(baz, tool_type="sync")
    assert 'baz' in caller.get_name_tools()
    assert caller.get_map_tools()['baz'](4) == 12

def test_invalid_tool_type():
    caller = ToolCaller()
    
    def invalid_tool(x: int) -> int:
        """Ferramenta de teste
        Args:
            x (int): valor
        Returns:
            int
        """
        return x
    
    with pytest.raises(ValueError):
        caller.register_tool(invalid_tool, tool_type="invalid_type")

def test_get_methods_return_types():
    caller = ToolCaller()
    
    @caller.tool
    def sync_tool(x: int) -> int:
        """Ferramenta síncrona
        Args:
            x (int): valor
        Returns:
            int
        """
        return x
    
    @caller.async_tool
    def async_tool(y: int) -> int:
        """Ferramenta assíncrona
        Args:
            y (int): valor
        Returns:
            int
        """
        return y
    
    # Verifica tipo de retorno de get_name_tools
    sync_tools = caller.get_name_tools()
    assert isinstance(sync_tools, set)
    assert 'sync_tool' in sync_tools
    
    # Verifica tipo de retorno de get_name_async_tools
    async_tools = caller.get_name_async_tools()
    assert isinstance(async_tools, set)
    assert 'async_tool' in async_tools
    
    # Verifica tipo de retorno de get_map_tools
    tools_map = caller.get_map_tools()
    assert isinstance(tools_map, dict)
    assert 'sync_tool' in tools_map
    assert 'async_tool' in tools_map
    assert callable(tools_map['sync_tool'])
    assert callable(tools_map['async_tool'])

# --- Adicionados: testes de process_tool_calls ---

class DummyResponse:
    class Choice:
        class Message:
            def __init__(self, tool_calls=None, content="resp"):
                self.tool_calls = tool_calls
                self.content = content
        def __init__(self, tool_calls=None):
            self.message = DummyResponse.Choice.Message(tool_calls)
    def __init__(self, tool_calls=None):
        self.choices = [DummyResponse.Choice(tool_calls)]

class DummyToolCall:
    def __init__(self, name, args, id="id1"):
        self.function = types.SimpleNamespace(name=name, arguments=args)
        self.id = id

def test_process_tool_calls_executes_tools():
    # Cria uma instância de ToolCaller e registra a ferramenta
    caller = ToolCaller()
    called = {}
    
    def tool_a(x):
        called['a'] = x
        return x + 1
    
    caller.register_tool(tool_a, tool_type="sync")
    
    tool_calls = [DummyToolCall('tool_a', '{"x": 42}')]  # Simula chamada
    response = DummyResponse(tool_calls)
    messages = []
    def llm_call_fn(**kwargs):
        # Simula resposta sem tool_calls para encerrar loop
        return DummyResponse()
    result = process_tool_calls(
        response,
        messages,
        caller,
        model='fake',
        llm_call_fn=llm_call_fn,
        verbose=False
    )
    assert called['a'] == 42
    assert isinstance(result, DummyResponse)

def test_process_tool_calls_clean_messages():
    # Cria uma instância de ToolCaller e registra a ferramenta
    caller = ToolCaller()
    
    def tool_a(x):
        return x + 1
    
    caller.register_tool(tool_a, tool_type="sync")
    
    tool_calls = [DummyToolCall('tool_a', '{"x": 42}')]
    response = DummyResponse(tool_calls)
    messages = []
    def llm_call_fn(**kwargs):
        result = DummyResponse()
        result.choices[0].message.content = "Final response"
        return result
    
    result = process_tool_calls(
        response,
        messages,
        caller,
        model='fake',
        llm_call_fn=llm_call_fn,
        verbose=False,
        clean_messages=True
    )
    
    # Com clean_messages=True, deve retornar o conteúdo da mensagem, não o objeto
    assert result == "Final response"

def test_process_tool_calls_max_chained_calls():
    # Cria uma instância de ToolCaller e registra a ferramenta
    caller = ToolCaller()
    call_count = 0
    
    def tool_a(x):
        return x + 1
    
    caller.register_tool(tool_a, tool_type="sync")
    
    # Criar uma função que sempre retorna tool_calls por 3 vezes, depois retorna sem tool_calls
    def llm_call_fn(**kwargs):
        nonlocal call_count
        call_count += 1
        if call_count <= 3:  # Primeiras 3 chamadas retornam tool_calls
            return DummyResponse([DummyToolCall('tool_a', '{"x": 42}')])
        return DummyResponse()  # Quarta chamada não tem tool_calls
    
    response = DummyResponse([DummyToolCall('tool_a', '{"x": 42}')])
    messages = []
    
    result = process_tool_calls(
        response,
        messages,
        caller,
        model='fake',
        llm_call_fn=llm_call_fn,
        verbose=False,
        max_chained_calls=2  # Limite definido para 2 chamadas
    )
    
    # Verifica se alguma mensagem de sistema sobre limite de chamadas foi adicionada
    assert any("maximum number of chained calls" in msg.get('content', '') 
               for msg in messages if msg.get('role') == 'system')
    assert isinstance(result, DummyResponse)

def test_process_tool_calls_tool_error():
    # Cria uma instância de ToolCaller e registra a ferramenta
    caller = ToolCaller()
    error_message = "Erro de teste"
    
    def failing_tool(x):
        raise Exception(error_message)
    
    caller.register_tool(failing_tool, tool_type="sync")
    
    tool_calls = [DummyToolCall('failing_tool', '{"x": 42}')]
    response = DummyResponse(tool_calls)
    messages = []
    
    def llm_call_fn(**kwargs):
        # Verifica se o conteúdo da mensagem de ferramenta contém o erro
        tool_messages = [msg for msg in kwargs['messages'] if msg.get('role') == 'tool']
        if tool_messages:
            content = json.loads(tool_messages[0]['content'])
            # Se o conteúdo contém o erro, retorna resposta sem tool_calls
            if error_message in content:
                return DummyResponse()
        # Caso contrário, continua gerando tool_calls
        return DummyResponse(tool_calls)
    
    result = process_tool_calls(
        response,
        messages,
        caller,
        model='fake',
        llm_call_fn=llm_call_fn,
        verbose=False
    )
    
    # Verifica se a mensagem de erro foi incluída nas mensagens
    tool_messages = [msg for msg in messages if msg.get('role') == 'tool']
    assert len(tool_messages) > 0
    error_content = json.loads(tool_messages[0]['content'])
    assert error_message in error_content
    assert isinstance(result, DummyResponse) 