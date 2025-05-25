import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class TranslationsScreen(tk.Toplevel):
    def __init__(self, master, project_name, project_path, master_file_path):
        super().__init__(master)
        self.title(f"Traduzioni - {project_name}")
        self.geometry("1000x700")
        self.project_name = project_name
        self.project_path = project_path
        self.master_file_path = master_file_path
        self.json_files = []
        self.translations = {}
        self.master_language = os.path.basename(master_file_path).split('.')[0]
        
        self.create_widgets()
        self.load_json_files()
        self.load_translations()
    
    def create_widgets(self):
        # Frame per i controlli
        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Titolo
        self.title_label = tk.Label(self.controls_frame, text=f"Traduzioni per {self.project_name}", font=("Helvetica", 16))
        self.title_label.pack(side=tk.LEFT, padx=5)
        
        # Frame principale
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Creiamo un frame con scrollbar
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def load_json_files(self):
        self.json_files = []
        
        # Verifica se il percorso esiste
        if not os.path.exists(self.project_path):
            messagebox.showerror("Errore", f"Il percorso {self.project_path} non esiste")
            return
        
        # Cerca tutti i file JSON nel percorso del progetto
        for root, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.lower().endswith(".json"):
                    file_path = os.path.join(root, file)
                    language = os.path.basename(file_path).split('.')[0]
                    self.json_files.append({
                        "language": language,
                        "path": file_path,
                        "is_master": file_path == self.master_file_path
                    })
    
    def load_translations(self):
        self.translations = {}
        
        # Carica tutti i file JSON
        for file_info in self.json_files:
            try:
                with open(file_info["path"], "r", encoding="utf-8") as f:
                    content = json.load(f)
                    self.translations[file_info["language"]] = content
            except Exception as e:
                messagebox.showerror("Errore", f"Impossibile caricare il file {file_info['path']}: {e}")
        
        # Crea la tabella delle traduzioni
        self.create_translations_table()
    
    def create_translations_table(self):
        # Pulisci il frame scrollabile
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.translations or self.master_language not in self.translations:
            messagebox.showerror("Errore", "File master non trovato o non valido")
            return
        
        # Ottieni tutte le lingue disponibili
        languages = list(self.translations.keys())
        
        # Assicurati che la lingua master sia la prima
        if self.master_language in languages:
            languages.remove(self.master_language)
            languages.insert(0, self.master_language)
        
        # Crea le intestazioni della tabella
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Colonna per le chiavi
        ttk.Label(header_frame, text="Chiave", font=("Helvetica", 10, "bold"), width=30).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Colonne per le lingue
        for i, lang in enumerate(languages):
            is_master = lang == self.master_language
            label_text = f"{lang} {' (Master)' if is_master else ''}"
            ttk.Label(header_frame, text=label_text, font=("Helvetica", 10, "bold"), width=30).grid(row=0, column=i+1, padx=5, pady=5, sticky="w")
        
        # Estrai tutte le chiavi dal file master
        master_data = self.translations[self.master_language]
        
        # Funzione ricorsiva per visualizzare le traduzioni
        def display_translations(data, prefix="", row_index=1):
            if isinstance(data, dict):
                for key, value in data.items():
                    current_key = f"{prefix}.{key}" if prefix else key
                    if isinstance(value, dict):
                        # Crea una riga per la chiave padre
                        key_frame = ttk.Frame(self.scrollable_frame)
                        key_frame.pack(fill=tk.X, padx=5, pady=2)
                        ttk.Label(key_frame, text=current_key, font=("Helvetica", 9, "bold"), width=30).grid(row=0, column=0, padx=5, pady=2, sticky="w")
                        
                        # Chiamata ricorsiva per i valori annidati
                        row_index = display_translations(value, current_key, row_index)
                    else:
                        # Crea una riga per la chiave-valore
                        key_frame = ttk.Frame(self.scrollable_frame)
                        key_frame.pack(fill=tk.X, padx=5, pady=2)
                        
                        # Mostra la chiave
                        ttk.Label(key_frame, text=current_key, width=30).grid(row=0, column=0, padx=5, pady=2, sticky="w")
                        
                        # Mostra i valori per ogni lingua
                        for i, lang in enumerate(languages):
                            # Ottieni il valore per questa lingua e chiave
                            lang_value = ""
                            try:
                                # Naviga nella struttura JSON per trovare il valore
                                lang_data = self.translations.get(lang, {})
                                path_parts = current_key.split('.')
                                for part in path_parts:
                                    if part and isinstance(lang_data, dict) and part in lang_data:
                                        lang_data = lang_data[part]
                                    else:
                                        lang_data = ""
                                        break
                                lang_value = str(lang_data) if lang_data else ""
                            except:
                                lang_value = ""
                            
                            # Mostra il valore
                            ttk.Label(key_frame, text=lang_value, width=30).grid(row=0, column=i+1, padx=5, pady=2, sticky="w")
                        
                        row_index += 1
            return row_index
        
        # Visualizza tutte le traduzioni
        display_translations(master_data)