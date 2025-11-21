---
description: Repository Information Overview
alwaysApply: true
---

# Bing Wallpaper Auto Updater

## Summary

A Windows desktop application that automatically downloads Bing's daily wallpaper and sets it as the desktop background. The application runs discreetly in the system tray, offering menu-based control for manual updates, toggling automatic daily updates, and configuring autostart functionality. All downloaded images are stored locally in the Pictures folder for user reference.

## Structure

- **bing.py** - Main application file containing the WallpaperApp class with tray integration, Bing API communication, and Windows background management
- **requirements.txt** - Python package dependencies
- **version_info.txt** - Version metadata for compiled executable
- **App.ico** - Application icon for system tray and executable
- **dist/** - Compiled executable output directory (bing.exe, bing.exe.alt)
- **.venv/** - Python virtual environment
- **.vscode/** - VS Code editor configuration

## Language & Runtime

**Language**: Python 3.x  
**Build System**: PyInstaller  
**Package Manager**: pip  
**Platform**: Windows (requires Windows API)

## Dependencies

**Main Dependencies**:
- **requests** - HTTP library for downloading images from Bing API
- **Pillow (PIL)** - Image processing and Icon creation
- **pystray** - System tray integration and menu handling
- **winshell** - Windows shell utilities (startup folder access)
- **pywin32** - Windows API access for setting desktop wallpaper

**Development Dependencies**:
- **pyinstaller** - Packaging Python application into standalone executable

## Build & Installation

**Install dependencies**:
```bash
pip install -r requirements.txt
```

**Run application**:
```bash
python bing.py
```

**Build executable**:
```bash
pyinstaller --onefile --noconsole --add-data "app.ico;." bing.py
```

This creates a standalone bing.exe in the dist/ folder that requires no Python installation.

## Main Entry Points

**Application Entry**: `bing.py:178` - `if __name__ == "__main__"` block initializes WallpaperApp and starts execution  
**Main Class**: `WallpaperApp` - Manages tray icon, menu interactions, wallpaper updates, and autostart configuration  
**Key Methods**:
- `get_bing_wallpaper()` - Fetches daily image from Bing API (de-DE market)
- `set_wallpaper()` - Sets wallpaper using Windows API (SPI_SETDESKWALLPAPER)
- `auto_update_loop()` - Background thread loop for 24-hour update cycle
- `toggle_autostart()` - Creates/removes startup shortcut in Windows startup folder

## Application Features

- **Daily Auto-Update**: Downloads new Bing wallpaper every 24 hours (configurable via tray menu)
- **Manual Update**: Instant wallpaper download and application via menu
- **Local Storage**: Saves images in `%USERPROFILE%\Pictures\BingWallpaper\` with ISO date naming
- **Duplicate Prevention**: Checks if today's image already exists before downloading
- **System Tray Integration**: Minimalist UI with context menu for all controls
- **Autostart Support**: Creates Windows startup shortcut for automatic launch on login

## Executable Version

**Current Version**: 1.0.2.1  
**Compiled Output**: dist/bing.exe (28.09 MB)  
**Metadata**: FileDescription: Bing Wallpaper Downloader, CompanyName: Marcus Tools
