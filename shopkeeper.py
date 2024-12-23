import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from psycopg2 import connect

# Функция для получения списка таблиц из базы данных
def get_table_names():
    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name NOT LIKE 'rental_history_%';
        """)
        
        tables = cur.fetchall()
        cur.close()
        conn.close()
        return [table[0] for table in tables]
    except Exception as e:
        messagebox.showerror("Error", f"Error getting table names: {e}")
        return []

# Функция для получения списка столбцов для выбранной таблицы
def get_column_names(table_name):
    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s;
        """, (table_name,))
        columns = cur.fetchall()
        cur.close()
        conn.close()
        return [column[0] for column in columns]
    except Exception as e:
        messagebox.showerror("Error", f"Error getting column names: {e}")
        return []

# Функция для отображения данных таблицы
def display_table_data(table_name):
    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()

        # Вызов SQL-функции вместо прямого SQL-запроса
        cur.execute("SELECT row_data FROM get_table_data(%s)", (table_name,))
        rows = cur.fetchall()

        # Если данные есть, разбираем JSON
        if rows:
            # Преобразуем JSON в словари
            parsed_rows = [row[0] for row in rows]
            # Получаем названия столбцов из ключей первого JSON-объекта
            columns = list(parsed_rows[0].keys())
        else:
            parsed_rows = []
            columns = []

        cur.close()
        conn.close()

        # Очистка старых данных
        for row in treeview.get_children():
            treeview.delete(row)

        # Установка столбцов в Treeview
        treeview["columns"] = columns
        treeview["show"] = "headings"

       # Настройка заголовков столбцов
        for column in columns:
            treeview.heading(column, text=column)  # Заголовок столбца
            treeview.column(column, anchor="w", stretch=True)  # Настройка ширины

        # Добавление новых данных
        for row in parsed_rows:
            treeview.insert("", "end", values=[row[col] for col in columns])

    except Exception as e:
        messagebox.showerror("Error", f"Error displaying table data: {e}")

# Функция для обновления записи
def update_row_in_db():
    table_name = table_combobox.get()
    column_name = column_combobox.get()
    new_value = entry_new_value.get()
    condition = entry_condition.get()

    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("SELECT update_row(%s, %s, %s, %s);", (table_name, column_name, new_value, condition))
        conn.commit()
        messagebox.showinfo("Success", "Row updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")
    finally:
        cur.close()
        conn.close()

# Функция для удаления записи
def delete_row_from_db():
    table_name = table_combobox.get()
    condition = entry_condition.get()

    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("SELECT delete_row(%s, %s);", (table_name, condition))
        conn.commit()
        messagebox.showinfo("Success", "Row deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")
    finally:
        cur.close()
        conn.close()

# Функции для добавления клиента
def add_client_to_db(name, email, phone, password):
    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()
        # Вызов хранимой процедуры
        cur.execute("SELECT add_client_and_user(%s, %s, %s, %s);", (name, email, phone, password))
        conn.commit()
        messagebox.showinfo("Success", "Client and database user added successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error: {e}")
    finally:
        cur.close()
        conn.close()

def new_client_gui_window():

    def add_client():
        name = entry_name.get()
        email = entry_email.get()
        phone = entry_phone.get()
        password = entry_password.get()

        if not name or not email or not phone or not password:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Передаем введенные данные в функцию добавления
        add_client_to_db(name, email, phone, password)

    # Создание GUI
    newClientWindow = tk.Tk()
    newClientWindow.title("Shopkeeper - Add Client")

    # Поля ввода данных клиента
    tk.Label(newClientWindow, text="Client Name").grid(row=0, column=0)
    entry_name = tk.Entry(newClientWindow)
    entry_name.grid(row=0, column=1)

    tk.Label(newClientWindow, text="Client Email").grid(row=1, column=0)
    entry_email = tk.Entry(newClientWindow)
    entry_email.grid(row=1, column=1)

    tk.Label(newClientWindow, text="Client Phone").grid(row=2, column=0)
    entry_phone = tk.Entry(newClientWindow)
    entry_phone.grid(row=2, column=1)

    tk.Label(newClientWindow, text="Client Password").grid(row=3, column=0)
    entry_password = tk.Entry(newClientWindow, show="*")
    entry_password.grid(row=3, column=1)

    # Кнопка для добавления клиента
    btn_add_client = tk.Button(newClientWindow, text="Add Client", command=add_client)
    btn_add_client.grid(row=4, column=0, columnspan=2)

    # Запуск GUI
    newClientWindow.mainloop()

# Функция для очистки текущей таблицы
def clear_selected_table():
    table_name = table_combobox.get()
    if not table_name:
        messagebox.showerror("Error", "Please select a table.")
        return

    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("SELECT clear_table(%s);", (table_name,))
        conn.commit()
        messagebox.showinfo("Success", f"Table '{table_name}' cleared successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error clearing table: {e}")
    finally:
        cur.close()
        conn.close()

# Функция для очистки всех таблиц
def clear_all_tables():
    if not messagebox.askyesno("Confirmation", "Are you sure you want to clear all tables? This action is irreversible."):
        return

    try:
        conn = connect(
            dbname="rental_store",
            user="shopkeeper",
            password="shopkeeper_password",
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("SELECT clear_all_tables();")
        conn.commit()
        messagebox.showinfo("Success", "All tables cleared successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error clearing all tables: {e}")
    finally:
        cur.close()
        conn.close()

# Создание окна GUI
root = tk.Tk()
root.title("Shopkeeper Interface")

# Элементы для выбора таблицы и столбца
tk.Label(root, text="Select Table").grid(row=0, column=0)
table_combobox = ttk.Combobox(root)
table_combobox.grid(row=0, column=1)

# Элементы для выбора столбца
tk.Label(root, text="Select Column").grid(row=1, column=0)
column_combobox = ttk.Combobox(root)
column_combobox.grid(row=1, column=1)

# Обновление комбобоксов с колонками, когда таблица выбрана
def update_column_combobox(event=None):
    table_name = table_combobox.get()
    columns = get_column_names(table_name)
    column_combobox['values'] = columns

# Заполнение комбобокса с таблицами при старте + я устал :((
table_combobox['values'] = get_table_names()

# обновлениe столбцов при изменении таблицы
table_combobox.bind("<<ComboboxSelected>>", update_column_combobox) 

# кнопки для отображения данных таблицы
def display_table():
    table_name = table_combobox.get()
    if table_name:
        display_table_data(table_name)

btn_display = tk.Button(root, text="Display Table", command=display_table)
btn_display.grid(row=2, column=0, columnspan=2)

# Treeview для отображения данных таблицы
treeview = ttk.Treeview(root)
treeview.grid(row=3, column=0, columnspan=4)

# обновлениe записи
tk.Label(root, text="New Value").grid(row=7, column=0)
entry_new_value = tk.Entry(root)
entry_new_value.grid(row=7, column=1)

tk.Label(root, text="Condition").grid(row=8, column=0)
entry_condition = tk.Entry(root)
entry_condition.grid(row=8, column=1)

btn_update = tk.Button(root, text="Update Row", command=update_row_in_db)
btn_update.grid(row=9, column=0, columnspan=2)

# удалениe записи
btn_delete = tk.Button(root, text="Delete Row", command=delete_row_from_db)
btn_delete.grid(row=10, column=0, columnspan=2)

# Добавление клиента
btn_create_client = tk.Button(root, text="Add new client", command=new_client_gui_window)
btn_create_client.grid(row=12, column=0, columnspan=1)

# очистка таблиц
btn_clear_table = tk.Button(root, text="Clear Table", command=clear_selected_table)
btn_clear_table.grid(row=6, column=0, columnspan=2)

btn_clear_all = tk.Button(root, text="Clear All Tables", command=clear_all_tables)
btn_clear_all.grid(row=11, column=0, columnspan=1, pady=5)

# Запуск GUI
root.mainloop()
