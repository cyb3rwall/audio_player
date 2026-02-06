#!/bin/bash

# Fichier de configuration
CONFIG_FILE="$HOME/.cache/mp3_player/config.conf"

# Charger la configuration
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    echo "Erreur: Fichier de configuration non trouvé"
    exit 1
fi

# Activer l'environnement virtuel
source "$VENV_PATH/bin/activate"

# Vérifier et mettre à jour les dépendances obligatoires (silencieusement)
pip install --upgrade pygame mutagen > /dev/null 2>&1

# Vérifier et mettre à jour yt-dlp si installé
if [ "$YTDLP_INSTALLED" = "true" ]; then
    pip install --upgrade yt-dlp > /dev/null 2>&1
fi

# Lancer l'application
python3 "$INSTALL_DIR/src/lecteur.py"
