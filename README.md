# Diacritice DOCX

**Restaurare diacritice în documente Word, folosind AI pe GPU.**

---

## 🇷🇴 Română

### Descriere

Acest script citește un document `.docx` scris în limba română fără diacritice și restaurează automat diacriticele, **ținând cont de contextul fiecărui cuvânt** (de exemplu, „par” din „par asemănătoare” rămâne „par”, iar „par” din „are păr blond” devine „păr”).

**Caracteristici:**
- Rulează pe GPU NVIDIA (CUDA) sau CPU
- Context-aware – model AI care decide unde pune diacritice și unde nu
- Păstrează 100% din textul original: capitalizare, formatare, spații, tab-uri, cuvinte
- Păstrează formatarea documentului bold/italic/font/tabele
- Exclude automat URL-uri și adrese de email
- Opțional: salvează o copie cu cuvintele modificate evidențiate cu galben (`--highlight`)
- Raport final cu numărul de cuvinte modificate

### Tehnologii

| Componentă | Tehnologie |
|---|---|
| Model AI | `iliemihai/mt5-base-romanian-diacritics` (Hugging Face) |
| GPU | PyTorch + CUDA (NVIDIA) |
| Documente | python-docx |

### Cerințe minime

- **Python** 3.10+
- **GPU:** NVIDIA CUDA (recomandat) sau CPU
- **VRAM:** 2GB+ (modelul ~1.5GB)
- **Spațiu disk:** ~3GB (modelul se descarcă la prima rulare)

### Instalare

```powershell
git clone https://github.com/Crisr/Diacritice-docx.git
cd Diacritice-docx

# Creează și activează virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Instalează dependințele
pip install -r requirements.txt
```

#### Accelerare GPU (CUDA)

Pasul de mai sus instalează PyTorch **CPU-only**. Pentru rulare pe GPU NVIDIA, PyTorch trebuie reinstalat cu suport CUDA, altfel procesarea va rula doar pe procesor (mult mai lent).

**Verifică versiunea ta de CUDA:**

```powershell
nvidia-smi
```

În output, caută rândul `CUDA Version: X.Y` (ex: `12.6`, `12.8`, `11.8`).

**Alege comanda potrivită în funcție de versiunea CUDA:**

| Versiune CUDA | Comandă pip |
|---|---|
| 12.8 / 12.7 / 12.6 | `pip install torch --index-url https://download.pytorch.org/whl/cu126` |
| 12.4 / 12.3 / 12.1 | `pip install torch --index-url https://download.pytorch.org/whl/cu124` |
| 11.8 | `pip install torch --index-url https://download.pytorch.org/whl/cu118` |

> Indexurile PyTorch sunt retrocompatibile cu versiuni mai noi de CUDA (ex: cu126 rulează și pe CUDA 12.8). Pentru lista completă și actualizată, vezi [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/).

**Verifică instalarea CUDA:**

```powershell
python -c "import torch; print(f'CUDA disponibil: {torch.cuda.is_available()}')"
```

Dacă afișează `True`, accelerarea hardware este activă. Dacă nu ai GPU NVIDIA sau nu instalezi PyTorch CUDA, scriptul va folosi automat CPU — poți forța explicit cu `--cpu`.

### Utilizare

```powershell
.venv\Scripts\Activate.ps1
python corecteaza_diacritice.py input.docx
```

**Opțiuni CLI:**

```
python corecteaza_diacritice.py input.docx -o rezultat.docx
python corecteaza_diacritice.py input.docx --cpu
python corecteaza_diacritice.py input.docx --batch 16
python corecteaza_diacritice.py input.docx --highlight
```

| Flag | Descriere |
|---|---|
| `-o, --output` | Cale output (default: `output.docx`) |
| `--batch N` | Dimensiune batch (default: 32) |
| `--cpu` | Forțează CPU în loc de GPU |
| `--highlight` | Salvează și `output_highlights.docx` cu cuvintele modificate evidențiate |

### Configurare

Modelul și sursa sunt specificate în `config.json`. Poți schimba modelul editând acest fișier, fără să modifici codul.

---

## 🇬🇧 English

### Description

This script reads a `.docx` file written in Romanian without diacritics and automatically restores diacritics **based on context** (e.g., "par" in "par asemănătoare" stays "par", while "par" in "are păr blond" becomes "păr").

**Features:**
- Runs on NVIDIA GPU (CUDA) or CPU
- Context-aware AI model – decides where diacritics are needed
- Preserves 100% of original text: capitalization, formatting, spaces, tabs, words
- Preserves bold/italic/font/tables
- Automatically excludes URLs and email addresses
- Optional: saves a highlighted copy with yellow background on modified words (`--highlight`)
- Final summary with modified word count

### Tech Stack

| Component | Technology |
|---|---|
| AI Model | `iliemihai/mt5-base-romanian-diacritics` (Hugging Face) |
| GPU | PyTorch + CUDA (NVIDIA) |
| Documents | python-docx |

### Requirements

- **Python** 3.10+
- **GPU:** NVIDIA CUDA (recommended) or CPU
- **VRAM:** 2GB+ (model ~1.5GB)
- **Disk space:** ~3GB (model downloads on first run)

### Installation

```bash
git clone https://github.com/Crisr/Diacritice-docx.git
cd Diacritice-docx

python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\Activate.ps1   # Windows

pip install -r requirements.txt
```

#### GPU Acceleration (CUDA)

The step above installs PyTorch **CPU-only**. For NVIDIA GPU acceleration, PyTorch must be reinstalled with CUDA support — otherwise processing runs on CPU only (much slower).

**Check your CUDA version:**

```bash
nvidia-smi
```

Look for `CUDA Version: X.Y` in the output (e.g. `12.6`, `12.8`, `11.8`).

**Choose the right command for your CUDA version:**

| CUDA Version | pip command |
|---|---|
| 12.8 / 12.7 / 12.6 | `pip install torch --index-url https://download.pytorch.org/whl/cu126` |
| 12.4 / 12.3 / 12.1 | `pip install torch --index-url https://download.pytorch.org/whl/cu124` |
| 11.8 | `pip install torch --index-url https://download.pytorch.org/whl/cu118` |

> PyTorch wheels are backward-compatible with newer CUDA drivers (e.g. cu126 works on CUDA 12.8). For the full and up-to-date list see [pytorch.org/get-started/locally](https://pytorch.org/get-started/locally/).

**Verify CUDA installation:**

```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

If it prints `True`, hardware acceleration is active. If you don't have an NVIDIA GPU or skip the CUDA step, the script will automatically fall back to CPU — you can also force it explicitly with `--cpu`.

### Usage

```bash
python corecteaza_diacritice.py input.docx
```

**CLI Options:**

| Flag | Description |
|---|---|
| `-o, --output` | Output path (default: `output.docx`) |
| `--batch N` | Batch size (default: 32) |
| `--cpu` | Force CPU instead of GPU |
| `--highlight` | Also save highlighted copy with modified words highlighted |

### Configuration

Model and source URLs are stored in `config.json`. Change the model by editing this file without touching Python code.

---

## Acknowledgement

Acest proiect a fost **vibe coded** cu ajutorul AI-ului din [OpenCode](https://opencode.ai) și [Visual Studio Code](https://code.visualstudio.com/), folosind modelul DeepSeek V4 Flash. Dezvoltarea a implicat colaborare continuă om-AI: specificații, implementare TDD, testare și debugging, totul prin conversation directă în CLI și editor.

This project was **vibe coded** with AI assistance using [OpenCode](https://opencode.ai) and [Visual Studio Code](https://code.visualstudio.com/), powered by the DeepSeek V4 Flash model. Development involved continuous human-AI collaboration: specifications, TDD implementation, testing, and debugging — all through direct CLI and editor conversation.

---

## Keywords

`diacritice` `romanian` `limba romana` `AI` `NLP` `transformers` `CUDA` `GPU` `pytorch` `docx` `microsoft word` `diacritics restoration` `context-aware` `python` `vibe coding` `opencode` `visual studio code` `deepseek` `TDD` `CLI` `mT5` `seq2seq` `blackwell` `RTX 5070`
