# app.py
import streamlit as st
from pathlib import Path
from datetime import datetime
import time
from TTS.api import TTS
from utils.text_splitter import split_text_to_chunks
from pydub import AudioSegment

OUTPUT_DIR = Path("audio_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="TTS Project", layout="wide")
st.title("🎤 Text → Speech — Long Form Generator (Coqui TTS)")

st.markdown("""
📌 **Instructions:**
- Paste text or upload `.txt` file  
- Select **Voice & Output settings**  
- Click **Generate** to create full-length audio
""")

uploaded_file = st.file_uploader("Upload .txt file (optional)", type=["txt"])
text_input = st.text_area("Paste your text here", height=300)

if uploaded_file:
    try:
        text_input = uploaded_file.read().decode("utf-8")
    except:
        st.error("File must be UTF-8 format.")

chunk_size = st.number_input("Chunk size (chars)", 2000, 8000, 4000, 500)
voice_choice = st.selectbox("Voice", ["Male", "Female"])
output_format = st.selectbox("Output format", ["wav", "mp3"], 0)
sample_rate = st.selectbox("Sample rate", [22050, 24000, 44100], index=0)

generate = st.button("🚀 Generate Audio")

VOICE_MODELS = {
    "Male": "tts_models/en/vctk/vits",
    "Female": "tts_models/en/ljspeech/tacotron2-DDC"
}

@st.cache_resource(show_spinner=True)
def load_model(name: str):
    return TTS(name)

if generate:
    if not text_input.strip():
        st.error("⚠ Please provide some text first!")
    else:
        with st.spinner("🧠 Processing text & loading model..."):
            chunks = split_text_to_chunks(text_input, chunk_size)
            st.info(f"📚 Text split into **{len(chunks)} chunks**.")
            tts = load_model(VOICE_MODELS[voice_choice])

        base = datetime.now().strftime("%Y%m%d_%H%M%S")
        part_files = []
        progress = st.progress(0)

        for i, chunk in enumerate(chunks, 1):
            temp_file = OUTPUT_DIR / f"{base}_part{i}.wav"
            tts.tts_to_file(text=chunk, file_path=str(temp_file))
            part_files.append(str(temp_file))
            progress.progress(int(i / len(chunks) * 100))
            time.sleep(0.1)

        st.success("🔊 Audio Parts Generated — Merging...")
        combined = AudioSegment.empty()
        for f in part_files:
            combined += AudioSegment.from_file(f)

        final_file = OUTPUT_DIR / f"{base}_final.{output_format}"
        combined.export(final_file, format=output_format)

        st.success(f"🎉 Final Audio Ready → `{final_file.name}`")
        st.audio(str(final_file))

        with open(final_file, "rb") as fh:
            st.download_button("⬇ Download", fh, file_name=final_file.name, mime=f"audio/{output_format}")

        st.info("⚡ Completed Successfully!")
