#!/usr/bin/env python3
"""
Backend du Lecteur Musical
Gère la lecture audio, la playlist et les téléchargements
"""

import pygame
import os
from pathlib import Path
from mutagen.mp3 import MP3
import random
import subprocess
import threading
import re
import json


class MusicPlayerBackend:
    """Gère toute la logique  du lecteur musical"""
    
    def __init__(self):
        # Initialiser pygame mixer
        pygame.mixer.init()
        
        # Variables d'état
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.song_length = 0
        self.pause_position = 0
        self.shuffle_mode = False
        self.download_folder = os.path.expanduser("~/Musique")
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Gestion des musiques likées
        self.liked_songs = []
        self.liked_songs_file = os.path.expanduser("~/.cache/mp3_player/liked_list.json")
        self._load_liked_songs()
        
        # Callbacks pour notifier le frontend
        self.on_song_changed = None
        self.on_playback_state_changed = None
        self.on_playlist_updated = None
        self.on_download_progress = None
        self.on_error = None
    
    # ===== Gestion de la playlist =====
    
    def add_folder(self, folder_path):
        """Ajoute tous les MP3 d'un dossier à la playlist"""
        if not folder_path or not os.path.exists(folder_path):
            return False, "Dossier invalide"
        
        mp3_files = []
        for file in sorted(os.listdir(folder_path)):
            if file.lower().endswith('.mp3'):
                full_path = os.path.join(folder_path, file)
                if full_path not in self.playlist:
                    mp3_files.append(full_path)
        
        if mp3_files:
            self.playlist.extend(mp3_files)
            if self.on_playlist_updated:
                self.on_playlist_updated(self.playlist)
            
            if len(self.playlist) == len(mp3_files):
                self.current_index = 0
                self.load_song(self.current_index, autoplay=False)
            
            return True, f"{len(mp3_files)} fichiers ajoutés"
        
        return False, "Aucun fichier MP3 nouveau trouvé"
    
    def add_files(self, file_paths):
        """Ajoute des fichiers MP3 spécifiques à la playlist"""
        if not file_paths:
            return False, "Aucun fichier sélectionné"
        
        new_files = [f for f in file_paths if f not in self.playlist]
        
        if new_files:
            self.playlist.extend(new_files)
            if self.on_playlist_updated:
                self.on_playlist_updated(self.playlist)
            
            if len(self.playlist) == len(new_files):
                self.current_index = 0
                self.load_song(self.current_index, autoplay=False)
            
            return True, f"{len(new_files)} fichiers ajoutés"
        
        return False, "Tous les fichiers sont déjà dans la playlist"
    
    def clear_playlist(self):
        """Vide complètement la playlist"""
        pygame.mixer.music.stop()
        self.playlist = []
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.song_length = 0
        self.pause_position = 0
        
        if self.on_playlist_updated:
            self.on_playlist_updated(self.playlist)
        if self.on_song_changed:
            self.on_song_changed(None, 0, 0)
        if self.on_playback_state_changed:
            self.on_playback_state_changed(False, False)
    
    def _load_liked_songs(self):
        """Charge la liste des musiques likées depuis le fichier JSON"""
        try:
            if os.path.exists(self.liked_songs_file):
                with open(self.liked_songs_file, 'r', encoding='utf-8') as f:
                    self.liked_songs = json.load(f)
        except Exception as e:
            print(f"Erreur lors du chargement des musiques likées: {e}")
            self.liked_songs = []
    
    def load_liked_songs(self):
        """Charge les musiques likées dans la playlist (depuis la liste en mémoire)"""
        if not self.liked_songs:
            return False, "Aucune musique likée trouvée"
        
        # Vérifier quels fichiers existent encore
        existing_files = [f for f in self.liked_songs if os.path.exists(f)]
        
        if not existing_files:
            return False, "Aucun fichier MP3 liké n'existe plus sur le disque"
        
        # Ajouter uniquement les fichiers qui ne sont pas déjà dans la playlist
        new_files = [f for f in existing_files if f not in self.playlist]
        
        if new_files:
            self.playlist.extend(new_files)
            if self.on_playlist_updated:
                self.on_playlist_updated(self.playlist)
            
            if len(self.playlist) == len(new_files):
                self.current_index = 0
                self.load_song(self.current_index, autoplay=False)
            
            return True, f"{len(new_files)} musiques likées ajoutées"
        
        return False, "Toutes les musiques likées sont déjà dans la playlist"
    
    def _save_liked_songs(self):
        """Sauvegarde la liste des musiques likées dans le fichier JSON"""
        try:
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(self.liked_songs_file), exist_ok=True)
            with open(self.liked_songs_file, 'w', encoding='utf-8') as f:
                json.dump(self.liked_songs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des musiques likées: {e}")
    
    # ===== Gestion de la lecture =====
    
    def load_song(self, index, autoplay=False):
        """Charge une chanson à un index donné"""
        if not (0 <= index < len(self.playlist)):
            return False, "Index invalide"
        
        try:
            pygame.mixer.music.load(self.playlist[index])
            filename = os.path.basename(self.playlist[index])
            
            # Obtenir la durée
            try:
                audio = MP3(self.playlist[index])
                self.song_length = audio.info.length
            except:
                self.song_length = 0
            
            self.pause_position = 0
            
            if autoplay:
                pygame.mixer.music.play()
                self.is_playing = True
                self.is_paused = False
            else:
                self.is_playing = False
                self.is_paused = False
            
            # Notifier le frontend
            if self.on_song_changed:
                self.on_song_changed(filename, self.song_length, index)
            if self.on_playback_state_changed:
                self.on_playback_state_changed(self.is_playing, self.is_paused)
            
            return True, filename
            
        except Exception as e:
            if self.on_error:
                self.on_error(f"Impossible de charger la chanson: {e}")
            return False, str(e)
    
    def play_pause(self):
        """Bascule entre lecture et pause"""
        if not self.playlist:
            if self.on_error:
                self.on_error("Chargez d'abord une playlist!")
            return False
        
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
            else:
                self.pause_position = self.get_current_position()
                pygame.mixer.music.pause()
                self.is_paused = True
        else:
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.pause_position = 0
        
        if self.on_playback_state_changed:
            self.on_playback_state_changed(self.is_playing, self.is_paused)
        
        return True
    
    def next_song(self):
        """Passe à la chanson suivante"""
        if self.playlist:
            self.current_index = self.get_next_song_index()
            self.load_song(self.current_index, autoplay=self.is_playing)
    
    def previous_song(self):
        """Retourne à la chanson précédente"""
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            self.load_song(self.current_index, autoplay=self.is_playing)
    
    def play_at_index(self, index):
        """Joue une chanson à un index spécifique"""
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self.load_song(self.current_index, autoplay=True)
    
    def seek(self, position_seconds):
        """Se déplace à une position spécifique dans la chanson"""
        if self.song_length > 0 and 0 <= position_seconds <= self.song_length:
            was_playing = self.is_playing and not self.is_paused
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.playlist[self.current_index])
            pygame.mixer.music.play(start=position_seconds)
            
            self.is_playing = True
            self.pause_position = position_seconds
            
            if not was_playing:
                pygame.mixer.music.pause()
                self.is_paused = True
            else:
                self.is_paused = False
            
            return True
        return False
    
    # ===== Mode shuffle =====
    
    def toggle_shuffle(self):
        """Active/désactive le mode aléatoire"""
        self.shuffle_mode = not self.shuffle_mode
        return self.shuffle_mode
    
    def get_next_song_index(self):
        """Obtient l'index de la prochaine chanson (avec shuffle si activé)"""
        if self.shuffle_mode:
            if len(self.playlist) > 1:
                possible_indices = [i for i in range(len(self.playlist)) if i != self.current_index]
                return random.choice(possible_indices)
            return 0
        else:
            return (self.current_index + 1) % len(self.playlist)
    
    # ===== Informations sur la lecture =====
    
    def get_current_position(self):
        """Obtient la position actuelle dans la chanson (en secondes)"""
        if self.is_playing:
            if self.is_paused:
                return self.pause_position
            else:
                pos_ms = pygame.mixer.music.get_pos()
                if pos_ms >= 0:
                    return self.pause_position + (pos_ms / 1000.0)
        return 0
    
    def is_song_finished(self):
        """Vérifie si la chanson actuelle est terminée"""
        return not pygame.mixer.music.get_busy() and self.is_playing and not self.is_paused
    
    def get_playlist_info(self):
        """Retourne les informations de la playlist"""
        return {
            'playlist': self.playlist,
            'current_index': self.current_index,
            'total_songs': len(self.playlist)
        }
    
    def get_playback_info(self):
        """Retourne les informations de lecture"""
        return {
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'current_position': self.get_current_position(),
            'song_length': self.song_length,
            'shuffle_mode': self.shuffle_mode
        }
    
    # ===== Téléchargement YouTube =====
    
    def check_ytdlp_installed(self):
        """Vérifie si yt-dlp est installé"""
        try:
            subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def install_ytdlp(self):
        """Installe yt-dlp via pip"""
        def install():
            try:
                subprocess.run(
                    ['pip', 'install', '--user', 'yt-dlp'],
                    capture_output=True,
                    check=True
                )
                if self.on_download_progress:
                    self.on_download_progress("✓ yt-dlp installé avec succès!")
            except subprocess.CalledProcessError as e:
                if self.on_error:
                    self.on_error(f"Erreur lors de l'installation: {e}")
        
        thread = threading.Thread(target=install, daemon=True)
        thread.start()
    
    def download_from_youtube(self, url, progress_callback=None):
        """Télécharge une vidéo YouTube en MP3"""
        def download():
            try:
                if progress_callback:
                    progress_callback("🔄 Démarrage du téléchargement...")
                
                # Extraire l'ID de la vidéo
                video_id = self._extract_video_id(url)
                if not video_id:
                    if self.on_error:
                        self.on_error("URL YouTube invalide")
                    return
                
                # Obtenir le titre
                if progress_callback:
                    progress_callback("📝 Récupération des informations...")
                
                title = self._get_video_title(url)
                safe_title = self._sanitize_filename(title)
                output_file = os.path.join(self.download_folder, f"{safe_title}.mp3")
                
                if progress_callback:
                    progress_callback(f"⬇️ Téléchargement de '{safe_title}'...")
                
                # Télécharger
                cmd = [
                    'yt-dlp',
                    '-x',
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',
                    '-o', output_file,
                    url
                ]
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if os.path.exists(output_file):
                    if progress_callback:
                        progress_callback(f"✓ Téléchargé: {safe_title}")
                    
                    # Ajouter à la playlist
                    if output_file not in self.playlist:
                        self.playlist.append(output_file)
                        if self.on_playlist_updated:
                            self.on_playlist_updated(self.playlist)
                        
                        if len(self.playlist) == 1:
                            self.current_index = 0
                            self.load_song(0, autoplay=False)
                else:
                    if self.on_error:
                        self.on_error("Le fichier téléchargé n'a pas été trouvé")
                
            except subprocess.CalledProcessError as e:
                if self.on_error:
                    self.on_error(f"Erreur de téléchargement: {e.stderr}")
            except Exception as e:
                if self.on_error:
                    self.on_error(f"Erreur: {str(e)}")
        
        thread = threading.Thread(target=download, daemon=True)
        thread.start()
    
    def _extract_video_id(self, url):
        """Extrait l'ID d'une vidéo YouTube depuis l'URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/)([^&\s]+)',
            r'youtube\.com/embed/([^&\s]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    
    def _get_video_title(self, url):
        """Récupère le titre d'une vidéo YouTube"""
        try:
            result = subprocess.run(
                ['yt-dlp', '--get-title', url],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "video"
    
    def _sanitize_filename(self, filename):
        """Nettoie un nom de fichier"""
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip()
        return filename[:200]
    
    # ===== Nettoyage =====
    
    def _load_liked_songs(self):
        """Charge la liste des musiques likées depuis le fichier"""
        if os.path.exists(self.liked_songs_file):
            try:
                with open(self.liked_songs_file, 'r', encoding='utf-8') as file:
                    self.liked_songs = json.load(file)
            except (json.JSONDecodeError, IOError):
                self.liked_songs = []

    def toggle_like_song(self, song_path):
        """Ajoute ou retire une musique de la liste des musiques likées"""
        if song_path in self.liked_songs:
            self.liked_songs.remove(song_path)
            return False  # Déliké
        else:
            self.liked_songs.append(song_path)
            return True  # Liké

    def is_song_liked(self, song_path):
        """Vérifie si une musique est likée"""
        return song_path in self.liked_songs

    def cleanup(self):
        """Nettoie les ressources et sauvegarde les données"""
        self._save_liked_songs()
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    
    @staticmethod
    def format_time(seconds):
        """Formate un temps en secondes en MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}:{secs:02d}"