import json
import re
from typing import Callable, Any, Dict


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
        print(f"Unable to extract function docstring {func_name}")
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
