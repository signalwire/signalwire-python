#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Fred: a Wikipedia knowledge bot

An agent that searches Wikipedia and shares facts about Wikipedia itself,
with a friendly, curious persona.
"""

from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class FredTheWikiBot(AgentBase):
    """Fred, a Wikipedia assistant with a friendly persona"""
    
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
                "Search before you say Wikipedia has nothing on a topic, even one that sounds made up",
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

            # The model may leave the category out, so default to random
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
                    "Wikipedia started as a side project of Nupedia, an encyclopedia written by experts!",
                    "Wikipedia's name comes from 'wiki' (Hawaiian for 'quick') and 'encyclopedia'!",
                    "Jimmy Wales and Larry Sanger founded Wikipedia!"
                ],
                "records": [
                    "English Wikipedia's one billionth edit was made on January 13, 2021!",
                    "Steven Pruitt has made more edits to English Wikipedia than anyone else, over three million!",
                    "Wikipedia is one of the most visited websites in the world!"
                ]
            }

            # The enum guides the model but doesn't bind it: random, or any
            # category Fred doesn't have, draws from every fact
            if category in facts:
                fact = random.choice(facts[category])
                # Say what kind of fact it is, so the model can introduce it
                return SwaigFunctionResult(f"Here's a {category} fact about Wikipedia: {fact}")

            all_facts = [fact for fact_list in facts.values() for fact in fact_list]
            fact = random.choice(all_facts)
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
    """Run Fred"""
    print("=" * 60)
    print("Fred: a Wikipedia knowledge bot")
    print("=" * 60)
    print()
    print("Fred searches Wikipedia and shares facts about Wikipedia itself.")
    print()
    print("Questions to try:")
    print("  - Tell me about Albert Einstein")
    print("  - What is quantum physics?")
    print("  - Who was Marie Curie?")
    print("  - Search for information about the solar system")
    print("  - Can you share a fun fact?")
    print()
    
    # Create and run Fred
    fred = FredTheWikiBot()
    
    # Get auth credentials for display
    username, password = fred.get_basic_auth_credentials()
    
    print(f"Fred is available at: http://localhost:{fred.port}/fred")
    print(f"Basic Auth: {username}:{password}")
    print()
    print("Starting Fred. Press Ctrl+C to stop.")
    print("=" * 60)
    
    try:
        fred.run()
    except KeyboardInterrupt:
        print("\nFred stopped.")


if __name__ == "__main__":
    main()