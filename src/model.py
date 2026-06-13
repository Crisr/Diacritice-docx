import json
import re
import torch
from pathlib import Path
from tqdm import tqdm
from transformers import MT5ForConditionalGeneration, T5Tokenizer


_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

if _CONFIG_PATH.exists():
    with open(_CONFIG_PATH, encoding="utf-8") as f:
        _CONFIG = json.load(f)
    MODEL_ID = _CONFIG["model"]["id"]
else:
    MODEL_ID = "iliemihai/mt5-base-romanian-diacritics"


class DiacriticsModel:
    def __init__(self, device: str | None = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        dtype = torch.float16 if self.device == "cuda" else torch.float32

        self.tokenizer = T5Tokenizer.from_pretrained(MODEL_ID)
        self.model = MT5ForConditionalGeneration.from_pretrained(
            MODEL_ID,
            torch_dtype=dtype,
        ).to(self.device)

        if self.device == "cuda":
            self.model = torch.compile(self.model, mode="reduce-overhead")
        self.model.eval()

    def restore(self, text: str, max_length: int = 256) -> str:
        if not text.strip():
            return text
        inputs = self.tokenizer(
            text, max_length=max_length, truncation=True, return_tensors="pt"
        ).to(self.device)
        with torch.inference_mode():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def restore_batch(self, texts: list[str], batch_size: int = 32) -> list[str]:
        results = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            inputs = self.tokenizer(
                batch, max_length=256, truncation=True, padding=True, return_tensors="pt"
            ).to(self.device)
            with torch.inference_mode():
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                )
            results.extend(
                self.tokenizer.decode(o, skip_special_tokens=True) for o in outputs
            )
        return results

    def restore_batch_with_progress(
        self, texts: list[str], batch_size: int = 32
    ) -> list[str]:
        results = []
        n_batches = (len(texts) + batch_size - 1) // batch_size
        for i in tqdm(range(0, len(texts), batch_size), total=n_batches, unit="batch"):
            batch = texts[i : i + batch_size]
            inputs = self.tokenizer(
                batch, max_length=256, truncation=True, padding=True, return_tensors="pt"
            ).to(self.device)
            with torch.inference_mode():
                outputs = self.model.generate(
                    input_ids=inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                )
            results.extend(
                self.tokenizer.decode(o, skip_special_tokens=True) for o in outputs
            )
        return results

    def restore_long(self, text: str) -> str:
        if len(self.tokenizer.encode(text)) <= 256:
            return self.restore(text)
        sentences = re.split(r'(?<=[.!?])\s+', text)
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
