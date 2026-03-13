import re
import docx
from datetime import datetime
import io
import PyPDF2


def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


def extract_date_from_filename(filename):
    # for format: 22-12-2024 or 01/02/2026 or 22.12.2024
    match = re.search(r"(\d{2})[/\-.](\d{2})[/\-.](\d{4})", filename)
    if match:
        first, second, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
        if first > 12:
            day, month = first, second
        elif second > 12:
            day, month = second, first
        else:
            day, month = first, second
        return datetime(year, month, day).date()

    # for format: July 17 or Jul 17
    match = re.search(r"([A-Za-z]+) (\d{1,2})", filename)
    if match:
        month_str, day = match.group(1), int(match.group(2))
        try:
            month = datetime.strptime(month_str, "%B").month
        except ValueError:
            try:
                month = datetime.strptime(month_str, "%b").month
            except ValueError:
                return datetime.now().date()
        return datetime(datetime.now().year, month, day).date()

    return datetime.now().date()


def read_pdf(contents: bytes) -> str:
    pdf = PyPDF2.PdfReader(io.BytesIO(contents))
    return "\n".join([page.extract_text() for page in pdf.pages])
