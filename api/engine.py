import os
import fitz
import re
import faiss
import random
import numpy as np
from sentence_transformers import SentenceTransformer
from SubstanceAi import settings
from mistralai import Mistral


class SubstanciaEngineUniversal:

    def __init__(self, user_profile: dict):
        self.encoder = SentenceTransformer(
            "paraphrase-multilingual-mpnet-base-v2"
        )

        # self.client = Mistral(
        #     api_key=os.environ.get("MISTRAL_API_KEY")
        # )
        self.client = Mistral(
            api_key=settings.MISTRAL_API_KEY )
        
        
        self.chunks = []
        self.index = None
        self.last_context = ""
        self.last_question = ""
        self.last_answer = ""
        self.user_profile = user_profile

    # -------------------------------
    # TEXT CLEANING (IDENTIQUE)
    # -------------------------------
    def clean_text_expert(self, text):
        text = re.sub(r'[|]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    # -------------------------------
    # FOLLOW-UP / SUMMARY (IDENTIQUE)
    # -------------------------------
    def is_summary_request(self, question):
        return "résumé" in question.lower() or "résume" in question.lower()

    def is_follow_up(self, question):
        keywords = [
            "explique-moi plus",
            "développe",
            "approfondis",
            "encore",
            "précédente"
        ]
        return any(k in question.lower() for k in keywords) \
            or self.is_summary_request(question)

    # -------------------------------
    # PDF INGESTION (IDENTIQUE)
    # -------------------------------
    def ingest_pdfs(self, file_paths):
        if not file_paths:
            return "Aucun fichier."

        self.chunks = []

        for path in file_paths:
            doc = fitz.open(path)
            fname = os.path.basename(path)

            for i, page in enumerate(doc):
                content = self.clean_text_expert(
                    page.get_text("text")
                )
                if len(content) > 50:
                    self.chunks.append({
                        "source": fname,
                        "page": i + 1,
                        "content": content,
                        "author": doc.metadata.get("author"),
                        "date": doc.metadata.get("creationDate")
                    })
            doc.close()

        contents = [c["content"] for c in self.chunks]

        embeddings = self.encoder.encode(
            contents,
            convert_to_numpy=True
        )

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings.astype("float32"))

        return f"{len(self.chunks)} pages indexées."

    # -------------------------------
    # ASK (LOGIQUE IDENTIQUE)
    # -------------------------------
    def ask(self, question):
        if self.index is None:
            return {
                "error": "Chargez un PDF d'abord."
            }

        follow_up = self.is_follow_up(question)
        is_summary = self.is_summary_request(question)
        sources_md = ""

        # ===== FOLLOW-UP =====
        if follow_up and self.last_answer:

            if is_summary:
                current_context = self.last_answer
                instruction = (
                    "Fais un résumé structuré et concis "
                    "de la réponse précédente."
                )
            else:
                current_context = self.last_context
                instruction = (
                    "Développe et approfondis l'explication "
                    f"précédente pour la question : "
                    f"'{self.last_question}'."
                )

        # ===== NEW QUESTION =====
        else:
            q_emb = self.encoder.encode(
                [question]
            ).astype("float32")

            faiss.normalize_L2(q_emb)
            scores, idx = self.index.search(q_emb, k=8)

            retrieved = []
            sources_md = "### Sources Pertinentes\n\n"
            count = 0

            for score, i in zip(scores[0], idx[0]):
                if score > 0.6:
                    c = self.chunks[i]
                    retrieved.append(c["content"])
                    sources_md += (
                        f"**[{count+1}] {c['source']} "
                        f"(p. {c['page']})** "
                        f"(Score: {score:.2f})\n"
                        f"> {c['content'][:150]}...\n\n"
                    )
                    count += 1

            if not retrieved:
                sources_md = (
                    "_Aucune source hautement pertinente trouvée._\n\n"
                )
                current_context = "Pas de contexte spécifique."
            else:
                current_context = "\n".join(retrieved)

            instruction = f"Réponds à la question : '{question}'"
            self.last_context = current_context
            self.last_question = question

        # -------------------------------
        # USER PROFILE TEXT (IDENTIQUE)
        # -------------------------------
        profile_text = "\n\nPROFIL UTILISATEUR :\n"
        for k, v in self.user_profile.items():
            if isinstance(v, list):
                profile_text += f"- {k}: {', '.join(v)}\n"
            else:
                profile_text += f"- {k}: {v}\n"

        random_seed = random.randint(1, 1000)

        # -------------------------------
        # SYSTEM PROMPT (COPIÉ MOT À MOT)
        # -------------------------------
        system_prompt = f"""
Tu es un professeur expert en pédagogie et en éducation, capable de devenir un spécialiste dans n'importe quel domaine présenté :
mathématiques, physique, chimie, informatique, médecine, biologie, langues, littérature, cuisine, arts, etc.

LANGUE :
- Réponds toujours dans la langue de la question si c'est le français ou l'anglais.
- Si la question est dans une autre langue, réponds dans la langue par défaut de l'utilisateur (profil).
- Si l'utilisateur demande explicitement une langue que tu ne supportes pas, réponds :
  "Je ne peux répondre qu’en français ou en anglais."

RÈGLES STRICTES :
- Explications claires, accessibles et pédagogiques, adaptées au profil utilisateur.
- Utilise uniquement du LaTeX inline simple si nécessaire.
- Ne donne pas d'exemples ou exercices prédéfinis.
- Structurer la réponse : Introduction → Développement → Points clés → Recommandations → Mini-exercices/quiz si pertinent.

FLEXIBILITÉ :
- Le domaine est détecté automatiquement à partir du contenu fourni ou de la question.
- Tu deviens immédiatement un expert dans ce domaine, mais toujours avec un rôle pédagogique.
- Réponses variées : analogies, exemples, mini-exercices, résumés, schémas textuels.

PROFIL UTILISATEUR :
{self.user_profile}

VARIABILITÉ : {random_seed}
- Les réponses à la même question doivent être différentes si la fonction est appelée plusieurs fois.
"""

        user_prompt = (
            f"CONTEXTE :\n{current_context}\n"
            f"{profile_text}\n\n"
            f"DEMANDE : {instruction}"
        )

        # -------------------------------
        # MISTRAL CALL
        # -------------------------------
        response = self.client.chat.complete(
            model="mistral-large-latest",
            temperature=0.8,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )

        answer = response.choices[0].message.content
        self.last_answer = answer

        return {
            "answer": answer,
            "sources": sources_md,
            "question": question
        }
