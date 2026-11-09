"""Chatbot qui répond à des questions sur un document (.txt, .md ou .pdf).

Exemples :
    python src/chatbot.py data/exemple.txt
    python src/chatbot.py mon_cours.pdf --question "Qu'est-ce que le surapprentissage ?"
"""
import argparse

from chunker import make_passages
from document_loader import load_document
from retriever import Retriever

MIN_SCORE = 0.08  # en dessous, on considère que le document ne contient pas la réponse
NOT_FOUND = "Je n'ai pas trouvé de réponse à cette question dans le document."


class DocumentChatbot:
    def __init__(self, path):
        pages = load_document(path)
        self.passages = make_passages(pages)
        self.retriever = Retriever(self.passages)

    def answer(self, question, top_k=3):
        """Renvoie (réponse, phrase clé, sources).

        La réponse est le passage le plus pertinent ; la phrase clé est,
        dans ce passage, la phrase la plus proche de la question.
        """
        results = self.retriever.search(question, top_k)
        if not results or results[0][0] < MIN_SCORE:
            return NOT_FOUND, None, []
        best_passage = results[0][1]
        key_sentence = self.retriever.best_sentence(question, best_passage)
        return best_passage.text, key_sentence, results


def print_answer(bot, question):
    answer, key_sentence, sources = bot.answer(question)
    print(f"\n🤖 {answer}")
    if key_sentence:
        print(f"\n   ➜ Phrase clé : {key_sentence}")
    if sources:
        print("\n   Sources :")
        for score, passage in sources:
            extract = passage.text if len(passage.text) <= 160 else passage.text[:157] + "..."
            print(f"   - [page {passage.page} | pertinence {score:.2f}] {extract}")


def main():
    parser = argparse.ArgumentParser(description="Pose des questions sur un document.")
    parser.add_argument("document", help="chemin du document (.txt, .md ou .pdf)")
    parser.add_argument("--question", "-q", help="pose une seule question puis quitte")
    args = parser.parse_args()

    bot = DocumentChatbot(args.document)
    print(f"Document chargé : {len(bot.passages)} passages indexés.")

    if args.question:
        print_answer(bot, args.question)
        return

    print("Posez vos questions (tapez « quitter » pour sortir).")
    while True:
        try:
            question = input("\n❓ Vous : ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if question.lower() in {"quitter", "exit", "quit", "q"}:
            break
        if question:
            print_answer(bot, question)
    print("\nAu revoir !")


if __name__ == "__main__":
    main()
