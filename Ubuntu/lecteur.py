#!/usr/bin/env python3
"""
Lecteur Musical Simple - Application de lecture de playlists MP3
Nécessite: pygame, mutagen, tkinter
Installation: pip install pygame mutagen
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import pygame
import os
from pathlib import Path
from mutagen.mp3 import MP3
import random
import subprocess
import threading
import re

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Lecteur Musical")
        self.root.geometry("600x400")
        self.root.configure(bg='#1e1e1e')
        
        # Initialiser pygame mixer
        pygame.mixer.init()
        
        # Variables
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.song_length = 0
        self.seeking = False
        self.pause_position = 0
        self.canvas_width = 580
        self.shuffle_mode = False
        self.download_folder = os.path.expanduser("~/Musique")
        os.makedirs(self.download_folder, exist_ok=True)
        
        self.setup_ui()
        
        # Timer pour mettre à jour le curseur
        self.update_slider()
    
    def setup_ui(self):
        # Frame principale
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Titre de la chanson en cours
        self.song_label = tk.Label(
            main_frame, 
            text="Aucune chanson", 
            font=('Arial', 14, 'bold'),
            bg='#1e1e1e',
            fg='white'
        )
        self.song_label.pack(pady=(0, 10))
        
        # Listbox pour la playlist
        playlist_frame = tk.Frame(main_frame, bg='#1e1e1e')
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
        
        self.playlist_box.bind('<Double-Button-1>', self.play_selected)
        
        # Frame pour le temps
        time_frame = tk.Frame(main_frame, bg='#1e1e1e')
        time_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.time_label = tk.Label(
            time_frame,
            text="0:00 / 0:00",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#b3b3b3'
        )
        self.time_label.pack()
        
        # Frame pour le curseur personnalisé
        slider_frame = tk.Frame(main_frame, bg='#1e1e1e', height=30)
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
        
        # Bindings pour le drag
        self.slider_canvas.bind("<Button-1>", self.on_slider_click)
        self.slider_canvas.bind("<B1-Motion>", self.on_slider_drag)
        self.slider_canvas.bind("<ButtonRelease-1>", self.on_slider_release)
        self.slider_canvas.bind("<Configure>", self.on_canvas_resize)
        
        # Frame pour les boutons de contrôle
        control_frame = tk.Frame(main_frame, bg='#1e1e1e')
        control_frame.pack()
        
        # Boutons de contrôle
        btn_style = {
            'font': ('Arial', 12),
            'bg': '#1db954',
            'fg': 'white',
            'activebackground': '#1ed760',
            'bd': 0,
            'padx': 15,
            'pady': 8
        }
        
        # Bouton shuffle à gauche
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
        
        tk.Button(
            control_frame,
            text="⏮",
            command=self.previous_song,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        self.play_button = tk.Button(
            control_frame,
            text="▶",
            command=self.play_pause,
            **btn_style
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="⏭",
            command=self.next_song,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="➕ Add Playlist",
            command=self.add_folder,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="🎵 Add Music",
            command=self.add_files,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="⬇️",
            command=self.show_download_dialog,
            bg='#2196F3',
            fg='white',
            activebackground='#42A5F5',
            font=('Arial', 12),
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="🗑️ Vider",
            command=self.clear_playlist,
            bg='#d32f2f',
            fg='white',
            activebackground='#f44336',
            font=('Arial', 12),
            bd=0,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def show_download_dialog(self):
        """Afficher une boîte de dialogue pour télécharger depuis YouTube"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Télécharger depuis YouTube")
        dialog.geometry("600x300")
        dialog.configure(bg='#1e1e1e')
        dialog.transient(self.root)
        
        # Attendre que la fenêtre soit visible avant grab_set
        dialog.update_idletasks()
        dialog.grab_set()
        
        # Label
        tk.Label(
            dialog,
            text="Entrez un lien YouTube (vidéo ou playlist):",
            font=('Arial', 11),
            bg='#1e1e1e',
            fg='white'
        ).pack(pady=(20, 10))
        
        # Champ de saisie
        url_entry = tk.Entry(
            dialog,
            font=('Arial', 11),
            bg='#2d2d2d',
            fg='white',
            insertbackground='white',
            width=60
        )
        url_entry.pack(pady=10, padx=20)
        url_entry.focus()
        
        # Frame pour la progression
        progress_frame = tk.Frame(dialog, bg='#1e1e1e')
        progress_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Barre de progression
        progress_canvas = tk.Canvas(
            progress_frame,
            bg='#1e1e1e',
            height=25,
            highlightthickness=0
        )
        progress_canvas.pack(fill=tk.X)
        
        # Fond de la barre
        progress_bg = progress_canvas.create_rectangle(
            0, 8, 560, 17,
            fill='#404040',
            outline=''
        )
        
        # Barre de progression (verte)
        progress_bar = progress_canvas.create_rectangle(
            0, 8, 0, 17,
            fill='#1db954',
            outline=''
        )
        
        # Texte de pourcentage
        progress_text = progress_canvas.create_text(
            280, 12,
            text="0%",
            fill='white',
            font=('Arial', 9, 'bold')
        )
        
        # Label de statut détaillé
        status_label = tk.Label(
            dialog,
            text="",
            font=('Arial', 9),
            bg='#1e1e1e',
            fg='#b3b3b3',
            wraplength=550,
            justify=tk.LEFT
        )
        status_label.pack(pady=5, padx=20)
        
        def update_progress(percentage, status_text):
            """Mettre à jour la barre de progression"""
            width = (percentage / 100.0) * 560
            progress_canvas.coords(progress_bar, 0, 8, width, 17)
            progress_canvas.itemconfig(progress_text, text=f"{int(percentage)}%")
            status_label.config(text=status_text)
            dialog.update()
        
        # Frame pour les boutons
        btn_frame = tk.Frame(dialog, bg='#1e1e1e')
        btn_frame.pack(pady=20)
        
        def start_download():
            url = url_entry.get().strip()
            if not url:
                messagebox.showwarning("Attention", "Veuillez entrer un lien YouTube!")
                return
            
            # Désactiver le bouton pendant le téléchargement
            download_btn.config(state=tk.DISABLED, text="Téléchargement...")
            cancel_btn.config(state=tk.DISABLED)
            update_progress(0, "Initialisation du téléchargement...")
            
            # Lancer le téléchargement dans un thread séparé
            thread = threading.Thread(
                target=lambda: self.download_from_youtube(
                    url, dialog, update_progress, download_btn, cancel_btn
                )
            )
            thread.daemon = True
            thread.start()
        
        download_btn = tk.Button(
            btn_frame,
            text="Télécharger",
            command=start_download,
            bg='#1db954',
            fg='white',
            font=('Arial', 11),
            padx=20,
            pady=5,
            bd=0
        )
        download_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Annuler",
            command=dialog.destroy,
            bg='#404040',
            fg='white',
            font=('Arial', 11),
            padx=20,
            pady=5,
            bd=0
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Permettre de lancer avec Entrée
        url_entry.bind("<Return>", lambda e: start_download())
    
    def download_from_youtube(self, url, dialog, update_progress, download_btn, cancel_btn):
        """Télécharger une vidéo/playlist YouTube avec yt-dlp"""
        try:
            # Vérifier si yt-dlp est installé
            result = subprocess.run(['which', 'yt-dlp'], capture_output=True, text=True)
            if result.returncode != 0:
                self.root.after(0, lambda: messagebox.showerror(
                    "Erreur", 
                    "yt-dlp n'est pas installé!\n\nInstallez-le avec:\npip install yt-dlp\nou\nsudo apt install yt-dlp"
                ))
                self.root.after(0, lambda: download_btn.config(state=tk.NORMAL, text="Télécharger"))
                self.root.after(0, lambda: cancel_btn.config(state=tk.NORMAL))
                return
            
            # Déterminer si c'est une playlist
            is_playlist = 'list=' in url
            
            # Variables pour suivre la progression de la playlist
            total_songs = 0
            current_song = 0
            
            # Construire la commande yt-dlp
            if is_playlist:
                output_template = os.path.join(
                    self.download_folder,
                    "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"
                )
                cmd = [
                    'yt-dlp',
                    '-x',
                    '--audio-format', 'mp3',
                    '-o', output_template,
                    '--yes-playlist',
                    '--newline',
                    url
                ]
            else:
                output_template = os.path.join(
                    self.download_folder,
                    "%(title)s.%(ext)s"
                )
                cmd = [
                    'yt-dlp',
                    '-x',
                    '--audio-format', 'mp3',
                    '-o', output_template,
                    '--newline',
                    url
                ]
            
            # Exécuter yt-dlp avec suivi en temps réel
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            current_file = ""
            file_progress = 0
            
            for line in process.stdout:
                line = line.strip()
                
                # Détecter le nombre total de vidéos dans la playlist
                if '[download] Downloading item' in line:
                    # Format: [download] Downloading item 3 of 22
                    match = re.search(r'Downloading item (\d+) of (\d+)', line)
                    if match:
                        current_song = int(match.group(1))
                        total_songs = int(match.group(2))
                        self.root.after(0, lambda c=current_song, t=total_songs: 
                            update_progress(0, f"Téléchargement de la musique {c}/{t}..."))
                
                # Extraire les informations de progression du fichier
                elif '[download]' in line:
                    # Extraire le pourcentage
                    if '%' in line:
                        try:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if '%' in part:
                                    file_progress = float(part.replace('%', ''))
                                    
                                    # Calculer la progression globale pour une playlist
                                    if total_songs > 0:
                                        # Progression globale = (chansons complétées + progression actuelle) / total
                                        global_progress = ((current_song - 1 + file_progress / 100.0) / total_songs) * 100
                                        status = f"Musique {current_song}/{total_songs} : {file_progress:.1f}%"
                                    else:
                                        global_progress = file_progress
                                        status = f"Téléchargement: {file_progress:.1f}%"
                                    
                                    self.root.after(0, lambda p=global_progress, s=status: 
                                        update_progress(p, s))
                                    break
                        except:
                            pass
                    elif 'Destination:' in line:
                        current_file = line.split('Destination:')[1].strip()
                        filename = os.path.basename(current_file)
                        if total_songs > 0:
                            self.root.after(0, lambda f=filename, c=current_song, t=total_songs: 
                                update_progress(0, f"Musique {c}/{t} : {f}"))
                        else:
                            self.root.after(0, lambda f=filename: 
                                update_progress(0, f"Préparation: {f}"))
                
                elif '[ExtractAudio]' in line:
                    if total_songs > 0:
                        global_progress = ((current_song - 0.05) / total_songs) * 100
                        self.root.after(0, lambda p=global_progress, c=current_song, t=total_songs: 
                            update_progress(p, f"Musique {c}/{t} : Conversion en MP3..."))
                    else:
                        self.root.after(0, lambda: update_progress(95, "Conversion en MP3..."))
                
                elif 'Deleting original file' in line or '[Metadata]' in line:
                    if total_songs > 0 and current_song == total_songs:
                        self.root.after(0, lambda: update_progress(98, "Finalisation..."))
            
            process.wait()
            
            if process.returncode == 0:
                # Succès
                self.root.after(0, lambda: update_progress(100, "Téléchargement terminé!"))
                
                if total_songs > 0:
                    success_msg = f"Téléchargement terminé!\n{total_songs} musiques téléchargées\nFichiers sauvegardés dans:\n{self.download_folder}"
                else:
                    success_msg = f"Téléchargement terminé!\nFichiers sauvegardés dans:\n{self.download_folder}"
                
                self.root.after(0, lambda msg=success_msg: messagebox.showinfo("Succès", msg))
                self.root.after(0, dialog.destroy)
            else:
                # Erreur
                self.root.after(0, lambda: messagebox.showerror(
                    "Erreur",
                    "Erreur lors du téléchargement. Vérifiez le lien YouTube."
                ))
                self.root.after(0, lambda: download_btn.config(state=tk.NORMAL, text="Télécharger"))
                self.root.after(0, lambda: cancel_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: update_progress(0, ""))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Erreur",
                f"Erreur inattendue:\n{str(e)}"
            ))
            self.root.after(0, lambda: download_btn.config(state=tk.NORMAL, text="Télécharger"))
            self.root.after(0, lambda: cancel_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: update_progress(0, ""))
    
    def toggle_shuffle(self):
        """Activer/désactiver le mode shuffle"""
        self.shuffle_mode = not self.shuffle_mode
        
        if self.shuffle_mode:
            self.shuffle_button.config(bg='#1db954', activebackground='#1ed760')
        else:
            self.shuffle_button.config(bg='#404040', activebackground='#505050')
    
    def get_next_song_index(self):
        """Obtenir l'index de la prochaine chanson (aléatoire si shuffle activé)"""
        if not self.playlist:
            return 0
        
        if self.shuffle_mode:
            if len(self.playlist) > 1:
                possible_indices = [i for i in range(len(self.playlist)) if i != self.current_index]
                return random.choice(possible_indices)
            else:
                return 0
        else:
            return (self.current_index + 1) % len(self.playlist)
    
    def clear_playlist(self):
        pygame.mixer.music.stop()
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.song_length = 0
        
        self.playlist_box.delete(0, tk.END)
        self.song_label.config(text="Aucune chanson")
        self.time_label.config(text="0:00 / 0:00")
        self.update_slider_position(0)
        self.play_button.config(text="▶")
    
    def add_folder(self):
        folder = filedialog.askdirectory(
            title="Sélectionner un dossier contenant des MP3",
            initialdir=self.download_folder
        )
        
        if folder:
            mp3_files = []
            for file in sorted(os.listdir(folder)):
                if file.lower().endswith('.mp3'):
                    full_path = os.path.join(folder, file)
                    if full_path not in self.playlist:
                        mp3_files.append(full_path)
            
            if mp3_files:
                self.playlist.extend(mp3_files)
                
                for file in mp3_files:
                    filename = os.path.basename(file)
                    self.playlist_box.insert(tk.END, filename)
                
                if len(self.playlist) == len(mp3_files):
                    self.current_index = 0
                    self.load_song(self.current_index, autoplay=False)
            else:
                messagebox.showwarning("Attention", "Aucun fichier MP3 nouveau trouvé dans ce dossier!")
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers MP3",
            initialdir=self.download_folder,
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
        )
        
        if files:
            new_files = [f for f in files if f not in self.playlist]
            
            if new_files:
                self.playlist.extend(new_files)
                
                for file in new_files:
                    filename = os.path.basename(file)
                    self.playlist_box.insert(tk.END, filename)
                
                if len(self.playlist) == len(new_files):
                    self.current_index = 0
                    self.load_song(self.current_index, autoplay=False)
            else:
                messagebox.showinfo("Info", "Tous les fichiers sont déjà dans la playlist!")
    
    def load_song(self, index, autoplay=False):
        if 0 <= index < len(self.playlist):
            try:
                pygame.mixer.music.load(self.playlist[index])
                filename = os.path.basename(self.playlist[index])
                self.song_label.config(text=filename)
                
                try:
                    audio = MP3(self.playlist[index])
                    self.song_length = audio.info.length
                except:
                    self.song_length = 0
                
                self.update_slider_position(0)
                self.pause_position = 0
                
                self.playlist_box.selection_clear(0, tk.END)
                self.playlist_box.selection_set(index)
                self.playlist_box.see(index)
                
                if autoplay:
                    pygame.mixer.music.play()
                    self.is_playing = True
                    self.is_paused = False
                    self.pause_position = 0
                    self.play_button.config(text="⏸")
                else:
                    self.is_playing = False
                    self.is_paused = False
                    self.pause_position = 0
                    self.play_button.config(text="▶")
                
                total_time = self.format_time(self.song_length)
                self.time_label.config(text=f"0:00 / {total_time}")
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger la chanson: {e}")
    
    def play_pause(self):
        if not self.playlist:
            messagebox.showwarning("Attention", "Chargez d'abord une playlist!")
            return
        
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.play_button.config(text="⏸")
            else:
                self.pause_position = self.get_current_position()
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_button.config(text="▶")
        else:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.pause_position = 0
            self.play_button.config(text="⏸")
    
    def next_song(self):
        if self.playlist:
            self.current_index = self.get_next_song_index()
            self.load_song(self.current_index, autoplay=self.is_playing)
    
    def previous_song(self):
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.load_song(self.current_index, autoplay=self.is_playing)
    
    def play_selected(self, event):
        selection = self.playlist_box.curselection()
        if selection:
            self.current_index = selection[0]
            self.load_song(self.current_index, autoplay=True)
    
    def on_canvas_resize(self, event):
        self.canvas_width = event.width
        self.slider_canvas.coords(self.slider_bg, 0, 13, self.canvas_width, 17)
        if self.song_length > 0:
            current_pos = self.get_current_position()
            progress = (current_pos / self.song_length) * 100
            self.update_slider_position(progress)
    
    def update_slider_position(self, percentage):
        x = (percentage / 100.0) * self.canvas_width
        self.slider_canvas.coords(self.slider_progress, 0, 13, x, 17)
        self.slider_canvas.coords(self.slider_handle, x-8, 7, x+8, 23)
    
    def on_slider_click(self, event):
        self.seeking = True
        self.update_slider_from_mouse(event.x)
    
    def on_slider_drag(self, event):
        if self.seeking:
            self.update_slider_from_mouse(event.x)
    
    def update_slider_from_mouse(self, x):
        x = max(0, min(x, self.canvas_width))
        percentage = (x / self.canvas_width) * 100
        self.update_slider_position(percentage)
    
    def on_slider_release(self, event):
        if self.song_length > 0:
            x = max(0, min(event.x, self.canvas_width))
            percentage = (x / self.canvas_width) * 100
            position = (percentage / 100.0) * self.song_length
            
            was_playing = self.is_playing and not self.is_paused
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.playlist[self.current_index])
            pygame.mixer.music.play(start=position)
            
            self.is_playing = True
            self.pause_position = position
            
            if not was_playing:
                pygame.mixer.music.pause()
                self.is_paused = True
            else:
                self.is_paused = False
        
        self.seeking = False
    
    def get_current_position(self):
        if self.is_playing:
            if self.is_paused:
                return self.pause_position
            else:
                pos_ms = pygame.mixer.music.get_pos()
                if pos_ms >= 0:
                    return self.pause_position + (pos_ms / 1000.0)
        return 0
    
    def update_slider(self):
        if self.is_playing and not self.is_paused and not self.seeking:
            try:
                current_pos = self.get_current_position()
                
                if self.song_length > 0:
                    progress = (current_pos / self.song_length) * 100
                    self.update_slider_position(progress)
                
                current_time = self.format_time(current_pos)
                total_time = self.format_time(self.song_length)
                self.time_label.config(text=f"{current_time} / {total_time}")
                
                if not pygame.mixer.music.get_busy() and self.is_playing and not self.is_paused:
                    self.next_song()
                    
            except:
                pass
        
        self.root.after(50, self.update_slider)
    
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    
    # Gérer la fermeture proprement
    def on_closing():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()