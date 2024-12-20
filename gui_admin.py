import tkinter as tk
from tkinter import messagebox
from psycopg2 import connect, sql

def add_client_to_db():
    name = entry_name.get()
    email = entry_email.get()
    phone = entry_phone.get()
    
    try:
        conn = connect(
            dbname="rental_store",
            user="rental_user",
            password="secure_password",
            host="localhost"
        )
        cur = conn.cursor()
        cur.execute("SELECT add_client(%s, %s, %s);", (name, email, phone))
        conn.commit()
        messagebox.showinfo("Success", "Client added successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        cur.close()
        conn.close()

# GUI setup
root = tk.Tk()
root.title("Add Client")

tk.Label(root, text="Name").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="Email").grid(row=1, column=0)
entry_email = tk.Entry(root)
entry_email.grid(row=1, column=1)

tk.Label(root, text="Phone").grid(row=2, column=0)
entry_phone = tk.Entry(root)
entry_phone.grid(row=2, column=1)

btn_add = tk.Button(root, text="Add Client", command=add_client_to_db)
btn_add.grid(row=3, column=0, columnspan=2)

root.mainloop()
