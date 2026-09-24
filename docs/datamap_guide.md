# DataMap Complete Guide: SWML Perspective and Development

A comprehensive guide to understanding, implementing, and testing DataMap configurations in SignalWire AI Agents from the SWML (SignalWire Markup Language) perspective.

<!-- snippet-setup: shared imports the guide examples assume -->
```python
from signalwire import DataMap, FunctionResult, SwaigFunctionResult
from signalwire.core.data_map import create_expression_tool
```

## Table of Contents

### 1. Introduction to DataMap in SWML
- [1.1 What is DataMap](#11-what-is-datamap)
- [1.2 DataMap vs Traditional Webhooks](#12-datamap-vs-traditional-webhooks)
- [1.3 SWML Integration Overview](#13-swml-integration-overview)
- [1.4 When to Use DataMap](#14-when-to-use-datamap)

### 2. DataMap Architecture and Processing Pipeline
- [2.1 Server-Side Processing Flow](#21-server-side-processing-flow)
- [2.2 Processing Order: Expressions, Webhooks, Foreach, Output](#22-processing-order-expressions-webhooks-foreach-output)
- [2.3 Context and Variable Scope](#23-context-and-variable-scope)
- [2.4 Serverless Execution Model](#24-serverless-execution-model)

### 3. DataMap Configuration Structure
- [3.1 Basic DataMap Schema](#31-basic-datamap-schema)
- [3.2 Function-Level Configuration](#32-function-level-configuration)
- [3.3 Nested DataMap Objects](#33-nested-datamap-objects)
- [3.4 Parameter Validation](#34-parameter-validation)

### 4. Template Expansion System
- [4.1 Template Syntax Overview](#41-template-syntax-overview)
- [4.2 Variable Types and Sources](#42-variable-types-and-sources)
- [4.3 Array and Object Access Patterns](#43-array-and-object-access-patterns)
- [4.4 Context-Specific Variables](#44-context-specific-variables)
- [4.5 Template Expansion Examples](#45-template-expansion-examples)

### 5. Webhook Configuration and HTTP Processing
- [5.1 Webhook Structure](#51-webhook-structure)
- [5.2 HTTP Methods and Headers](#52-http-methods-and-headers)
- [5.3 Request Body Construction](#53-request-body-construction)
- [5.4 Sequential Webhook Processing](#54-sequential-webhook-processing)
- [5.5 Webhook Failure Detection](#55-webhook-failure-detection)

### 6. Response Processing and Data Handling
- [6.1 Response Data Structure](#61-response-data-structure)
- [6.2 Array vs Object Response Handling](#62-array-vs-object-response-handling)
- [6.3 Error Response Processing](#63-error-response-processing)
- [6.4 Custom Error Keys](#64-custom-error-keys)

### 7. Foreach Processing and Array Iteration
- [7.1 Foreach Configuration](#71-foreach-configuration)
- [7.2 Array Data Sources](#72-array-data-sources)
- [7.3 Template Expansion in Foreach](#73-template-expansion-in-foreach)
- [7.4 String Concatenation and Formatting](#74-string-concatenation-and-formatting)
- [7.5 Foreach Limitations and Best Practices](#75-foreach-limitations-and-best-practices)

### 8. Output Generation and Result Formatting
- [8.1 Webhook-Level Output](#81-webhook-level-output)
- [8.2 DataMap-Level Fallback Output](#82-datamap-level-fallback-output)
- [8.3 Response vs Action Outputs](#83-response-vs-action-outputs)
- [8.4 SWML Action Generation](#84-swml-action-generation)

### 9. Skills System Integration
- [9.1 DataMap Skills vs Raw Configuration](#91-datamap-skills-vs-raw-configuration)
- [9.2 Skill-Based DataMap Creation](#92-skill-based-datamap-creation)
- [9.3 Skill Configuration Patterns](#93-skill-configuration-patterns)
- [9.4 Multi-Instance Skill Usage](#94-multi-instance-skill-usage)

### 10. Practical Examples and Use Cases
- [10.1 API Integration Examples](#101-api-integration-examples)
- [10.2 Knowledge Base Search](#102-knowledge-base-search)
- [10.3 External Service Integration](#103-external-service-integration)
- [10.4 Multi-Step Processing Workflows](#104-multi-step-processing-workflows)

### 11. Development and Testing
- [11.1 Local Development Setup](#111-local-development-setup)
- [11.2 Environment Variable Configuration](#112-environment-variable-configuration)
- [11.3 CLI Testing Tools](#113-cli-testing-tools)
- [11.4 Debugging DataMap Execution](#114-debugging-datamap-execution)

### 12. Advanced Patterns and Best Practices
- [12.1 Multiple Webhook Fallback Chains](#121-multiple-webhook-fallback-chains)
- [12.2 Complex Template Expressions](#122-complex-template-expressions)
- [12.3 Dynamic API Endpoint Selection](#123-dynamic-api-endpoint-selection)
- [12.4 Response Transformation Patterns](#124-response-transformation-patterns)

### 13. Error Handling and Reliability
- [13.1 HTTP Error Codes and Handling](#131-http-error-codes-and-handling)
- [13.2 Network Timeout and Retry Logic](#132-network-timeout-and-retry-logic)
- [13.3 Graceful Degradation Strategies](#133-graceful-degradation-strategies)
- [13.4 Monitoring and Observability](#134-monitoring-and-observability)

### 14. Security and Best Practices
- [14.1 API Key Management](#141-api-key-management)
- [14.2 Secure Header Configuration](#142-secure-header-configuration)
- [14.3 Input Validation and Sanitization](#143-input-validation-and-sanitization)
- [14.4 Rate Limiting Considerations](#144-rate-limiting-considerations)

### 15. Performance Optimization
- [15.1 Request Optimization](#151-request-optimization)
- [15.2 Response Size Management](#152-response-size-management)
- [15.3 Caching Strategies](#153-caching-strategies)
- [15.4 Execution Time Considerations](#154-execution-time-considerations)

### 16. Migration and Upgrade Paths
- [16.1 From Webhook to DataMap Migration](#161-from-webhook-to-datamap-migration)
- [16.2 Legacy Configuration Support](#162-legacy-configuration-support)
- [16.3 Version Compatibility](#163-version-compatibility)
- [16.4 Gradual Migration Strategies](#164-gradual-migration-strategies)

---

*This guide provides comprehensive coverage of DataMap functionality within the SignalWire AI Agents framework, from basic concepts to advanced implementation patterns.*

## 1. Introduction to DataMap in SWML

### 1.1 What is DataMap

DataMap is a serverless function execution system within SignalWire AI Agents that enables integration with external APIs without the need for custom webhook endpoints. Unlike traditional webhook-based SWAIG (SignalWire AI Gateway) functions that require you to host and maintain HTTP endpoints, DataMap functions are executed entirely within the SignalWire infrastructure. SWAIG is the platform's AI tool-calling system with native access to the media stack. DataMap is one way to define SWAIG functions without running your own server.

The SDK's role stops at building this configuration: `DataMap.to_swaig_function()` serializes it into the SWAIG function definition. SignalWire's platform runs it during a call, fetching each webhook, expanding template variables, and evaluating expressions. Sections 2 to 8 describe what happens on that side.

**Key Characteristics:**
- **Serverless Architecture**: No need to host webhook endpoints
- **Built-in HTTP Client**: Native HTTP request capabilities
- **Template-Based Configuration**: Declarative API integration using template expansion
- **Sequential Processing**: Multiple webhook fallback support
- **Response Transformation**: Built-in data processing and formatting
- **Error Handling**: Automatic failure detection and fallback mechanisms

**DataMap Execution Flow:**
```
Function Call → Template Expansion → HTTP Request → Response Processing → Output Generation
```

### 1.2 DataMap vs Traditional Webhooks

| Aspect | Traditional Webhooks | DataMap |
|--------|---------------------|---------|
| **Infrastructure** | Requires hosted endpoints | Serverless execution |
| **Configuration** | Code-based handlers | Declarative JSON/YAML |
| **HTTP Requests** | Manual implementation | Built-in HTTP client |
| **Error Handling** | Custom error logic | Automatic failure detection |
| **Template Expansion** | Manual string formatting | Native template system |
| **Scalability** | Limited by hosting infrastructure | Auto-scaling serverless |
| **Maintenance** | Server maintenance required | Zero maintenance overhead |
| **Development Speed** | Slower (code + deploy) | Faster (configuration only) |

**Traditional Webhook Example:**
```python
def search_knowledge(args, post_data):
    # Custom HTTP request logic
    response = requests.post("https://api.example.com/search", 
                           json={"query": args["query"]})
    # Custom error handling
    if response.status_code != 200:
        return {"error": "API request failed"}
    # Custom response processing
    data = response.json()
    return {"response": f"Found: {data['results'][0]['text']}"}
```

**DataMap Equivalent:**
```json
{
  "function": "search_knowledge",
  "data_map": {
    "webhooks": [{
      "url": "https://api.example.com/search",
      "method": "POST",
      "headers": {"Content-Type": "application/json"},
      "params": {"query": "${args.query}"},
      "output": {"response": "Found: ${array[0].text}"},
      "error_keys": ["error"]
    }],
    "output": {"response": "Search service unavailable"}
  }
}
```

### 1.3 SWML Integration Overview

DataMap integrates with SWML (SignalWire Markup Language) through the AI verb's function calling mechanism. When an AI agent needs to call a function, SWML automatically detects whether it's a traditional webhook or DataMap function and routes the execution appropriately.

**SWML AI Verb Integration:**
```xml
<ai>
  <prompt>You can search knowledge using the search_knowledge function</prompt>
  <SWAIG>
    <function name="search_knowledge" data_map="..." />
  </SWAIG>
</ai>
```

**Execution Context:**
- DataMap functions have access to all SWML context variables
- Function arguments are automatically validated against parameter schemas
- Results can generate both response text and SWML actions
- Global data and prompt variables are available for template expansion

**Integration Benefits:**
- **Declarative Configuration**: Define API integrations using configuration, not code
- **Automatic Validation**: Parameter validation based on JSON schema
- **Context Awareness**: Access to conversation state and SWML variables
- **Action Generation**: Can produce SWML actions for call control
- **Error Recovery**: Built-in fallback mechanisms maintain conversation flow

### 1.4 When to Use DataMap

**Ideal Use Cases:**
- **External API Integration**: REST API calls to third-party services
- **Knowledge Base Queries**: Search operations against document stores
- **Data Transformation**: Simple data processing and formatting
- **Service Aggregation**: Combining data from multiple sources
- **Rapid Prototyping**: Quick API integration without infrastructure

**DataMap is Perfect For:**
- Simple to moderate API integration complexity
- Read-heavy operations (GET, POST with JSON)
- Services with predictable response formats
- Scenarios requiring fallback mechanisms
- Development teams without DevOps infrastructure

**Consider Traditional Webhooks When:**
- Complex business logic is required
- Advanced error handling and retry mechanisms needed
- Custom authentication schemes beyond headers
- Heavy computational processing required
- Integration with non-HTTP protocols
- Need for persistent state or caching
- Complex response transformation logic

**Hybrid Approach:**
Many applications benefit from using both DataMap and traditional webhooks:
- DataMap for simple API calls and data retrieval
- Traditional webhooks for complex processing and business logic
- DataMap for rapid prototyping, webhooks for production optimization

## 2. DataMap Architecture and Processing Pipeline

The SDK's part in this pipeline is small: `DataMap.to_swaig_function()` (in `signalwire/signalwire/core/data_map.py`) builds the `data_map` structure and hands it to SWML as part of the function definition. Everything described in this section happens on SignalWire's platform when your agent calls the function during a live call. That includes the HTTP requests, template expansion, and expression evaluation, which the rest of this section and sections 4 to 8 describe.

### 2.1 Server-Side Processing Flow

DataMap execution occurs entirely within the SignalWire infrastructure, following a deterministic processing pipeline implemented in the server-side `mod_openai.c` module. This flow determines how you configure DataMap functions.

**Server-Side Architecture:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SWML Engine   │────│   DataMap        │────│   HTTP Client   │
│   Function Call │    │   Processor      │    │   Request       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                       ┌──────▼──────┐
                       │   Template   │
                       │   Expansion  │
                       │   Engine     │
                       └─────────────┘
```

**Processing Modules:**
- **Function Router**: Determines if function is DataMap or webhook
- **Context Builder**: Assembles variable context from function arguments and SWML state
- **Template Engine**: Expands variables in URLs, headers, and request bodies
- **HTTP Client**: Executes HTTP requests with timeout and error handling
- **Response Processor**: Parses and validates HTTP responses
- **Foreach Engine**: Processes array data with template expansion
- **Output Generator**: Formats final results for SWML consumption

### 2.2 Processing Order: Expressions, Webhooks, Foreach, Output

DataMap processing follows a strict sequential order that ensures deterministic execution and proper error handling:

**1. Expression Processing (Optional)**:
```json
{
  "expressions": [
    {
      "pattern": "simple query",
      "output": {"response": "This is a simple response for: ${args.query}"}
    }
  ]
}
```
- Each expression expands its `string` template, such as `${args.query}`, and matches the result against its `pattern`, a PCRE regular expression
- Expressions are tried in order; the first match's `output` ends the function
- Bypasses HTTP requests for known cases

**2. Webhook Sequential Processing**:
```json
{
  "webhooks": [
    {"url": "https://primary-api.com/search", "...": "..."},
    {"url": "https://fallback-api.com/search", "...": "..."}
  ]
}
```
- Process webhooks in array order
- Stop at the first webhook that produces an output
- Each webhook has independent configuration, and evaluates its own `foreach`, then `expressions`, then `output` when its response arrives

**3. Foreach Processing (Per Successful Webhook)**:
```json
{
  "foreach": {
    "input_key": "results",
    "output_key": "formatted_results",
    "max": 5,
    "append": "Result: ${this.title}\n"
  }
}
```
- Processes array data from successful webhook response
- Builds concatenated strings using template expansion
- Stores result in context for output templates

**4. Output Generation**:
```json
{
  "output": {
    "response": "Found results: ${formatted_results}",
    "action": [{"SWML": {"version": "1.0.0", "...": "..."}}]
  }
}
```
- Webhook-level output (if webhook succeeds)
- DataMap-level fallback output (if all webhooks fail)
- A generic error for the AI if nothing produced an output

The first valid `output` anywhere ends the function, like a `return` statement.

**Processing Flow Diagram:**
```
Function Call
     │
     ▼
┌─────────────┐     Yes    ┌──────────────┐
│ Expressions │────────────│ Return Early │
│   Match?    │            │   Output     │
└─────────────┘            └──────────────┘
     │ No
     ▼
┌─────────────┐
│  Webhook 1  │────┐
│   Success?  │    │
└─────────────┘    │
     │ No          │ Yes
     ▼             ▼
┌─────────────┐  ┌─────────────┐
│  Webhook 2  │  │   Foreach   │
│   Success?  │  │ Processing  │
└─────────────┘  └─────────────┘
     │ No          │
     ▼             ▼
┌─────────────┐  ┌─────────────┐
│  Fallback   │  │   Webhook   │
│   Output    │  │   Output    │
└─────────────┘  └─────────────┘
```

### 2.3 Context and Variable Scope

Every template reads from one JSON object, the template data, which the platform builds for each call of the function. A template names a path from its root: `${args.query}` walks from the root into `args` and then `query`. Its root holds:

- `args`: the arguments the AI extracted for this call, by parameter name. Example: `${args.query}`.
- `global_data`: the application's global data, as the agent set it with `set_global_data()` or an action changed it. Example: `${global_data.api_token}`.
- `meta_data`: the function's own metadata. Example: `${meta_data.table.sales}`.
- Details of the call: `call_id`, `ai_session_id`, `conversation_id`, `function` (the function's name), `caller_id_name`, `caller_id_num`, `project_id`, `space_id` and `app_name`.
- `prompt_vars`: built-in variables describing the call and the AI session.

When a webhook responds, its JSON response joins the root. If the response is an object, its fields are read directly: a response of `{"total": 25, "results": [...]}` gives `${total}` and `${results[0].title}`. There is no `response.` prefix. If the response is an array, it's under `array`: `${array[0].joke}`.

During a `foreach`, `this` is the current element of the array it walks, as in `${this.title}`, and the text it builds is stored under its `output_key`, as in `${formatted_results}`.

**Context evolution:**
```javascript
// When the function is called
{
  "args": {"query": "SignalWire", "count": 3},
  "global_data": {...},
  "meta_data": {...},
  "call_id": "..."
}

// After a webhook returns the object {"results": [...], "total": 25}
{
  "args": {"query": "SignalWire", "count": 3},
  "results": [{"title": "...", "text": "..."}, ...],
  "total": 25,
  ...
}

// After a webhook returns an array
{
  "args": {"query": "SignalWire", "count": 3},
  "array": [{"title": "...", "text": "..."}, ...],
  ...
}

// While a foreach walks "results"
{
  "args": {"query": "SignalWire", "count": 3},
  "results": [...],
  "this": {"title": "Current item", "text": "Current content"},
  ...
}
```

### 2.4 Serverless Execution Model

DataMap functions execute in a serverless environment with specific characteristics and limitations:

**Execution Environment:**
- **Stateless**: No persistent memory between function calls
- **Isolated**: Each function execution is independent
- **Time-Limited**: HTTP requests have built-in timeouts
- **Resource-Constrained**: Optimized for typical API integration scenarios

**Execution Lifecycle:**
```
1. Function Call Received
   ├── Parse DataMap configuration
   ├── Validate function arguments
   └── Build initial context

2. Template Expansion
   ├── Expand webhook URLs and headers
   ├── Expand request body parameters
   └── Prepare HTTP request configuration

3. HTTP Request Execution
   ├── Make HTTP request with timeouts
   ├── Handle network errors
   └── Parse response (JSON/text)

4. Response Processing
   ├── Validate response structure
   ├── Check for error conditions
   └── Add response to context

5. Foreach Processing (if configured)
   ├── Extract array data
   ├── Iterate with template expansion
   └── Build concatenated result

6. Output Generation
   ├── Expand output templates
   ├── Format final response
   └── Return to SWML engine
```

**Performance Characteristics:**
- **Cold Start**: First execution may have slight latency
- **Warm Execution**: Subsequent calls are optimized
- **Concurrency**: Multiple functions can execute simultaneously
- **Scalability**: Automatic scaling based on demand

**Resource Limits:**

SignalWire's platform enforces these limits when it runs a data_map function. The SDK has no timeout, size, or concurrency setting of its own to configure or override them.

- HTTP request timeout: ~30 seconds
- Response size limits: Reasonable API response sizes
- Memory constraints: Optimized for typical API responses
- Concurrent execution: Platform-managed scaling

## 3. DataMap Configuration Structure

### 3.1 Basic DataMap Schema

DataMap configurations follow a specific JSON schema that defines how external APIs are integrated and how responses are processed. Understanding this schema is essential for creating effective DataMap functions.

**Complete DataMap Function Structure:**
```json
{
  "function": "function_name",
  "description": "Human-readable function description",
  "parameters": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string|number|boolean|array|object",
        "description": "Parameter description",
        "required": true,
        "enum": ["optional", "enumeration", "values"]
      }
    },
    "required": ["param1", "param2"]
  },
  "data_map": {
    "expressions": [...],
    "webhooks": [...],
    "output": {...}
  }
}
```

**Core Schema Elements:**

1. **Function Metadata**
   - `function`: Unique function identifier
   - `description`: Human-readable description for AI understanding
   - `parameters`: JSON Schema for function arguments validation

2. **DataMap Configuration** (`data_map`)
   - `expressions`: Optional pattern-based early return logic
   - `webhooks`: Array of HTTP request configurations
   - `output`: Fallback output when all webhooks fail

**Minimal DataMap Example:**
```json
{
  "function": "simple_api_call",
  "description": "Call external API",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Search query"}
    },
    "required": ["query"]
  },
  "data_map": {
    "webhooks": [{
      "url": "https://api.example.com/search",
      "method": "GET",
      "headers": {"Authorization": "Bearer ${global_data.api_token}"},
      "params": {"q": "${args.query}"},
      "output": {"response": "Result: ${data}"}
    }]
  }
}
```

### 3.2 Function-Level Configuration

Function-level configuration defines the interface between the AI agent and the DataMap execution engine:

**Parameter Schema Definition:**
```json
{
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query text",
        "minLength": 1,
        "maxLength": 500
      },
      "category": {
        "type": "string",
        "description": "Content category filter",
        "enum": ["docs", "api", "tutorials", "blog"],
        "default": "docs"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results",
        "minimum": 1,
        "maximum": 20,
        "default": 5
      },
      "filters": {
        "type": "array",
        "description": "Additional search filters",
        "items": {"type": "string"},
        "maxItems": 10
      }
    },
    "required": ["query"],
    "additionalProperties": false
  }
}
```

**Validation Features:**
- **Type Validation**: Ensures correct data types
- **Range Validation**: Min/max values for numbers and arrays
- **Enumeration**: Restricts to specific allowed values
- **Required Fields**: Ensures essential parameters are provided
- **Default Values**: Automatic parameter population
- **Additional Properties**: Controls extra parameter handling

**AI Integration Benefits:**
```json
{
  "description": "Search the knowledge base for documentation and tutorials. Use specific keywords and categories for better results.",
  "parameters": {
    "properties": {
      "query": {
        "description": "Specific search terms - be precise for better results"
      },
      "category": {
        "description": "Content type: 'docs' for documentation, 'api' for API references, 'tutorials' for guides"
      }
    }
  }
}
```

### 3.3 Nested DataMap Objects

DataMap configurations can include nested objects and complex data structures for advanced use cases:

**Complex Webhook Configuration:**
```json
{
  "data_map": {
    "webhooks": [
      {
        "url": "https://api.primary.com/v2/search",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json",
          "Authorization": "Bearer ${global_data.primary_token}",
          "X-Client-Version": "2.1",
          "X-Request-ID": "${args.request_id}"
        },
        "params": {
          "query": {
            "text": "${args.query}",
            "filters": {
              "category": "${args.category}",
              "date_range": {
                "start": "${args.start_date}",
                "end": "${args.end_date}"
              },
              "tags": "${args.tags}"
            },
            "options": {
              "highlight": true,
              "max_results": "${args.limit}",
              "include_metadata": true
            }
          }
        },
        "foreach": {
          "input_key": "results",
          "output_key": "formatted_results",
          "max": 10,
          "append": "## ${this.title}\n${this.excerpt}\n**Score:** ${this.relevance_score}\n\n"
        },
        "output": {
          "response": "Found ${total} results:\n\n${formatted_results}",
          "action": [
            {
              "SWML": {
                "version": "1.0.0",
                "sections": {
                  "main": [
                    {
                      "set": {
                        "last_search_query": "${args.query}",
                        "last_search_results": "${total}",
                        "search_timestamp": "${timestamp}"
                      }
                    }
                  ]
                }
              }
            }
          ]
        },
        "error_keys": ["error", "message", "detail"]
      }
    ],
    "output": {
      "response": "I'm sorry, the search service is currently unavailable. Please try again later."
    }
  }
}
```

**Nested Structure Benefits:**
- **Complex API Integration**: Support for sophisticated API requirements
- **Conditional Logic**: Dynamic parameter construction based on arguments
- **Rich Response Processing**: Multiple output types and formatting
- **SWML Action Generation**: Create call control actions from API responses

### 3.4 Parameter Validation

Parameter validation ensures data integrity and provides clear error messages when function calls fail validation:

**Comprehensive Validation Example:**
```json
{
  "parameters": {
    "type": "object",
    "properties": {
      "email": {
        "type": "string",
        "description": "Email address to validate",
        "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.[a-zA-Z]{2,}$",
        "maxLength": 254
      },
      "user_preferences": {
        "type": "object",
        "description": "User preference settings",
        "properties": {
          "language": {
            "type": "string",
            "enum": ["en", "es", "fr", "de"],
            "default": "en"
          },
          "notifications": {
            "type": "object",
            "properties": {
              "email": {"type": "boolean", "default": true},
              "sms": {"type": "boolean", "default": false},
              "push": {"type": "boolean", "default": true}
            }
          }
        }
      },
      "metadata": {
        "type": "object",
        "description": "Additional metadata",
        "additionalProperties": true,
        "maxProperties": 20
      }
    },
    "required": ["email"],
    "dependencies": {
      "user_preferences": {
        "properties": {
          "email": {"const": true}
        }
      }
    }
  }
}
```

**Validation Error Handling:**
When validation fails, the AI agent receives clear error messages:

```json
{
  "error": "Parameter validation failed",
  "details": [
    {
      "parameter": "email",
      "message": "Invalid email format",
      "received": "invalid-email"
    },
    {
      "parameter": "limit",
      "message": "Value must be between 1 and 20",
      "received": 50
    }
  ]
}
```

**Best Practices for Parameter Design:**
1. **Clear Descriptions**: Help the AI understand parameter purpose
2. **Appropriate Constraints**: Balance flexibility with validation
3. **Sensible Defaults**: Reduce required parameters where possible
4. **Enum Values**: Provide clear options for categorical parameters
5. **Nested Structure**: Organize complex parameters logically

## 4. Template Expansion System

### 4.1 Template Syntax Overview

Template expansion builds URLs, request parameters and responses from the call's data. SignalWire's platform expands templates when it runs your `data_map` function; the SDK never evaluates one itself. `swaig-test --exec` simulates the expansion locally (see [section 11](#11-development-and-testing)).

**Variables.** `${path}` is replaced by the value at `path` in the template data (see [2.3](#23-context-and-variable-scope)). `%{path}` means the same. A path uses dots for object fields and zero-based `[n]` for array elements, as in `${args.filters.category}` and `${results[0].title}`. If the path is valid but the value isn't set, the template becomes an empty string.

**Prefix helpers.** Inside `${...}`, a helper name and a colon before the path transform the value:

| Helper | What it does | Example |
|---|---|---|
| `lc` | Lowercases the value | `${lc:args.department}` |
| `enc` | URL-encodes the value; the platform's reference also writes it with its encoding named, `enc:url` | `${enc:args.query}` or `${enc:url:args.query}` |

Helpers chain, and apply from left to right. `${lc:enc:args.location}` takes the value of `args.location`, lowercases it, then URL-encodes it, in one step. The built-in weather skill builds its request URL this way:

```
https://api.weatherapi.com/v1/current.json?key=KEY&q=${lc:enc:args.location}
```

**Nested templates** expand from the inside out. In `${meta_data.contacts.${lc:args.department}}`, the inner template turns "Sales" into `sales`, and the outer one then reads `meta_data.contacts.sales`.

**`@{...}` functions** take arguments after a space:

| Function | Syntax | What it does |
|---|---|---|
| `strftime_tz` | `@{strftime_tz <timezone> <format>}` | The current date and time in a time zone, with strftime codes: `@{strftime_tz America/Chicago %Y-%m-%d %H:%M:%S}` |
| `fmt_ph` | `@{fmt_ph <format> <number>}` or `@{fmt_ph <format>:sep:<separator> <number>}` | Formats a phone number as `national` (the default), `international`, `RFC3966` or `e164`, optionally with a separator between digit groups for text-to-speech: `@{fmt_ph national:sep:- ${caller_id_num}}` |
| `expr` | `@{expr <expression>}` | Arithmetic on literal numbers, with `+ - * /` and parentheses; it can't read variables: `@{expr (100 - 25) / 5}` |
| `echo` | `@{echo <text>}` | Returns its argument, for debugging expansion: `@{echo ${args.input}}` |
| `separate` | `@{separate <text>}` | Puts a space between characters, so text-to-speech spells out codes: `@{separate ${args.code}}` reads "ABC123" as "A B C 1 2 3" |
| `sleep` | `@{sleep <seconds>}` | Pauses for that many seconds. Delays can cause timeouts, so use it sparingly |

Template functions work in SWAIG contexts only: `data_map` expressions, webhooks and output, responses from SWAIG function webhooks, and AI prompt variable expansion. Other SWML methods don't expand them.

### 4.2 Variable Types and Sources

- **Function arguments**: `${args.query}`
- **Webhook response fields**, at the root: `${total}`, `${results[0].title}`, and `${array[0].text}` for an array response
- **Global data**: `${global_data.api_token}`
- **Function metadata**: `${meta_data.table}`
- **Call details**: `${call_id}`, `${caller_id_num}`
- **Foreach**: `${this.title}` while walking an array, and the `output_key` it fills, such as `${formatted_results}`

### 4.3 Array and Object Access Patterns

**Array access:**
```
${results[0].title}
${array[0].joke}
```

**Object access:**
```
${current.condition.text}
${args.filters.category}
```

### 4.4 Context-Specific Variables

- In a webhook's `url` and `params`: `args`, `global_data`, `meta_data` and the call details. The response doesn't exist yet.
- In a webhook's `foreach`, `expressions` and `output`: all of those, plus the response's fields (or `array`).
- In a `foreach` `append` template: also `this`, the current element.
- In the top-level `output`, which runs when no webhook produced an output: `args`, `global_data`, `meta_data` and the call details.

### 4.5 Template Expansion Examples

**Simple Template Expansion:**
```
{
  "function": "simple_api_call",
  "description": "Call external API",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {"type": "string", "description": "Search query"}
    },
    "required": ["query"]
  },
  "data_map": {
    "webhooks": [{
      "url": "https://api.example.com/search",
      "method": "GET",
      "headers": {"Authorization": "Bearer ${global_data.api_token}"},
      "params": {"q": "${args.query}"},
      "output": {"response": "Result: ${data}"}
    }]
  }
}
```

**Complex Template Expansion:**
```
{
  "function": "search_knowledge",
  "description": "Search the knowledge base for documentation and tutorials",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Specific search terms - be precise for better results"
      },
      "category": {
        "type": "string",
        "description": "Content type: 'docs' for documentation, 'api' for API references, 'tutorials' for guides",
        "enum": ["docs", "api", "tutorials"],
        "default": "docs"
      }
    },
    "required": ["query"]
  },
  "data_map": {
    "webhooks": [
      {
        "url": "https://api.primary.com/v2/search",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json",
          "Authorization": "Bearer ${global_data.primary_token}",
          "X-Client-Version": "2.1",
          "X-Request-ID": "${args.request_id}"
        },
        "params": {
          "query": {
            "text": "${args.query}",
            "filters": {
              "category": "${args.category}",
              "date_range": {
                "start": "${args.start_date}",
                "end": "${args.end_date}"
              },
              "tags": "${args.tags}"
            },
            "options": {
              "highlight": true,
              "max_results": "${args.limit}",
              "include_metadata": true
            }
          }
        },
        "foreach": {
          "input_key": "results",
          "output_key": "formatted_results",
          "max": 10,
          "append": "## ${this.title}\n${this.excerpt}\n**Score:** ${this.relevance_score}\n\n"
        },
        "output": {
          "response": "Found ${total} results:\n\n${formatted_results}",
          "action": [
            {
              "SWML": {
                "version": "1.0.0",
                "sections": {
                  "main": [
                    {
                      "set": {
                        "last_search_query": "${args.query}",
                        "last_search_results": "${total}",
                        "search_timestamp": "${timestamp}"
                      }
                    }
                  ]
                }
              }
            }
          ]
        },
        "error_keys": ["error", "message", "detail"]
      }
    ],
    "output": {
      "response": "I'm sorry, the search service is currently unavailable. Please try again later."
    }
  }
}
```

## 5. Webhook Configuration and HTTP Processing

### 5.1 Webhook Structure

Each entry in `webhooks` describes one HTTP request. The SWML schema defines these fields:

| Field | Required | What it does |
|---|---|---|
| `url` | Yes | The endpoint. Templates in it are expanded before the request, as in `https://api.example.com/weather?q=${enc:args.city}`. Credentials can go in it as `https://user:password@host/...`. |
| `method` | Yes | The HTTP method, such as `GET` or `POST`. |
| `headers` | No | Headers to send, such as `Authorization`. |
| `params` | No | The request's parameters, sent as its JSON body. Templates in the values are expanded first. The SDK sets this with `.params()`. |
| `input_args_as_params` | No | When true, the function's arguments are merged into `params`. With no `params`, they become the whole body. |
| `require_args` | No | Arguments that must be present for this request to be made. |
| `error_keys` | No | Keys that mark a response as a failure when they appear in it. |
| `foreach`, `expressions`, `output` | No | Evaluated in that order when the response arrives. See [section 7](#7-foreach-processing-and-array-iteration) and [section 8](#8-output-generation-and-result-formatting). |

### 5.2 HTTP Methods and Headers

The request uses the webhook's `method` and `headers`. It has a body when `params` is set or the method is `POST`: the expanded `params` object, as JSON. A `GET` without `params` has no body.

### 5.3 Request Body Construction

`params` is the body. For example, this webhook:

```json
{
  "url": "https://api.example.com/weather",
  "method": "POST",
  "params": {"call_id": "${call_id}", "city": "${args.location}"},
  "output": {"response": "The weather in ${city} is ${temp} degrees and ${conditions}."}
}
```

sends `{"call_id": "...", "city": "New York"}`. Its output then reads `city`, `temp` and `conditions` from the root of the JSON the API returns. With `input_args_as_params: true` and no `params`, the body is the arguments themselves, such as `{"location": "New York"}`.

### 5.4 Sequential Webhook Processing

Webhooks run in array order. The first one to produce an output ends the function, like a `return` statement, so later webhooks act as fallbacks:

```json
{
  "webhooks": [
    {"url": "https://primary-api.example.com/search", "...": "..."},
    {"url": "https://fallback-api.example.com/search", "...": "..."}
  ]
}
```

### 5.5 Webhook Failure Detection

A webhook that fails moves processing to the next one. That includes a response containing one of its `error_keys`, such as `"error_keys": ["error"]` for an API that reports errors in an `error` field. When no webhook produces an output, the top-level `output` runs; without one, the AI gets a generic error.

## 6. Response Processing and Data Handling

### 6.1 Response Data Structure

A webhook's response is parsed as JSON, and joins the template data (see [2.3](#23-context-and-variable-scope)) for its `foreach`, `expressions` and `output`.

### 6.2 Array vs Object Response Handling

An object response's fields are read from the root, with no prefix. For this response:

```json
{"results": [{"title": "Rates", "text": "..."}], "total": 25}
```

`${total}` is `25` and `${results[0].title}` is `Rates`.

An array response is under `array`. For this response:

```json
[{"joke": "Why did the webhook cross the road?"}]
```

`${array[0].joke}` is the joke.

### 6.3 Error Response Processing

DataMap functions can handle errors and provide clear error messages:

**Error Handling Example:**
```json
{
  "error": "API request failed",
  "details": {
    "status_code": 400,
    "message": "Invalid request parameters"
  }
}
```

### 6.4 Custom Error Keys

DataMap functions can define custom error keys to provide more detailed error information:

**Custom Error Keys Example:**
```json
{
  "error": "API request failed",
  "details": {
    "status_code": 400,
    "message": "Invalid request parameters"
  }
}
```

## 7. Foreach Processing and Array Iteration

### 7.1 Foreach Configuration

`foreach` turns an array in the webhook's response into text for the output:

- `input_key` (required): the key in the response whose value is the array, such as `results`.
- `output_key` (required): where the built text is stored; the output reads it as `${formatted_results}`.
- `append` (required): a template added to the text once per element, where `${this.title}` reads the current element's field.
- `max`: the most elements to use, from the start of the array.

**Foreach Configuration Example:**
```json
{
  "foreach": {
    "input_key": "results",
    "output_key": "formatted_results",
    "max": 5,
    "append": "Result: ${this.title}\n"
  }
}
```

For a response of `{"results": [{"title": "Rates"}, {"title": "Coverage"}]}`, `${formatted_results}` is `Result: Rates` and `Result: Coverage`, one per line.

### 7.2 Array Data Sources

`input_key` names a field of the webhook's response that holds an array. It's a key name, such as `results`, not a template.

### 7.3 Template Expansion in Foreach

DataMap functions can expand template variables within foreach append templates:

**Foreach Template Expansion Example:**
```json
{
  "foreach": {
    "input_key": "results",
    "output_key": "formatted_results",
    "max": 5,
    "append": "Result: ${this.title}\n"
  }
}
```

### 7.4 String Concatenation and Formatting

DataMap functions can concatenate and format string data:

**String Concatenation Example:**
```json
{
  "response": {
    "formatted_results": "Result: ${this.title}\n"
  }
}
```

### 7.5 Foreach Limitations and Best Practices

DataMap functions should be used cautiously when processing large arrays:

**Foreach Limitations:**
- **Performance**: Processing large arrays can be slow
- **Memory**: Large arrays can consume significant memory

**Best Practices:**
1. **Limit Array Size**: Use pagination or limit parameters
2. **Optimize Template Expansion**: Minimize array access in templates
3. **Use Foreach with Caution**: Only use when necessary

## 8. Output Generation and Result Formatting

### 8.1 Webhook-Level Output

DataMap functions can return output directly from webhook responses:

**Webhook Output Example:**
```json
{
  "response": {
    "formatted_results": "Result: ${this.title}\n"
  }
}
```

### 8.2 DataMap-Level Fallback Output

DataMap functions can provide a fallback output when all webhooks fail:

**Fallback Output Example:**
```json
{
  "output": {
    "response": "Search service unavailable"
  }
}
```

### 8.3 Response vs Action Outputs

DataMap functions can return both response text and SWML actions:

**Response vs Action Output Example:**
```json
{
  "response": {
    "formatted_results": "Result: ${this.title}\n"
  },
  "action": [{"SWML": {"version": "1.0.0", "...": "..."}}]
}
```

### 8.4 SWML Action Generation

DataMap functions can generate SWML actions for call control:

**SWML Action Generation Example:**
```json
{
  "action": [{"SWML": {"version": "1.0.0", "...": "..."}}]
}
```

## 9. Skills System Integration

### 9.1 DataMap Skills vs Raw Configuration

DataMap functions can be integrated with the skills system:

**Skills System Integration Example:**
```json
{
  "function": "search_knowledge",
  "description": "Search the knowledge base for documentation and tutorials",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Specific search terms - be precise for better results"
      },
      "category": {
        "type": "string",
        "description": "Content type: 'docs' for documentation, 'api' for API references, 'tutorials' for guides",
        "enum": ["docs", "api", "tutorials"],
        "default": "docs"
      }
    },
    "required": ["query"]
  },
  "data_map": {
    "webhooks": [
      {
        "url": "https://api.primary.com/v2/search",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json",
          "Authorization": "Bearer ${global_data.primary_token}",
          "X-Client-Version": "2.1",
          "X-Request-ID": "${args.request_id}"
        },
        "params": {
          "query": {
            "text": "${args.query}",
            "filters": {
              "category": "${args.category}",
              "date_range": {
                "start": "${args.start_date}",
                "end": "${args.end_date}"
              },
              "tags": "${args.tags}"
            },
            "options": {
              "highlight": true,
              "max_results": "${args.limit}",
              "include_metadata": true
            }
          }
        },
        "foreach": {
          "input_key": "results",
          "output_key": "formatted_results",
          "max": 10,
          "append": "## ${this.title}\n${this.excerpt}\n**Score:** ${this.relevance_score}\n\n"
        },
        "output": {
          "response": "Found ${total} results:\n\n${formatted_results}",
          "action": [
            {
              "SWML": {
                "version": "1.0.0",
                "sections": {
                  "main": [
                    {
                      "set": {
                        "last_search_query": "${args.query}",
                        "last_search_results": "${total}",
                        "search_timestamp": "${timestamp}"
                      }
                    }
                  ]
                }
              }
            }
          ]
        },
        "error_keys": ["error", "message", "detail"]
      }
    ],
    "output": {
      "response": "I'm sorry, the search service is currently unavailable. Please try again later."
    }
  }
}
```

### 9.2 Skill-Based DataMap Creation

A skill builds this same structure with the `DataMap` fluent builder instead of hand-written JSON. The `joke`, `swml_transfer`, and `datasphere_serverless` skills all create their tool this way. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 9.3 Skill Configuration Patterns

The `parameters` dict a skill passes to `DataMap.parameter()` becomes this function definition's JSON Schema, in the same shape as the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 9.4 Multi-Instance Skill Usage

Each `add_skill()` call with a distinct `tool_name` builds its own DataMap function, so the same skill can register more than one tool on one agent. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

## 10. Practical Examples and Use Cases

### 10.1 API Integration Examples

A DataMap webhook can call any REST API that returns JSON, using the same `webhooks`, `params`, and `output` fields as the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 10.2 Knowledge Base Search

The built-in `datasphere_serverless` skill uses a DataMap webhook this way, to search a document index without a webhook server. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 10.3 External Service Integration

The `error_keys` list on the worked example's webhook, in [9.1](#91-datamap-skills-vs-raw-configuration), lets a DataMap function detect a third-party API's own error format. It looks past HTTP status alone.

### 10.4 Multi-Step Processing Workflows

A DataMap function's `webhooks` array is a fallback chain. The platform tries each entry in order and stops at the first success, as in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration). It does not let one webhook read an earlier webhook's response in the same call.

## 11. Development and Testing

### 11.1 Local Development Setup

Use `swaig-test` to run a DataMap function locally against its real webhook, without deploying an agent. See the [CLI guide](cli_guide.md) for the command, and the worked example in [9.1](#91-datamap-skills-vs-raw-configuration) for the configuration shape.

### 11.2 Environment Variable Configuration

Read a secret from `os.environ` when you build the DataMap in Python. Or reference `${global_data.key}` in a header or parameter instead, as in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration), if the value is set into global data at runtime.

### 11.3 CLI Testing Tools

`swaig-test --exec <function> --verbose` runs a DataMap function's real webhook and prints each processing stage. See [DataMap Function Testing](cli_guide.md#datamap-function-testing) in the CLI guide, and the worked example in [9.1](#91-datamap-skills-vs-raw-configuration) for the configuration it is testing.

### 11.4 Debugging DataMap Execution

`--verbose` traces template expansion, the HTTP request and response, and fallback handling. See [Troubleshooting](cli_guide.md#troubleshooting) in the CLI guide, and the worked example in [9.1](#91-datamap-skills-vs-raw-configuration) for the configuration shape.

The simulation expands templates as [section 4](#4-template-expansion-system) describes: paths, the `lc` and `enc` helpers, and nested templates. It leaves `@{...}` functions as they are, and a path that doesn't resolve shows as `<MISSING:path>`. It builds the call's arguments, but not global data, metadata or the call details the platform adds. It also accepts an argument without its `args.` prefix, as `${location}`; write `${args.location}`, the form the platform documents.

## 12. Advanced Patterns and Techniques

### 12.0 Helper Functions

For common patterns, convenience functions simplify DataMap creation:

#### Simple API Tool

`create_simple_api_tool` builds a one-webhook DataMap from a URL and a response template:

```python
from signalwire.core.data_map import create_simple_api_tool

weather = create_simple_api_tool(
    name='get_weather',
    url='https://api.weather.com/v1/current?key=API_KEY&q=${args.location}',
    response_template='Weather: ${current.condition.text}, ${current.temp_f}°F',
    parameters={
        'location': {
            'type': 'string',
            'description': 'City name',
            'required': True
        }
    },
    headers={'X-API-Key': 'your-api-key'},
    error_keys=['error']
)
```

#### Expression Tool

`create_expression_tool` builds a pattern-matching DataMap that returns a result without calling a webhook:

```python
from signalwire.core.data_map import create_expression_tool

control = create_expression_tool(
    name='media_control',
    # Maps a test value to a (regex, FunctionResult) tuple. The test value is
    # matched against the pattern; on a match the FunctionResult is emitted.
    patterns={
        '${args.command}': (
            r'start|play|begin',
            FunctionResult().add_action('start', True),
        ),
    },
    parameters={
        'command': {'type': 'string', 'description': 'Control command'}
    }
)
```

### 12.1 Multiple Webhook Fallback Chains

DataMap functions can be configured with multiple webhooks to handle different scenarios and provide fallback mechanisms:

**Multiple Webhook Configuration Example:**
```json
{
  "webhooks": [
    {"url": "https://primary-api.com/search", "...": "..."},
    {"url": "https://fallback-api.com/search", "...": "..."}
  ]
}
```

### 12.2 Complex Template Expressions

Nest object and array access freely inside a template, such as `${data.results[0].title}` or `${args.filters.category}`, as the worked example in [9.1](#91-datamap-skills-vs-raw-configuration) does for its search filters.

### 12.3 Dynamic API Endpoint Selection

Put `${args.region}` directly in the URL string passed to `.webhook()`. The platform expands it per call, using that call's actual argument values. A Python f-string in the same spot is fixed once, when the agent builds the DataMap. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 12.4 Response Transformation Patterns

Reshape a response with the `output` template's own string interpolation, such as `${total} results: ${formatted_results}`, rather than a separate transformation step. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

## 13. Error Handling and Reliability

### 13.1 HTTP Error Codes and Handling

DataMap functions can handle various HTTP error codes:

**HTTP Error Handling Example:**
```json
{
  "error": "API request failed",
  "details": {
    "status_code": 400,
    "message": "Invalid request parameters"
  }
}
```

### 13.2 Network Timeout and Retry Logic

A DataMap function has no configurable timeout or retry count. Add a second entry to the `webhooks` array as a fallback for when the first one fails, as in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 13.3 Graceful Degradation Strategies

Set a `fallback_output()` at the DataMap level for when every webhook in the chain fails, as in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 13.4 Monitoring and Observability

For DataMap monitoring, rely on `swaig-test --verbose` during development, and your own logging inside any webhook you host. The `data_map` structure itself has no monitoring or metrics option. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

## 14. Security and Best Practices

### 14.1 API Key Management

Keep an API key in `global_data` or a header, not as a literal string in the DataMap definition. The worked example in [9.1](#91-datamap-skills-vs-raw-configuration) does this with `${global_data.primary_token}`.

### 14.2 Secure Header Configuration

Pass a `headers` dict to `.webhook()`, as in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration), for any header the API needs, including authentication.

### 14.3 Input Validation and Sanitization

The `parameters` JSON Schema, the same one `.parameter()` builds in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration), is what the platform uses to validate a function call's arguments.

### 14.4 Rate Limiting Considerations

A DataMap function has no built-in rate limiting. Track request volume in the API you call, or in `global_data` between calls, if you need to cap usage. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

## 15. Performance Optimization

### 15.1 Request Optimization

Request only what you need: a narrow `params`/`body`, and a `foreach.max` cap on how many array items to format, as in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 15.2 Response Size Management

A `data_map` response has no size limit of its own. Keep an `output` template's interpolated fields short, and use `foreach.max` to cap how many array items you format, as in the worked example in [9.1](#91-datamap-skills-vs-raw-configuration). The platform enforces its own limits on the final response; see [2.4 Serverless Execution Model](#24-serverless-execution-model).

### 15.3 Caching Strategies

A `data_map` response has no cache of its own; each call re-runs the webhook. Cache upstream, in the API you call, if repeated identical requests are expensive. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 15.4 Execution Time Considerations

Each webhook in the chain runs in sequence until one succeeds, so a slow or unreachable primary API delays every fallback behind it. Keep the `webhooks` array short, and order it fastest and most reliable first. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

## 16. Migration and Upgrade Paths

### 16.1 From Webhook to DataMap Migration

Move logic that a Python webhook handler used to compute into `${...}` templates and `error_keys`, as the [traditional webhook vs DataMap comparison](#12-datamap-vs-traditional-webhooks) shows. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration) for the resulting shape.

### 16.2 Legacy Configuration Support

The SDK has one `DataMap` class and one `data_map` JSON shape; there is no older format to support side by side. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 16.3 Version Compatibility

A `data_map` function is plain JSON inside the SWAIG function definition, so it is versioned with the rest of your SWML document, not on its own. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

### 16.4 Gradual Migration Strategies

Run a DataMap function and a webhook function side by side under different names. Switch your prompt's instructions from one to the other once you trust the replacement. See the worked example in [9.1](#91-datamap-skills-vs-raw-configuration).

---

*This guide provides comprehensive coverage of DataMap functionality within the SignalWire AI Agents framework, from basic concepts to advanced implementation patterns.*

## Related Documentation

For related topics, see:

- **[API Reference](api_reference.md)** - Complete DataMap class API reference
- **[SWAIG Reference](swaig_reference.md)** - SWAIG function results and actions
- **[Agent Guide](agent_guide.md)** - General agent development including SWAIG functions
- **[Contexts Guide](contexts_guide.md)** - Structured workflows with function restrictions
