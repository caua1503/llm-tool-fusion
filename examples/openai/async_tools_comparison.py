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

import asyncio
from openai import AsyncOpenAI
from typing import Dict, Any, List
from llm_tool_fusion import ToolCaller

# =============================================
# Método Tradicional
# Traditional Method
# =============================================

async def traditional_async_way():
    client = AsyncOpenAI()
    default_model = "gpt-4o"

    async def get_user_info(user_id: str) -> Dict[str, Any]:
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
                "description": "Obtém informações completas do usuário incluindo pedidos\nGet complete user information including orders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "ID do usuário | User ID"
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
    client = AsyncOpenAI()
    manager = ToolCaller()
    default_model = "gpt-4o"
    # Definição simples com decorador async_tool
    # Simple definition with async_tool decorator
    @manager.async_tool
    async def get_user_info(user_id: str) -> Dict[str, Any]:
        """
        Obtém informações completas do usuário incluindo pedidos
        Get complete user information including orders
        
        Args:
            user_id (str): ID do usuário | User ID
            
        Returns:
            Dict[str, Any]: Dados do usuário e pedidos | User data and orders
        """
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
    
    available_tools = manager.get_map_tools()
    async_available_tools = manager.get_name_async_tools()

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
    
    # Processamento automático das chamadas assíncronas
    # Automatic processing of async calls
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

if __name__ == "__main__":
    print("\nMétodo Tradicional | Traditional Method:")
    print("=" * 50)
    print(asyncio.run(traditional_async_way()))
    
    print("\nMétodo llm-tool-fusion | llm-tool-fusion Method:")
    print("=" * 50)
    print(asyncio.run(llm_tool_fusion_async_way())) 