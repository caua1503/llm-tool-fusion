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

    def get_object_tools(self) -> dict[str, Callable]:
        list_name_tools = {} 
        for func in self._list_tools + self._async_list_tools:
            if func.__name__ not in list_name_tools:
                list_name_tools[func.__name__] = func
        return list_name_tools

    def get_tools(self) -> list[str]:
        x = 0
        tools = self._list_tools + self._async_list_tools
        for tool in tools:
            self._tools.append(extract_docstring(tools[x]))
            x += 1
        return self._tools

    def get_name_async_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._async_list_tools}
    
    def get_name_tools(self) -> set[str]:
        return {f"{func.__name__}" for func in self._list_tools}
