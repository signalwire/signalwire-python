"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Unit tests for contexts module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any, Optional

from signalwire.core.contexts import (
    ContextBuilder,
    Context,
    Step,
    GatherInfo,
    GatherQuestion,
    create_simple_context
)


class TestStep:
    """Test Step functionality"""
    
    def test_basic_initialization(self) -> None:
        """Test basic Step initialization"""
        step = Step("greeting")
        
        assert step.name == "greeting"
        assert step._text is None
        assert step._step_criteria is None
        assert step._functions is None
        assert step._valid_steps is None
        assert step._sections == []
    
    def test_set_text(self) -> None:
        """Test setting step text"""
        step = Step("greeting")
        
        result = step.set_text("Hello, how can I help you today?")
        
        assert result is step  # Should return self for chaining
        assert step._text == "Hello, how can I help you today?"
    
    def test_add_section(self) -> None:
        """Test adding POM sections"""
        step = Step("greeting")
        
        result = step.add_section("Introduction", "Welcome to our service")
        
        assert result is step  # Should return self for chaining
        assert len(step._sections) == 1
        assert step._sections[0]["title"] == "Introduction"
        assert step._sections[0]["body"] == "Welcome to our service"
    
    def test_add_bullets(self) -> None:
        """Test adding bullet sections"""
        step = Step("greeting")
        bullets = ["First point", "Second point", "Third point"]
        
        result = step.add_bullets("Key Points", bullets)
        
        assert result is step  # Should return self for chaining
        assert len(step._sections) == 1
        assert step._sections[0]["title"] == "Key Points"
        assert step._sections[0]["bullets"] == bullets
    
    def test_set_step_criteria(self) -> None:
        """Test setting step criteria"""
        step = Step("greeting")
        
        result = step.set_step_criteria("User has provided their name")
        
        assert result is step  # Should return self for chaining
        assert step._step_criteria == "User has provided their name"
    
    def test_set_functions(self) -> None:
        """Test setting available functions"""
        step = Step("greeting")
        
        # Test with function list
        result = step.set_functions(["get_weather", "search"])
        assert result is step
        assert step._functions == ["get_weather", "search"]
        
        # Test with "none"
        step.set_functions("none")
        assert step._functions == "none"  # type: ignore[comparison-overlap]  # testing "none" sentinel
    
    def test_set_valid_steps(self) -> None:
        """Test setting valid steps"""
        step = Step("greeting")
        valid_steps = ["next", "collect_info", "end"]
        
        result = step.set_valid_steps(valid_steps)
        
        assert result is step  # Should return self for chaining
        assert step._valid_steps == valid_steps
    
    def test_text_and_sections_conflict(self) -> None:
        """Test that text and sections cannot be mixed"""
        step = Step("greeting")
        
        # Set text first
        step.set_text("Hello")
        
        # Adding sections should raise error
        with pytest.raises(ValueError, match="Cannot add POM sections when set_text"):
            step.add_section("Title", "Body")
        
        with pytest.raises(ValueError, match="Cannot add POM sections when set_text"):
            step.add_bullets("Title", ["bullet"])
    
    def test_sections_and_text_conflict(self) -> None:
        """Test that sections and text cannot be mixed"""
        step = Step("greeting")
        
        # Add section first
        step.add_section("Title", "Body")
        
        # Setting text should raise error
        with pytest.raises(ValueError, match="Cannot use set_text\\(\\) when POM sections"):
            step.set_text("Hello")
    
    def test_render_text_with_text(self) -> None:
        """Test rendering text when text is set"""
        step = Step("greeting")
        step.set_text("Hello, how can I help you?")
        
        rendered = step._render_text()
        
        assert rendered == "Hello, how can I help you?"
    
    def test_render_text_with_sections(self) -> None:
        """Test rendering text from POM sections"""
        step = Step("greeting")
        step.add_section("Welcome", "Hello there!")
        step.add_bullets("Options", ["Option 1", "Option 2"])
        
        rendered = step._render_text()
        
        assert "## Welcome" in rendered
        assert "Hello there!" in rendered
        assert "## Options" in rendered
        assert "- Option 1" in rendered
        assert "- Option 2" in rendered
    
    def test_render_text_no_content(self) -> None:
        """Test rendering text when no content is set"""
        step = Step("greeting")
        
        with pytest.raises(ValueError, match="Step 'greeting' has no text or POM sections"):
            step._render_text()
    
    def test_to_dict_basic(self) -> None:
        """Test converting step to dictionary"""
        step = Step("greeting")
        step.set_text("Hello!")
        
        result = step.to_dict()
        
        assert result["text"] == "Hello!"
        assert "step_criteria" not in result
        assert "functions" not in result
        assert "valid_steps" not in result
    
    def test_to_dict_complete(self) -> None:
        """Test converting step with all fields to dictionary"""
        step = Step("greeting")
        step.set_text("Hello!")
        step.set_step_criteria("User responds")
        step.set_functions(["search"])
        step.set_valid_steps(["next"])
        
        result = step.to_dict()
        
        assert result["text"] == "Hello!"
        assert result["step_criteria"] == "User responds"
        assert result["functions"] == ["search"]
        assert result["valid_steps"] == ["next"]


class TestContext:
    """Test Context functionality"""
    
    def test_basic_initialization(self) -> None:
        """Test basic Context initialization"""
        context = Context("customer_service")
        
        assert context.name == "customer_service"
        assert context._steps == {}
        assert context._step_order == []
        assert context._valid_contexts is None
    
    def test_add_step(self) -> None:
        """Test adding steps to context"""
        context = Context("customer_service")
        
        step = context.add_step("greeting")
        
        assert isinstance(step, Step)
        assert step.name == "greeting"
        assert "greeting" in context._steps
        assert context._step_order == ["greeting"]
    
    def test_add_multiple_steps(self) -> None:
        """Test adding multiple steps"""
        context = Context("customer_service")
        
        step1 = context.add_step("greeting")
        step2 = context.add_step("collect_info")
        step3 = context.add_step("provide_solution")
        
        assert len(context._steps) == 3
        assert context._step_order == ["greeting", "collect_info", "provide_solution"]
        assert all(isinstance(step, Step) for step in [step1, step2, step3])
    
    def test_add_duplicate_step(self) -> None:
        """Test adding duplicate step names"""
        context = Context("customer_service")
        
        context.add_step("greeting")
        
        with pytest.raises(ValueError, match="Step 'greeting' already exists"):
            context.add_step("greeting")
    
    def test_set_valid_contexts(self) -> None:
        """Test setting valid contexts"""
        context = Context("customer_service")
        valid_contexts = ["sales", "technical_support"]
        
        result = context.set_valid_contexts(valid_contexts)
        
        assert result is context  # Should return self for chaining
        assert context._valid_contexts == valid_contexts
    
    def test_to_dict_basic(self) -> None:
        """Test converting context to dictionary"""
        context = Context("customer_service")
        step = context.add_step("greeting")
        step.set_text("Hello!")
        
        result = context.to_dict()
        
        assert "steps" in result
        assert len(result["steps"]) == 1
        assert result["steps"][0]["text"] == "Hello!"
        assert "valid_contexts" not in result
    
    def test_to_dict_with_valid_contexts(self) -> None:
        """Test converting context with valid contexts"""
        context = Context("customer_service")
        step = context.add_step("greeting")
        step.set_text("Hello!")
        context.set_valid_contexts(["sales"])
        
        result = context.to_dict()
        
        assert "steps" in result
        assert result["valid_contexts"] == ["sales"]
    
    def test_to_dict_no_steps(self) -> None:
        """Test converting context with no steps"""
        context = Context("customer_service")
        
        with pytest.raises(ValueError, match="Context 'customer_service' has no steps"):
            context.to_dict()


class TestContextBuilder:
    """Test ContextBuilder functionality"""
    
    def test_basic_initialization(self) -> None:
        """Test basic ContextBuilder initialization"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        # ContextBuilder doesn't store agent reference, just uses it during init
        assert builder._contexts == {}
    
    def test_add_context(self) -> None:
        """Test adding a context"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        context = builder.add_context("customer_service")
        assert isinstance(context, Context)
        assert "customer_service" in builder._contexts
    
    def test_add_duplicate_context(self) -> None:
        """Test adding duplicate context raises error"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        builder.add_context("customer_service")
        
        # The actual API raises an error for duplicates
        with pytest.raises(ValueError, match="Context 'customer_service' already exists"):
            builder.add_context("customer_service")
    
    def test_validate_success(self) -> None:
        """Test successful validation with default context — returns None
        and the validated config is reachable via to_dict() with the right
        shape."""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)

        context = builder.add_context("default")  # Must be named 'default' for single context
        step = context.add_step("greeting")
        step.set_text("Hello!")

        # validate() returns None when the configuration is valid.
        result = builder.validate()  # type: ignore[func-returns-value]  # validate() returns None; asserting it ran without raising
        assert result is None
        # And the validated structure round-trips through to_dict.
        d = builder.to_dict()
        assert "default" in d
        # Context.to_dict() puts steps in a list of dicts; verify the
        # named step survives the round trip.
        step_names = [s["name"] for s in d["default"]["steps"]]
        assert "greeting" in step_names
    
    def test_validate_no_contexts(self) -> None:
        """Test validation with no contexts"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        with pytest.raises(ValueError, match="At least one context must be defined"):
            builder.validate()
    
    def test_validate_context_no_steps(self) -> None:
        """Test validation with context having no steps"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        builder.add_context("default")  # Must be named 'default' for single context
        
        with pytest.raises(ValueError, match="Context 'default' must have at least one step"):
            builder.validate()
    
    def test_to_dict(self) -> None:
        """Test converting builder to dictionary"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        context = builder.add_context("default")  # Must be named 'default' for single context
        step = context.add_step("greeting")
        step.set_text("Hello!")
        
        result = builder.to_dict()
        assert isinstance(result, dict)
        assert "default" in result


class TestCreateSimpleContext:
    """Test create_simple_context factory function"""
    
    def test_create_simple_context_default(self) -> None:
        """Test creating simple context with default name"""
        context = create_simple_context()
        
        assert isinstance(context, Context)
        assert context.name == "default"
    
    def test_create_simple_context_custom_name(self) -> None:
        """Test creating simple context with custom name"""
        context = create_simple_context("my_context")
        
        assert isinstance(context, Context)
        assert context.name == "my_context"


class TestContextIntegration:
    """Test context integration scenarios"""
    
    def test_complete_context_workflow(self) -> None:
        """Test complete context building workflow with multiple contexts"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        # Create customer service context
        customer_service = builder.add_context("customer_service")
        customer_service.set_valid_contexts(["sales", "technical_support"])
        
        # Add greeting step
        greeting = customer_service.add_step("greeting")
        greeting.set_text("Hello! Welcome to customer service. How can I help you today?")
        greeting.set_step_criteria("User has stated their issue")
        greeting.set_functions(["search_knowledge_base", "escalate_to_human"])
        greeting.set_valid_steps(["next", "gather_info"])  # Use valid step names
        
        # Add information gathering step
        gather_info = customer_service.add_step("gather_info")
        gather_info.add_section("Information Needed", "Please provide the following details:")
        gather_info.add_bullets("Required Information", [
            "Account number or phone number",
            "Description of the issue",
            "When did the issue start?"
        ])
        gather_info.set_step_criteria("All required information has been collected")
        gather_info.set_valid_steps(["next", "greeting"])
        
        # Add resolution step
        resolution = customer_service.add_step("resolution")
        resolution.set_text("Based on the information provided, here's how we can resolve your issue:")
        resolution.set_functions("none")  # No functions needed for final step
        
        # Add the referenced contexts to satisfy validation
        sales = builder.add_context("sales")
        sales_step = sales.add_step("sales_greeting")
        sales_step.set_text("Welcome to sales!")
        
        technical_support = builder.add_context("technical_support")
        tech_step = technical_support.add_step("tech_greeting")
        tech_step.set_text("Welcome to technical support!")
        
        # Validate the complete structure
        builder.validate()
        
        # Convert to dictionary
        result = builder.to_dict()
        assert "customer_service" in result
        assert "sales" in result
        assert "technical_support" in result
        assert len(result["customer_service"]["steps"]) == 3
    
    def test_multiple_contexts(self) -> None:
        """Test building multiple contexts"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        
        # Create sales context
        sales = builder.add_context("sales")
        sales_step = sales.add_step("pitch")
        sales_step.set_text("Let me tell you about our amazing products!")
        
        # Create support context
        support = builder.add_context("support")
        support_step = support.add_step("diagnose")
        support_step.set_text("Let's troubleshoot your issue.")
        
        # Validate and convert
        builder.validate()
        result = builder.to_dict()
        
        # Verify both contexts exist
        assert "sales" in result
        assert "support" in result
        assert len(result["sales"]["steps"]) == 1
        assert len(result["support"]["steps"]) == 1
    
    def test_complex_step_configuration(self) -> None:
        """Test complex step configuration with all features"""
        context = Context("complex")
        
        step = context.add_step("complex_step")
        
        # Use method chaining
        step.add_section("Overview", "This is a complex step with multiple sections") \
            .add_bullets("Features", ["Feature 1", "Feature 2", "Feature 3"]) \
            .add_section("Instructions", "Follow these steps carefully") \
            .set_step_criteria("All features have been demonstrated") \
            .set_functions(["demo_feature_1", "demo_feature_2", "demo_feature_3"]) \
            .set_valid_steps(["next", "previous", "help"])
        
        # Convert to dict and verify
        step_dict = step.to_dict()
        
        # Check that all sections are rendered
        text = step_dict["text"]
        assert "## Overview" in text
        assert "This is a complex step" in text
        assert "## Features" in text
        assert "- Feature 1" in text
        assert "## Instructions" in text
        assert "Follow these steps" in text
        
        # Check other fields
        assert step_dict["step_criteria"] == "All features have been demonstrated"
        assert step_dict["functions"] == ["demo_feature_1", "demo_feature_2", "demo_feature_3"]
        assert step_dict["valid_steps"] == ["next", "previous", "help"]


class TestStepResetAndContextNavigation:
    """Tests for Step reset parameters and context navigation features"""

    def test_set_valid_contexts(self) -> None:
        """Test setting valid contexts on a step"""
        step = Step("transfer")
        result = step.set_valid_contexts(["sales", "support"])
        assert result is step
        assert step._valid_contexts == ["sales", "support"]

    def test_set_reset_system_prompt(self) -> None:
        """Test setting reset system prompt"""
        step = Step("transfer")
        result = step.set_reset_system_prompt("You are a sales agent.")
        assert result is step
        assert step._reset_system_prompt == "You are a sales agent."

    def test_set_reset_user_prompt(self) -> None:
        """Test setting reset user prompt"""
        step = Step("transfer")
        result = step.set_reset_user_prompt("Please help me buy something.")
        assert result is step
        assert step._reset_user_prompt == "Please help me buy something."

    def test_set_reset_consolidate(self) -> None:
        """Test setting reset consolidate flag"""
        step = Step("transfer")
        result = step.set_reset_consolidate(True)
        assert result is step
        assert step._reset_consolidate is True

    def test_set_reset_full_reset(self) -> None:
        """Test setting reset full_reset flag"""
        step = Step("transfer")
        result = step.set_reset_full_reset(True)
        assert result is step
        assert step._reset_full_reset is True

    def test_to_dict_with_valid_contexts(self) -> None:
        """Test to_dict includes valid_contexts when set"""
        step = Step("transfer")
        step.set_text("Transferring you now.")
        step.set_valid_contexts(["sales", "support"])
        result = step.to_dict()
        assert result["valid_contexts"] == ["sales", "support"]

    def test_to_dict_with_partial_reset(self) -> None:
        """Test to_dict includes reset object with only system_prompt"""
        step = Step("transfer")
        step.set_text("Transferring you now.")
        step.set_reset_system_prompt("New system prompt")
        result = step.to_dict()
        assert "reset" in result
        assert result["reset"]["system_prompt"] == "New system prompt"
        assert "user_prompt" not in result["reset"]
        assert "consolidate" not in result["reset"]
        assert "full_reset" not in result["reset"]

    def test_to_dict_with_full_reset_object(self) -> None:
        """Test to_dict includes reset object with all fields"""
        step = Step("transfer")
        step.set_text("Transferring you now.")
        step.set_reset_system_prompt("New system prompt")
        step.set_reset_user_prompt("User message")
        step.set_reset_consolidate(True)
        step.set_reset_full_reset(True)
        result = step.to_dict()
        assert result["reset"]["system_prompt"] == "New system prompt"
        assert result["reset"]["user_prompt"] == "User message"
        assert result["reset"]["consolidate"] is True
        assert result["reset"]["full_reset"] is True

    def test_to_dict_no_reset_when_defaults(self) -> None:
        """Test to_dict omits reset when all reset fields are defaults"""
        step = Step("greeting")
        step.set_text("Hello!")
        result = step.to_dict()
        assert "reset" not in result


class TestContextEntryParameters:
    """Tests for Context entry parameters (system_prompt, consolidate, etc.)"""

    def test_set_post_prompt(self) -> None:
        """Test setting post prompt"""
        context = Context("sales")
        result = context.set_post_prompt("Summarize the conversation")
        assert result is context
        assert context._post_prompt == "Summarize the conversation"

    def test_set_system_prompt(self) -> None:
        """Test setting system prompt"""
        context = Context("sales")
        result = context.set_system_prompt("You are a sales agent.")
        assert result is context
        assert context._system_prompt == "You are a sales agent."

    def test_set_system_prompt_conflict_with_sections(self) -> None:
        """Test that set_system_prompt raises when sections already exist"""
        context = Context("sales")
        context.add_system_section("Role", "You are a sales agent.")
        with pytest.raises(ValueError, match="Cannot use set_system_prompt"):
            context.set_system_prompt("You are a sales agent.")

    def test_set_consolidate(self) -> None:
        """Test setting consolidate flag"""
        context = Context("sales")
        result = context.set_consolidate(True)
        assert result is context
        assert context._consolidate is True

    def test_set_full_reset(self) -> None:
        """Test setting full_reset flag"""
        context = Context("sales")
        result = context.set_full_reset(True)
        assert result is context
        assert context._full_reset is True

    def test_set_user_prompt(self) -> None:
        """Test setting user prompt"""
        context = Context("sales")
        result = context.set_user_prompt("I want to buy something.")
        assert result is context
        assert context._user_prompt == "I want to buy something."

    def test_set_isolated(self) -> None:
        """Test setting isolated flag"""
        context = Context("sales")
        result = context.set_isolated(True)
        assert result is context
        assert context._isolated is True


class TestContextSystemPromptSections:
    """Tests for Context system prompt POM sections"""

    def test_add_system_section(self) -> None:
        """Test adding a POM section to system prompt"""
        context = Context("sales")
        result = context.add_system_section("Role", "You are a sales agent.")
        assert result is context
        assert len(context._system_prompt_sections) == 1
        assert context._system_prompt_sections[0]["title"] == "Role"
        assert context._system_prompt_sections[0]["body"] == "You are a sales agent."

    def test_add_system_section_conflict_with_set_system_prompt(self) -> None:
        """Test that add_system_section raises when set_system_prompt already used"""
        context = Context("sales")
        context.set_system_prompt("You are a sales agent.")
        with pytest.raises(ValueError, match="Cannot add POM sections for system prompt"):
            context.add_system_section("Role", "You are a sales agent.")

    def test_add_system_bullets(self) -> None:
        """Test adding bullet points to system prompt"""
        context = Context("sales")
        result = context.add_system_bullets("Rules", ["Be polite", "Be helpful"])
        assert result is context
        assert len(context._system_prompt_sections) == 1
        assert context._system_prompt_sections[0]["bullets"] == ["Be polite", "Be helpful"]

    def test_add_system_bullets_conflict_with_set_system_prompt(self) -> None:
        """Test that add_system_bullets raises when set_system_prompt already used"""
        context = Context("sales")
        context.set_system_prompt("You are a sales agent.")
        with pytest.raises(ValueError, match="Cannot add POM sections for system prompt"):
            context.add_system_bullets("Rules", ["Be polite"])

    def test_render_system_prompt_with_text(self) -> None:
        """Test _render_system_prompt returns text when set"""
        context = Context("sales")
        context.set_system_prompt("You are a sales agent.")
        assert context._render_system_prompt() == "You are a sales agent."

    def test_render_system_prompt_with_sections(self) -> None:
        """Test _render_system_prompt renders POM sections"""
        context = Context("sales")
        context.add_system_section("Role", "You are a sales agent.")
        context.add_system_bullets("Rules", ["Be polite", "Be helpful"])
        rendered = context._render_system_prompt()
        assert rendered is not None
        assert "## Role" in rendered
        assert "You are a sales agent." in rendered
        assert "## Rules" in rendered
        assert "- Be polite" in rendered
        assert "- Be helpful" in rendered

    def test_render_system_prompt_none(self) -> None:
        """Test _render_system_prompt returns None when nothing is set"""
        context = Context("sales")
        assert context._render_system_prompt() is None


class TestContextPromptSections:
    """Tests for Context prompt (separate from system_prompt) POM sections"""

    def test_set_prompt(self) -> None:
        """Test setting context prompt text"""
        context = Context("sales")
        result = context.set_prompt("Welcome to the sales department.")
        assert result is context
        assert context._prompt_text == "Welcome to the sales department."

    def test_set_prompt_conflict_with_sections(self) -> None:
        """Test that set_prompt raises when sections already exist"""
        context = Context("sales")
        context.add_section("Greeting", "Welcome!")
        with pytest.raises(ValueError, match="Cannot use set_prompt"):
            context.set_prompt("Welcome!")

    def test_add_section(self) -> None:
        """Test adding a section to context prompt"""
        context = Context("sales")
        result = context.add_section("Greeting", "Welcome to our store!")
        assert result is context
        assert len(context._prompt_sections) == 1
        assert context._prompt_sections[0]["title"] == "Greeting"
        assert context._prompt_sections[0]["body"] == "Welcome to our store!"

    def test_add_section_conflict_with_set_prompt(self) -> None:
        """Test that add_section raises when set_prompt already used"""
        context = Context("sales")
        context.set_prompt("Welcome!")
        with pytest.raises(ValueError, match="Cannot add POM sections when set_prompt"):
            context.add_section("Greeting", "Welcome!")

    def test_add_bullets(self) -> None:
        """Test adding bullet points to context prompt"""
        context = Context("sales")
        result = context.add_bullets("Products", ["Widget A", "Widget B"])
        assert result is context
        assert len(context._prompt_sections) == 1
        assert context._prompt_sections[0]["bullets"] == ["Widget A", "Widget B"]

    def test_add_bullets_conflict_with_set_prompt(self) -> None:
        """Test that add_bullets raises when set_prompt already used"""
        context = Context("sales")
        context.set_prompt("Welcome!")
        with pytest.raises(ValueError, match="Cannot add POM sections when set_prompt"):
            context.add_bullets("Products", ["Widget A"])

    def test_render_prompt_with_text(self) -> None:
        """Test _render_prompt returns text when set"""
        context = Context("sales")
        context.set_prompt("Welcome to sales.")
        assert context._render_prompt() == "Welcome to sales."

    def test_render_prompt_with_sections(self) -> None:
        """Test _render_prompt renders POM sections"""
        context = Context("sales")
        context.add_section("Greeting", "Hello!")
        context.add_bullets("Items", ["Item 1", "Item 2"])
        rendered = context._render_prompt()
        assert rendered is not None
        assert "## Greeting" in rendered
        assert "Hello!" in rendered
        assert "## Items" in rendered
        assert "- Item 1" in rendered
        assert "- Item 2" in rendered

    def test_render_prompt_none(self) -> None:
        """Test _render_prompt returns None when nothing is set"""
        context = Context("sales")
        assert context._render_prompt() is None


class TestContextFillers:
    """Tests for Context enter/exit filler functionality"""

    def test_set_enter_fillers(self) -> None:
        """Test setting enter fillers"""
        context = Context("sales")
        fillers = {"en-US": ["Welcome!", "Hello!"], "default": ["Hi!"]}
        result = context.set_enter_fillers(fillers)
        assert result is context
        assert context._enter_fillers == fillers

    def test_set_enter_fillers_empty_dict(self) -> None:
        """Test that empty dict does not set enter fillers"""
        context = Context("sales")
        result = context.set_enter_fillers({})
        assert result is context
        assert context._enter_fillers is None

    def test_set_enter_fillers_non_dict(self) -> None:
        """Test that non-dict does not set enter fillers"""
        context = Context("sales")
        result = context.set_enter_fillers(None)  # type: ignore[arg-type]  # intentional invalid input
        assert result is context
        assert context._enter_fillers is None

    def test_set_exit_fillers(self) -> None:
        """Test setting exit fillers"""
        context = Context("sales")
        fillers = {"en-US": ["Goodbye!", "Thank you!"], "default": ["Bye!"]}
        result = context.set_exit_fillers(fillers)
        assert result is context
        assert context._exit_fillers == fillers

    def test_set_exit_fillers_empty_dict(self) -> None:
        """Test that empty dict does not set exit fillers"""
        context = Context("sales")
        result = context.set_exit_fillers({})
        assert result is context
        assert context._exit_fillers is None

    def test_set_exit_fillers_non_dict(self) -> None:
        """Test that non-dict does not set exit fillers"""
        context = Context("sales")
        result = context.set_exit_fillers(None)  # type: ignore[arg-type]  # intentional invalid input
        assert result is context
        assert context._exit_fillers is None

    def test_add_enter_filler(self) -> None:
        """Test adding enter fillers for a specific language"""
        context = Context("sales")
        result = context.add_enter_filler("en-US", ["Welcome!", "Hello!"])
        assert result is context
        assert context._enter_fillers == {"en-US": ["Welcome!", "Hello!"]}

    def test_add_enter_filler_multiple_languages(self) -> None:
        """Test adding enter fillers for multiple languages"""
        context = Context("sales")
        context.add_enter_filler("en-US", ["Welcome!"])
        context.add_enter_filler("es", ["Bienvenido!"])
        assert context._enter_fillers == {"en-US": ["Welcome!"], "es": ["Bienvenido!"]}

    def test_add_enter_filler_invalid_inputs(self) -> None:
        """Test that invalid inputs to add_enter_filler are ignored"""
        context = Context("sales")
        context.add_enter_filler("", ["Hello!"])
        assert context._enter_fillers is None
        context.add_enter_filler("en-US", [])
        assert context._enter_fillers is None
        context.add_enter_filler("en-US", None)  # type: ignore[arg-type]  # intentional invalid input
        assert context._enter_fillers is None

    def test_add_exit_filler(self) -> None:
        """Test adding exit fillers for a specific language"""
        context = Context("sales")
        result = context.add_exit_filler("en-US", ["Goodbye!", "See you!"])
        assert result is context
        assert context._exit_fillers == {"en-US": ["Goodbye!", "See you!"]}

    def test_add_exit_filler_multiple_languages(self) -> None:
        """Test adding exit fillers for multiple languages"""
        context = Context("sales")
        context.add_exit_filler("en-US", ["Goodbye!"])
        context.add_exit_filler("es", ["Adios!"])
        assert context._exit_fillers == {"en-US": ["Goodbye!"], "es": ["Adios!"]}

    def test_add_exit_filler_invalid_inputs(self) -> None:
        """Test that invalid inputs to add_exit_filler are ignored"""
        context = Context("sales")
        context.add_exit_filler("", ["Bye!"])
        assert context._exit_fillers is None
        context.add_exit_filler("en-US", [])
        assert context._exit_fillers is None
        context.add_exit_filler("en-US", None)  # type: ignore[arg-type]  # intentional invalid input
        assert context._exit_fillers is None


class TestContextToDictComprehensive:
    """Tests for Context.to_dict with various combinations of parameters"""

    def test_to_dict_with_post_prompt(self) -> None:
        """Test to_dict includes post_prompt"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.set_post_prompt("Summarize the conversation")
        result = context.to_dict()
        assert result["post_prompt"] == "Summarize the conversation"

    def test_to_dict_with_system_prompt(self) -> None:
        """Test to_dict includes system_prompt"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.set_system_prompt("You are a sales agent.")
        result = context.to_dict()
        assert result["system_prompt"] == "You are a sales agent."

    def test_to_dict_with_system_sections(self) -> None:
        """Test to_dict renders system prompt from POM sections"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.add_system_section("Role", "You are a sales agent.")
        result = context.to_dict()
        assert "system_prompt" in result
        assert "## Role" in result["system_prompt"]

    def test_to_dict_with_consolidate_and_full_reset(self) -> None:
        """Test to_dict includes consolidate and full_reset"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.set_consolidate(True)
        context.set_full_reset(True)
        result = context.to_dict()
        assert result["consolidate"] is True
        assert result["full_reset"] is True

    def test_to_dict_with_user_prompt(self) -> None:
        """Test to_dict includes user_prompt"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.set_user_prompt("I want to buy something.")
        result = context.to_dict()
        assert result["user_prompt"] == "I want to buy something."

    def test_to_dict_with_isolated(self) -> None:
        """Test to_dict includes isolated"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.set_isolated(True)
        result = context.to_dict()
        assert result["isolated"] is True

    def test_to_dict_with_prompt_text(self) -> None:
        """Test to_dict includes prompt when set_prompt used"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.set_prompt("Welcome to the sales department.")
        result = context.to_dict()
        assert result["prompt"] == "Welcome to the sales department."
        assert "pom" not in result

    def test_to_dict_with_prompt_sections(self) -> None:
        """Test to_dict includes pom when sections added"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.add_section("Greeting", "Welcome!")
        context.add_bullets("Products", ["Widget A", "Widget B"])
        result = context.to_dict()
        assert "pom" in result
        assert "prompt" not in result
        assert len(result["pom"]) == 2

    def test_to_dict_with_enter_and_exit_fillers(self) -> None:
        """Test to_dict includes fillers"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        context.set_enter_fillers({"en-US": ["Welcome!"]})
        context.set_exit_fillers({"en-US": ["Goodbye!"]})
        result = context.to_dict()
        assert result["enter_fillers"] == {"en-US": ["Welcome!"]}
        assert result["exit_fillers"] == {"en-US": ["Goodbye!"]}

    def test_to_dict_omits_defaults(self) -> None:
        """Test to_dict omits fields that are at default values"""
        context = Context("sales")
        context.add_step("greeting").set_text("Hello!")
        result = context.to_dict()
        assert "post_prompt" not in result
        assert "system_prompt" not in result
        assert "consolidate" not in result
        assert "full_reset" not in result
        assert "user_prompt" not in result
        assert "isolated" not in result
        assert "prompt" not in result
        assert "pom" not in result
        assert "enter_fillers" not in result
        assert "exit_fillers" not in result


class TestContextBuilderValidation:
    """Tests for ContextBuilder validation edge cases"""

    def test_validate_single_context_not_named_default(self) -> None:
        """Test validation fails when single context is not named 'default'"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        context = builder.add_context("custom_name")
        context.add_step("greeting").set_text("Hello!")
        with pytest.raises(ValueError, match="single context, it must be named 'default'"):
            builder.validate()

    def test_validate_invalid_step_reference(self) -> None:
        """Test validation fails when valid_steps references unknown step"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        context = builder.add_context("default")
        step = context.add_step("greeting")
        step.set_text("Hello!")
        step.set_valid_steps(["nonexistent_step"])
        with pytest.raises(ValueError, match="references unknown step 'nonexistent_step'"):
            builder.validate()

    def test_validate_next_is_allowed_in_valid_steps(self) -> None:
        """Test validation allows 'next' as a valid step reference — it is
        a reserved keyword that the validator must accept without resolving
        it as a real step name."""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        context = builder.add_context("default")
        step = context.add_step("greeting")
        step.set_text("Hello!")
        step.set_valid_steps(["next"])
        # validate() returns None and "next" was preserved on the step.
        assert builder.validate() is None  # type: ignore[func-returns-value]  # validate() returns None; asserting it ran without raising
        d = builder.to_dict()
        greeting = d["default"]["steps"][0]
        assert greeting["valid_steps"] == ["next"]

    def test_validate_invalid_context_reference_at_context_level(self) -> None:
        """Test validation fails for unknown context in context-level valid_contexts"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        ctx1 = builder.add_context("ctx1")
        ctx1.add_step("s1").set_text("Hello!")
        ctx1.set_valid_contexts(["nonexistent_context"])
        ctx2 = builder.add_context("ctx2")
        ctx2.add_step("s2").set_text("Hi!")
        with pytest.raises(ValueError, match="Context 'ctx1' references unknown context 'nonexistent_context'"):
            builder.validate()

    def test_validate_invalid_context_reference_at_step_level(self) -> None:
        """Test validation fails for unknown context in step-level valid_contexts"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        ctx1 = builder.add_context("ctx1")
        step = ctx1.add_step("s1")
        step.set_text("Hello!")
        step.set_valid_contexts(["nonexistent_context"])
        ctx2 = builder.add_context("ctx2")
        ctx2.add_step("s2").set_text("Hi!")
        with pytest.raises(ValueError, match="references unknown context 'nonexistent_context'"):
            builder.validate()

    def test_validate_valid_context_references(self) -> None:
        """Test validation passes with valid context references at BOTH the
        context level and the step level. The to_dict() output must reflect
        both references (proving validation didn't strip them)."""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        ctx1 = builder.add_context("ctx1")
        step1 = ctx1.add_step("s1")
        step1.set_text("Hello!")
        step1.set_valid_contexts(["ctx2"])
        ctx1.set_valid_contexts(["ctx2"])
        ctx2 = builder.add_context("ctx2")
        ctx2.add_step("s2").set_text("Hi!")
        # Returns None on success; both refs survive serialisation.
        assert builder.validate() is None  # type: ignore[func-returns-value]  # validate() returns None; asserting it ran without raising
        d = builder.to_dict()
        assert d["ctx1"]["valid_contexts"] == ["ctx2"]
        assert d["ctx1"]["steps"][0]["valid_contexts"] == ["ctx2"]

    def test_to_dict_preserves_order(self) -> None:
        """Test that to_dict preserves context insertion order"""
        mock_agent = Mock()
        builder = ContextBuilder(mock_agent)
        ctx1 = builder.add_context("alpha")
        ctx1.add_step("s1").set_text("A")
        ctx2 = builder.add_context("beta")
        ctx2.add_step("s2").set_text("B")
        ctx3 = builder.add_context("gamma")
        ctx3.add_step("s3").set_text("C")
        result = builder.to_dict()
        assert list(result.keys()) == ["alpha", "beta", "gamma"]


# ---------------------------------------------------------------------------
# GatherInfo / GatherQuestion
# ---------------------------------------------------------------------------

class TestGatherQuestion:
    """Test GatherQuestion class"""

    def test_basic_question(self) -> None:
        q = GatherQuestion(key="name", question="What is your name?")
        d = q.to_dict()
        assert d == {"key": "name", "question": "What is your name?"}

    def test_question_with_all_fields(self) -> None:
        q = GatherQuestion(
            key="email", question="Email?", type="string",
            confirm=True, prompt="Be precise", functions=["validate_email"]
        )
        d = q.to_dict()
        assert d["key"] == "email"
        assert d["confirm"] is True
        assert d["prompt"] == "Be precise"
        assert d["functions"] == ["validate_email"]

    def test_default_type_not_included(self) -> None:
        q = GatherQuestion(key="x", question="Q?")
        assert "type" not in q.to_dict()

    def test_non_default_type_included(self) -> None:
        q = GatherQuestion(key="age", question="Age?", type="integer")
        assert q.to_dict()["type"] == "integer"


class TestGatherInfo:
    """Test GatherInfo class"""

    def test_basic_gather_info(self) -> None:
        gi = GatherInfo()
        gi.add_question("name", "What is your name?")
        d = gi.to_dict()
        assert "questions" in d
        assert len(d["questions"]) == 1

    def test_gather_info_with_all_params(self) -> None:
        gi = GatherInfo(output_key="profile", completion_action="next_step",
                        prompt="Welcome!")
        gi.add_question("name", "Name?")
        d = gi.to_dict()
        assert d["output_key"] == "profile"
        assert d["completion_action"] == "next_step"
        assert d["prompt"] == "Welcome!"

    def test_gather_info_no_questions_raises(self) -> None:
        gi = GatherInfo()
        with pytest.raises(ValueError, match="at least one question"):
            gi.to_dict()

    def test_method_chaining(self) -> None:
        gi = GatherInfo()
        result = gi.add_question("a", "Q1?").add_question("b", "Q2?")
        assert result is gi
        assert len(gi._questions) == 2

    def test_completion_action_passed_as_is(self) -> None:
        gi = GatherInfo(completion_action="my_custom_step")
        gi.add_question("x", "Q?")
        assert gi.to_dict()["completion_action"] == "my_custom_step"


class TestStepGatherInfo:
    """Test Step gather_info integration"""

    def test_set_gather_info_and_add_questions(self) -> None:
        step = Step("intake")
        step.set_text("Collect info")
        step.set_gather_info(output_key="data", completion_action="next_step")
        step.add_gather_question("name", "Name?")
        step.add_gather_question("email", "Email?", confirm=True)
        d = step.to_dict()
        assert "gather_info" in d
        assert d["gather_info"]["output_key"] == "data"
        assert len(d["gather_info"]["questions"]) == 2

    def test_add_gather_question_without_set_gather_info_raises(self) -> None:
        step = Step("s")
        with pytest.raises(ValueError, match="Must call set_gather_info"):
            step.add_gather_question("key", "Q?")

    def test_gather_info_completion_action_named_step(self) -> None:
        step = Step("s")
        step.set_text("Go")
        step.set_gather_info(completion_action="review")
        step.add_gather_question("x", "Q?")
        d = step.to_dict()
        assert d["gather_info"]["completion_action"] == "review"


class TestGatherInfoValidation:
    """Test ContextBuilder validation of gather_info completion_action"""

    def _make_builder(self) -> ContextBuilder:
        return ContextBuilder(Mock())

    def test_next_step_valid_when_following_step_exists(self) -> None:
        """When `completion_action='next_step'` is set on a step that has a
        following step in the same context, validate() must accept it."""
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("gather") \
            .set_text("Gather") \
            .set_gather_info(completion_action="next_step") \
            .add_gather_question("name", "Name?")
        ctx.add_step("process").set_text("Process")
        # validate() returns None and to_dict() preserves the action verbatim.
        assert builder.validate() is None  # type: ignore[func-returns-value]  # validate() returns None; asserting it ran without raising
        d = builder.to_dict()
        gather_step = d["default"]["steps"][0]
        assert gather_step["gather_info"]["completion_action"] == "next_step"

    def test_next_step_invalid_on_last_step(self) -> None:
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("only_step") \
            .set_text("Gather") \
            .set_gather_info(completion_action="next_step") \
            .add_gather_question("name", "Name?")
        with pytest.raises(ValueError, match="last step"):
            builder.validate()

    def test_named_step_valid(self) -> None:
        """When `completion_action` names a step that exists ANYWHERE in
        the same context (not necessarily the next one), validate() must
        accept it."""
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("gather") \
            .set_text("Gather") \
            .set_gather_info(completion_action="review") \
            .add_gather_question("name", "Name?")
        ctx.add_step("middle").set_text("Middle")
        ctx.add_step("review").set_text("Review")
        assert builder.validate() is None  # type: ignore[func-returns-value]  # validate() returns None; asserting it ran without raising
        d = builder.to_dict()
        # The named step is preserved and the target step exists in the dict.
        step_names = [s["name"] for s in d["default"]["steps"]]
        assert "review" in step_names
        gather_step = next(s for s in d["default"]["steps"] if s["name"] == "gather")
        assert gather_step["gather_info"]["completion_action"] == "review"

    def test_named_step_invalid_when_not_defined(self) -> None:
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("gather") \
            .set_text("Gather") \
            .set_gather_info(completion_action="nonexistent") \
            .add_gather_question("name", "Name?")
        ctx.add_step("other").set_text("Other")
        with pytest.raises(ValueError, match="is not a step in this context"):
            builder.validate()

    def test_no_completion_action_always_valid(self) -> None:
        """When no `completion_action` is set on gather_info, validate()
        must always accept it — even on the last (only) step in the
        context. The gather_info dict in the output must NOT contain a
        completion_action key."""
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("only_step") \
            .set_text("Gather") \
            .set_gather_info() \
            .add_gather_question("name", "Name?")
        assert builder.validate() is None  # type: ignore[func-returns-value]  # validate() returns None; asserting it ran without raising
        d = builder.to_dict()
        only_step = d["default"]["steps"][0]
        # No completion_action was set, so it must not appear in the output.
        assert "completion_action" not in only_step["gather_info"]

    def test_next_step_valid_not_last_in_multi_step(self) -> None:
        """In a context with three steps where step1 and step2 both use
        `completion_action='next_step'`, validate() must accept BOTH
        because each has a following step."""
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("step1") \
            .set_text("S1") \
            .set_gather_info(completion_action="next_step") \
            .add_gather_question("a", "Q?")
        ctx.add_step("step2") \
            .set_text("S2") \
            .set_gather_info(completion_action="next_step") \
            .add_gather_question("b", "Q?")
        ctx.add_step("step3").set_text("S3")
        assert builder.validate() is None  # type: ignore[func-returns-value]  # validate() returns None; asserting it ran without raising
        d = builder.to_dict()
        names = [s["name"] for s in d["default"]["steps"]]
        # Both gather steps remain present; step3 (the terminal) was
        # what made the next_step refs valid.
        assert names == ["step1", "step2", "step3"]
        assert d["default"]["steps"][0]["gather_info"]["completion_action"] == "next_step"
        assert d["default"]["steps"][1]["gather_info"]["completion_action"] == "next_step"

    def test_second_to_last_next_step_valid_last_next_step_invalid(self) -> None:
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("s1").set_text("S1")
        ctx.add_step("s2") \
            .set_text("S2") \
            .set_gather_info(completion_action="next_step") \
            .add_gather_question("x", "Q?")
        # s2 is the last step
        with pytest.raises(ValueError, match="last step"):
            builder.validate()


class TestStepFunctionsSerialization:
    """Pinning tests for Step.set_functions semantics in to_dict output."""

    def test_omitted_functions_key_absent_from_dict(self) -> None:
        """If set_functions() is never called, the resulting step dict
        must NOT contain a 'functions' key — that omission is what tells
        the C runtime to inherit the previous step's active set.
        """
        step = Step("s")
        step.set_text("hi")
        d = step.to_dict()
        assert "functions" not in d, (
            "Step with no set_functions() call must omit the key entirely "
            "so the runtime applies inheritance semantics."
        )

    def test_explicit_empty_list_persists(self) -> None:
        """functions=[] is the documented disable-all form. It must
        round-trip into the dict so the runtime sees the empty list."""
        step = Step("s")
        step.set_text("hi")
        step.set_functions([])
        d = step.to_dict()
        assert d["functions"] == []

    def test_none_string_persists_as_synonym(self) -> None:
        """functions="none" is a Python convenience; it should appear
        in the dict so the runtime treats it like an empty list."""
        step = Step("s")
        step.set_text("hi")
        step.set_functions("none")
        d = step.to_dict()
        assert d["functions"] == "none"

    def test_explicit_list_round_trips(self) -> None:
        step = Step("s")
        step.set_text("hi")
        step.set_functions(["a", "b"])
        d = step.to_dict()
        assert d["functions"] == ["a", "b"]


class TestReservedToolNameValidation:
    """ContextBuilder.validate() must reject user tools that collide
    with reserved native tool names (next_step / change_context / gather_submit)."""

    def _make_agent_with_tools(self, tool_names: List[str]) -> Mock:
        """Build a mock agent that exposes a real dict of registered tools
        at agent._tool_registry._swaig_functions, matching the structure
        the production code reads from."""
        agent = Mock()
        agent._tool_registry = Mock()
        agent._tool_registry._swaig_functions = {name: Mock() for name in tool_names}
        return agent

    def _builder_with_minimal_context(self, agent: Mock) -> ContextBuilder:
        builder = ContextBuilder(agent)
        ctx = builder.add_context("default")
        ctx.add_step("only").set_text("Step text")
        return builder

    def test_collision_with_next_step_rejected(self) -> None:
        agent = self._make_agent_with_tools(["next_step", "lookup"])
        builder = self._builder_with_minimal_context(agent)
        with pytest.raises(ValueError, match="next_step"):
            builder.validate()

    def test_collision_with_change_context_rejected(self) -> None:
        agent = self._make_agent_with_tools(["change_context"])
        builder = self._builder_with_minimal_context(agent)
        with pytest.raises(ValueError, match="reserved"):
            builder.validate()

    def test_collision_with_gather_submit_rejected(self) -> None:
        agent = self._make_agent_with_tools(["gather_submit", "search"])
        builder = self._builder_with_minimal_context(agent)
        with pytest.raises(ValueError, match="gather_submit"):
            builder.validate()

    def test_no_collision_passes(self) -> None:
        agent = self._make_agent_with_tools(["lookup_account", "send_email"])
        builder = self._builder_with_minimal_context(agent)
        builder.validate()  # should not raise

    def test_empty_tool_registry_passes(self) -> None:
        agent = self._make_agent_with_tools([])
        builder = self._builder_with_minimal_context(agent)
        builder.validate()  # should not raise

    def test_mock_agent_does_not_trigger_check(self) -> None:
        """Plain Mock() agents (used throughout the existing test suite)
        must not accidentally trip the collision check — the real check
        only fires when _swaig_functions is an actual dict."""
        builder = self._builder_with_minimal_context(Mock())
        builder.validate()  # should not raise


class TestImprovedCompletionActionErrorMessage:
    """The completion_action validation errors should be actionable."""

    def _make_builder(self) -> ContextBuilder:
        return ContextBuilder(Mock())

    def test_next_step_on_last_step_error_lists_remediations(self) -> None:
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("only") \
            .set_text("Last step") \
            .set_gather_info(completion_action="next_step") \
            .add_gather_question("x", "Q?")
        try:
            builder.validate()
            assert False, "expected ValueError"
        except ValueError as e:
            msg = str(e)
            # Suggestions an LLM can act on:
            assert "add another step" in msg
            assert "completion_action=None" in msg

    def test_unknown_step_error_lists_available_steps(self) -> None:
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("alpha").set_text("A")
        ctx.add_step("beta") \
            .set_text("B") \
            .set_gather_info(completion_action="gamma") \
            .add_gather_question("x", "Q?")
        try:
            builder.validate()
            assert False, "expected ValueError"
        except ValueError as e:
            msg = str(e)
            assert "is not a step in this context" in msg
            # Should enumerate the legal options
            assert "alpha" in msg
            assert "beta" in msg


class TestInitialStep:
    """Tests for Context.set_initial_step and its to_dict / validation."""

    def _make_builder(self) -> ContextBuilder:
        return ContextBuilder(Mock())

    def test_set_initial_step_round_trips_to_dict(self) -> None:
        ctx = Context("default")
        ctx.add_step("greeting").set_text("Hello")
        ctx.add_step("triage").set_text("What?")
        ctx.set_initial_step("triage")
        d = ctx.to_dict()
        assert d["initial_step"] == "triage"

    def test_omitted_initial_step_absent_from_dict(self) -> None:
        ctx = Context("default")
        ctx.add_step("greeting").set_text("Hello")
        d = ctx.to_dict()
        assert "initial_step" not in d

    def test_validation_accepts_valid_initial_step(self) -> None:
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("a").set_text("A")
        ctx.add_step("b").set_text("B")
        ctx.set_initial_step("b")
        builder.validate()  # should not raise

    def test_validation_rejects_invalid_initial_step(self) -> None:
        builder = self._make_builder()
        ctx = builder.add_context("default")
        ctx.add_step("a").set_text("A")
        ctx.set_initial_step("nonexistent")
        with pytest.raises(ValueError, match="initial_step='nonexistent'"):
            builder.validate()


class TestContextBuilderReset:
    """Tests for ContextBuilder.reset() and AgentBase.reset_contexts()."""

    def _make_builder(self) -> ContextBuilder:
        agent = Mock()
        agent._tool_registry = None
        return ContextBuilder(agent)

    def test_reset_clears_all_contexts(self) -> None:
        builder = self._make_builder()
        builder.add_context("default").add_step("s").set_text("T")
        assert len(builder._contexts) > 0
        builder.reset()
        assert len(builder._contexts) == 0
        assert len(builder._context_order) == 0

    def test_reset_returns_self(self) -> None:
        builder = self._make_builder()
        result = builder.reset()
        assert result is builder

    def test_reset_allows_rebuilding(self) -> None:
        builder = self._make_builder()
        builder.add_context("default").add_step("s1").set_text("First")
        builder.reset()
        ctx = builder.add_context("default")
        ctx.add_step("s2").set_text("Second")
        builder.validate()  # should not raise
        result = builder.to_dict()
        # steps in to_dict is a list of step dicts
        step_names = [s["name"] for s in result["default"]["steps"]]
        assert "s2" in step_names
        assert "s1" not in step_names

    def test_reset_on_empty_builder(self) -> None:
        builder = self._make_builder()
        builder.reset()  # should not raise
        assert len(builder._contexts) == 0

class TestHistoryMode:
    """Step/context `history` visibility mode (keep | default | hide)."""

    def test_step_history_emitted(self) -> None:
        step = Step("s").set_text("t").set_history("hide")
        assert step.to_dict()["history"] == "hide"

    def test_step_history_absent_by_default(self) -> None:
        step = Step("s").set_text("t")
        assert "history" not in step.to_dict()

    def test_step_history_keep(self) -> None:
        assert Step("s").set_text("t").set_history("keep").to_dict()["history"] == "keep"

    def test_step_history_default_is_emitted_when_explicit(self) -> None:
        # Explicit "default" is still written out — it overrides a context default
        assert Step("s").set_text("t").set_history("default").to_dict()["history"] == "default"

    def test_step_history_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="history must be one of"):
            Step("s").set_history("bogus")

    def test_step_history_is_chainable(self) -> None:
        step = Step("s")
        assert step.set_history("hide") is step

    def test_context_history_emitted(self) -> None:
        ctx = Context("c")
        ctx.set_history("keep")
        ctx.add_step("s").set_text("t")
        assert ctx.to_dict()["history"] == "keep"

    def test_context_history_absent_by_default(self) -> None:
        ctx = Context("c")
        ctx.add_step("s").set_text("t")
        assert "history" not in ctx.to_dict()

    def test_context_history_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="history must be one of"):
            Context("c").set_history("nope")

    def test_step_history_overrides_context_in_swml(self) -> None:
        """Both are emitted; the runtime resolves step -> context -> default."""
        ctx = Context("c")
        ctx.set_history("keep")
        ctx.add_step("s").set_text("t").set_history("hide")
        d = ctx.to_dict()
        assert d["history"] == "keep"
        assert d["steps"][0]["history"] == "hide"


class TestGatherIsolated:
    """gather_info.isolated and per-question isolated overrides."""

    def test_gather_isolated_emitted(self) -> None:
        g = GatherInfo(isolated=True)
        g.add_question("k", "Q?")
        assert g.to_dict()["isolated"] is True

    def test_gather_isolated_absent_by_default(self) -> None:
        g = GatherInfo()
        g.add_question("k", "Q?")
        assert "isolated" not in g.to_dict()

    def test_question_isolated_absent_by_default(self) -> None:
        q = GatherQuestion(key="k", question="Q?")
        assert "isolated" not in q.to_dict()

    def test_question_isolated_true(self) -> None:
        q = GatherQuestion(key="k", question="Q?", isolated=True)
        assert q.to_dict()["isolated"] is True

    def test_question_isolated_false_is_emitted(self) -> None:
        """False must survive to SWML so it can override an isolated gather."""
        q = GatherQuestion(key="k", question="Q?", isolated=False)
        assert q.to_dict()["isolated"] is False

    def test_step_gather_isolated_roundtrip(self) -> None:
        step = Step("collect").set_text("t")
        step.set_gather_info(output_key="cust", isolated=True)
        step.add_gather_question("name", "Your name?")
        step.add_gather_question("zip", "Your ZIP?", isolated=False)

        gather = step.to_dict()["gather_info"]
        assert gather["isolated"] is True
        assert gather["output_key"] == "cust"
        assert "isolated" not in gather["questions"][0]
        assert gather["questions"][1]["isolated"] is False
