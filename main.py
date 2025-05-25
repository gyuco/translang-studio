import os
import tkinter as tk
from screens.projects_screen import ProjectsScreen

class TranslangStudio(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Translang Studio")
        self.geometry("800x600")
        
        # Assicurati che la directory data esista
        os.makedirs("data", exist_ok=True)
        
        # Carica la schermata principale
        self.projects_screen = ProjectsScreen(self)
        self.projects_screen.pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    app = TranslangStudio()
    app.mainloop()