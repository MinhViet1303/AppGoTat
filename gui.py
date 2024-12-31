from customtkinter import *
from CTkListbox import *
from CTkMessagebox import CTkMessagebox
import replace
import json
import pygetwindow as gw

abbreviations = {}

class App(CTk):
    def __init__(self):
        super().__init__()
        self.title("Ứng dụng gõ tắt")

        # Load config ban đầu
        self.abbreviations, self.blacklist = replace.load_config()
        
        # Khung chứa ô tìm kiếm
        self.search_frame = CTkFrame(master=self)
        self.search_frame.pack(padx=20, pady=(10, 0), fill="x")

        # Ô nhập liệu tìm kiếm
        self.search_entry = CTkEntry(master=self.search_frame, placeholder_text="Tìm kiếm...")
        self.search_entry.pack(fill="x")
        self.search_entry.bind("<KeyRelease>", self.search_abbreviations) # Kết nối sự kiện

        # Khung chứa Listbox
        self.listbox_frame = CTkFrame(master=self)
        self.listbox_frame.pack(padx=20, pady=(10, 0), fill="both", expand=True)

        # Listbox hiển thị các từ viết tắt
        self.listbox = CTkListbox(master=self.listbox_frame, multiple_selection = True)
        self.listbox.pack(side="left", expand=True, fill="both")

        # Khung chứa nhập liệu và nút bấm
        self.input_frame = CTkFrame(master=self)
        self.input_frame.pack(padx=20, pady=(10, 20), fill="x")

        # Nhập từ viết tắt
        self.abbr_label = CTkLabel(master=self.input_frame, text="Từ viết tắt:")
        self.abbr_label.grid(row=0, column=0, sticky="w")
        self.abbr_entry = CTkEntry(master=self.input_frame)
        self.abbr_entry.grid(row=0, column=1, padx=5, sticky="ew")

        # Nhập từ thay thế
        self.repl_label = CTkLabel(master=self.input_frame, text="Thay thế bằng:")
        self.repl_label.grid(row=1, column=0, sticky="w")
        self.repl_entry = CTkEntry(master=self.input_frame)
        self.repl_entry.grid(row=1, column=1, padx=5, sticky="ew")

        self.input_frame.columnconfigure(1, weight=1) # Để input entry chiếm hết chỗ trống

        # Nút Thêm/Sửa từ viết tắt (bây giờ cả thêm và sửa đều dùng nút này)
        self.add_button = CTkButton(master=self.input_frame, text="Thêm/Sửa", command=self.add_abbreviation)
        self.add_button.grid(row=0, column=2, rowspan=1, padx=5, sticky="ns")

        # Nút Xoá từ viết tắt
        self.delete_button = CTkButton(master=self.input_frame, text="Xoá", command=self.delete_abbreviation)
        self.delete_button.grid(row=1, column=2, rowspan=1, padx=5, sticky="ns")
        
        self.load_abbreviations()
        self.listbox.bind("<<ListboxSelect>>", self.on_select)
        
    
        # Khung chứa Listbox Blacklist
        self.blacklist_frame = CTkFrame(master=self)
        self.blacklist_frame.pack(padx=20, pady=(10, 0), fill="both", expand=True)

        # Label cho Blacklist
        self.blacklist_label = CTkLabel(master=self.blacklist_frame, text="Blacklist:")
        self.blacklist_label.pack()

        # Listbox hiển thị các cửa sổ bị blacklist
        self.blacklist_listbox = CTkListbox(master=self.blacklist_frame, multiple_selection = True)
        self.blacklist_listbox.pack(side="left", expand=True, fill="both")

        # Khung chứa dropdown và nút bấm Blacklist
        self.blacklist_input_frame = CTkFrame(master=self)
        self.blacklist_input_frame.pack(padx=20, pady=(10, 20), fill="x")

        # Dropdown chọn cửa sổ
        self.window_options = [""] # Khởi tạo danh sách rỗng
        self.window_dropdown = CTkOptionMenu(master=self.blacklist_input_frame, values=self.window_options)
        self.window_dropdown.pack(side="left", expand=True, fill="x")

        # Nút Thêm vào Blacklist
        self.add_blacklist_button = CTkButton(master=self.blacklist_input_frame, text="Thêm", command=self.add_to_blacklist)
        self.add_blacklist_button.pack(side="left", padx=5)

        # Nút Xoá khỏi Blacklist
        self.remove_blacklist_button = CTkButton(master=self.blacklist_input_frame, text="Xoá", command=self.remove_from_blacklist)
        self.remove_blacklist_button.pack(side="left", padx=5)

        self.load_blacklist()
        self.update_window_list() # Cập nhật danh sách cửa sổ khi khởi động

    def load_blacklist(self):
        self.blacklist_listbox.delete(0, END)
        for item in self.blacklist:
            self.blacklist_listbox.insert(END, item)

    def save_blacklist(self):
        config = {"abbreviations": self.abbreviations, "blacklist": self.blacklist}
        replace.save_config(config)
        replace.load_config()
        replace.blacklist = self.blacklist

    def update_window_list(self):
        self.window_options = []
        # Thêm tiêu đề của chính cửa sổ ứng dụng
        self.window_options.append(self.title()) # Lấy tiêu đề cửa sổ hiện tại và thêm vào danh sách

        for window in gw.getAllWindows():
            if window.title and window.title not in self.window_options: # Kiểm tra để tránh trùng lặp
                self.window_options.append(window.title)
        self.window_dropdown.configure(values=self.window_options)
    
    def add_to_blacklist(self):
        selected_window = self.window_dropdown.get()
        if selected_window and selected_window not in self.blacklist:
            self.blacklist.append(selected_window)
            self.load_blacklist()
            self.save_blacklist()

    def remove_from_blacklist(self):
        selected_indices = self.blacklist_listbox.curselection()
        if selected_indices:
            items_to_remove = [self.blacklist_listbox.get(i) for i in selected_indices]
            for item in items_to_remove:
                self.blacklist.remove(item)
            self.load_blacklist()
            self.save_blacklist()
        else:
            CTkMessagebox(title="Cảnh báo", message="Vui lòng chọn một cửa sổ để xoá khỏi blacklist.", icon="warning")


    # Thêm hàm on_select
    def on_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_item = self.listbox.get(selected_index[0])
            abbr, replacement = selected_item.split(" => ")
            self.abbr_entry.delete(0, END)
            self.abbr_entry.insert(0, abbr)
            self.repl_entry.delete(0, END)
            self.repl_entry.insert(0, replacement)
            
    # Hàm tìm kiếm
    def search_abbreviations(self, event):
        search_text = self.search_entry.get().lower()
        self.listbox.delete(0, END)
        for abbr, replacement in self.abbreviations.items():
            if search_text in abbr.lower() or search_text in replacement.lower(): # Tìm kiếm không phân biệt hoa thường
                self.listbox.insert(END, f"{abbr} => {replacement}")

    def load_abbreviations(self):
        self.listbox.delete(0, END)
        for abbr, replacement in self.abbreviations.items():
            self.listbox.insert(END, f"{abbr} => {replacement}")

    def save_abbreviations(self):
        config = {"abbreviations": self.abbreviations, "blacklist": self.blacklist}
        replace.save_config(config)
        replace.load_config() # load lại config trong replace.py
        replace.abbreviations = self.abbreviations # cập nhật biến abbreviations trong replace.py

    def add_abbreviation(self):
        abbr = self.abbr_entry.get()
        replacement = self.repl_entry.get()
        if abbr and replacement:
            if abbr in self.abbreviations:
                CTkMessagebox(title = "Cảnh báo", message =  f"Từ viết tắt '{abbr}' đã tồn tại.", icon="warning")
            else:
                self.abbreviations[abbr] = replacement
                self.load_abbreviations()
                self.save_abbreviations()
                self.abbr_entry.delete(0, END)
                self.repl_entry.delete(0, END)
        else:
            CTkMessagebox(title = "Cảnh báo", message =  "Vui lòng nhập đầy đủ từ viết tắt và từ thay thế.", icon="warning")
            
    def delete_abbreviation(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_item = self.listbox.get(selected_index[0])
            abbr, replacement = selected_item.split(" => ")

            # Lấy giá trị trả về từ CTkMessageBox
            result = CTkMessagebox(title="Xác nhận?", message=f"Bạn có chắc chắn muốn xoá '{abbr}'?", icon="question", option_1="Cancel", option_2="Yes", option_focus="Cancel")

            # Kiểm tra giá trị trả về
            result = result.get()
            if result == "Yes":
                del self.abbreviations[abbr]
                self.listbox.delete(selected_index[0])  # Xoá phần tử được chọn
                self.save_abbreviations()
        else:
            CTkMessagebox(title = "Cảnh báo", message =  "Vui lòng chọn một từ viết tắt để xoá.", icon="warning")


    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()