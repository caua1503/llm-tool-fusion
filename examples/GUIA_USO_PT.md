# Guia de Uso - llm-tool-fusion

## 📖 Visão Geral

O **llm-tool-fusion** é uma biblioteca que simplifica a criação e o uso de ferramentas (tools) para modelos de linguagem grandes (LLMs). Com ela, você pode:

- ✅ Definir ferramentas usando decoradores simples
- ✅ Processar automaticamente as chamadas de ferramentas
- ✅ Trabalhar com diferentes frameworks (OpenAI, Ollama, etc.)
- ✅ Executar ferramentas síncronas e assíncronas

## 🚀 Instalação

```bash
pip install llm-tool-fusion
```

## 📋 Uso Básico

### 1. Criando um ToolCaller

```python
from llm_tool_fusion import ToolCaller

# Para OpenAI (padrão)
manager = ToolCaller()

# Para Ollama
manager = ToolCaller(framework="ollama")
```

### 2. Definindo Ferramentas

#### Ferramenta Síncrona
```python
@manager.tool
def calcular_preco(preco: float, desconto: float) -> float:
    """
    Calcula o preço final com desconto
    
    Args:
        preco (float): Preço original
        desconto (float): Percentual de desconto
        
    Returns:
        float: Preço final
    """
    return preco * (1 - desconto / 100)
```

#### Ferramenta Assíncrona
```python
@manager.async_tool
async def buscar_clima(cidade: str) -> str:
    """
    Busca informações do clima
    
    Args:
        cidade (str): Nome da cidade
        
    Returns:
        str: Informações do clima
    """
    # Simulação de uma chamada assíncrona
    await asyncio.sleep(1)
    return f"Clima ensolarado em {cidade}"
```

### 3. Registrando Ferramentas Manualmente

```python
def minha_funcao(valor: int) -> int:
    """Multiplica por 2"""
    return valor * 2

# Registro individual
manager.register_tool(minha_funcao)

# Registro em lote
ferramentas = [
    {"function": funcao1, "type": "sync"},
    {"function": funcao2, "type": "async"}
]
manager.register_list_tools(ferramentas)
```

## 🔄 Processamento Automático

### Configuração Básica

```python
from openai import OpenAI
from llm_tool_fusion import process_tool_calls

client = OpenAI()

# Função para fazer chamadas ao LLM
llm_call_fn = lambda model, messages, tools: client.chat.completions.create(
    model=model, 
    messages=messages, 
    tools=tools
)

# Mensagens iniciais
messages = [{"role": "user", "content": "Calcule 100 reais com 20% de desconto"}]

# Primeira chamada
response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=manager.get_tools()
)
```

### Processamento Automático

```python
resposta_final = process_tool_calls(
    response=response,           # Resposta inicial do LLM
    messages=messages,           # Histórico de mensagens
    tool_caller=manager,         # Instância do ToolCaller
    model="gpt-4",              # Modelo a usar
    llm_call_fn=llm_call_fn,    # Função de chamada
    verbose=True,               # Logs detalhados
    verbose_time=True,          # Métricas de tempo
    clean_messages=True,        # Retorna só o conteúdo
    use_async_poll=True,        # Execução paralela
    max_chained_calls=5         # Limite de chamadas
)

print(resposta_final)
```

## ⚙️ Métodos Principais do ToolCaller

### Obtenção de Informações
```python
# Lista de ferramentas formatadas
tools = manager.get_tools()

# Mapa de ferramentas disponíveis
available_tools = manager.get_map_tools()

# Nomes das ferramentas assíncronas
async_tools = manager.get_name_async_tools()

# Nomes das ferramentas síncronas
sync_tools = manager.get_name_tools()

# Framework atual
framework = manager.get_framework()
```

## ⚡ Parâmetros de Configuração

### process_tool_calls()

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `response` | Any | ✅ | Resposta inicial do modelo |
| `messages` | List | ✅ | Lista de mensagens |
| `tool_caller` | ToolCaller | ✅ | Instância do gerenciador |
| `model` | str | ✅ | Nome do modelo |
| `llm_call_fn` | Callable | ✅ | Função de chamada ao LLM |
| `verbose` | bool | ❌ | Logs detalhados (padrão: False) |
| `verbose_time` | bool | ❌ | Métricas de tempo (padrão: False) |
| `clean_messages` | bool | ❌ | Retorna só conteúdo (padrão: False) |
| `use_async_poll` | bool | ❌ | Execução paralela (padrão: False) |
| `max_chained_calls` | int | ❌ | Limite de chamadas (padrão: 5) |

## 🚀 Versão Assíncrona

Para aplicações que necessitam de processamento assíncrono:

```python
from llm_tool_fusion import process_tool_calls_async

# Função assíncrona de chamada
async_llm_call_fn = lambda model, messages, tools: await client.chat.completions.acreate(
    model=model, 
    messages=messages, 
    tools=tools
)

# Processamento assíncrono
resposta_final = await process_tool_calls_async(
    response=response,
    messages=messages,
    tool_caller=manager,
    model="gpt-4",
    llm_call_fn=async_llm_call_fn,
    use_async_poll=True  # Recomendado para melhor performance
)
```

## 🔧 Frameworks Suportados

- **OpenAI**: `ToolCaller(framework="openai")`
- **Ollama**: `ToolCaller(framework="ollama")`

## 💡 Dicas de Performance

1. **use_async_poll=True**: Para múltiplas ferramentas assíncronas
2. **verbose=False**: Em produção para melhor performance
3. **max_chained_calls**: Ajuste conforme necessário
4. **clean_messages=True**: Para respostas mais limpas

## ⚠️ Observações Importantes

- Sempre documente suas ferramentas com docstrings
- Use type hints para melhor integração
- Teste suas ferramentas antes de usar em produção
- Gerencie adequadamente as exceções nas suas ferramentas

## 📚 Exemplos Completos

Veja os arquivos na pasta `examples/` para exemplos completos com OpenAI e Ollama. 