from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# Configuration CORS (pour que React puisse communiquer avec ce script)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# L'URL correcte (on pointe sur /ask et non plus /docs)
RENDER_MODEL_URL = "https://substanceai-model.onrender.com/ask"

@app.post("/api/auth/chat_model/")
async def handle_prediction(question: str = Form(...)):
    print(f"Question reçue de React : {question}")
    
    # On prépare le JSON exactement comme demandé par votre modèle
    payload = {
        "question": question,
        "chat_history": []  # On envoie une liste vide pour l'instant
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Appel au modèle sur Render
            response = await client.post(
                RENDER_MODEL_URL, 
                json=payload, 
                timeout=60.0 
            )
            
            # Vérification du succès
            response.raise_for_status()
            
            data = response.json()
            print(f"Réponse reçue de Render : {data}")
            return data
            
        except httpx.HTTPStatusError as e:
            print(f"Erreur Render ({e.response.status_code}) : {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail="Le modèle a rejeté la requête")
        except Exception as e:
            print(f"Erreur de connexion : {str(e)}")
            raise HTTPException(status_code=500, detail="Impossible de joindre Render")