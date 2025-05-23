from llm_tool_fusion import ToolCaller
from decimal import Decimal, getcontext
import re
import math
import statistics

mathematical_agent = ToolCaller()

@mathematical_agent.tool
def calculator(expression: str) -> str :
    """
    Mathematical calculator for mathematical expressions

    Args:
        expression (str): The expression to be calculated (example: "1+1").
    Returns:
        Decimal | str: The result of the expression or "operation error" in case of error.
    """
    try:
        getcontext().prec = 28
        expr_decimal = re.sub(r'\b\d+(\.\d+)?\b', lambda x: f'Decimal("{x.group(0)}")', expression)
        result = eval(expr_decimal, {"__builtins__":  None, "Decimal": Decimal})
        return str(result)
    except Exception as e:
        print(f"Calculator error: {str(e)}")
        return "operation error"

@mathematical_agent.tool
def average(numbers: list[float]) -> float:
    """
    Calculates the arithmetic mean of a list of numbers.

    Args:
        numbers (list[float]): List of numbers to calculate the average.
    Returns:
        float: Arithmetic mean of the numbers.
    """
    try:
        return statistics.mean(numbers)
    except Exception as e:
        print(f"Error calculating average: {str(e)}")
        return "operation error"

@mathematical_agent.tool
def median(numbers: list[float]) -> float:
    """
    Calculates the median of a list of numbers.

    Args:
        numbers (list[float]): List of numbers to calculate the median.
    Returns:
        float: Median of the numbers.
    """
    try:
        return statistics.median(numbers)
    except Exception as e:
        print(f"Error calculating median: {str(e)}")
        return "operation error"

@mathematical_agent.tool
def standard_deviation(numbers: list[float]) -> float:
    """
    Calculates the standard deviation of a list of numbers.

    Args:
        numbers (list[float]): List of numbers to calculate the standard deviation.
    Returns:
        float: Standard deviation of the numbers.
    """
    try:
        return statistics.stdev(numbers)
    except Exception as e:
        print(f"Error calculating standard deviation: {str(e)}")
        return "operation error"

@mathematical_agent.tool
def power(base: float, exponent: float) -> float:
    """
    Calculates the power of a number.

    Args:
        base (float): Base number.
        exponent (float): Exponent.
    Returns:
        float: Result of the power operation.
    """
    try:
        return math.pow(base, exponent)
    except Exception as e:
        print(f"Error calculating power: {str(e)}")
        return "operation error"

@mathematical_agent.tool
def square_root(number: float) -> float:
    """
    Calculates the square root of a number.

    Args:
        number (float): Number to calculate the square root.
    Returns:
        float: Square root of the number.
    """
    try:
        return math.sqrt(number)
    except Exception as e:
        print(f"Error calculating square root: {str(e)}")
        return "operation error"



    
    
    


