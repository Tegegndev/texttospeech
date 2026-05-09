# Text-to-Speech Telegram Bot

This project provides a Telegram bot that converts user text messages into speech audio files.

## Features
- Receives text messages from Telegram users
- Detects input language automatically
- Converts text to speech using an external API
- Returns generated audio back to users
- Supports webhook-based deployment with Flask

## Project Structure
- `/home/runner/work/texttospeech/texttospeech/__init__.py` — main bot and Flask webhook app
- `/home/runner/work/texttospeech/texttospeech/config.py` — configuration values
- `/home/runner/work/texttospeech/texttospeech/requirements.txt` — Python dependencies
- `/home/runner/work/texttospeech/texttospeech/voices/` — temporary generated audio output
- `/home/runner/work/texttospeech/texttospeech/user_data.json` — stored user metadata

## Requirements
- Python 3.10+
- A Telegram Bot Token
- A Detect Language API key
- Access to the configured text-to-speech API endpoint

## Setup
1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your configuration values in `config.py` (or migrate these values to environment variables).

## Run
```bash
python __init__.py
```

The Flask app starts on port `5000` by default and exposes:
- `/` — health/home response
- `/webhook` — Telegram update webhook endpoint
- `/set_webhook` — helper route to set Telegram webhook URL

## Notes
- Keep secrets out of source control.
- Ensure the `voices` directory is writable by the runtime user.
- Generated audio files are removed after being sent.
