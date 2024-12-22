import tkinter as tk
from tkinter import ttk, messagebox
from psycopg2 import connect, sql
from psycopg2.errors import UndefinedTable
from datetime import datetime

# Функция для подключения к базе данных
def connect_to_db(user, password):
    try:
        conn = connect(
            dbname="rental_store",
            user=user,
            password=password,
            host="localhost"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"Database connection failed: {e}")
        return None

# Авторизация
def login():
    email = email_entry.get()
    password = password_entry.get()

    global conn
    conn = connect_to_db(email, password)

    if conn:
        root.destroy()
        open_client_window(email)

# Главное окно клиента
def open_client_window(email):
    client_window = tk.Tk()
    client_window.title(f"Client - {email}")
    client_window.geometry("800x600")

    # Функция: показать все игры
    def display_games():
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM games;")
            rows = cur.fetchall()
            update_table(game_table, rows)
            cur.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch games: {e}")

    # Функция: поиск игр по жанру
    def search_games():
        genre = search_entry.get()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM games WHERE genre ILIKE %s;",
                (f"%{genre}%",)
            )
            rows = cur.fetchall()
            update_table(game_table, rows)
            cur.close()
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {e}")

    # Функция: оформление заказа
    def make_order():
        game_id = game_id_entry.get()
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO rentals (client_id, game_id, start_date, end_date)
                SELECT client_id, %s, %s, %s FROM clients WHERE email = %s;
                """,
                (game_id, start_date, end_date, email)
            )
            conn.commit()
            messagebox.showinfo("Success", "Order placed successfully!")
            cur.close()
        except Exception as e:
            messagebox.showerror("Error", f"Order failed: {e}")

    # Вспомогательная функция: обновить таблицу
    def update_table(table, rows):
        for row in table.get_children():
            table.delete(row)
        for row in rows:
            table.insert("", tk.END, values=row)

# Открытие отдельного окна для работы с историей заказов
    def open_order_history_window():
        order_history_window = tk.Toplevel(client_window)
        order_history_window.title("Order History")
        order_history_window.geometry("900x600")

        # Функция: показать всю историю заказов
        def display_history():
            try:
                cur = conn.cursor()
                table_name = f"rental_history_{email}"
                cur.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name)))
                rows = cur.fetchall()
                update_table(history_table, rows)
                cur.close()
            except UndefinedTable:
                messagebox.showerror("Error", "History table does not exist.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch history: {e}")

        # Функция: поиск в истории заказов по game_id
        def search_history():
            game_id = search_history_entry.get()
            try:
                cur = conn.cursor()
                table_name = f"rental_history_{email}"
                cur.execute(
                    sql.SQL("SELECT * FROM {} WHERE game_id = %s;").format(sql.Identifier(table_name)),
                    (game_id,)
                )
                rows = cur.fetchall()
                update_table(history_table, rows)
                cur.close()
            except Exception as e:
                messagebox.showerror("Error", f"Search failed: {e}")

        # Функция: удалить заказы по game_id
        def delete_orders_by_game():
            game_id = search_history_entry.get()
            try:
                cur = conn.cursor()
                table_name = f"rental_history_{email}"
                cur.execute(
                    sql.SQL("DELETE FROM {} WHERE game_id = %s;").format(sql.Identifier(table_name)),
                    (game_id,)
                )
                conn.commit()
                messagebox.showinfo("Success", f"Orders with Game ID {game_id} deleted successfully!")
                display_history()  # Обновляем таблицу истории после удаления
                cur.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete orders: {e}")

        # Функция: удалить заказ по ID заказа
        def delete_order_by_id():
            order_id = order_id_entry.get()
            try:
                cur = conn.cursor()
                table_name = f"rental_history_{email}"
                cur.execute(
                    sql.SQL("DELETE FROM {} WHERE rental_id = %s;").format(sql.Identifier(table_name)),
                    (order_id,)
                )
                conn.commit()
                messagebox.showinfo("Success", f"Order {order_id} deleted successfully!")
                display_history()  # Обновляем таблицу истории после удаления
                cur.close()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete order: {e}")

        # Виджеты окна истории заказов
        ttk.Label(order_history_window, text="Order History").pack()
        search_history_frame = tk.Frame(order_history_window)
        search_history_frame.pack()
        search_history_entry = ttk.Entry(search_history_frame)
        search_history_entry.pack(side=tk.LEFT, padx=5)
        search_history_button = ttk.Button(search_history_frame, text="Search by Game ID", command=search_history)
        search_history_button.pack(side=tk.LEFT, padx=5)
        delete_by_game_button = ttk.Button(search_history_frame, text="Delete by Game ID", command=delete_orders_by_game)
        delete_by_game_button.pack(side=tk.LEFT, padx=5)

        history_table = ttk.Treeview(
            order_history_window,
            columns=("Rental ID", "Client ID", "Game ID", "Start Date", "End Date", "Discount", "Total Price"),
            show="headings"
        )
        for col in ("Rental ID", "Client ID", "Game ID", "Start Date", "End Date", "Discount", "Total Price"):
            history_table.heading(col, text=col)
        history_table.pack()

        delete_frame = tk.Frame(order_history_window)
        delete_frame.pack(pady=5)
        ttk.Label(delete_frame, text="Enter Rental ID to delete:").pack(side=tk.LEFT)
        order_id_entry = ttk.Entry(delete_frame)
        order_id_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(delete_frame, text="Delete by Rental ID", command=delete_order_by_id).pack(side=tk.LEFT, padx=5)

        # Кнопка для загрузки всей истории
        ttk.Button(order_history_window, text="Display History", command=display_history).pack(pady=10)

    # Виджеты главного окна
    ttk.Label(client_window, text="Games").pack()
    search_frame = tk.Frame(client_window)
    search_frame.pack()
    search_entry = ttk.Entry(search_frame)
    search_entry.pack(side=tk.LEFT, padx=5)
    search_button = ttk.Button(search_frame, text="Search by Genre", command=search_games)
    search_button.pack(side=tk.LEFT, padx=5)
    game_table = ttk.Treeview(client_window, columns=("ID", "Name", "Genre", "Description", "Price"), show="headings")
    for col in ("ID", "Name", "Genre", "Description", "Price"):
        game_table.heading(col, text=col)
    game_table.pack()

    order_frame = tk.Frame(client_window)
    order_frame.pack(pady=10)
    ttk.Label(order_frame, text="Game ID:").grid(row=0, column=0, padx=5, pady=5)
    game_id_entry = ttk.Entry(order_frame)
    game_id_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(order_frame, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    start_date_entry = ttk.Entry(order_frame)
    start_date_entry.grid(row=1, column=1, padx=5, pady=5)
    ttk.Label(order_frame, text="End Date (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5)
    end_date_entry = ttk.Entry(order_frame)
    end_date_entry.grid(row=2, column=1, padx=5, pady=5)
    ttk.Button(order_frame, text="Make Order", command=make_order).grid(row=3, columnspan=2, pady=10)

    ttk.Button(client_window, text="Load Games", command=display_games).pack(pady=10)
    ttk.Button(client_window, text="Show Order History", command=open_order_history_window).pack(pady=10)

    client_window.mainloop()

# Окно авторизации
root = tk.Tk()
root.title("Login")
root.geometry("400x200")
ttk.Label(root, text="Email:").pack(pady=5)
email_entry = ttk.Entry(root)
email_entry.pack(pady=5)
ttk.Label(root, text="Password:").pack(pady=5)
password_entry = ttk.Entry(root, show="*")
password_entry.pack(pady=5)
ttk.Button(root, text="Login", command=login).pack(pady=10)
root.mainloop()
