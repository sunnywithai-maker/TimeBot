# main.py
import os
import google.generativeai as genai
from twilio.rest import Client
from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# --- Load Environment Variables ---
# This code will run once when the container starts.
# It will crash with a clear error if a variable is missing.
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    TWILIO_SID = os.environ["TWILIO_SID"]
    TWILIO_TOKEN = os.environ["TWILIO_TOKEN"]
    WHATSAPP_FROM = os.environ["WHATSAPP_FROM"]
    WHATSAPP_TO = os.environ["WHATSAPP_TO"]
    print("SUCCESS: All environment variables loaded.")
except KeyError as e:
    # This provides a clear error in the logs if a variable is missing.
    raise RuntimeError(f"FATAL ERROR: Environment variable {e} not set.") from e

# --- The Prompt for withAI Brain ---
BRAIN_PROMPT = """
You are withAI Brain. Generate the "Top 1" unique AI product idea for today.
Your response MUST strictly follow the established output format, starting with "💡 **Idea Title:**".
The tone must be visionary and strategic, as if pitching to top CEOs.
The idea must be absolutely unique and pass your internal novelty review.
Do not include any text before the "💡 **Idea Title:**" line.
"""

# --- The Main Web Endpoint ---
@app.route("/")
def run_daily_idea_automation():
    """
    This is the main function triggered by Cloud Scheduler.
    It runs the entire process of getting an idea and sending it.
    """
    print("INFO: Automation process started by HTTP request.")
    
    # 1. Call the AI Brain
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(BRAIN_PROMPT)
        idea_text = response.text
        print("INFO: Idea generated successfully from AI.")
    except Exception as e:
        error_message = f"ERROR: Failed to call Google AI API: {e}"
        print(error_message)
        return error_message, 500

    # 2. Send the message via Twilio
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        if len(idea_text) > 1500:
            idea_text = idea_text[:1500] + "\n\n[Message truncated]"
        
        message = client.messages.create(
            from_=WHATSAPP_FROM,
            body=idea_text,
            to=WHATSAPP_TO
        )
        success_message = f"SUCCESS: Automation complete. Message sent with SID: {message.sid}"
        print(success_message)
        return success_message, 200
    except Exception as e:
        error_message = f"ERROR: Failed to send WhatsApp message via Twilio: {e}"
        print(error_message)
        return error_message, 500