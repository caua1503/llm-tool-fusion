def test_public_api_import():
    from llm_tool_fusion import ToolCaller, process_tool_calls, process_tool_calls_async
    assert ToolCaller is not None
    assert process_tool_calls is not None
    assert process_tool_calls_async is not None 