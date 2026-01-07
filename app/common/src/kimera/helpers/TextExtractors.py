import pdfplumber

class TextExtractors:
    def is_pdf(file_path):
        try:
            with pdfplumber.open(file_path) as pdf:
                return True  # If it opens without error, it's a valid PDF
        except Exception:
            return False

    @staticmethod
    def extract_text_pdfplumber(pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text().strip() + "\n"

        return text
