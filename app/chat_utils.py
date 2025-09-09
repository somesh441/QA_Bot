from fpdf import FPDF
from typing import List, Dict
import base64
from datetime import datetime

def generate_pdf(history: List[Dict]) -> bytes:
    """Generate PDF from chat history"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.cell(200, 10, txt="Chat History Export", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='C')
    pdf.ln(10)
    
    # Content
    for qa in history:
        pdf.set_font("", "B")
        pdf.multi_cell(0, 10, txt=f"Q: {qa['question']}", border=0)
        pdf.set_font("", "")
        pdf.multi_cell(0, 10, txt=f"A: {qa['answer']}", border=0)
        pdf.ln(5)
        
        if qa.get("sources"):
            pdf.set_font("", "I", size=10)
            pdf.cell(0, 10, txt="Sources:", ln=1)
            for src in qa["sources"]:
                pdf.multi_cell(0, 8, txt=f"- {src[:120]}...", border=0)
            pdf.ln(3)
    
    return pdf.output(dest='S').encode('latin1')

def create_download_button(content: bytes, file_name: str, mime_type: str):
    """Create a download button for Streamlit"""
    b64 = base64.b64encode(content).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{file_name}">Download</a>'