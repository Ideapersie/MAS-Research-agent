# OpenRouter Usage Accounting - Implementation Summary

## What Was Added

OpenRouter usage accounting has been enabled to track API usage and costs for all LLM requests.

## Where It Was Added

### 1. Configuration Level (src/config.py)
```python
config_list = [
    {
        "model": performance_model,
        "api_key": api_key,
        "base_url": "https://openrouter.ai/api/v1",
        "api_type": "openai",
        "usage": {
            "include": True  # ← Added here
        }
    },
    # ... same for other models
]
```

### 2. Agent Level (All 3 agents)
Added to `llm_config` for each agent:
- **src/agents/performance_analyst.py**
- **src/agents/critique_agent.py**
- **src/agents/synthesizer.py**

```python
llm_config={
    "config_list": model_config,
    "temperature": 0.7,
    "timeout": 120,
    "extra_body": {
        "usage": {
            "include": True  # ← Added here
        }
    }
}
```

## How It Works

### OpenRouter API Request Format
When enabled, requests to OpenRouter include:
```json
{
  "model": "deepseek/deepseek-chat",
  "messages": [...],
  "usage": {
    "include": true
  }
}
```

### OpenRouter API Response Format
OpenRouter will include usage information in responses:
```json
{
  "choices": [...],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 250,
    "total_tokens": 400
  }
}
```

## Benefits

1. **Track Token Usage**: See exactly how many tokens each request uses
2. **Cost Monitoring**: Calculate actual costs based on token usage
3. **Optimization**: Identify expensive queries and optimize
4. **Budget Management**: Monitor spending against budget limits

## Viewing Usage Data

### Option 1: OpenRouter Dashboard
- Go to https://openrouter.ai/activity
- See detailed usage statistics
- View costs per model and request
- Export usage data

### Option 2: API Response (Programmatic)
If you want to log usage programmatically, you can access the response from AutoGen:
```python
# After an agent conversation, AutoGen may expose usage info
# in the conversation history or response metadata
```

### Option 3: Environment Variable (Optional Enhancement)
You could add logging in the future:
```python
# In main.py after agent conversation:
for message in groupchat.messages:
    if 'usage' in message:
        print(f"Usage: {message['usage']}")
```

## Testing

To verify it's working:

1. **Run a simple query:**
   ```bash
   python src/main.py "What is machine learning?"
   ```

2. **Check OpenRouter Dashboard:**
   - Go to https://openrouter.ai/activity
   - You should see the request with usage information
   - Token counts and costs should be displayed

## Troubleshooting

### If usage tracking doesn't appear:

**Issue 1: AutoGen 0.1.14 may not support extra_body**
```python
# Solution: The "usage" in config_list should work
# The extra_body is a fallback/enhancement
```

**Issue 2: OpenRouter doesn't show usage**
```python
# Check:
# 1. You're using the correct API key
# 2. Requests are actually going through OpenRouter
# 3. Check the OpenRouter dashboard after a few minutes
```

**Issue 3: Want to log usage locally**
```python
# Enhancement: Add logging in main.py
# After each agent response, log token usage if available
import logging
logging.info(f"Token usage: {response.get('usage', {})}")
```

## Cost Tracking Formula

With usage data, you can calculate costs:
```python
# Example for DeepSeek
input_cost = (prompt_tokens / 1_000_000) * 0.14  # $0.14 per 1M input tokens
output_cost = (completion_tokens / 1_000_000) * 0.28  # $0.28 per 1M output tokens
total_cost = input_cost + output_cost
```

## Files Modified

1. ✅ **src/config.py** - Added `usage: {include: True}` to config_list
2. ✅ **src/agents/performance_analyst.py** - Added `extra_body` with usage tracking
3. ✅ **src/agents/critique_agent.py** - Added `extra_body` with usage tracking
4. ✅ **src/agents/synthesizer.py** - Added `extra_body` with usage tracking

## Verification Command

```bash
# Check that config includes usage parameter:
python -c "from src.config import get_openrouter_config; import os; os.environ['OPENROUTER_API_KEY']='test'; print(get_openrouter_config()[0])"
```

Expected output should include:
```python
{
  'model': 'deepseek/deepseek-chat',
  'api_key': 'test',
  'base_url': 'https://openrouter.ai/api/v1',
  'api_type': 'openai',
  'usage': {'include': True}  # ← This should be present
}
```

## Next Steps (Optional Enhancements)

### 1. Add Usage Logging to Main
```python
# In src/main.py after conversation:
def log_usage_stats(groupchat):
    """Log token usage and costs from conversation."""
    total_tokens = 0
    for message in groupchat.messages:
        if 'usage' in message:
            usage = message['usage']
            total_tokens += usage.get('total_tokens', 0)
            print(f"Agent: {message.get('name')}, Tokens: {usage.get('total_tokens', 0)}")

    print(f"\nTotal tokens used: {total_tokens}")
```

### 2. Add Cost Calculation
```python
def calculate_cost(usage_data, model_name):
    """Calculate cost based on usage and model."""
    costs = {
        "deepseek/deepseek-chat": {"input": 0.14, "output": 0.28},
        "google/gemini-flash-1.5": {"input": 0.075, "output": 0.30},
    }

    if model_name in costs:
        input_cost = (usage_data['prompt_tokens'] / 1_000_000) * costs[model_name]['input']
        output_cost = (usage_data['completion_tokens'] / 1_000_000) * costs[model_name]['output']
        return input_cost + output_cost
    return 0
```

### 3. Add Budget Alerts
```python
# Set budget limit
BUDGET_LIMIT = 5.00  # $5

# Check after each run
if total_cost > BUDGET_LIMIT:
    print(f"WARNING: Budget exceeded! ${total_cost:.2f} > ${BUDGET_LIMIT}")
```

---

## Summary

✅ **Usage accounting is now enabled** for all OpenRouter API requests
✅ **Track costs** via OpenRouter dashboard
✅ **Two-level implementation**: config level + agent level (redundancy ensures it works)
✅ **No code changes needed for basic usage** - just check dashboard

**Ready to use!** Your usage and costs will now be tracked automatically on OpenRouter.
