"""
Este arquivo demonstra a diferença entre implementar ferramentas assíncronas
diretamente vs usar a biblioteca llm-tool-fusion.

This file demonstrates the difference between implementing async tools
directly vs using the llm-tool-fusion library.
"""

import sys
import os
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dotenv import load_dotenv
import asyncio
from openai import AsyncOpenAI
from typing import Dict, Any, List
from llm_tool_fusion import ToolCaller, process_tool_calls_async
import time

load_dotenv()

client = AsyncOpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"))

default_model = os.getenv("DEFAULT_MODEL")
# =============================================
# Método Tradicional
# Traditional Method
# =============================================

async def traditional_async_way():

    async def get_user_info(user_id: str) -> Dict[str, Any]:
        # Execução automática das chamadas assíncronas
        # Automatic execution of async calls
        async def fetch_user():
            await asyncio.sleep(1)  # Simulando request
            return {"id": user_id, "name": "João", "age": 30}
            
        async def fetch_orders():
            await asyncio.sleep(1)  # Simulando request
            return [{"id": "1", "product": "Laptop"}, {"id": "2", "product": "Mouse"}]
            
        user_data, orders = await asyncio.gather(
            fetch_user(),
            fetch_orders()
        )
        
        return {
            "user": user_data,
            "orders": orders
        }
    
    def calculate_price(price: float, discount: float) -> float:
        return price * (1 - discount / 100)
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_user_info",
                "description": "Get complete user information including orders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID"
                        }
                    },
                    "required": ["user_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate_price",
                "description": "Calculates total price with discount",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "price": {
                            "type": "float",
                            "description": "Base price"
                        },
                        "discount": {
                            "type": "float",
                            "description": "Discount percentage"
                        }
                    },
                    "required": ["price", "discount"]
                }
            }
        }
    ]
    # Precisa implementar manualmente o gerenciamento de ferramentas assíncronas
    # Need to manually implement async tools management
    async_available_tools = ["get_user_info"]
    
    available_tools = {
        "get_user_info": get_user_info,
        "calculate_price": calculate_price
    }
    messages = [
        {"role": "user", "content": "Mostre os dados do usuário 123 incluindo pedidos"}
    ]
    # Primeira chamada para obter a intenção do LLM
    response = await client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=tools
    )
    
    # Precisa implementar manualmente a lógica de execução assíncrona
    # Need to manually implement async execution logic
    if response.choices[0].message.tool_calls:
        tool_results = []
        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name in available_tools:
                # Execução manual das chamadas assíncronas
                # Manual execution of async calls
                import json
                args = json.loads(tool_call.function.arguments)
                
                #verificação se a ferramenta e assincrona | checking if the tool is asynchronous
                result = available_tools[tool_call.function.name](**args) if tool_call.function.name not in async_available_tools else await available_tools[tool_call.function.name](**args)
                
                tool_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": str(result)
                })
                
        messages.append(response.choices[0].message)
        messages.extend(tool_results)
        
            # Segunda chamada para processar o resultado
        final_response = await client.chat.completions.create(
            model=default_model,
            messages=messages
            )
            
        return final_response.choices[0].message.content

# =============================================
# Método llm-tool-fusion
# llm-tool-fusion Method
# =============================================

async def llm_tool_fusion_async_way():

    manager = ToolCaller()
    # Definição simples com decorador async_tool
    # Simple definition with async_tool decorator
    @manager.async_tool
    async def get_user_info(user_id: str) -> Dict[str, Any]:
        """
        Get complete user information including orders
        
        Args:
            user_id (str): User ID
            
        Returns:
            Dict[str, Any]: User data and orders
        """
        # Execução automática das chamadas assíncronas
        # Automatic execution of async calls
        async def fetch_user():
            await asyncio.sleep(1)  # Simulando request
            return {"id": user_id, "name": "João", "age": 30}
            
        async def fetch_orders():
            await asyncio.sleep(1)  # Simulando request
            return [{"id": "1", "product": "Laptop"}, {"id": "2", "product": "Mouse"}]
            
        user_data, orders = await asyncio.gather(
            fetch_user(),
            fetch_orders()
        )
        
        return {
            "user": user_data,
            "orders": orders
        }
    
    @manager.tool
    def calculate_price(price: float, discount: float) -> float:
        """
        Calculates total price with discount
        
        Args:
            price (float): Base price
            discount (float): Discount percentage
            
        Returns:
            float: Final price with discount
        """
        return price * (1 - discount / 100)
    
    messages = [
        {"role": "user", "content": "Mostre os dados do usuário 123 incluindo pedidos"}
    ]
    # O process_tool_calls gerencia automaticamente a execução assíncrona
    # process_tool_calls automatically manages async execution
    response = await client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=manager.get_tools()
    )
    
    llm_call_fn=lambda model, messages, tools: client.chat.completions.create(model=model, messages=messages, tools=tools)
    
    final_response = await process_tool_calls_async(
        response= response,
        messages= messages,
        tool_caller= manager,
        model= default_model,
        llm_call_fn= llm_call_fn,
        verbose=True,  # (opicional): se True, exibe logs detalhados | (optional): If True, displays detailed logs
        verbose_time=True,  # (opicional): se True, exibe logs de tempo de execução das funções | (optional): If True, displays runtime logs of functions
        clean_messages=True,  #(opicional): se True, limpa as mensagens após o processamento | (optional): If True, clears messages after processing
        max_chained_calls=5 # (padrão: 5) número máximo de chamadas encadeadas permitidas | # (default: 5) maximum number of chained calls allowed
    )

    return final_response

# =============================================
# Exemplo de Encadeamento de Ferramentas Assíncronas
# Async Tool Chaining Example
# =============================================

async def chained_async_tools_example():
    """
    Exemplo que demonstra o uso encadeado de ferramentas assíncronas,
    onde o resultado de uma ferramenta é usado como entrada para outra.
    
    Example that demonstrates chained use of async tools,
    where the result of one tool is used as input for another.
    """

    manager = ToolCaller()

    
    # Base de dados simulada de usuários
    # Simulated user database
    users_db = {
        "user1": {"id": "user1", "name": "João Silva", "account_balance": 1500.0},
        "user2": {"id": "user2", "name": "Maria Oliveira", "account_balance": 2300.0},
        "user3": {"id": "user3", "name": "Carlos Santos", "account_balance": 950.0}
    }
    
    # Base de dados simulada de produtos
    # Simulated product database
    products_db = {
        "prod1": {"id": "prod1", "name": "Smartphone", "price": 1200.0, "stock": 15},
        "prod2": {"id": "prod2", "name": "Notebook", "price": 3500.0, "stock": 8},
        "prod3": {"id": "prod3", "name": "Fones de Ouvido", "price": 150.0, "stock": 30}
    }
    
    @manager.async_tool
    async def find_user(query: str) -> Dict:
        """
        Localiza usuário por ID ou nome.

        Args:
            query (str): Identificador ou nome do usuário
        
        Returns:
            dict: Dados do usuário encontrado
        """
        # Simula uma busca assíncrona
        await asyncio.sleep(0.5)
        
        # Busca por ID
        if query in users_db:
            return users_db[query]
        
        # Busca por nome (simples, case-insensitive)
        query = query.lower()
        for user_id, user_data in users_db.items():
            if query in user_data["name"].lower():
                return user_data
        
        return {"error": "Usuário não encontrado"}
    
    @manager.async_tool
    async def check_account_balance(user_id: str) -> Dict:
        """
        Consulta saldo da conta de um usuário.

        Args:
            user_id(str): Identificador do usuário
        
        Returns:
            dict: Informações do saldo da conta
        """
        # Simula uma busca assíncrona
        await asyncio.sleep(0.5)
        
        if user_id in users_db:
            user = users_db[user_id]
            return {
                "user_id": user_id,
                "name": user["name"],
                "balance": user["account_balance"]
            }
        return {"error": f"Usuário com ID {user_id} não encontrado"}
    
    @manager.async_tool
    async def find_product(query: str) -> Dict:
        """
        Localiza produto por ID ou nome.

        Args:
            query(str): Identificador ou nome do produto
        
        Returns:
            dict: Dados do produto encontrado
        """
        # Simula uma busca assíncrona
        await asyncio.sleep(0.5)
        
        # Busca por ID
        if query in products_db:
            return products_db[query]
        
        # Busca por nome (simples, case-insensitive)
        query = query.lower()
        for prod_id, prod_data in products_db.items():
            if query in prod_data["name"].lower():
                return prod_data
        
        return {"error": "Produto não encontrado"}
    
    @manager.async_tool
    async def check_purchase_eligibility(user_id: str, product_id: str) -> Dict:
        """
        Verifica elegibilidade de compra de um produto.

        Args:
            user_id(str): Identificador do usuário
            product_id(str): Identificador do produto
        
        Returns:
            dict: Resultado da verificação de compra
        """
        # Simula uma verificação assíncrona
        await asyncio.sleep(0.5)
        
        if user_id not in users_db:
            return {"eligible": False, "reason": f"Usuário {user_id} não encontrado"}
        
        if product_id not in products_db:
            return {"eligible": False, "reason": f"Produto {product_id} não encontrado"}
        
        user = users_db[user_id]
        product = products_db[product_id]
        
        if product["stock"] <= 0:
            return {"eligible": False, "reason": f"Produto {product['name']} fora de estoque"}
        
        if user["account_balance"] < product["price"]:
            return {
                "eligible": False, 
                "reason": f"Saldo insuficiente. Necessário: R${product['price']}, Disponível: R${user['account_balance']}"
            }
        
        return {
            "eligible": True,
            "user": user["name"],
            "product": product["name"],
            "price": product["price"],
            "balance_after": user["account_balance"] - product["price"]
        }
    
    # Exemplo de prompt que requer encadeamento de ferramentas
    messages = [
        {"role": "user", "content": "busque o usuario Maria e verifique se ela pode comprar um notebook com o saldo atual dela?"}
    ]
    
    # Primeira chamada ao LLM
    response = await client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=manager.get_tools()
    )
    
    # Processamento automático com encadeamento
    llm_call_fn = lambda model, messages, tools: client.chat.completions.create(model=model, messages=messages, tools=tools)
    
    final_response = await process_tool_calls_async(
        response=response,
        messages=messages,
        tool_caller=manager,
        model=default_model,
        llm_call_fn=llm_call_fn,
        verbose=True,
        verbose_time=True,
        clean_messages=True,
        max_chained_calls=5
    )
    
    return final_response

# =============================================
# Exemplo de uso com async_poll
# Example of use with async_poll
# =============================================

async def async_poll_example():
    """
    Exemplo que demonstra o uso do async_poll para executar várias ferramentas
    assíncronas em paralelo e processar os resultados à medida que ficam disponíveis.
    
    Example that demonstrates the use of async_poll to execute several
    asynchronous tools in parallel and process the results as they become available.
    """
    manager = ToolCaller()
    
    # Simulação de diferentes APIs com tempos de resposta variados
    # Simulation of different APIs with varied response times
    
    @manager.async_tool
    async def fetch_weather(city: str) -> Dict:
        """
        Busca previsão do tempo para uma cidade.
        
        Args:
            city (str): Nome da cidade
            
        Returns:
            Dict: Dados da previsão do tempo
        """
        # Simulando API com tempo de resposta longo (2s)
        await asyncio.sleep(2)
        weather_data = {
            "city": city,
            "temperature": 28,
            "condition": "Ensolarado",
            "humidity": 65
        }
        return weather_data
    
    @manager.async_tool
    async def fetch_news(topic: str) -> Dict:
        """
        Busca notícias sobre um tópico específico.
        
        Args:
            topic (str): Tópico das notícias
            
        Returns:
            Dict: Lista de notícias
        """
        # Simulando API com tempo de resposta médio (2s)
        await asyncio.sleep(2)
        
        news_data = {
            "topic": topic,
            "articles": [
                {"title": f"Novidades sobre {topic}", "source": "Jornal Daily"},
                {"title": f"Últimas atualizações: {topic}", "source": "Tech News"}
            ]
        }
        return news_data
    
    @manager.async_tool
    async def fetch_stock_price(symbol: str) -> Dict:
        """
        Busca cotação atual de uma ação.
        
        Args:
            symbol (str): Símbolo da ação
            
        Returns:
            Dict: Dados da cotação
        """
        # Simulando API com tempo de resposta curto (1s)
        await asyncio.sleep(1)
        
        import random
        price = round(random.uniform(50, 200), 2)
        stock_data = {
            "symbol": symbol,
            "price": price,
            "change": round(random.uniform(-5, 5), 2),
            "volume": random.randint(10000, 1000000)
        }
        return stock_data
    
    # Exemplo de prompt que requer múltiplas consultas assíncronas
    messages = [
        {"role": "user", "content": "Preciso das seguintes informações para tomar decisões hoje: previsão do tempo em São Paulo, notícias sobre tecnologia e cotação da ação AAPL"}
    ]
    
    # Primeira chamada ao LLM
    response = await client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=manager.get_tools()
    )
    
    # Processamento utilizando async_poll para executar ferramentas em paralelo
    llm_call_fn = lambda model, messages, tools: client.chat.completions.create(model=model, messages=messages, tools=tools)
    
    print("\n[ASYNC POLL] Iniciando execução com async_poll=True")
    
    start_time_async_poll = time.time()
    
    final_response = await process_tool_calls_async(
        response=response,
        messages=messages,
        tool_caller=manager,
        model=default_model,
        llm_call_fn=llm_call_fn,
        verbose=True,
        verbose_time=True,
        clean_messages=True,
        use_async_poll=True,  # Ativando o async_poll para execução paralela
        max_chained_calls=5
    )
    
    end_time_async_poll = time.time()
    
    # Para comparação, executamos novamente sem async_poll
    messages = [
        {"role": "user", "content": "Preciso das seguintes informações para tomar decisões hoje: previsão do tempo em São Paulo, notícias sobre tecnologia e cotação da ação AAPL"}
    ]
    
    response = await client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=manager.get_tools()
    )
    
    print("\n[SEM ASYNC POLL] Iniciando execução com async_poll=False")
    
    start_time_no_async_poll = time.time()
    
    regular_response = await process_tool_calls_async(
        response=response,
        messages=messages,
        tool_caller=manager,
        model=default_model,
        llm_call_fn=llm_call_fn,
        verbose=True,
        verbose_time=True,
        clean_messages=True,
        use_async_poll=False,  # Desativando o async_poll para execução sequencial
        max_chained_calls=5
    )
    
    end_time_no_async_poll = time.time()
    print(f"\n[ASYNC POLL] Tempo total de execução: {end_time_async_poll - start_time_async_poll} segundos")
    print(f"\n[SEM ASYNC POLL] Tempo total de execução: {end_time_no_async_poll - start_time_no_async_poll} segundos")
    
    return final_response

if __name__ == "__main__":
    print("\nMétodo Tradicional | Traditional Method:")
    print("=" * 50)
    print(asyncio.run(traditional_async_way()))
    
    print("\nMétodo llm-tool-fusion | llm-tool-fusion Method:")
    print("=" * 50)
    print(asyncio.run(llm_tool_fusion_async_way()))

    print("\nExemplo de Encadeamento de Ferramentas Assíncronas | Async Tool Chaining Example:")
    print("=" * 50)
    print(asyncio.run(chained_async_tools_example()))
    
    print("\nExemplo de Async Poll (Execução Paralela) | Async Poll Example (Parallel Execution):")
    print("=" * 50)
    print(asyncio.run(async_poll_example()))

    