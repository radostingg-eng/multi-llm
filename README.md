# multi-llm

Pool multiple free-tier API keys for seamless terminal chat. When one key hits its rate limit, automatically switches to the next.

Supports **Gemini** and **Groq** keys. Add as many as you want — more keys = more free requests.

## Quick Start

```bash
git clone https://github.com/radostingg-eng/multi-llm.git
cd multi-llm
bash setup.sh      # installs git hooks + test deps
./multi-llm        # first run walks you through adding keys
```

## Getting Your Free API Keys

You need at least one key. Both are free:

### Gemini (Google)
1. Go to https://aistudio.google.com/apikey
2. Click **Create API Key**
3. Copy it — looks like `AIzaSy...`

### Groq
1. Go to https://console.groq.com/keys
2. Sign up or log in
3. Click **Create API Key**
4. Copy it — looks like `gsk_...`

**Tip:** Make keys with multiple Google/Groq accounts to multiply your free usage.

## Commands

```
./multi-llm              Start chatting
./multi-llm --add        Add more keys
./multi-llm --status     Show which keys are available
./multi-llm --reset      Clear all rate-limit cooldowns
./multi-llm --help       Help
```

Inside chat:
- `/status` — show key availability
- `/help` — show commands
- `quit` or Ctrl+C — exit

## How It Works

- Keys are tried in order: Gemini keys first, then Groq as fallback
- When a key gets rate-limited (HTTP 429), it goes on a 1-hour cooldown
- The next available key picks up seamlessly — your conversation continues
- Keys are encrypted with your passphrase and stored in `~/.multi-llm/config.json`

## For Developers

```bash
bash setup.sh                          # one-time: installs hooks + pytest
python3 -m pytest tests/ -v           # run all 29 tests
```

**Quality gates (same as sovereign-engine):**
- **Pre-commit hook**: blocks config.json from commits, runs syntax check + full test suite
- **Post-commit hook**: auto-pushes to origin
- **GitHub Actions CI**: tests on Linux/Mac/Windows with Python 3.9 + 3.12

## Requirements

- Python 3.6+ (no pip install needed for the tool itself)
- Internet connection

## Security

- Keys are encrypted at rest (PBKDF2 key derivation + XOR cipher)
- Config file is chmod 600 (owner-only read/write on Mac/Linux)
- Keys are never logged or printed
- Passphrase is verified on each launch
