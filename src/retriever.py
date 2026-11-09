"""Recherche des passages les plus pertinents avec TF-IDF et la similarité cosinus."""
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Mots vides français (sans accents, car les accents sont retirés avant la comparaison)
FRENCH_STOP_WORDS = {
    "a", "au", "aux", "avec", "ce", "ces", "cet", "cette", "dans", "de", "des", "du", "elle",
    "en", "et", "est", "etre", "eu", "il", "ils", "je", "la", "le", "les", "leur", "lui", "ma",
    "mais", "me", "meme", "mes", "moi", "mon", "ne", "nous", "on", "ou", "par", "pas", "pour",
    "qu", "que", "qui", "quoi", "sa", "se", "ses", "son", "sont", "sur", "ta", "te", "tes",
    "toi", "ton", "tu", "un", "une", "vos", "votre", "vous", "y", "quel", "quelle", "quels",
    "quelles", "comment", "pourquoi", "quand", "combien", "ou", "donc", "ni", "car", "c", "d", "l", "j", "n", "s", "t",
}
STOP_WORDS = sorted(FRENCH_STOP_WORDS | set(ENGLISH_STOP_WORDS))


class Retriever:
    """Indexe des passages et renvoie les plus proches d'une question."""

    def __init__(self, passages):
        if not passages:
            raise ValueError("Aucun passage à indexer.")
        self.passages = passages
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",   # "modèle" et "modele" deviennent le même mot
            stop_words=STOP_WORDS,
            ngram_range=(1, 2),        # mots seuls + paires de mots ("machine learning")
            sublinear_tf=True,
        )
        self.matrix = self.vectorizer.fit_transform(p.text for p in passages)

    def search(self, question, top_k=3):
        """Renvoie une liste de (score, passage), du plus pertinent au moins pertinent."""
        scores = cosine_similarity(self.vectorizer.transform([question]), self.matrix)[0]
        best = scores.argsort()[::-1][:top_k]
        return [(float(scores[i]), self.passages[i]) for i in best if scores[i] > 0]

    def best_sentence(self, question, passage):
        """Dans un passage, renvoie la phrase la plus proche de la question."""
        vectors = self.vectorizer.transform(passage.sentences)
        scores = cosine_similarity(self.vectorizer.transform([question]), vectors)[0]
        return passage.sentences[int(scores.argmax())]
