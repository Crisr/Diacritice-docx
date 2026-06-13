from docx import Document


def extract_paragraphs(docx_path: str) -> tuple[list[dict], Document]:
    doc = Document(docx_path)
    result = []
    for para in doc.paragraphs:
        full_text = para.text
        if not full_text.strip():
            continue
        runs_info = []
        for run in para.runs:
            runs_info.append({
                "run": run,
                "text": run.text,
            })
        result.append({"text": full_text, "runs": runs_info})
    return result, doc
