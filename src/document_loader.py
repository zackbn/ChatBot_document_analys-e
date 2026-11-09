"""Lecture de documents .txt, .md et .pdf."""
from pathlib import Path

from pypdf import PdfReader

SUPPORTED = {".txt", ".md", ".pdf"}


def load_document(path):
    """Renvoie une liste de (numéro de page, texte).

    Un fichier texte est considéré comme une seule page.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Format non supporté : {suffix} (formats acceptés : {', '.join(sorted(SUPPORTED))})")

    if suffix == ".pdf":
        reader = PdfReader(path)
        pages = [(i + 1, page.extract_text() or "") for i, page in enumerate(reader.pages)]
    else:
        pages = [(1, path.read_text(encoding="utf-8"))]

    pages = [(n, text) for n, text in pages if text.strip()]
    if not pages:
        raise ValueError("Le document ne contient aucun texte lisible (PDF scanné ?).")
    return pages
