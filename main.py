import threading
import subprocess
import time

def run_gui():
    try:
        import gui
        gui.App().mainloop()
    except Exception as e:
        print(f"Lỗi khi chạy GUI: {e}")

def run_replace(stop_event):  # Nhận stop_event
    try:
        import replace
        replace.run_replace_function()
    except Exception as e:
        print(f"Lỗi khi chạy replace: {e}")

if __name__ == "__main__":
    stop_event = threading.Event() # Tạo event để dừng thread replace

    gui_thread = threading.Thread(target=run_gui)
    replace_thread = threading.Thread(target=run_replace, args=(stop_event,)) # Truyền stop_event

    gui_thread.start()
    replace_thread.start()

    try:
        gui_thread.join()
    except KeyboardInterrupt:
        print("Đang tắt chương trình...")
        stop_event.set() # Set event để dừng replace thread
        replace_thread.join()
        print("Chương trình đã tắt.")