import os
import sys
import ctypes
import time
import requests
import subprocess
import shutil
import threading
import itertools
import pystray
import win32com.client
from datetime import datetime
from PIL import Image
from io import BytesIO
from packaging import version

# Settings
NEKORAY_URL = "https://github.com/DevikTeam/nekoray/releases/download/nekotest/nekoray.7z"
DISCORD_FIX_URL = "https://github.com/KiryaScript/discord-fix-app/releases/download/v7.1.1/DiscordFix.7z"
SEVENZIP_URL = "https://www.7-zip.org/a/7z2500-x64.exe"
NEKORAY_ARCHIVE = "nekoray.7z"
DISCORD_FIX_ARCHIVE = "DiscordFix.7z"
SEVENZIP_EXE = "7z-installer.exe"
TEMP_DIR = r"C:\Temp\nekoray_temp"
SEVENZIP_DIR = os.path.join(TEMP_DIR, "7zip")
NEKORAY_INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], "Nekoray")
DISCORD_FIX_INSTALL_DIR = os.path.join(os.environ["ProgramFiles"], "DiscordFix")
NEKORAY_EXE = os.path.join(NEKORAY_INSTALL_DIR, "nekoray.exe")
DISCORD_FIX_EXE = os.path.join(DISCORD_FIX_INSTALL_DIR, "Установить как службу в АВТОЗАПУСК v2.exe")
LOG_FILE = r"C:\nekoray_install.log"
DESKTOP_DIR = os.path.join(os.environ["USERPROFILE"], "Desktop")
NEKORAY_SHORTCUT = "Nekoray.lnk"
DISCORD_FIX_SHORTCUT = "DiscordFix.lnk"
GITHUB_RELEASES_API = "https://api.github.com/repos/DevikTeam/nekoray/releases"

# Animation frames
ANIMATIONS = {
    "spinner": [
        "| Installing /",
        "| Installing -",
        "| Installing \\",
        "| Installing |",
    ],
    "progress": [
        "[          ]",
        "[=         ]",
        "[==        ]",
        "[===       ]",
        "[====      ]",
        "[=====     ]",
        "[======    ]",
        "[=======   ]",
        "[========  ]",
        "[========= ]",
        "[==========]"
    ],
    "logo": [
        """
        ███╗   ██╗███████╗██╗  ██╗ ██████╗ ██████╗  █████╗ ██╗   ██╗
        ████╗  ██║██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
        ██╔██╗ ██║█████╗  █████╔╝ ██║   ██║██████╔╝███████║ ╚████╔╝ 
        ██║╚██╗██║██╔══╝  ██╔═██╗ ██║   ██║██╔══██╗██╔══██║  ╚██╔╝  
        ██║ ╚████║███████╗██║  ██╗╚██████╔╝██║  ██║██║  ██║   ██║   
        ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   
        """,
        """
        .██╗   ██╗███████╗██╗  ██╗ ██████╗ ██████╗  █████╗ ██╗   ██╗.
         ███╗  ██║██╔════╝██║ ██╔╝██╔═══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝ 
        ██╔██╗ ██║█████╗  █████╔╝ ██║   ██║██████╔╝███████║ ╚████╔╝  
        ██║╚██╗██║██╔══╝  ██╔═██╗ ██║   ██║██╔══██╗██╔══██║  ╚██╔╝   
        ██║ ╚████║███████╗██║  ██╗╚██████╔╝██║  ██║██║  ██║   ██║    
        ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    
        """
    ]
}

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"Failed to write to log: {e}")
    print(message)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        log("Fuck, admin rights required! Relaunching with UAC...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(1)
    log("[✓] Admin rights granted")

def animation(frames):
    spinner = itertools.cycle(frames)
    while not stop_animation.is_set():
        frame = next(spinner)
        sys.stdout.write("\r" + frame)
        sys.stdout.flush()
        time.sleep(0.3)
    sys.stdout.write("\r" + " " * 80 + "\r")  # Clear the line

def start_animation(animation_type):
    global anim_thread
    stop_animation.clear()
    anim_thread = threading.Thread(target=animation, args=(ANIMATIONS[animation_type],))
    anim_thread.daemon = True
    anim_thread.start()

def stop_animation_func():
    stop_animation.set()
    anim_thread.join(timeout=1.0)

def create_temp_dirs():
    start_animation("spinner")
    log("Creating temporary directories...")
    try:
        os.makedirs(TEMP_DIR, exist_ok=True)
        os.makedirs(SEVENZIP_DIR, exist_ok=True)
        log(f"TEMP_DIR: {TEMP_DIR}")
        log(f"SEVENZIP_DIR: {SEVENZIP_DIR}")
        log("[✓] Temp directories created")
    except Exception as e:
        log(f"Fuck, failed to create temp directories: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def download_file(url, dest):
    start_animation("progress")
    log(f"Downloading {os.path.basename(dest)}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        if not os.path.exists(dest):
            raise FileNotFoundError("Download completed but file not found!")
        log(f"[✓] {os.path.basename(dest)} downloaded")
    except Exception as e:
        log(f"Shit, failed to download {os.path.basename(dest)}: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def install_sevenzip():
    start_animation("spinner")
    log("Installing 7-Zip...")
    sevenzip_path = os.path.join(TEMP_DIR, SEVENZIP_EXE)
    try:
        subprocess.run([sevenzip_path, "/S", f"/D={SEVENZIP_DIR}"], check=True, capture_output=True)
        if not os.path.exists(os.path.join(SEVENZIP_DIR, "7z.exe")):
            raise FileNotFoundError("7-Zip installation completed but 7z.exe not found!")
        log("[✓] 7-Zip installed")
    except Exception as e:
        log(f"Fuck, 7-Zip installation failed: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def extract_archive(archive_path, install_dir):
    start_animation("progress")
    log(f"Extracting {os.path.basename(archive_path)}...")
    sevenzip_exe = os.path.join(SEVENZIP_DIR, "7z.exe")
    try:
        subprocess.run([sevenzip_exe, "x", archive_path, f"-o{install_dir}", "-y"], check=True, capture_output=True)
        log(f"[✓] {os.path.basename(archive_path)} extracted")
    except Exception as e:
        log(f"Fuck, failed to extract {os.path.basename(archive_path)}: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def create_shortcut(exe_path, shortcut_name, description):
    start_animation("spinner")
    log(f"Creating desktop shortcut for {os.path.basename(exe_path)}...")
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = os.path.join(DESKTOP_DIR, shortcut_name)
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = exe_path
        shortcut.WorkingDirectory = os.path.dirname(exe_path)
        shortcut.IconLocation = exe_path
        shortcut.Description = description
        shortcut.save()
        log(f"[✓] Desktop shortcut created for {os.path.basename(exe_path)}")
    except Exception as e:
        log(f"Fuck, failed to create desktop shortcut: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def cleanup_temp():
    start_animation("spinner")
    log("Cleaning up temporary files...")
    try:
        if os.path.exists(os.path.join(TEMP_DIR, NEKORAY_ARCHIVE)):
            os.remove(os.path.join(TEMP_DIR, NEKORAY_ARCHIVE))
        if os.path.exists(os.path.join(TEMP_DIR, DISCORD_FIX_ARCHIVE)):
            os.remove(os.path.join(TEMP_DIR, DISCORD_FIX_ARCHIVE))
        if os.path.exists(os.path.join(TEMP_DIR, SEVENZIP_EXE)):
            os.remove(os.path.join(TEMP_DIR, SEVENZIP_EXE))
        if os.path.exists(SEVENZIP_DIR):
            shutil.rmtree(SEVENZIP_DIR)
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        log("[✓] Temp files cleaned up")
    except Exception as e:
        log(f"Shit, failed to clean up temp files: {e}")
    stop_animation_func()

def check_updates():
    start_animation("spinner")
    log("Checking for Nekoray updates...")
    try:
        response = requests.get(GITHUB_RELEASES_API, timeout=10)
        response.raise_for_status()
        releases = response.json()
        if not releases:
            log("No releases found on GitHub!")
            stop_animation_func()
            return None
        latest_release = releases[0]
        latest_version = latest_release["tag_name"]
        current_version = "nekotest"  # Replace with actual version if known
        log(f"Current version: {current_version}")
        log(f"Latest version: {latest_version}")
        if version.parse(latest_version.lstrip('v')) > version.parse(current_version.lstrip('v')):
            log("Update available!")
            for asset in latest_release["assets"]:
                if asset["name"].endswith(".7z"):
                    return asset["browser_download_url"]
            log("No .7z file found in latest release!")
        else:
            log("Nekoray is up to date!")
        stop_animation_func()
        return None
    except Exception as e:
        log(f"Fuck, failed to check updates: {e}")
        stop_animation_func()
        return None

def update_nekoray():
    update_url = check_updates()
    if update_url:
        start_animation("progress")
        log("Updating Nekoray...")
        try:
            if os.path.exists(NEKORAY_INSTALL_DIR):
                shutil.rmtree(NEKORAY_INSTALL_DIR)
            download_file(update_url, os.path.join(TEMP_DIR, NEKORAY_ARCHIVE))
            extract_archive(os.path.join(TEMP_DIR, NEKORAY_ARCHIVE), NEKORAY_INSTALL_DIR)
            create_shortcut(NEKORAY_EXE, NEKORAY_SHORTCUT, "Nekoray Proxy Manager")
            log("[✓] Nekoray updated")
        except Exception as e:
            log(f"Fuck, failed to update Nekoray: {e}")
            stop_animation_func()
            sys.exit(1)
        stop_animation_func()
    else:
        log("No update needed or failed to find update!")

def uninstall_nekoray():
    start_animation("spinner")
    log("Uninstalling Nekoray...")
    try:
        if os.path.exists(NEKORAY_INSTALL_DIR):
            shutil.rmtree(NEKORAY_INSTALL_DIR)
        shortcut_path = os.path.join(DESKTOP_DIR, NEKORAY_SHORTCUT)
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        log("[✓] Nekoray uninstalled")
    except Exception as e:
        log(f"Fuck, failed to uninstall Nekoray: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def uninstall_discord_fix():
    start_animation("spinner")
    log("Uninstalling DiscordFix...")
    try:
        if os.path.exists(DISCORD_FIX_INSTALL_DIR):
            shutil.rmtree(DISCORD_FIX_INSTALL_DIR)
        shortcut_path = os.path.join(DESKTOP_DIR, DISCORD_FIX_SHORTCUT)
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
        log("[✓] DiscordFix uninstalled")
    except Exception as e:
        log(f"Fuck, failed to uninstall DiscordFix: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def install_nekoray():
    start_animation("logo")
    log("Installing Nekoray...")
    try:
        download_file(NEKORAY_URL, os.path.join(TEMP_DIR, NEKORAY_ARCHIVE))
        extract_archive(os.path.join(TEMP_DIR, NEKORAY_ARCHIVE), NEKORAY_INSTALL_DIR)
        create_shortcut(NEKORAY_EXE, NEKORAY_SHORTCUT, "Nekoray Proxy Manager")
        log("[✓] Nekoray installed")
    except Exception as e:
        log(f"Fuck, failed to install Nekoray: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def install_discord_fix():
    start_animation("logo")
    log("Installing DiscordFix...")
    try:
        download_file(DISCORD_FIX_URL, os.path.join(TEMP_DIR, DISCORD_FIX_ARCHIVE))
        extract_archive(os.path.join(TEMP_DIR, DISCORD_FIX_ARCHIVE), DISCORD_FIX_INSTALL_DIR)
        create_shortcut(DISCORD_FIX_EXE, DISCORD_FIX_SHORTCUT, "DiscordFix Application")
        log("[✓] DiscordFix installed")
    except Exception as e:
        log(f"Fuck, failed to install DiscordFix: {e}")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def launch_nekoray():
    start_animation("spinner")
    if os.path.exists(NEKORAY_EXE):
        log("Launching Nekoray...")
        subprocess.Popen([NEKORAY_EXE])
        log("[✓] Nekoray launched")
    else:
        log(f"Fuck, nekoray.exe not found at {NEKORAY_EXE}!")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def launch_discord_fix():
    start_animation("spinner")
    if os.path.exists(DISCORD_FIX_EXE):
        log("Launching DiscordFix...")
        subprocess.Popen([DISCORD_FIX_EXE])
        log("[✓] DiscordFix launched")
    else:
        log(f"Fuck, DiscordFix.exe not found at {DISCORD_FIX_EXE}!")
        stop_animation_func()
        sys.exit(1)
    stop_animation_func()

def show_menu():
    print("\n=== Nekoray & DiscordFix Installer ===")
    print("1. Install Nekoray")
    print("2. Install DiscordFix")
    print("3. Install Both")
    print("4. Exit")
    choice = input("Enter choice (1-4): ").strip()
    return choice

def create_tray_icon():
    image = Image.new("RGB", (64, 64), color="white")  # Placeholder icon
    icon = pystray.Icon("Nekoray", image, "Nekoray & DiscordFix Manager")
    icon.menu = pystray.Menu(
        pystray.MenuItem("Check Nekoray Updates", check_updates),
        pystray.MenuItem("Update Nekoray", update_nekoray),
        pystray.MenuItem("Install Nekoray", install_nekoray),
        pystray.MenuItem("Uninstall Nekoray", uninstall_nekoray),
        pystray.MenuItem("Launch Nekoray", launch_nekoray),
        pystray.MenuItem("Install DiscordFix", install_discord_fix),
        pystray.MenuItem("Uninstall DiscordFix", uninstall_discord_fix),
        pystray.MenuItem("Launch DiscordFix", launch_discord_fix),
        pystray.MenuItem("Exit", lambda: icon.stop())
    )
    return icon

def main():
    global stop_animation, anim_thread
    stop_animation = threading.Event()

    run_as_admin()
    create_temp_dirs()
    download_file(SEVENZIP_URL, os.path.join(TEMP_DIR, SEVENZIP_EXE))
    install_sevenzip()

    choice = show_menu()
    if choice == "1":
        install_nekoray()
        launch_nekoray()
    elif choice == "2":
        install_discord_fix()
        launch_discord_fix()
    elif choice == "3":
        install_nekoray()
        install_discord_fix()
        launch_nekoray()
        launch_discord_fix()
    elif choice == "4":
        log("Exiting installer...")
        sys.exit(0)
    else:
        log("Invalid choice, exiting...")
        sys.exit(1)

    cleanup_temp()
    tray_icon = create_tray_icon()
    tray_icon.run()

if __name__ == "__main__":
    main()