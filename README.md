# llm-tool-fusion

[![Python](https://img.shields.io/badge/python->=3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](pyproject.toml)

## 🇧🇷 Português

### 📖 Descrição

**llm-tool-fusion** é uma biblioteca Python que simplifica e unifica a definição e chamada de ferramentas para grandes modelos de linguagem (LLMs). Compatível com frameworks populares que suportam tool calling, como Ollama, LangChain e OpenAI, ela permite integrar facilmente novas funções e módulos, tornando o desenvolvimento de aplicativos avançados de IA mais ágil e modular atraves de decoradores de funções.

### ✨ Principais Recursos

- 🔧 **Unificação de APIs**: Interface única para diferentes frameworks de LLM
- 🚀 **Integração Simplificada**: Adicione novas ferramentas com facilidade
- 🔗 **Compatibilidade Ampla**: Suporte para Ollama, LangChain, OpenAI e outros
- 📦 **Modularidade**: Arquitetura modular para desenvolvimento escalável
- ⚡ **Performance**: Otimizado para aplicações em produção

### 🚀 Instalação

```bash
pip install llm-tool-fusion
```

### 📋 Uso Básico (Exemplo com OpenAI)

```python
from llm_tool_fusion import ToolManager
from openai import OpenAI

client = OpenAI()

# Inicialize o gerenciador de ferramentas
manager = ToolManager()

# Adicione suas ferramentas personalizadas
@manager.tool
def multiply(numero1: int, numero2: int) -> int:
    """
    Multiplica doi numeros
    Args:
        numero1: int
        numero2: int
    Returns:
        int
    """

    return numero1 * numero2

response = client.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": "Quanto e 25 * 557 ?"}],
    tools=manager.get_tools()
)

print(response.output)
# Use com seu framework preferido
# Exemplo com OpenAI, LangChain, Ollama, etc.
```

### 🔧 Frameworks Suportados

- **OpenAI** - API oficial e modelos GPT
- **LangChain** - Framework completo para aplicações LLM
- **Ollama** - Execução local de modelos
- **Anthropic Claude** - API da Anthropic
- **E muito mais...**

### 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🇺🇸 English

### 📖 Description

**llm-tool-fusion** is a Python library that simplifies and unifies the definition and calling of tools for large language models (LLMs). Compatible with popular frameworks that support tool calling, such as Ollama, LangChain, and OpenAI, it allows you to easily integrate new functions and modules, making the development of advanced AI applications more agile and modular through function decorators..

### ✨ Key Features

- 🔧 **API Unification**: Single interface for different LLM frameworks
- 🚀 **Simplified Integration**: Add new tools with ease
- 🔗 **Wide Compatibility**: Support for Ollama, LangChain, OpenAI, and others
- 📦 **Modularity**: Modular architecture for scalable development
- ⚡ **Performance**: Optimized for production applications

### 🚀 Installation

```bash
pip install llm-tool-fusion
```

### 📋 Basic Usage (Example with OpenAI)

```python
from llm_tool_fusion import ToolManager
from openai import OpenAI

client = OpenAI()

# Inicialize o gerenciador de ferramentas
manager = ToolManager()

# Adicione suas ferramentas personalizadas
@manager.tool
def multiply(number1: int, number2: int) -> int:
    """
    Multiplies two numbers
    Args:
        number1: int
        number2: int
    Returns:
        int
    """

    return number1 * number2

response = client.responses.create(
    model="gpt-4.1",
    input=[{"role": "user", "content": "what is 25 * 557 ?"}],
    tools=manager.get_tools()
)

print(response.output)

# Use with your preferred framework
# Example with OpenAI, LangChain, Ollama, etc.
```

### 🔧 Supported Frameworks

- **OpenAI** - Official API and GPT models
- **LangChain** - Complete framework for LLM applications
- **Ollama** - Local model execution
- **Anthropic Claude** - Anthropic's API
- **And many more...**

### 🤝 Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🛠️ Development

### Prerequisites

- Python >= 3.12
- pip or poetry for dependency management

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/caua1503/llm-tool-fusion.git
cd llm-tool-fusion

# Install dependencies
pip install -e .

# Run tests
python -m pytest
```

### Project Structure

```
llm-tool-fusion/
├── llm_tool_fusion/
│   └── __init__.py
|   └── _core.py
|   └── _utils.py
│      
├── tests/
├── examples/
├── pyproject.toml
└── README.md
```

---

**⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!**

**⭐ If this project was helpful to you, consider starring it on GitHub!**
