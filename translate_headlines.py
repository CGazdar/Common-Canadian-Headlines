import csv
import os
import sys

from db import HERE, connect

MODEL = "Helsinki-NLP/opus-mt-fr-en"
BATCH = 64


def french_outlets():
    with open(HERE / "outlets.csv", newline="", encoding="utf-8") as f:
        return sorted(r["outlet_id"] for r in csv.DictReader(f)
                      if (r.get("language") or "en").strip().lower() == "fr")


def get_translator():
    if os.environ.get("FAKE_TRANSLATE"):                  # for testing the plumbing only
        return lambda batch: ["EN: " + t for t in batch]
    import torch
    from transformers import MarianMTModel, MarianTokenizer
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    tok = MarianTokenizer.from_pretrained(MODEL)
    model = MarianMTModel.from_pretrained(MODEL).to(device).eval()

    def run(batch):
        enc = tok(batch, return_tensors="pt", padding=True, truncation=True, max_length=128).to(device)
        with torch.no_grad():
            out = model.generate(**enc, num_beams=1, max_new_tokens=96)
        return tok.batch_decode(out, skip_special_tokens=True)
    return run


def main():
    conn = connect()
    conn.execute("CREATE TABLE IF NOT EXISTS translations (headline_id INTEGER PRIMARY KEY, text_en TEXT)")
    fr = french_outlets()
    if not fr:
        sys.exit("No outlets with language = fr in outlets.csv.")
    marks = ",".join("?" * len(fr))
    if "--sample" in sys.argv:
        for hid, a, b in conn.execute(
                f"SELECT c.id, c.headline, t.text_en FROM headlines_clean c JOIN translations t ON t.headline_id = c.id "
                f"WHERE c.outlet_id IN ({marks}) ORDER BY random() LIMIT 30", fr):
            print(f"FR: {a}\nEN: {b}\n")
        return
    limit = next((int(a) for a in sys.argv[1:] if a.isdigit()), None)
    todo = conn.execute(
        f"SELECT c.id, c.headline FROM headlines_clean c LEFT JOIN translations t ON t.headline_id = c.id "
        f"WHERE c.outlet_id IN ({marks}) AND t.headline_id IS NULL AND c.is_syndicated = 0 ORDER BY length(c.headline), c.id", fr).fetchall()
    if limit:
        todo = todo[:limit]
    print(f"{len(todo):,} French headlines to translate ({', '.join(fr)})", flush=True)
    translate = get_translator()
    done = 0
    try:
        for i in range(0, len(todo), BATCH):
            chunk = todo[i:i + BATCH]
            texts = translate([h for _, h in chunk])
            conn.executemany("INSERT OR REPLACE INTO translations VALUES (?,?)",
                             [(hid, t) for (hid, _), t in zip(chunk, texts)])
            conn.commit()
            done += len(chunk)
            if (i // BATCH) % 50 == 0:
                print(f"  {done:,}/{len(todo):,}", flush=True)
    except KeyboardInterrupt:
        print("\nStopped. Progress is saved; run again to continue.")
    print(f"Done: {done:,} translated. Look at a few with: python translate_headlines.py --sample")


if __name__ == "__main__":
    main()