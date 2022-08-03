import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, askyesno
import sqlite3

with sqlite3.connect("pojazdy.db") as db:
    cursor = db.cursor()
from datetime import datetime
import re

# TODO sprawdzenie czy podane dane nie widnieją już w bazie po klinięciu zastosuj

cursor.execute(""" CREATE TABLE IF NOT EXISTS pojazdy(
id integer PRIMARY KEY AUTOINCREMENT, 
nr_rej text NOT NULL, 
data_pobrania text NOT NULL,
osoba_pobranie text NOT NULL, 
operator_pobranie text NOT NULL, 
data_zwrotu text, 
osoba_zwrot text, 
operator_zwrot text); """)

root = tk.Tk()
root.title("Archeo 2022")
root.attributes("-topmost", 1)


def zastosuj_pobranie():
    now = datetime.now().strftime("%y-%m-%d %H:%M")
    teczka = pobranie_entry.get().upper()
    osoba = combobox_pobierajacy.get().title()
    operator = combobox_operator.get().title()

    # TODO do optymalizacji

    if teczka == "" or osoba == "":
        showerror("Błąd", "Pola  'Numer TR' i 'Osoba pobierająca' są obowiązkowe!")
    elif check_tr(teczka):
        cursor.execute(f""" INSERT INTO pojazdy(nr_rej, data_pobrania, osoba_pobranie, operator_pobranie) 
        VALUES("{teczka}", "{now}", "{osoba}", "{operator}"); """)
        db.commit()

        for n in cursor.execute(""" SELECT * FROM pojazdy"""):
            archeo_data.insert("", tk.END, values=n)
    elif not check_tr(teczka):
        poprawna_tr = askyesno("Błędny numer rejestracyjny",
                               f"Numer TR powinien składać się z wyróżnika powiatu, ODSTĘPU i pojemnoci.\n"
                               f"Czy '{teczka}' to na pewno poprawny numer rejestracyjny?")
        if poprawna_tr:
            cursor.execute(f""" INSERT INTO pojazdy(nr_rej, data_pobrania, osoba_pobranie, operator_pobranie) 
            VALUES("{teczka}", "{now}", "{osoba}", "{operator}"); """)
            db.commit()

            for n in cursor.execute(""" SELECT * FROM pojazdy"""):
                archeo_data.insert("", tk.END, values=n)


def zastosuj_zwrot():
    now = datetime.now().strftime("%y-%m-%d %H:%M")
    teczka = zwrot_entry.get().upper()
    osoba = combobox_zwracajacy.get().title()
    operator = combobox_operator.get().title()

    cursor.execute(f""" UPDATE pojazdy SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", 
    operator_zwrot = "{operator}" WHERE nr_rej = "{teczka}"; """)
    db.commit()

    for n in cursor.execute(f""" SELECT * FROM pojazdy WHERE nr_rej = "{teczka}"; """):
        archeo_data.insert("", tk.END, values=n)


def check_tr(nr_rej):
    pattern = re.compile(r"^[A-Z]{1,3}\s[A-Z\d]{3,5}$|^[A-Z]\d\s[A-Z\d]{3,5}$")
    if pattern.search(nr_rej):
        return True
    else:
        return False


def enable_frame(event):
    pobranie_entry.config(state="enabled")
    combobox_pobierajacy.config(state="enabled")
    zwrot_entry.config(state="enabled")
    combobox_zwracajacy.config(state="enabled")

# WINDOW SIZE & LOCATION
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.80)

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 1.8)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(True, True)

# NOTEBOOK WIDGET
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

pojazd = ttk.Frame(notebook)
kierowca = ttk.Frame(notebook)

pojazd.pack(fill="both", expand=True)
kierowca.pack(fill="both", expand=True)

notebook.add(pojazd, text="Pojazdy")
notebook.add(kierowca, text="Kierowcy")

# CONFIGURE THE GRID
pojazd.columnconfigure(0, minsize=30)
pojazd.columnconfigure(1, weight=3)
pojazd.columnconfigure(2, weight=1)
pojazd.columnconfigure(3, weight=3)
pojazd.columnconfigure(4, minsize=30)

# WELCOME LABEL
welcome_label = ttk.Label(
    pojazd,
    text="Witaj w Archeo 2022!",
    background="green",
    foreground="white",
    font="Arial 15 bold",
    anchor="center",
)

welcome_label.grid(columnspan=5, row=0, sticky="WE", pady=5, ipady=5)

# COMBOBOX FRAME
combobox_frame = ttk.Frame(
    pojazd,
    borderwidth=15,
)

combobox_frame.grid(column=1, columnspan=3, row=2)

# LABEL & COMBOBOX IN COMBOBOX FRAME - SELECT OPERATOR
combobox_label = ttk.Label(
    combobox_frame,
    text="Wybierz operatora:",
    background="blue",
    foreground="white",
    font="Arial 13"
)

combobox_operator = ttk.Combobox(combobox_frame)

combobox_operator["values"] = ["Arkadiusz Wieloch",
                               "Barbara Naruszewicz",
                               "Dorota Sikora",
                               ]

combobox_label.grid(column=0, row=0, sticky="E")
combobox_operator.grid(column=1, row=0, sticky="W")

combobox_operator.bind("<KeyPress>", enable_frame)
combobox_operator.bind("<<ComboboxSelected>>", enable_frame, add="+")

# CENTER FRAMES

left_frame = ttk.LabelFrame(pojazd, text="Pobranie akt")
left_frame.columnconfigure(0, minsize=100)
left_frame.columnconfigure(1, weight=1)
left_frame.columnconfigure(2, weight=1)
left_frame.columnconfigure(3, minsize=100)

separator_frame = ttk.Frame(pojazd)

right_frame = ttk.LabelFrame(pojazd, text="Zwrot akt")
right_frame.columnconfigure(0, minsize=100)
right_frame.columnconfigure(1, weight=1)
right_frame.columnconfigure(2, weight=1)
right_frame.columnconfigure(3, minsize=100)

left_frame.grid(column=1, row=4, sticky="NSWE")
separator_frame.grid(column=2, row=4)
right_frame.grid(column=3, row=4, sticky="NSWE")

# SEPARATOR FRAME
vertical_separator = ttk.Separator(
    separator_frame,
    orient="vertical",
    cursor="man",
)

vertical_separator.grid(pady=10, ipady=100)

# LEFT FRAME
pobranie_label = ttk.Label(left_frame, text="Numer TR:", background="yellow")

pobranie_entry = ttk.Entry(left_frame, state="disabled")

pobierajacy_label = ttk.Label(left_frame, text="Pobierający akta:")

combobox_pobierajacy = ttk.Combobox(left_frame, state="disabled")

combobox_pobierajacy["values"] = ["Błażej Prajs",
                                  "Marzena Ciszek",
                                  "Wojciech Kaczmarek",
                                  ]

zastosuj_pobranie_button = ttk.Button(left_frame, text="Zastosuj", command=zastosuj_pobranie)

pobranie_label.grid(column=1, row=0, sticky="E", pady=30)
pobranie_entry.grid(column=2, row=0, sticky="WE")
pobierajacy_label.grid(column=1, row=1, sticky="E", pady=20)
combobox_pobierajacy.grid(column=2, row=1, sticky="WE")
zastosuj_pobranie_button.grid(column=1, columnspan=2, row=2, sticky="WE", pady=5)

# RIGHT FRAME
zwrot_label = ttk.Label(right_frame, text="Numer TR", background="pink")

zwracana_teczka = tk.StringVar()
zwrot_entry = ttk.Entry(right_frame, textvariable=zwracana_teczka, state="disabled")

zwracajacy_label = ttk.Label(right_frame, text="Zwracający akta:")

selected_zwracajacy = tk.StringVar()
combobox_zwracajacy = ttk.Combobox(right_frame, textvariable=selected_zwracajacy, state="disabled")

combobox_zwracajacy["values"] = ["Błażej Prajs",
                                 "Marzena Ciszek",
                                 "Wojciech Kaczmarek",
                                 ]

zastosuj_zwrot_button = ttk.Button(right_frame, text="Zastosuj", command=zastosuj_zwrot)

zwrot_label.grid(column=1, row=0, sticky="E", pady=30)
zwrot_entry.grid(column=2, row=0, sticky="WE")
zwracajacy_label.grid(column=1, row=1, sticky="E", pady=20)
combobox_zwracajacy.grid(column=2, row=1, sticky="WE")
zastosuj_zwrot_button.grid(column=1, columnspan=2, row=2, pady=5, sticky="WE")

# HORIZONTAL SEPARATOR
horizontal_separator = ttk.Separator(pojazd,
                                     orient="horizontal",
                                     cursor="man",
                                     )

horizontal_separator.grid(column=1,
                          columnspan=3,
                          row=8,
                          ipadx=window_width,
                          pady=15,
                          )

# DATABASE AREA
columns = ("id", "TR", "Data pobrania", "Pobierający", "Operator pobranie",
           "Data zwrotu", "Zwracający", "Operator zwrot")

archeo_data = ttk.Treeview(pojazd, columns=columns, show='headings', displaycolumns='#all')

for column in columns:
    archeo_data.heading(column, text=column)

archeo_data.column("id", width=60)
archeo_data.column("TR", width=120)
archeo_data.column("Data pobrania", width=120)
archeo_data.column("Data zwrotu", width=120)
archeo_data.column("Operator pobranie", width=140)

archeo_data.grid(column=1, columnspan=3, row=10, sticky="NSEW")

# SCROLLBAR
scrollbar = ttk.Scrollbar(pojazd, orient=tk.VERTICAL, command=archeo_data.yview)
archeo_data.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(column=4, row=10, sticky="NS")

# CLOSE BUTTON
zamknij_button = ttk.Button(pojazd, text="Zamknij", command=lambda: root.quit())
zamknij_button.grid(column=2, row=12, sticky="WE", padx=10, pady=10)

root.mainloop()
