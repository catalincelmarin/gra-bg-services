# Module `kimera.helpers.TextExtractors`

Thin wrapper around `pdfplumber` for PDF validation and text extraction.

## `TextExtractors`

### `is_pdf(file_path: str) -> bool`
Attempts to open `file_path` with `pdfplumber`. Returns `True` when parsing succeeds; swallows any exception and returns `False` otherwise. Useful for quick MIME sniffing without depending on file extensions.

### `extract_text_pdfplumber(pdf_path: str) -> str`
Iterates over each page in the PDF and concatenates the extracted text, stripping trailing whitespace and adding a newline between pages. No post-processing beyond that.
