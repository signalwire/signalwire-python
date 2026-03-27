# API Ninjas Trivia Skill

A configurable skill for getting trivia questions from API Ninjas with customizable categories and multiple tool instances. Supports serverless DataMap webhook execution.

## Features

- **Multiple Instances**: Create different tools with unique names and category sets
- **Configurable Categories**: Choose from 14 trivia categories
- **Dynamic Enum Generation**: Function parameters built from selected categories
- **DataMap Efficiency**: Serverless webhook execution, no agent processing load
- **API Integration**: Direct webhook to API Ninjas trivia endpoint
- **Error Handling**: Graceful fallback for API failures

## Configuration

### Basic Structure

```python
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "your_custom_tool_name",
    "api_key": "your_api_ninjas_key",
    "categories": ["category1", "category2", ...]  # Optional, defaults to all
})
```

### Parameters

- **tool_name** (string): Custom name for the generated SWAIG function (default: "get_trivia")
- **api_key** (string, required): Your API Ninjas API key
- **categories** (array, optional): List of category strings to enable (default: all categories)

### Available Categories

| Category | Description |
|----------|-------------|
| `artliterature` | Art and Literature |
| `language` | Language |
| `sciencenature` | Science and Nature |
| `general` | General Knowledge |
| `fooddrink` | Food and Drink |
| `peopleplaces` | People and Places |
| `geography` | Geography |
| `historyholidays` | History and Holidays |
| `entertainment` | Entertainment |
| `toysgames` | Toys and Games |
| `music` | Music |
| `mathematics` | Mathematics |
| `religionmythology` | Religion and Mythology |
| `sportsleisure` | Sports and Leisure |

## Usage Examples

### All Categories (Default)

```python
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_trivia",
    "api_key": "your_api_key"
})
```

**Generated Tool**: `get_trivia(category)`
**Actions**: All 14 categories available

### Science & Math Only

```python
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_science_trivia",
    "api_key": "your_api_key",
    "categories": ["sciencenature", "mathematics"]
})
```

**Generated Tool**: `get_science_trivia(category)`
**Actions**: `["sciencenature", "mathematics"]`

### Entertainment Trivia

```python
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_entertainment_trivia", 
    "api_key": "your_api_key",
    "categories": ["entertainment", "music", "toysgames"]
})
```

**Generated Tool**: `get_entertainment_trivia(category)`
**Actions**: `["entertainment", "music", "toysgames"]`

### Geography & History

```python
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_geography_trivia",
    "api_key": "your_api_key", 
    "categories": ["geography", "historyholidays", "peopleplaces"]
})
```

**Generated Tool**: `get_geography_trivia(category)`
**Actions**: `["geography", "historyholidays", "peopleplaces"]`

## Generated SWAIG Function

For the science & math example above, the skill generates:

```json
{
    "function": "get_science_trivia",
    "description": "Get trivia questions for get science trivia",
    "parameters": {
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Category for trivia question. Options: sciencenature: Science and Nature; mathematics: Mathematics",
                "enum": ["sciencenature", "mathematics"]
            }
        },
        "required": ["category"]
    },
    "data_map": {
        "webhook": {
            "url": "https://api.api-ninjas.com/v1/trivia?category=%{args.category}",
            "method": "GET",
            "headers": {
                "X-Api-Key": "your_api_key"
            }
        },
        "output": {
            "response": "Category %{array[0].category} question: %{array[0].question} Answer: %{array[0].answer}, be sure to give the user time to answer before saying the answer."
        },
        "error_keys": ["error"],
        "fallback_output": {
            "response": "Sorry, I cannot get trivia questions right now. Please try again later."
        }
    }
}
```

## Execution Flow

1. **AI calls function**: `get_science_trivia(category: "mathematics")`
2. **DataMap webhook**: `GET https://api.api-ninjas.com/v1/trivia?category=mathematics`
3. **API response**: `[{"category": "Mathematics", "question": "What is 2+2?", "answer": "4"}]`
4. **AI responds**: "Category Mathematics question: What is 2+2? Answer: 4, be sure to give the user time to answer before saying the answer."

## Multiple Instances

You can add multiple instances for different use cases:

```python
# General trivia with all categories
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_trivia",
    "api_key": "your_api_key"
})

# Science-focused trivia
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_science_trivia", 
    "api_key": "your_api_key",
    "categories": ["sciencenature", "mathematics"]
})

# Entertainment trivia
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_fun_trivia",
    "api_key": "your_api_key",
    "categories": ["entertainment", "music", "toysgames", "sportsleisure"]
})

# Educational trivia
agent.add_skill("api_ninjas_trivia", {
    "tool_name": "get_educational_trivia",
    "api_key": "your_api_key", 
    "categories": ["geography", "historyholidays", "artliterature", "language"]
})
```

This creates four separate tools: `get_trivia`, `get_science_trivia`, `get_fun_trivia`, and `get_educational_trivia`.

## API Integration

The skill integrates directly with API Ninjas trivia endpoint:

- **Endpoint**: `https://api.api-ninjas.com/v1/trivia`
- **Method**: GET
- **Parameters**: `category` (from enum)
- **Headers**: `X-Api-Key` with your API key
- **Response**: Array with question, answer, and category

## Benefits

- **Reusable**: Same skill supports different category combinations
- **Configurable**: Easy to add/remove categories without code changes
- **Efficient**: DataMap webhook execution, no agent load
- **Type Safe**: Enum parameters prevent invalid categories
- **Error Handling**: Graceful fallback for API failures
- **Maintainable**: Centralized trivia logic

## Error Handling

- **Invalid Categories**: Validation at skill initialization
- **API Failures**: Fallback response for network/API issues
- **Missing API Key**: Clear error message during setup

## Implementation Notes

- Categories are validated against the official API Ninjas list
- Enum values use exact API category names
- Human-readable descriptions are auto-generated
- Instance keys combine skill name and tool name for uniqueness
- API key is stored securely in DataMap headers 