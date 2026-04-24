import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# --- Настройки ---
DATA_FILE = "books.json"

# --- Класс основного приложения ---
class BookTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("800x600")

        # Создание виджетов
        self.create_widgets()
        
        # Загрузка данных при старте
        self.load_books()

    def create_widgets(self):
        # --- Рамка для ввода данных ---
        input_frame = tk.LabelFrame(self.root, text="Добавить новую книгу", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill="x")

        # Поля ввода
        tk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="e")
        self.title_entry = tk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, columnspan=3, sticky="w", pady=5)

        tk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="e")
        self.author_entry = tk.Entry(input_frame, width=40)
        self.author_entry.grid(row=1, column=1, columnspan=3, sticky="w", pady=5)

        tk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="e")
        self.genre_entry = tk.Entry(input_frame, width=40)
        self.genre_entry.grid(row=2, column=1, columnspan=3, sticky="w", pady=5)

        tk.Label(input_frame, text="Страниц:").grid(row=3, column=0, sticky="e")
        self.pages_entry = tk.Entry(input_frame, width=15)
        self.pages_entry.grid(row=3, column=1, sticky="w", pady=5)

        # Кнопка добавления
        add_btn = tk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        add_btn.grid(row=4, column=1, pady=10)

        # --- Рамка для таблицы и фильтрации ---
        table_frame = tk.Frame(self.root)
        table_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Таблица (Treeview)
        self.columns = ("Название", "Автор", "Жанр", "Страниц")
        self.tree = ttk.Treeview(table_frame, columns=self.columns, show="headings")
        
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=0, width=150, stretch=False)
        
        # Полоса прокрутки
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # --- Рамка для фильтрации ---
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(padx=10, pady=(0, 10), fill="x")

        tk.Label(filter_frame, text="Фильтр по жанру:").grid(row=0, column=0)
        self.filter_genre_entry = tk.Entry(filter_frame)
        self.filter_genre_entry.grid(row=0, column=1)

        tk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2)
        self.filter_pages_entry = tk.Entry(filter_frame)
        self.filter_pages_entry.grid(row=0, column=3)

        filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=0, column=4, padx=(5, 0))

        clear_btn = tk.Button(filter_frame, text="Очистить фильтр", command=self.clear_filter)
        clear_btn.grid(row=0, column=5)

    # --- Логика работы с данными ---
    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        
        pages_raw = self.pages_entry.get().strip()
        
         # Валидация
         if not (title and author and genre and pages_raw):
             messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
             return

         if not pages_raw.isdigit():
             messagebox.showerror("Ошибка", "Количество страниц должно быть целым числом!")
             return

         pages = int(pages_raw)
         
         # Добавление в таблицу
         self.tree.insert("", "end", values=(title, author, genre, pages))
         
         # Очистка полей
         self.title_entry.delete(0, 'end')
         self.author_entry.delete(0, 'end')
         self.genre_entry.delete(0, 'end')
         self.pages_entry.delete(0, 'end')
         
    def save_books(self):
         books_data = [self.tree.item(i)['values'] for i in self.tree.get_children()]
         
         try:
             with open(DATA_FILE, 'w', encoding='utf-8') as f:
                 json.dump(books_data, f, ensure_ascii=False, indent=4)
             messagebox.showinfo("Успех", "Данные успешно сохранены!")
         except Exception as e:
             messagebox.showerror("Ошибка сохранения", str(e))

    def load_books(self):
         if not os.path.exists(DATA_FILE):
             return

         try:
             with open(DATA_FILE, 'r', encoding='utf-8') as f:
                 books_data = json.load(f)
             
             for book in books_data:
                 # Проверяем структуру данных на случай ручного редактирования json
                 if len(book) == 4 and isinstance(book[3], int):
                     self.tree.insert("", "end", values=tuple(book))
                 else:
                     messagebox.showwarning("Предупреждение", "Некорректный формат данных в файле.")
                     break
         except json.JSONDecodeError:
             messagebox.showerror("Ошибка", "Ошибка чтения файла JSON. Возможно, файл поврежден.")

    # --- Логика фильтрации ---
    def apply_filter(self):
         filter_genre = self.filter_genre_entry.get().lower()
         filter_pages_raw = self.filter_pages_entry.get()
         
         try:
             filter_pages = int(filter_pages_raw) if filter_pages_raw.isdigit() else None
         except ValueError:
             filter_pages = None

         for child in self.tree.get_children():
             values = self.tree.item(child)['values']
             title_val = values[0].lower()
             author_val = values[1].lower()
             genre_val = values[2].lower()
             pages_val = values[3]

             match_genre = (filter_genre == "") or (filter_genre in genre_val) or (filter_genre in title_val) or (filter_genre in author_val)
             
             match_pages = (filter_pages is None) or (pages_val >= filter_pages)

             if match_genre and match_pages:
                 self.tree.item(child, tags='visible')
             else:
                 self.tree.item(child, tags='hidden')
         
         self.tree.tag_configure('hidden', foreground='gray')
         self.tree.tag_configure('visible', foreground='black')

    def clear_filter(self):
         self.filter_genre_entry.delete(0, 'end')
         self.filter_pages_entry.delete(0, 'end')
         
         for child in self.tree.get_children():
             self.tree.item(child, tags='')

# --- Точка входа ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    
    # Добавляем меню для сохранения/загрузки
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Сохранить в JSON", command=app.save_books)
    filemenu.add_command(label="Загрузить из JSON", command=lambda: [app.tree.delete(*app.tree.get_children()), app.load_books()])
    menubar.add_cascade(label="Файл", menu=filemenu)
    
    root.config(menu=menubar)
    
    root.mainloop()
