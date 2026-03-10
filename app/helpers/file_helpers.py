import re
import docx
from datetime import datetime


def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


def extract_date_from_filename(filename):
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