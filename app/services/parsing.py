"""
Извлечение текста из загруженных файлов (PDF / DOCX).

Пока резюме и вакансию принимаем как обычный текст (AnalyzeRequest),
но этот модуль понадобится, как только добавим загрузку файлов —
эндпоинт тогда примет UploadFile и передаст его сюда.
"""

from io import BytesIO

from docx import Document
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    document = Document(BytesIO(file_bytes))
    paragraphs = [p.text for p in document.paragraphs]
    return "\n".join(paragraphs).strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    """Определяет тип файла по расширению и вызывает нужный парсер."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    if lower.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    # .txt и всё остальное — пробуем прочитать как обычный текст
    return file_bytes.decode("utf-8", errors="ignore").strip()
