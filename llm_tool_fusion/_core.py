from functools import wraps
from typing import Callable
from ._utils import extract_docstring

class ToolCaller:
    def __init__(self):
        self._list_tools = []
        self._async_list_tools = []
        self._tools = []

    def tool(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        self._list_tools.append(wrapper)
        return wrapper
    
    def async_tool(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        self._async_list_tools.append(wrapper)
        return wrapper

    def get_tools(self) -> list[str]:
        x = 0
        tools = self._list_tools + self._async_list_tools
        self._tools = []
        for tool in tools:
            tool_info = extract_docstring(tools[x])
            self._tools.append({
                "type": "function",
                "function": tool_info
            })
            x += 1
        return self._tools

    def get_name_async_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._async_list_tools}
    
    def get_name_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._list_tools}
    
    def get_map_tools(self) -> dict[str, Callable]:
        return {f"{func.__name__}": func for func in self._list_tools + self._async_list_tools}
    
    def register_tool(self, function: Callable, tool_type: str = "sync"):
        if tool_type == "sync":
            self._list_tools.append(function)
        elif tool_type == "async":
            self._async_list_tools.append(function)
        else:
            raise ValueError("Invalid tool type. Use 'sync' or 'async'.")
        self._tools.append({
            "type": "function",
            "function": extract_docstring(function)
        })
        
        