"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for POM builder module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

# signalwire.pom is now vendored inside this package, so no mocks needed at import time
from signalwire.core.pom_builder import PomBuilder


class TestPomBuilder:
    """Test PomBuilder functionality"""
    
    def test_basic_initialization(self):
        """Test basic PomBuilder initialization"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            builder = PomBuilder()
            
            assert mock_pom.called
            assert builder._sections == {}
    
    def test_add_section_basic(self):
        """Test adding a basic section"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            result = builder.add_section("Introduction", "This is the introduction section.")
            
            assert result is builder  # Should return self for chaining
            mock_pom.return_value.add_section.assert_called_with(
                title="Introduction",
                body="This is the introduction section.",
                bullets=[],
                numbered=False,
                numberedBullets=False
            )
            assert builder._sections["Introduction"] == mock_section
    
    def test_add_section_with_options(self):
        """Test adding a section with various options"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            bullets = ["Point 1", "Point 2"]
            
            result = builder.add_section(
                "Features", 
                "Key features:",
                bullets=bullets,
                numbered=True,
                numbered_bullets=True
            )
            
            assert result is builder
            mock_pom.return_value.add_section.assert_called_with(
                title="Features",
                body="Key features:",
                bullets=bullets,
                numbered=True,
                numberedBullets=True
            )
    
    def test_add_section_with_subsections(self):
        """Test adding a section with subsections"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            subsections = [
                {"title": "Sub 1", "body": "Content 1"},
                {"title": "Sub 2", "body": "Content 2", "bullets": ["bullet1"]}
            ]
            
            builder.add_section("Main Section", "Main content", subsections=subsections)
            
            # Verify subsections were added
            assert mock_section.add_subsection.call_count == 2
            mock_section.add_subsection.assert_any_call(
                title="Sub 1",
                body="Content 1",
                bullets=[]
            )
            mock_section.add_subsection.assert_any_call(
                title="Sub 2",
                body="Content 2",
                bullets=["bullet1"]
            )
    
    def test_add_to_section_new_section(self):
        """Test adding content to a new section (auto-vivification)"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.body = ""
            mock_section.bullets = []
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            result = builder.add_to_section("New Section", body="Some content")
            
            assert result is builder
            # Should have created the section first
            mock_pom.return_value.add_section.assert_called()
            assert mock_section.body == "Some content"
    
    def test_add_to_section_existing_section(self):
        """Test adding content to an existing section"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.body = "Existing content"
            mock_section.bullets = []
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            builder.add_section("Existing Section")
            
            result = builder.add_to_section("Existing Section", body="Additional content")
            
            assert result is builder
            assert mock_section.body == "Existing content\n\nAdditional content"
    
    def test_add_to_section_bullets(self):
        """Test adding bullets to a section"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.bullets = []
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            builder.add_section("Test Section")
            
            # Add single bullet
            builder.add_to_section("Test Section", bullet="Single bullet")
            assert "Single bullet" in mock_section.bullets
            
            # Add multiple bullets - fix the mock expectation
            mock_section.bullets = Mock()  # Make bullets a mock with extend method
            builder.add_to_section("Test Section", bullets=["Bullet 1", "Bullet 2"])
            mock_section.bullets.extend.assert_called_with(["Bullet 1", "Bullet 2"])
    
    def test_add_subsection(self):
        """Test adding subsections"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_parent_section = Mock()
            mock_subsection = Mock()
            mock_parent_section.add_subsection.return_value = mock_subsection
            mock_pom.return_value.add_section.return_value = mock_parent_section
            
            builder = PomBuilder()
            builder.add_section("Parent Section")
            
            result = builder.add_subsection(
                "Parent Section", 
                "Subsection Title", 
                "Subsection body",
                bullets=["bullet1", "bullet2"]
            )
            
            assert result is builder
            mock_parent_section.add_subsection.assert_called_with(
                title="Subsection Title",
                body="Subsection body",
                bullets=["bullet1", "bullet2"]
            )
    
    def test_add_subsection_auto_vivification(self):
        """Test adding subsection with auto-creation of parent"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_parent_section = Mock()
            mock_pom.return_value.add_section.return_value = mock_parent_section
            
            builder = PomBuilder()
            
            # Add subsection to non-existent parent
            builder.add_subsection("New Parent", "Subsection", "Content")
            
            # Should have created parent section
            mock_pom.return_value.add_section.assert_called()
            mock_parent_section.add_subsection.assert_called()
    
    def test_has_section(self):
        """Test checking if section exists"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            
            assert not builder.has_section("Nonexistent")
            
            builder.add_section("Existing Section")
            assert builder.has_section("Existing Section")
    
    def test_get_section(self):
        """Test getting section by title"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            
            assert builder.get_section("Nonexistent") is None
            
            builder.add_section("Test Section")
            assert builder.get_section("Test Section") == mock_section
    
    def test_render_methods(self):
        """Test rendering methods"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_pom.return_value.render_markdown.return_value = "# Markdown"
            mock_pom.return_value.render_xml.return_value = "<xml>content</xml>"
            
            builder = PomBuilder()
            
            assert builder.render_markdown() == "# Markdown"
            assert builder.render_xml() == "<xml>content</xml>"
            
            mock_pom.return_value.render_markdown.assert_called_once()
            mock_pom.return_value.render_xml.assert_called_once()
    
    def test_to_dict_and_to_json(self):
        """Test conversion methods"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_dict = [{"title": "Section", "body": "Content"}]
            mock_json = '{"sections": []}'
            mock_pom.return_value.to_dict.return_value = mock_dict
            mock_pom.return_value.to_json.return_value = mock_json
            
            builder = PomBuilder()
            
            assert builder.to_dict() == mock_dict
            assert builder.to_json() == mock_json
            
            mock_pom.return_value.to_dict.assert_called_once()
            mock_pom.return_value.to_json.assert_called_once()
    
    def test_from_sections_classmethod(self):
        """Test creating PomBuilder from sections"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_pom_instance = Mock()
            # Fix the mock to have iterable sections
            mock_pom_instance.sections = [Mock(name="section1"), Mock(name="section2")]
            mock_pom.from_json.return_value = mock_pom_instance
            
            sections = [{"title": "Section 1", "body": "Content 1"}]
            
            builder = PomBuilder.from_sections(sections)
            assert builder.pom is mock_pom_instance
            mock_pom.from_json.assert_called_once_with(sections)
    
    def test_method_chaining(self):
        """Test method chaining functionality"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.bullets = []
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            
            # Test chaining multiple operations
            result = (builder
                     .add_section("Section 1", "Content 1")
                     .add_section("Section 2", "Content 2")
                     .add_to_section("Section 1", bullet="New bullet")
                     .add_subsection("Section 2", "Subsection", "Sub content"))
            
            assert result is builder
            assert mock_pom.return_value.add_section.call_count == 2


class TestPomBuilderIntegration:
    """Test PomBuilder integration scenarios"""
    
    def test_complex_document_building(self):
        """Test building a complex document structure"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.bullets = []
            mock_section.body = ""
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            
            # Build a complex document
            builder.add_section("Introduction", "Welcome to our guide")
            
            builder.add_section("Features", "Key features include:")
            builder.add_to_section("Features", bullets=[
                "Easy to use",
                "Highly configurable",
                "Well documented"
            ])
            
            builder.add_section("Getting Started")
            builder.add_subsection("Getting Started", "Installation", "Run pip install...")
            builder.add_subsection("Getting Started", "Configuration", "Set up your config...")
            
            builder.add_section("Advanced Topics", numbered=True)
            builder.add_to_section("Advanced Topics", body="For advanced users...")
            
            # Verify the structure was built correctly
            assert len(builder._sections) == 4
            assert "Introduction" in builder._sections
            assert "Features" in builder._sections
            assert "Getting Started" in builder._sections
            assert "Advanced Topics" in builder._sections
    
    def test_agent_prompt_building(self):
        """Test building agent prompts using PomBuilder"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.bullets = []
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            
            # Build a comprehensive agent prompt
            builder.add_section(
                "Role Definition",
                "You are a helpful customer service agent."
            )
            
            builder.add_section("Capabilities")
            builder.add_to_section("Capabilities", bullets=[
                "Answer questions about products",
                "Help with account issues",
                "Escalate complex problems"
            ])
            
            builder.add_section("Guidelines")
            builder.add_subsection("Guidelines", "Tone", "Always be polite and professional")
            builder.add_subsection("Guidelines", "Accuracy", "Provide accurate information")
            
            builder.add_section("Escalation", "When to escalate:")
            builder.add_to_section("Escalation", bullets=[
                "Technical issues beyond scope",
                "Billing disputes over $100",
                "Customer requests supervisor"
            ])
            
            # Verify the prompt structure
            assert len(builder._sections) == 4
            assert builder.has_section("Role Definition")
            assert builder.has_section("Capabilities")
            assert builder.has_section("Guidelines")
            assert builder.has_section("Escalation")
    
    def test_documentation_generation(self):
        """Test generating API documentation"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.bullets = []
            mock_section.body = ""
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            
            # Build API documentation
            builder.add_section("API Overview", "This API provides...")
            
            builder.add_section("Authentication")
            builder.add_to_section("Authentication", body="All requests require authentication")
            builder.add_subsection("Authentication", "API Keys", "Use Bearer tokens")
            builder.add_subsection("Authentication", "Rate Limits", "1000 requests per hour")
            
            builder.add_section("Endpoints")
            
            # Add endpoint documentation
            endpoints = [
                ("GET /users", "Retrieve user list"),
                ("POST /users", "Create new user"),
                ("GET /users/{id}", "Get specific user"),
                ("PUT /users/{id}", "Update user"),
                ("DELETE /users/{id}", "Delete user")
            ]
            
            for endpoint, description in endpoints:
                builder.add_subsection("Endpoints", endpoint, description)
            
            builder.add_section("Examples")
            builder.add_to_section("Examples", body="Here are some usage examples:")
            
            # Verify documentation structure
            assert len(builder._sections) == 4
            assert builder.has_section("API Overview")
            assert builder.has_section("Authentication")
            assert builder.has_section("Endpoints")
            assert builder.has_section("Examples")
    
    def test_error_recovery_and_flexibility(self):
        """Test error recovery and flexible usage patterns"""
        with patch('signalwire.core.pom_builder.PromptObjectModel') as mock_pom:
            mock_section = Mock()
            mock_section.bullets = []
            mock_section.body = ""
            mock_pom.return_value.add_section.return_value = mock_section
            
            builder = PomBuilder()
            
            # Test adding content to non-existent sections (auto-vivification)
            builder.add_to_section("Auto Created", body="This section was auto-created")
            assert builder.has_section("Auto Created")
            
            # Test adding subsections to non-existent parents
            builder.add_subsection("Another Auto", "Sub", "Subsection content")
            assert builder.has_section("Another Auto")
            
            # Test multiple additions to same section
            builder.add_to_section("Auto Created", bullet="First bullet")
            builder.add_to_section("Auto Created", bullets=["Second", "Third"])
            builder.add_to_section("Auto Created", body="Additional content")
            
            # Verify flexibility
            assert len(builder._sections) == 2
            assert builder.get_section("Auto Created") is not None
            assert builder.get_section("Another Auto") is not None 