import json
import re
import time
import os
import pyautogui
import pygetwindow as gw
import pyperclip
from pynput import keyboard
import threading
import psutil

CONFIG_FILE = "config.json"
last_modified = 0
last_size = 0  # Biến lưu kích thước file lần cuối
abbreviations = {}
blacklist = []
current_word = ""

def load_config():
    """Đọc cấu hình từ file config.json. Tạo file nếu chưa tồn tại."""
    global abbreviations, blacklist
    abbreviations = {}
    blacklist = []
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            abbreviations = data.get("abbreviations", {})
            blacklist = data.get("blacklist", [])
    except FileNotFoundError:
        print(f"File cấu hình '{CONFIG_FILE}' không tồn tại. Đang tạo file mới.")
        # Tạo file config.json với nội dung mặc định (rỗng)
        default_config = {"abbreviations": {}, "blacklist": []}
        save_config(default_config) # Gọi hàm save_config để lưu
        print(f"Đã tạo file cấu hình '{CONFIG_FILE}' thành công.")
    except json.JSONDecodeError:
        print(f"Lỗi đọc file JSON '{CONFIG_FILE}'. Kiểm tra định dạng file. Đang tạo file mới.")
        # Tạo file config.json với nội dung mặc định (rỗng)
        default_config = {"abbreviations": {}, "blacklist": []}
        save_config(default_config) # Gọi hàm save_config để lưu
        print(f"Đã tạo lại file cấu hình '{CONFIG_FILE}' thành công.")
    return abbreviations, blacklist

def save_config(config):
    """Lưu cấu hình vào file config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def check_for_changes():
    """Kiểm tra xem file JSON có bị thay đổi hay không (cả thời gian và kích thước)."""
    global last_modified, last_size
    try:
        modified_time = os.path.getmtime(CONFIG_FILE)
        file_size = os.path.getsize(CONFIG_FILE)
        if modified_time != last_modified or file_size != last_size:
            load_config()
            last_modified = modified_time
            last_size = file_size
            print("Đã cập nhật file config.")
            print(abbreviations)
            print(blacklist)
    except FileNotFoundError:
        pass
    except OSError:
        pass
def is_blacklisted():
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            window_title = active_window.title.lower()
            for item in blacklist:
                if item.lower() == window_title: # So sánh chính xác title
                    return True
        return False
    except gw.PyGetWindowException:
        return False
    except AttributeError:
        return False

def on_release(key):
    if key == keyboard.Key.esc:
        return False

def on_press(key):
    global current_word
    if is_blacklisted(): # Kiểm tra blacklist trước khi thay thế
        return
    
    try:
        current_word += key.char
    except AttributeError:
        if key == keyboard.Key.space:
            current_word += " "
        elif key == keyboard.Key.backspace:
            current_word = current_word[:-1]
        else:
            current_word = ""

    for abbr, replacement in abbreviations.items():
        if current_word.endswith(abbr):
            for _ in range(len(abbr)):
                pyautogui.press('backspace')
            time.sleep(0.05)
            pyperclip.copy(replacement)
            pyautogui.hotkey('ctrl', 'v')
            current_word = ""
            break

def run_replace_function():
    global last_modified, last_size
    load_config()
    if os.path.exists(CONFIG_FILE):
        last_modified = os.path.getmtime(CONFIG_FILE)
        last_size = os.path.getsize(CONFIG_FILE)
    else:
        last_modified = 0
        last_size = 0
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        while listener.running:
            check_for_changes()
            time.sleep(1)

if __name__ != "__main__":
    pass
else:
    run_replace_function()