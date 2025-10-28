import streamlit as st
import os
import json
import re

# --- Helper Functions for Data Persistence ---
def load_user_data():
    """Load user data from the JSON file."""
    DB_FILE = "user_data.json"
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

# --- Reusable function from Home.py (moved here for this page's logic) ---
def extract_video_id(youtube_video_url):
    """Extracts the video ID from a YouTube URL."""
    pattern = re.compile(r"(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)(?P<video_id>[^&?]+)")
    match = pattern.search(youtube_video_url)
    if match:
        return match.group("video_id")
    return None

def run_profile_page():
    """Renders the user profile page with history."""

    # --- Inject Custom CSS ---
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
    # --- Authentication Check ---
    if not st.session_state.get('logged_in', False) and not st.session_state.get('is_trial', False):
        st.warning('Please log in or start a free trial to view your profile.')
        st.stop()

    # --- Page Content ---
    st.markdown("<h1 class='main-header'>Your Profile</h1>", unsafe_allow_html=True)
    st.write(f"Logged in as: **{st.session_state.username}**")

    st.markdown("---")
    st.markdown("<h2 class='section-header'>History of Notes</h2>", unsafe_allow_html=True)

    user_data = load_user_data()
    username = st.session_state.username

    # Check if the user exists and has a history
    if username in user_data and "history" in user_data[username] and user_data[username]["history"]:
        history = user_data[username]["history"]
        # Display history in reverse chronological order
        for i, item in enumerate(reversed(history)):
            # Use the video title for the expander, if available. Fallback to URL.
            expander_title = item.get('title', item.get('youtube_link', 'Unknown Link'))
            
            with st.expander(f"**Video {len(history) - i}:** {expander_title}"):
                
                # Display the video thumbnail
                video_id = extract_video_id(item.get('youtube_link', ''))
                if video_id:
                    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width=200)

                # Display all the requested information
                if 'timestamp' in item:
                    st.write(f"**Date:** {item.get('timestamp', 'N/A')}")
                
                st.write("**YouTube URL:**")
                st.write(item.get("youtube_link", "No link found."))
                
                st.write("**Summary:**")
                st.write(item.get("summary", "No summary found."))
                
                if "notes" in item and item["notes"]:
                    st.write("**My Notes:**")
                    st.write(item["notes"])

                if "transcript" in item and item["transcript"]:
                    st.write("**Video Transcript:**")
                    st.write(item["transcript"])
    else:
        st.info("You have no history yet. Generate some notes on the Home page to get started!")

if __name__ == "__main__":
    run_profile_page()