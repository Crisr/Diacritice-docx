# Corector Diacritice DOCX — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Script CLI care restaurează diacriticele în documente .docx românești folosind model ML, păstrând formatarea originală.

**Architecture:** Python monorepo simplu — 3 module (extractor, model, mapper) + CLI entry point. Citire docx cu python-docx, procesare cu mt5 pe GPU, mapare text corectat pe run-uri.

**Tech Stack:** Python 3.10+, python-docx, transformers, torch (CUDA), sentencepiece, pytest

---

## File Structure

```
diacritice/
├── corecteaza_diacritice.py   # CLI entry point
├── pyproject.toml              # Project config + dependencies
├── src/
│   ├── __init__.py
│   ├── extractor.py            # Citește docx, extrage text+runs per paragraf
│   ├── model.py                # Încarcă mt5, procesează text în batch-uri
│   └── mapper.py               # Mapează text corectat înapoi pe runs
└── tests/
    ├── __init__.py
    ├── test_extractor.py
    ├── test_model.py
    └── test_mapper.py
```

---

### Task 1: Project Setup

**Files:**
- Create: `pyproject.toml`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Create pyproject.toml**

```toml
[project]
name = "corector-diacritice"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "python-docx>=1.1.0",
    "transformers>=4.30.0",
    "torch>=2.0.0",
    "sentencepiece>=0.1.99",
]

[project.scripts]
corecteaza = "corecteaza_diacritice:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

- [ ] **Create `src/__init__.py`** (empty file)
- [ ] **Create `tests/__init__.py`** (empty file)
- [ ] **Create virtualenv and install dependencies**

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pip install pytest
```

- [ ] **Verify: pytest runs without errors**

```bash
pytest --collect-only
```

---

### Task 2: Extractor — citire docx

**Files:**
- Create: `src/extractor.py`
- Create: `tests/test_extractor.py`

#### Test: extrage text paragraf simplu

```python
from extractor import extract_paragraphs

def test_extract_single_paragraph(tmp_path):
    from docx import Document
    doc = Document()
    doc.add_paragraph("A inceput sa ii taie un fir de par.")
    path = tmp_path / "test.docx"
    doc.save(str(path))

    paragraphs, doc_obj = extract_paragraphs(str(path))
    assert len(paragraphs) == 1
    assert paragraphs[0]["text"] == "A inceput sa ii taie un fir de par."
    assert len(paragraphs[0]["runs"]) == 1
```

#### Implementation

```python
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
                "weight": len(run.text) / max(len(full_text), 1),
            })
        result.append({"text": full_text, "runs": runs_info})
    return result, doc
```

#### Test: paragraf cu 3 run-uri

```python
def test_extract_paragraph_with_multiple_runs(tmp_path):
    from docx import Document
    doc = Document()
    p = doc.add_paragraph()
    r1 = p.add_run("A inceput ")
    r1.bold = True
    r2 = p.add_run("sa ii taie ")
    r2.italic = True
    r3 = p.add_run("un fir de par.")
    path = tmp_path / "test.docx"
    doc.save(str(path))

    paragraphs, doc_obj = extract_paragraphs(str(path))
    assert len(paragraphs) == 1
    assert paragraphs[0]["runs"][0]["text"] == "A inceput "
    assert paragraphs[0]["runs"][1]["text"] == "sa ii taie "
    assert paragraphs[0]["runs"][2]["text"] == "un fir de par."
```

#### Test: skip paragrafe goale

```python
def test_extract_skips_empty_paragraphs(tmp_path):
    from docx import Document
    doc = Document()
    doc.add_paragraph("")
    doc.add_paragraph("Text real")
    path = tmp_path / "test.docx"
    doc.save(str(path))

    paragraphs, doc_obj = extract_paragraphs(str(path))
    assert len(paragraphs) == 1
    assert paragraphs[0]["text"] == "Text real"
```

---

### Task 3: Model — wrapper mt5

**Files:**
- Create: `src/model.py`
- Create: `tests/test_model.py`

#### Implementation

```python
import torch
from transformers import MT5ForConditionalGeneration, T5Tokenizer


class DiacriticsModel:
    def __init__(self, device: str | None = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        self.tokenizer = T5Tokenizer.from_pretrained("iliemihai/mt5-base-romanian-diacritics")
        self.model = MT5ForConditionalGeneration.from_pretrained(
            "iliemihai/mt5-base-romanian-diacritics"
        ).to(self.device)

    def restore(self, text: str, max_length: int = 256) -> str:
        if not text.strip():
            return text
        inputs = self.tokenizer(text, max_length=max_length, truncation=True, return_tensors="pt").to(self.device)
        outputs = self.model.generate(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def restore_batch(self, texts: list[str], batch_size: int = 8) -> list[str]:
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            inputs = self.tokenizer(batch, max_length=256, truncation=True, padding=True, return_tensors="pt").to(self.device)
            outputs = self.model.generate(input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"])
            results.extend(self.tokenizer.decode(o, skip_special_tokens=True) for o in outputs)
        return results

    def restore_long(self, text: str) -> str:
        if len(self.tokenizer.encode(text)) <= 256:
            return self.restore(text)
        sentences = text.replace("!\n", "!\n").replace("?\n", "?\n").split(". ")
        chunks = []
        current = ""
        for s in sentences:
            candidate = current + (". " if current else "") + s
            if len(self.tokenizer.encode(candidate)) <= 256:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = s
        if current:
            chunks.append(current)
        results = self.restore_batch(chunks)
        return " ".join(results)
```

#### Test: diacritics restoration

```python
def test_diacritics_restoration():
    from model import DiacriticsModel
    model = DiacriticsModel()
    input_text = "A inceput sa ii taie un fir de par."
    result = model.restore(input_text)
    assert "început" in result
    assert "să" in result
    assert "păr" in result
```

#### Test: batch processing and long text

```python
def test_batch_restoration():
    from model import DiacriticsModel
    model = DiacriticsModel()
    texts = [
        "A inceput sa ii taie un fir de par.",
        "Fata sta in fata si tine camasa de in in mana.",
    ]
    results = model.restore_batch(texts)
    assert len(results) == 2

def test_long_text_restoration():
    from model import DiacriticsModel
    model = DiacriticsModel()
    long_text = " ".join(["A inceput sa ii taie un fir de par."] * 50)
    result = model.restore_long(long_text)
    assert "început" in result
```

---

### Task 4: Mapper — text corectat înapoi pe runs

**Files:**
- Create: `src/mapper.py`
- Create: `tests/test_mapper.py`

#### Implementation

```python
def map_text_to_runs(original_text: str, corrected_text: str, runs_info: list[dict]) -> None:
    if not runs_info:
        return
    if len(runs_info) == 1:
        runs_info[0]["run"].text = corrected_text
        return
    corrected_words = corrected_text.split()
    original_words = original_text.split()
    n_words = len(original_words)
    if n_words == 0:
        return
    word_start = 0
    for info in runs_info:
        n_run_words = max(1, round(info["weight"] * n_words))
        chunk = corrected_words[word_start : word_start + n_run_words]
        info["run"].text = " ".join(chunk) + " " if info["text"].endswith(" ") else " ".join(chunk)
        word_start += n_run_words
```

#### Test: single run

```python
def test_map_single_run():
    from docx import Document
    doc = Document()
    p = doc.add_paragraph("A inceput sa ii taie un fir de par.")
    run = p.runs[0]

    from mapper import map_text_to_runs
    runs_info = [{"run": run, "text": run.text, "weight": 1.0}]
    map_text_to_runs("A inceput sa ii taie un fir de par.", "A început să îi taie un fir de păr.", runs_info)
    assert run.text == "A început să îi taie un fir de păr."
```

#### Test: multiple runs

```python
def test_map_multiple_runs():
    from docx import Document
    doc = Document()
    p = doc.add_paragraph()
    r1 = p.add_run("A inceput ")
    r2 = p.add_run("sa ii taie ")
    r3 = p.add_run("un fir de par.")

    from mapper import map_text_to_runs
    original = "A inceput sa ii taie un fir de par."
    corrected = "A început să îi taie un fir de păr."
    runs_info = [
        {"run": r1, "text": "A inceput ", "weight": len("A inceput ") / len(original)},
        {"run": r2, "text": "sa ii taie ", "weight": len("sa ii taie ") / len(original)},
        {"run": r3, "text": "un fir de par.", "weight": len("un fir de par.") / len(original)},
    ]
    map_text_to_runs(original, corrected, runs_info)
    assert "început" in r1.text
    assert "să" in r2.text
    assert "păr" in r3.text
```

---

### Task 5: CLI entry point

**Files:**
- Create: `corecteaza_diacritice.py`

```python
import argparse
import sys
from pathlib import Path

from extractor import extract_paragraphs
from model import DiacriticsModel
from mapper import map_text_to_runs


def main():
    parser = argparse.ArgumentParser(description="Restaurează diacriticele într-un document .docx")
    parser.add_argument("input", type=str, help="Calea către fișierul .docx")
    parser.add_argument("-o", "--output", type=str, default=None, help="Calea de output")
    parser.add_argument("--batch", type=int, default=8, help="Dimensiunea batch-ului")
    parser.add_argument("--cpu", action="store_true", help="Forțează CPU")

    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Eroare: {input_path} nu există.", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or str(input_path.with_stem(input_path.stem + "_corectat"))

    print(f"Citește {input_path}...")
    paragraphs, doc = extract_paragraphs(str(input_path))

    if not paragraphs:
        print("Nu s-a găsit text de procesat.")
        doc.save(output_path)
        return

    print(f"Paragrafe găsite: {len(paragraphs)}")
    model = DiacriticsModel(device="cpu" if args.cpu else None)

    texts = [p["text"] for p in paragraphs]
    corrected = model.restore_batch(texts, batch_size=args.batch)

    for p, ct in zip(paragraphs, corrected):
        map_text_to_runs(p["text"], ct, p["runs"])

    doc.save(output_path)
    print(f"Document salvat: {output_path}")


if __name__ == "__main__":
    main()
```

---

### Task 6: E2E — test integrare

**Files:**
- Create: `tests/test_e2e.py`

```python
def test_e2e_diacritics_restoration(tmp_path):
    from docx import Document
    doc = Document()
    p = doc.add_paragraph()
    p.add_run("A inceput ").bold = True
    p.add_run("sa ii taie ").italic = True
    p.add_run("un fir de par.")
    input_path = tmp_path / "input.docx"
    doc.save(str(input_path))

    output_path = tmp_path / "output.docx"
    import subprocess
    result = subprocess.run(
        ["python", "corecteaza_diacritice.py", str(input_path), "-o", str(output_path)],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"stderr: {result.stderr}"
    result_doc = Document(str(output_path))
    full_text = result_doc.paragraphs[0].text
    assert "început" in full_text
    assert "să" in full_text
    assert "păr" in full_text
```
