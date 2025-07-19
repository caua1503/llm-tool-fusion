# llm-tool-fusion

<div align="center">
  <img src="assets/logo.png" alt="LLM Tool Fusion Logo" width="300">
</div>

<div align="center">

[![Python](https://img.shields.io/badge/python->=3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.2-orange.svg)](pyproject.toml)

</div>

## 📖 Read this documentation in [Portuguese](README.pt.md)

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

### ⚠️ Compatibility Notice

> **Note:** Tool declaration (functions and decorators) works with any LLM framework that supports tool calling. However, automatic tool call processing (`process_tool_calls` and `process_tool_calls_async`) has specific and optimized support only for some frameworks (such as OpenAI, Ollama, etc). For other frameworks, you may need to adapt the call function (`llm_call_fn`).

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
