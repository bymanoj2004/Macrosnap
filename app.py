#Import genai package
from google import genai
from google.genai import types
import streamlit as st
import asyncio
from telegram import Bot

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
TELEGRAM_BOT_TOKEN = st.secrets["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()

#step 1: onboarding (username and phone number)

if 'onboarded' not in st.session_state:
    st.title("🥗 MacroSnap")
    st.caption("Snap it. Track it. Text yourself the results.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        telegram_number = st.text_input(
            "Telegram number (with country code)",
            placeholder="+91XXXXXXXXXX",
        )

        submitted = st.form_submit_button("Let's go 🚀")
    
    if submitted:
        if not name.strip() or not telegram_number.strip():
            st.warning("Please fill in both your name and Telegram number.")
        else:
            st.session_state.name = name.strip()
            st.session_state.telegram_number = telegram_number.strip()

            st.session_state.chat = gemini_client.chats.create(
                model = "gemini-2.5-flash",
                config = types.GenerateContentConfig(system_instruction = SYSTEM_PROMPT)
            )

            st.session_state.messages = []
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

# Building the chat interface
def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])

def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)


# Handling input (text and photos)
def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"

user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file = True,
    file_type = ["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)

    elif photo is not None:
        parts.append("What is this meal? Give me the calories and macros.")

    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)
    add_message("assistant", "text", answer)



def send_telegram(chat_id, user_name, summary):
    try:
        text = clean_telegram_text(summary)

        message_text = (
            f"🥗 MacroSnap Nutrition Summary\n\n"
            f"Hi {user_name}!\n\n"
            f"{text}"
        )

        bot = Bot(token=TELEGRAM_BOT_TOKEN)

        asyncio.run(
            bot.send_message(
                chat_id=chat_id,
                text=message_text,
            )
        )

        return True, "Message sent successfully."

    except Exception as error:
        return False, str(error)

def clean_telegram_text(text):
    if not text:
        return "No nutrition summary available."

    text = " ".join(text.split())

    return text[:4000] + "..." if len(text) > 4000 else text

header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)

with header_col:
    st.title("🥗 MacroSnap")

with button_col:
    send_disabled = len(st.session_state.messages) <= 2

    if st.button(
        "📤 Send to Telegram",
        disabled=send_disabled,
        use_container_width=True
    ):
        with st.spinner("Summarizing your day..."):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

        success, info = send_telegram(
            TELEGRAM_CHAT_ID,
            st.session_state.name,
            summary
        )

        if success:
            st.success("Sent! Check your Telegram 📲")
        else:
            st.error(f"Couldn't send that: {info}")