"""
Este arquivo demonstra a diferença entre processar chamadas de ferramentas
tradicionalmente vs usar a biblioteca llm-tool-fusion.

This file demonstrates the difference between processing tool calls
traditionally vs using the llm-tool-fusion library.
"""
import os
import sys
import asyncio
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any, List
from llm_tool_fusion import ToolCaller, process_tool_calls
load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)
default_model = os.getenv("DEFAULT_MODEL")
framework = os.getenv("FRAMEWORK")
# =============================================
# Método Tradicional
# Traditional Method
# =============================================

def traditional_tool_processing():

    def calculate_price(price: float, discount: float) -> float:
        return price * (1 - discount / 100)
    
    async def example_async_tool(param: str) -> str:
        return f"Async tool result: {param}"
    
    # Definição das ferramentas
    # Tools definition
    tools = [
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
    
    available_tools = {
        "calculate_price": calculate_price
    }
    async_available_tools = ["example_async_tool"]
    
    # Primeira chamada para obter a intenção do LLM
    # First call to get LLM's intention

    messages = [
        {"role": "user", "content": "Calcule o preço final de um produto de R$100 com 20% de desconto"}
    ]

    response = client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=tools
    )
    
    # Processamento manual das chamadas de ferramentas
    # Manual processing of tool calls
    if response.choices[0].message.tool_calls:
        tools_results = []
        for tool_call in response.choices[0].message.tool_calls:
            if tool_call.function.name in available_tools:
                # Execução manual da ferramenta
                # Manual tool execution
                import json
                args = json.loads(tool_call.function.arguments)
                
                #verificação se a ferramenta e assincrona | checking if the tool is asynchronous
                result = available_tools[tool_call.function.name](**args) if tool_call.function.name not in async_available_tools else asyncio.run(available_tools[tool_call.function.name](**args)) 
                
                # Formatação manual da resposta
                # Manual response formatting
                tools_results.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": "calculate_price",
                    "content": str(result)
                })

            messages.append(response.choices[0].message)
            messages.extend(tools_results)

            # Nova chamada para processar o resultado
            # New call to process the result
            final_response = client.chat.completions.create(
                model=default_model,
                messages=messages
            )
            
            return final_response.choices[0].message.content

# =============================================
# Método llm-tool-fusion
# llm-tool-fusion Method
# =============================================

def llm_tool_fusion_processing():
    manager = ToolCaller()
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
    
    @manager.async_tool
    async def example_async_tool(param: str) -> str:
        """
        Example asynchronous tool
        
        Args:
            param (str): Input parameter
            
        Returns:
            str: Async tool result

        """
        return f"Async tool result: {param}"
    
    messages = [
        {"role": "user", "content": "oi, tudo bem?"}
    ]
    # Primeira chamada ao LLM
    # First LLM call
    response = client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=manager.get_tools()
    )
    
    # Processamento automático com process_tool_calls
    # Automatic processing with process_tool_calls

    llm_call_fn=lambda model, messages, tools: client.chat.completions.create(model=model, messages=messages, tools=tools)
    
    final_response = process_tool_calls(
        response= response,
        messages= messages,
        tool_caller= manager,
        model= default_model,
        llm_call_fn= llm_call_fn,
        verbose=True,  # (opicional): se True, exibe logs detalhados | (optional): If True, displays detailed logs
        verbose_time=True,  # (opicional): se True, exibe logs de tempo de execução das funções | (optional): If True, displays runtime logs of functions
        clean_messages=True  #(opicional): se True, limpa as mensagens após o processamento | (optional): If True, clears messages after processing
    )
    
    return final_response

# =============================================
# Exemplo de Encadeamento de Ferramentas
# Tool Chaining Example
# =============================================

def chained_tools_example():
    """
    Exemplo que demonstra o uso encadeado de ferramentas,
    onde o resultado de uma ferramenta é usado como entrada para outra.
    
    Example that demonstrates chained use of tools,
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
    
    @manager.tool
    def find_user(query: str) -> Dict:
        """
        Localiza usuário por ID ou nome.

        Args:
            query (str): Identificador ou nome do usuário
        
        Returns:
            dict: Dados do usuário encontrado
        """
        # Busca por ID
        if query in users_db:
            return users_db[query]
        
        # Busca por nome (simples, case-insensitive)
        query = query.lower()
        for user_id, user_data in users_db.items():
            if query in user_data["name"].lower():
                return user_data
        
        return {"error": "Usuário não encontrado"}
    
    @manager.tool
    def check_account_balance(user_id: str) -> Dict:
        """
        Consulta saldo da conta de um usuário por ID.

        Args:
            user_id(str): Identificador do usuário (ID)
        
        Returns:
            dict: Informações do saldo da conta
        """
        if user_id in users_db:
            user = users_db[user_id]
            return {
                "user_id": user_id,
                "name": user["name"],
                "balance": user["account_balance"]
            }
        return {"error": f"Usuário com ID {user_id} não encontrado"}
    
    @manager.tool
    def find_product(query: str) -> Dict:
        """
        Localiza produto por ID ou nome.

        Args:
            query(str): Identificador ou nome do produto
        
        Returns:
            dict: Dados do produto encontrado
        """
        # Busca por ID
        if query in products_db:
            return products_db[query]
        
        # Busca por nome (simples, case-insensitive)
        query = query.lower()
        for prod_id, prod_data in products_db.items():
            if query in prod_data["name"].lower():
                return prod_data
        
        return {"error": "Produto não encontrado"}
    
    @manager.tool
    def check_purchase_eligibility(user_id: str, product_id: str) -> Dict:
        """
        Verifica elegibilidade de compra de um produto (ID) para um usuário (ID).

        Args:
            user_id(str): Identificador do usuário (ID)
            product_id(str): Identificador do produto (ID)
        
        Returns:
            dict: Resultado da verificação de compra
        """
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
    response = client.chat.completions.create(
        model=default_model,
        messages=messages,
        tools=manager.get_tools()
    )
    
    # Processamento automático com encadeamento
    llm_call_fn = lambda model, messages, tools: client.chat.completions.create(model=model, messages=messages, tools=tools)
    
    final_response = process_tool_calls(
        response=response,
        messages=messages,
        tool_caller= manager,
        model=default_model,
        llm_call_fn=llm_call_fn,
        verbose=True,
        verbose_time=True,
        clean_messages=True,
        max_chained_calls=5
    )
    
    return final_response

if __name__ == "__main__":
    # print("\nMétodo Tradicional | Traditional Method:")
    # print("=" * 50)
    # traditional_response = traditional_tool_processing()
    # print(traditional_response)
    
    print("\nMétodo llm-tool-fusion | llm-tool-fusion Method:")
    print("=" * 50)
    fusion_response = llm_tool_fusion_processing()
    print(fusion_response)
    
    # print("\nExemplo de Encadeamento de Ferramentas | Tool Chaining Example:")
    # print("=" * 50)
    # chained_response = chained_tools_example()
    # print(chained_response) 