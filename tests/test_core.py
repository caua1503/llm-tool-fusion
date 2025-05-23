import pytest
from llm_tool_fusion._core import ToolCaller

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