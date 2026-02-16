# Linux

## First, clone the project into the directory of your choice. Then, you can choose between 2 methods to install the mp3 player :

### 1] Use installer.sh
```bash
chmod +x installer.sh
./installer.sh
```

### 2] You can do what the installer does yourself.

### Setup venv

```bash
python3 -m venv ~/venv/mp3_player_venv
source ~/venv/mp3_player_venv/bin/activate
pip install pygame mutagen
```

### Optional module implemented solely for downloading mp3 files that you are authorized to download.

# Avec yt-dlp
```bash
pip install yt-dlp && mkdir -p ~/.cache/mp3_player && echo -e "YTDLP_INSTALLED=true\nINSTALL_DIR=$(pwd)\nVENV_PATH=$HOME/venv/mp3_player_venv" > ~/.cache/mp3_player/config.conf
```

# Sans yt-dlp
```bash
mkdir -p ~/.cache/mp3_player && echo -e "YTDLP_INSTALLED=false\nINSTALL_DIR=$(pwd)\nVENV_PATH=$HOME/venv/mp3_player_venv" > ~/.cache/mp3_player/config.conf
``

### Launch the player

```bash
python3 lecteur.py
```

### If you want to run it as an app

```bash
nano ~/.local/share/applications/mp3-player.desktop
```

And adapt this example:

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=MP3 reader
Comment=Lecteur MP3 avec téléchargement YouTube
Exec=bash -c 'source path_to_venv/mp3_player/bin/activate && python3 path_to_lecteur.py/lecteur.py'
Icon=/home/generic_name/.local/share/icons/logo_mp3_player.png
Terminal=false
Categories=Audio;Player;
StartupNotify=true
```
