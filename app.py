import streamlit as st
from google import genai
from google.genai import types
import tempfile
import os
import wave
import pydub

# ----------------------------------------------------------------------
# Core TTS logic (Gemini)
# ----------------------------------------------------------------------

def save_pcm_as_wav(pcm_data: bytes, wav_path: str, channels=1, rate=24000, sample_width=2):
    """Gemini TTS returns raw 16-bit PCM audio at 24kHz mono.
    Wrap it in a proper WAV container so it can be played/converted."""
    with wave.open(wav_path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def text_to_speech(api_key: str, text: str, model: str, voice: str) -> str:
    """
    Converts text to speech using Google's Gemini TTS models and saves
    the output as a WAV file. Returns the path to the audio file.
    """
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice
                    )
                )
            ),
        ),
    )

    pcm_data = response.candidates[0].content.parts[0].inline_data.data

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        wav_path = tmpfile.name

    save_pcm_as_wav(pcm_data, wav_path)
    return wav_path


def convert_audio_format(input_path, output_path, format):
    audio = pydub.AudioSegment.from_wav(input_path)
    audio.export(output_path, format=format)


# ----------------------------------------------------------------------
# Streamlit UI
# ----------------------------------------------------------------------

st.title("🔊 Text to Speech Converter 📝")
st.image("https://www.piecex.com/product_image/20190625044028-00000544-image2.png")
st.markdown("""
This app converts text to speech using Google's **Gemini TTS** models.
Please enter your Gemini API key on the sidebar. **Do not share your API key with others.**
""")

# Input for Gemini API key
api_key = st.sidebar.text_input("Enter your Gemini API key", type="password")

# Select box for model selection
model = st.sidebar.selectbox(
    "Select Model",
    ["gemini-3.6-flash-preview-tts", "gemini-2.5-pro-preview-tts","gemini-3.1-flash-tts-preview"],
)

# Select box for voice selection (Gemini prebuilt voices)
voice = st.sidebar.selectbox(
    "Select Voice",
    [
        "Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus",
        "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus",
        "Umbriel", "Algieba", "Despina", "Erinome", "Algenib",
        "Rasalgethi", "Laomedeia", "Achernar", "Alnilam", "Schedar",
        "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi",
        "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat",
    ],
)

# Select box for output format selection
format = st.sidebar.selectbox("Select Format", ["wav", "mp3", "opus", "aac", "flac"])

# Text input from user
user_input = st.text_area("Enter text to convert to speech", "Hello, welcome to our text to speech converter!")

if st.button("Convert"):
    if not api_key:
        st.error("API key is required to convert text to speech.")
    else:
        with st.spinner("Converting text to speech..."):
            try:
                wav_speech_path = text_to_speech(api_key, user_input, model, voice)

                if format != "wav":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmpfile:
                        convert_audio_format(wav_speech_path, tmpfile.name, format)
                        speech_path = tmpfile.name
                    os.remove(wav_speech_path)
                else:
                    speech_path = wav_speech_path

                # Display an audio player for the generated file
                with open(speech_path, "rb") as f:
                    audio_bytes = f.read()
                st.audio(audio_bytes, format=f"audio/{format}")

                # Offer a real download button (byte-based, works reliably in Streamlit)
                st.download_button(
                    label=f"Download {format.upper()} file",
                    data=audio_bytes,
                    file_name=f"speech.{format}",
                    mime=f"audio/{format}",
                )

                # Clean up: delete the temporary file after use
                os.remove(speech_path)
            except Exception as e:
                st.error(f"An error occurred: {e}")


# ----------------------------------------------------------------------
# Footer / styling (unchanged from original)
# ----------------------------------------------------------------------

sidebar_footer_html = """
<div style="text-align: left;">
    <p style="font-size: 16px;"><b>Author: 🌟 Abdul Hadi 🌟</b></p>
    <a href="https://github.com/abdulhadi-mlk"><img src="https://img.shields.io/badge/GitHub-Profile-blue?style=for-the-badge&logo=github" alt="GitHub"/></a><br>
    <a href="https://www.linkedin.com/in/abdul-hadi-mlk/"><img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/></a><br>
    <a href="mailto:abdulhadimalik4540@gmail.com"><img src="https://img.shields.io/badge/Gmail-Contact%20Me-red?style=for-the-badge&logo=gmail" alt="Gmail"/></a>
</div>
"""
st.sidebar.markdown(sidebar_footer_html, unsafe_allow_html=True)


def set_background_image():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://images.pexels.com/photos/4097159/pexels-photo-4097159.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1");
            background-size: cover;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


set_background_image()

sidebar_background_image = """
<style>
[data-testid="stSidebar"] {
    background-image: url("https://images.pexels.com/photos/6101958/pexels-photo-6101958.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1");
    background-size: cover;
}
</style>
"""
st.sidebar.markdown(sidebar_background_image, unsafe_allow_html=True)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

footer_css = """
<style>
.footer {
    position: fixed;
    right: 0;
    bottom: 0;
    width: auto;
    background-color: transparent;
    color: black;
    text-align: right;
    padding-right: 10px;
}
</style>
"""

footer_html = """
<div class="footer">
    <p>Credit: Dr. Aammar Tufail | Phd | Data Scientist | Bioinformatician (<a href="https://www.youtube.com/@Codanics" target="_blank">CODANICS</a>)</p>
    <a href="https://github.com/AammarTufail"><img src="https://img.shields.io/badge/GitHub-Profile-blue?style=for-the-badge&logo=github" alt="GitHub"/></a>
    <a href="https://www.kaggle.com/muhammadaammartufail"><img src="https://img.shields.io/badge/Kaggle-Profile-blue?style=for-the-badge&logo=kaggle" alt="Kaggle"/></a>
    <a href="https://www.linkedin.com/in/dr-muhammad-aammar-tufail-02471213b/"><img src="https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn"/></a>
    <a href="https://www.youtube.com/@codanics"><img src="https://img.shields.io/badge/YouTube-Profile-red?style=for-the-badge&logo=youtube" alt="YouTube"/></a>
    <a href="https://www.facebook.com/aammar.tufail"><img src="https://img.shields.io/badge/Facebook-Profile-blue?style=for-the-badge&logo=facebook" alt="Facebook"/></a>
    <a href="https://twitter.com/aammar_tufail"><img src="https://img.shields.io/badge/Twitter-Profile-blue?style=for-the-badge&logo=twitter" alt="Twitter/X"/></a>
    <a href="https://www.instagram.com/aammartufail/"><img src="https://img.shields.io/badge/Instagram-Profile-blue?style=for-the-badge&logo=instagram" alt="Instagram"/></a>
    <a href="mailto:aammar@codanics.com"><img src="https://img.shields.io/badge/Email-Contact%20Me-red?style=for-the-badge&logo=email" alt="Email"/></a>
</div>
"""

st.markdown(footer_css, unsafe_allow_html=True)
st.markdown(footer_html, unsafe_allow_html=True)