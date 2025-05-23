import sys
import os
import json
import asyncio
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_tool_fusion import ToolCaller

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
async def fetch_user_data(user_id: str) -> str:
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

# mostra as ferramentas disponíveis | shows available tools
print(json.dumps(main.get_tools(), indent=4))
