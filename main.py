import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, askyesno
import sqlite3

with sqlite3.connect("pojazdy.db") as db:
    cursor = db.cursor()
from datetime import datetime
import re

# TODO Zmienić ikone potwierdzenia
# TODO Uprządkować kod i porobić opisy

cursor.execute(""" CREATE TABLE IF NOT EXISTS pojazdy( id integer PRIMARY KEY AUTOINCREMENT, 
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


def insert_pobranie_to_db(nrrej, data, osoba, operator):
    return f""" INSERT INTO pojazdy(nr_rej, data_pobrania, osoba_pobranie, operator_pobranie) 
        VALUES("{nrrej}", "{data}", "{osoba}", "{operator}"); """


def zastosuj_pobranie():
    now = datetime.now().strftime("%y-%m-%d %H:%M")
    teczka = pobranie_entry.get().upper()
    osoba = combobox_pobierajacy.get().title()
    operator = combobox_operator.get().title()

    if inna_data_pobrania.get():
        if format_inna_data(data_pobrania_entry.get()):
            now = data_pobrania_entry.get()
        else:
            return showerror("Błąd", "Sprawdź czy podana data jest prawidłowa. "
                                     "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")

    if sprawdz_czy_dubel(teczka):
        return showerror("Błąd", f"Teczka o nr '{teczka}' została już pobrana i nie odnotowano jej zwrotu.")

    if teczka == "" or osoba == "":
        # Jeśli nie wpisze się TR lub pobierającego wyskoczy błąd
        return showerror("Błąd", "Pola  'Numer TR' i 'Pobierający akta' są obowiązkowe!")

    elif check_tr(teczka):
        # Jeśli nr TR jest poprawny - wstaw dane do bazy
        cursor.execute(insert_pobranie_to_db(teczka, now, osoba, operator))
        db.commit()

    elif not check_tr(teczka):
        # Jeśli nr TR jest błędny pokaż zapytanie
        poprawna_tr = askyesno("Błąd",
                               f"Numer TR powinien składać się z wyróżnika powiatu, ODSTĘPU i pojemności.\n"
                               f"Czy '{teczka}' to na pewno poprawny numer rejestracyjny?")
        if poprawna_tr:
            # Po zatwierdzeniu wprowadzi dane do bazy
            cursor.execute(insert_pobranie_to_db(teczka, now, osoba, operator))
            db.commit()

    potwierdzenie_zapisu(teczka, now, osoba, operator)


def potwierdzenie_zapisu(tr, data, pobierajacy, operator):
    # Funkcja wyszukuje czy w bazie jest zapisany podany rekord,
    # jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych
    wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE nr_rej = "{tr}" 
                                                    AND data_pobrania >= "{data}" 
                                                    AND osoba_pobranie = "{pobierajacy}" 
                                                    AND operator_pobranie = "{operator}" 
                                                    AND data_zwrotu IS NULL; """
    cursor.execute(wyszukanie_wpisu)
    if len(cursor.fetchall()) == 1:
        for n in cursor.execute(wyszukanie_wpisu):
            archeo_data.insert("", tk.END, values=n)
        img = tk.PhotoImage(file="check.gif")
        potwierdzenie_label.configure(image=img,
                                      text=f"Prawidłowo zapisano pobranie teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                                      compound="left", font="Helvetica 8")
        potwierdzenie_label.image = img


def zastosuj_zwrot():
    now = datetime.now().strftime("%y-%m-%d %H:%M")
    teczka = zwrot_entry.get().upper()
    osoba = combobox_zwracajacy.get().title()
    operator = combobox_operator.get().title()

    if inna_data_zwrot.get():
        if format_inna_data(data_zwrotu_entry.get()):
            now = data_zwrotu_entry.get()
        else:
            return showerror("Błąd", "Sprawdź czy podana data jest prawidłowa. "
                                     "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")

    if teczka == "" or osoba == "":
        # Jeśli nie wpisze się TR lub pobierającego wyskoczy błąd
        return showerror("Błąd", "Pola  'Numer TR' i 'Pobierający akta' są obowiązkowe!")

    cursor.execute(f""" SELECT * FROM pojazdy WHERE data_zwrotu IS NULL AND nr_rej = "{teczka}"; """)
    if len(cursor.fetchall()) == 0:
        showerror("Błąd", f"Nie znaleziono niezwróconej teczki o nr '{teczka}'.")
    else:
        cursor.execute(f""" UPDATE pojazdy SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", 
    operator_zwrot = "{operator}" WHERE nr_rej = "{teczka}" AND data_zwrotu IS NULL; """)
        db.commit()

    potwierdzenie_zwrotu(teczka, now, osoba, operator)


def potwierdzenie_zwrotu(tr, data, pobierajacy, operator):
    # Funkcja wyszukuje czy podana teczka występuje z podaną datą zwrotu.
    # Jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych
    wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE nr_rej = "{tr}" 
                                                    AND data_zwrotu >= "{data}" 
                                                    AND osoba_zwrot = "{pobierajacy}" 
                                                    AND operator_zwrot = "{operator}"; """
    cursor.execute(wyszukanie_wpisu)
    if len(cursor.fetchall()) >= 1:
        for n in cursor.execute(wyszukanie_wpisu):
            archeo_data.insert("", tk.END, values=n)
        img = tk.PhotoImage(file="check.gif")
        potwierdzenie_zwrotu_label.configure(image=img,
                                      text=f"Prawidłowo odnotowano zwrot teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                                      compound="left", font="Helvetica 8")
        potwierdzenie_zwrotu_label.image = img


def check_tr(nr_rej):
    # Funkcja sprawdzająca czy podany nr TR jest zgodny ze wzorem
    pattern = re.compile(r"^[A-Z]{1,3}\s[A-Z\d]{3,5}$|^[A-Z]\d\s[A-Z\d]{3,5}$")
    if pattern.search(nr_rej):
        return True
    else:
        return False


def enable_frame(event):
    # Funkcja aktywująca okienka po wybraniu operatora
    pobranie_entry.config(state="enabled")
    combobox_pobierajacy.config(state="enabled")
    zwrot_entry.config(state="enabled")
    combobox_zwracajacy.config(state="enabled")


def show_all():
    # Funkcja do przycisku "Pokaż wszystko", żeby wyświetlić wszystkie dane z bazy
    for n in cursor.execute(""" SELECT * FROM pojazdy """):
        archeo_data.insert("", tk.END, values=n)


def clear():
    # Funkcja do przycisku "Wyczyść". Usuwa wszystkie wiersze w polu z danymi z bazy, lub tylko zaznaczoną
    if archeo_data.selection():
        selected_data = archeo_data.selection()
        archeo_data.delete(selected_data)
    else:
        archeo_data.delete(*archeo_data.get_children())


def inna_data():
    # Jeśli zaznaczy się checkbox uaktywni się pole na date i przeniesie tam 'focus'
    if inna_data_pobrania.get():
        data_pobrania_entry.config(state="enable")
        data_pobrania_entry.delete(0, "end")
        data_pobrania_entry.focus_set()
    # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem
    if not inna_data_pobrania.get():
        data_pobrania_entry.insert(0, "RRRR-MM-DD")
        data_pobrania_entry.config(state="disabled")


def inna_data_zwrotu():
    # Jeśli zaznaczy się checkbox uaktywni się pole na date i przeniesie tam 'focus'
    if inna_data_zwrot.get():
        data_zwrotu_entry.config(state="enable")
        data_zwrotu_entry.delete(0, "end")
        data_zwrotu_entry.focus_set()
    # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem
    if not inna_data_zwrot.get():
        data_zwrotu_entry.insert(0, "RRRR-MM-DD")
        data_zwrotu_entry.config(state="disabled")


def format_inna_data(data):
    # Funkcja sprawdzająca czy podana data ma prawidłowy format
    format_daty = re.compile(r"^20\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[1-2]\d|3[0-1])$")
    if format_daty.search(data):
        return True
    else:
        return False


def sprawdz_czy_dubel(tr):
    # Funkcja sprawdza czy w bazie istnieje już wpis z podanymi danymi bez daty zwrotu
    wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE nr_rej = "{tr}" AND data_zwrotu IS NULL; """
    cursor.execute(wyszukanie_wpisu)
    if len(cursor.fetchall()) > 0:
        return True
    else:
        return False


# WINDOW SIZE & LOCATION
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = 1400
window_height = 700

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 1.8)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(True, True)

# NOTEBOOK WIDGET
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True, fill="both")

pojazd = ttk.Frame(notebook)
kierowca = ttk.Frame(notebook)
wyszukiwanie = ttk.Frame(notebook)

pojazd.pack(fill="both", expand=True)
kierowca.pack(fill="both", expand=True)
wyszukiwanie.pack(fill="both", expand=True)

notebook.add(pojazd, text="Pojazdy")
notebook.add(kierowca, text="Kierowcy")
notebook.add(wyszukiwanie, text="Wyszukiwanie")

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
    font=("Arial", 15, "bold"),
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
    background="dark grey",
    foreground="white",
    font="Arial 13 bold"
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

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ LEFT FRAME @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
tablica = tk.PhotoImage(file="tablica.gif")
tablica_label = ttk.Label(left_frame, image=tablica)
tablica_label.place(relx=0.457, rely=0.064)

# NUMER REJESTRACYJNY
pobranie_label = ttk.Label(left_frame, text="Numer TR:", background="yellow")
pobranie_entry = ttk.Entry(left_frame, state="disabled", width=12, justify="center", font=("Helvetica", 13, "bold"))

# OSOBA POBIERAJĄCA
pobierajacy_label = ttk.Label(left_frame, text="Pobierający akta:")
combobox_pobierajacy = ttk.Combobox(left_frame, state="disabled")
combobox_pobierajacy["values"] = ["Błażej Prajs",
                                  "Marzena Ciszek",
                                  "Wojciech Kaczmarek",
                                  ]

# INNA DATA POBRANIA
inna_data_pobrania = tk.BooleanVar()
data_pobrania_check = ttk.Checkbutton(left_frame, onvalue=True, offvalue=False, text="Inna data",
                                      variable=inna_data_pobrania, command=inna_data)
# wzor_data = tk.StringVar(value="rrrr-mm-dd")
data_pobrania_entry = ttk.Entry(left_frame)
data_pobrania_entry.insert(0, "RRRR-MM-DD")
data_pobrania_entry.config(state="disabled")

# ZASTOSUJ - PRZYCISK
zastosuj_pobranie_button = ttk.Button(left_frame, text="Zastosuj", command=zastosuj_pobranie)

pobranie_label.grid(column=1, row=0, sticky="E", pady=20, padx=30)
pobranie_entry.grid(column=2, row=0, sticky="W", )
pobierajacy_label.grid(column=1, row=1, sticky="E", pady=10)
combobox_pobierajacy.grid(column=2, row=1, sticky="WE")
data_pobrania_check.grid(column=1, row=2, sticky="E", pady=10)
data_pobrania_entry.grid(column=2, row=2, sticky="W")
zastosuj_pobranie_button.grid(column=1, columnspan=2, row=3, sticky="WE", pady=5)
potwierdzenie_label = tk.Label(left_frame)
potwierdzenie_label.grid(column=0, columnspan=4, row=4)
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ RIGHT FRAME @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
tablica2 = tk.PhotoImage(file="tablica.gif")
tablica_label2 = ttk.Label(right_frame, image=tablica2)
tablica_label2.place(relx=0.455, rely=0.064)

# TABLICA REJESTRACYJNA
zwrot_label = ttk.Label(right_frame, text="Numer TR", background="pink")
zwrot_entry = ttk.Entry(right_frame, state="disabled", width=12, justify="center", font=("Helvetica", 13, "bold"))

# OSBOA ZWRACAJĄCA
zwracajacy_label = ttk.Label(right_frame, text="Zwracający akta:")
combobox_zwracajacy = ttk.Combobox(right_frame, state="disabled")
combobox_zwracajacy["values"] = ["Błażej Prajs",
                                 "Marzena Ciszek",
                                 "Wojciech Kaczmarek",
                                 ]

# INNA DATA ZWROTU
inna_data_zwrot = tk.BooleanVar()
data_zwrotu_check = ttk.Checkbutton(right_frame, onvalue=True, offvalue=False, text="Inna data",
                                      variable=inna_data_zwrot, command=inna_data_zwrotu)
# wzor_data = tk.StringVar(value="rrrr-mm-dd")
data_zwrotu_entry = ttk.Entry(right_frame)
data_zwrotu_entry.insert(0, "RRRR-MM-DD")
data_zwrotu_entry.config(state="disabled")

# ZASTOSUJ PRZYCISK
zastosuj_zwrot_button = ttk.Button(right_frame, text="Zastosuj", command=zastosuj_zwrot)

zwrot_label.grid(column=1, row=0, sticky="E", pady=20, padx=30)
zwrot_entry.grid(column=2, row=0, sticky="W")
zwracajacy_label.grid(column=1, row=1, sticky="E", pady=10)
combobox_zwracajacy.grid(column=2, row=1, sticky="WE")
data_zwrotu_check.grid(column=1, row=2, sticky="E", pady=10)
data_zwrotu_entry.grid(column=2, row=2, sticky="W")
zastosuj_zwrot_button.grid(column=1, columnspan=2, row=3, pady=5, sticky="WE")
potwierdzenie_zwrotu_label = tk.Label(right_frame)
potwierdzenie_zwrotu_label.grid(column=0, columnspan=4, row=4)

# HORIZONTAL SEPARATOR
horizontal_separator = ttk.Separator(pojazd, orient="horizontal", cursor="spider")

horizontal_separator.grid(column=1,
                          columnspan=3,
                          row=8,
                          ipadx=window_width,
                          pady=15,
                          )

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ DATABASE AREA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
columns = ("id", "TR", "Data pobrania", "Pobierający", "Operator pobranie",
           "Data zwrotu", "Zwracający", "Operator zwrot")

archeo_data = ttk.Treeview(pojazd, columns=columns, show='headings', displaycolumns='#all', height=10)

for column in columns:
    archeo_data.heading(column, text=column, anchor='center')

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

# SHOW ALL BUTTON
show_all_button = ttk.Button(pojazd, text="Pokaż wszystko", command=show_all)
show_all_button.grid(column=3, row=12, sticky="E")

# CLEAR BUTTON
clear_button = ttk.Button(pojazd, text="Clear", command=clear)
clear_button.grid(column=1, row=12, sticky="W")

root.mainloop()
