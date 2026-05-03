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
        self.data_file = "trainings.json"
        self.trainings = []
        # Здесь потом будет интерфейс и логика
        self.load_data()

    def load_data(self):
        pass  # загрузим позже

    def save_data(self):
        pass  # сохраним позже

    def refresh_table(self):
        pass  # обновление таблицы позже

    def add_training(self):
        pass  # добавление позже

    def apply_filter(self):
        pass  # фильтрация позже

    def reset_filter(self):
        pass  # сброс позже

    def delete_training(self):
        pass  # удаление позже

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()