"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
FAQBotAgent - Prefab agent for answering frequently asked questions
"""

from typing import List, Dict, Any, Optional, Union
import json
import os

from signalwire.core.agent_base import AgentBase
from signalwire.core.function_result import FunctionResult


class FAQBotAgent(AgentBase):
    """
    A prefab agent designed to answer frequently asked questions based on
    a provided list of question/answer pairs.
    
    This agent will:
    1. Match user questions against the FAQ database
    2. Provide the most relevant answer
    3. Suggest other relevant questions when appropriate
    
    Example:
        agent = FAQBotAgent(
            faqs=[
                {
                    "question": "What is SignalWire?",
                    "answer": "SignalWire is a developer-friendly cloud communications platform."
                },
                {
                    "question": "How much does it cost?",
                    "answer": "SignalWire offers pay-as-you-go pricing with no monthly fees."
                }
            ]
        )
    """
    
    def __init__(
        self,
        faqs: List[Dict[str, str]],
        suggest_related: bool = True,
        persona: Optional[str] = None,
        name: str = "faq_bot",
        route: str = "/faq",
        **kwargs
    ):
        """
        Initialize an FAQ bot agent
        
        Args:
            faqs: List of FAQ items, each with:
                - question: The question text
                - answer: The answer text
                - categories: Optional list of category tags
            suggest_related: Whether to suggest related questions
            persona: Optional custom personality description
            name: Agent name for the route
            route: HTTP route for this agent
            **kwargs: Additional arguments for AgentBase
        """
        # Initialize the base agent
        super().__init__(
            name=name,
            route=route,
            use_pom=True,
            **kwargs
        )
        
        self.faqs = faqs
        self.suggest_related = suggest_related
        self.persona = persona or "You are a helpful FAQ bot that provides accurate answers to common questions."
        
        # Build the prompt
        self._build_faq_bot_prompt()
        
        # Set up the post-prompt template
        self._setup_post_prompt()
        
        # Configure additional agent settings
        self._configure_agent_settings()
    
    def _build_faq_bot_prompt(self):
        """Build the agent prompt for the FAQ bot"""
        # Set up the personality
        self.prompt_add_section(
            "Personality", 
            body=self.persona
        )
        
        # Set up the goal
        self.prompt_add_section(
            "Goal", 
            body="Answer user questions by matching them to the most similar FAQ in your database."
        )
        
        # Set up the instructions
        instructions = [
            "Compare user questions to your FAQ database and find the best match.",
            "Provide the answer from the FAQ database for the matching question.",
            "If no close match exists, politely say you don't have that information.",
            "Be concise and factual in your responses."
        ]
        
        # Add instruction about suggesting related questions if enabled
        if self.suggest_related:
            instructions.append(
                "When appropriate, suggest other related questions from the FAQ database that might be helpful."
            )
            
        self.prompt_add_section(
            "Instructions",
            bullets=instructions
        )
        
        # Add FAQ Database section with subsections for each FAQ
        faq_subsections = []
        for faq in self.faqs:
            question = faq.get("question", "")
            answer = faq.get("answer", "")
            categories = faq.get("categories", [])
            
            # Skip invalid entries
            if not question or not answer:
                continue
                
            # Build the body text with answer and optional categories
            body_text = answer
            if categories:
                category_str = "Categories: " + ", ".join(categories)
                body_text = f"{body_text}\n\n{category_str}"
                
            faq_subsections.append({
                "title": question,
                "body": body_text
            })
            
        # Add the FAQ Database section with all FAQ subsections
        self.prompt_add_section(
            "FAQ Database",
            body="Here is your database of frequently asked questions and answers:",
            subsections=faq_subsections
        )
        
        # Add section about suggesting related questions if enabled
        if self.suggest_related:
            self.prompt_add_section(
                "Related Questions",
                body="When appropriate, suggest other related questions from the FAQ database that might be helpful."
            )
    
    def _setup_post_prompt(self):
        """Set up the post-prompt for summary"""
        post_prompt = """
        Return a JSON summary of this interaction:
        {
            "question": "MAIN_QUESTION_ASKED",
            "matched_faq": "MATCHED_FAQ_QUESTION_OR_null",
            "answered_successfully": true/false,
            "suggested_related": []
        }
        """
        self.set_post_prompt(post_prompt)
    
    def _configure_agent_settings(self):
        """Configure additional agent settings"""
        # Add hints for better recognition of FAQ-related terms
        hints = []
        
        # Add questions and categories as hints
        for faq in self.faqs:
            # Extract key terms from questions
            question = faq.get("question", "")
            if question:
                # Split question into words and add words with 4+ characters
                words = [word.strip(".,?!") for word in question.split() if len(word.strip(".,?!")) >= 4]
                hints.extend(words)
                
            # Add categories as hints
            categories = faq.get("categories", [])
            hints.extend(categories)
        
        # Remove duplicates and add as hints
        unique_hints = list(set(hints))
        if unique_hints:
            self.add_hints(unique_hints)
        
        # Set AI behavior parameters
        self.set_params({
            "wait_for_user": False,
            "end_of_speech_timeout": 1000,
            "ai_volume": 5
        })
        
        # Add global data
        self.set_global_data({
            "faq_count": len(self.faqs),
            "categories": list(set(
                category 
                for faq in self.faqs 
                for category in faq.get("categories", [])
            ))
        })
        
        # Configure native functions
        self.set_native_functions(["check_time"])
    
    @AgentBase.tool(
        name="search_faqs",
        description="Search for FAQs matching a specific query or category",
        parameters={
            "query": {
                "type": "string",
                "description": "The search query"
            },
            "category": {
                "type": "string",
                "description": "Optional category to filter by"
            }
        }
    )
    def search_faqs(self, args, raw_data):
        """
        Search for FAQs matching a specific query or category
        
        This function helps find relevant FAQs based on a search query or category.
        It returns matching FAQs in order of relevance.
        """
        query = args.get("query", "").lower()
        category = args.get("category", "").lower()
        
        # Simple search logic (in a real implementation, you would use more
        # sophisticated search algorithms such as vector embeddings)
        results = []
        
        for faq in self.faqs:
            question = faq.get("question", "").lower()
            categories = [c.lower() for c in faq.get("categories", [])]
            match_score = 0
            
            # Match on query
            if query and query in question:
                # Simple substring matching - higher score for exact matches
                if query == question:
                    match_score += 100
                else:
                    match_score += 50
                    
                # Boost score for matches at the beginning of the question
                if question.startswith(query):
                    match_score += 25
                    
            # Match on category
            if category and category in categories:
                match_score += 30
                
            # Only include results with a positive match score
            if match_score > 0:
                results.append({
                    "question": faq.get("question"),
                    "score": match_score
                })
                
        # Sort results by score (highest first)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Limit to top 3 results
        top_results = results[:3]
        
        if top_results:
            result_text = "Here are the most relevant FAQs:\n\n"
            for i, result in enumerate(top_results, 1):
                result_text += f"{i}. {result['question']}\n"
                
            return FunctionResult(result_text)
        else:
            return FunctionResult("No matching FAQs found.")
    
    def on_summary(self, summary, raw_data=None):
        """
        Process the interaction summary
        
        Args:
            summary: Summary data from the conversation
            raw_data: The complete raw POST data from the request
        """
        if summary:
            try:
                # For structured summary
                if isinstance(summary, dict):
                    print(f"FAQ interaction summary: {json.dumps(summary, indent=2)}")
                else:
                    print(f"FAQ interaction summary: {summary}")
                    
                # Subclasses can override this to log or save the interaction
            except Exception as e:
                print(f"Error processing summary: {str(e)}")
