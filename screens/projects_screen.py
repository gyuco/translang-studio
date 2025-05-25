import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import platform
from shared.utils import load_projects, save_projects
from screens.json_files_screen import JsonFilesScreen

class ProjectsScreen(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.projects = []
        
        self.create_widgets()
        self.load_projects()
    
    def create_widgets(self):
        # Frame per i controlli
        self.controls_frame = tk.Frame(self)
        self.controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Titolo
        self.title_label = tk.Label(self.controls_frame, text="Progetti", font=("Helvetica", 16))
        self.title_label.pack(side=tk.LEFT, padx=5)
        
        # Pulsante per aggiungere un nuovo progetto
        self.add_button = tk.Button(self.controls_frame, text="Nuovo Progetto", command=self.show_add_project)
        self.add_button.pack(side=tk.RIGHT, padx=5)
        
        # Frame per la grid dei progetti
        self.projects_frame = tk.Frame(self)
        self.projects_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Creazione della grid con Treeview
        self.tree = ttk.Treeview(self.projects_frame, columns=("name", "path"), show="headings")
        self.tree.heading("name", text="Nome Progetto")
        self.tree.heading("path", text="Percorso")
        self.tree.column("name", width=200)
        self.tree.column("path", width=400)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.projects_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        
        # Binding per il menu contestuale - approccio specifico per sistema operativo
        if platform.system() == "Darwin":  # macOS
            self.tree.bind("<Button-2>", self.show_context_menu)  # Click centrale su macOS
            self.tree.bind("<Control-Button-1>", self.show_context_menu)  # Control+click su macOS
        else:  # Windows/Linux
            self.tree.bind("<Button-3>", self.show_context_menu)  # Tasto destro standard
        
        # Rimuovo il binding per il doppio click
        # self.tree.bind("<Double-1>", self.open_json_files_screen)
        
        # Frame per aggiungere/modificare progetti (inizialmente nascosto)
        self.edit_frame = tk.Frame(self)
        
        # Campi per nome e percorso
        tk.Label(self.edit_frame, text="Nome Progetto:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = tk.Entry(self.edit_frame, width=40)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Frame per il percorso con entry e pulsante
        tk.Label(self.edit_frame, text="Percorso:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.path_frame = tk.Frame(self.edit_frame)
        self.path_frame.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        self.path_entry = tk.Entry(self.path_frame, width=32)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = tk.Button(self.path_frame, text="Sfoglia", command=self.browse_directory)
        self.browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Pulsanti per salvare e annullare
        self.buttons_frame = tk.Frame(self.edit_frame)
        self.buttons_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.save_button = tk.Button(self.buttons_frame, text="Salva", command=self.save_project)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.cancel_button = tk.Button(self.buttons_frame, text="Annulla", command=self.hide_edit_frame)
        self.cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Variabile per tenere traccia dell'ID del progetto in fase di modifica
        self.editing_id = None
    
    def browse_directory(self):
        # Apre il selettore di directory
        directory = filedialog.askdirectory(title="Seleziona Directory")
        if directory:
            # Aggiorna il campo di testo con il percorso selezionato
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, directory)
    
    def load_projects(self):
        self.projects = load_projects()
        self.update_projects_grid()
    
    def update_projects_grid(self):
        # Cancella tutti gli elementi esistenti
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Aggiunge i progetti alla grid
        for project in self.projects:
            self.tree.insert("", tk.END, values=(project["name"], project["path"]), iid=str(project["id"]))
    
    def show_context_menu(self, event):
        # Identifica l'elemento selezionato
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Seleziona l'elemento
        self.tree.selection_set(item)
        self.tree.focus(item)  # Imposta anche il focus sull'elemento selezionato
        
        # Crea il menu contestuale
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Mostra Files", command=lambda: self.open_json_files_screen(item))
        context_menu.add_command(label="Modifica", command=lambda: self.show_edit_project(item))
        context_menu.add_command(label="Elimina", command=lambda: self.delete_project(item))
        
        # Mostra il menu contestuale
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()  # Assicura che il menu rilasci il controllo quando viene chiuso
    
    def show_add_project(self):
        # Resetta i campi
        self.name_entry.delete(0, tk.END)
        self.path_entry.delete(0, tk.END)
        
        # Resetta l'ID in modifica
        self.editing_id = None
        
        # Mostra il frame di modifica
        self.edit_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def show_edit_project(self, item_id):
        # Trova il progetto selezionato
        project_id = int(item_id)
        project = next((p for p in self.projects if p["id"] == project_id), None)
        
        if project:
            # Imposta i valori nei campi
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, project["name"])
            
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, project["path"])
            
            # Imposta l'ID in modifica
            self.editing_id = project_id
            
            # Mostra il frame di modifica
            self.edit_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def hide_edit_frame(self):
        # Nasconde il frame di modifica
        self.edit_frame.pack_forget()
    
    def save_project(self):
        name = self.name_entry.get().strip()
        path = self.path_entry.get().strip()
        
        if not name or not path:
            messagebox.showerror("Errore", "Nome e percorso sono obbligatori")
            return
        
        if self.editing_id is None:
            # Aggiunge un nuovo progetto
            new_id = 1
            if self.projects:
                new_id = max(p["id"] for p in self.projects) + 1
            
            self.projects.append({
                "id": new_id,
                "name": name,
                "path": path
            })
        else:
            # Modifica un progetto esistente
            for project in self.projects:
                if project["id"] == self.editing_id:
                    project["name"] = name
                    project["path"] = path
                    break
        
        # Salva i progetti
        save_projects(self.projects)
        
        # Aggiorna la grid
        self.update_projects_grid()
        
        # Nasconde il frame di modifica
        self.hide_edit_frame()
    
    def delete_project(self, item_id):
        # Chiede conferma
        if not messagebox.askyesno("Conferma", "Sei sicuro di voler eliminare questo progetto?"):
            return
        
        # Elimina il progetto
        project_id = int(item_id)
        self.projects = [p for p in self.projects if p["id"] != project_id]
        
        # Salva i progetti
        save_projects(self.projects)
        
        # Aggiorna la grid
        self.update_projects_grid()
    
    def open_json_files_screen(self, item):
        # Modifica la funzione per accettare direttamente l'item invece dell'evento
        if not item:
            return
        
        # Trova il progetto selezionato
        project_id = int(item)
        project = next((p for p in self.projects if p["id"] == project_id), None)
        
        if project:
            # Apre la schermata dei file JSON
            JsonFilesScreen(self.master, project["name"], project["path"])