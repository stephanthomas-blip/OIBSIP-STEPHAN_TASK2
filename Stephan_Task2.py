import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime
import matplotlib.pyplot as plt

try:
    conn = psycopg2.connect(
        host="localhost",
        database="Masterpiece",
        user="postgres",
        password="password",
        port="5432"
    )

    cursor = conn.cursor()

except Exception as e:
    messagebox.showerror(
        "Database Connection Error",
        str(e)
    )
    raise SystemExit

def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal Weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def save_record(name, weight, height, bmi, category):

    query = """
    INSERT INTO bmi_records
    (name, weight, height, bmi, category, record_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            name,
            weight,
            height,
            bmi,
            category,
            datetime.now()
        )
    )

    conn.commit()

def calculate_bmi():

    try:

        name = name_entry.get().strip()

        if not name:
            messagebox.showwarning(
                "Input Error",
                "Please enter your name."
            )
            return

        weight = float(weight_entry.get())
        height = float(height_entry.get())

        if weight <= 0 or weight > 500:
            raise ValueError("Invalid Weight")

        if height <= 0 or height > 3:
            raise ValueError("Invalid Height")

        bmi = weight / (height ** 2)

        category = bmi_category(bmi)

        result_label.config(
            text=f"BMI = {bmi:.2f}\nCategory = {category}"
        )

        save_record(
            name,
            weight,
            height,
            bmi,
            category
        )

        load_history()

    except ValueError:
        messagebox.showerror(
            "Input Error",
            "Enter valid values."
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )

def load_history():

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT
        name,
        weight,
        height,
        bmi,
        category,
        record_date
        FROM bmi_records
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def show_graph():

    name = name_entry.get().strip()

    if not name:
        messagebox.showwarning(
            "Missing Name",
            "Enter a name first."
        )
        return

    cursor.execute("""
        SELECT bmi, record_date
        FROM bmi_records
        WHERE name = %s
        ORDER BY record_date
    """, (name,))

    data = cursor.fetchall()

    if not data:
        messagebox.showinfo(
            "No Data",
            "No records found."
        )
        return

    bmi_values = []
    dates = []

    for bmi, date in data:
        bmi_values.append(bmi)
        dates.append(date.strftime("%d-%m-%Y"))

    plt.figure(figsize=(8, 5))
    plt.plot(dates, bmi_values, marker='o')
    plt.title(f"{name}'s BMI Trend")
    plt.xlabel("Date")
    plt.ylabel("BMI")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def clear_fields():
    name_entry.delete(0, tk.END)
    weight_entry.delete(0, tk.END)
    height_entry.delete(0, tk.END)

    result_label.config(
        text="Enter Details and Calculate BMI"
    )

root = tk.Tk()
root.title("BMI Calculator")
root.geometry("1000x700")
root.configure(bg="#D9F3FF")


title = tk.Label(
    root,
    text="BMI CALCULATOR",
    font=("Arial", 24, "bold"),
    bg="#D9F3FF",
    fg="navy"
)

title.pack(pady=15)

input_frame = tk.Frame(root, bg="#D9F3FF")
input_frame.pack(pady=10)

tk.Label(
    input_frame,
    text="Name",
    bg="#D9F3FF",
    font=("Arial", 12)
).grid(row=0, column=0, padx=10, pady=10)

name_entry = tk.Entry(
    input_frame,
    width=30
)

name_entry.grid(row=0, column=1)

tk.Label(
    input_frame,
    text="Weight (kg)",
    bg="#D9F3FF",
    font=("Arial", 12)
).grid(row=1, column=0, padx=10, pady=10)

weight_entry = tk.Entry(
    input_frame,
    width=30
)

weight_entry.grid(row=1, column=1)

tk.Label(
    input_frame,
    text="Height (m)",
    bg="#D9F3FF",
    font=("Arial", 12)
).grid(row=2, column=0, padx=10, pady=10)

height_entry = tk.Entry(
    input_frame,
    width=30
)

height_entry.grid(row=2, column=1)

button_frame = tk.Frame(root, bg="#D9F3FF")
button_frame.pack(pady=15)

calculate_btn = tk.Button(
    button_frame,
    text="Calculate BMI",
    width=18,
    bg="green",
    fg="white",
    font=("Arial", 11, "bold"),
    command=calculate_bmi
)

calculate_btn.grid(row=0, column=0, padx=10)

graph_btn = tk.Button(
    button_frame,
    text="Show Trend Graph",
    width=18,
    bg="orange",
    font=("Arial", 11, "bold"),
    command=show_graph
)

graph_btn.grid(row=0, column=1, padx=10)

clear_btn = tk.Button(
    button_frame,
    text="Clear",
    width=18,
    bg="red",
    fg="white",
    font=("Arial", 11, "bold"),
    command=clear_fields
)

clear_btn.grid(row=0, column=2, padx=10)

result_label = tk.Label(
    root,
    text="Enter Details and Calculate BMI",
    font=("Arial", 18, "bold"),
    bg="#D9F3FF",
    fg="darkred"
)

result_label.pack(pady=15)


history_label = tk.Label(
    root,
    text="BMI History Records",
    font=("Arial", 16, "bold"),
    bg="#D9F3FF"
)

history_label.pack()


columns = (
    "Name",
    "Weight",
    "Height",
    "BMI",
    "Category",
    "Date"
)

tree = ttk.Treeview(
    root,
    columns=columns,
    show="headings",
    height=15
)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=150)

tree.pack(
    fill="both",
    expand=True,
    padx=10,
    pady=10
)


load_history()

root.mainloop()

cursor.close()
conn.close()
