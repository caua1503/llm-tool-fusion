import sys
import os
import json
import asyncio
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_tool_fusion import ToolCaller
from external_tools import calculator, standard_deviation, median

main = ToolCaller()

@main.tool
def multiply(number1: int, number2: int) -> int:
    """
    Multiplies two numbers
    Args:
        number1: int
        number2: int
    Returns:
        int
    """

    return number1 * number2

@main.async_tool
async def fetch_user_data_async(user_id: str) -> str:
    """
    Simulates an asynchronous operation that first finds a user,
    then fetches related data from two tables in parallel.
    Args:
        user_id (str): The ID of the user to fetch data for.
    Returns:
        str: A formatted string containing the user's profile information.
    """

    print("Searching for user...")
    await asyncio.sleep(0.2)  
    if user_id != "123":
        return "User not found"

    print("User found. Fetching related data...")

    # Defina duas tarefas assíncronas | Define two async tasks
    async def fetch_orders():
        await asyncio.sleep(0.3)
        return "Orders: [Order1, Order2]"

    async def fetch_payments():
        await asyncio.sleep(0.1)
        return "Payments: [Paid]"

    orders, payments = await asyncio.gather(fetch_orders(), fetch_payments())

    return f"User Profile:\n{orders}\n{payments}"

#Registrando uma função importada ao agente | Registering an imported function to the agent
main.register_tool(calculator)


list_external_tools = [{"function":standard_deviation, "type":"sync"}, 
                       {"function":median, "type":"sync"}]

main.register_list_tools(list_external_tools)

# Ferramentas disponíveis | Available tools
print("\nFerramentas disponíveis | Available tools:")
print(json.dumps(main.get_tools(), indent=4))
print("="*30)

# Nomes das ferramentas assíncronas | Names of available async tools
print("\nNomes das ferramentas assíncronas | Names of available async tools:")
print(main.get_name_async_tools())
print("="*30)

# Nomes das ferramentas síncronas | Names of available syncronous tools
print("\nNomes das ferramentas síncronas | Names of available syncronous tools:") 
print(main.get_name_tools())
print("="*30)

# Este dicionário associa o nome de cada ferramenta a sua respectiva função. | This dictionary associates the name of each tool with its respective function.
print("\nMapa de ferramentas | Tools map:")
print(main.get_map_tools())
print("="*30)
