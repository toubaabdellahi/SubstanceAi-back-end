# Python 3.11
FROM python:3.11-slim

# Dépendances système nécessaires pour FAISS et PyMuPDF
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Installer Rust (pour tokenizers)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Créer le dossier de travail
WORKDIR /app

# Copier et installer requirements
COPY backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copier tout le backend
COPY backend/ .

# Exposer le port 8000
EXPOSE 8000

# Lancer Gunicorn
CMD ["gunicorn", "SubstanceAi.wsgi:application", "--bind", "0.0.0.0:8000"]
