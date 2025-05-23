import json
import re

def extract_docstring(func):
    """
    Extrai informações de descrição, parâmetros e retorno de uma docstring.

    Args:
        func: Função da qual a docstring será extraída.

    Returns:
        dict: Dicionário contendo descrição, parâmetros e retorno em formato JSON.
    """
    doc = func.__doc__
    if not doc:
        return {
            "description": "",
            "parameters": {},
            "returns": ""
        }

    # Inicializa a estrutura do resultado
    result = {
        "description": "",
        "parameters": {},
        "returns": ""
    }

    # Divide a docstring em linhas
    lines = doc.strip().split('\n')
    current_section = "description"
    param_name = None

    # Regex para identificar seções
    param_pattern = re.compile(r'^\s*(Args|Parameters):\s*$')
    return_pattern = re.compile(r'^\s*(Returns|Return):\s*$')
    param_def_pattern = re.compile(r'^\s*(\w+)\s*\(([^)]+)\):\s*(.*)$')

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
                result["parameters"][param_name] = {
                    "type": param_type.strip(),
                    "description": param_desc.strip()
                }
            elif param_name and line:  # Continuação da descrição do parâmetro
                result["parameters"][param_name]["description"] += " " + line
        elif current_section == "returns":
            if line:
                result["returns"] += line + " "

    # Limpa espaços extras
    result["description"] = result["description"].strip()
    result["returns"] = result["returns"].strip()
    for param in result["parameters"]:
        result["parameters"][param]["description"] = result["parameters"][param]["description"].strip()

    return json.dumps(result, indent=2, ensure_ascii=False)