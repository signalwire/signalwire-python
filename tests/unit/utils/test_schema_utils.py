"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for schema_utils module
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
try:
    # Python 3.11+: the Traversable ABC lives under importlib.resources.abc.
    from importlib.resources.abc import Traversable
except ModuleNotFoundError:
    # Python 3.10: importlib.resources.abc does not exist yet; the ABC is at
    # importlib.abc.Traversable (used here only as a type annotation).
    from importlib.abc import Traversable
from unittest.mock import Mock, patch, MagicMock, mock_open
from typing import Dict, List, Any, Optional

from signalwire.utils.schema_utils import SchemaUtils


class TestSchemaUtils:
    """Test SchemaUtils functionality"""
    
    def test_basic_initialization_with_schema_path(self) -> None:
        """Test basic SchemaUtils initialization with schema path"""
        with patch.object(SchemaUtils, 'load_schema', return_value={}):
            with patch.object(SchemaUtils, '_extract_verb_definitions', return_value={}):
                utils = SchemaUtils(schema_path="/path/to/schema.json")
                
                assert utils.schema_path == "/path/to/schema.json"
                assert utils.schema == {}
                assert utils.verbs == {}
    
    def test_initialization_without_schema_path(self) -> None:
        """Test initialization without schema path uses default"""
        with patch.object(SchemaUtils, '_get_default_schema_path', return_value="/default/schema.json"):
            with patch.object(SchemaUtils, 'load_schema', return_value={}):
                with patch.object(SchemaUtils, '_extract_verb_definitions', return_value={}):
                    utils = SchemaUtils()
                    
                    assert utils.schema_path == "/default/schema.json"
    
    def test_get_default_schema_path_importlib_resources_new(self) -> None:
        """Test default schema path using importlib.resources (Python 3.13+)"""
        utils = SchemaUtils.__new__(SchemaUtils)  # Create without calling __init__
        
        mock_path = Mock()
        mock_path.__str__ = Mock(return_value="/package/schema.json")  # type: ignore[method-assign]
        
        with patch('importlib.resources.files') as mock_files:
            mock_files.return_value.joinpath.return_value = mock_path
            
            result = utils._get_default_schema_path()
            
            assert result == "/package/schema.json"
            mock_files.assert_called_once_with("signalwire")
    
    def test_get_default_schema_path_importlib_resources_old(self) -> None:
        """Test default schema path using importlib.resources (Python 3.7-3.8)"""
        utils = SchemaUtils.__new__(SchemaUtils)
        
        with patch('importlib.resources.files', side_effect=AttributeError):
            with patch('importlib.resources.path') as mock_path:
                mock_context = Mock()
                mock_context.__enter__ = Mock(return_value=Path("/old/schema.json"))
                mock_context.__exit__ = Mock(return_value=None)
                mock_path.return_value = mock_context
                
                result = utils._get_default_schema_path()
                
                assert result == "/old/schema.json"
    
    def test_get_default_schema_path_manual_search(self) -> None:
        """Test default schema path using manual file search when importlib.resources fails"""
        utils = SchemaUtils.__new__(SchemaUtils)
        utils.log = Mock()

        import importlib.resources
        original_files = importlib.resources.files

        def failing_files(package: str) -> Traversable:
            if package == "signalwire":
                raise ImportError("mocked")
            return original_files(package)

        with patch('importlib.resources.files', side_effect=failing_files):
            with patch('os.path.exists') as mock_exists:
                with patch('os.getcwd', return_value="/current"):
                    # First path exists
                    mock_exists.side_effect = lambda path: path == "/current/schema.json"

                    result = utils._get_default_schema_path()

                    assert result == "/current/schema.json"

    def test_get_default_schema_path_not_found(self) -> None:
        """Test default schema path when file is not found anywhere"""
        utils = SchemaUtils.__new__(SchemaUtils)
        utils.log = Mock()

        import importlib.resources
        original_files = importlib.resources.files

        def failing_files(package: str) -> Traversable:
            if package == "signalwire":
                raise ImportError("mocked")
            return original_files(package)

        with patch('importlib.resources.files', side_effect=failing_files):
            with patch('os.path.exists', return_value=False):

                result = utils._get_default_schema_path()

                assert result is None
    
    def test_load_schema_success(self) -> None:
        """Test successful schema loading"""
        schema_data = {
            "$defs": {
                "SWMLMethod": {
                    "anyOf": [{"$ref": "#/$defs/AIMethod"}]
                },
                "AIMethod": {
                    "properties": {
                        "ai": {"type": "object"}
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            schema_path = f.name
        
        try:
            utils = SchemaUtils.__new__(SchemaUtils)
            utils.schema_path = schema_path
            utils.log = Mock()
            
            result = utils.load_schema()
            
            assert result == schema_data
        finally:
            os.unlink(schema_path)
    
    def test_load_schema_file_not_found(self) -> None:
        """Test schema loading when file doesn't exist"""
        utils = SchemaUtils.__new__(SchemaUtils)
        utils.schema_path = "/nonexistent/schema.json"
        utils.log = Mock()
        
        result = utils.load_schema()
        
        assert result == {}
        utils.log.error.assert_called_once()
    
    def test_load_schema_invalid_json(self) -> None:
        """Test schema loading with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            schema_path = f.name
        
        try:
            utils = SchemaUtils.__new__(SchemaUtils)
            utils.schema_path = schema_path
            utils.log = Mock()
            
            result = utils.load_schema()
            
            assert result == {}
            utils.log.error.assert_called_once()
        finally:
            os.unlink(schema_path)
    
    def test_load_schema_no_path(self) -> None:
        """Test schema loading when no path is provided"""
        utils = SchemaUtils.__new__(SchemaUtils)
        utils.schema_path = None
        utils.log = Mock()
        
        result = utils.load_schema()
        
        assert result == {}
        utils.log.warning.assert_called_once()


class TestVerbExtraction:
    """Test verb extraction functionality"""
    
    def test_extract_verb_definitions_success(self) -> None:
        """Test successful verb extraction"""
        schema = {
            "$defs": {
                "SWMLMethod": {
                    "anyOf": [
                        {"$ref": "#/$defs/AIMethod"},
                        {"$ref": "#/$defs/AnswerMethod"}
                    ]
                },
                "AIMethod": {
                    "properties": {
                        "ai": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string"}
                            }
                        }
                    }
                },
                "AnswerMethod": {
                    "properties": {
                        "answer": {
                            "type": "object",
                            "properties": {
                                "max_duration": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        }
        
        utils = SchemaUtils.__new__(SchemaUtils)
        utils.schema = schema
        utils.log = Mock()
        
        verbs = utils._extract_verb_definitions()
        
        assert "ai" in verbs
        assert "answer" in verbs
        assert verbs["ai"]["name"] == "ai"
        assert verbs["ai"]["schema_name"] == "AIMethod"
        assert verbs["answer"]["name"] == "answer"
        assert verbs["answer"]["schema_name"] == "AnswerMethod"
    
    def test_extract_verb_definitions_no_swml_method(self) -> None:
        """Test verb extraction when SWMLMethod is missing"""
        schema: dict[str, Any] = {"$defs": {}}
        
        utils = SchemaUtils.__new__(SchemaUtils)
        utils.schema = schema
        utils.log = Mock()
        
        verbs = utils._extract_verb_definitions()
        
        assert verbs == {}
        utils.log.warning.assert_called_once()
    
    def test_extract_verb_definitions_no_anyof(self) -> None:
        """Test verb extraction when anyOf is missing"""
        schema: dict[str, Any] = {
            "$defs": {
                "SWMLMethod": {
                    "properties": {}
                }
            }
        }
        
        utils = SchemaUtils.__new__(SchemaUtils)
        utils.schema = schema
        utils.log = Mock()
        
        verbs = utils._extract_verb_definitions()
        
        assert verbs == {}


class TestVerbProperties:
    """Test verb property access methods"""
    
    def setup_method(self) -> None:
        """Set up test data"""
        self.utils = SchemaUtils.__new__(SchemaUtils)
        self.utils.verbs = {
            "ai": {
                "name": "ai",
                "schema_name": "AIMethod",
                "definition": {
                    "properties": {
                        "ai": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string"},
                                "temperature": {"type": "number"}
                            },
                            "required": ["prompt"]
                        }
                    }
                }
            },
            "answer": {
                "name": "answer",
                "schema_name": "AnswerMethod",
                "definition": {
                    "properties": {
                        "answer": {
                            "type": "object",
                            "properties": {
                                "max_duration": {"type": "integer"}
                            }
                        }
                    }
                }
            }
        }
    
    def test_get_verb_properties_existing(self) -> None:
        """Test getting properties for existing verb"""
        result = self.utils.get_verb_properties("ai")
        
        expected = {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"},
                "temperature": {"type": "number"}
            },
            "required": ["prompt"]
        }
        assert result == expected
    
    def test_get_verb_properties_nonexistent(self) -> None:
        """Test getting properties for nonexistent verb"""
        result = self.utils.get_verb_properties("nonexistent")
        
        assert result == {}
    
    def test_get_verb_required_properties_existing(self) -> None:
        """Test getting required properties for existing verb"""
        result = self.utils.get_verb_required_properties("ai")
        
        assert result == ["prompt"]
    
    def test_get_verb_required_properties_no_required(self) -> None:
        """Test getting required properties when none are specified"""
        result = self.utils.get_verb_required_properties("answer")
        
        assert result == []
    
    def test_get_verb_required_properties_nonexistent(self) -> None:
        """Test getting required properties for nonexistent verb"""
        result = self.utils.get_verb_required_properties("nonexistent")
        
        assert result == []
    
    def test_get_all_verb_names(self) -> None:
        """Test getting all verb names"""
        result = self.utils.get_all_verb_names()
        
        assert set(result) == {"ai", "answer"}
    
    def test_get_verb_parameters_existing(self) -> None:
        """Test getting parameters for existing verb"""
        result = self.utils.get_verb_parameters("ai")
        
        expected = {
            "prompt": {"type": "string"},
            "temperature": {"type": "number"}
        }
        assert result == expected
    
    def test_get_verb_parameters_nonexistent(self) -> None:
        """Test getting parameters for nonexistent verb"""
        result = self.utils.get_verb_parameters("nonexistent")
        
        assert result == {}


class TestVerbValidation:
    """Test verb validation functionality"""

    def setup_method(self) -> None:
        """Set up test data"""
        self.utils = SchemaUtils.__new__(SchemaUtils)
        self.utils._validation_enabled = True
        self.utils._full_validator = None
        self.utils.log = Mock()
        self.utils.verbs = {
            "ai": {
                "name": "ai",
                "schema_name": "AIMethod",
                "definition": {
                    "properties": {
                        "ai": {
                            "type": "object",
                            "properties": {
                                "prompt": {"type": "string"},
                                "temperature": {"type": "number"}
                            },
                            "required": ["prompt"]
                        }
                    }
                }
            }
        }
    
    def test_validate_verb_valid_config(self) -> None:
        """Test validation with valid configuration"""
        config = {"prompt": "You are helpful"}
        
        is_valid, errors = self.utils.validate_verb("ai", config)
        
        assert is_valid is True
        assert errors == []
    
    def test_validate_verb_missing_required(self) -> None:
        """Test validation with missing required property"""
        config = {"temperature": 0.7}
        
        is_valid, errors = self.utils.validate_verb("ai", config)
        
        assert is_valid is False
        assert len(errors) == 1
        assert "Missing required property 'prompt'" in errors[0]
    
    def test_validate_verb_nonexistent_verb(self) -> None:
        """Test validation with nonexistent verb"""
        config = {"some": "config"}
        
        is_valid, errors = self.utils.validate_verb("nonexistent", config)
        
        assert is_valid is False
        assert len(errors) == 1
        assert "Unknown verb: nonexistent" in errors[0]
    
    def test_validate_verb_extra_properties_allowed(self) -> None:
        """Test validation allows extra properties"""
        config = {"prompt": "You are helpful", "extra_prop": "value"}
        
        is_valid, errors = self.utils.validate_verb("ai", config)
        
        assert is_valid is True
        assert errors == []


class TestCodeGeneration:
    """Test code generation functionality"""
    
    def setup_method(self) -> None:
        """Set up test data"""
        self.utils = SchemaUtils.__new__(SchemaUtils)
        self.utils.verbs = {
            "ai": {
                "name": "ai",
                "schema_name": "AIMethod",
                "definition": {
                    "properties": {
                        "ai": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "The AI prompt text"
                                },
                                "temperature": {
                                    "type": "number",
                                    "description": "Temperature for AI generation"
                                }
                            },
                            "required": ["prompt"]
                        }
                    }
                }
            }
        }
    
    def test_generate_method_signature(self) -> None:
        """Test method signature generation"""
        result = self.utils.generate_method_signature("ai")
        
        assert "def ai(self, prompt: str, temperature: Optional[float] = None, **kwargs) -> bool:" in result
        assert "Add the ai verb to the current document" in result
        assert "prompt: The AI prompt text" in result
        assert "temperature: Temperature for AI generation" in result
    
    def test_generate_method_body(self) -> None:
        """Test method body generation"""
        result = self.utils.generate_method_body("ai")
        
        assert "config = {}" in result
        assert "if prompt is not None:" in result
        assert "config['prompt'] = prompt" in result
        assert "if temperature is not None:" in result
        assert "config['temperature'] = temperature" in result
        assert "return self.add_verb('ai', config)" in result
    
    def test_get_type_annotation_string(self) -> None:
        """Test type annotation for string"""
        param_def = {"type": "string"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "str"
    
    def test_get_type_annotation_integer(self) -> None:
        """Test type annotation for integer"""
        param_def = {"type": "integer"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "int"
    
    def test_get_type_annotation_number(self) -> None:
        """Test type annotation for number"""
        param_def = {"type": "number"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "float"
    
    def test_get_type_annotation_boolean(self) -> None:
        """Test type annotation for boolean"""
        param_def = {"type": "boolean"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "bool"
    
    def test_get_type_annotation_array(self) -> None:
        """Test type annotation for array"""
        param_def = {
            "type": "array",
            "items": {"type": "string"}
        }
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "List[str]"
    
    def test_get_type_annotation_array_no_items(self) -> None:
        """Test type annotation for array without items"""
        param_def = {"type": "array"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "List[Any]"
    
    def test_get_type_annotation_object(self) -> None:
        """Test type annotation for object"""
        param_def = {"type": "object"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "Dict[str, Any]"
    
    def test_get_type_annotation_anyof(self) -> None:
        """Test type annotation for anyOf"""
        param_def = {
            "anyOf": [
                {"type": "string"},
                {"type": "integer"}
            ]
        }
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "Any"
    
    def test_get_type_annotation_ref(self) -> None:
        """Test type annotation for $ref"""
        param_def = {"$ref": "#/$defs/SomeType"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "Any"
    
    def test_get_type_annotation_unknown(self) -> None:
        """Test type annotation for unknown type"""
        param_def = {"type": "unknown"}
        
        result = self.utils._get_type_annotation(param_def)
        
        assert result == "Any"


class TestSchemaUtilsIntegration:
    """Test integration scenarios"""
    
    def test_complete_workflow(self) -> None:
        """Test complete schema utils workflow"""
        schema_data = {
            "$defs": {
                "SWMLMethod": {
                    "anyOf": [
                        {"$ref": "#/$defs/AIMethod"},
                        {"$ref": "#/$defs/PlayMethod"}
                    ]
                },
                "AIMethod": {
                    "properties": {
                        "ai": {
                            "type": "object",
                            "properties": {
                                "prompt": {
                                    "type": "string",
                                    "description": "AI prompt"
                                },
                                "temperature": {
                                    "type": "number",
                                    "description": "Generation temperature"
                                }
                            },
                            "required": ["prompt"]
                        }
                    }
                },
                "PlayMethod": {
                    "properties": {
                        "play": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to play"
                                }
                            },
                            "required": ["url"]
                        }
                    }
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema_data, f)
            schema_path = f.name
        
        try:
            # Initialize with schema
            utils = SchemaUtils(schema_path)
            
            # Test verb discovery
            verb_names = utils.get_all_verb_names()
            assert "ai" in verb_names
            assert "play" in verb_names
            
            # Test validation
            valid_config = {"prompt": "Hello"}
            is_valid, errors = utils.validate_verb("ai", valid_config)
            assert is_valid is True
            
            invalid_config: dict[str, Any] = {}
            is_valid, errors = utils.validate_verb("ai", invalid_config)
            assert is_valid is False
            
            # Test code generation
            signature = utils.generate_method_signature("ai")
            assert "def ai(" in signature
            
            body = utils.generate_method_body("ai")
            assert "add_verb('ai'" in body
            
        finally:
            os.unlink(schema_path)
    
    def test_error_recovery(self) -> None:
        """Test error recovery scenarios"""
        # Test with invalid schema path
        utils = SchemaUtils("/nonexistent/schema.json")
        
        # Should still work with empty schema
        assert utils.get_all_verb_names() == []
        
        # Validation should fail gracefully
        is_valid, errors = utils.validate_verb("ai", {})
        assert is_valid is False
        assert "Unknown verb" in errors[0]
    
    def test_empty_schema_handling(self) -> None:
        """Test handling of empty schema"""
        with patch.object(SchemaUtils, 'load_schema', return_value={}):
            utils = SchemaUtils("/path/to/schema.json")
            
            assert utils.get_all_verb_names() == []
            assert utils.get_verb_properties("ai") == {}
            assert utils.get_verb_parameters("ai") == {}
            
            is_valid, errors = utils.validate_verb("ai", {})
            assert is_valid is False 