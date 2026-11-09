"""Découpage du document en passages : un passage = un paragraphe.

Les paragraphes trop longs (souvent le cas des PDF) sont découpés en
fenêtres de phrases qui se chevauchent, pour ne pas couper une information.
"""
import re
from dataclasses import dataclass

SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
PARAGRAPH_BREAK = re.compile(r"\n\s*\n")


@dataclass
class Passage:
    text: str
    page: int
    sentences: list


def split_sentences(text):
    """Découpe un texte en phrases (après un point, un point d'exclamation ou d'interrogation)."""
    return [s.strip() for s in SENTENCE_END.split(text) if len(s.strip()) > 2]


def split_paragraphs(text, min_words=8):
    """Découpe sur les lignes vides. Un paragraphe très court (un titre)
    est rattaché au paragraphe suivant."""
    paragraphs, pending = [], ""
    for block in PARAGRAPH_BREAK.split(text):
        block = " ".join(block.split())  # espaces et retours à la ligne normalisés
        if not block:
            continue
        block = f"{pending} {block}".strip() if pending else block
        if len(block.split()) < min_words:
            pending = block if block.endswith((".", "!", "?", ":")) else block + "."
        else:
            paragraphs.append(block)
            pending = ""
    if pending:
        paragraphs.append(pending)
    return paragraphs


def make_passages(pages, max_sentences=5, overlap=1):
    """Renvoie la liste des passages de toutes les pages."""
    if not 0 <= overlap < max_sentences:
        raise ValueError("Il faut 0 <= overlap < max_sentences")
    step = max_sentences - overlap
    passages = []
    for page, text in pages:
        for paragraph in split_paragraphs(text):
            sentences = split_sentences(paragraph)
            if len(sentences) <= max_sentences:
                passages.append(Passage(paragraph, page, sentences))
                continue
            for start in range(0, len(sentences) - overlap, step):
                group = sentences[start:start + max_sentences]
                passages.append(Passage(" ".join(group), page, group))
    return passages
