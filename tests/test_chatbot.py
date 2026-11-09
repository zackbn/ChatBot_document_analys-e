"""Tests du chatbot. Lancement : python -m pytest"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from chatbot import DocumentChatbot  # noqa: E402
from chunker import make_passages, split_sentences  # noqa: E402
from document_loader import load_document  # noqa: E402

EXAMPLE = ROOT / "data" / "exemple.txt"


@pytest.fixture(scope="module")
def bot():
    return DocumentChatbot(EXAMPLE)


def test_split_sentences():
    assert split_sentences("Bonjour. Ça va ? Oui !") == ["Bonjour.", "Ça va ?", "Oui !"]


def test_paragraphs_and_title():
    pages = [(1, "Mon titre\n\nPremier paragraphe avec assez de mots pour compter. Fin.\n\nDeuxieme paragraphe lui aussi assez long pour compter.")]
    passages = make_passages(pages)
    assert len(passages) == 2
    assert passages[0].text.startswith("Mon titre.")


def test_long_paragraph_overlap():
    pages = [(1, "A un. B deux. C trois. D quatre. E cinq. F six. G sept.")]
    passages = make_passages(pages, max_sentences=3, overlap=1)
    assert len(passages) == 3
    assert passages[0].sentences[-1] == passages[1].sentences[0]


@pytest.mark.parametrize("question, expected", [
    ("Comment choisir le nombre de clusters ?", "coude"),
    ("Qu'est-ce que le surapprentissage ?", "overfitting"),
    ("À quoi sert la régression ?", "valeur numérique"),
    ("Quelles bibliothèques pour le deep learning ?", "PyTorch"),
])
def test_answers(bot, question, expected):
    answer, key_sentence, sources = bot.answer(question)
    assert sources, "aucune source trouvée"
    assert key_sentence in answer
    assert expected.lower() in answer.lower()


def test_unknown_question(bot):
    answer, key_sentence, sources = bot.answer("Quelle est la recette de la tarte aux pommes ?")
    assert sources == [] and key_sentence is None
    assert "pas trouvé" in answer


def test_unsupported_format(tmp_path):
    f = tmp_path / "doc.docx"
    f.write_text("x")
    with pytest.raises(ValueError):
        load_document(f)


def test_pdf(tmp_path):
    canvas = pytest.importorskip("reportlab.pdfgen.canvas")
    pdf = tmp_path / "doc.pdf"
    c = canvas.Canvas(str(pdf))
    c.drawString(72, 720, "Python est un langage de programmation.")
    c.showPage()
    c.drawString(72, 720, "Le modele KNN utilise les voisins les plus proches.")
    c.save()
    answer, _, sources = DocumentChatbot(pdf).answer("Que utilise le modele KNN ?")
    assert "voisins" in answer
    assert sources[0][1].page == 2
