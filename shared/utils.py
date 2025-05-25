import json
import os

def load_projects():
    """Carica i progetti dal file JSON"""
    projects_file = os.path.join("data", "projects.json")
    
    if not os.path.exists(projects_file):
        return []
    
    try:
        with open(projects_file, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Errore nel caricamento dei progetti: {e}")
        return []

def save_projects(projects):
    """Salva i progetti nel file JSON"""
    projects_file = os.path.join("data", "projects.json")
    
    # Assicurati che la directory data esista
    os.makedirs("data", exist_ok=True)
    
    try:
        with open(projects_file, "w") as f:
            json.dump(projects, f, indent=4)
        return True
    except Exception as e:
        print(f"Errore nel salvataggio dei progetti: {e}")
        return False