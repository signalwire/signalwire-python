#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Fred - The Wikipedia Knowledge Bot

A friendly agent that can search Wikipedia for factual information.
Fred is curious, helpful, and loves sharing knowledge from Wikipedia.
"""

from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class FredTheWikiBot(AgentBase):
    """Fred - Your friendly Wikipedia assistant"""
    
    def __init__(self):
        super().__init__(
            name="Fred",
            route="/fred"
        )
        
        # Set up Fred's personality using POM
        self.prompt_add_section(
            "Personality", 
            "You are Fred, a friendly and knowledgeable assistant who loves learning and sharing information from Wikipedia. You're enthusiastic about facts and always eager to help people discover new things."
        )
        
        self.prompt_add_section(
            "Goal",
            "Help users find reliable factual information by searching Wikipedia. Make learning fun and engaging."
        )
        
        self.prompt_add_section(
            "Instructions",
            bullets=[
                "Introduce yourself as Fred when greeting users",
                "Use the search_wiki function whenever users ask about factual topics",
                "Be enthusiastic about sharing knowledge",
                "If Wikipedia doesn't have information, suggest alternative search terms",
                "Make learning conversational and enjoyable",
                "Add interesting context or follow-up questions to engage users"
            ]
        )
        
        # Add the Wikipedia search skill with custom configuration
        self.add_skill("wikipedia_search", {
            "num_results": 2,  # Get up to 2 articles for broader coverage
            "no_results_message": "Oh, I couldn't find anything about '{query}' on Wikipedia. Maybe try different keywords or let me know if you meant something else!",
            "swaig_fields": {
                "fillers": {
                    "en-US": [
                        "Let me look that up on Wikipedia for you...",
                        "Searching Wikipedia for that information...",
                        "One moment, checking Wikipedia...",
                        "Let me find that in the encyclopedia..."
                    ]
                }
            }
        })
        
        # Add a fun fact function
        @self.tool(
            name="share_fun_fact",
            description="Share an interesting fact about Wikipedia itself",
            parameters={
                "category": {
                    "type": "string",
                    "description": "Type of fact to share",
                    "enum": ["statistics", "history", "records", "random"]
                }
            }
        )
        def share_fun_fact(args, raw_data):
            import random

            # Get the requested category
            category = args.get("category", "random")

            # Define facts by category
            facts = {
                "statistics": [
                    "Wikipedia has over 6 million articles in English alone!",
                    "Wikipedia is available in more than 300 languages!",
                    "Wikipedia receives over 18 billion page views per month!",
                    "There are over 100,000 active Wikipedia contributors!"
                ],
                "history": [
                    "Wikipedia was launched on January 15, 2001!",
                    "The first Wikipedia article was about the letter 'U'!",
                    "Wikipedia's name comes from 'wiki' (Hawaiian for 'quick') and 'encyclopedia'!",
                    "Jimmy Wales and Larry Sanger founded Wikipedia!"
                ],
                "records": [
                    "The most edited Wikipedia page is about George W. Bush!",
                    "The longest Wikipedia article is about California Proposition 8!",
                    "Wikipedia is the 7th most visited website in the world!",
                    "The Wikipedia article on 'List of Pokemon' is one of the most viewed!"
                ],
                "random": []  # Will be filled with all facts
            }

            # Combine all facts for random selection
            all_facts = []
            for fact_list in facts.values():
                if fact_list:  # Skip empty random list
                    all_facts.extend(fact_list)
            facts["random"] = all_facts

            # Select appropriate fact
            fact_list = facts.get(category, facts["random"])
            if not fact_list:
                return SwaigFunctionResult("I don't have any facts in that category.")

            fact = random.choice(fact_list)

            # Add category context to response
            if category != "random":
                return SwaigFunctionResult(f"Here's a {category} fact about Wikipedia: {fact}")
            else:
                return SwaigFunctionResult(f"Here's a fun Wikipedia fact: {fact}")
        
        # Configure Fred's voice
        self.add_language(
            name="English",
            code="en-US",
            voice="rime.bolt",  # A friendly, energetic voice for Fred
            speech_fillers=[
                "Hmm, let me think...",
                "Oh, that's interesting...",
                "Great question!",
                "Let me see..."
            ]
        )
        
        # Add some hints for better speech recognition
        self.add_hints([
            "Wikipedia",
            "Fred",
            "tell me about",
            "what is",
            "who is",
            "search for",
            "look up"
        ])
        
        # Set conversation parameters
        self.set_params({
            "ai_model": "gpt-4.1-nano",
            "wait_for_user": True,
            "end_of_speech_timeout": 1000,
            "ai_volume": 7,
            "local_tz": "America/New_York"
        })
        
        # Add some context about Fred
        self.set_global_data({
            "assistant_name": "Fred",
            "specialty": "Wikipedia knowledge",
            "personality_traits": ["friendly", "curious", "enthusiastic", "helpful"]
        })


def main():
    """Run Fred the Wiki Bot"""
    print("=" * 60)
    print("🤖 Fred - The Wikipedia Knowledge Bot")
    print("=" * 60)
    print()
    print("Fred is a friendly assistant who loves searching Wikipedia!")
    print("He can help you learn about almost any topic.")
    print()
    print("Example questions you can ask Fred:")
    print("  • 'Tell me about Albert Einstein'")
    print("  • 'What is quantum physics?'")
    print("  • 'Who was Marie Curie?'")
    print("  • 'Search for information about the solar system'")
    print("  • 'Can you share a fun fact?'")
    print()
    
    # Create and run Fred
    fred = FredTheWikiBot()
    
    # Get auth credentials for display
    username, password = fred.get_basic_auth_credentials()
    
    print(f"Fred is available at: http://localhost:3000/fred")
    print(f"Basic Auth: {username}:{password}")
    print()
    print("Starting Fred... Press Ctrl+C to stop.")
    print("=" * 60)
    
    try:
        fred.run()
    except KeyboardInterrupt:
        print("\n👋 Fred says goodbye! Thanks for learning with me!")


if __name__ == "__main__":
    main()