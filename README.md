# MacroSnap

MacroSnap is a Streamlit app that helps users understand the nutrition of their meals by analyzing meal photos or text descriptions. It uses Google Gemini to estimate calories and macros, then lets users send a summary message through Telegram.

## Features

- Upload a meal photo or describe a dish in plain text
- Estimate calories and macronutrients (protein, carbs, fat)
- Keep a conversational nutrition chat for each user
- Collect a name and WhatsApp number during onboarding
- Send a summarized nutrition update to Telegram

## Tech Stack

- Python
- Streamlit
- Google GenAI SDK
- python-telegram-bot

## Project Structure

- `app.py` — main Streamlit application
- `prompts.py` — system and user prompts used by the AI assistant
- `requirements.txt` — Python dependencies
- `.streamlit/secrets.toml` — local secret configuration for API keys

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your secret keys in `.streamlit/secrets.toml`:

   ```toml
   GEMINI_API_KEY = "your_google_gemini_api_key"
   TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
   TELEGRAM_CHAT_ID = "your_telegram_chat_id"
   ```

   Note: this app reads secrets using Streamlit's `st.secrets` configuration.

## Run the App

```bash
streamlit run app.py
```

## How It Works

1. The user enters their name and WhatsApp number.
2. They upload a photo of a meal or type a food description.
3. Gemini analyzes the meal and estimates calories and macros.
4. The conversation is displayed in the app.
5. The user can send a combined meal summary to Telegram.

## Notes

- The app is intended for quick nutrition estimation and should be treated as approximate guidance.
- The generated nutrition info is based on AI estimation and may vary from actual values.
- Keep API keys secure and do not commit secrets to version control.
