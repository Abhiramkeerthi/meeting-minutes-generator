import os
import tempfile
import streamlit as st
import whisper
from groq import Groq
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# ENV + CLIENTS
# ─────────────────────────────────────────────
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Minutes AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CUSTOM CSS  — dark editorial aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0d0e12 !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: #0d0e12 !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 2.5rem 4rem 4rem !important; max-width: 960px !important; margin: auto; }

/* ── Hero ── */
.hero {
    padding: 3rem 0 2rem;
    border-bottom: 1px solid #222;
    margin-bottom: 2.5rem;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: #c8a96e;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.8rem;
    line-height: 1.05;
    color: #f0ece4;
    margin: 0 0 0.5rem;
}
.hero-title em {
    font-style: italic;
    color: #c8a96e;
}
.hero-sub {
    font-size: 1rem;
    color: #888;
    font-weight: 300;
    margin-top: 0.75rem;
    max-width: 520px;
}

/* ── Section labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.6rem;
}

/* ── Cards ── */
.card {
    background: #13141a;
    border: 1px solid #222;
    border-radius: 12px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}

/* ── Radio buttons ── */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
}
div[data-testid="stRadio"] > div > label {
    background: #13141a !important;
    border: 1px solid #2a2b33 !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.2rem !important;
    cursor: pointer !important;
    font-size: 0.85rem !important;
    color: #aaa !important;
    transition: all 0.2s !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: #1e1f28 !important;
    border-color: #c8a96e !important;
    color: #c8a96e !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #13141a;
    border: 1.5px dashed #2a2b33;
    border-radius: 10px;
    padding: 1rem;
}
[data-testid="stFileUploader"]:hover { border-color: #c8a96e44; }
[data-testid="stFileUploaderDropzoneInstructions"] { color: #666 !important; }

/* ── Textarea ── */
textarea {
    background: #13141a !important;
    border: 1px solid #2a2b33 !important;
    border-radius: 8px !important;
    color: #e0ddd6 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    resize: vertical !important;
}
textarea:focus { border-color: #c8a96e !important; box-shadow: none !important; }

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
    background: #13141a !important;
    border: 1px solid #2a2b33 !important;
    border-radius: 8px !important;
    color: #e0ddd6 !important;
}

/* ── Primary button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #c8a96e, #a88848) !important;
    color: #0d0e12 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 2rem !important;
    letter-spacing: 0.03em !important;
    transition: opacity 0.2s !important;
    width: 100% !important;
    height: 3.2em !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.88 !important; }

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: #13141a !important;
    color: #c8a96e !important;
    border: 1px solid #c8a96e55 !important;
    border-radius: 8px !important;
    width: 100% !important;
    font-size: 0.85rem !important;
    padding: 0.6rem !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #1e1f28 !important;
    border-color: #c8a96e !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #13141a !important;
    border-radius: 8px !important;
    border-left: 3px solid #c8a96e !important;
    color: #bbb !important;
    font-size: 0.85rem !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #13141a !important;
    border: 1px solid #222 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary { color: #888 !important; font-size: 0.85rem !important; }

/* ── Output card ── */
.output-wrapper {
    background: #13141a;
    border: 1px solid #222;
    border-radius: 12px;
    padding: 2.2rem 2.4rem;
    margin-top: 1.5rem;
    line-height: 1.75;
}
.output-wrapper h1, .output-wrapper h2 {
    font-family: 'DM Serif Display', serif;
    color: #f0ece4;
}
.output-wrapper h3, .output-wrapper h4 {
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    color: #c8a96e;
    margin-top: 1.4rem;
    letter-spacing: 0.02em;
}
.output-wrapper p, .output-wrapper li { color: #c0bdb6; font-size: 0.92rem; }
.output-wrapper ul { padding-left: 1.4rem; }
.output-wrapper li { margin-bottom: 0.3rem; }
.output-wrapper hr { border-color: #222; margin: 1.4rem 0; }
.output-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #222;
}
.output-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    background: #c8a96e22;
    color: #c8a96e;
    border: 1px solid #c8a96e44;
    border-radius: 4px;
    padding: 0.25rem 0.6rem;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p { color: #888 !important; font-size: 0.85rem !important; }

/* ── Divider ── */
hr { border-color: #1e1f28 !important; }

/* ── Footer ── */
.footer {
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid #1e1f28;
    text-align: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #333;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: #0d0e12; }
::-webkit-scrollbar-thumb { background: #2a2b33; border-radius: 4px; }

/* ── Labels ── */
label, [data-testid="stWidgetLabel"] p {
    color: #777 !important;
    font-size: 0.8rem !important;
    font-family: 'DM Mono', monospace !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ AI-Powered Document Intelligence</div>
    <div class="hero-title">Minutes <em>AI</em></div>
    <div class="hero-sub">
        Turn any meeting recording or transcript into polished, structured minutes — instantly.
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD WHISPER MODEL
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading Whisper model…")
def load_whisper_model():
    return whisper.load_model("base")

whisper_model = load_whisper_model()

# ─────────────────────────────────────────────
# INPUT MODE
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Input Method</div>', unsafe_allow_html=True)
mode = st.radio(
    "Input Method",
    ["🎙️  Upload Audio / Video", "📋  Paste Transcript"],
    horizontal=True,
    label_visibility="collapsed"
)

transcript = ""

# ─────────────────────────────────────────────
# AUDIO INPUT
# ─────────────────────────────────────────────
if mode == "🎙️  Upload Audio / Video":

    col_upload, col_lang = st.columns([3, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Drop your file here",
            type=["mp3", "wav", "m4a", "mp4", "ogg", "webm"],
            label_visibility="collapsed"
        )

    with col_lang:
        language = st.selectbox(
            "Audio Language",
            options=[
                "Auto-detect",
                "English", "Hindi", "Tamil", "Telugu", "Kannada",
                "Spanish", "French", "German", "Mandarin", "Arabic",
                "Portuguese", "Japanese", "Korean", "Italian", "Russian"
            ]
        )

    lang_map = {
        "Auto-detect": None, "English": "en", "Hindi": "hi",
        "Tamil": "ta", "Telugu": "te", "Kannada": "kn",
        "Spanish": "es", "French": "fr", "German": "de",
        "Mandarin": "zh", "Arabic": "ar", "Portuguese": "pt",
        "Japanese": "ja", "Korean": "ko", "Italian": "it", "Russian": "ru"
    }

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        st.info(f"🔄 Transcribing **{uploaded_file.name}** and translating to English — this may take a moment…")

        try:
            selected_lang = lang_map.get(language)

            # Always use task="translate" so Whisper outputs English
            # regardless of the source language (Tamil, Hindi, etc.)
            whisper_kwargs = {"task": "translate"}
            if selected_lang:
                whisper_kwargs["language"] = selected_lang  # hint to Whisper what the input lang is

            result = whisper_model.transcribe(tmp_path, **whisper_kwargs)
            transcript = result["text"].strip()
            detected = result.get("language", "unknown")

            st.success(f"✅ Done  ·  detected language: **{detected}**  →  translated to **English**")

            with st.expander("📄 View raw transcript (English)"):
                st.write(transcript)

        except Exception as e:
            st.error(f"❌ Transcription failed: {e}")
        finally:
            os.unlink(tmp_path)

# ─────────────────────────────────────────────
# TEXT INPUT
# ─────────────────────────────────────────────
elif mode == "📋  Paste Transcript":
    st.markdown('<div class="section-label">Transcript</div>', unsafe_allow_html=True)
    transcript = st.text_area(
        "Transcript",
        placeholder="Paste the meeting transcript here…\n\nE.g.\nAlice: Good morning everyone. Let's start with the Q3 review...",
        height=280,
        label_visibility="collapsed"
    )

# ─────────────────────────────────────────────
# SETTINGS ROW
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Output Options</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    detail_level = st.selectbox(
        "Detail Level",
        ["Concise  (exec summary)", "Standard  (full minutes)", "Detailed  (verbose notes)"]
    )
with col2:
    output_format = st.selectbox(
        "Format",
        ["Formal / Corporate", "Startup / Casual", "Technical / Engineering"]
    )

# ─────────────────────────────────────────────
# AI FUNCTION
# ─────────────────────────────────────────────
def generate_minutes(text: str, detail: str, fmt: str) -> str:

    detail_instructions = {
        "Concise  (exec summary)": "Be concise. Keep each section to 2–4 bullet points max. Focus on what matters most.",
        "Standard  (full minutes)": "Provide thorough but readable minutes. Use clear bullet points and avoid padding.",
        "Detailed  (verbose notes)": "Be exhaustive. Capture all discussion points, nuances, disagreements, and context."
    }

    format_instructions = {
        "Formal / Corporate": "Use formal, professional language suited for board-level or corporate stakeholders.",
        "Startup / Casual": "Keep the tone clear and direct — professional but not stiff. Skip jargon.",
        "Technical / Engineering": "Include technical specifics, system names, and engineering terminology. Be precise."
    }

    prompt = f"""You are an expert meeting secretary. Generate structured meeting minutes from the transcript below.

Tone: {format_instructions.get(fmt, '')}
Detail: {detail_instructions.get(detail, '')}

Output EXACTLY in this markdown structure (use ## for section headers):

## 📌 Meeting Title
[Infer a concise title from the content]

## 🗓️ Overview
| Field | Value |
|-------|-------|
| Date | [if mentioned, else "Not specified"] |
| Attendees | [list names if mentioned] |
| Duration | [if mentioned, else "Not specified"] |
| Facilitator | [if mentioned, else "Not specified"] |

## 📝 Summary
[2–4 sentence high-level summary of what the meeting was about and what was accomplished]

## 💬 Key Discussion Points
[Bullet list of main topics discussed]

## ✅ Decisions Made
[Bullet list of concrete decisions or conclusions reached — if none, write "No formal decisions recorded."]

## 📋 Action Items
[Table format:]
| # | Task | Owner | Deadline |
|---|------|-------|----------|
| 1 | ... | ... | ... |

If no action items, write: "No action items recorded."

## ⚠️ Risks / Blockers
[Any risks, blockers, or concerns raised. If none, write "None identified."]

## 🏁 Conclusion
[1–2 sentence wrap-up of next steps or closing remarks]

---
*Generated by Minutes AI*

Now process this transcript:

{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2048,
    )

    return response.choices[0].message.content

# ─────────────────────────────────────────────
# GENERATE BUTTON
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if st.button("✦ Generate Meeting Minutes"):

    if not transcript.strip():
        st.warning("⚠️ Please upload an audio file or paste a transcript first.")
    elif len(transcript.strip()) < 30:
        st.warning("⚠️ The transcript seems too short. Please provide more content.")
    else:
        with st.spinner("Drafting your minutes…"):
            try:
                output = generate_minutes(transcript, detail_level, output_format)

                st.markdown("""
                <div class="output-wrapper">
                    <div class="output-header">
                        <span class="output-badge">Generated Minutes</span>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(output)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download as .txt",
                    data=output,
                    file_name="meeting_minutes.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"❌ Failed to generate minutes: {e}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Minutes AI &nbsp;·&nbsp; Whisper + Groq + Streamlit &nbsp;·&nbsp; Built for clarity
</div>
""", unsafe_allow_html=True)
