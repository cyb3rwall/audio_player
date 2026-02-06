# Linux

## Setup venv

```bash
python3 -m venv ~/venv/mp3_player_venv
source ~/venv/mp3_player_venv/bin/activate
pip install pygame mutagen
```

## Optional module implemented solely for downloading mp3 files that you are authorized to download.
```bash
pip install yt-dlp
```

## Launch the player

```bash
python3 lecteur.py
```

## If you want to run it as an app

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
