# multi-llm

Smart launcher for the Gemini CLI. Rotates free API keys automatically and uses Groq to make them last longer.

## Quick Start

```bash
git clone https://github.com/radostingg-eng/multi-llm.git
cd multi-llm
bash setup.sh       # installs git hooks + test deps
./multi-llm         # first run: finds your keys, validates them, launches Gemini CLI
```

**Shortcut:** after setup, use `ml` from anywhere instead of `multi-llm`.

## What It Does

| You type | What happens |
|---|---|
| `ml` | Launches Gemini CLI with next available key |
| `ml "what is a mutex"` | Groq answers instantly — no Gemini quota burned |
| `ml "refactor the auth module"` | Groq enhances your prompt, then launches Gemini CLI |
| All Gemini keys exhausted | Drops into Groq quick-chat (text only, shows countdown) |
| Exit Gemini CLI | Groq summarizes session, loads it as context next time |

## Smart Features (powered by Groq)

1. **Smart routing** — Simple questions go to Groq instantly. Complex tasks go to Gemini CLI. Saves your Gemini quota for real work.
2. **Prompt enhancer** — Groq rewrites your prompt before Gemini sees it. Better prompts = better results = fewer follow-ups.
3. **Quick-chat fallback** — When all Gemini keys are on cooldown, you get Groq chat instead of a dead end. Clearly labeled as text-only.
4. **Session memory** — After each Gemini session, Groq summarizes what you did. Next launch feeds it back as context.

## Getting Free API Keys

### Gemini (Google)
1. Go to https://aistudio.google.com/apikey
2. Click **Create API Key**
3. Copy it (starts with `AIza...`)

### Groq
1. Go to https://console.groq.com/keys
2. Sign up / log in
3. Click **Create API Key**
4. Copy it (starts with `gsk_...`)

Keys are validated on setup — bad keys are caught immediately.

**Tip:** Multiple Google/Groq accounts = more free usage.

## Commands

```
ml                      Launch Gemini CLI
ml "question"           Smart route (Groq or Gemini)
ml --status             Show which keys are ready
ml --add                Add more keys
ml --update             Pull latest version
ml --reset              Clear all cooldowns
ml --no-enhance         Skip prompt enhancement
```

Gemini CLI flags pass through:
```
ml -p "explain this code"
ml --model gemini-2.5-pro
```

## Updating

```
ml --update
```

## For Developers

```bash
bash setup.sh                     # one-time: hooks + pytest
python3 -m pytest tests/ -v      # 27 tests
```

**Quality gates:**
- Pre-commit hook: syntax check + tests + blocks config.json
- Post-commit hook: auto-push to origin
- GitHub Actions CI: Linux/Mac/Windows, Python 3.9 + 3.12

## Requirements

- Python 3.6+ (no pip install needed for the tool itself)
- Gemini CLI: `npm install -g @google/gemini-cli`
- Works on Mac, Linux, and Windows
