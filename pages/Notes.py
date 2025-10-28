import streamlit as st
import io
from fpdf import FPDF, FPDF_FONT_DIR
import os 
from docx import Document # Import the docx library


def run_summary_page():
    # --- Inject necessary CSS and remove print-related styles ---
    st.markdown(
        """
        <style>
        .section-header { 
            font-size: 2em; 
            color: var(--yellow-accent); 
            border-bottom: 2px solid var(--yellow-accent); 
            padding-bottom: 5px; 
            margin-top: 2em; 
        }
        .download-button {
            background-color: var(--blue-accent);
            color: var(--foreground);
            border-radius: 12px;
            padding: 10px 24px;
            font-size: 1.2em;
            border: none;
            box-shadow: 3px 3px 6px #000000;
            cursor: pointer;
            transition: transform 0.2s;
            margin-top: 20px;
        }
        .download-button:hover {
            transform: scale(1.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- Authentication Check (Corrected) ---
    if not st.session_state.get('logged_in', False) and not st.session_state.get('is_trial', False):
        st.warning('Please log in or start a free trial to access this page.')
        st.stop()

    # --- Reusable function to generate download data ---
    def get_download_data(format, content):
        # if format == "PDF":
        #     pdf = FPDF()
        #     pdf.add_page()
            
        #     # Use a Unicode-compatible font
        #     # pdf.add_font("DejaVuSansCondensed", "", os.path.join(FPDF_FONT_DIR, "DejaVuSansCondensed.ttf"), uni=True)
        #     font_path = os.path.join("fonts", "DejaVuSansCondensed.ttf")
        #     pdf.add_font("DejaVuSansCondensed", "", font_path, uni=True)
        #     pdf.set_font("DejaVuSansCondensed", "", 12)

            
        #     # Ensure content is a string and handle markdown
        #     content = content.replace('*', '').replace('**', '').replace('###', '')
        #     pdf.multi_cell(0, 10, content)
        #     return pdf.output(dest='S').encode('latin1')
        
        if format == "Word":
            # Create a new Word document
            doc = Document()
            doc.add_paragraph(content)
            
            # Save the document to a BytesIO object
            doc_stream = io.BytesIO()
            doc.save(doc_stream)
            doc_stream.seek(0)
            return doc_stream.getvalue()
        
        elif format == "Text":
            # Remove markdown formatting for plain text
            plain_text = content.replace('*', '').replace('**', '').replace('###', '')
            return plain_text.encode('utf-8')
        
        return b"" # Return empty bytes if format is not recognized


    # --- Main Page Content ---
    if 'summary' in st.session_state and st.session_state.summary:
        st.markdown("---")
        st.markdown("<h2 class='section-header'>Summary and Notes</h2>", unsafe_allow_html=True)
        st.write(st.session_state.summary)

        # --- Download Section ---
        st.markdown("---")
        st.markdown("<h2 class='section-header'>Download Notes</h2>", unsafe_allow_html=True)
        
        # Selectbox for format
        download_format = st.selectbox(
            "Choose a format for your notes:",
            options=[ "Word", "Text"]
        )

        # Map format to a correct file extension and MIME type
        format_map = {
            "PDF": {"ext": "pdf", "mime": "application/pdf"},
            "Word": {"ext": "docx", "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"},
            "Text": {"ext": "txt", "mime": "text/plain"},
        }

        download_file_name = f"summary.{format_map[download_format]['ext']}"
        download_data = get_download_data(download_format, st.session_state.summary)

        # The Download button
        st.download_button(
            label=f"Download as {download_format}",
            data=download_data,
            file_name=download_file_name,
            mime=format_map[download_format]['mime'],
            help=f"Click to download your notes as a {download_format} file."
        )

    else:
        st.info("Please go to the main page and enter a YouTube link to generate notes.")


if __name__ == '__main__':
    run_summary_page()