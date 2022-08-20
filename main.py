import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, askyesno
import re
from datetime import datetime
import sqlite3


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Archeo 2022')

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS pojazdy( id integer PRIMARY KEY AUTOINCREMENT, 
                                                                    tr text NOT NULL, 
                                                                    data_pobrania text NOT NULL, 
                                                                    osoba_pobranie text NOT NULL, 
                                                                    operator_pobranie text NOT NULL, 
                                                                    data_zwrotu text, 
                                                                    osoba_zwrot text, 
                                                                    operator_zwrot text); """)
        self.db.close()

        # Set LABEL STYLE
        self.style = ttk.Style(self.root)
        self.style.configure('TLabel', font='Helvetica 12 bold')

        # Screen size
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Window size
        self.window_width = int(self.screen_width * 0.9)
        self.window_height = int(self.screen_height * 0.87)

        # Window location
        self.center_x = int(self.screen_width / 2 - self.window_width / 2)
        self.center_y = int(self.screen_height / 2 - self.window_height / 1.9)
        self.root.geometry(f'{self.window_width}x{self.window_height}+{self.center_x}+{self.center_y}')
        self.root.resizable(False, False)

        # MENU BAR
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu = tk.Menu(self.menubar, tearoff=0)

            # Menu items
        self.file_menu.add_command(label='Informacje')
        self.file_menu.add_command(label='Pusty')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Zamknij', command=self.root.destroy)

        self.help_menu.add_command(label='Witaj!')
        self.help_menu.add_command(label='O aplikacji..')

        self.menubar.add_cascade(label='Opcje', menu=self.file_menu)
        self.menubar.add_cascade(label='Więcej', menu=self.help_menu)

        # Welcome label
        self.welcome = tk.Label(self.root,
                                background='green',
                                foreground='white',
                                font='Arial 15 bold',
                                text='Witaj w Archeo 2022!'
                                )
        self.welcome.pack(fill='both', ipady=5)

        # OPERATOR select
        self.operator_values = ['Arkadiusz Wieloch',
                                'Barbara Naruszewicz',
                                'Dorota Sikora']
            # Operator Frame
        self.operator_frame = tk.Frame(self.root, background='dark grey')
        self.operator_frame.pack(pady=10, anchor='center')

            # Operator Label
        self.operator_label = tk.Label(self.operator_frame, anchor='center',
                                       text='Wybierz operatora:',
                                       background='dark grey',
                                       foreground='white',
                                       font='Arial 13 bold')
        self.operator_label.grid(column=0, row=0, sticky="E")

            # Operator Combobox
        self.operator_combobox = ttk.Combobox(self.operator_frame, values=self.operator_values, )
        self.operator_combobox.grid(column=1, row=0, sticky='W')

        self.operator_combobox.bind("<KeyPress>", self.enable_frames)
        self.operator_combobox.bind("<<ComboboxSelected>>", self.enable_frames, add="+")

        # NOTEBOOK WIDGET
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=5, expand=True, fill="both")

        self.pojazd = tk.Frame(self.notebook)
        self.kierowca = tk.Frame(self.notebook)
        self.wyszukiwanie = tk.Frame(self.notebook)

        self.pojazd.pack(fill="both", expand=True)
        self.kierowca.pack(fill="both", expand=True)
        self.wyszukiwanie.pack(fill="both", expand=True)

        self.notebook.add(self.pojazd, text="Pojazdy")
        self.notebook.add(self.kierowca, text="Kierowcy")
        self.notebook.add(self.wyszukiwanie, text="Wyszukiwanie")

        self.pojazd.columnconfigure(0, minsize=30)
        self.pojazd.columnconfigure(1, weight=3)
        self.pojazd.columnconfigure(2, weight=1)
        self.pojazd.columnconfigure(3, weight=3)
        self.pojazd.columnconfigure(4, minsize=30)

        # POBRANIE AKT POJAZDU --> pp
        self.pojazd_pobranie_labelframe = tk.LabelFrame(self.pojazd, text='Pobranie akt pojazdu')
        self.pojazd_pobranie_labelframe.grid(column=1, row=0, padx=30, sticky='NEWS', pady=20)

        self.pojazd_pobranie_labelframe.columnconfigure(0, minsize=100)
        self.pojazd_pobranie_labelframe.columnconfigure(1, weight=1)
        self.pojazd_pobranie_labelframe.columnconfigure(2, weight=1)
        self.pojazd_pobranie_labelframe.columnconfigure(3, minsize=100)

            # Tablica rejestracyjna
        self.pp_tablica_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Numer TR:', background='yellow')
        self.pp_tablica_label.grid(column=1, row=0, sticky='E', pady=20, padx=10)

        self.pp_tablica_img = tk.PhotoImage(file='tablica.gif')
        self.pp_tablica_img_label = ttk.Label(self.pojazd_pobranie_labelframe, image=self.pp_tablica_img)
        self.pp_tablica_img_label.grid(column=2, row=0, sticky='W')

        self.pp_tablica_entry = tk.Entry(self.pojazd_pobranie_labelframe, state='disabled', width=12,
                                         justify='center', font='Arial 13 bold')
        self.pp_tablica_entry.grid(column=2, row=0, sticky='W', padx=14)

            # Osoba pobierająca
        self.pp_osoba_values = ['Błażej Prajs',
                                'Marzena Ciszek',
                                'Dawid Łuczak']

        self.pp_osoba_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Osoba pobierająca:', background='pink')
        self.pp_osoba_label.grid(column=1, row=1, sticky='E', pady=10, padx=10)

        self.pp_osoba_combobox = ttk.Combobox(self.pojazd_pobranie_labelframe, values=self.pp_osoba_values,
                                              state='disabled')
        self.pp_osoba_combobox.grid(column=2, row=1, sticky='W')

            # Inna data pobrania
        self.pp_data = tk.BooleanVar()
        self.pp_data_check = ttk.Checkbutton(self.pojazd_pobranie_labelframe,
                                             onvalue=True,
                                             offvalue=False,
                                             text='Inna data',
                                             variable=self.pp_data,
                                             command=self.pp_inna_data)
        self.pp_data_check.grid(column=1, row=2, sticky='E', pady=10, padx=10)

        self.pp_data_entry = tk.Entry(self.pojazd_pobranie_labelframe)
        self.pp_data_entry.insert(0, 'RRRR-MM-DD')
        self.pp_data_entry.config(state='disabled')
        self.pp_data_entry.grid(column=2, row=2, sticky='W')

            # Przycisk 'Zastosuj' POBRANIE
        self.pp_zastosuj_button = tk.Button(self.pojazd_pobranie_labelframe, text='Zastosuj', width=40,
                                            command=self.pojazd_zastosuj_pobranie)
        self.pp_zastosuj_button.grid(column=1, columnspan=2, row=3, pady=20)

            # Potwierdzenie zapisu
        self.pp_potwierdzenie_label = tk.Label(self.pojazd_pobranie_labelframe)
        self.pp_potwierdzenie_label.grid(column=0, columnspan=4, row=4)

        # VERTICAL SEPARATOR - POJAZD
        self.pojazd_ver_separator = ttk.Separator(self.pojazd, orient='vertical')
        self.pojazd_ver_separator.grid(column=2, row=0, ipady=130, pady=10)

        # ZWROT AKT POJAZDU --> pz
        self.pojazd_zwrot_labelframe = tk.LabelFrame(self.pojazd, text='Zwrot akt pojazdu')
        self.pojazd_zwrot_labelframe.grid(column=3, row=0, padx=30, sticky='NEWS', pady=20)

        self.pojazd_zwrot_labelframe.columnconfigure(0, minsize=100)
        self.pojazd_zwrot_labelframe.columnconfigure(1, weight=1)
        self.pojazd_zwrot_labelframe.columnconfigure(2, weight=1)
        self.pojazd_zwrot_labelframe.columnconfigure(3, minsize=100)

            # Tablica rejestracyjna
        self.pz_tablica_label = ttk.Label(self.pojazd_zwrot_labelframe, text='Numer TR:', background='yellow')
        self.pz_tablica_label.grid(column=1, row=0, sticky='E', pady=20, padx=10)

        self.pz_tablica_img = tk.PhotoImage(file='tablica.gif')
        self.pz_tablica_img_label = ttk.Label(self.pojazd_zwrot_labelframe, image=self.pz_tablica_img)
        self.pz_tablica_img_label.grid(column=2, row=0, sticky='W')

        self.pz_tablica_entry = tk.Entry(self.pojazd_zwrot_labelframe, state='disabled', width=12,
                                         justify='center', font='Arial 13 bold')
        self.pz_tablica_entry.grid(column=2, row=0, sticky='W', padx=14)

            # Osoba zwracająca
        self.pz_osoba_values = ['Błażej Prajs',
                                'Marzena Ciszek',
                                'Dawid Łuczak']

        self.pz_osoba_label = ttk.Label(self.pojazd_zwrot_labelframe, text='Osoba zwracająca:', background='pink')
        self.pz_osoba_label.grid(column=1, row=1, sticky='E', pady=10, padx=10)

        self.pz_osoba_combobox = ttk.Combobox(self.pojazd_zwrot_labelframe, values=self.pp_osoba_values,
                                              state='disabled')
        self.pz_osoba_combobox.grid(column=2, row=1, sticky='W')

            # Inna data zwrotu
        self.pz_data = tk.BooleanVar()
        self.pz_data_check = ttk.Checkbutton(self.pojazd_zwrot_labelframe,
                                             onvalue=True,
                                             offvalue=False,
                                             text='Inna data',
                                             variable=self.pz_data,
                                             command=self.pz_inna_data)
        self.pz_data_check.grid(column=1, row=2, sticky='E', pady=10, padx=10)

        self.pz_data_entry = tk.Entry(self.pojazd_zwrot_labelframe)
        self.pz_data_entry.insert(0, 'RRRR-MM-DD')
        self.pz_data_entry.config(state='disabled')
        self.pz_data_entry.grid(column=2, row=2, sticky='W')

            # Przycisk 'Zastosuj' ZWROT
        self.pz_zastosuj_button = tk.Button(self.pojazd_zwrot_labelframe, text='Zastosuj',
                                            width=40, command=self.pojazd_zastosuj_zwrot)
        self.pz_zastosuj_button.grid(column=1, columnspan=2, row=3, pady=20)

            # Potwierdzenie zapisu
        self.pz_potwierdzenie_label = tk.Label(self.pojazd_zwrot_labelframe)
        self.pz_potwierdzenie_label.grid(column=0, columnspan=4, row=4)

        # HORIZONTAL SEPARATOR
        self.pojazd_hor_separator = ttk.Separator(self.pojazd, orient='horizontal')
        self.pojazd_hor_separator.grid(column=1, columnspan=3, row=2, ipadx=self.window_width, pady=30)

        # DATABASE VIEW
        self.pojazd_db_columns = ("id", "TR", "Data pobrania", "Pobierający", "Operator - pobranie", "Data zwrotu",
                                  "Zwracający", "Operator - zwrot")
        self.pojazd_db_view = ttk.Treeview(self.pojazd, columns=self.pojazd_db_columns, show='headings', height=18)

        for column in self.pojazd_db_columns:
            self.pojazd_db_view.heading(column, text=column, anchor='center')

        self.pojazd_db_view.column("id", width=60)
        self.pojazd_db_view.column("TR", width=120)
        self.pojazd_db_view.column("Data pobrania", width=120)
        self.pojazd_db_view.column("Data zwrotu", width=120)
        self.pojazd_db_view.column("Operator - pobranie", width=140)

        self.pojazd_db_view.grid(column=1, columnspan=3, row=4, sticky='NEWS')

            # SCROLLBAR
        self.pojazd_db_scrollbar = ttk.Scrollbar(self.pojazd, orient=tk.VERTICAL, command=self.pojazd_db_view.yview)
        self.pojazd_db_view.configure(yscrollcommand=self.pojazd_db_scrollbar.set)
        self.pojazd_db_scrollbar.grid(column=4, row=4, sticky='NS')

        # CLOSE BUTTON
        self.zamknij_button = ttk.Button(self.pojazd, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button.grid(column=2, row=6, sticky="WE", padx=10, pady=10)

        self.pokaz_wszystko = ttk.Button(self.pojazd, text='Pokaż wszystko', command=self.show_all)
        self.pokaz_wszystko.grid(column=3, row=6)

        self.root.mainloop()

    def show_all(self):
        # Funkcja do przycisku "Pokaż wszystko", żeby wyświetlić wszystkie dane z bazy
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        for n in self.cursor.execute(""" SELECT * FROM pojazdy """):
            self.pojazd_db_view.insert("", tk.END, values=n)
        self.db.close()

    def enable_frames(self, event):
        # Funkcja aktywująca okienka po wybraniu operatora
        self.pp_tablica_entry.config(state='normal')
        self.pp_osoba_combobox.config(state='normal')
        self.pz_tablica_entry.config(state='normal')
        self.pz_osoba_combobox.config(state='normal')

    def pp_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.pp_data.get():
            self.pp_data_entry.config(state='normal')
            self.pp_data_entry.delete(0, "end")
            self.pp_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem
        if not self.pp_data.get():
            self.pp_data_entry.insert(0, "RRRR-MM-DD")
            self.pp_data_entry.config(state="disabled")

    def pz_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.pz_data.get():
            self.pz_data_entry.config(state='normal')
            self.pz_data_entry.delete(0, "end")
            self.pz_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem
        if not self.pz_data.get():
            self.pz_data_entry.insert(0, "RRRR-MM-DD")
            self.pz_data_entry.config(state="disabled")

    def check_tr(self, nr_rej):
        # Funkcja sprawdzająca, czy podany nr TR jest zgodny ze wzorem
        pattern = re.compile(r"^[A-Z]{1,3}\s[A-Z\d]{3,5}$|^[A-Z]\d\s[A-Z\d]{3,5}$")
        if pattern.search(nr_rej):
            return True
        else:
            return False

    def pp_czy_dubel(self, tr):
        # Funkcja sprawdza, czy w bazie istnieje już wpis z podanymi danymi bez daty zwrotu
        wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE tr = "{tr}" AND data_zwrotu IS NULL; """
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False

    def format_inna_data(self, data):
        # Funkcja sprawdzająca, czy podana data ma prawidłowy format
        format_daty = re.compile(r"^20\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[1-2]\d|3[0-1])$")
        if format_daty.search(data):
            return True
        else:
            return False

    def insert_pobranie_to_db(self, tr, data, osoba, operator):
        return f""" INSERT INTO pojazdy(tr, data_pobrania, osoba_pobranie, operator_pobranie) 
                                VALUES("{tr}", "{data}", "{osoba}", "{operator}"); """

    def pp_potwierdzenie_zapisu(self, tr, data, pobierajacy, operator):
        # Funkcja wyszukuje czy w bazie jest zapisany podany rekord,
        # jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych
        wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE tr = "{tr}" 
                                                        AND data_pobrania >= "{data}" 
                                                        AND osoba_pobranie = "{pobierajacy}" 
                                                        AND operator_pobranie = "{operator}" 
                                                        AND data_zwrotu IS NULL; """
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) == 1:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.pojazd_db_view.insert("", tk.END, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.pp_potwierdzenie_label.configure(
                image=img,
                text=f"   Prawidłowo zapisano pobranie teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.pp_potwierdzenie_label.image = img
        else:
            wrong = tk.PhotoImage(file='wrong.jpg')
            self.pp_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki o nr {tr}.",
                compound="left", font="Helvetica 8"
            )
            self.pp_potwierdzenie_label.image = wrong

    def pojazd_zastosuj_pobranie(self):
        now = datetime.now().strftime("%y-%m-%d %H:%M")
        teczka = self.pp_tablica_entry.get().upper()
        osoba = self.pp_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        if self.pp_data.get():
            if self.format_inna_data(self.pp_data_entry.get()):
                now = self.pp_data_entry.get()
            else:
                return showerror("Błąd", "Sprawdź czy podana data jest prawidłowa. "
                                         "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")

        if self.pp_czy_dubel(teczka):
            return showerror("Błąd", f"Teczka o nr '{teczka}' została już pobrana i nie odnotowano jej zwrotu.")

        if teczka == "" or osoba == "":
            # Jeśli nie wpisze się TR lub pobierającego wyskoczy błąd
            return showerror("Błąd", "Pola  'Numer TR' i 'Pobierający akta' są obowiązkowe!")

        elif self.check_tr(teczka):
            # Jeśli nr TR jest poprawny - wstaw dane do bazy
            self.cursor.execute(self.insert_pobranie_to_db(teczka, now, osoba, operator))
            self.db.commit()

        elif not self.check_tr(teczka):
            # Jeśli nr TR jest błędny pokaż zapytanie
            poprawna_tr = askyesno("Błąd",
                                   f"Numer TR powinien składać się z wyróżnika powiatu, ODSTĘPU i pojemności.\n"
                                   f"Czy '{teczka}' to na pewno poprawny numer rejestracyjny?")
            if poprawna_tr:
                # Po zatwierdzeniu wprowadzi dane do bazy
                self.cursor.execute(self.insert_pobranie_to_db(teczka, now, osoba, operator))
                self.db.commit()

        self.pp_potwierdzenie_zapisu(teczka, now, osoba, operator)
        self.db.close()

    def pojazd_potwierdzenie_zwrotu(self, tr, data, pobierajacy, operator):
        # Funkcja wyszukuje czy podana teczka występuje z podaną datą zwrotu.
        # Jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych
        wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE tr = "{tr}" 
                                                        AND data_zwrotu >= "{data}" 
                                                        AND osoba_zwrot = "{pobierajacy}" 
                                                        AND operator_zwrot = "{operator}"; """
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) >= 1:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.pojazd_db_view.insert("", tk.END, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.pz_potwierdzenie_label.configure(
                image=img,
                text=f"Prawidłowo odnotowano zwrot teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.pz_potwierdzenie_label.image = img
        else:
            wrong = tk.PhotoImage(file='wrong.jpg')
            self.pz_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki o nr {tr}.",
                compound="left", font="Helvetica 8"
            )
            self.pz_potwierdzenie_label.image = wrong

    def pojazd_zastosuj_zwrot(self):
        now = datetime.now().strftime("%y-%m-%d %H:%M")
        teczka = self.pz_tablica_entry.get().upper()
        osoba = self.pz_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        if self.pz_data.get():
            if self.format_inna_data(self.pz_data_entry.get()):
                now = self.pz_data_entry.get()
            else:
                return showerror("Błąd", "Sprawdź czy podana data jest prawidłowa. "
                                         "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")

        if teczka == "" or osoba == "":
            # Jeśli nie wpisze się TR lub pobierającego wyskoczy błąd
            return showerror("Błąd", "Pola  'Numer TR' i 'Pobierający akta' są obowiązkowe!")

        self.cursor.execute(f""" SELECT * FROM pojazdy WHERE data_zwrotu IS NULL AND tr = "{teczka}"; """)
        if len(self.cursor.fetchall()) == 0:
            showerror("Błąd", f"Nie znaleziono niezwróconej teczki o nr '{teczka}'.")
        else:
            self.cursor.execute(f""" UPDATE pojazdy SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", 
            operator_zwrot = "{operator}" WHERE tr = "{teczka}" AND data_zwrotu IS NULL; """)
            self.db.commit()

        self.pojazd_potwierdzenie_zwrotu(teczka, now, osoba, operator)
        self.db.close()

if __name__ == '__main__':
    app = App()
