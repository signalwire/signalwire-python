"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for SWAIGFunction class
"""

import pytest
import json
from typing import Any
from unittest.mock import Mock, patch

from signalwire.core.swaig_function import SWAIGFunction


class TestSWAIGFunctionInitialization:
    """Test SWAIGFunction initialization"""
    
    def test_basic_initialization(self) -> None:
        """Test basic function initialization"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function",
            parameters={"param1": {"type": "string"}}
        )
        
        assert func.name == "test_function"
        assert func.description == "Test function"
        assert func.parameters == {"param1": {"type": "string"}}
        assert func.handler == test_handler
    
    def test_initialization_with_all_parameters(self) -> None:
        """Test initialization with all parameters"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="advanced_function",
            handler=test_handler,
            description="Advanced test function",
            parameters={
                "param1": {"type": "string"},
                "param2": {"type": "integer"}
            },
            secure=True,
            fillers={"thinking": ["Let me think...", "Processing..."]},
            webhook_url="https://example.com/webhook",
            custom_field="custom_value"
        )
        
        assert func.name == "advanced_function"
        assert func.description == "Advanced test function"
        assert func.secure is True
        assert func.fillers == {"thinking": ["Let me think...", "Processing..."]}
        assert func.webhook_url == "https://example.com/webhook"
        assert func.is_external is True
    
    def test_initialization_with_defaults(self) -> None:
        """Test initialization with default values"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}

        func = SWAIGFunction(
            name="default_function",
            handler=test_handler,
            description="Default test function"
        )

        # Check default values
        assert func.secure is False  # Default should be non-secure
        assert func.fillers is None
        assert func.webhook_url is None
        assert func.is_external is False

    def test_is_typed_handler_defaults_false(self) -> None:
        """Test that is_typed_handler defaults to False"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}

        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function"
        )
        assert func.is_typed_handler is False

    def test_is_typed_handler_set_true(self) -> None:
        """Test that is_typed_handler can be set to True"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}

        func = SWAIGFunction(
            name="typed_function",
            handler=test_handler,
            description="Typed function",
            is_typed_handler=True
        )
        assert func.is_typed_handler is True


class TestSWAIGFunctionExecution:
    """Test function execution"""
    
    def test_execute_basic(self) -> None:
        """Test basic function execution"""
        def test_handler(args: dict[str, Any], raw_data: Any) -> dict[str, Any]:
            return {"result": "success", "args": args}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function"
        )
        
        result = func.execute({"param1": "value1"}, {"call_id": "123"})
        
        assert isinstance(result, dict)
        assert "response" in result or "result" in result
    
    def test_execute_with_swaig_function_result(self) -> None:
        """Test execution returning FunctionResult"""
        from signalwire.core.function_result import FunctionResult
        
        def test_handler(args: dict[str, Any], raw_data: Any) -> FunctionResult:
            return FunctionResult("Function executed successfully")
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function"
        )
        
        result = func.execute({"param1": "value1"}, {"call_id": "123"})
        
        assert isinstance(result, dict)
        assert "response" in result
    
    def test_execute_with_error_handling(self) -> None:
        """Test execution with error handling"""
        def test_handler(args: dict[str, Any], raw_data: Any) -> None:
            raise ValueError("Test error")
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function"
        )
        
        result = func.execute({"param1": "value1"}, {"call_id": "123"})
        
        # Should return error response, not raise exception
        assert isinstance(result, dict)
        assert "response" in result
    
    def test_call_method(self) -> None:
        """Test __call__ method"""
        def test_handler(*args: Any, **kwargs: Any) -> dict[str, Any]:
            return {"args": args, "kwargs": kwargs}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function"
        )
        
        result = func("arg1", param="value")
        assert result == {"args": ("arg1",), "kwargs": {"param": "value"}}


class TestSWAIGFunctionSerialization:
    """Test function serialization"""
    
    def test_to_swaig_basic(self) -> None:
        """Test basic to_swaig conversion"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function",
            parameters={"param1": {"type": "string"}}
        )
        
        swaig_dict = func.to_swaig("https://example.com")
        
        assert swaig_dict["function"] == "test_function"
        assert swaig_dict["description"] == "Test function"
        assert "parameters" in swaig_dict
        assert "web_hook_url" in swaig_dict
    
    def test_to_swaig_with_token(self) -> None:
        """Test to_swaig with token and call_id"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function"
        )
        
        swaig_dict = func.to_swaig("https://example.com", token="test-token", call_id="call-123")
        
        assert "token=test-token" in swaig_dict["web_hook_url"]
        assert "call_id=call-123" in swaig_dict["web_hook_url"]
    
    def test_to_swaig_with_fillers(self) -> None:
        """Test to_swaig with fillers"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        fillers = {"thinking": ["Processing...", "Let me think..."]}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function",
            fillers=fillers
        )
        
        swaig_dict = func.to_swaig("https://example.com")
        
        assert swaig_dict["fillers"] == fillers
    
    def test_ensure_parameter_structure(self) -> None:
        """Test parameter structure normalization"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        # Test with simple parameters
        func1 = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function",
            parameters={"param1": {"type": "string"}}
        )
        
        structure = func1._ensure_parameter_structure()
        assert structure["type"] == "object"
        assert "properties" in structure
        
        # Test with already structured parameters
        func2 = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function",
            parameters={"type": "object", "properties": {"param1": {"type": "string"}}}  # type: ignore[dict-item]  # valid mixed-value SWAIG parameter structure
        )
        
        structure = func2._ensure_parameter_structure()
        assert structure["type"] == "object"
        assert "properties" in structure


class TestSWAIGFunctionValidation:
    """Test function validation"""
    
    def test_validate_args(self) -> None:
        """Test argument validation"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function",
            parameters={"param1": {"type": "string"}}
        )
        
        # validate_args returns (is_valid, errors) tuple
        is_valid, errors = func.validate_args({"param1": "value"})
        assert is_valid is True
        is_valid, errors = func.validate_args({"invalid": "value"})
        assert isinstance(is_valid, bool)
    
    def test_function_name_validation(self) -> None:
        """Test function name validation"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        # Should accept valid function names
        valid_names = ["test_function", "testFunction", "test123", "function_with_underscores"]
        
        for name in valid_names:
            func = SWAIGFunction(
                name=name,
                handler=test_handler,
                description="Test function"
            )
            assert func.name == name


class TestSWAIGFunctionErrorHandling:
    """Test error handling and edge cases"""
    
    def test_none_handler(self) -> None:
        """Test handling of None handler"""
        func = SWAIGFunction(
            name="test_function",
            handler=None,  # type: ignore[arg-type]  # intentional invalid input for validation test
            description="Test function"
        )
        
        assert func.handler is None
    
    def test_empty_function_name(self) -> None:
        """Test handling of empty function name"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="",
            handler=test_handler,
            description="Test function"
        )
        
        assert func.name == ""
    
    def test_none_description(self) -> None:
        """Test handling of None description"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description=None  # type: ignore[arg-type]  # intentional invalid input for validation test
        )

        assert func.description is None
    
    def test_execute_with_none_raw_data(self) -> None:
        """Test execution with None raw_data"""
        def test_handler(args: dict[str, Any], raw_data: Any) -> dict[str, Any]:
            return {"args": args, "raw_data": raw_data}
        
        func = SWAIGFunction(
            name="test_function",
            handler=test_handler,
            description="Test function"
        )
        
        # Should handle None raw_data gracefully
        result = func.execute({"param1": "value1"}, None)
        assert isinstance(result, dict)


class TestSWAIGFunctionIntegration:
    """Test integration functionality"""
    
    def test_external_webhook_configuration(self) -> None:
        """Test external webhook configuration"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="webhook_function",
            handler=test_handler,
            description="Function with webhook",
            webhook_url="https://example.com/webhook"
        )
        
        assert func.is_external is True
        assert func.webhook_url == "https://example.com/webhook"
    
    def test_security_configuration(self) -> None:
        """Test security configuration"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        # Secure function
        secure_func = SWAIGFunction(
            name="secure_function",
            handler=test_handler,
            description="Secure function",
            secure=True
        )
        
        # Non-secure function
        public_func = SWAIGFunction(
            name="public_function",
            handler=test_handler,
            description="Public function",
            secure=False
        )
        
        assert secure_func.secure is True
        assert public_func.secure is False
    
    def test_extra_swaig_fields(self) -> None:
        """Test extra SWAIG fields"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="function_with_extras",
            handler=test_handler,
            description="Function with extra fields",
            custom_field="custom_value",
            another_field={"nested": "data"}
        )
        
        swaig_dict = func.to_swaig("https://example.com")
        
        assert swaig_dict["custom_field"] == "custom_value"
        assert swaig_dict["another_field"] == {"nested": "data"}
    
    def test_json_serialization(self) -> None:
        """Test JSON serialization of SWAIG output"""
        def test_handler() -> dict[str, Any]:
            return {"result": "success"}
        
        func = SWAIGFunction(
            name="json_function",
            handler=test_handler,
            description="JSON test function",
            parameters={"param1": {"type": "string"}}
        )
        
        swaig_dict = func.to_swaig("https://example.com")
        
        # Should be JSON serializable
        json_str = json.dumps(swaig_dict)
        assert isinstance(json_str, str)
        
        # Should be deserializable
        parsed = json.loads(json_str)
        assert parsed["function"] == "json_function" 