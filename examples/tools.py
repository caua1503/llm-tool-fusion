import sys
import os
import json
# Adiciona o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_tool_fusion import ToolCaller

main = ToolCaller()

@main.tool
def minha_ferramenta(parametro: str, outro_parametro: int) -> str:
    """
    Descricao da sua ferramenta

    Args:
        parametro (str): Descricao do parametro
        outro_parametro (int): Descricao do outro parametro
    Returns:
        palavra: str
    """

    return f"Resultado: {parametro} e {outro_parametro}"

@main.async_tool
async def minha_ferramenta_async(parametro: str, outro_parametro: int) -> str:
    """
    Descricao da sua ferramenta assíncrona

    Args:
        parametro (str): Descricao do parametro
        outro_parametro (int): Descricao do outro parametro
    Returns:
        palavra: str
    """
    return f"Resultado: {parametro} e {outro_parametro}"

# mostra as ferramentas disponíveis | shows available tools
print(json.dumps(main.get_tools(), indent=4))
