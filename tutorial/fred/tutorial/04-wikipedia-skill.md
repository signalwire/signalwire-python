# Lesson 4: Adding the Wikipedia Search Skill

Fred's job is answering questions from Wikipedia. Instead of writing the search code, this lesson adds the SDK's `wikipedia_search` skill, configures it, and looks at what the skill does inside the agent.

## Table of Contents

1. [Understanding Skills](#understanding-skills)
2. [Adding the Wikipedia Skill](#adding-the-wikipedia-skill)
3. [Configuring the Skill](#configuring-the-skill)
4. [How Skills Work Internally](#how-skills-work-internally)
5. [Testing Wikipedia Search](#testing-wikipedia-search)
6. [How Fred Uses Wikipedia Search](#how-fred-uses-wikipedia-search)
7. [Skill Benefits](#skill-benefits)

---

## Understanding Skills

Skills are modules that add a capability to an agent, much like plugins.

### What Is a Skill?

A skill has four properties:

- It's a self-contained module with one capability
- It registers its own functions and prompt text with the agent
- It's configured with a dictionary of parameters
- It can be reused across agents

### Available Built-in Skills

The SDK includes several ready-made skills, including:

- `wikipedia_search`: search Wikipedia articles
- `datetime`: get the current date and time
- `math`: perform calculations
- `web_search`: search the web with the Google Custom Search API (needs an API key)
- `weather_api`: get weather from WeatherAPI.com (needs an API key)

## Adding the Wikipedia Skill

Adding a skill takes one line in the agent's constructor.

### Step 1: Basic Skill Addition

Add this to Fred's `__init__` method, after the global data:

```python
        # Add the Wikipedia search skill
        self.add_skill("wikipedia_search")
```

With that line, Fred can search Wikipedia. The next step tunes the skill for Fred.

### Step 2: Customized Configuration

Replace the basic line with a configured version:

```python
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
```

## Configuring the Skill

The configuration dictionary has three options.

### Configuration Parameters

Each option changes one part of how the skill behaves:

| Option | Default | What it does |
|---|---|---|
| `num_results` | `1` | The number of Wikipedia articles to return. More results cover more ground, and make longer responses. Fred uses 2. |
| `no_results_message` | A generic "couldn't find" message | What the function returns when no article matches. `{query}` is replaced with the search term. Write it in the agent's voice, because the model relays it to the caller. |
| `swaig_fields` | None | Extra settings for the function the skill registers. `fillers` are phrases the platform says while the search runs. |

### Example Configurations

Different agents need different settings:

```python
# Minimal configuration
self.add_skill("wikipedia_search")

# Academic assistant
self.add_skill("wikipedia_search", {
    "num_results": 3,
    "no_results_message": "No Wikipedia entries found for '{query}'. Check the spelling or try related terms."
})

# Casual helper
self.add_skill("wikipedia_search", {
    "num_results": 1,
    "no_results_message": "Hmm, Wikipedia doesn't have info on '{query}'. Got another topic?",
    "swaig_fields": {
        "fillers": {
            "en-US": ["Let me check...", "Looking that up..."]
        }
    }
})
```

## How Skills Work Internally

`add_skill()` does three things when it runs.

### What Happens When You Add a Skill

1. **Skill loading.** The SDK imports the skill's module:

   ```python
   # The SDK dynamically imports the skill module
   from signalwire.skills.wikipedia_search.skill import WikipediaSearchSkill
   ```

2. **Skill initialization.** It creates the skill with your configuration:

   ```python
   # Creates skill instance with your configuration
   skill = WikipediaSearchSkill(agent=self, params=config)
   ```

3. **Tool registration.** The skill registers its function with the agent. This is the skill's own code:

   ```python
   # Inside WikipediaSearchSkill.register_tools()
   self.define_tool(
       name="search_wiki",
       description="Search Wikipedia for information about a topic and get article summaries",
       parameters={
           "query": {
               "type": "string",
               "description": "The search term or topic to look up on Wikipedia",
           }
       },
       handler=self._search_wiki_handler,
   )
   ```

The skill also adds a "Wikipedia Search" section to the prompt, which tells the model when to use the function.

### The search_wiki Function

After adding the skill, Fred has a `search_wiki` function with this signature:

<!-- snippet: no-compile signature-illustration (pseudo-signature; `string` is not a Python type) -->
```python
search_wiki(query: string) -> string
```

When the model calls it, the function:

1. Searches Wikipedia for articles that match the query
2. Retrieves each article's summary
3. Returns the summaries as text

The model calls it with the caller's topic, for example:

- `search_wiki("Albert Einstein")`
- `search_wiki("quantum physics")`
- `search_wiki("Great Wall of China")`

## Testing Wikipedia Search

A `main` function can confirm the skill loaded, without starting a server.

### Step 3: Update Main Function

Replace `main` with this version:

<!-- snippet: no-run illustrative fragment (references `FredTheWikiBot` established in the surrounding prose) -->
```python
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
    print()
    
    # Create Fred
    fred = FredTheWikiBot()
    
    # Show loaded skills
    loaded_skills = fred.list_skills()
    print(f"Fred's skills: {', '.join(loaded_skills)}")
    print()
    
    # The skill automatically adds tools to the agent
    # You can verify this by checking registered functions
    print("Wikipedia search is ready.")
    
if __name__ == "__main__":
    main()
```

Run the file to build Fred and list its skills:

```bash
python fred.py
```

The output lists the loaded skill:

```
============================================================
Fred: a Wikipedia knowledge bot
============================================================

Fred searches Wikipedia and shares facts about Wikipedia itself.

Questions to try:
  - Tell me about Albert Einstein
  - What is quantum physics?
  - Who was Marie Curie?
  - Search for information about the solar system

Fred's skills: wikipedia_search

Wikipedia search is ready.
```

## How Fred Uses Wikipedia Search

When a caller asks about a topic, five things happen:

1. **The caller says:** "Tell me about Albert Einstein"
2. **The model decides** the question needs Wikipedia
3. **The model calls** `search_wiki("Albert Einstein")`
4. **The skill returns** the article summaries
5. **The model answers** the caller, in Fred's voice

### Example Conversation Flow

A conversation with Fred might go like this:

```
Caller: "Hi there!"
Fred:   "Hello! I'm Fred, your friendly Wikipedia assistant! What would you like to know about today?"

Caller: "Tell me about black holes"
Fred:   [filler] "Let me look that up on Wikipedia for you..."
Fred:   "Fascinating topic! According to Wikipedia, a black hole is a region of spacetime where gravity is so strong that nothing, not even light, can escape from it..."

Caller: "That's interesting! Who discovered them?"
Fred:   [filler] "Searching Wikipedia for that information..."
Fred:   "Great question! The idea of black holes has a long history..."
```

## Skill Benefits

A skill saves you from writing and maintaining the integration yourself.

### Why Use Skills Instead of Custom Code?

With the skill, Wikipedia search is one line:

```python
# One line
self.add_skill("wikipedia_search")
```

Without it, you'd write every part yourself:

```python
# You'd need to:
# 1. Choose a Wikipedia API
# 2. Make the API calls
# 3. Parse the responses
# 4. Format the results
# 5. Handle errors
# 6. Register a SWAIG function
# 7. Write its handler
```

### What Skills Provide

Using a skill gives you:

1. **Tested functionality**: built and tested with the SDK
2. **A consistent interface**: every skill is configured the same way
3. **Error handling**: failures return a message instead of crashing the call
4. **Documentation**: each skill has a README in the SDK
5. **Maintenance**: fixes arrive with SDK updates

## Next Steps

Fred can search Wikipedia. Next, add a function of your own that shares facts about Wikipedia. Continue with [Lesson 5: Creating Custom Functions](05-custom-functions.md).

---

[Previous: Basic Agent](03-basic-agent.md) | [Overview](README.md) | [Next: Custom Functions](05-custom-functions.md)
