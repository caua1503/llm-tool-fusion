# Usage Guide - llm-tool-fusion

## 📖 Overview

**llm-tool-fusion** is a library that simplifies the creation and use of tools for large language models (LLMs). With it, you can:

- ✅ Define tools using simple decorators
- ✅ Automatically process tool calls
- ✅ Work with different frameworks (OpenAI, Ollama, etc.)
- ✅ Execute synchronous and asynchronous tools

## 🚀 Installation

```bash
pip install llm-tool-fusion
```

## 📋 Basic Usage

### 1. Creating a ToolCaller

```python
from llm_tool_fusion import ToolCaller

# For OpenAI (default)
manager = ToolCaller()

# For Ollama
manager = ToolCaller(framework="ollama")
```

### 2. Defining Tools

#### Synchronous Tool
```python
@manager.tool
def calculate_price(price: float, discount: float) -> float:
    """
    Calculate final price with discount
    
    Args:
        price (float): Original price
        discount (float): Discount percentage
        
    Returns:
        float: Final price
    """
    return price * (1 - discount / 100)
```

#### Asynchronous Tool
```python
@manager.async_tool
async def get_weather(city: str) -> str:
    """
    Get weather information
    
    Args:
        city (str): City name
        
    Returns:
        str: Weather information
    """
    # Simulate an async call
    await asyncio.sleep(1)
    return f"Sunny weather in {city}"
```

### 3. Manually Registering Tools

```python
def my_function(value: int) -> int:
    """Multiply by 2"""
    return value * 2

# Individual registration
manager.register_tool(my_function)

# Batch registration
tools_list = [
    {"function": function1, "type": "sync"},
    {"function": function2, "type": "async"}
]
manager.register_list_tools(tools_list)
```

## 🔄 Automatic Processing

### Basic Setup

```python
from openai import OpenAI
from llm_tool_fusion import process_tool_calls

client = OpenAI()

# Function to make LLM calls
llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
    model=model, 
    messages=messages, 
    tools=tools
)

# Initial messages
messages = [{"role": "user", "content": "Calculate $100 with 20% discount"}]

# First call
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=manager.get_tools()
)
```

### Automatic Processing

```python
final_response = process_tool_calls(
    response=response,           # Initial LLM response
    messages=messages,           # Message history
    tool_caller=manager,         # ToolCaller instance
    model="gpt-4",              # Model to use
    llm_call_fn=llm_call_fn,    # Call function
    verbose=True,               # Detailed logs
    verbose_time=True,          # Time metrics
    clean_messages=True,        # Return only content
    use_async_poll=True,        # Parallel execution
    max_chained_calls=5         # Call limit
)

print(final_response)
```

## ⚙️ Main ToolCaller Methods

### Information Retrieval
```python
# List of formatted tools
tools = manager.get_tools()

# Map of available tools
available_tools = manager.get_map_tools()

# Names of async tools
async_tools = manager.get_name_async_tools()

# Names of sync tools
sync_tools = manager.get_name_tools()

# Current framework
framework = manager.get_framework()
```

## ⚡ Configuration Parameters

### process_tool_calls()

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `response` | Any | ✅ | Initial model response |
| `messages` | List | ✅ | List of messages |
| `tool_caller` | ToolCaller | ✅ | Manager instance |
| `model` | str | ✅ | Model name |
| `llm_call_fn` | Callable | ✅ | LLM call function |
| `verbose` | bool | ❌ | Detailed logs (default: False) |
| `verbose_time` | bool | ❌ | Time metrics (default: False) |
| `clean_messages` | bool | ❌ | Return only content (default: False) |
| `use_async_poll` | bool | ❌ | Parallel execution (default: False) |
| `max_chained_calls` | int | ❌ | Call limit (default: 5) |

## 🚀 Asynchronous Version

For applications that need asynchronous processing:

```python
from llm_tool_fusion import process_tool_calls_async

# Async call function
async_llm_call_fn = lambda model, messages, tools: await client.chat.completions.acreate(
    model=model, 
    messages=messages, 
    tools=tools
)

# Async processing
final_response = await process_tool_calls_async(
    response=response,
    messages=messages,
    tool_caller=manager,
    model="gpt-4",
    llm_call_fn=async_llm_call_fn,
    use_async_poll=True  # Recommended for better performance
)
```

## 🔧 Supported Frameworks

- **OpenAI**: `ToolCaller(framework="openai")`
- **Ollama**: `ToolCaller(framework="ollama")`

## 💡 Performance Tips

1. **use_async_poll=True**: For multiple async tools
2. **verbose=False**: In production for better performance
3. **max_chained_calls**: Adjust as needed
4. **clean_messages=True**: For cleaner responses

## ⚠️ Important Notes

- Always document your tools with docstrings
- Use type hints for better integration
- Test your tools before using in production
- Properly handle exceptions in your tools

## 📚 Complete Examples

Check the files in the `examples/` folder for complete examples with OpenAI and Ollama.

## ⚠️ Compatibility Notice

> **Note:** Tool declaration (functions and decorators) works with any LLM framework that supports tool calling. However, automatic tool call processing (`process_tool_calls` and `process_tool_calls_async`) has specific and optimized support only for some frameworks (such as OpenAI, Ollama, etc). For other frameworks, you may need to adapt the call function (`llm_call_fn`). 