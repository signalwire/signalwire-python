# LLM Parameters Guide

This guide explains how to customize Language Model (LLM) parameters in SignalWire AI Agents to fine-tune the AI's behavior for your specific use case.

## Overview

SignalWire SDK provides methods to customize LLM parameters for both the main prompt and post-prompt, allowing precise control over the AI's response characteristics.

**Important:** The SDK passes parameters through to the SignalWire server without validation. Model-specific parameters are validated and handled by the server based on the target model's capabilities and requirements. Invalid parameters for the selected model will be handled or ignored by the server.

## Available Methods

### set_prompt_llm_params(**params)

Sets LLM parameters for the main agent prompt. Accepts any parameters that will be passed to the server.

```python
agent.set_prompt_llm_params(
    temperature=0.7,
    top_p=0.9,
    presence_penalty=0.0,
    frequency_penalty=0.0
)
```

### set_post_prompt_llm_params(**params)

Sets LLM parameters for the post-prompt (conversation summary). Accepts any parameters that will be passed to the server.

```python
agent.set_post_prompt_llm_params(
    temperature=0.3,
    top_p=0.95,
    presence_penalty=0.0,
    frequency_penalty=0.0
)
```

## Common Parameter Descriptions

These are commonly used parameters, but any parameter accepted by your model can be used. The actual ranges and defaults are model-specific and handled by the server.

### temperature
Controls the randomness of the AI's responses. The SWML schema allows 0.0 to 1.5, with a default of 1.0.
- **Lower values (e.g., 0.0-0.3)**: More deterministic, focused, and consistent responses
- **Medium values (e.g., 0.4-0.7)**: Balanced creativity and consistency
- **Higher values (e.g., 0.8+)**: More creative, diverse, and unpredictable responses

### top_p
Nucleus sampling parameter that controls the cumulative probability of token selection. The SWML schema allows 0.0 to 1.0, with a default of 1.0.
- **Lower values (e.g., 0.1-0.5)**: Only considers the most likely tokens
- **Medium values (e.g., 0.6-0.9)**: Balanced token selection
- **Higher values (e.g., 0.95-1.0)**: Considers a wider range of tokens

### Interruption

How easily the caller can interrupt the AI isn't an LLM parameter. The platform accepts `barge_confidence` in the prompt but never applies it: the confidence a caller's speech needs to interrupt is fixed. Tune interruption with these AI params, through `set_param()`:
- **`barge_min_words`** (1-99): how many words the caller must say before the AI stops speaking. Higher values make the AI harder to interrupt.
- **`enable_barge`**: which barge modes are on: `"complete"`, `"partial"`, `"all"`, or a boolean.
- **`barge_match_string`**: a string or regular expression that interrupts the AI when the caller says it.

```python
agent.set_param("barge_min_words", 3)  # Let the AI finish unless the caller says 3+ words
```

### presence_penalty
Topic diversity control. Penalizes tokens based on whether they appear in the conversation so far. The SWML schema allows -2.0 to 2.0, with a default of 0.
- **Negative values**: Encourages repetition of topics
- **Zero**: No penalty
- **Positive values**: Discourages repetition, encourages new topics

### frequency_penalty
Repetition control. Penalizes tokens based on their frequency in the conversation. The SWML schema allows -2.0 to 2.0, with a default of 0.
- **Negative values**: Encourages repetition of specific words
- **Zero**: No penalty
- **Positive values**: Discourages word repetition, encourages vocabulary variety

**Note:** No default values are sent unless explicitly set using `set_prompt_llm_params()` or `set_post_prompt_llm_params()`. The server will apply model-appropriate defaults if parameters are not specified.

## Use Case Examples

### Customer Service Agent

Low temperature keeps responses consistent.

```python
class CustomerServiceAgent(AgentBase):
    def __init__(self):
        super().__init__(name="customer-service", route="/support")
        
        self.prompt_add_section("Role", "You are a professional customer service representative.")
        
        # Consistent, helpful responses
        self.set_prompt_llm_params(
            temperature=0.3,        # Low randomness for consistency
            top_p=0.9,             # Focused token selection
            presence_penalty=0.1,  # Slight penalty to avoid repetition
            frequency_penalty=0.1  # Encourage varied language
        )
```

### Creative Writing Assistant

Higher temperature suits a collaborative, creative agent.

```python
class CreativeWritingAgent(AgentBase):
    def __init__(self):
        super().__init__(name="creative-writer", route="/writer")
        
        self.prompt_add_section("Role", "You are a creative writing assistant.")
        
        # Creative, diverse responses
        self.set_prompt_llm_params(
            temperature=0.8,        # High randomness for creativity
            top_p=0.95,            # Wide token selection
            presence_penalty=-0.1, # Allow topic revisiting
            frequency_penalty=0.3  # Encourage vocabulary diversity
        )
```

### Technical Documentation Bot

Very low temperature and a stricter post-prompt setting keep answers precise.

```python
class TechnicalDocsAgent(AgentBase):
    def __init__(self):
        super().__init__(name="tech-docs", route="/docs")
        
        self.prompt_add_section("Role", "You are a technical documentation assistant.")
        
        # Precise, accurate responses
        self.set_prompt_llm_params(
            temperature=0.2,        # Very low randomness
            top_p=0.8,             # More focused token selection
            presence_penalty=0.0,  # Neutral on repetition
            frequency_penalty=0.2  # Some vocabulary variety
        )
        
        # Even more focused for summaries
        self.set_post_prompt_llm_params(
            temperature=0.1       # Extremely consistent
        )
```

### Legal Advisor Bot

Low temperature favors accuracy, and requiring a few words before the AI stops lets it finish its caveats.

```python
class LegalAdvisorAgent(AgentBase):
    def __init__(self):
        super().__init__(name="legal-advisor", route="/legal")
        
        self.prompt_add_section("Role", "You are a legal information assistant.")
        self.prompt_add_section("Disclaimer", "Always remind users to consult a real attorney.")
        
        # Cautious, precise responses
        self.set_prompt_llm_params(
            temperature=0.2,        # Very consistent
            top_p=0.85,            # Focused selection
            presence_penalty=0.0,  # Allow legal term repetition
            frequency_penalty=0.0  # Legal language often repeats
        )

        # Harder to interrupt: the caller must say 3 words to stop the AI
        self.set_param("barge_min_words", 3)
```

## Best Practices

### 1. Start with Defaults
Begin with the default values and adjust based on observed behavior.

### 2. Test Incrementally
Make small adjustments and test thoroughly to understand the impact.

### 3. Consider the Use Case
- **Customer Service**: Low temperature (0.2-0.4)
- **Creative Tasks**: Higher temperature (0.7-0.9)
- **Technical/Legal**: Very low temperature (0.1-0.3)
- **General Assistant**: Medium temperature (0.5-0.7)

### 4. Match Post-Prompt Parameters
Post-prompt parameters should typically be lower temperature than main prompt for consistent summaries.

### 5. Tune Interruption Separately
Interruption is set with the `barge_min_words` param, not an LLM parameter:
- Too high: Users have difficulty interrupting the AI
- Too low: Background noise interrupts the AI

## Parameter Interactions

### Temperature + Top-p
These parameters work together to control randomness:
- Low temperature + Low top_p = Very focused responses
- High temperature + High top_p = Maximum creativity
- Low temperature + High top_p = Consistent but with fallback options
- High temperature + Low top_p = Creative within constraints

### Penalty Parameters
Presence and frequency penalties can be used together:
- Both positive: Strong encouragement for variety
- Both negative: Strong encouragement for repetition
- Mixed: Fine-tuned control over specific repetition patterns

## Troubleshooting

### AI is too repetitive
- Increase `presence_penalty` (try 0.3-0.6)
- Increase `frequency_penalty` (try 0.3-0.6)
- Slightly increase `temperature`

### AI is too random/inconsistent
- Decrease `temperature` (try 0.2-0.4)
- Decrease `top_p` (try 0.7-0.85)

### AI gets interrupted by background noise
- Raise the `barge_min_words` param, as in `set_param("barge_min_words", 3)`
- Check for background noise in the environment
- Consider the user's speaking clarity

### Users can't interrupt the AI
- Lower the `barge_min_words` param, and check that `enable_barge` isn't turned off
- Train users to speak more clearly when interrupting
- Consider the use case (e.g., legal/medical may need higher thresholds)

## Parameter Behavior

**No Default Values:** The SDK does not send any LLM parameters unless explicitly set using `set_prompt_llm_params()` or `set_post_prompt_llm_params()`. When parameters are not specified, the SignalWire server will apply appropriate defaults based on the model being used.

**Server-Side Validation:** All parameter validation is handled by the SignalWire server. The SDK accepts any parameters and passes them through without modification. This allows:
- Use of model-specific parameters without SDK updates
- Forward compatibility with new models and parameters
- Server-side optimization based on model capabilities

**Partial Configuration:** You can set only the parameters you want to customize. For example:
```python
# Only set temperature, let server handle other parameters
agent.set_prompt_llm_params(temperature=0.7)

# Or set multiple specific parameters
agent.set_prompt_llm_params(
    temperature=0.5,
    top_p=0.9
)
```

## Examples

The repository includes these working examples:

- `examples/llm_params_demo.py` - Three agent personas (customer service, creative, technical) demonstrating different LLM parameter configurations
- `examples/simple_agent.py` - Basic LLM parameter tuning with `set_prompt_llm_params()`