"""
Download and cache embedding models for the SJSU Virtual Assistant
Downloads sentence-transformers models required for semantic search
"""

import os
from sentence_transformers import SentenceTransformer


def download_models():
    """Download required embedding models"""
    
    print("SJSU Virtual Assistant - Model Download")
    print()
    
    # List of models to download
    models = [
        "all-MiniLM-L6-v2",
        "all-mpnet-base-v2"
    ]
    
    print(f"Downloading {len(models)} embedding models...")
    print()
    
    for i, model_name in enumerate(models, 1):
        print(f"[{i}/{len(models)}] Downloading {model_name}...")
        try:
            model = SentenceTransformer(model_name)
            print(f"    Successfully downloaded and cached {model_name}")
            print(f"    Model dimensions: {model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"    Error downloading {model_name}: {str(e)}")
        print()
    
    print("Model download complete!")
    print()
    print("Models are cached in: ~/.cache/torch/sentence_transformers/")
    print()


if __name__ == "__main__":
    download_models()
