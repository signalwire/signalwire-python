# Weather API Skill

A configurable skill for getting current weather information from WeatherAPI.com with customizable temperature units and TTS-optimized natural language responses.

## Features

- **Configurable Temperature Units**: Choose between Fahrenheit and Celsius
- **TTS-Friendly Responses**: Natural language numbers without abbreviations or symbols
- **Real-time Weather Data**: Current conditions via WeatherAPI.com
- **DataMap Efficiency**: Serverless webhook execution, no agent processing load
- **Error Handling**: Graceful fallback for API failures or invalid locations
- **Comprehensive Weather Info**: Temperature, conditions, wind, clouds, feels-like

## Configuration

### Basic Structure

```python
agent.add_skill("weather_api", {
    "tool_name": "get_weather",
    "api_key": "your_weatherapi_key", 
    "temperature_unit": "fahrenheit"  # or "celsius"
})
```

### Parameters

- **tool_name** (string, optional): Custom name for the generated SWAIG function (default: "get_weather")
- **api_key** (string, required): Your WeatherAPI.com API key
- **temperature_unit** (string, optional): "fahrenheit" or "celsius" (default: "fahrenheit")

## Usage Examples

### Fahrenheit Weather (Default)

```python
agent.add_skill("weather_api", {
    "tool_name": "get_weather",
    "api_key": "your_weatherapi_key"
})
```

**Generated Tool**: `get_weather(location)`
**Temperature Format**: "seventy two degrees Fahrenheit"

### Celsius Weather

```python
agent.add_skill("weather_api", {
    "tool_name": "get_weather_celsius",
    "api_key": "your_weatherapi_key",
    "temperature_unit": "celsius"
})
```

**Generated Tool**: `get_weather_celsius(location)`
**Temperature Format**: "twenty two degrees Celsius"

### Custom Tool Name

```python
agent.add_skill("weather_api", {
    "tool_name": "check_current_weather",
    "api_key": "your_weatherapi_key",
    "temperature_unit": "fahrenheit"
})
```

**Generated Tool**: `check_current_weather(location)`

## Generated SWAIG Function

For the Fahrenheit example above, the skill generates:

```json
{
    "function": "get_weather",
    "description": "Get current weather information for any location",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city, state, country, or location to get weather for"
            }
        },
        "required": ["location"]
    },
    "data_map": {
        "webhook": {
            "url": "https://api.weatherapi.com/v1/current.json?key=your_api_key&q=%{enc:args.location}&aqi=no",
            "method": "GET"
        },
        "output": {
            "response": "Tell the user the current weather conditions. Express all temperatures in Fahrenheit using natural language numbers without abbreviations or symbols for clear text-to-speech pronunciation. For example, say 'seventy two degrees Fahrenheit' instead of '72F' or '72°F'. Include the condition, current temperature, wind direction and speed, cloud coverage percentage, and what the temperature feels like. Current conditions: ${current.condition.text}. Temperature: ${current.temp_f} degrees Fahrenheit. Wind: ${current.wind_dir} at ${current.wind_mph} miles per hour. Cloud coverage: ${current.cloud} percent. Feels like: ${current.feelslike_f} degrees Fahrenheit."
        },
        "error_keys": ["error"],
        "fallback_output": {
            "response": "Sorry, I cannot get weather information right now. Please try again later or check if the location name is correct."
        }
    }
}
```

## TTS Optimization

The skill is specifically designed for text-to-speech systems:

### Natural Language Numbers
- ✅ "seventy two degrees Fahrenheit"
- ❌ "72F" or "72°F"

### Full Pronunciation
- ✅ "twenty two degrees Celsius" 
- ❌ "22C" or "22°C"

### Complete Weather Description
- Current conditions description
- Temperature in natural language
- Wind direction and speed
- Cloud coverage percentage
- Feels-like temperature

## Execution Flow

1. **AI calls function**: `get_weather(location: "New York")`
2. **DataMap webhook**: `GET https://api.weatherapi.com/v1/current.json?key=...&q=New%20York&aqi=no`
3. **API response**: Weather data with current conditions
4. **AI responds**: "Tell the user the current weather conditions. Express all temperatures in Fahrenheit using natural language numbers... Current conditions: Partly cloudy. Temperature: seventy two degrees Fahrenheit. Wind: Southwest at fifteen miles per hour. Cloud coverage: twenty five percent. Feels like: seventy five degrees Fahrenheit."

## WeatherAPI.com Integration

The skill integrates with WeatherAPI.com's current weather endpoint:

- **Endpoint**: `https://api.weatherapi.com/v1/current.json`
- **Parameters**: `key`, `q` (location), `aqi=no`
- **Response**: Real-time weather data including temperature, conditions, wind, clouds
- **Location Support**: Cities, states, countries, coordinates, airports, etc.

## Temperature Unit Support

### Fahrenheit Configuration
```python
"temperature_unit": "fahrenheit"
```
- Uses `temp_f` and `feelslike_f` fields
- Displays as "degrees Fahrenheit"

### Celsius Configuration  
```python
"temperature_unit": "celsius"
```
- Uses `temp_c` and `feelslike_c` fields
- Displays as "degrees Celsius"

## Error Handling

- **Invalid API Key**: Validation during skill initialization
- **Invalid Temperature Unit**: Must be "fahrenheit" or "celsius"
- **API Failures**: Graceful fallback response for network/API issues
- **Invalid Locations**: Fallback suggests checking location name

## Benefits

- **TTS Optimized**: Natural language responses perfect for voice agents
- **Configurable**: Easy temperature unit switching without code changes
- **Efficient**: DataMap webhook execution, no agent processing load
- **Reliable**: Real-time data from established weather service
- **User Friendly**: Clear error messages and location flexibility
- **Professional**: Production-ready with comprehensive error handling

## Implementation Notes

- Temperature unit determines which API fields to use (`temp_f`/`temp_c`, `feelslike_f`/`feelslike_c`)
- Response includes detailed TTS instructions for natural pronunciation
- URL encoding automatically applied to location parameter
- Wind speed always reported in miles per hour regardless of temperature unit
- No air quality data requested to keep responses focused 