import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from config import SBC_INDEX_DIR, SBC_SOURCE_DIR, SBC_TOP_K


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def read_source(path: Path) -> str:
    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )

    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        return "\n".join(
            page.extract_text() or ""
            for page in reader.pages
        )

    if suffix == ".docx":
        from docx import Document

        doc = Document(str(path))
        return "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

    return ""


def chunk(text: str, words_per_chunk=900, overlap=120):
    words = text.split()

    output = []
    start = 0

    while start < len(words):
        end = min(start + words_per_chunk, len(words))
        output.append(" ".join(words[start:end]))

        if end >= len(words):
            break

        start = end - overlap

    return output


def build_index():
    records = []

    for path in SBC_SOURCE_DIR.rglob("*"):
        if not path.is_file():
            continue

        if path.name == "PUT_OFFICIAL_SBC_FILES_HERE.txt":
            continue

        text = read_source(path)

        if not text.strip():
            continue

        for number, piece in enumerate(chunk(text)):
            records.append({
                "source": str(
                    path.relative_to(SBC_SOURCE_DIR)
                ),
                "chunk": number,
                "text": piece,
            })

    if not records:
        print(
            "No SBC documents found in data/sbc.\n"
            "Place official/current SBC PDF/TXT/MD/DOCX files there first."
        )
        return False

    model = SentenceTransformer(EMBEDDING_MODEL)

    vectors = model.encode(
        [record["text"] for record in records],
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    vectors = np.asarray(
        vectors,
        dtype="float32",
    )

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    SBC_INDEX_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    faiss.write_index(
        index,
        str(SBC_INDEX_DIR / "index.faiss"),
    )

    (SBC_INDEX_DIR / "metadata.json").write_text(
        json.dumps(
            records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"Indexed {len(records)} chunks.")
    return True


class SBCRetriever:
    def __init__(self):
        self.index_file = SBC_INDEX_DIR / "index.faiss"
        self.metadata_file = SBC_INDEX_DIR / "metadata.json"

        self.index = None
        self.metadata = []
        self.model = None

        if (
            self.index_file.exists()
            and self.metadata_file.exists()
        ):
            self.index = faiss.read_index(
                str(self.index_file)
            )

            self.metadata = json.loads(
                self.metadata_file.read_text(
                    encoding="utf-8"
                )
            )

            self.model = SentenceTransformer(
                EMBEDDING_MODEL
            )

    def search(
        self,
        query: str,
        top_k: int = SBC_TOP_K,
    ):
        if self.index is None:
            return []

        vector = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        vector = np.asarray(
            vector,
            dtype="float32",
        )

        scores, ids = self.index.search(
            vector,
            top_k,
        )

        results = []

        for score, idx in zip(
            scores[0],
            ids[0],
        ):
            if idx < 0:
                continue

            item = dict(self.metadata[idx])
            item["score"] = float(score)
            results.append(item)

        return results

    def context(self, query: str):
        results = self.search(query)

        if not results:
            return (
                "SBC EVIDENCE NOT AVAILABLE. "
                "The local SBC index is empty or not built."
            )

        blocks = []

        for item in results:
            blocks.append(
                f"SOURCE: {item['source']}\n"
                f"CHUNK: {item['chunk']}\n"
                f"SCORE: {item['score']:.4f}\n"
                f"{item['text']}"
            )

        return "\n\n---\n\n".join(blocks)
