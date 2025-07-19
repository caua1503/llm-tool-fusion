# llm-tool-fusion

<div align="center">
  <img src="assets/logo.png" alt="LLM Tool Fusion Logo" width="300">
</div>

<div align="center">

[![Python](https://img.shields.io/badge/python->=3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.2.2-orange.svg)](pyproject.toml)

</div>

## 📖 Descrição

**llm-tool-fusion** é uma biblioteca Python que simplifica e unifica a definição e chamada de ferramentas para grandes modelos de linguagem (LLMs). Compatível com frameworks populares que suportam tool calling, como Ollama, LangChain e OpenAI, ela permite integrar facilmente novas funções e módulos, tornando o desenvolvimento de aplicativos avançados de IA mais ágil e modular atraves de decoradores de funções.

## ✨ Principais Recursos

- 🔧 **Unificação de APIs**: Interface única para diferentes frameworks de LLM
- 🚀 **Integração Simplificada**: Adicione novas ferramentas com facilidade
- 🔗 **Compatibilidade Ampla**: Suporte para Ollama, LangChain, OpenAI e outros
- 📦 **Modularidade**: Arquitetura modular para desenvolvimento escalável
- ⚡ **Performance**: Otimizado para aplicações em produção
- 📝 **Menos Verbosidade**: Sintaxe simplificada para declaração de funções
- 🔄 **Processamento Automático**: Execução automática de chamadas de ferramentas (opcional)

## 🚀 Instalação

```bash
pip install llm-tool-fusion
```

## 📋 Uso Básico (Exemplo com OpenAI)

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

## 🔄 Processamento Automático de Chamadas

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

### 🎯 Parâmetros Principais

- **`response`** (obrigatório): Resposta inicial do modelo
- **`messages`** (obrigatório): Lista de mensagens do chat
- **`tool_caller`** (obrigatório): Instância da classe ToolCaller
- **`model`** (obrigatório): Nome do modelo
- **`llm_call_fn`** (obrigatório): Função que faz a chamada ao modelo

### ⚙️ Parâmetros Opcionais

- **`verbose`**: Exibe logs detalhados da execução
- **`verbose_time`**: Mostra métricas de tempo de execução
- **`clean_messages`**: Retorna apenas o conteúdo da mensagem final
- **`use_async_poll`**: Executa ferramentas assíncronas em paralelo para melhor performance
- **`max_chained_calls`**: Limite de chamadas encadeadas (padrão: 5)

### ⚡ Performance com `use_async_poll`

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

### ✨ Características Principais

- 🔁 **Ciclo Automático**: Processa todas as chamadas de ferramentas até a conclusão
- ⚡ **Suporte Assíncrono**: Executa ferramentas síncronas e assíncronas automaticamente
- 📝 **Logs Inteligentes**: Acompanhe a execução com logs detalhados e métricas de tempo
- 🛡️ **Tratamento de Erros**: Gerenciamento robusto de erros durante a execução
- 💬 **Gestão de Contexto**: Mantém o histórico de conversas organizado
- 🔧 **Configurável**: Personalize o comportamento conforme sua necessidade

### 🚀 Versão Assíncrona

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

### 🔧 Suporte a Frameworks

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

## 🔧 Frameworks Suportados

- **OpenAI** - API oficial e modelos GPT
- **LangChain** - Framework completo para aplicações LLM
- **Ollama** - Execução local de modelos
- **Anthropic Claude** - API da Anthropic
- **E muito mais...**

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## ⚠️ Aviso de Compatibilidade

> **Atenção:** A declaração de ferramentas (funções e decoradores) funciona com qualquer framework de LLM que suporte tool calling. Porém, o processamento automático de chamadas de ferramentas (`process_tool_calls` e `process_tool_calls_async`) possui suporte específico e otimizado apenas para alguns frameworks (como OpenAI, Ollama, etc). Para outros frameworks, pode ser necessário adaptar a função de chamada (`llm_call_fn`).

## 🛠️ Desenvolvimento

### Pré-requisitos

- Python >= 3.12
- pip ou poetry para gerenciamento de dependências

### Configuração do Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/caua1503/llm-tool-fusion.git
cd llm-tool-fusion

# Instale as dependências
pip install -e .

# Execute os testes
python -m pytest
```

### Estrutura do Projeto

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
