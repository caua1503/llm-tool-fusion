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
from ollama import Client
from llm_tool_fusion import ToolCaller, process_tool_calls

# =============================================
# Método Tradicional
# Traditional Method
# =============================================
client = Client()
default_model = "qwen2.53b:latest"

def traditional_tool_processing():

    def calculate_price(price: float, discount: float) -> float:
        return price * (1 - discount / 100)
    
    async def get_user_info_async_tool(id: str) -> str:
        return f"User info: joao"
    
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
        },
        {
            "type": "function",
            "function": {
                "name": "get_user_info_async_tool",
                "description": "Get user info",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "str",
                            "description": "User id"
                        }
                    }
                }
            }
        }
    ]
    
    available_tools = {
        "calculate_price": calculate_price,
        "get_user_info_async_tool": get_user_info_async_tool
    }
    async_available_tools = ["get_user_info_async_tool"]
    
    # Primeira chamada para obter a intenção do LLM
    # First call to get LLM's intention

    messages = [
        {"role": "user", "content": "Calcule o preço final de um produto de R$100 com 20% de desconto e pegue o nome do usuario com id 1"}
    ]

    response = client.chat(
        model=default_model,
        messages=messages,
        tools=tools
    )
    
    # Processamento manual das chamadas de ferramentas
    # Manual processing of tool calls
    if response.message.tool_calls:
        tools_results = []
        for tool in response.message.tool_calls:
            if function_to_call := available_tools.get(tool.function.name):
                print('Calling function:', tool.function.name)
                print('Arguments:', tool.function.arguments)
                output = function_to_call(**tool.function.arguments) if tool.function.name not in async_available_tools else asyncio.run(function_to_call(**tool.function.arguments))
                print('Function output:', output)
                tools_results.append({"role": "tool", "content": str(output), "name": tool.function.name})
            else:
                print('Function not found:', tool.function.name)

        messages.append(response.message)
        messages.extend(tools_results)
        final_response = client.chat(model=default_model, messages=messages)
        return final_response
    else:
        print("No tool calls found")
        return response

# =============================================
# Método llm-tool-fusion
# llm-tool-fusion Method
# =============================================

def llm_tool_fusion_processing():
    client = Client()
    manager = ToolCaller(framework= "ollama")
    default_model = "qwen2.53b:latest"

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
    async def get_user_info_async_tool(id: str) -> str:
        """
        Get user info

        Args:
            id (str): User id
            
        Returns:
            str: User info
        """

        return f"User info: joao"
    
    messages = [
        {"role": "user", "content": "Calcule o preço final de um produto de R$100 com 20% de desconto e pegue o nome do usuario com id 1"}
    ]
    # Primeira chamada ao LLM
    # First LLM call
    response = client.chat(
        model=default_model,
        messages=messages,
        tools=manager.get_tools()
    )
    
    # Processamento automático com process_tool_calls
    # Automatic processing with process_tool_calls
    llm_call_fn=lambda model, messages, tools: client.chat(model=model, messages=messages, tools=tools)
    
    final_response = process_tool_calls(
        response= response,
        messages= messages,
        tool_caller= manager,
        model= default_model,
        llm_call_fn= llm_call_fn,
        verbose=True,  # Defina como False para ocultar logs (opicional, False por padrao) | Set to False to hide logs (optional, False by default)
        verbose_time=True,  # Defina como False para ocultar logs de tempo (opicional, False por padrao) | Set to False to hide time logs (optional, False by default)
        max_chained_calls= 5,
        clean_messages= True
    )
    
    return final_response

if __name__ == "__main__":
    print("\nMétodo Tradicional | Traditional Method:")
    print("=" * 50)
    traditional_response = traditional_tool_processing()
    print(traditional_response.message.content)
    
    print("\nMétodo llm-tool-fusion | llm-tool-fusion Method:")
    print("=" * 50)
    fusion_response = llm_tool_fusion_processing()
    print(fusion_response) 