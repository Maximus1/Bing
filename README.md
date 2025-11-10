# Bing Wallpaper für Windows

Ein einfaches Python-Skript, das täglich das aktuelle Bing-Bild des Tages als Desktophintergrund für Windows festlegt. Die Anwendung läuft unauffällig im System-Tray (Infobereich der Taskleiste) und bietet grundlegende Steuerungsoptionen.

## ✨ Funktionen

#### Tägliche automatische Updates: 
Holt einmal alle 24 Stunden automatisch das neueste Bing-Hintergrundbild und legt es als Desktop-Hintergrund fest.

#### Manuelles Update: 
Über das Tray-Menü kann das Hintergrundbild jederzeit manuell aktualisiert werden.

#### Lokale Speicherung: 
Speichert die heruntergeladenen Bilder im Ordner C:\Benutzer\<DeinName>\Bilder\BingWallpaper, um eine Sammlung der täglichen Bilder anzulegen.

#### System-Tray-Integration: 
Bietet ein Menü für einfache Steuerung:

#### Jetzt aktualisieren: 
Startet sofort den Download und die Aktualisierung.

#### Automatisch alle 24h: 
Aktiviert oder deaktiviert die automatische Aktualisierung.

#### Beenden: 
Schließt die Anwendung.

#### Effizient: 
Prüft, ob das Bild des Tages bereits heruntergeladen wurde, um unnötige Downloads zu vermeiden.

#### Keine aufdringliche Benutzeroberfläche: 
Läuft komplett im Hintergrund und wird nur über das Icon im Infobereich gesteuert.

## 🚀 Installation und Ausführung

1. Voraussetzungen
- Python 3.x
- Windows-Betriebssystem

2. Abhängigkeiten installieren
- Öffne eine Kommandozeile (CMD oder PowerShell) und installiere die benötigten Python-Pakete:

````bash
pip install requests Pillow pystray
````
3. Skript ausführen
Führe das Skript einfach über die Kommandozeile aus. Es erscheint ein Icon im System-Tray.

````bash
python bing.py
````

## 📦 Erstellen einer eigenständigen .exe-Datei (Optional)

Um das Skript als eigenständige Anwendung zu verteilen, die keine Python-Installation erfordert, kann PyInstaller verwendet werden.

PyInstaller installieren:

````bash
pip install pyinstaller
````
#### Icon vorbereiten: 
Stelle sicher, dass sich eine Icon-Datei namens app.ico im selben Verzeichnis wie das Skript befindet.

#### Anwendung erstellen: 
Führe den folgenden Befehl im Terminal aus. Er bündelt das Skript, das Icon und alle Abhängigkeiten in einer einzigen .exe-Datei im dist-Ordner.

````bash
pyinstaller --onefile --noconsole --add-data "app.ico;." bing.py
--onefile: Erstellt eine einzelne ausführbare Datei.
--noconsole: Verhindert, dass beim Start ein Konsolenfenster geöffnet wird (wichtig für eine Hintergrundanwendung).
--add-data "app.ico;."
````
Fügt die app.ico-Datei zum Paket hinzu.

Die fertige bing.exe kann nun direkt ausgeführt und zum Autostart-Ordner von Windows hinzugefügt werden, um sie bei jedem Systemstart automatisch zu laden.
