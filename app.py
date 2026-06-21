import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Файл для хранения расходов
EXPENSES_FILE = "expenses.json"

# Загрузка данных
def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        with open(EXPENSES_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# Сохранение данных
def save_expenses(expenses):
    with open(EXPENSES_FILE, "w", encoding="utf-8") as f:
        json.dump(expenses, f, ensure_ascii=False, indent=4)

# Валидация даты
def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Добавление расхода
def add_expense():
    amount_str = entry_amount.get().strip()
    category = entry_category.get().strip()
    date = entry_date.get().strip()

    # Валидация
    if not amount_str or not category or not date:
        messagebox.showwarning("Ошибка", "Все поля обязательны!")
        return
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Ошибка", "Сумма должна быть положительным числом!")
        return
    if not is_valid_date(date):
        messagebox.showwarning("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
        return

    # Добавление
    expense = {"сумма": amount, "категория": category, "дата": date}
    expenses.append(expense)
    save_expenses(expenses)
    update_table()
    clear_inputs()
    messagebox.showinfo("Успех", "Расход добавлен!")

# Обновление таблицы
def update_table(data=None):
    for row in tree.get_children():
        tree.delete(row)
    data = data or expenses
    for exp in data:
        tree.insert("", "end", values=(exp["сумма"], exp["категория"], exp["дата"]))

# Очистка полей ввода
def clear_inputs():
    entry_amount.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_date.delete(0, tk.END)

# Фильтрация по категории
def filter_by_category():
    category = filter_category.get().strip()
    if not category:
        update_table()
        return
    filtered = [e for e in expenses if e["категория"].lower() == category.lower()]
    update_table(filtered)

# Фильтрация по дате (период)
def filter_by_date():
    start_date = filter_start.get().strip()
    end_date = filter_end.get().strip()

    if not start_date or not end_date:
        messagebox.showwarning("Ошибка", "Введите обе даты!")
        return
    if not (is_valid_date(start_date) and is_valid_date(end_date)):
        messagebox.showwarning("Ошибка", "Неверный формат даты!")
        return

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    filtered = [
        e for e in expenses
        if start <= datetime.strptime(e["дата"], "%Y-%m-%d") <= end
    ]
    update_table(filtered)

# Подсчёт суммы за период
def calculate_total():
    start_date = filter_start.get().strip()
    end_date = filter_end.get().strip()

    if not start_date or not end_date:
        messagebox.showwarning("Ошибка", "Введите обе даты для расчёта!")
        return
    if not (is_valid_date(start_date) and is_valid_date(end_date)):
        messagebox.showwarning("Ошибка", "Неверный формат даты!")
        return

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    total = sum(
        e["сумма"] for e in expenses
        if start <= datetime.strptime(e["дата"], "%Y-%m-%d") <= end
    )
    messagebox.showinfo("Итого", f"Общая сумма расходов: {total:.2f} ₽")

# GUI
root = tk.Tk()
root.title("💰 Expense Tracker — Трекер расходов")
root.geometry("800x600")
root.resizable(False, False)

# Загрузка данных
expenses = load_expenses()

# Ввод расхода
tk.Label(root, text="Добавить расход", font=("Arial", 14, "bold")).pack(pady=10)

frame_input = tk.Frame(root)
frame_input.pack(pady=5)

tk.Label(frame_input, text="Сумма (₽):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_amount = tk.Entry(frame_input, width=15)
entry_amount.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_input, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_category = tk.Entry(frame_input, width=15)
entry_category.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_input, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5, sticky="e")
entry_date = tk.Entry(frame_input, width=15)
entry_date.grid(row=0, column=5, padx=5, pady=5)

tk.Button(root, text="Добавить расход", command=add_expense, bg="lightgreen", font=("Arial", 10)).pack(pady=5)

# Таблица
tree = ttk.Treeview(root, columns=("Сумма", "Категория", "Дата"), show="headings", height=10)
tree.heading("Сумма", text="Сумма (₽)")
tree.heading("Категория", text="Категория")
tree.heading("Дата", text="Дата")
tree.column("Сумма", width=150, anchor="center")
tree.column("Категория", width=200, anchor="center")
tree.column("Дата", width=150, anchor="center")
tree.pack(pady=10, fill="x", padx=20)

update_table()  # Показать сохранённые данные

# Фильтрация
tk.Label(root, text="Фильтрация", font=("Arial", 12, "bold")).pack(pady=10)

frame_filter = tk.Frame(root)
frame_filter.pack(pady=5)

# По категории
tk.Label(frame_filter, text="Категория:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
filter_category = tk.Entry(frame_filter, width=15)
filter_category.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame_filter, text="Фильтр по категории", command=filter_by_category).grid(row=0, column=2, padx=10)

# По дате
tk.Label(frame_filter, text="С:").grid(row=0, column=3, padx=5, pady=5, sticky="e")
filter_start = tk.Entry(frame_filter, width=12)
filter_start.grid(row=0, column=4, padx=5, pady=5)

tk.Label(frame_filter, text="По:").grid(row=0, column=5, padx=5, pady=5, sticky="e")
filter_end = tk.Entry(frame_filter, width=12)
filter_end.grid(row=0, column=6, padx=5, pady=5)

tk.Button(frame_filter, text="Фильтр по дате", command=filter_by_date).grid(row=0, column=7, padx=10)
tk.Button(frame_filter, text="Посчитать сумму", command=calculate_total, bg="lightblue").grid(row=0, column=8, padx=10)

# Запуск
root.mainloop()
