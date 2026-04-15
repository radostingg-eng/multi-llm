# multi-llm

Rotate multiple free API keys and launch the **real Gemini CLI** (or Groq CLI). When one key runs out, exit and re-run — it picks the next available key.

No custom chat interface. Just a thin launcher that swaps keys.

## Quick Start

```bash
git clone https://github.com/radostingg-eng/multi-llm.git
cd multi-llm
bash setup.sh       # installs git hooks + test deps
./multi-llm         # first run: add your keys, then launches Gemini CLI
```

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

**Tip:** Use multiple Google/Groq accounts to multiply your free usage.

## Usage

```
multi-llm                  Launch CLI with next available key
multi-llm --status         Show which keys are ready
multi-llm --add            Add more keys
multi-llm --update         Pull latest version from GitHub
multi-llm --reset          Clear all rate-limit cooldowns
multi-llm --help           Help
```

Any other flags pass straight to the Gemini CLI:
```
multi-llm -p "explain this code"
multi-llm --model gemini-2.5-pro
```

## How It Works

1. Launches the real `gemini` CLI with the first available API key
2. You use Gemini CLI normally (full interactive, tools, file editing, everything)
3. When you hit a rate limit, exit Gemini CLI
4. Re-run `multi-llm` — it asks if the last key was rate-limited, marks it, and tries the next
5. Rate-limited keys cool down for 1 hour, then become available again
6. If all Gemini keys are exhausted, falls back to Groq CLI

## Updating

When the person who shared this pushes changes:
```
multi-llm --update
```

## For Developers

```bash
bash setup.sh                     # installs hooks + pytest
python3 -m pytest tests/ -v      # run tests
```

**Quality gates:**
- Pre-commit hook: syntax check + tests + blocks config.json
- Post-commit hook: auto-push to origin
- GitHub Actions CI: Linux/Mac/Windows, Python 3.9 + 3.12

## Requirements

- Python 3.6+
- Gemini CLI installed (`npm install -g @google/gemini-cli`)
- Internet connection
