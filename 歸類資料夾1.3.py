import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
import os
import re
import shutil


class FolderManager:
    def __init__(self, source_dir, target_dir, exception_folders):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.exception_folders = exception_folders

    def move_folders(self):
        style_folders = os.listdir(self.target_dir)

        for style_folder in style_folders:
            style_folder_path = os.path.join(self.target_dir, style_folder)
            if os.path.isdir(style_folder_path):
                author_folders = os.listdir(style_folder_path)
                for author_folder in author_folders:
                    author_folder_path = os.path.join(
                        style_folder_path, author_folder)
                    if os.path.isdir(author_folder_path):
                        self.move_author_folders(
                            style_folder, author_folder, author_folder_path)
        self.move_unclassified_folders()

    def move_author_folders(self, style_folder, author_folder, target_folder_path):
        files = os.listdir(self.source_dir)

        for folder in files:
            folder_path = os.path.join(self.source_dir, folder)
            if os.path.isdir(folder_path):
                if not re.match(r'\[.*\].*', folder):
                    continue
                if style_folder in self.exception_folders:
                    continue
                if self.is_author_match(folder, author_folder):
                    if folder != author_folder:
                        target_subfolder_path = os.path.join(
                            target_folder_path)
                        os.makedirs(target_subfolder_path, exist_ok=True)
                        shutil.move(folder_path, target_subfolder_path)
                        print(f"已將 {folder} 移動至 {target_subfolder_path}")

    def move_unclassified_folders(self):
        unclassified_folder_path = os.path.join(self.target_dir, "未分類作者")
        os.makedirs(unclassified_folder_path, exist_ok=True)

        for folder in os.listdir(self.source_dir):
            folder_path = os.path.join(self.source_dir, folder)
            if os.path.isdir(folder_path):
                author_info = self.get_author_info(folder)
                if author_info:
                    author_name, author_alias = author_info
                    author_folder_name = f"[{author_name} ({author_alias})]" if author_alias else f"[{author_name}]"
                    author_folder_path = os.path.join(
                        unclassified_folder_path, author_folder_name)
                    os.makedirs(author_folder_path, exist_ok=True)
                    target_subfolder_path = os.path.join(
                        author_folder_path, folder)
                    shutil.move(folder_path, target_subfolder_path)
                    print(f"已將 {folder} 移動至 {target_subfolder_path}")
                else:
                    print(f"無法獲取 {folder} 的作者資訊，無法建立作者資料夾")

    def is_author_match(self, folder_name, author_folder_name):
        folder_info = self.get_author_info(folder_name)
        if folder_info:
            folder_author_name, folder_author_alias = folder_info
            author_info = self.get_author_info(author_folder_name)
            if author_info:
                author_name, author_alias = author_info
                folder_name_no_space = folder_author_name.replace(
                    " ", "").lower()
                folder_alias_no_space = folder_author_alias.replace(
                    " ", "").lower()
                author_name_no_space = author_name.replace(" ", "").lower()
                author_alias_no_space = author_alias.replace(" ", "").lower()
                if folder_name_no_space == author_name_no_space or folder_name_no_space == author_alias_no_space:
                    return True
                if folder_author_alias and (folder_alias_no_space == author_name_no_space or folder_alias_no_space == author_alias_no_space):
                    return True
        return False

    def get_author_info(self, author_folder_name):
        match = re.search(r'\[(.*?)\]', author_folder_name)
        if match:
            author_info = match.group(1)
            author_parts = author_info.split(
                ' (', 1) if ' (' in author_info else [author_info]
            author_name = author_parts[0]
            author_alias = author_parts[1].strip(')') if len(
                author_parts) > 1 else ''
            return author_name, author_alias
        return None


class FolderManagerGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("nhentai歸類器")
        self.window.geometry("800x600")

        font_family_list = font.families()

        if "Noto Sans TC" in font_family_list:
            font_style = font.Font(family="Noto Sans TC", size=12)
        else:

            font_style = font.Font(size=16)

        self.window.option_add("*Font", font_style)

        instruction_text = """
        注意事項

        1. 這個程式假設你的已歸類資料夾存在以作者風格或常用程度進行分類的第一層資料夾，
        而作者資料夾在這層資料夾當中。
        2. 若找不到作者資料夾，程式會將其整理並放至於已歸類資料夾中的「未分類作者」資料夾中。
        3. 如果你在已歸類資料夾中存在除了nhentai的作者資料夾以外還有其他資料夾，
        為了效率考量建議填寫例外資料夾，例外資料夾以半形逗號分隔。

        注意：在開始移動之前，請確保您已經選擇了有效的來源目錄和目標目錄。

        4. 移動完成後，您將看到一個彈出視窗顯示「完成」，在過程中建議不要關閉程式。"""

        self.instruction_label = tk.Label(
            self.window, text=instruction_text, justify=tk.LEFT)
        self.instruction_label.pack()

        source_label = tk.Label(self.window, text="等待歸類目錄：")
        source_label.pack()
        self.source_entry = tk.Entry(self.window)
        self.source_entry.pack()
        source_button = tk.Button(
            self.window, text="選擇目錄", command=self.select_source_directory)
        source_button.pack()

        target_label = tk.Label(self.window, text="已歸類目錄：")
        target_label.pack()
        self.target_entry = tk.Entry(self.window)
        self.target_entry.pack()
        target_button = tk.Button(
            self.window, text="選擇目錄", command=self.select_target_directory)
        target_button.pack()

        exception_label = tk.Label(
            self.window, text="例外資料夾（以\'或\"夾住，並以逗號分隔）：")
        exception_label.pack()
        self.exception_entry = tk.Entry(self.window)
        self.exception_entry.pack()

        start_button = tk.Button(
            self.window, text="開始歸類", command=self.start_move)
        start_button.pack()

    def select_directory(self, entry):
        selected_dir = filedialog.askdirectory()
        entry.delete(0, tk.END)
        entry.insert(tk.END, selected_dir)

    def select_source_directory(self):
        self.select_directory(self.source_entry)

    def select_target_directory(self):
        self.select_directory(self.target_entry)

    def start_move(self):
        source_dir = self.source_entry.get()
        target_dir = self.target_entry.get()
        exception_folders = self.exception_entry.get().split(',')

        if not source_dir or not target_dir:
            messagebox.showerror("錯誤", "請選擇來源目錄和目標目錄")
            return

        if not os.path.isdir(source_dir):
            messagebox.showerror("錯誤", "無效的來源目錄")
            return

        if not os.path.isdir(target_dir):
            messagebox.showerror("錯誤", "無效的目標目錄")
            return

        folder_manager = FolderManager(
            source_dir, target_dir, exception_folders)
        folder_manager.move_folders()
        messagebox.showinfo("完成", "資料夾移動完成")

    def run(self):
        self.window.mainloop()


folder_manager_gui = FolderManagerGUI()
folder_manager_gui.run()
