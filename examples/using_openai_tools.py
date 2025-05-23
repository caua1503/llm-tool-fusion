import sys
import os
import json
import asyncio
# Adiciona o diretório pai ao sys.path | Adds the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from llm_tool_fusion import ToolCaller, process_tool_calls
from external_tools import calculator
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# Usando o OpenRouter
# api_key = os.getenv("OPENROUTER_API_KEY")
# openrouter_model = "meta-llama/llama-3.3-8b-instruct:free"
# openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", 
#                            api_key=api_key)


# Usando o ollama(localhost)
ollama_client = OpenAI(base_url="http://localhost:11434/v1", 
                       api_key="ollama")
ollama_model = "qwen2.53b:latest"   

main = ToolCaller()

@main.tool
def multiply(number1: int, number2: int) -> int:
    """
    Multiplies two numbers
    Args:
        number1(int): The first number to multiply
        number2(int): The second number to multiply
    Returns:
        int: The product of the two numbers
    """

    return number1 * number2

@main.async_tool
async def fetch_user_data_async(user_id: str) -> str:
    """
    obtem os dados do usuario
    Args:
        user_id (str): o id do usuario.
    Returns:
        str: uma string formatada contendo as informações do perfil do usuario.
    """

    # print("Searching for user...")
    await asyncio.sleep(0.2)  
    if user_id != "123":
        return "User not found"

    # print("User found. Fetching related data...")

    # Defina duas tarefas assíncronas | Define two async tasks
    async def fetch_orders():
        await asyncio.sleep(0.3)
        return "Orders: [buy, sell]"

    async def fetch_payments():
        await asyncio.sleep(0.1)
        return "Payments: [ok, pending]"
    
    async def vehicle_info():
        await asyncio.sleep(0.1)
        return "Vehicle: [car, truck]"
    async def user_info():
        await asyncio.sleep(0.1)
        return "User: [Pedro, 20, São Paulo]"

    orders, payments, vehicle, user = await asyncio.gather(fetch_orders(), 
                                                           fetch_payments(), 
                                                           vehicle_info(), 
                                                           user_info())

    return f"User Profile:\n{orders}\n{payments}\n{vehicle}\n{user}"

main.register_tool(calculator)

system_prompt= """Você é um assistente de IA que responde sempre em português.
Para realizar ações, você DEVE usar as ferramentas (tools) disponíveis através do formato tool_calls.
NÃO gere código Python ou sugira implementações - use apenas as ferramentas fornecidas."""

user_input = "quais sao os dados do usuario com o id 123? e quanto e 76876 + 76876?"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input},
]

request_1 = {
    "model": ollama_model,
    "messages": messages,
    "tools": main.get_tools(),
}

# response_1 = openrouter_client.chat.completions.create(**request_1)
response_1 = ollama_client.chat.completions.create(**request_1)


llm_call_fn = lambda model, messages, tools: ollama_client.chat.completions.create(model=model, messages=messages, tools=tools)

response_2 = process_tool_calls(
    response=response_1,
    messages=messages,
    async_tools_name=main.get_name_async_tools(),
    available_tools=main.get_map_tools(),
    model=ollama_model,
    llm_call_fn=llm_call_fn,
    tools=main.get_tools(),
    verbose=True,  # Defina como False para ocultar logs | Set to False to hide logs
    verbose_time=True 
)

print(response_2.choices[0].message.content)
