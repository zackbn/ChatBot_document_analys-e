# Chatbot de questions-réponses sur un document

Un chatbot en Python qui lit un document (**.txt, .md ou .pdf**) et répond à des questions sur son contenu. Il renvoie le passage le plus pertinent, la phrase clé et ses sources (numéro de page et score de pertinence).

Il fonctionne **sans clé d'API et sans connexion internet** : la recherche repose sur TF-IDF et la similarité cosinus (scikit-learn).

```
$ python src/chatbot.py data/exemple.txt -q "À quoi sert la régression ?"
Document chargé : 7 passages indexés.

🤖 En apprentissage supervisé, la régression sert à prédire une valeur numérique, comme le prix
   d'une maison. La classification sert à prédire une catégorie, ...

   ➜ Phrase clé : En apprentissage supervisé, la régression sert à prédire une valeur numérique,
     comme le prix d'une maison.

   Sources :
   - [page 1 | pertinence 0.22] En apprentissage supervisé, la régression sert à prédire ...
```

Si la question n'a pas de rapport avec le document, le chatbot répond qu'il n'a pas trouvé de réponse au lieu d'inventer.

## Fonctionnement

```
Document (.txt / .pdf)
   │  1. Lecture                    document_loader.py   (pypdf pour les PDF, page par page)
   ▼
Passages
   │  2. Découpage                  chunker.py           (un passage = un paragraphe ;
   │                                                      fenêtres de phrases qui se chevauchent
   │                                                      pour les paragraphes trop longs)
   ▼
Matrice TF-IDF
   │  3. Indexation                 retriever.py         (mots seuls + paires de mots,
   │                                                      accents et mots vides FR/EN ignorés)
   ▼
Question ──► 4. Similarité cosinus ──► passage le plus proche ──► phrase clé + sources
```

**TF-IDF** donne un poids élevé aux mots fréquents dans un passage mais rares dans le reste du document. Ce sont ceux qui caractérisent le passage. La question est transformée en vecteur de la même manière, puis on cherche le passage dont le vecteur est le plus proche (**similarité cosinus**).

## Installation

```bash
git clone https://github.com/zackbn/document-qa-chatbot.git
cd document-qa-chatbot
pip install -r requirements.txt
```

## Utilisation

```bash
# Mode conversation
python src/chatbot.py data/exemple.txt

# Une seule question
python src/chatbot.py mon_cours.pdf --question "Qu'est-ce que le surapprentissage ?"

# Tests
python -m pytest
```

`data/exemple.txt` est un court texte d'introduction au Machine Learning qui sert de démonstration.

## Structure

```
document-qa-chatbot/
├── src/
│   ├── document_loader.py   # lecture .txt / .md / .pdf
│   ├── chunker.py           # découpage en paragraphes et en phrases
│   ├── retriever.py         # index TF-IDF et recherche par similarité cosinus
│   └── chatbot.py           # interface en ligne de commande
├── data/exemple.txt         # document de démonstration
├── tests/test_chatbot.py    # 10 tests (pytest)
└── requirements.txt
```

## Limites et améliorations prévues

- TF-IDF compare des **mots**, pas des **sens** : « voiture » et « automobile » ne sont pas reconnus comme synonymes. → Utiliser des embeddings (`sentence-transformers`).
- La réponse est un extrait du document, pas une phrase rédigée. → Ajouter un modèle de langage qui rédige la réponse à partir des passages trouvés (architecture **RAG**).
- Les PDF scannés (images) ne sont pas lus. → Ajouter de l'OCR.
- Interface en ligne de commande uniquement. → Interface web avec Streamlit.

## Auteur

**Zakarya Benani Sadoun** — Étudiant en Master IA & Big Data (ESGI Paris), à la recherche d'une alternance Ingénieur IA · [GitHub](https://github.com/zackbn)
