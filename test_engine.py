from api.engine import SubstanciaEngineUniversal

user_profile = {
    "Quelle langue préfères-tu pour apprendre ?": "Français",
    "Quel niveau de langue préfères-tu dans les explications ?": "Simple",
}

engine = SubstanciaEngineUniversal(user_profile)

pdfs = ["npl-3-4.pdf"]  # mets un vrai PDF ici

engine.ingest_pdfs(pdfs)

result = engine.ask("C'est quoi la tokenisation ?")

print(result["answer"])
