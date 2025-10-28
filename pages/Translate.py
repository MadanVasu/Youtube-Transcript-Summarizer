import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import os



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
        padding: 10px 24px; font-size: 1.2em; border: none; box-shadow: 3px 3px 6px #ff0808;
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


def run_translate_page():
    # --- Authentication Check ---
    if not st.session_state.get('logged_in', False) and not st.session_state.get('is_trial', False):
        st.warning('Please log in or start a free trial to access this page.')
        st.stop()

    # --- Reusable Functions for this page ---
    def translate_text(text, target_language):
        try:
            translated = GoogleTranslator(source='auto', target=target_language).translate(text)
            return translated
        except Exception as e:
            st.error(f"Translation failed: {e}")
            return text

    def text_to_speech(text, lang='en', speed=1.0):
        # gTTS has a 'slow' parameter, not a continuous speed slider.
        # This approximates the slider by toggling the 'slow' option.
        slow_speed = True if speed < 1.0 else False
        tts = gTTS(text, lang=lang, slow=slow_speed)
        
        # Use a temporary file for the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            tts.save(temp_file.name)
            temp_file_path = temp_file.name
        return temp_file_path

    # --- Define the languages here (for simplicity, kept in a dictionary) ---
    languages = {
        "Abkhaz": "ab", "Acehnese": "ace", "Acholi": "ach", "Afrikaans": "af", "Albanian": "sq", "Alur": "alz",
        "Amharic": "am", "Arabic": "ar", "Armenian": "hy", "Assamese": "as", "Aawadhi": "awa", "Aymara": "ay",
        "Azerbaijani": "az", "Balinese": "ban", "Bambara": "bm", "Bashkir": "ba", "Basque": "eu",
        "Batak Karo": "btx", "Batak Simalungun": "bts", "Batak Toba": "bbc", "Belarusian": "be", "Bemba": "bem",
        "Bengali": "bn", "Betawi": "bew", "Bhojpuri": "bho", "Bikol": "bik", "Bosnian": "bs", "Breton": "br",
        "Bulgarian": "bg", "Buryat": "bua", "Cantonese": "yue", "Catalan": "ca", "Cebuano": "ceb",
        "Chichewa (Nyanja)": "ny", "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
        "Chuvash": "cv", "Corsican": "co", "Crimean Tatar": "crh", "Croatian": "hr", "Czech": "cs", "Danish": "da",
        "Dinka": "din", "Divehi": "dv", "Dogri": "doi", "Dombe": "dov", "Dutch": "nl", "Dzongkha": "dz",
        "English": "en", "Esperanto": "eo", "Estonian": "et", "Ewe": "ee", "Fijian": "fj",
        "Filipino (Tagalog)": "fil", "Finnish": "fi", "French": "fr", "French (French)": "fr-FR",
        "French (Canadian)": "fr-CA", "Frisian": "fy", "Fulfulde": "ff", "Gagauz": "gag", "Galician": "gl",
        "Ganda (Luganda)": "lg", "Georgian": "ka", "German": "de", "Greek": "el", "Guarani": "gn",
        "Gujarati": "gu", "Haitian Creole": "ht", "Hakha Chin": "cnh", "Hausa": "ha", "Hawaiian": "haw",
        "Hebrew": "he", "Hiligaynon": "hil", "Hindi": "hi", "Hmong": "hmn", "Hungarian": "hu", "Hunsrik": "hrx",
        "Icelandic": "is", "Igbo": "ig", "Iloko": "ilo", "Indonesian": "id", "Irish": "ga", "Italian": "it",
        "Japanese": "ja", "Javanese": "jv", "Kannada": "kn", "Kapampangan": "pam", "Kazakh": "kk",
        "Khmer": "km", "Kiga": "cgg", "Kinyarwanda": "rw", "Kituba": "ktu", "Konkani": "gom", "Korean": "ko",
        "Krio": "kri", "Kurdish (Kurmanji)": "ku", "Kurdish (Sorani)": "ckb", "Kyrgyz": "ky", "Lao": "lo",
        "Latgalian": "ltg", "Latin": "la", "Latvian": "lv", "Ligurian": "lij", "Limburgan": "li",
        "Lingala": "ln", "Lithuanian": "lt", "Lombard": "lmo", "Luo": "luo", "Luxembourgish": "lb",
        "Macedonian": "mk", "Maithili": "mai", "Makassar": "mak", "Malagasy": "mg", "Malay": "ms",
        "Malay (Jawi)": "ms-Arab", "Malayalam": "ml", "Maltese": "mt", "Maori": "mi", "Marathi": "mr",
        "Meadow Mari": "mhr", "Meiteilon (Manipuri)": "mni-Mtei", "Minang": "min", "Mizo": "lus",
        "Mongolian": "mn", "Myanmar (Burmese)": "my", "Ndebele (South)": "nr", "Nepal Bhasa (Newari)": "new",
        "Nepali": "ne", "Northern Sotho (Sepedi)": "nso", "Norwegian": "no", "Nuer": "nus", "Occitan": "oc",
        "Odia (Oriya)": "or", "Oromo": "om", "Pangasinan": "pag", "Papiamento": "pap", "Pashto": "ps",
        "Persian": "fa", "Polish": "pl", "Portuguese": "pt", "Portuguese (Portugal)": "pt-PT",
        "Portuguese (Brazil)": "pt-BR", "Punjabi": "pa", "Punjabi (Shahmukhi)": "pa-Arab", "Quechua": "qu",
        "Romani": "rom", "Romanian": "ro", "Rundi": "rn", "Russian": "ru", "Samoan": "sm", "Sango": "sg",
        "Sanskrit": "sa", "Scots Gaelic": "gd", "Serbian": "sr", "Sesotho": "st", "Seychellois Creole": "crs",
        "Shan": "shn", "Shona": "sn", "Sicilian": "scn", "Silesian": "szl", "Sindhi": "sd",
        "Sinhala (Sinhalese)": "si", "Slovak": "sk", "Slovenian": "sl", "Somali": "so", "Spanish": "es",
        "Sundanese": "su", "Swahili": "sw", "Swati": "ss", "Swedish": "sv", "Tajik": "tg", "Tamil": "ta",
        "Tatar": "tt", "Telugu": "te", "Tetum": "tet", "Thai": "th", "Tigrinya": "ti", "Tsonga": "ts",
        "Tswana": "tn", "Turkish": "tr", "Turkmen": "tk", "Twi (Akan)": "ak", "Ukrainian": "uk",
        "Urdu": "ur", "Uyghur": "ug", "Uzbek": "uz", "Vietnamese": "vi", "Welsh": "cy", "Xhosa": "xh",
        "Yiddish": "yi", "Yoruba": "yo", "Yucatec Maya": "yua", "Zulu": "zu"
    }

    # --- Page UI and Logic ---
    st.markdown("---")
    st.markdown("<h2 class='section-header'>Translate Notes</h2>", unsafe_allow_html=True)

    if 'summary' in st.session_state and st.session_state.summary:
        selected_language = st.selectbox(
            "Select language for translation:",
            options=list(languages.keys())
        )
        
        if st.button("Translate Notes"):
            with st.spinner('Translating...'):
                target_lang = languages[selected_language]
                translated_summary = translate_text(st.session_state.summary, target_lang)
                st.session_state["translated_summary"] = translated_summary
                st.session_state["translated_lang"] = target_lang
            st.write(f"**Translated Summary ({selected_language}):**")
            st.write(translated_summary)

        st.markdown("---")
        st.markdown("<h2 class='section-header'>Listen to the Notes</h2>", unsafe_allow_html=True)
        speed_factor = st.slider("Select Playback Speed:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)

        # Fix to correctly pass the transcript as a single string to the TTS function
        transcript_exists = "transcript" in st.session_state and st.session_state.transcript
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Play Full Transcript", disabled=not transcript_exists):
                if "transcript" in st.session_state:
                 with st.spinner('Generating audio...'):
                    # Join the transcript list into a single string
                    # full_text = " ".join(d.text for d in st.session_state.transcript)
                    audio_file = text_to_speech(st.session_state.summary, lang='en', speed=speed_factor)
                st.audio(audio_file)
                os.remove(audio_file)

        with col2:
            if st.button("Play Summary"):
                with st.spinner('Generating audio...'):
                    audio_file = text_to_speech(st.session_state.summary, lang='en', speed=speed_factor)
                st.audio(audio_file)
                os.remove(audio_file)

        translated_summary_exists = "translated_summary" in st.session_state and st.session_state.translated_summary
        if st.button(f"Play Translated Summary ({st.session_state.get('translated_lang', 'en')})", disabled=not translated_summary_exists):
            with st.spinner('Generating audio...'):
                audio_file = text_to_speech(st.session_state.translated_summary, lang=st.session_state.translated_lang, speed=speed_factor)
            st.audio(audio_file)
            os.remove(audio_file)

    else:
        st.info("Please go to the main page and enter a YouTube link to generate notes.")


if __name__ == "__main__":
    run_translate_page()