# Math Skill

The math skill provides safe mathematical calculation capabilities for agents. It allows users to perform basic arithmetic operations and complex mathematical expressions with security protections against code injection.

## Features

- Safe mathematical expression evaluation
- Support for basic arithmetic operations
- Parentheses support for complex expressions
- Division by zero protection
- Security filtering to prevent code injection
- No external dependencies required

## Requirements

- **Packages**: None (uses built-in Python functionality)
- **No external APIs required**

## Parameters

### Optional Parameters

- `swaig_fields` (dict): Additional SWAIG function configuration
  - `secure` (boolean): Override security settings for the calculation function
  - `fillers` (dict): Language-specific filler phrases while calculating
  - Any other SWAIG function parameters

**Note**: This skill does not require any configuration parameters beyond the optional swaig_fields. It works out-of-the-box with no setup.

## Tools Created

- `calculate` - Perform a mathematical calculation with basic operations

## Usage Examples

### Basic Usage

```python
# No configuration needed - works immediately
agent.add_skill("math")
```

### With Custom Fillers

```python
agent.add_skill("math", {
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Let me calculate that for you...",
                "Crunching the numbers...",
                "Computing the result...",
                "Working out the math..."
            ],
            "es-ES": [
                "Déjame calcular eso...",
                "Procesando los números...",
                "Calculando el resultado..."
            ]
        }
    }
})
```

### Disabling Security (if needed)

```python
agent.add_skill("math", {
    "swaig_fields": {
        "secure": False  # Allow unauthenticated calculation requests
    }
})
```

## How It Works

### Calculation Function
- **Input**: Mathematical expression as a string
- **Processing**: Validates expression for safety, then evaluates it
- **Output**: Shows the original expression and the calculated result
- **Example**: "2 + 3 * 4 = 14"

### Supported Operations

- **Addition**: `+` (e.g., "5 + 3")
- **Subtraction**: `-` (e.g., "10 - 7")
- **Multiplication**: `*` (e.g., "6 * 8")
- **Division**: `/` (e.g., "15 / 3")
- **Modulo**: `%` (e.g., "17 % 5")
- **Exponentiation**: `**` (e.g., "2 ** 3")
- **Parentheses**: `()` for grouping (e.g., "(2 + 3) * 4")

### Expression Examples

- Simple: `"2 + 3"` → "2 + 3 = 5"
- Complex: `"(10 + 5) * 2 / 3"` → "(10 + 5) * 2 / 3 = 10.0"
- With decimals: `"3.14 * 2"` → "3.14 * 2 = 6.28"
- Powers: `"2 ** 8"` → "2 ** 8 = 256"
- Modulo: `"17 % 5"` → "17 % 5 = 2"

## Function Parameters

The calculate tool accepts one parameter:

- `expression` (string, required): Mathematical expression to evaluate
  - Must contain only numbers, operators, and parentheses
  - Operators allowed: `+`, `-`, `*`, `/`, `%`, `**`, `(`, `)`
  - Decimal numbers are supported
  - Spaces are allowed and ignored

## Security Features

### Input Validation
- Only allows safe mathematical characters: numbers, operators, parentheses, spaces, decimal points
- Blocks any potentially dangerous code or function calls
- Uses regex pattern matching for character validation

### Safe Evaluation
- Uses Python's `eval()` with restricted builtins (empty `__builtins__`)
- No access to system functions or imports
- Cannot execute arbitrary code

### Error Handling
- **Division by Zero**: Returns friendly error message
- **Invalid Syntax**: Returns error for malformed expressions
- **Illegal Characters**: Rejects expressions with non-math characters
- **Empty Input**: Prompts user to provide an expression

## Error Examples

- **Division by zero**: "Error: Division by zero is not allowed."
- **Invalid characters**: "Invalid expression. Only numbers and basic math operators are allowed."
- **Syntax error**: "Error calculating '2 + + 3': Invalid expression"
- **Empty input**: "Please provide a mathematical expression to calculate."

## Common Use Cases

1. **Basic Arithmetic**: "What's 15 + 27?"
2. **Percentage Calculations**: "What's 15% of 200?" → "200 * 0.15"
3. **Complex Expressions**: "Calculate (100 + 50) * 0.08"
4. **Powers and Roots**: "What's 2 to the power of 10?"
5. **Financial Calculations**: "If I have $500 and spend $125, how much is left?"

## Best Practices

1. **Default Behavior**: The skill works immediately without configuration
2. **User Education**: Help users understand they can use parentheses for complex calculations
3. **Expression Formatting**: The skill is forgiving with spaces and formatting
4. **Error Recovery**: Provide helpful guidance when users make syntax errors
5. **Security**: The skill is designed to be safe even with malicious input

## Agent Integration

When added to an agent, this skill automatically:

- Adds speech recognition hints for math-related words
- Provides prompt guidance about calculation capabilities
- Enables the agent to respond to mathematical questions
- Shows both the original expression and result for transparency

The skill is designed to be completely self-contained and secure, making it safe for any agent to use for mathematical calculations. 