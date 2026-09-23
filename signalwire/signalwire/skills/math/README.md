# Math Skill

The math skill provides safe mathematical calculation capabilities for agents. It allows users to perform basic arithmetic operations and complex mathematical expressions with security protections against code injection.

## Features

The skill covers these capabilities:

- Safe mathematical expression evaluation
- Support for basic arithmetic operations
- Parentheses support for complex expressions
- Division by zero protection
- Security filtering to prevent code injection
- No external dependencies required

## Requirements

The skill needs no packages and no external API:

- **Packages**: None (uses built-in Python functionality)
- **No external APIs required**

## Parameters

### Optional Parameters

The skill accepts one optional parameter, for SWAIG function configuration:

- `swaig_fields` (dict): Additional SWAIG function configuration
  - `secure` (boolean): Override security settings for the calculation function
  - `fillers` (dict): Language-specific filler phrases while calculating
  - Any other SWAIG function parameters

This skill needs no configuration parameters beyond the optional `swaig_fields`, and it works with no setup.

## Tools Created

The skill registers one tool:

- `calculate` - Perform a mathematical calculation with basic operations

## Usage Examples

### Basic Usage

Add the skill with no parameters, and the `calculate` tool is available immediately:

```python
# No configuration needed - works immediately
agent.add_skill("math")
```

### With Custom Fillers

Add language-specific filler phrases the agent speaks while it calculates:

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

Set `secure` to `False` to allow the tool to run without authentication:

```python
agent.add_skill("math", {
    "swaig_fields": {
        "secure": False  # Allow unauthenticated calculation requests
    }
})
```

## How It Works

### Calculation Function

The `calculate` tool takes a string and returns the expression alongside its result:

- **Input**: Mathematical expression as a string
- **Processing**: Validates expression for safety, then evaluates it
- **Output**: Shows the original expression and the calculated result
- **Example**: "2 + 3 * 4 = 14"

### Supported Operations

The tool supports these operators:

- **Addition**: `+` (e.g., "5 + 3")
- **Subtraction**: `-` (e.g., "10 - 7")
- **Multiplication**: `*` (e.g., "6 * 8")
- **Division**: `/` (e.g., "15 / 3")
- **Modulo**: `%` (e.g., "17 % 5")
- **Exponentiation**: `**` (e.g., "2 ** 3")
- **Parentheses**: `()` for grouping (e.g., "(2 + 3) * 4")

### Expression Examples

These examples show the exact response the tool returns:

- Simple: `"2 + 3"` produces "2 + 3 = 5"
- Complex: `"(10 + 5) * 2 / 3"` produces "(10 + 5) * 2 / 3 = 10.0"
- With decimals: `"3.14 * 2"` produces "3.14 * 2 = 6.28"
- Powers: `"2 ** 8"` produces "2 ** 8 = 256"
- Modulo: `"17 % 5"` produces "17 % 5 = 2"

## Function Parameters

The calculate tool accepts one parameter:

- `expression` (string, required): Mathematical expression to evaluate
  - Must contain only numbers, operators, and parentheses
  - Operators allowed: `+`, `-`, `*`, `/`, `%`, `**`, `(`, `)`
  - Decimal numbers are supported
  - Spaces are allowed and ignored

## Security Features

### Safe Evaluation

The skill never calls Python's `eval`. Instead, it parses and walks the expression itself:

- Parses the expression to an AST (`ast.parse(..., mode="eval")`) and walks it with a restricted evaluator
- The evaluator only permits numeric constants and a fixed set of arithmetic operators (`+`, `-`, `*`, `/`, `%`, `**`, unary `+`/`-`)
- Never calls Python's built-in `eval`, so there is no access to names, attributes, calls, system functions, or imports
- Caps the exponent to prevent resource exhaustion
- Cannot execute arbitrary code

### Error Handling

The tool catches these cases and returns a message instead of raising an exception:

- **Division by Zero**: Returns friendly error message
- **Invalid Syntax**: Returns error for malformed expressions
- **Illegal Characters**: Rejects expressions with non-math characters
- **Empty Input**: Prompts user to provide an expression

## Error Examples

These are the exact messages the tool returns:

- **Division by zero**: "Error: Division by zero is not allowed."
- **Invalid characters**: "Error: Invalid expression. Only numbers and basic math operators (+, -, *, /, %, **, parentheses) are allowed."
- **Calculation error**: "Error calculating '10.0 ** 1000': Invalid expression" (for example, an expression whose result overflows)
- **Empty input**: "Please provide a mathematical expression to calculate."

## Common Use Cases

The tool handles questions phrased in natural language, not only bare expressions:

1. **Basic Arithmetic**: "What's 15 + 27?"
2. **Percentage Calculations**: "What's 15% of 200?" becomes "200 * 0.15"
3. **Complex Expressions**: "Calculate (100 + 50) * 0.08"
4. **Powers and Roots**: "What's 2 to the power of 10?"
5. **Financial Calculations**: "If I have $500 and spend $125, how much is left?"

## Best Practices

Keep these points in mind when you add this skill to an agent:

1. **Default Behavior**: The skill works immediately without configuration
2. **User Education**: Help users understand they can use parentheses for complex calculations
3. **Expression Formatting**: The skill is forgiving with spaces and formatting
4. **Error Recovery**: Provide helpful guidance when users make syntax errors
5. **Security**: Malicious input cannot execute code; the evaluator only accepts numbers and arithmetic operators

## Agent Integration

When added to an agent, this skill automatically:

- Adds speech recognition hints for math-related words
- Provides prompt guidance about calculation capabilities
- Enables the agent to respond to mathematical questions
- Shows both the original expression and result for transparency

It is self-contained and safe for any agent to use for mathematical calculations.