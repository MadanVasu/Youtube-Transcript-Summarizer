import streamlit as st

#Page Set Up
home_page = st.Page(
    page = 'pages/Home.py',
    title = 'Home',
    icon = '🏠' ,
    default = True,
)
notes_page = st.Page(
    page = 'pages/Notes.py',    
    title = 'Notes',
    icon = '📝',
)
translate_page = st.Page(
    page = 'pages/Translate.py',    
    title = 'Translate',
    icon = '🌐',

)

profile_page = st.Page(
    page = 'pages/profile.py',  
    title = 'Profile',  
    icon = '👤',
)



#Navigation set up
pg = st.navigation(
    {  "Info":[home_page,profile_page],
       "Features":[notes_page, translate_page]
    }
)

#Logo
st.logo("logo/ytlogo.png")
st.sidebar.text("YouTube Transcript App")


#Run Navigation
pg.run()