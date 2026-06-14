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
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0d0e12 !important;
    color: #e8e6e0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stAppViewContainer"] > .main { background: #0d0e12 !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 2.5rem 4rem 4rem !important; max-width: 980px !important; margin: auto; }

.hero { padding: 3rem 0 2rem; border-bottom: 1px solid #1e1f28; margin-bottom: 2.5rem; }
.hero-eyebrow { font-family: 'DM Mono', monospace; font-size: 0.68rem; letter-spacing: 0.22em; color: #c8a96e; text-transform: uppercase; margin-bottom: 0.75rem; }
.hero-title { font-family: 'DM Serif Display', serif; font-size: 3.8rem; line-height: 1.05; color: #f0ece4; margin: 0 0 0.5rem; }
.hero-title em { font-style: italic; color: #c8a96e; }
.hero-sub { font-size: 0.95rem; color: #666; font-weight: 300; margin-top: 0.75rem; max-width: 520px; }

.section-label { font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase; color: #555; margin-bottom: 0.5rem; }

/* Radio */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div { display: flex; gap: 0.6rem; flex-wrap: wrap; }
div[data-testid="stRadio"] > div > label {
    background: #13141a !important; border: 1px solid #2a2b33 !important;
    border-radius: 8px !important; padding: 0.55rem 1.1rem !important;
    cursor: pointer !important; font-size: 0.83rem !important; color: #999 !important;
    transition: all 0.2s !important;
}
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: #1e1f28 !important; border-color: #c8a96e !important; color: #c8a96e !important;
}

/* File uploader */
[data-testid="stFileUploader"] { background: #13141a; border: 1.5px dashed #2a2b33; border-radius: 10px; padding: 1rem; }
[data-testid="stFileUploader"]:hover { border-color: #c8a96e55; }
[data-testid="stFileUploaderDropzoneInstructions"] { color: #555 !important; }

/* Textarea */
textarea { background: #13141a !important; border: 1px solid #2a2b33 !important; border-radius: 8px !important; color: #e0ddd6 !important; font-family: 'DM Mono', monospace !important; font-size: 0.82rem !important; }
textarea:focus { border-color: #c8a96e !important; box-shadow: none !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div { background: #13141a !important; border: 1px solid #2a2b33 !important; border-radius: 8px !important; color: #e0ddd6 !important; }

/* Primary button */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #c8a96e, #a88848) !important;
    color: #0d0e12 !important; border: none !important; border-radius: 8px !important;
    font-weight: 700 !important; font-size: 0.92rem !important; padding: 0.65rem 2rem !important;
    letter-spacing: 0.04em !important; width: 100% !important; height: 3.2em !important;
    transition: opacity 0.2s !important;
}
div[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: #13141a !important; color: #c8a96e !important;
    border: 1px solid #c8a96e44 !important; border-radius: 8px !important;
    width: 100% !important; font-size: 0.85rem !important; padding: 0.65rem !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover { background: #1e1f28 !important; border-color: #c8a96e !important; }

/* Alerts */
[data-testid="stAlert"] { background: #13141a !important; border-radius: 8px !important; border-left: 3px solid #c8a96e !important; color: #aaa !important; font-size: 0.84rem !important; }

/* Expander */
[data-testid="stExpander"] { background: #13141a !important; border: 1px solid #1e1f28 !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary { color: #777 !important; font-size: 0.83rem !important; }

/* Output card */
.output-card { background: #13141a; border: 1px solid #222; border-radius: 14px; padding: 2.4rem 2.6rem; margin-top: 1.8rem; }
.output-card h2 { font-family: 'DM Serif Display', serif; color: #f0ece4; font-size: 1.5rem; margin-top: 0; }
.output-card h3 { font-family: 'DM Sans', sans-serif; font-weight: 600; color: #c8a96e; font-size: 0.9rem; letter-spacing: 0.05em; text-transform: uppercase; margin-top: 1.8rem; margin-bottom: 0.6rem; }
.output-card p, .output-card li { color: #b8b5ae; font-size: 0.91rem; line-height: 1.75; }
.output-card ul { padding-left: 1.4rem; }
.output-card li { margin-bottom: 0.35rem; }
.output-card table { width: 100%; border-collapse: collapse; margin-top: 0.5rem; font-size: 0.87rem; }
.output-card th { background: #1a1b22; color: #c8a96e; font-family: 'DM Mono', monospace; font-size: 0.65rem; letter-spacing: 0.12em; text-transform: uppercase; padding: 0.6rem 0.9rem; text-align: left; border: 1px solid #222; }
.output-card td { color: #b0ada6; padding: 0.55rem 0.9rem; border: 1px solid #1e1f28; vertical-align: top; }
.output-card tr:nth-child(even) td { background: #111217; }
.output-card hr { border-color: #1e1f28; margin: 1.6rem 0; }
.output-badge-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 1.6rem; padding-bottom: 1rem; border-bottom: 1px solid #1e1f28; }
.badge { font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.14em; text-transform: uppercase; border-radius: 4px; padding: 0.22rem 0.55rem; }
.badge-gold { background: #c8a96e18; color: #c8a96e; border: 1px solid #c8a96e33; }
.badge-gray { background: #1e1f28; color: #555; border: 1px solid #2a2b33; }

[data-testid="stSpinner"] p { color: #777 !important; font-size: 0.84rem !important; }
hr { border-color: #1e1f28 !important; }
.footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid #1a1b22; text-align: center; font-family: 'DM Mono', monospace; font-size: 0.62rem; letter-spacing: 0.14em; text-transform: uppercase; color: #2e2f38; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d0e12; }
::-webkit-scrollbar-thumb { background: #2a2b33; border-radius: 4px; }
label, [data-testid="stWidgetLabel"] p { color: #666 !important; font-size: 0.75rem !important; font-family: 'DM Mono', monospace !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ AI-Powered Document Intelligence</div>
    <div class="hero-title">Minutes <em>AI</em></div>
    <div class="hero-sub">Turn any meeting recording or transcript into polished, structured minutes — instantly.</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# WHISPER MODEL
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading Whisper model…")
def load_whisper_model():
    return whisper.load_model("base")

whisper_model = load_whisper_model()

# ─────────────────────────────────────────────
# OPTION DEFINITIONS  (defined once, used everywhere)
# ─────────────────────────────────────────────
DETAIL_OPTIONS = ["Concise (exec summary)", "Standard (full minutes)", "Detailed (verbose notes)"]
FORMAT_OPTIONS = ["Formal / Corporate", "Startup / Casual", "Technical / Engineering"]

DETAIL_PROMPTS = {
    "Concise (exec summary)":     "Be very concise. Max 3 bullet points per section. Only the most critical information. Skip minor details.",
    "Standard (full minutes)":    "Be thorough and readable. Cover all main points with clear bullets. Balance detail with brevity.",
    "Detailed (verbose notes)":   "Be exhaustive. Capture every discussion point, disagreement, nuance, and context. Include who said what where possible.",
}

FORMAT_PROMPTS = {
    "Formal / Corporate":         "Use formal, polished language suitable for board members, executives, or official records. No slang.",
    "Startup / Casual":           "Keep it clear, direct and human. Professional but not stiff. Avoid corporate jargon.",
    "Technical / Engineering":    "Be precise with technical details. Include system names, version numbers, stack references, and engineering terminology where present.",
}

# ─────────────────────────────────────────────
# INPUT MODE
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Input Method</div>', unsafe_allow_html=True)
mode = st.radio(
    "Input Method",
    ["🎙️ Upload Audio / Video", "📋 Paste Transcript"],
    horizontal=True,
    label_visibility="collapsed"
)

transcript = ""

# ─────────────────────────────────────────────
# AUDIO INPUT
# ─────────────────────────────────────────────
if mode == "🎙️ Upload Audio / Video":

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

    LANG_MAP = {
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

        st.info(f"🔄 Transcribing **{uploaded_file.name}** and translating to English…")

        try:
            whisper_kwargs = {"task": "translate"}   # always output English
            selected_lang = LANG_MAP.get(language)
            if selected_lang:
                whisper_kwargs["language"] = selected_lang  # tells Whisper what input lang is

            result = whisper_model.transcribe(tmp_path, **whisper_kwargs)
            transcript = result["text"].strip()
            detected = result.get("language", "unknown")

            st.success(f"✅ Done — detected **{detected}** → translated to **English**")

            with st.expander("📄 View raw transcript"):
                st.write(transcript)

        except Exception as e:
            st.error(f"❌ Transcription failed: {e}")
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

# ─────────────────────────────────────────────
# TEXT INPUT
# ─────────────────────────────────────────────
elif mode == "📋 Paste Transcript":
    st.markdown('<div class="section-label">Transcript</div>', unsafe_allow_html=True)
    transcript = st.text_area(
        "Transcript",
        placeholder="Paste the meeting transcript here…\n\nE.g.\nAlice: Let's start with the Q3 review...\nBob: Revenue is up 12% quarter-on-quarter...",
        height=280,
        label_visibility="collapsed"
    )

# ─────────────────────────────────────────────
# OUTPUT OPTIONS
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Output Options</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    detail_level = st.selectbox("Detail Level", DETAIL_OPTIONS, index=1)
with col2:
    output_format = st.selectbox("Tone & Format", FORMAT_OPTIONS, index=0)

# ─────────────────────────────────────────────
# GENERATE FUNCTION
# ─────────────────────────────────────────────
def generate_minutes(text: str, detail: str, fmt: str) -> str:
    detail_instruction = DETAIL_PROMPTS.get(detail, DETAIL_PROMPTS["Standard (full minutes)"])
    format_instruction = FORMAT_PROMPTS.get(fmt, FORMAT_PROMPTS["Formal / Corporate"])

    prompt = f"""You are a professional meeting secretary. Your job is to generate structured, accurate meeting minutes from the transcript provided.

TONE: {format_instruction}
DETAIL LEVEL: {detail_instruction}

Generate the meeting minutes using EXACTLY this markdown structure. Do not skip any section. Fill every section based on what is in the transcript.

## Meeting Title
[Infer a concise, specific title from the content — e.g. "Q3 Product Roadmap Review" or "Sprint 14 Planning"]

## Overview
| Field | Details |
|-------|---------|
| Date | [Date if mentioned, else "Not specified"] |
| Attendees | [Names/roles if mentioned, else "Not specified"] |
| Duration | [Duration if mentioned, else "Not specified"] |
| Facilitator | [Name if mentioned, else "Not specified"] |

## Executive Summary
[Write {2 if 'Concise' in detail else 4} clear sentences summarising what was discussed, decided, and what happens next. This should stand alone as a quick read for someone who wasn't in the meeting.]

## Key Discussion Points
[Bullet list — each point is a distinct topic raised. Start each bullet with a bold topic label, e.g. **Budget Review** — then explain what was discussed.]

## Decisions Made
[Bullet list of every concrete decision or agreement reached. If none, write: No formal decisions recorded.]

## Action Items
| # | Task | Owner | Deadline |
|---|------|-------|----------|
[Fill each row. If no action items, write a single row: | — | No action items recorded | — | — |]

## Risks & Blockers
[Bullet list of any risks, blockers, dependencies, or concerns raised. If none, write: None identified.]

## Next Steps / Conclusion
[1–3 sentences on what happens after this meeting — next meeting, follow-ups, key deadlines.]

---
*Generated by Minutes AI*

TRANSCRIPT:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are an expert meeting secretary. Always follow the exact output format requested. Never skip sections. Never add extra commentary outside the format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.15,
        max_tokens=2500,
    )

    return response.choices[0].message.content

# ─────────────────────────────────────────────
# GENERATE BUTTON
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)

if st.button("✦ Generate Meeting Minutes"):
    if not transcript.strip():
        st.warning("⚠️ Please upload an audio file or paste a transcript first.")
    elif len(transcript.strip()) < 40:
        st.warning("⚠️ The transcript is too short. Please provide more content.")
    else:
        with st.spinner("Drafting your minutes…"):
            try:
                output = generate_minutes(transcript, detail_level, output_format)

                # Badge row
                st.markdown(f"""
                <div class="output-card">
                    <div class="output-badge-row">
                        <span class="badge badge-gold">Generated Minutes</span>
                        <span class="badge badge-gray">{detail_level}</span>
                        <span class="badge badge-gray">{output_format}</span>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(output)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    st.download_button(
                        label="📥 Download as .txt",
                        data=output,
                        file_name="meeting_minutes.txt",
                        mime="text/plain"
                    )
                with col_dl2:
                    st.download_button(
                        label="📄 Download as .md",
                        data=output,
                        file_name="meeting_minutes.md",
                        mime="text/markdown"
                    )

            except Exception as e:
                st.error(f"❌ Failed to generate minutes: {e}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Minutes AI &nbsp;·&nbsp; Whisper + Groq LLaMA 3.3 70B + Streamlit &nbsp;·&nbsp; Built for clarity
</div>
""", unsafe_allow_html=True)
