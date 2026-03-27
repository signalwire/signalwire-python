#!/usr/bin/env python3
"""
Copyright (c) 2025 SignalWire

This file is part of the SignalWire AI Agents SDK.

Licensed under the MIT License.
See LICENSE file in the project root for full license information.
"""

"""
Survey Agent Example - Demonstrating the SurveyAgent prefab

This example shows how to create and configure a SurveyAgent for collecting
structured survey responses from users with different question types.

Features demonstrated:
1. Setting up various question types (rating, multiple choice, yes/no, open-ended)
2. Customizing the survey introduction and conclusion
3. Handling validation for different question types
4. Processing survey results
"""

import os
import logging
import sys
import json
import argparse
from datetime import datetime

# Import structlog for proper structured logging
import structlog

# Import the SurveyAgent prefab
from signalwire.prefabs import SurveyAgent
from signalwire.core.function_result import FunctionResult

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Set up the root logger with structlog
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Create structured logger
logger = structlog.get_logger("survey_agent")


class ProductSurveyAgent(SurveyAgent):
    """
    A survey agent customized for product feedback collection.
    
    This extends the base SurveyAgent with:
    1. Custom result processing
    2. Additional validation rules
    3. Custom SWAIG functions for enhanced functionality
    """
    
    def __init__(self, **kwargs):
        """Initialize the ProductSurveyAgent with default settings"""
        # Define the survey questions
        questions = [
            {
                "id": "product_satisfaction",
                "text": "On a scale of 1-5, how satisfied are you with our product?",
                "type": "rating",
                "scale": 5,
                "required": True
            },
            {
                "id": "usage_frequency",
                "text": "How often do you use our product?",
                "type": "multiple_choice",
                "options": ["Daily", "Weekly", "Monthly", "Rarely"],
                "required": True
            },
            {
                "id": "primary_feature",
                "text": "Which feature do you use the most?",
                "type": "multiple_choice",
                "options": ["Communication Tools", "File Sharing", "Task Management", "Analytics"],
                "required": True
            },
            {
                "id": "recommend",
                "text": "Would you recommend our product to others?",
                "type": "yes_no",
                "required": True
            },
            {
                "id": "improvement_suggestions",
                "text": "What improvements would you suggest for our product?",
                "type": "open_ended",
                "required": False
            }
        ]
        
        # Survey introduction and conclusion
        introduction = (
            "Thank you for participating in our product survey! "
            "Your feedback helps us improve our products and services. "
            "This survey should take about 2-3 minutes to complete."
        )
        
        conclusion = (
            "Thank you for completing our survey! Your feedback is extremely valuable "
            "and will help us improve our product. If you have further questions, "
            "please contact our support team."
        )
        
        # Initialize the base SurveyAgent with our custom settings
        super().__init__(
            survey_name="Product Feedback Survey",
            questions=questions,
            introduction=introduction,
            conclusion=conclusion,
            brand_name="SampleTech",
            max_retries=2,
            name="product_survey",
            route="/product_survey",
            **kwargs
        )
        
        # Override some parameters for better user experience
        self.set_params({
            "ai_model": "gpt-4.1-nano",
            "end_of_speech_timeout": 2000,  # Longer timeout for more thoughtful responses
            "ai_volume": 6,  # Slightly louder than default
            "wait_for_user": True  # Wait for user to speak first
        })
        
        logger.info("product_survey_agent_initialized")
    
    @SurveyAgent.tool(
        name="analyze_feedback",
        description="Analyze the customer feedback for sentiment and key themes",
        parameters={
            "feedback": {
                "type": "string",
                "description": "The customer's open-ended feedback text"
            }
        }
    )
    def analyze_feedback(self, args, raw_data):
        """
        Analyze customer feedback to identify sentiment and key themes
        
        This is a simple demonstration function that would typically connect
        to an NLP service or sentiment analysis API.
        """
        feedback = args.get("feedback", "")
        
        # Simple keyword-based "analysis" (in a real application, use NLP)
        sentiment = "neutral"
        key_themes = []
        
        # Very basic sentiment detection
        positive_words = ["great", "good", "excellent", "love", "like", "helpful"]
        negative_words = ["bad", "poor", "terrible", "hate", "dislike", "difficult"]
        
        # Count positive and negative words
        positive_count = sum(1 for word in positive_words if word in feedback.lower())
        negative_count = sum(1 for word in negative_words if word in feedback.lower())
        
        # Determine sentiment based on word counts
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
            
        # Extract potential themes (very simplified)
        theme_keywords = {
            "UI/UX": ["interface", "design", "layout", "ui", "ux"],
            "Performance": ["speed", "slow", "fast", "performance", "lag"],
            "Features": ["feature", "functionality", "capability", "tool"],
            "Support": ["help", "support", "assistance", "customer service"]
        }
        
        # Check for themes
        for theme, keywords in theme_keywords.items():
            if any(keyword in feedback.lower() for keyword in keywords):
                key_themes.append(theme)
        
        # Return the analysis
        return FunctionResult({
            "response": f"I've analyzed the feedback. The sentiment appears to be {sentiment}. " +
                        (f"Key themes identified: {', '.join(key_themes)}" if key_themes else "No specific themes identified."),
            "sentiment": sentiment,
            "themes": key_themes
        })
    
    def on_summary(self, summary, raw_data=None):
        """
        Process the survey results summary
        
        This method is called when a survey is completed and receives the
        structured results.
        
        Args:
            summary: Summary data containing survey responses
            raw_data: The complete raw POST data from the request
        """
        if not summary:
            logger.warning("empty_survey_summary")
            return
            
        try:
            # For structured summary
            if isinstance(summary, dict):
                # Log the summary
                logger.info("survey_completed", 
                           survey=summary.get("survey_name", "Unknown Survey"),
                           timestamp=summary.get("timestamp", datetime.now().isoformat()))
                
                # Get the responses
                responses = summary.get("responses", {})
                
                # Calculate satisfaction score
                if "product_satisfaction" in responses:
                    try:
                        satisfaction = int(responses["product_satisfaction"])
                        logger.info("satisfaction_score", score=satisfaction, max=5)
                        
                        # Alert on low satisfaction
                        if satisfaction <= 2:
                            logger.warning("low_satisfaction_detected", score=satisfaction)
                            # In a real application, you might trigger follow-up actions here
                    except ValueError:
                        logger.error("invalid_satisfaction_score", value=responses["product_satisfaction"])
                
                # Check recommendation status
                if "recommend" in responses:
                    recommend = responses["recommend"].lower()
                    is_promoter = recommend in ["yes", "y", "true"]
                    logger.info("recommendation_status", would_recommend=is_promoter)
                
                # Process improvement suggestions
                if "improvement_suggestions" in responses and responses["improvement_suggestions"]:
                    logger.info("received_improvement_suggestions", 
                               suggestions=responses["improvement_suggestions"])
                    
                # In a real application, you would:
                # 1. Store the survey responses in a database
                # 2. Update customer records
                # 3. Generate reports or dashboards
                # 4. Trigger follow-up actions based on responses
                
                # Print the summary for demonstration purposes
                print(f"Survey completed: {json.dumps(summary, indent=2)}")
                
            else:
                logger.warning("unstructured_survey_summary", summary=str(summary))
                print(f"Survey summary (unstructured): {summary}")
                
        except Exception as e:
            logger.error("error_processing_survey_summary", error=str(e))
            print(f"Error processing survey summary: {str(e)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Product Survey Agent")
    parser.add_argument("--port", type=int, default=3000, help="Port to run the server on")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument("--suppress-logs", action="store_true", help="Suppress extra logs")
    args = parser.parse_args()
    
    # Find schema.json in the current directory or parent directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    schema_locations = [
        os.path.join(current_dir, "schema.json"),
        os.path.join(parent_dir, "schema.json")
    ]
    
    schema_path = None
    for loc in schema_locations:
        if os.path.exists(loc):
            schema_path = loc
            logger.info("schema_found", path=schema_path)
            break
            
    if not schema_path:
        logger.warning("schema_not_found", locations=schema_locations)
    
    # Create an agent instance
    agent = ProductSurveyAgent(
        schema_path=schema_path,
        host=args.host,
        port=args.port,
        suppress_logs=args.suppress_logs
    )
    
    # Print credentials
    username, password, source = agent.get_basic_auth_credentials(include_source=True)
    
    logger.info("starting_agent", 
               url=f"http://{args.host}:{args.port}/product_survey", 
               username=username, 
               password_length=len(password),
               auth_source=source)
    
    print("Starting the Product Survey Agent. Press Ctrl+C to stop.")
    print(f"Agent 'product_survey' is available at:")
    print(f"URL: http://localhost:{args.port}/product_survey")
    print(f"Basic Auth: {username}:{password}")
    
    try:
        # Start the agent's server
        agent.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        logger.info("server_shutdown")
        print("\nStopping the agent.") 