# Getting Started with Research Agent System

This guide will help you set up and run the multi-agent research analysis system.

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure API Key

**Required:** Get an OpenRouter API key
1. Go to https://openrouter.ai/
2. Sign up / Log in
3. Get your API key from the dashboard

**Create .env file:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# Replace 'your_openrouter_api_key_here' with your actual key
```

Your `.env` file should look like:
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx

# Budget-Recommended Models (keep these defaults for testing)
PERFORMANCE_ANALYST_MODEL=deepseek/deepseek-chat
CRITIQUE_AGENT_MODEL=deepseek/deepseek-chat
SYNTHESIZER_MODEL=google/gemini-flash-1.5 # Depending on your budget, opus would be a better model
```

### 3. Check Configuration

```bash
python src/config.py
```

You should see:
- ✅ OpenRouter API Key: Configured
- Model configuration details
- Cost estimate per analysis

### 4. Run Your First Analysis

```bash
python src/main.py "Analyze the ReAct framework for LLM reasoning"
```

This will:
1. Search ArXiv for relevant papers
2. Performance Analyst analyzes innovations and benefits
3. Critique Agent analyzes limitations and concerns
4. Synthesizer creates balanced report
5. Save report to `outputs/reports/`

## Configuration Details

### Model Selection (Budget-Conscious)

The default configuration is optimized for cost-effectiveness:

**Default (Recommended for Testing):**
- **Cost:** ~$0.02-0.05 per analysis
- **Performance Analyst:** DeepSeek Chat ($0.14/$0.28 per 1M tokens)
- **Critique Agent:** DeepSeek Chat ($0.14/$0.28 per 1M tokens)
- **Synthesizer:** Gemini Flash 1.5 ($0.075/$0.30 per 1M tokens)
- **Quality:** Excellent for research analysis

**Ultra Budget Option:**
```bash
# In .env, set all to DeepSeek:
SYNTHESIZER_MODEL=deepseek/deepseek-chat
```
- **Cost:** ~$0.01-0.03 per analysis
- **Quality:** Still very good

**Better Synthesis Option:**
```bash
# In .env:
SYNTHESIZER_MODEL=anthropic/claude-3-haiku
```
- **Cost:** ~$0.05-0.15 per analysis
- **Quality:** Excellent synthesis

### Email Configuration (Optional)

Email delivery is **optional**. Reports are always saved locally.

To enable email delivery:

1. **For Gmail users:**
   ```bash
   # In .env:
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   EMAIL_FROM=your_email@gmail.com
   EMAIL_TO=recipient@example.com
   ```

2. **Get Gmail App Password:**
   - Enable 2-Factor Authentication on your Google account
   - Go to: [Google Account → Security → App Passwords](https://myaccount.google.com/apppasswords)
   - Generate password for "Mail"
   - Use this password in `SMTP_PASSWORD` (NOT your regular Gmail password)

3. **Test email connection:**
   ```bash
   python -c "from src.mcp_servers.email_server.email_tools import EmailSender; import os; from dotenv import load_dotenv; load_dotenv(); s = EmailSender(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT', 587)), os.getenv('SMTP_USERNAME'), os.getenv('SMTP_PASSWORD'), os.getenv('EMAIL_FROM')); print(s.test_connection())"
   ```

## Usage Examples

### Basic Analysis

```bash
python src/main.py "Analyze the ReAct framework for LLM reasoning and tool use"
```

### Compare Techniques

```bash
python src/main.py "Compare RLHF and DPO alignment techniques for LLMs"
```

### Analyze Model Architecture

```bash
python src/main.py "Summarize Llama 3 architecture, training techniques, and innovations"
```

### Analyze Framework

```bash
python src/main.py "Analyze Reflexion framework for self-reflection in agents"
```

### Check Status

```bash
# Check configuration
python src/main.py --status

# Check cost estimate
python src/main.py --cost
```

## What Happens During Analysis

1. **Performance Analyst** searches ArXiv and analyzes:
   - What makes the work unique
   - Technical innovations (architecture, techniques)
   - Why approaches work (theory)
   - Practical benefits

2. **Critique Agent** searches ArXiv and analyzes:
   - Reproducibility challenges
   - Computational costs
   - Failure modes and limitations
   - When approaches don't work

3. **Synthesizer** creates balanced report with:
   - Executive Summary
   - Innovations & Contributions
   - Critical Analysis
   - Balanced Assessment (tradeoffs, when to use)
   - Recommendations

4. **Reports saved to:** `outputs/reports/TIMESTAMP_query.md`

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run basic tests only
pytest tests/test_basic.py -v
```

## Troubleshooting

### "OpenRouter API key not found"

**Solution:** Add your API key to `.env` file:
```bash
OPENROUTER_API_KEY=sk-or-v1-your-actual-key
```

### "No papers found"

**Possible causes:**
- Query too specific - try broader terms
- ArXiv API timeout - try again
- Check internet connection

**Try:**
```bash
# Instead of: "GPT-4V multimodal architecture 2024"
# Use: "multimodal vision language models"
```

### "Email sending failed"

**Solutions:**
1. Email is optional - reports are still saved locally
2. For Gmail: Use App Password, not regular password
3. Enable 2FA on Google account first
4. Check SMTP settings in `.env`

### Import Errors

**Solution:**
```bash
# Make sure you're in the venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### "Rate limit exceeded"

**Solution:**
- OpenRouter has rate limits per key
- Wait a few minutes and try again
- Check your OpenRouter dashboard for limits

## Cost Management

### Estimated Costs

| Configuration | Per Analysis | 100 Analyses |
|--------------|-------------|-------------|
| All DeepSeek | $0.01-0.03 | $1-3 |
| DeepSeek + Gemini Flash (default) | $0.02-0.05 | $2-5 |
| DeepSeek + Claude Haiku | $0.05-0.15 | $5-15 |
| DeepSeek + Claude Sonnet | $0.20-0.50 | $20-50 |

### Tips to Reduce Costs

1. **Use default models** (DeepSeek + Gemini Flash)
2. **Limit paper searches** - reduce `ARXIV_MAX_RESULTS` in `.env`
3. **Test with short queries** first
4. **Monitor usage** on OpenRouter dashboard

### Monitor Your Spending

- Check: https://openrouter.ai/activity
- Set spending limits in OpenRouter settings
- Each analysis shows model usage in output

## Next Steps

### For Research
- Try different research topics
- Compare frameworks (ReAct vs Reflexion)
- Analyze training techniques (RLHF vs DPO vs PPO)
- Study model architectures (Llama, GPT, Claude)

### For Production
- Consider adding web GUI (Gradio or Streamlit)
- Set up scheduled analyses (daily/weekly digests)
- Add more data sources beyond ArXiv
- Implement caching for repeated queries

### For Development
- Review [CLAUDE.md](CLAUDE.md) for architecture details
- Modify agent system messages for different perspectives
- Add new tools for other data sources
- Extend report formats

## Support

### Issues
- Check existing issues: https://github.com/your-repo/issues
- Create new issue with error details

### Documentation
- Project architecture: [CLAUDE.md](CLAUDE.md)
- Code structure: See inline comments
- AutoGen docs: https://microsoft.github.io/autogen/

## Example Output

After running an analysis, you'll find in `outputs/reports/`:

```
20250113_143022_Analyze_ReAct_framework.md
```

Contents:
```markdown
# Research Analysis: ReAct Framework for LLM Reasoning

## Executive Summary
[High-level overview]

## Innovations & Contributions
### Framework Pattern
[Details on ReAct's reasoning + acting approach]

### Technical Details
[How it works]

### Benefits
[Why it's effective]

## Critical Analysis
### Computational Costs
[Inference overhead analysis]

### Limitations
[When it fails]

## Balanced Assessment
[Tradeoffs and recommendations]

## Recommendations
[For researchers, practitioners, field]

## Referenced Papers
[Full citations with ArXiv links]
```

---

**Ready to start?** Run your first analysis:

```bash
python src/main.py "Analyze Constitutional AI for LLM alignment"
```
