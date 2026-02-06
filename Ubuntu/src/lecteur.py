import subprocess
import sys
import os
from pathlib import Path
from music_player_frontend import main


def load_config():
    """Charge la configuration depuis le fichier config.conf"""
    config_file = Path.home() / '.cache' / 'mp3_player' / 'config.conf'
    config = {
        'YTDLP_INSTALLED': 'false'
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    # Ignorer les commentaires et lignes vides
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
        except Exception as e:
            print(f"Avertissement : Impossible de lire la configuration : {e}")
    
    return config


def check_dependencies():
    """Vérifie et met à jour les dépendances si nécessaire"""
    # Charger la configuration
    config = load_config()
    
    # Dépendances obligatoires
    dependencies = ['pygame', 'mutagen']
    
    # Ajouter yt-dlp si installé
    if config.get('YTDLP_INSTALLED', 'false').lower() == 'true':
        dependencies.append('yt-dlp')
    
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '--upgrade'] + dependencies,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("Erreur lors de la mise à jour des dépendances")


if __name__ == "__main__":
    check_dependencies()
    main()