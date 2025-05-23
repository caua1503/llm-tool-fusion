import pytest
from llm_tool_fusion._utils import extract_docstring, process_tool_calls
import types

# Teste para extract_docstring

def dummy_func(a: int, b: str) -> bool:
    """Soma e concatena
    Args:
        a (int): número
        b (str): texto
    Returns:
        bool
    """
    return True

def test_extract_docstring():
    doc = extract_docstring(dummy_func)
    assert doc['name'] == 'dummy_func'
    assert 'Soma e concatena' in doc['description']
    assert 'a' in doc['parameters']['properties']
    assert doc['parameters']['properties']['a']['type'] == 'int'
    assert 'número' in doc['parameters']['properties']['a']['description']
    assert 'b' in doc['parameters']['properties']
    assert doc['parameters']['properties']['b']['type'] == 'str'
    assert 'texto' in doc['parameters']['properties']['b']['description']

# Teste para process_tool_calls (mock)
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
    called = {}
    def tool_a(x):
        called['a'] = x
        return x + 1
    tool_calls = [DummyToolCall('tool_a', '{"x": 42}')]  # Simula chamada
    response = DummyResponse(tool_calls)
    messages = []
    def llm_call_fn(**kwargs):
        # Simula resposta sem tool_calls para encerrar loop
        return DummyResponse()
    result = process_tool_calls(
        response,
        messages,
        async_tools_name=[],
        available_tools={'tool_a': tool_a},
        model='fake',
        llm_call_fn=llm_call_fn,
        tools=[],
        verbose=False
    )
    assert called['a'] == 42
    assert isinstance(result, DummyResponse) 