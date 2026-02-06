#!/bin/bash

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_step() {
    echo -e "${BLUE}[ÉTAPE]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Fonction pour gérer les erreurs
handle_error() {
    print_error "$1"
    print_error "Installation interrompue."
    exit 1
}

# Bannière
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          INSTALLATEUR MP3 PLAYER                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ÉTAPE 0 : Informer l'utilisateur
print_info "Cet installateur va effectuer les actions suivantes :"
echo "  1. Créer un environnement virtuel Python dans ~/venv/mp3_player_venv"
echo "  2. Installer les dépendances nécessaires (pygame, mutagen)"
echo "  3. Proposer l'installation optionnelle de yt-dlp"
echo "  4. Créer un lanceur d'application (.desktop)"
echo ""
read -p "Voulez-vous continuer ? (o/n) : " confirm
if [[ ! "$confirm" =~ ^[oO]$ ]]; then
    print_info "Installation annulée par l'utilisateur."
    exit 0
fi
echo ""

# Vérifier que Python3 est installé
print_step "Vérification de Python3..."
if ! command -v python3 &> /dev/null; then
    handle_error "Python3 n'est pas installé. Veuillez l'installer d'abord."
fi
PYTHON_VERSION=$(python3 --version)
print_success "Python3 détecté : $PYTHON_VERSION"
echo ""

# ÉTAPE 1 : Créer l'environnement virtuel
print_step "Création de l'environnement virtuel dans ~/venv/mp3_player_venv..."
if [ -d "$HOME/venv/mp3_player_venv" ]; then
    print_info "L'environnement virtuel existe déjà."
    read -p "Voulez-vous le recréer ? (o/n) : " recreate
    if [[ "$recreate" =~ ^[oO]$ ]]; then
        rm -rf "$HOME/venv/mp3_player_venv" || handle_error "Impossible de supprimer l'ancien environnement virtuel"
        python3 -m venv "$HOME/venv/mp3_player_venv" || handle_error "Échec de la création de l'environnement virtuel"
        print_success "Environnement virtuel recréé"
    else
        print_success "Utilisation de l'environnement virtuel existant"
    fi
else
    mkdir -p "$HOME/venv" || handle_error "Impossible de créer le répertoire ~/venv"
    python3 -m venv "$HOME/venv/mp3_player_venv" || handle_error "Échec de la création de l'environnement virtuel"
    print_success "Environnement virtuel créé"
fi
echo ""

# Activer l'environnement virtuel
print_step "Activation de l'environnement virtuel..."
source "$HOME/venv/mp3_player_venv/bin/activate" || handle_error "Impossible d'activer l'environnement virtuel"
print_success "Environnement virtuel activé"
echo ""

# ÉTAPE 2 : Installer les modules nécessaires
print_step "Installation des dépendances obligatoires (pygame, mutagen)..."
print_info "Cela peut prendre quelques minutes..."
pip install --upgrade pip > /dev/null 2>&1
pip install pygame mutagen || handle_error "Échec de l'installation des dépendances obligatoires"
print_success "pygame et mutagen installés avec succès"
echo ""

# ÉTAPE 3 : Proposition d'installer yt-dlp
print_step "Installation optionnelle de yt-dlp..."
print_info "yt-dlp permet de télécharger des fichiers MP3 (uniquement ceux que vous êtes autorisé à télécharger)"
read -p "Voulez-vous installer yt-dlp ? (o/n) : " install_ytdlp
if [[ "$install_ytdlp" =~ ^[oO]$ ]]; then
    pip install yt-dlp || handle_error "Échec de l'installation de yt-dlp"
    print_success "yt-dlp installé avec succès"
else
    print_info "Installation de yt-dlp ignorée"
fi
echo ""

# ÉTAPE 4 : Récupérer le chemin absolu du répertoire courant
print_step "Récupération du chemin d'installation..."
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_success "Chemin d'installation : $INSTALL_DIR"
echo ""

# Vérifier que lecteur.py existe
if [ ! -f "$INSTALL_DIR/src/lecteur.py" ]; then
    handle_error "Le fichier lecteur.py n'a pas été trouvé dans $INSTALL_DIR/src/"
fi

# Vérifier que l'icône existe (optionnel)
ICON_PATH="$INSTALL_DIR/icons/logo_mp3_player.png"
if [ ! -f "$ICON_PATH" ]; then
    print_info "L'icône n'a pas été trouvée dans $ICON_PATH"
    print_info "Le lanceur sera créé sans icône"
    ICON_PATH=""
fi

# ÉTAPE 5 : Créer le fichier .desktop
print_step "Création du lanceur d'application..."
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/mp3-player.desktop"

# Créer le répertoire si nécessaire
mkdir -p "$DESKTOP_DIR" || handle_error "Impossible de créer le répertoire $DESKTOP_DIR"

# Créer le fichier .desktop
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=MP3 Player
Comment=MP3 player with essential features and without trackers
Exec=bash -c 'source $HOME/venv/mp3_player_venv/bin/activate && python3 $INSTALL_DIR/src/lecteur.py'
Icon=$ICON_PATH
Terminal=false
Categories=Audio;Player;
StartupNotify=true
EOF

if [ $? -ne 0 ]; then
    handle_error "Échec de la création du fichier .desktop"
fi

# Rendre le fichier .desktop exécutable
chmod +x "$DESKTOP_FILE" || handle_error "Impossible de rendre le lanceur exécutable"
print_success "Lanceur créé : $DESKTOP_FILE"
echo ""

# Actualiser le cache des applications
print_step "Actualisation du cache des applications..."
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null
    print_success "Cache des applications actualisé"
else
    print_info "update-desktop-database non disponible, le lanceur sera visible au prochain redémarrage"
fi

# Actualiser le cache des icônes (si gtk-update-icon-cache est disponible)
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t ~/.local/share/icons 2>/dev/null || true
fi
echo ""

# Désactiver l'environnement virtuel
deactivate

# Message final
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          INSTALLATION TERMINÉE AVEC SUCCÈS !               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
print_success "Vous pouvez maintenant :"
echo "  • Chercher 'MP3 Player' dans votre menu d'applications"
echo "  • Ou lancer manuellement avec :"
echo "    source ~/venv/mp3_player_venv/bin/activate && python3 $INSTALL_DIR/src/lecteur.py"
echo ""
print_info "Pour désinstaller, supprimez simplement :"
echo "  • L'environnement virtuel : rm -r ~/venv/mp3_player_venv"
echo "  • Le lanceur : rm $DESKTOP_FILE"
echo ""
