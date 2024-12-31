import customtkinter
import json
import tkinter as tk
from tkinter import messagebox
import psutil
import pygetwindow as gw

CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Lỗi", f"Lỗi đọc file JSON. Kiểm tra định dạng của {CONFIG_FILE}")
        return {}

def save_config(config): # Hàm save_config được sửa
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Quản lý từ viết tắt")
        self.geometry("700x600")

        self.config_data = load_config() # Load toàn bộ config
        self.abbreviations = self.config_data.get("abbreviations", {})
        self.blacklist = self.config_data.get("blacklist", [])

        self.abbr_label = customtkinter.CTkLabel(self, text="Từ viết tắt:")
        self.abbr_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.abbr_entry = customtkinter.CTkEntry(self)
        self.abbr_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.replace_label = customtkinter.CTkLabel(self, text="Từ thay thế:")
        self.replace_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.replace_entry = customtkinter.CTkEntry(self)
        self.replace_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Danh sách cửa sổ đang hoạt động
        self.window_list_label = customtkinter.CTkLabel(self, text="Cửa sổ đang hoạt động:")
        self.window_list_label.grid(row=7, column=0, padx=10, pady=(10, 5), sticky="w")

        self.selected_window = tk.StringVar(self)
        self.selected_window.set("Chọn cửa sổ")

        self.window_dropdown = tk.OptionMenu(self, self.selected_window, "")
        self.window_dropdown.grid(row=8, column=0, padx=10, pady=(0, 10), sticky="ew")

        # Blacklist (SỬA ĐỔI: dùng Listbox)
        self.blacklist_label = customtkinter.CTkLabel(self, text="Blacklist:")
        self.blacklist_label.grid(row=5, column=0, padx=10, pady=(10, 5), sticky="w")
        self.blacklist_listbox = tk.Listbox(self) # Thay bằng tk.Listbox
        self.blacklist_listbox.grid(row=6, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="nsew")
        self.grid_rowconfigure(6, weight=1) # Giữ cho listbox có thể giãn nở

        # Nút Add to Blacklist
        self.add_to_blacklist_button = customtkinter.CTkButton(self, text="Thêm vào Blacklist", command=self.add_selected_to_blacklist)
        self.add_to_blacklist_button.grid(row=9, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        # Nút Xóa Blacklist
        self.delete_blacklist_button = customtkinter.CTkButton(self, text="Xóa Blacklist", command=self.delete_blacklist_item)
        self.delete_blacklist_button.grid(row=10, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        self.load_blacklist()
        self.after(100, self.update_window_list)

        self.add_button = customtkinter.CTkButton(self, text="Thêm/Sửa", command=self.add_or_update)
        self.add_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        self.delete_button = customtkinter.CTkButton(self, text="Xóa", command=self.delete)
        self.delete_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

        self.grid_columnconfigure(1, weight=1)

        self.listbox = tk.Listbox(self)
        self.listbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        self.update_listbox()
    
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for abbr, replacement in self.abbreviations.items():
            self.listbox.insert(tk.END, f"{abbr} : {replacement}")
    
    def update_window_list(self):
        """Cập nhật danh sách cửa sổ và dropdown (chỉ lấy title)."""
        windows = gw.getAllTitles()

        self.window_dropdown['menu'].delete(0, 'end')
        if windows:
            for window in windows:
                self.window_dropdown['menu'].add_command(label=window, command=lambda value=window: self.selected_window.set(value))
        else:
            self.window_dropdown['menu'].add_command(label="Không có cửa sổ nào", command=lambda: None)
        self.selected_window.set("Chọn cửa sổ")

    def add_selected_to_blacklist(self):
        selected_window = self.selected_window.get()
        if selected_window != "Chọn cửa sổ":
            if selected_window not in self.blacklist:
                self.blacklist.append(selected_window)
                self.save_config() # Lưu config NGAY SAU KHI THÊM
                self.load_blacklist() # Load lại blacklist để cập nhật giao diện
            else:
                messagebox.showwarning("Cảnh báo", "Mục này đã có trong Blacklist.")
        else:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một cửa sổ.")

    def delete_blacklist_item(self):
        try:
            selection = self.blacklist_listbox.curselection()
            if selection:
                index = selection[0]
                del self.blacklist[index]
                self.save_config() # Lưu config NGAY SAU KHI XÓA
                self.load_blacklist() # Load lại blacklist để cập nhật giao diện
            else:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mục để xóa.")
        except IndexError:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mục để xóa.")
        except tk.TclError:
            pass

    def load_blacklist(self):
        self.blacklist_listbox.delete(0, tk.END)
        for item in self.blacklist:
            if isinstance(item, dict):
                if "title" in item:
                    self.blacklist_listbox.insert(tk.END, item["title"])
                elif "title_regex" in item:
                    self.blacklist_listbox.insert(tk.END, item["title_regex"])
                elif "process" in item:
                    self.blacklist_listbox.insert(tk.END, item["process"])
                elif "pid" in item:
                    self.blacklist_listbox.insert(tk.END, str(item["pid"]))
            elif isinstance(item, str):
                self.blacklist_listbox.insert(tk.END, item)
            else:
                print(f"Định dạng blacklist không được hỗ trợ: {item}")

    def save_config(self):
        config = {
            "abbreviations": self.abbreviations,
            "blacklist": self.blacklist,
        }
        save_config(config)

    def add_or_update(self):
        abbr = self.abbr_entry.get().strip()
        replacement = self.replace_entry.get().strip()

        if not abbr or not replacement:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin.")
            return

        self.abbreviations[abbr] = replacement
        self.save_config() # Lưu config (bao gồm cả blacklist)
        self.update_listbox()
        self.abbr_entry.delete(0, tk.END)
        self.replace_entry.delete(0, tk.END)

    def delete(self):
        try:
            selection = self.listbox.curselection()[0]
            selected_item = self.listbox.get(selection)
            abbr = selected_item.split(" : ")[0]
            del self.abbreviations[abbr]
            self.save_config() # Lưu config (bao gồm cả blacklist)
            self.update_listbox()
        except IndexError:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một mục để xóa.")
            return

if __name__ == "__main__":
    app = App()
    app.mainloop()