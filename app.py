import os
os.environ["PATH"] += os.pathsep + os.getcwd()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

import streamlit as st
import whisper
from datetime import datetime
from groq import Groq

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Meeting Minutes",
    page_icon="🧠",
    layout="wide"
)


st.markdown("""
<style>
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.subtitle {
    color: #888;
    margin-bottom: 2rem;
}
.block {
    padding: 1.2rem;
    border-radius: 12px;
    background-color: #111;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧠 Meeting Minutes Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload audio/video or paste transcript → get structured minutes</div>', unsafe_allow_html=True)

 
model = whisper.load_model("base")
mode = st.radio(
    "Choose Input Method",
    ["🎤 Upload Audio / Video", "📄 Paste Transcript"],
    horizontal=True
)

transcript = ""

# ---------------- AUDIO / VIDEO ----------------
if mode == "🎤 Upload Audio / Video":
    uploaded_file = st.file_uploader(
        "Upload file",
        type=["mp3", "wav", "m4a", "mp4"]
    )

    if uploaded_file is not None:
        file_ext = uploaded_file.name.split(".")[-1]
        temp_file = f"temp_input.{file_ext}"

        with open(temp_file, "wb") as f:
            f.write(uploaded_file.read())

        st.info("🔄 Transcribing...")

        try:
            result = model.transcribe(temp_file)
            transcript = result["text"]

            with st.expander("📄 View Transcript"):
                st.write(transcript)

        except Exception as e:
            st.error(f"Transcription Error: {e}")

# ---------------- PASTE TRANSCRIPT ----------------
elif mode == "📄 Paste Transcript":
    transcript = st.text_area(
        "Paste your transcript here",
        height=250,
        placeholder="Paste meeting conversation..."
    )

# ---------------- AI FUNCTION ----------------
def generate_minutes(transcript):
    try:
        prompt = f"""
You are an AI assistant.

From the transcript, generate:

1. A short meeting title (max 6 words)
2. Summary
3. Key Points
4. Decisions
5. Action Items (Task | Owner | Deadline)

Return clean formatted output.

Transcript:
{transcript}
"""

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# ---------------- GENERATE BUTTON ----------------
if st.button("🚀 Generate Minutes") and transcript:

    with st.spinner("Thinking..."):
        output = generate_minutes(transcript)

    today = datetime.now().strftime("%d %B %Y")

    # Extract title
    if "title" in output.lower():
        meeting_title = output.split("\n")[0].replace("TITLE:", "").strip()
    else:
        meeting_title = "Meeting Summary"

    # ---------------- DISPLAY ----------------
    col1, col2 = st.columns([1,2])

    with col1:
        st.markdown("### 📌 Meeting Info")
        st.write(f"**Title:** {meeting_title}")
        st.write(f"**Date:** {today}")

    with col2:
        st.markdown("### 📋 Generated Minutes")
        st.markdown(output)

    st.divider()

    # ---------------- DOWNLOAD ----------------
    st.download_button(
        "📥 Download",
        output,
        file_name="meeting_minutes.txt"
    )