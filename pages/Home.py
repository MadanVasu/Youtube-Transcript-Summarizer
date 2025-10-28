import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
from googleapiclient.discovery import build
import tempfile

# --- Load environment variables and configure APIs ---
load_dotenv()
try:
    genai.configure(api_key=os.getenv("API"))
    youtube_api_key = os.getenv("YOUTUBE_API_KEY")
    if not youtube_api_key:
        st.error("YOUTUBE_API_KEY not found in .env file. Please add it to use the video functionality.")
    if not os.getenv("API"):
        st.error("API key for Gemini not found in .env file. Please add it.")
except Exception as e:
    st.error(f"Error configuring API keys: {e}")

# --- Custom CSS and JS Injection (from your previous code) ---
# NOTE: Using a single style block is cleaner than opening a file.
st.markdown(
    """
    <style>
    .st-emotion-cache-1r4qj8m { text-align: center; }
    :root {
        --background: hsl(240, 65%, 28%); --foreground: hsl(288, 50%, 96%);
        --blue-accent: #1a65c2; --yellow-accent: #c98909;
        --green-accent: hsl(92, 67%, 49%); --button-color: hsl(220, 78%, 44%);
        --input-background: hsl(210 40% 96.1%); --input-border: #f00e0e;
        --input-text-color: #2e3440;
    }
    .dark {
        --background: hsl(86, 81%, 47%); --foreground: hsl(210 40% 98%);
        --blue-accent: #88c0d0; --yellow-accent: #ebcb8b;
        --green-accent: #a3be8c; --button-color: #2e3440;
        --input-background: hsl(217, 63%, 41%); --input-border: #1e5cd6;
        --input-text-color: #d8dee9;
    }
    .stApp { background-color: var(--background); color: var(--foreground); }
    label { color: var(--foreground) !important; }
    .main-header { font-size: 3em; font-weight: bold; color: var(--blue-accent); text-align: center; margin-bottom: 0.5em; text-shadow: 2px 2px 4px #ee1313; }
    .stButton > button {
        background-color: var(--green-accent); color: var(--button-color); border-radius: 12px;
        padding: 4px 2px; font-size: 1.2em; border: none; box-shadow: 3px 3px 6px #ff0808;
        transition: transform 0.2s;
    }
    .stButton > button:hover { transform: scale(1.05); }
    .stTextInput > div > div > input {
        background-color: var(--input-background) !important; color: var(--input-text-color) !important;
        border-radius: 10px; border: 2px solid var(--input-border) !important; padding: 10px;
    }
    .section-header { font-size: 2em; color: var(--yellow-accent); border-bottom: 2px solid var(--yellow-accent); padding-bottom: 5px; margin-top: 2em; }
    .print-button {
        background-color: var(--blue-accent); color: var(--foreground); border-radius: 12px;
        padding: 10px 24px; font-size: 1.2em; border: none; box-shadow: 3px 3px 6px #000000;
        cursor: pointer; transition: transform 0.2s; margin-top: 20px;
    }
    .print-button:hover { transform: scale(1.05); }
    @media print { .noprint { visibility: hidden; display: none; } }
    </style>
    <script>
        function printSummary() {
            window.print();
        }
    </script>
    """,
    unsafe_allow_html=True
)

# --- Reusable Functions ---
@st.cache_data
def extract_video_id(youtube_video_url):
    pattern = re.compile(r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)(?P<video_id>[^&?]+)")
    match = pattern.search(youtube_video_url)
    if match:
        return match.group("video_id")
    return None

@st.cache_data
def extract_transcript_details(youtube_video_url):
    video_id = extract_video_id(youtube_video_url)
    if not video_id:
        st.error("Invalid YouTube URL. Please provide a valid URL.")
        return None, None
    
    video_title = "Title not found"
    transcript_text = ""
    # First, try to get the video metadata (title, description)
    try:
        youtube = build('youtube', 'v3', developerKey=youtube_api_key)
        request = youtube.videos().list(part='snippet', id=video_id)
        response = request.execute()
        
        if response['items']:
            video_snippet = response['items'][0]['snippet']
            video_title = video_snippet.get('title', video_title)
    except Exception as e:
        st.error(f"An error occurred while fetching video metadata: {e}")
        return None, None

    try:
        ytapi = YouTubeTranscriptApi()
        transcript_text = ytapi.fetch(video_id)
        return str(transcript_text)
        # return transcript_text

    except (TranscriptsDisabled, NoTranscriptFound) as e:
        try:
            youtube = build('youtube', 'v3', developerKey=youtube_api_key)
            request = youtube.videos().list(part='snippet', id=video_id)
            response = request.execute()
            
            if response['items']:
                video_snippet = response['items'][0]['snippet']
                video_title = video_snippet.get('title', 'No Title Available')
                video_description = video_snippet.get('description', 'No Description Available')
                return f"Video Title: {video_title}\n\nVideo Description: {video_description}"
            else:
                st.error("Could not find video details. The video may be private, deleted, or the API key is incorrect.")
                return None
        except Exception as e:
            st.error(f"An error occurred while using the YouTube Data API: {e}")
            st.error("Please check your YOUTUBE_API_KEY in the .env file.")
            return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

def generate_gemini_content(transcript_text, prompt):
    model=genai.GenerativeModel("gemini-2.5-flash")
    # full_text = " ".join(d.text for d in transcript_text)
    response=model.generate_content(prompt + transcript_text)
    return response.text

# --- Main App Function ---
def run_home_page():
    # --- Initialize Session State ---
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "is_trial" not in st.session_state:
        st.session_state.is_trial = False
    if "auth_stage" not in st.session_state:
        st.session_state.auth_stage = 'main'
    
    # --- Header with Logo and Auth Buttons ---
    col1, col2, col3 = st.columns([2, 4, 4])
    with col1:
        st.image('logo/ytlogo.png', width=120)
    
    with col3:
        if st.session_state.logged_in:
            st.write(f"Welcome back, {st.session_state.username}!")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.is_trial = False
                st.session_state.auth_stage = 'main'
                st.rerun()
        elif st.session_state.is_trial:
            st.write("Welcome, Trial User!")
            if st.button("End Trial"):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.is_trial = False
                st.session_state.auth_stage = 'main'
                st.rerun()
        else:
            login_btn, register_btn, trial_btn = st.columns(3)
            with login_btn:
                if st.button("Login", use_container_width=True, key="main_login"):
                    st.session_state.auth_stage = 'login'
                    st.rerun()
            with register_btn:
                if st.button("Register", use_container_width=True, key="main_register"):
                    st.session_state.auth_stage = 'register'
                    st.rerun()
            with trial_btn:
                if st.button("Free Trial", use_container_width=True, key="main_trial"):
                    st.session_state.is_trial = True
                    st.session_state.username = "Trial User"
                    st.rerun()

    # --- Conditional UI based on login status ---
    if st.session_state.logged_in or st.session_state.is_trial:
        # --- Main Hero Section with Description ---
        st.write("")
        st.header("Built specifically for Indian content creators and global users...")
        st.write("our platform offers unmatched language support and AI capabilities.")
        st.write("")

        # --- Feature Grid (3x2 Layout) ---
        col_a, col_b, col_c = st.columns(3, gap="large")
        with col_a:
            st.markdown("<h3><span style='color: #e91e63;'>▶️</span> Unlimited Video Length</h3>", unsafe_allow_html=True)
            st.write("Process videos from 1 minute to 10+ hours without restrictions")
        with col_b:
            st.markdown("<h3><span style='color: #2196f3;'>🌐</span> 100+ Languages</h3>", unsafe_allow_html=True)
            st.write("Support for Indian languages (Hindi, Tamil, Telugu) and global languages")
        with col_c:
            st.markdown("<h3><span style='color: #9c27b0;'>📚</span> AI Summarization</h3>", unsafe_allow_html=True)
            st.write("Smart summaries using Gemini 1.5 Pro, GPT-4, and Claude 3")
        col_d, col_e, col_f = st.columns(3)
        with col_d:
            st.markdown("<h3><span style='color: #4caf50;'>🎙️</span> High-Accuracy Transcription</h3>", unsafe_allow_html=True)
            st.write("Whisper AI + Google Speech-to-Text for perfect transcripts")
        with col_e:
            st.markdown("<h3><span style='color: #ff9800;'>🎧</span> Text-to-Speech</h3>", unsafe_allow_html=True)
            st.write("Natural Indian voices with ElevenLabs and Amazon Polly")
        with col_f:
            st.markdown("<h3><span style='color: #03a9f4;'>⬇️</span> Export Options</h3>", unsafe_allow_html=True)
            st.write("Download as Markdown, PDF, DOCX, or MP3 audio files")

        # --- "Perfect for Indian Content" Section ---
        st.markdown('<div class="indian-content-section">', unsafe_allow_html=True)
        st.header("Perfect for Indian Content")
        st.write("First platform to offer comprehensive Indian language support with context-aware AI translation")
        st.markdown('</div>', unsafe_allow_html=True)

        # --- Main Summarizer UI (from your new code) ---
        st.markdown("---")
        st.title("YouTube Transcript to Detailed Notes Converter")
        youtube_link = st.text_input("Enter YouTube Video Link:")

        prompt = """You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video. Your response should have three parts: first, the entire transcript of the video in the same language, a detailed summary of the video in a large paragraph, and next to it, detailed notes in a point-wise format. Please provide a paragraph of video summary and a point-wise notes in markdown format. Please provide the summary of the text given here: """

        if youtube_link:
            video_id = extract_video_id(youtube_link)
            if video_id:
                st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

        if st.button("Get Detailed Notes"):
            with st.spinner('Fetching transcript and generating summary...'):
                transcript_text = extract_transcript_details(youtube_link)
                if transcript_text:
                    summary = generate_gemini_content(transcript_text, prompt)
                    st.session_state["summary"] = summary
                    st.session_state["transcript"] = transcript_text
                    st.write(summary)
    else:
        # --- Login/Register Forms ---
        st.write("")
        st.title("Welcome! Please Login or Register.")
        st.image("logo/mainpagelogo.png")
        st.title("YouTube Transcript Summarizer")
        if st.session_state.auth_stage == 'login':
            with st.form("login_form"):
                st.subheader("Login")
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")
                if submitted:
                    if username == "user" and password == "password": # Dummy credentials
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
            if st.button("Back"):
                st.session_state.auth_stage = 'main'
                st.rerun()
        elif st.session_state.auth_stage == 'register':
            with st.form("register_form"):
                st.subheader("Register")
                new_username = st.text_input("Choose a Username")
                new_password = st.text_input("Create a Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Register")
                if submitted:
                    if new_password == confirm_password:
                        st.session_state.logged_in = True
                        st.session_state.username = new_username
                        st.success("Registration successful! You are now logged in.")
                        st.rerun()
                    else:
                        st.error("Passwords do not match.")
            if st.button("Back"):
                st.session_state.auth_stage = 'main'
                st.rerun()

# Run the page content
if __name__ == "__main__":
    run_home_page()