#!/usr/bin/env python
"""
Eine Anwendung für die Windows-Taskleiste, die täglich das Bing-Hintergrundbild herunterlädt
und als Desktop-Hintergrund festlegt. Bietet Optionen für manuelle Updates und Autostart.
"""
import os
import sys
import threading
import logging
import ctypes
from datetime import date
from typing import Any, Optional, cast
from pathlib import Path

# Type-Ignores helfen hier, solange die Bibliotheken keine Type-Stubs haben.

import requests  # type: ignore  # pylint: disable=import-error
from PIL import Image, ImageDraw  # type: ignore  # pylint: disable=import-error
from pystray import Icon as icon, Menu as menu, MenuItem as item  # type: ignore # pylint: disable=import-error

try:
    from win32com.client import Dispatch  # type: ignore # pylint: disable=import-error
except ImportError:
    Dispatch = None

# Logging konfigurieren

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Konstanten für die Windows API zum Setzen des Hintergrundbilds

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 3

def resource_path(relative_path: str) -> str:
    """
    Ermittelt den absoluten Pfad zu einer Ressource, funktioniert für den
    Entwicklungsmodus und für PyInstaller.
    """
    try:
        # PyInstaller erstellt einen temporären Ordner und speichert den Pfad in _MEIPASS.
        base_path: str = cast(str, sys._MEIPASS)  # type: ignore  # pylint: disable=protected-access
    except AttributeError:
        # _MEIPASS ist nicht gesetzt, wir sind im normalen Entwicklungsmodus.
        base_path: str = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class WallpaperApp:
    """
    Die Hauptklasse der Anwendung. Verwaltet das Taskleisten-Icon, Menüaktionen,
    das Herunterladen von Hintergrundbildern und den Autostart-Mechanismus.
    """
    def __init__(self) -> None:
        """Initialisiert die Anwendung, das Stop-Event und erstellt das Taskleisten-Icon."""
        self.auto_update_enabled = True
        self.auto_update_thread = None
        self.stop_event = threading.Event()
        self.icon: Any = self._create_tray_icon()

    def _create_tray_icon(self) -> Any:
        """Erstellt und konfiguriert das pystray-Icon und sein Menü."""
        try:
            image: Any = Image.open(resource_path("app.ico"))  # type: ignore
        except FileNotFoundError:
            logging.warning("Icon 'app.ico' nicht gefunden. Erzeuge Standard-Icon.")
            image = Image.new('RGB', (64, 64), 'black')  # type: ignore
        draw: Any = ImageDraw.Draw(image)
        draw.rectangle((16, 16, 48, 48), fill='white')

        # Definiert das Menü für das Symbol

        tray_menu: Any = menu(
            item('Jetzt aktualisieren', self.update_wallpaper),
            item(
                'Automatisch alle 24h',
                self.toggle_auto_update,
                checked=lambda _item: self.auto_update_enabled  # type: ignore
            ),
            item(
                'Beim Systemstart ausführen',
                self.toggle_autostart,
                checked=lambda _item: os.path.exists(self._get_autostart_shortcut_path())  # type: ignore
            ),
            menu.SEPARATOR,  # type: ignore
            item('Beenden', self.exit_app),
        )
        return icon('BingWallpaper', image, "Bing Wallpaper", tray_menu)  # type: ignore

    def get_bing_wallpaper(self) -> Optional[str]:
        """Lädt das aktuelle Bing-Tagesbild herunter und speichert es."""
        try:

            # Bing API für das Tagesbild

            api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=de-DE"
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()  # Löst einen Fehler bei HTTP-Fehlercodes aus
            data = response.json()
            image_url = "https://www.bing.com" + data["images"][0]["url"]

            # Speicherpfad vorbereiten

            folder = Path.home() / "Pictures" / "BingWallpaper"
            folder.mkdir(parents=True, exist_ok=True)
            filename = folder / f"bing_{date.today().isoformat()}.jpg"

            # Nur speichern, wenn noch nicht vorhanden

            if not filename.exists():
                logging.info("Lade neues Bild herunter von: %s", image_url)
                img_response = requests.get(image_url, timeout=10)
                img_response.raise_for_status()
                with open(filename, "wb") as f:
                    f.write(img_response.content)
                logging.info("Hintergrundbild heruntergeladen und gespeichert: %s", filename)
            else:
                logging.info("Heutiges Bild bereits vorhanden.")

            return str(filename)
        except requests.exceptions.RequestException as e:
            logging.error("Netzwerkfehler beim Herunterladen des Bildes: %s", e)
            return None
        except (KeyError, IndexError) as e:
            logging.error("Fehler beim Verarbeiten der API-Antwort: %s", e)
            return None

    def set_wallpaper(self, image_path: Optional[str]) -> None:
        """Setzt das angegebene Bild als Desktop-Hintergrund."""
        if image_path and os.path.exists(image_path):

            # Desktop-Hintergrund mit Windows-API ändern

            ctypes.windll.user32.SystemParametersInfoW(
                SPI_SETDESKWALLPAPER, 0, image_path, SPIF_UPDATEINIFILE
                )
            logging.info("Hintergrundbild gesetzt: %s", image_path)

    def update_wallpaper(self, _icon: Any = None, _item: Any = None) -> None:
        """Startet den Prozess zum Aktualisieren des Hintergrundbildes."""
        logging.info("Starte Update des Hintergrundbildes...")
        image_path = self.get_bing_wallpaper()
        self.set_wallpaper(image_path)

    def auto_update_loop(self) -> None:
        """Diese Schleife läuft im Hintergrund und führt alle 24 Stunden ein Update aus."""
        while not self.stop_event.is_set():
            self.update_wallpaper()

            # Warte 24 Stunden (86400 Sekunden), aber prüfe alle 60 Sekunden,
            # ob das Programm beendet werden soll.

            self.stop_event.wait(timeout=24 * 60 * 60) # 24 Stunden

    def toggle_auto_update(self, _icon: Any, _item: Any) -> None:
        """Aktiviert oder deaktiviert das automatische tägliche Update."""
        self.auto_update_enabled = not self.auto_update_enabled
        if self.auto_update_enabled:
            self.start_auto_update_thread()
            logging.info("Automatisches Update aktiviert.")
        else:
            self.stop_auto_update_thread()
            logging.info("Automatisches Update deaktiviert.")

    def _get_autostart_shortcut_path(self) -> str:
        """Gibt den vollständigen Pfad zur Verknüpfungsdatei im Autostart-Ordner zurück."""
        startup_folder = os.path.expandvars(
            r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
            )
        return os.path.join(startup_folder, "BingWallpaper.lnk")

    def toggle_autostart(self, _icon: Any, _item: Any) -> None:
        """Erstellt oder löscht die Verknüpfung im Autostart-Ordner."""
        shortcut_path = self._get_autostart_shortcut_path()

        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            logging.info("Autostart deaktiviert: Verknüpfung entfernt.")
        else:
            if Dispatch is None:
                logging.error(
                    "pywin32 nicht installiert. Kann Autostart-Verknüpfung nicht erstellen."
                )
                return

            try:
                shell = Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)

                if getattr(sys, 'frozen', False):
                    shortcut.TargetPath = sys.executable
                else:
                    shortcut.TargetPath = 'py.exe'
                    shortcut.Arguments = f'"{os.path.abspath(__file__)}"'

                shortcut.save()
                logging.info("Autostart aktiviert: Verknüpfung erstellt in %s", shortcut_path)
            except OSError as e:
                logging.error("Fehler beim Speichern der Autostart-Verknüpfung: %s", e)
            except (AttributeError, TypeError) as e:
                logging.error("Fehler bei der COM-Interaktion mit WScript.Shell: %s", e)
    def start_auto_update_thread(self) -> None:
        """Startet den Hintergrundthread für automatische Updates, falls er nicht bereits läuft."""
        if self.auto_update_thread is None or not self.auto_update_thread.is_alive():
            self.stop_event.clear()
            self.auto_update_thread = threading.Thread(target=self.auto_update_loop, daemon=True)
            self.auto_update_thread.start()

    def stop_auto_update_thread(self) -> None:
        """Signalisiert dem Hintergrundthread, dass er sich beenden soll."""
        self.stop_event.set()

    def exit_app(self, _icon: Any, _item: Any) -> None:
        """Beendet die Anwendung sauber."""
        self.stop_auto_update_thread()
        self.icon.stop()

    def run(self) -> None:
        """Startet die Anwendung und das Taskleisten-Icon."""
        self.start_auto_update_thread()
        self.icon.run()

if __name__ == "__main__":

    # Haupt-Einstiegspunkt des Skripts.

    app = WallpaperApp()
    app.run()
