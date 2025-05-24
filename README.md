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
- 📝 **Menos Verbosidade**: Sintaxe simplificada para declaração de funções
- 🔄 **Processamento Automático**: Execução automática de chamadas de ferramentas (opcional)

### 🚀 Instalação

```bash
pip install llm-tool-fusion
```

### 📋 Uso Básico (Exemplo com OpenAI)

```python
from openai import OpenAI
from llm_tool_fusion import ToolCaller, process_tool_calls

# Inicializa o cliente OpenAI e o gerenciador de ferramentas
client = OpenAI()
manager = ToolCaller()

# Define uma ferramenta usando o decorador
@manager.tool
def calculate_price(price: float, discount: float) -> float:
    """
    Calcula o preço final com desconto
    
    Args:
        price (float): Preço base
        discount (float): Percentual de desconto
        
    Returns:
        float: Preço final com desconto
    """
    return price * (1 - discount / 100)

# Prepara a mensagem e faz a chamada ao LLM
messages = [
    {"role": "user", "content": "Calcule o preço final de um produto de R$100 com 20% de desconto"}
]

# Primeira chamada ao LLM
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=manager.get_tools()
)

# Define a função de chamada da IA
# Esta função lambda permite compatibilidade com diferentes bibliotecas (OpenAI, Anthropic, etc)
# Você pode adaptar esta função para usar qualquer biblioteca que desejar
llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
    model=model, 
    messages=messages, 
    tools=tools
)

# Processa a resposta automaticamente
final_response = process_tool_calls(
    response=response,
    messages=messages,
    async_tools_name=manager.get_name_async_tools(),
    available_tools=manager.get_map_tools(),
    model="gpt-4",
    llm_call_fn=llm_call_fn,
    tools=manager.get_tools(),
    verbose=True,
    verbose_time=True,
    clean_messages=True
)

print(final_response)
```

### 🔄 Processamento de Chamadas

O llm-tool-fusion oferece um sistema robusto e simples para processar chamadas de ferramentas:

```python
# Processamento automático de chamadas
final_response = process_tool_calls(
    response=response,        # Resposta inicial do LLM
    messages=messages,        # Histórico de mensagens
    async_tools_name=manager.get_name_async_tools(),  # Nome das ferramentas assíncronas
    available_tools=manager.get_map_tools(),          # Mapa de ferramentas disponíveis
    model="gpt-4",           # Modelo a ser usado
    llm_call_fn=llm_call_fn, # Função de chamada ao LLM
    tools=manager.get_tools(),# Lista de ferramentas
    verbose=True,            # (opcional) Logs detalhados
    verbose_time=True,       # (opcional) Métricas de tempo
    clean_messages=True      # (opcional) Limpa mensagens após processamento, nao e necessario .choices[0].message.content
)
```

#### ✨ Características Principais

- 🔁 **Ciclo Automático**: Processa todas as chamadas de ferramentas até a conclusão
- ⚡ **Suporte Assíncrono**: Executa ferramentas síncronas e assíncronas automaticamente
- 📝 **Logs Inteligentes**: Acompanhe a execução com logs detalhados e métricas de tempo
- 🛡️ **Tratamento de Erros**: Gerenciamento robusto de erros durante a execução
- 💬 **Gestão de Contexto**: Mantém o histórico de conversas organizado
- 🔧 **Configurável**: Personalize o comportamento conforme sua necessidade

#### 🚀 Versão Assíncrona

Para aplicações que precisam de processamento assíncrono:

```python
# Processamento assíncrono de chamadas
final_response = await process_tool_calls_async(
    response=response,
    messages=messages,
    # ... mesmos parâmetros da versão síncrona ...
)
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

**llm-tool-fusion** is a Python library that simplifies and unifies the definition and calling of tools for large language models (LLMs). Compatible with popular frameworks that support tool calling, such as Ollama, LangChain, and OpenAI, it allows you to easily integrate new functions and modules, making the development of advanced AI applications more agile and modular through function decorators.

### ✨ Key Features

- 🔧 **API Unification**: Single interface for different LLM frameworks
- 🚀 **Simplified Integration**: Add new tools with ease
- 🔗 **Wide Compatibility**: Support for Ollama, LangChain, OpenAI, and others
- 📦 **Modularity**: Modular architecture for scalable development
- ⚡ **Performance**: Optimized for production applications
- 📝 **Less Verbosity**: Simplified syntax for function declarations
- 🔄 **Automatic Processing**: Automatic execution of tool calls (optional)

### 🚀 Installation

```bash
pip install llm-tool-fusion
```

### 📋 Basic Usage (Example with OpenAI)

```python
from openai import OpenAI
from llm_tool_fusion import ToolCaller, process_tool_calls

# Initialize OpenAI client and tool manager
client = OpenAI()
manager = ToolCaller()

# Define a tool using the decorator
@manager.tool
def calculate_price(price: float, discount: float) -> float:
    """
    Calculate final price with discount
    
    Args:
        price (float): Base price
        discount (float): Discount percentage
        
    Returns:
        float: Final price with discount
    """
    return price * (1 - discount / 100)

# Prepare message and make LLM call
messages = [
    {"role": "user", "content": "Calculate the final price of a $100 product with 20% discount"}
]

# First LLM call
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=manager.get_tools()
)

# Define the AI call function
# This lambda function allows compatibility with different libraries (OpenAI, Anthropic, etc)
# You can adapt this function to use any library you want
llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
    model=model, 
    messages=messages, 
    tools=tools
)

# Process response automatically
final_response = process_tool_calls(
    response=response,
    messages=messages,
    async_tools_name=manager.get_name_async_tools(),
    available_tools=manager.get_map_tools(),
    model="gpt-4",
    llm_call_fn=llm_call_fn,
    tools=manager.get_tools(),
    verbose=True,
    verbose_time=True,
    clean_messages=True
)

print(final_response)
```

### 🔄 Processamento de Chamadas

llm-tool-fusion provides a robust and simple system for processing tool calls:

```python
# Automatic tool call processing
final_response = process_tool_calls(
    response=response,        # Initial response from the LLM
    messages=messages,        # Message history
    async_tools_name=manager.get_name_async_tools(),  # Names of asynchronous tools
    available_tools=manager.get_map_tools(),          # Map of available tools
    model="gpt-4",           # Model to be used
    llm_call_fn=llm_call_fn, # Function to call the LLM
    tools=manager.get_tools(),# List of tools
    verbose=True,            # (optional) Detailed logs
    verbose_time=True,       # (optional) Time metrics
    clean_messages=True      # (optional) Clears messages after processing, no .choices[0].message.content required
)
```

#### ✨ Main Features

- 🔁 **Automatic Loop**: Processes all tool calls to completion
- ⚡ **Asynchronous Support**: Runs synchronous and asynchronous tools automatically
- 📝 **Smart Logs**: Track execution with detailed logs and time metrics
- 🛡️ **Error Handling**: Robust error management during execution
- 💬 **Context Management**: Keeps conversation history organized
- 🔧 **Configurable**: Customize behavior to your needs

#### 🚀 Versão Assíncrona

For applications that need asynchronous processing:

```python
# Asynchronous processing of tool calls
final_response = await process_tool_calls_async(
    response=response,
    messages=messages,
    # ... same parameters as the synchronous version ...
)
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
