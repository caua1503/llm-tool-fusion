# llm-tool-fusion

<div align="center">
  <img src="logo.png" alt="LLM Tool Fusion Logo" width="300">
</div>

<div align="center">

[![Python](https://img.shields.io/badge/python->=3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](pyproject.toml)

</div>

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

available_tools = manager.get_map_tools()
async_available_tools = manager.get_name_async_tools()
    
# Processamento manual das chamadas de ferramentas
if response.choices[0].message.tool_calls:
    tool_results = []
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name in available_tools:
            # Execução manual da ferramenta
            import json
            args = json.loads(tool_call.function.arguments)

            #verificação se a ferramenta e assincrona
            result = available_tools[tool_call.function.name](**args) if tool_call.function.name not in async_available_tools else asyncio.run(available_tools[tool_call.function.name](**args)) 
                
            # Coloca os resultados em uma lista
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.function.name,
                "content": str(result)
            })
        
    # Adiciona todas as respostas de uma vez
    messages.append(response.choices[0].message)
    messages.extend(tool_results)
        
    # Nova chamada para processar o resultado
    final_response = client.chat.completions.create(
        model=default_model,
        messages=messages
    )
            
    return final_response.choices[0].message.content

print(final_response)
```

### 🔄 Processamento Automático de Chamadas

O llm-tool-fusion oferece um sistema robusto e simples para processar chamadas de ferramentas (instruções de uso em examples):

```python
# Função para chamadas ao LLM
llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
    model=model, 
    messages=messages, 
    tools=tools
)

# Processamento automático de chamadas
final_response = process_tool_calls(
    response=response,           # Resposta inicial do LLM
    messages=messages,           # Histórico de mensagens
    tool_caller=manager,         # Instância do ToolCaller
    model="gpt-4",              # Modelo a ser usado
    llm_call_fn=llm_call_fn,    # Função de chamada ao LLM
    verbose=True,               # (opcional) Logs detalhados
    verbose_time=True,          # (opcional) Métricas de tempo
    clean_messages=True,        # (opcional) Retorna apenas o conteúdo da mensagem
    use_async_poll=False,       # (opcional) Executa ferramentas assíncronas em paralelo
    max_chained_calls=5         # (opcional) Máximo de chamadas encadeadas
)
```

#### 🎯 Parâmetros Principais

- **`response`** (obrigatório): Resposta inicial do modelo
- **`messages`** (obrigatório): Lista de mensagens do chat
- **`tool_caller`** (obrigatório): Instância da classe ToolCaller
- **`model`** (obrigatório): Nome do modelo
- **`llm_call_fn`** (obrigatório): Função que faz a chamada ao modelo

#### ⚙️ Parâmetros Opcionais

- **`verbose`**: Exibe logs detalhados da execução
- **`verbose_time`**: Mostra métricas de tempo de execução
- **`clean_messages`**: Retorna apenas o conteúdo da mensagem final
- **`use_async_poll`**: Executa ferramentas assíncronas em paralelo para melhor performance
- **`max_chained_calls`**: Limite de chamadas encadeadas (padrão: 5)

#### ⚡ Performance com `use_async_poll`

Quando você tem múltiplas ferramentas assíncronas sendo chamadas simultaneamente, o parâmetro `use_async_poll=True` oferece melhor performance:

```python
# Sem async_poll: ferramentas executam sequencialmente
final_response = process_tool_calls(
    # ... outros parâmetros ...
    use_async_poll=False  # Padrão: execução sequencial
)

# Com async_poll: ferramentas assíncronas executam em paralelo
final_response = process_tool_calls(
    # ... outros parâmetros ...
    use_async_poll=True   # Execução paralela para melhor performance
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
    tool_caller=manager,
    model="gpt-4",
    llm_call_fn=async_llm_call_fn,
    verbose=True,
    use_async_poll=True  # Recomendado para melhor performance
)
```

#### 🔧 Suporte a Frameworks

O sistema funciona com diferentes frameworks através do parâmetro `framework` no `ToolCaller`:

```python
# Para OpenAI (padrão)
manager = ToolCaller(framework="openai")

# Para Ollama
manager = ToolCaller(framework="ollama")
llm_call_fn = lambda model, messages, tools: ollama.Client().chat(
    model=model,
    messages=messages,
    tools=tools
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

available_tools = manager.get_map_tools()
async_available_tools = manager.get_name_async_tools()
    
# Manual processing of tool calls
if response.choices[0].message.tool_calls:
    tool_results = []
    for tool_call in response.choices[0].message.tool_calls:
        if tool_call.function.name in available_tools:
            # Manual tool execution
            import json
            args = json.loads(tool_call.function.arguments)

print(final_response)
```

### 🔄 Automatic Call Processing

llm-tool-fusion provides a robust and simple system for processing tool calls automatically:

```python
# Function for LLM calls
llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
    model=model, 
    messages=messages, 
    tools=tools
)

# Automatic tool call processing
final_response = process_tool_calls(
    response=response,           # Initial response from the LLM
    messages=messages,           # Message history
    tool_caller=manager,         # ToolCaller instance
    model="gpt-4",              # Model to be used
    llm_call_fn=llm_call_fn,    # Function to call the LLM
    verbose=True,               # (optional) Detailed logs
    verbose_time=True,          # (optional) Time metrics
    clean_messages=True,        # (optional) Returns only message content
    use_async_poll=False,       # (optional) Execute async tools in parallel
    max_chained_calls=5         # (optional) Maximum chained calls
)
```

#### 🎯 Main Parameters

- **`response`** (required): Initial response from the model
- **`messages`** (required): List of chat messages
- **`tool_caller`** (required): ToolCaller class instance
- **`model`** (required): Model name
- **`llm_call_fn`** (required): Function that calls the model

#### ⚙️ Optional Parameters

- **`verbose`**: Shows detailed execution logs
- **`verbose_time`**: Shows execution time metrics
- **`clean_messages`**: Returns only the final message content
- **`use_async_poll`**: Executes async tools in parallel for better performance
- **`max_chained_calls`**: Limit of chained calls (default: 5)

#### ⚡ Performance with `use_async_poll`

When you have multiple asynchronous tools being called simultaneously, the `use_async_poll=True` parameter offers better performance:

```python
# Without async_poll: tools execute sequentially
final_response = process_tool_calls(
    # ... other parameters ...
    use_async_poll=False  # Default: sequential execution
)

# With async_poll: async tools execute in parallel
final_response = process_tool_calls(
    # ... other parameters ...
    use_async_poll=True   # Parallel execution for better performance
)
```

#### ✨ Main Features

- 🔁 **Automatic Loop**: Processes all tool calls to completion
- ⚡ **Asynchronous Support**: Runs synchronous and asynchronous tools automatically
- 📝 **Smart Logs**: Track execution with detailed logs and time metrics
- 🛡️ **Error Handling**: Robust error management during execution
- 💬 **Context Management**: Keeps conversation history organized
- 🔧 **Configurable**: Customize behavior to your needs

#### 🚀 Asynchronous Version

For applications that need asynchronous processing:

```python
# Asynchronous processing of tool calls
final_response = await process_tool_calls_async(
    response=response,
    messages=messages,
    tool_caller=manager,
    model="gpt-4",
    llm_call_fn=async_llm_call_fn,
    verbose=True,
    use_async_poll=True  # Recommended for better performance
)
```

#### 🔧 Framework Support

The system works with different frameworks through the `framework` parameter in `ToolCaller`:

```python
# For OpenAI (default)
manager = ToolCaller(framework="openai")

# For Ollama
manager = ToolCaller(framework="ollama")
llm_call_fn = lambda model, messages, tools: ollama.Client().chat(
    model=model,
    messages=messages,
    tools=tools
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
