import os
import sys
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from llm_tool_fusion._utils import _extract_docstring

def dummy_func(a: int, b: str) -> bool:
    """Soma e concatena
    Args:
        a (int): número
        b (str): texto
    Returns:
        bool
    """
    return True

def test__extract_docstring():
    doc = _extract_docstring(dummy_func)
    assert doc['name'] == 'dummy_func'
    assert 'Soma e concatena' in doc['description']
    assert 'a' in doc['parameters']['properties']
    assert doc['parameters']['properties']['a']['type'] == 'int'
    assert 'número' in doc['parameters']['properties']['a']['description']
    assert 'b' in doc['parameters']['properties']
    assert doc['parameters']['properties']['b']['type'] == 'str'
    assert 'texto' in doc['parameters']['properties']['b']['description']

def test__extract_docstring_no_docstring():
    def no_doc_func(x):
        return x

    doc = _extract_docstring(no_doc_func)
    assert doc['name'] == 'no_doc_func'
    assert doc['description'] == ''
    assert isinstance(doc['parameters']['properties'], dict)
    assert len(doc['parameters']['properties']) == 0 