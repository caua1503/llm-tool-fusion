"""
Este arquivo demonstra a diferença entre definir ferramentas diretamente com OpenAI
vs usar a biblioteca llm-tool-fusion.

This file demonstrates the difference between defining tools directly with OpenAI
vs using the llm-tool-fusion library.
"""
import os
import sys
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from openai import OpenAI
from typing import List, Dict, Any
from llm_tool_fusion import ToolCaller

# =============================================
# Método Tradicional OpenAI
# Traditional OpenAI Method
# =============================================

def traditional_openai_way():
    client = OpenAI()
    
    # Definição verbosa de ferramentas
    # Verbose tool definition
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Obtém a previsão do tempo para uma cidade\nGet weather forecast for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "Nome da cidade | City name"
                        },
                        "country": {
                            "type": "string",
                            "description": "País (opcional) | Country (optional)"
                        }
                    },
                    "required": ["city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_user",
                "description": "Cria um novo usuário no sistema\nCreates a new user in the system",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Nome completo | Full name"
                        },
                        "email": {
                            "type": "string",
                            "description": "Email do usuário | User email"
                        },
                        "age": {
                            "type": "integer",
                            "description": "Idade | Age"
                        }
                    },
                    "required": ["name", "email"]
                }
            }
        }
    ]
    
    # Uso das ferramentas
    # Tool usage
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Como está o tempo em São Paulo?"}],
        tools=tools
    )
    
    return response

# =============================================
# Método llm-tool-fusion
# llm-tool-fusion Method
# =============================================

def llm_tool_fusion_way():
    client = OpenAI()
    manager = ToolCaller()
    
    # Definição limpa e direta com decoradores
    # Clean and direct definition with decorators
    @manager.tool
    def get_weather(city: str, country: str = None) -> Dict[str, Any]:
        """
        Get weather forecast for a city
        
        Args:
            city (str): City name
            country (str, optional): Country
            
        Returns:
            Dict[str, Any]: Weather information
        """
        # Implementação aqui | Implementation here
        pass
    
    @manager.tool
    def create_user(name: str, email: str, age: int = None) -> Dict[str, Any]:
        """
        Creates a new user in the system
        
        Args:
            name (str): Full name
            email (str): User email
            age (int, optional): Age
            
        Returns:
            Dict[str, Any]: Created user data
        """
        # Implementação aqui | Implementation here
        pass
    
    # Uso das ferramentas - muito mais simples!
    # Tool usage - much simpler!
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Como está o tempo em São Paulo?"}],
        tools=manager.get_tools()
    )
    
    return response

if __name__ == "__main__":
    print("\nMétodo Tradicional OpenAI | Traditional OpenAI Method:")
    print("=" * 50)
    traditional_openai_way()
    
    print("\nMétodo llm-tool-fusion | llm-tool-fusion Method:")
    print("=" * 50)
    llm_tool_fusion_way() 