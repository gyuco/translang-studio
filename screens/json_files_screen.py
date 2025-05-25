import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from shared.utils import load_projects, save_projects

class JsonFilesScreen(tk.Toplevel):
    def __init__(self, master, project_name, project_path):
        super().__init__(master)
        self.title(f"File JSON - {project_name}")
        self.geometry("800x600")
        self.project_name = project_name
        self.project_path = project_path
        self.json_files = []
        self.selected_item = None
        
        self.create_widgets()
        self.load_json_files()
        self.load_master_file()
    
    def create_widgets(self):
        # Frame per i controlli
        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Titolo
        self.title_label = tk.Label(self.controls_frame, text=f"File JSON in {self.project_name}", font=("Helvetica", 16))
        self.title_label.pack(side=tk.LEFT, padx=5)
        
        # Pulsante "Usa come master"
        self.master_button = tk.Button(self.controls_frame, text="Usa come master", command=self.set_as_master, state=tk.DISABLED)
        self.master_button.pack(side=tk.RIGHT, padx=5)
        
        # Frame per la grid dei file JSON
        self.files_frame = tk.Frame(self)
        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Creazione della grid con Treeview
        self.tree = ttk.Treeview(self.files_frame, columns=("filename", "path", "size", "master"), show="headings")
        self.tree.heading("filename", text="Nome File")
        self.tree.heading("path", text="Percorso")
        self.tree.heading("size", text="Dimensione (KB)")
        self.tree.heading("master", text="Master")
        self.tree.column("filename", width=200)
        self.tree.column("path", width=350)
        self.tree.column("size", width=100)
        self.tree.column("master", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.files_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Binding per il doppio click
        self.tree.bind("<Double-1>", self.open_json_file)
        
        # Binding per la selezione
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
    
    def on_select(self, event):
        # Attiva il pulsante "Usa come master" quando una riga è selezionata
        selected_items = self.tree.selection()
        if selected_items:
            self.selected_item = selected_items[0]
            self.master_button.config(state=tk.NORMAL)
        else:
            self.selected_item = None
            self.master_button.config(state=tk.DISABLED)
    
    def set_as_master(self):
        if not self.selected_item:
            return
        
        # Ottiene l'indice del file selezionato
        file_index = int(self.selected_item)
        file_path = self.json_files[file_index]["path"]
        
        # Carica i progetti
        projects = load_projects()
        
        # Trova il progetto corrente e aggiorna il master_file
        for project in projects:
            if project["name"] == self.project_name and project["path"] == self.project_path:
                project["master_file"] = file_path
                break
        
        # Salva i progetti aggiornati
        save_projects(projects)
        
        # Aggiorna la visualizzazione
        self.load_master_file()
        messagebox.showinfo("Informazione", f"File '{os.path.basename(file_path)}' impostato come master")
    
    def load_master_file(self):
        # Carica i progetti
        projects = load_projects()
        
        # Trova il progetto corrente
        project = next((p for p in projects if p["name"] == self.project_name and p["path"] == self.project_path), None)
        
        # Resetta lo stato master per tutti i file
        for i in range(len(self.json_files)):
            if "master" in self.json_files[i]:
                self.json_files[i]["master"] = ""
        
        # Se il progetto ha un master_file, aggiorna lo stato
        if project and "master_file" in project:
            master_file = project["master_file"]
            for i, file in enumerate(self.json_files):
                if file["path"] == master_file:
                    self.json_files[i]["master"] = "✓"
        
        # Aggiorna la grid
        self.update_files_grid()
    
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
                    file_size = os.path.getsize(file_path) / 1024  # Dimensione in KB
                    self.json_files.append({
                        "filename": file,
                        "path": file_path,
                        "size": round(file_size, 2),
                        "master": ""
                    })
        
        self.update_files_grid()
    
    def update_files_grid(self):
        # Cancella tutti gli elementi esistenti
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Aggiunge i file JSON alla grid
        for i, file in enumerate(self.json_files):
            self.tree.insert("", tk.END, values=(file["filename"], file["path"], file["size"], file["master"]), iid=str(i))
    
    def open_json_file(self, event):
        # Identifica l'elemento selezionato
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Ottiene l'indice del file selezionato
        file_index = int(item)
        file_path = self.json_files[file_index]["path"]
        
        try:
            # Carica il contenuto del file JSON
            with open(file_path, "r", encoding="utf-8") as f:
                json_content = json.load(f)
            
            # Crea una nuova finestra per visualizzare il contenuto
            json_window = tk.Toplevel(self)
            json_window.title(f"Contenuto - {self.json_files[file_index]['filename']}")
            json_window.geometry("600x400")
            
            # Crea un widget Text con scrollbar
            text_frame = tk.Frame(json_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
            
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            # Inserisce il contenuto JSON formattato
            formatted_json = json.dumps(json_content, indent=4)
            text_widget.insert(tk.END, formatted_json)
            text_widget.config(state=tk.DISABLED)  # Rende il testo di sola lettura
            
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile aprire il file: {e}")