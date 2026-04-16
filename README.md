# multi-llm

Smart launcher for the Gemini CLI. Rotates free API keys automatically and uses Groq to make them last longer.

## Installation

### 1. Install Gemini CLI (requires Node.js)

```bash
npm install -g @google/gemini-cli
```

### 2. Get your free API keys

**Gemini (Google)** — https://aistudio.google.com/apikey
1. Click **Create API Key**
2. Copy it (starts with `AIza...`)
3. Make more keys with other Google accounts for extra quota

**Groq** — https://console.groq.com/keys
1. Sign up / log in
2. Click **Create API Key**
3. Copy it (starts with `gsk_...`)

### 3. Clone and set up

```bash
git clone https://github.com/radostingg-eng/multi-llm.git
cd multi-llm
bash setup.sh
```

### 4. Run it

```bash
./multi-llm
```

First run auto-detects any `GEMINI_API_KEY*` and `GROQ_API_KEY*` environment variables. If none found, it asks you to paste keys one by one — each key is validated immediately.

### 5. (Optional) Add shortcut

```bash
# Mac (Homebrew)
ln -sf ~/multi-llm/multi-llm /opt/homebrew/bin/ml

# Mac/Linux
ln -sf ~/multi-llm/multi-llm /usr/local/bin/ml
```

Now just type `ml` from anywhere.

## Daily Use

```
ml                          Launch Gemini CLI
ml "quick question"         Groq answers instantly (no Gemini quota used)
ml "refactor the auth"      Groq enhances prompt, then launches Gemini CLI
ml --status                 Show which keys are ready
ml --add                    Add more keys
ml --update                 Pull latest version
ml --version                Check version
ml --reset                  Clear all cooldowns
ml --no-enhance             Skip prompt enhancement
```

Gemini CLI flags pass through:
```
ml -p "explain this code"
ml --model gemini-2.5-pro
```

Inside Gemini CLI, use `/exit` or `Ctrl+C` to quit.

## What It Does

| You type | What happens |
|---|---|
| `ml` | Launches Gemini CLI with next available key |
| `ml "what is a mutex"` | Groq answers instantly — no Gemini quota burned |
| `ml "refactor the auth module"` | Groq enhances your prompt, then launches Gemini |
| All Gemini keys exhausted | Drops into Groq quick-chat (text only, shows countdown) |
| Exit Gemini CLI | Groq summarizes session, loads it as context next time |

## Smart Features (powered by Groq)

1. **Smart routing** — Simple questions go to Groq instantly. Complex tasks go to Gemini CLI. Saves your Gemini quota for real work.
2. **Prompt enhancer** — Groq rewrites your prompt before Gemini sees it. Better prompts = better results = fewer follow-ups.
3. **Quick-chat fallback** — When all Gemini keys are on cooldown, you get Groq chat instead of a dead end. Clearly labeled as text-only.
4. **Session memory** — After each Gemini session, Groq summarizes what you did. Next launch feeds it back as context.

## Updating

```
ml --update
```

Pulls the latest code from GitHub and re-installs hooks.

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

- Python 3.6+
- Node.js (for Gemini CLI)
- Works on Mac, Linux, and Windows
