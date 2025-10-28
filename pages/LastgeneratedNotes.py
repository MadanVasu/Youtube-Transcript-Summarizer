import streamlit as st
from Home import extract_video_id


# This new block will display the summary if it already exists in session_state,
# even if the page reloaded.
if "summary" in st.session_state and st.session_state.summary:
    youtube_link = st.session_state.get("youtube_link", "")
    video_id = extract_video_id(youtube_link)
    st.markdown("---")
    st.markdown("<h2 class='section-header'>Last Generated Notes</h2>", unsafe_allow_html=True)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    st.write(st.session_state.summary)
