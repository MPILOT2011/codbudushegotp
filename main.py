import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("650x500")

        # Данные и файл
        self.data_file = "trainings.json"
        self.trainings = []        # список словарей: {"date":..., "type":..., "duration":...}
        self.load_data()

        # Переменные для фильтров (если None — фильтр не активен)
        self.filter_type = None    # строка или пустая строка
        self.filter_date = None    # строка в формате YYYY-MM-DD

        # --- Верхняя панель добавления ---
        input_frame = ttk.LabelFrame(root, text="Новая тренировка", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата:").grid(row=0, column=0, sticky="w")
        self.entry_date = ttk.Entry(input_frame, width=15)
        self.entry_date.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w")
        self.combo_type = ttk.Combobox(input_frame, values=["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Растяжка"], width=18)
        self.combo_type.grid(row=0, column=3, padx=5, pady=2)

        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w")
        self.entry_duration = ttk.Entry(input_frame, width=10)
        self.entry_duration.grid(row=0, column=5, padx=5, pady=2)

        self.btn_add = ttk.Button(input_frame, text="Добавить", command=self.add_training)
        self.btn_add.grid(row=0, column=6, padx=10)

        # --- Таблица ---
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")

        self.tree.column("date", width=100, anchor="center")
        self.tree.column("type", width=150, anchor="center")
        self.tree.column("duration", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Панель фильтров ---
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, sticky="w")
        self.filter_combo = ttk.Combobox(filter_frame, values=["Все"] + ["Бег", "Плавание", "Велосипед", "Силовая", "Йога", "Растяжка"], width=18)
        self.filter_combo.grid(row=0, column=1, padx=5, pady=2)
        self.filter_combo.set("Все")

        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=2, sticky="w")
        self.filter_entry_date = ttk.Entry(filter_frame, width=15)
        self.filter_entry_date.grid(row=0, column=3, padx=5, pady=2)

        self.btn_apply = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.btn_apply.grid(row=0, column=4, padx=5)

        self.btn_reset = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        self.btn_reset.grid(row=0, column=5, padx=5)

        # --- Кнопка удаления ---
        self.btn_delete = ttk.Button(root, text="Удалить выбранную тренировку", command=self.delete_training)
        self.btn_delete.pack(pady=5)

        # Первоначальное отображение
        self.refresh_table()

    # ---------- Валидация ----------
    def validate_date(self, date_str):
        """Проверяет, что строка является датой в формате YYYY-MM-DD."""
        if not date_str:
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, dur_str):
        """Проверяет, что длительность — положительное целое число."""
        if not dur_str:
            return False
        try:
            val = int(dur_str)
            return val > 0
        except ValueError:
            return False

    # ---------- Работа с данными ----------
    def load_data(self):
        """Загружает тренировки из JSON-файла, если файл отсутствует — создаёт демо-данные."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.trainings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.trainings = []
        else:
            # Демо-данные для первого запуска
            self.trainings = [
                {"date": "2026-05-08", "type": "Бег", "duration": 30},
                {"date": "2026-05-08", "type": "Силовая", "duration": 60},
                {"date": "2026-05-10", "type": "Плавание", "duration": 45}
            ]
            self.save_data()

    def save_data(self):
        """Сохраняет все тренировки в JSON."""
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=2)

    def refresh_table(self):
        """Обновляет таблицу с учётом текущих фильтров."""
        # Очистка
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Применяем фильтры
        filtered = self.trainings
        if self.filter_type and self.filter_type != "Все":
            filtered = [t for t in filtered if t["type"].lower() == self.filter_type.lower()]
        if self.filter_date:
            filtered = [t for t in filtered if t["date"] == self.filter_date]

        # Заполнение
        for tr in filtered:
            self.tree.insert("", "end", values=(tr["date"], tr["type"], tr["duration"]))

    # ---------- Обработчики кнопок ----------
    def add_training(self):
        """Добавляет новую тренировку после валидации."""
        date = self.entry_date.get().strip()
        train_type = self.combo_type.get().strip()
        duration = self.entry_duration.get().strip()

        # Проверки
        if not date or not train_type or not duration:
            messagebox.showwarning("Ошибка", "Все поля обязательны для заполнения.")
            return

        if not self.validate_date(date):
            messagebox.showerror("Неверный формат", "Дата должна быть в формате YYYY-MM-DD (например, 2026-05-10).")
            return

        if not self.validate_duration(duration):
            messagebox.showerror("Неверное значение", "Длительность должна быть положительным целым числом (минут).")
            return

        duration_int = int(duration)

        # Добавляем
        new_entry = {"date": date, "type": train_type, "duration": duration_int}
        self.trainings.append(new_entry)
        self.save_data()

        # Очищаем поля ввода
        self.entry_date.delete(0, "end")
        self.combo_type.set("")
        self.entry_duration.delete(0, "end")

        self.refresh_table()
        messagebox.showinfo("Успех", "Тренировка добавлена.")

    def apply_filter(self):
        """Применяет фильтры из панели фильтрации."""
        # Тип
        filter_type = self.filter_combo.get().strip()
        self.filter_type = filter_type if filter_type != "Все" else None

        # Дата
        filter_date = self.filter_entry_date.get().strip()
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка фильтра", "Дата в фильтре должна быть в формате YYYY-MM-DD.")
                return
            self.filter_date = filter_date
        else:
            self.filter_date = None

        self.refresh_table()

    def reset_filter(self):
        """Сбрасывает все фильтры и показывает все записи."""
        self.filter_type = None
        self.filter_date = None
        self.filter_combo.set("Все")
        self.filter_entry_date.delete(0, "end")
        self.refresh_table()

    def delete_training(self):
        """Удаляет выбранную в таблице тренировку."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Удаление", "Выберите тренировку для удаления.")
            return

        # Получаем данные выделенной строки
        item = self.tree.item(selected[0])
        values = item["values"]  # [date, type, duration]

        # Ищем соответствующую запись в self.trainings
        # Поскольку у нас может быть несколько одинаковых, удаляем первое совпадение
        date, typ, dur = values[0], values[1], int(values[2])
        idx_to_delete = -1
        for i, t in enumerate(self.trainings):
            if t["date"] == date and t["type"] == typ and t["duration"] == dur:
                idx_to_delete = i
                break

        if idx_to_delete >= 0:
            if messagebox.askyesno("Подтверждение", "Удалить выбранную тренировку?"):
                del self.trainings[idx_to_delete]
                self.save_data()
                self.refresh_table()
        else:
            messagebox.showerror("Ошибка", "Запись не найдена в данных.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()