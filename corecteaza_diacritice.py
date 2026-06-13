import argparse
import json
import sys
from pathlib import Path

from src.extractor import extract_paragraphs
from src.model import DiacriticsModel
from src.mapper import map_text_to_runs, compute_diacritics_stats, merge_diacritics, save_highlighted_copy


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        print(f"Model: {cfg['model']['id']}")
        print(f"Sursa: {cfg['model']['url']}")
        print()

    parser = argparse.ArgumentParser(
        description="Restaureaza diacriticele intr-un document .docx"
    )
    parser.add_argument("input", type=str, help="Calea catre fisierul .docx")
    parser.add_argument("-o", "--output", type=str, default=None,
                        help="Calea de output (default: output.docx)")
    parser.add_argument("--batch", type=int, default=32,
                        help="Dimensiunea batch-ului (default: 32)")
    parser.add_argument("--cpu", action="store_true",
                        help="Fortheaza CPU chiar daca GPU e disponibil")
    parser.add_argument("--highlight", action="store_true",
                        help="Salveaza si output_highlights.docx cu cuvintele modificate evidențiate cu galben")

    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Eroare: fisierul {input_path} nu exista.", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or "output.docx"

    print(f"Citeste {input_path}...")
    paragraphs, doc = extract_paragraphs(str(input_path))

    if not paragraphs:
        print("Nu s-a gasit text de procesat.")
        doc.save(output_path)
        print(f"Document salvat: {output_path}")
        return

    print(f"Paragrafe gasite: {len(paragraphs)}")
    print(f"Se incarca modelul mt5 (device: {'cpu' if args.cpu else 'auto'})...")
    model = DiacriticsModel(device="cpu" if args.cpu else None)

    print(f"Se restaureaza diacriticele (batch={args.batch})...")
    texts = [p["text"] for p in paragraphs]
    corrected = model.restore_batch_with_progress(texts, batch_size=args.batch)

    print(f"Se actualizeaza documentul...")
    all_orig = []
    all_merged = []
    paragraphs_data = []
    for p, ct in zip(paragraphs, corrected):
        merged = merge_diacritics(p["text"], ct)
        all_orig.append(p["text"])
        all_merged.append(merged)
        map_text_to_runs(p["text"], ct, p["runs"])
        paragraphs_data.append({
            "orig_words": p["text"].split(),
            "merged_words": merged.split(),
        })

    doc.save(output_path)
    print(f"Document salvat: {output_path}")

    if args.highlight:
        hl_path = str(Path(output_path).with_stem(Path(output_path).stem + "_highlights"))
        save_highlighted_copy(str(input_path), hl_path, paragraphs_data)
        print(f"Highlights salvat:  {hl_path}")

    stats = compute_diacritics_stats(" ".join(all_orig), " ".join(all_merged))
    print()
    print("--- Sumar ---")
    print(f"  Total cuvinte in document:   {stats['total']}")
    print(f"  Cuvinte nemodificate (context): {stats['potential']}")
    print(f"  Cuvinte modificate:           {stats['modified']}")


if __name__ == "__main__":
    main()
