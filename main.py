# main.py (Final Version using Vertex AI)
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from twilio.rest import Client
from flask import Flask

app = Flask(__name__)

# --- Project Configuration ---
# These are now public details, not secrets.
PROJECT_ID = "timebot-477600"
LOCATION = "europe-west1" # Your Cloud Run region

# --- Load Secrets ---
# We no longer need a Gemini/AI API key.
try:
    TWILIO_SID = os.environ["TWILIO_SID"]
    TWILIO_TOKEN = os.environ["TWILIO_TOKEN"]
    WHATSAPP_FROM = os.environ["WHATSAPP_FROM"]
    WHATSAPP_TO = os.environ["WHATSAPP_TO"]
    print("SUCCESS: All environment variables loaded.")
except KeyError as e:
    raise RuntimeError(f"FATAL ERROR: Environment variable {e} not set.") from e

# --- Initialize Vertex AI ---
# This happens once when the container starts.
vertexai.init(project=PROJECT_ID, location=LOCATION)

# --- The Prompt for withAI Brain ---
BRAIN_PROMPT = """
You are withAI Brain. Generate the "Top 1" unique AI product idea for today.
Your response MUST strictly follow the established output format, starting with "💡 **Idea Title:**".
The tone must be visionary and strategic, as if pitching to top CEOs.
The idea must be absolutely unique and pass your internal novelty review.
Do not include any text before the "💡 **Idea Title:**" line.
"""

@app.route("/")
def run_daily_idea_automation():
    """Main function triggered by Cloud Scheduler."""
    print("INFO: Automation process started by HTTP request.")
    
    # 1. Call the Vertex AI Brain
    try:
        # Load the Gemini 1.0 Pro model from Vertex AI
        model = GenerativeModel("gemini-1.0-pro")
        response = model.generate_content(BRAIN_PROMPT)
        idea_text = response.text
        print("INFO: Idea generated successfully from Vertex AI.")
    except Exception as e:
        error_message = f"ERROR: Failed to call Vertex AI API: {e}"
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
