# multi-llm

Pool multiple free-tier API keys for seamless terminal chat. When one key hits its rate limit, automatically switches to the next.

Supports **Gemini** and **Groq** keys. Add as many as you want — more keys = more free requests.

## Quick Start

```bash
git clone <this-repo>
cd multi-llm
./multi-llm
```

First run walks you through setup:
1. Choose a passphrase (encrypts your keys locally)
2. Add your API keys
3. Start chatting

## Get Free API Keys

| Provider | Free Tier | Get Key |
|----------|-----------|---------|
| Gemini | 15 RPM, 1M TPM | https://aistudio.google.com/apikey |
| Groq | 30 RPM, 15K TPD | https://console.groq.com/keys |

You can create multiple keys with different Google/Groq accounts.

## Commands

```
multi-llm              Start chatting
multi-llm --add        Add more keys
multi-llm --status     Show which keys are available
multi-llm --reset      Clear all rate-limit cooldowns
multi-llm --help       Help
```

Inside chat:
- `/status` — show key availability
- `quit` or Ctrl+C — exit

## How It Works

- Keys are tried in order: all Gemini keys first, then Groq
- When a key gets rate-limited (HTTP 429), it's put on a 1-hour cooldown
- The next available key picks up seamlessly — your conversation continues
- Keys are encrypted with your passphrase (PBKDF2 + XOR) and stored in `~/.multi-llm/config.json`

## Requirements

- Python 3.6+ (no pip packages needed)
- Internet connection

## Security

- Keys are encrypted at rest with your passphrase
- Config file is chmod 600 (owner-only read/write)
- Keys are never logged or printed
- Passphrase is verified on each launch
