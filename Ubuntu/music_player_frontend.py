#!/usr/bin/env python3
"""
Frontend du Lecteur Musical - Interface utilisateur
Utilise tkinter pour l'interface graphique
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from music_player_backend import MusicPlayerBackend


class MusicPlayerFrontend:
    """Gère l'interface utilisateur du lecteur musical"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Lecteur Musical")
        self.root.geometry("600x400")
        self.root.configure(bg='#1e1e1e')
        
        # Créer le backend
        self.backend = MusicPlayerBackend()
        
        # Variables UI
        self.seeking = False
        self.canvas_width = 580
        
        # Configurer les callbacks du backend
        self.setup_backend_callbacks()
        
        # Créer l'interface
        self.setup_ui()
        
        # Démarrer la mise à jour du slider
        self.update_slider()
    
    def setup_backend_callbacks(self):
        """Configure les callbacks pour les événements du backend"""
        self.backend.on_song_changed = self.on_song_changed
        self.backend.on_playback_state_changed = self.on_playback_state_changed
        self.backend.on_playlist_updated = self.on_playlist_updated
        self.backend.on_download_progress = self.on_download_progress
        self.backend.on_error = self.on_error
    
    # ===== Callbacks du backend =====
    
    def on_song_changed(self, filename, length, index):
        """Appelé quand la chanson change"""
        if filename:
            self.song_label.config(text=f"Playing : {filename}")
            total_time = self.backend.format_time(length)
            self.time_label.config(text=f"0:00 / {total_time}")

            # Mettre à jour la sélection dans la listbox
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(index)
            self.playlist_box.see(index)

            # Mettre à jour l'état du bouton like
            current_song = self.backend.playlist[index]
            if self.backend.is_song_liked(current_song):
                self.like_button.config(text="❤️", fg="#FF69B4")
            else:
                self.like_button.config(text="♡", fg="white")
        else:
            self.song_label.config(text="No song")
            self.time_label.config(text="0:00 / 0:00")

        self.update_slider_position(0)
    
    def on_playback_state_changed(self, is_playing, is_paused):
        """Appelé quand l'état de lecture change"""
        if is_playing and not is_paused:
            self.play_button.config(text="⏸")
        else:
            self.play_button.config(text="▶")
    
    def on_playlist_updated(self, playlist):
        """Appelé quand la playlist est mise à jour"""
        self.playlist_box.delete(0, tk.END)
        for file_path in playlist:
            filename = os.path.basename(file_path)
            self.playlist_box.insert(tk.END, filename)
    
    def on_download_progress(self, message):
        """Appelé pour afficher la progression du téléchargement"""
        if hasattr(self, 'download_status_label'):
            self.download_status_label.config(text=message)
    
    def on_error(self, error_message):
        """Appelé en cas d'erreur"""
        messagebox.showerror("Erreur", error_message)
    
    # ===== Construction de l'interface =====
    
    def setup_ui(self):
        """Construit l'interface utilisateur complète"""
        # Frame principale
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Frame pour le titre de la chanson et le bouton like
        title_frame = tk.Frame(main_frame, bg='#1e1e1e')
        title_frame.pack(pady=(0, 10), fill=tk.X)

        # Titre de la chanson en cours
        self.song_label = tk.Label(
            title_frame, 
            text="No song", 
            font=('Arial', 14, 'bold'),
            bg='#1e1e1e',
            fg='white',
            anchor='w'
        )
        self.song_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bouton cœur pour liker la chanson
        self.like_button = tk.Button(
            title_frame,
            text="♡",
            font=('Arial', 14),
            bg='#1e1e1e',
            fg='white',
            activebackground='#1e1e1e',
            activeforeground='#FF69B4',
            bd=0,
            command=self.toggle_like
        )
        self.like_button.pack(side=tk.RIGHT, padx=5)

        # Listbox pour la playlist
        self.create_playlist_box(main_frame)

        # Affichage du temps
        self.create_time_display(main_frame)

        # Curseur de progression
        self.create_progress_slider(main_frame)

        # Boutons de contrôle
        self.create_control_buttons(main_frame)

    def toggle_like(self):
        """Gère le clic sur le bouton cœur pour liker/déliker une chanson"""
        current_song = self.backend.playlist[self.backend.current_index] if self.backend.playlist else None
        if current_song:
            is_liked = self.backend.toggle_like_song(current_song)
            if is_liked:
                self.like_button.config(text="❤️", fg="#FF69B4")
            else:
                self.like_button.config(text="♡", fg="white")

    def create_playlist_box(self, parent):
        """Crée la listbox pour afficher la playlist"""
        playlist_frame = tk.Frame(parent, bg='#1e1e1e')
        playlist_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        scrollbar = tk.Scrollbar(playlist_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.playlist_box = tk.Listbox(
            playlist_frame,
            bg='#2d2d2d',
            fg='white',
            selectbackground='#1db954',
            font=('Arial', 10),
            yscrollcommand=scrollbar.set
        )
        self.playlist_box.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.playlist_box.yview)
        
        # Double-clic pour jouer
        self.playlist_box.bind('<Double-Button-1>', self.on_playlist_double_click)
    
    def create_time_display(self, parent):
        """Crée l'affichage du temps"""
        time_frame = tk.Frame(parent, bg='#1e1e1e')
        time_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.time_label = tk.Label(
            time_frame,
            text="0:00 / 0:00",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#b3b3b3'
        )
        self.time_label.pack()
    
    def create_progress_slider(self, parent):
        """Crée le curseur de progression personnalisé"""
        slider_frame = tk.Frame(parent, bg='#1e1e1e', height=30)
        slider_frame.pack(fill=tk.X, pady=(0, 20))
        slider_frame.pack_propagate(False)
        
        # Canvas pour le curseur personnalisé
        self.slider_canvas = tk.Canvas(
            slider_frame,
            bg='#1e1e1e',
            height=30,
            highlightthickness=0
        )
        self.slider_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Dessiner la barre de fond
        self.slider_bg = self.slider_canvas.create_rectangle(
            0, 13, 580, 17,
            fill='#404040',
            outline=''
        )
        
        # Barre de progression
        self.slider_progress = self.slider_canvas.create_rectangle(
            0, 13, 0, 17,
            fill='#1db954',
            outline=''
        )
        
        # Curseur rond
        self.slider_handle = self.slider_canvas.create_oval(
            -8, 7, 8, 23,
            fill='#1db954',
            outline='white',
            width=2
        )
        
        # Événements pour le drag
        self.slider_canvas.bind("<Button-1>", self.on_slider_click)
        self.slider_canvas.bind("<B1-Motion>", self.on_slider_drag)
        self.slider_canvas.bind("<ButtonRelease-1>", self.on_slider_release)
        self.slider_canvas.bind("<Configure>", self.on_canvas_resize)
    
    def create_control_buttons(self, parent):
        """Crée les boutons de contrôle"""
        control_frame = tk.Frame(parent, bg='#1e1e1e')
        control_frame.pack()
        
        # Style des boutons
        btn_style = {
            'font': ('Arial', 12),
            'bg': '#1db954',
            'fg': 'white',
            'activebackground': '#1ed760',
            'bd': 0,
            'padx': 15,
            'pady': 8
        }
        
        # Bouton shuffle
        self.shuffle_button = tk.Button(
            control_frame,
            text="🔀",
            command=self.toggle_shuffle,
            font=('Arial', 12),
            bg='#404040',
            fg='white',
            activebackground='#505050',
            bd=0,
            padx=15,
            pady=8
        )
        self.shuffle_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton précédent
        tk.Button(
            control_frame,
            text="⏮",
            command=self.backend.previous_song,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton play/pause
        self.play_button = tk.Button(
            control_frame,
            text="▶",
            command=self.backend.play_pause,
            **btn_style
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton suivant
        tk.Button(
            control_frame,
            text="⏭",
            command=self.backend.next_song,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton ajouter playlist
        tk.Button(
            control_frame,
            text="➕ Add Playlist",
            command=self.add_folder,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton ajouter musique
        tk.Button(
            control_frame,
            text="🎵 Add Music",
            command=self.add_files,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton charger musiques likées
        tk.Button(
            control_frame,
            text="❤️ Liked",
            command=self.load_liked_songs,
            bg='#E91E63',
            fg='white',
            activebackground='#F06292',
            font=('Arial', 12),
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton télécharger
        tk.Button(
            control_frame,
            text=" ⬇️ ",
            command=self.show_download_dialog,
            bg='#2196F3',
            fg='white',
            activebackground='#42A5F5',
            font=('Arial', 12),
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Bouton vider
        tk.Button(
            control_frame,
            text=" 🗑️ ",
            command=self.backend.clear_playlist,
            bg='#d32f2f',
            fg='white',
            activebackground='#f44336',
            font=('Arial', 12),
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    # ===== Gestion des événements UI =====
    
    def add_folder(self):
        """Ouvre un dialogue pour ajouter un dossier"""
        folder = filedialog.askdirectory(
            title="Sélectionner un dossier contenant des MP3",
            initialdir=self.backend.download_folder
        )
        
        if folder:
            success, message = self.backend.add_folder(folder)
            if not success:
                messagebox.showwarning("Attention", message)
    
    def add_files(self):
        """Ouvre un dialogue pour ajouter des fichiers"""
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers MP3",
            initialdir=self.backend.download_folder,
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        
        if files:
            success, message = self.backend.add_files(files)
            if not success:
                messagebox.showinfo("Info", message)
    
    def load_liked_songs(self):
        """Charge les musiques likées dans la playlist"""
        success, message = self.backend.load_liked_songs()
        if success:
            messagebox.showinfo("Musiques likées", message)
        else:
            messagebox.showwarning("Musiques likées", message)
    
    def on_playlist_double_click(self, event):
        """Gère le double-clic sur la playlist"""
        selection = self.playlist_box.curselection()
        if selection:
            self.backend.play_at_index(selection[0])

            # Mettre à jour l'état du bouton like
            current_song = self.backend.playlist[selection[0]]
            if self.backend.is_song_liked(current_song):
                self.like_button.config(text="❤️", fg="#FF69B4")
            else:
                self.like_button.config(text="♡", fg="white")
    
    def toggle_shuffle(self):
        """Active/désactive le mode shuffle"""
        shuffle_enabled = self.backend.toggle_shuffle()
        if shuffle_enabled:
            self.shuffle_button.config(bg='#1db954', activebackground='#1ed760')
        else:
            self.shuffle_button.config(bg='#404040', activebackground='#505050')
    
    # ===== Gestion du slider =====
    
    def on_canvas_resize(self, event):
        """Redimensionne le slider quand la fenêtre change"""
        self.canvas_width = event.width
        self.slider_canvas.coords(self.slider_bg, 0, 13, self.canvas_width, 17)
        
        info = self.backend.get_playback_info()
        if info['song_length'] > 0:
            progress = (info['current_position'] / info['song_length']) * 100
            self.update_slider_position(progress)
    
    def update_slider_position(self, percentage):
        """Met à jour la position visuelle du slider"""
        x = (percentage / 100.0) * self.canvas_width
        self.slider_canvas.coords(self.slider_progress, 0, 13, x, 17)
        self.slider_canvas.coords(self.slider_handle, x-8, 7, x+8, 23)
    
    def on_slider_click(self, event):
        """Gère le clic sur le slider"""
        self.seeking = True
        self.update_slider_from_mouse(event.x)
    
    def on_slider_drag(self, event):
        """Gère le glissement du slider"""
        if self.seeking:
            self.update_slider_from_mouse(event.x)
    
    def update_slider_from_mouse(self, x):
        """Met à jour le slider selon la position de la souris"""
        x = max(0, min(x, self.canvas_width))
        percentage = (x / self.canvas_width) * 100
        self.update_slider_position(percentage)
    
    def on_slider_release(self, event):
        """Gère le relâchement du slider"""
        info = self.backend.get_playback_info()
        if info['song_length'] > 0:
            x = max(0, min(event.x, self.canvas_width))
            percentage = (x / self.canvas_width) * 100
            position = (percentage / 100.0) * info['song_length']
            self.backend.seek(position)
        
        self.seeking = False
    
    def update_slider(self):
        """Met à jour le slider périodiquement"""
        info = self.backend.get_playback_info()
        
        if info['is_playing'] and not info['is_paused'] and not self.seeking:
            try:
                current_pos = info['current_position']
                song_length = info['song_length']
                
                if song_length > 0:
                    progress = (current_pos / song_length) * 100
                    self.update_slider_position(progress)
                
                current_time = self.backend.format_time(current_pos)
                total_time = self.backend.format_time(song_length)
                self.time_label.config(text=f"{current_time} / {total_time}")
                
                # Vérifier si la chanson est terminée
                if self.backend.is_song_finished():
                    self.backend.next_song()
                    
            except:
                pass
        
        self.root.after(50, self.update_slider)
    
    # ===== Dialogue de téléchargement YouTube =====
    
    def show_download_dialog(self):
        """Affiche le dialogue de téléchargement YouTube"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Télécharger depuis YouTube")
        dialog.geometry("600x300")
        dialog.configure(bg='#1e1e1e')
        dialog.transient(self.root)
        
        dialog.update_idletasks()
        
        try:
            dialog.grab_set()
        except:
            pass
        
        # Titre
        title_label = tk.Label(
            dialog,
            text="Télécharger de la musique depuis YouTube",
            font=('Arial', 14, 'bold'),
            bg='#1e1e1e',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Instructions
        instructions = tk.Label(
            dialog,
            text="Collez l'URL d'une vidéo YouTube ci-dessous:",
            font=('Arial', 10),
            bg='#1e1e1e',
            fg='#b3b3b3'
        )
        instructions.pack(pady=(0, 10))
        
        # Champ URL
        url_entry = tk.Entry(
            dialog,
            font=('Arial', 12),
            bg='#2d2d2d',
            fg='white',
            insertbackground='white'
        )
        url_entry.pack(fill=tk.X, padx=40, pady=10)
        url_entry.focus()
        
        # Label de statut
        self.download_status_label = tk.Label(
            dialog,
            text="",
            font=('Arial', 10),
            bg='#1e1e1e',
            fg='#1db954'
        )
        self.download_status_label.pack(pady=10)
        
        # Frame pour les boutons
        button_frame = tk.Frame(dialog, bg='#1e1e1e')
        button_frame.pack(pady=20)
        
        def start_download():
            url = url_entry.get().strip()
            if not url:
                messagebox.showwarning("Attention", "Veuillez entrer une URL")
                return
            
            # Vérifier yt-dlp
            if not self.backend.check_ytdlp_installed():
                response = messagebox.askyesno(
                    "Installation requise",
                    "yt-dlp n'est pas installé. Voulez-vous l'installer maintenant?"
                )
                if response:
                    self.backend.install_ytdlp()
                return
            
            # Lancer le téléchargement
            self.backend.download_from_youtube(url, self.on_download_progress)
            url_entry.delete(0, tk.END)
        
        # Bouton télécharger
        download_btn = tk.Button(
            button_frame,
            text="⬇️ Télécharger",
            command=start_download,
            font=('Arial', 12),
            bg='#2196F3',
            fg='white',
            activebackground='#42A5F5',
            bd=0,
            padx=20,
            pady=10
        )
        download_btn.pack(side=tk.LEFT, padx=5)
        
        # Bouton fermer
        close_btn = tk.Button(
            button_frame,
            text="Fermer",
            command=dialog.destroy,
            font=('Arial', 12),
            bg='#404040',
            fg='white',
            activebackground='#505050',
            bd=0,
            padx=20,
            pady=10
        )
        close_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter pour télécharger
        url_entry.bind('<Return>', lambda e: start_download())
    
    def on_closing(self):
        """Gère la fermeture de l'application"""
        self.backend.cleanup()
        self.root.destroy()


def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    app = MusicPlayerFrontend(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()