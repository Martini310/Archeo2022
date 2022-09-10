import _tkinter
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, askyesno, showinfo, showwarning
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

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS kierowcy( id integer PRIMARY KEY AUTOINCREMENT, 
                                                                    pesel text, 
                                                                    nazwisko text NOT NULL, 
                                                                    imie text NOT NULL,  
                                                                    nr_kk text NOT NULL, 
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
        self.window_height = int(self.screen_height * 0.88)

        # Window location
        self.center_x = int(self.screen_width / 2 - self.window_width / 2)
        self.center_y = int(self.screen_height / 2 - self.window_height / 1.88)
        self.root.geometry(f'{self.window_width}x{self.window_height}+{self.center_x}+{self.center_y}')
        self.root.resizable(True, True)

        # MENU BAR
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu = tk.Menu(self.menubar, tearoff=0)

        # Menu items
        self.file_menu.add_command(label='Informacje', command=self.info)
        self.file_menu.add_command(label='Pusty')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Zamknij', command=self.root.destroy)

        self.help_menu.add_command(label='Edytuj operatorów', command=self.operator_edit_window)
        self.help_menu.add_command(label='Edytuj osoby - Kierowca', command=self.osoba_kierowca_edit_window)
        self.help_menu.add_command(label='Edytuj osoby - Pojazd', command=self.osoba_pojazd_edit_window)

        self.menubar.add_cascade(label='Menu', menu=self.file_menu)
        self.menubar.add_cascade(label='Opcje', menu=self.help_menu)

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
        self.notebook.pack(expand=True, fill="both")

        self.pojazd = tk.Frame(self.notebook)
        self.kierowca = tk.Frame(self.notebook)
        self.wyszukiwanie = tk.Frame(self.notebook)

        self.pojazd.pack(fill="both", expand=True)
        self.kierowca.pack(fill="both", expand=True)
        self.wyszukiwanie.pack(fill="both", expand=True)

        self.notebook.add(self.pojazd, text="Pojazdy")
        self.notebook.add(self.kierowca, text="Kierowcy")
        self.notebook.add(self.wyszukiwanie, text="Wyszukiwanie")

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ POJAZD @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.pojazd.columnconfigure(0, minsize=30)
        self.pojazd.columnconfigure(1, weight=3)
        self.pojazd.columnconfigure(2, weight=1)
        self.pojazd.columnconfigure(3, weight=3)
        self.pojazd.columnconfigure(4, minsize=30)

        # POBRANIE AKT POJAZDU --> pp
        self.pojazd_pobranie_labelframe = tk.LabelFrame(self.pojazd, text='Pobranie akt pojazdu')
        self.pojazd_pobranie_labelframe.grid(column=1, row=0, padx=30, sticky='NEWS', pady=20)

        self.pojazd_pobranie_labelframe.columnconfigure(0, minsize=50)
        self.pojazd_pobranie_labelframe.columnconfigure(1, weight=1)
        self.pojazd_pobranie_labelframe.columnconfigure(2, weight=1)
        self.pojazd_pobranie_labelframe.columnconfigure(3, minsize=50)

        # Tablica rejestracyjna
        self.pp_tablica_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Numer TR:', background='yellow')
        self.pp_tablica_label.grid(column=1, row=0, sticky='E', pady=20, padx=10)

        self.pp_tablica_img = tk.PhotoImage(file='tablica.gif')
        self.pp_tablica_img_label = ttk.Label(self.pojazd_pobranie_labelframe, image=self.pp_tablica_img)
        self.pp_tablica_img_label.grid(column=2, row=0, sticky='W')

        self.pp_tablica_entry = ttk.Entry(self.pojazd_pobranie_labelframe, state='disabled', width=12,
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

        self.pojazd_zwrot_labelframe.columnconfigure(0, minsize=50)
        self.pojazd_zwrot_labelframe.columnconfigure(1, weight=1)
        self.pojazd_zwrot_labelframe.columnconfigure(2, weight=1)
        self.pojazd_zwrot_labelframe.columnconfigure(3, minsize=50)

        # Tablica rejestracyjna
        self.pz_tablica_label = ttk.Label(self.pojazd_zwrot_labelframe, text='Numer TR:', background='yellow')
        self.pz_tablica_label.grid(column=1, row=0, sticky='E', pady=20, padx=10)

        self.pz_tablica_img = tk.PhotoImage(file='tablica.gif')
        self.pz_tablica_img_label = ttk.Label(self.pojazd_zwrot_labelframe, image=self.pz_tablica_img)
        self.pz_tablica_img_label.grid(column=2, row=0, sticky='W')

        self.pz_tablica_entry = ttk.Entry(self.pojazd_zwrot_labelframe, state='disabled', width=12,
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

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ KIEROWCA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.kierowca.columnconfigure(0, minsize=30)
        self.kierowca.columnconfigure(1, weight=3)
        self.kierowca.columnconfigure(2, weight=1)
        self.kierowca.columnconfigure(3, weight=3)
        self.kierowca.columnconfigure(4, minsize=30)

        # POBRANIE AKT KIEROWCY --> kp
        self.kierowca_pobranie_labelframe = tk.LabelFrame(self.kierowca, text='Pobranie akt kierowcy')
        self.kierowca_pobranie_labelframe.grid(column=1, row=0, padx=30, sticky='NEWS', pady=20)

        self.kierowca_pobranie_labelframe.columnconfigure(0, minsize=50)
        self.kierowca_pobranie_labelframe.columnconfigure(1, weight=1)
        self.kierowca_pobranie_labelframe.columnconfigure(2, weight=1)
        self.kierowca_pobranie_labelframe.columnconfigure(3, minsize=50)

        # PESEL - KIEROWCA POBRANIE AKT
        self.kp_pesel_label = ttk.Label(self.kierowca_pobranie_labelframe, text='PESEL:')
        self.kp_pesel_label.grid(column=1, row=0, sticky='E', pady=10)

        self.kp_pesel_string = tk.StringVar()
        self.kp_pesel_entry = tk.Entry(self.kierowca_pobranie_labelframe, width=15, state='disabled',
                                       font='Arial 13 bold', textvariable=self.kp_pesel_string)
        self.kp_pesel_entry.grid(column=2, row=0, sticky='W')
        self.kp_pesel_entry.bind('<FocusOut>', self.sprawdz_pesel_pobranie)

        # DATA URODZENIA - KIEROWCA (w przypadku braku PESEL)
        self.kp_data_ur_var = tk.BooleanVar()
        self.kp_data_ur_check = ttk.Checkbutton(self.kierowca_pobranie_labelframe,
                                                onvalue=True,
                                                offvalue=False,
                                                text='Data ur.',
                                                variable=self.kp_data_ur_var,
                                                command=self.kp_data_urodzenia)
        self.kp_data_ur_check.grid(column=2, row=0, sticky='W', pady=10, padx=150)

        self.kp_data_ur_entry = tk.Entry(self.kierowca_pobranie_labelframe)
        self.kp_data_ur_entry.insert(0, 'RRRR-MM-DD')
        self.kp_data_ur_entry.config(state='disabled')
        self.kp_data_ur_entry.grid(column=2, row=0, sticky='E', padx=70)

        # Imię i Nazwisko - POBRANIE AKT
        self.kp_imie_label = ttk.Label(self.kierowca_pobranie_labelframe, text='Imię:')
        self.kp_imie_label.grid(column=1, row=2, sticky='E')

        self.kp_imie_entry = tk.Entry(self.kierowca_pobranie_labelframe, state='disabled')
        self.kp_imie_entry.grid(column=2, row=2, sticky='W', pady=10)

        self.kp_nazwisko_label = ttk.Label(self.kierowca_pobranie_labelframe, text='Nazwisko:')
        self.kp_nazwisko_label.grid(column=2, row=2, sticky='W', padx=150)

        self.kp_nazwisko_entry = tk.Entry(self.kierowca_pobranie_labelframe, state='disabled')
        self.kp_nazwisko_entry.grid(column=2, row=2, sticky='E', pady=10, padx=50)

        # NR Karty Kierowcy - POBRANIE AKT
        self.kp_nr_kk_label = ttk.Label(self.kierowca_pobranie_labelframe, text='Numer Karty Kierowcy:')
        self.kp_nr_kk_label.grid(column=1, row=6, sticky='E')

        self.kp_nr_kk_entry = tk.Entry(self.kierowca_pobranie_labelframe)
        self.kp_nr_kk_entry.grid(column=2, row=6, sticky='W', pady=10)
        self.kp_nr_kk_entry.insert(0, 'B/U')
        self.kp_nr_kk_entry.config(state='disabled')

        # UWAGI - KIEROWCA
        self.kp_uwagi_label = tk.Label(self.kierowca_pobranie_labelframe, text='Uwagi:')
        self.kp_uwagi_label.grid(column=2, row=8, sticky='E', padx=175)

        self.kp_uwagi = tk.Text(self.kierowca_pobranie_labelframe, height=3, width=20,
                                state='disabled', background='gray90')
        self.kp_uwagi.grid(column=2, row=8, rowspan=2, padx=10, sticky='E')

        # Osoba Pobierająca
        self.kp_osoba_values = ['Renata Taszarek',
                                'Kamila Mikołajczak',
                                'Dorota Borowska']

        self.kp_osoba_label = ttk.Label(self.kierowca_pobranie_labelframe, text='Osoba pobierająca:')
        self.kp_osoba_label.grid(column=1, row=8, sticky='E', pady=10)

        self.kp_osoba_combobox = ttk.Combobox(self.kierowca_pobranie_labelframe, values=self.kp_osoba_values,
                                              state='disabled')
        self.kp_osoba_combobox.grid(column=2, row=8, sticky='W')

        # INNA DATA - KIEROWCA POBRANIE
        self.kp_data = tk.BooleanVar()
        self.kp_data_check = ttk.Checkbutton(self.kierowca_pobranie_labelframe,
                                             onvalue=True,
                                             offvalue=False,
                                             text='Inna data',
                                             variable=self.kp_data,
                                             command=self.kp_inna_data)
        self.kp_data_check.grid(column=1, row=10, sticky='E', pady=10, padx=10)

        self.kp_data_entry = tk.Entry(self.kierowca_pobranie_labelframe)
        self.kp_data_entry.insert(0, 'RRRR-MM-DD')
        self.kp_data_entry.config(state='disabled')
        self.kp_data_entry.grid(column=2, row=10, sticky='W')

        # PRZYCISK ZASTOSUJ - KIEROWCA POBRANIE
        self.kp_zastosuj_button = tk.Button(self.kierowca_pobranie_labelframe, text='Zastosuj',
                                            width=40, command=self.kierowca_zastosuj_pobranie)
        self.kp_zastosuj_button.grid(column=1, columnspan=2, row=12, pady=10)

        # Potwierdzenie zapisu - Kierowca pobranie
        self.kp_potwierdzenie_label = tk.Label(self.kierowca_pobranie_labelframe)
        self.kp_potwierdzenie_label.grid(column=0, columnspan=4, row=14)

        # VERTICAL SEPARATOR - KIEROWCA
        self.kierowca_ver_separator = ttk.Separator(self.kierowca, orient='vertical')
        self.kierowca_ver_separator.grid(column=2, row=0, ipady=130, pady=10)

        # ZWROT AKT KIEROWCY --> kz
        self.kierowca_zwrot_labelframe = tk.LabelFrame(self.kierowca, text='Zwrot akt kierowcy')
        self.kierowca_zwrot_labelframe.grid(column=3, row=0, padx=30, sticky='NEWS', pady=20)

        self.kierowca_zwrot_labelframe.columnconfigure(0, minsize=100)
        self.kierowca_zwrot_labelframe.columnconfigure(1, weight=1)
        self.kierowca_zwrot_labelframe.columnconfigure(2, weight=1)
        self.kierowca_zwrot_labelframe.columnconfigure(3, minsize=240)

        # PESEL - ZWROT AKT
        self.kz_pesel_label = ttk.Label(self.kierowca_zwrot_labelframe, text='PESEL:')
        self.kz_pesel_label.grid(column=1, row=0, sticky='E', pady=30)

        self.kz_pesel_string = tk.StringVar()
        self.kz_pesel_entry = tk.Entry(self.kierowca_zwrot_labelframe, width=15, state='disabled',
                                       font='Arial 13 bold', textvariable=self.kz_pesel_string)
        self.kz_pesel_entry.grid(column=2, row=0, sticky='W')
        self.kz_pesel_entry.bind('<FocusOut>', self.sprawdz_pesel_zwrot)

        # Imię i Nazwisko - ZWROT AKT
        # self.kz_imie_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Imię:')
        # self.kz_imie_label.grid(column=1, row=2, sticky='E')

        # self.kz_imie_entry = tk.Entry(self.kierowca_zwrot_labelframe, state='disabled')
        # self.kz_imie_entry.grid(column=2, row=2, sticky='W', pady=10)

        # self.kz_nazwisko_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Nazwisko:')
        # self.kz_nazwisko_label.grid(column=2, row=2, sticky='W', padx=150)

        # self.kz_nazwisko_entry = tk.Entry(self.kierowca_zwrot_labelframe, state='disabled')
        # self.kz_nazwisko_entry.grid(column=2, row=2, sticky='E', pady=10, padx=50)

        # NR Karty Kierowcy - ZWROT AKT
        # self.kz_nr_kk_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Numer Karty Kierowcy:')
        # self.kz_nr_kk_label.grid(column=1, row=6, sticky='E')

        # self.kz_nr_kk_entry = tk.Entry(self.kierowca_zwrot_labelframe)
        # self.kz_nr_kk_entry.grid(column=2, row=6, sticky='W', pady=10)
        # self.kz_nr_kk_entry.insert(0, 'B/U')
        # self.kz_nr_kk_entry.config(state='disabled')

        # Osoba zwracająca
        self.kz_osoba_values = ['Renata Taszarek',
                                'Kamila Mikołajczak',
                                'Dorota Borowska']

        self.kz_osoba_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Osoba zwracająca:')
        self.kz_osoba_label.grid(column=1, row=8, sticky='E', pady=20)

        self.kz_osoba_combobox = ttk.Combobox(self.kierowca_zwrot_labelframe, values=self.kz_osoba_values,
                                              state='disabled')
        self.kz_osoba_combobox.grid(column=2, row=8, sticky='W')

        # INNA DATA - KIEROWCA ZWROT
        self.kz_data = tk.BooleanVar()
        self.kz_data_check = ttk.Checkbutton(self.kierowca_zwrot_labelframe,
                                             onvalue=True,
                                             offvalue=False,
                                             text='Inna data',
                                             variable=self.kz_data,
                                             command=self.kz_inna_data
                                             )
        self.kz_data_check.grid(column=1, row=10, sticky='E', pady=20, padx=10)

        self.kz_data_entry = tk.Entry(self.kierowca_zwrot_labelframe)
        self.kz_data_entry.insert(0, 'RRRR-MM-DD')
        self.kz_data_entry.config(state='disabled')
        self.kz_data_entry.grid(column=2, row=10, sticky='W')

        # PRZYCISK ZASTOSUJ - KIEROWCA ZWROT
        self.kz_zastosuj_button = tk.Button(self.kierowca_zwrot_labelframe, text='Zastosuj',
                                            width=40, command=self.kierowca_zastosuj_zwrot)
        self.kz_zastosuj_button.grid(column=1, columnspan=2, row=12, pady=10)

        # Potwierdzenie zapisu - Kierowca pobranie
        self.kz_potwierdzenie_label = tk.Label(self.kierowca_zwrot_labelframe)
        self.kz_potwierdzenie_label.grid(column=0, columnspan=4, row=14)

        # KIEROWCA HORIZONTAL SEPARATOR
        self.kierowca_hor_separator = ttk.Separator(self.kierowca, orient='horizontal')
        self.kierowca_hor_separator.grid(column=1, columnspan=3, row=2, ipadx=self.window_width, pady=30)

        # KIEROWCA DATABASE VIEW
        self.kierowca_db_columns = ('id', 'PESEL', 'Nazwisko', 'Imię', 'Nr Karty Kierowcy', 'Data pobrania',
                                    'Pobierający', 'Operator - pobranie', 'Data zwrotu', 'Zwracający',
                                    'Operator - zwrot')
        self.kierowca_db_view = ttk.Treeview(self.kierowca, columns=self.kierowca_db_columns, show='headings',
                                             height=18)

        for column in self.kierowca_db_columns:
            self.kierowca_db_view.heading(column, text=column, anchor='center')

        self.kierowca_db_view.column("id", width=15)
        self.kierowca_db_view.column("PESEL", width=60)
        self.kierowca_db_view.column("Nazwisko", width=80)
        self.kierowca_db_view.column("Imię", width=80)
        self.kierowca_db_view.column("Nr Karty Kierowcy", width=50)
        self.kierowca_db_view.column("Data pobrania", width=80)
        self.kierowca_db_view.column("Pobierający", width=80)
        self.kierowca_db_view.column("Operator - pobranie", minwidth=80)
        self.kierowca_db_view.column("Data zwrotu", width=80)
        self.kierowca_db_view.column("Zwracający", width=80)
        self.kierowca_db_view.column("Operator - zwrot", minwidth=80)

        self.kierowca_db_view.grid(column=1, columnspan=3, row=4, sticky='NEWS')

        # KIEROWCA SCROLLBAR
        self.kierowca_db_scrollbar = ttk.Scrollbar(self.kierowca, orient=tk.VERTICAL,
                                                   command=self.kierowca_db_view.yview)
        self.kierowca_db_view.configure(yscrollcommand=self.kierowca_db_scrollbar.set)
        self.kierowca_db_scrollbar.grid(column=4, row=4, sticky='NS')

        # CLOSE BUTTON
        self.zamknij_button2 = ttk.Button(self.kierowca, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button2.grid(column=2, row=6, sticky="WE", padx=10, pady=10)

        self.pokaz_wszystko2 = ttk.Button(self.kierowca, text='Pokaż wszystko', command=self.show_all_kierowca)
        self.pokaz_wszystko2.grid(column=3, row=6)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ WYSZUKIWARKA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # Pole wyboru rejestru do przeszukania
        self.rejestr_labelframe = ttk.Labelframe(self.wyszukiwanie, text='Wybierz rejestr')
        self.rejestr_labelframe.grid(column=0, row=0, pady=5, padx=15, sticky='W')

        # Zmienna wartości RadioButton
        self.selected_value = tk.IntVar(value=0)

        # RadioButton Pojazd i Kierowca
        self.rejestr_pojazd_radio = ttk.Radiobutton(self.rejestr_labelframe, text='Pojazd', value=1,
                                                    variable=self.selected_value, command=self.wybierz_rejestr)
        self.rejestr_pojazd_radio.grid(column=0, row=0, pady=5, padx=10)

        self.rejestr_kierowca_radio = ttk.Radiobutton(self.rejestr_labelframe, text='Kierowca', value=0,
                                                      variable=self.selected_value, command=self.wybierz_rejestr)
        self.rejestr_kierowca_radio.grid(column=1, row=0, pady=5, padx=10)

        # Pole z opcjami wyszukiwania
        self.wyszukiwanie_options = ttk.Labelframe(self.wyszukiwanie, text='Opcje wyszukiwania')
        self.wyszukiwanie_options.grid(column=0, row=1, sticky='W', padx=15, ipadx=15)

        # OPCJE WYSZUKIWANIA

        # @@@ POJAZD @@@
        self.wyszukaj_pojazd_frame = tk.Frame(self.wyszukiwanie_options)
        # self.wyszukaj_pojazd_frame.grid(column=0, row=0)

        # Nr Rejestracyjny
        self.szukaj_tr_label = ttk.Label(self.wyszukaj_pojazd_frame, text='     Numer TR:', font='Arial 10')
        self.szukaj_tr_label.grid(column=0, row=0, pady=10)

        self.szukaj_tr_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=10)
        self.szukaj_tr_entry.grid(column=1, row=0)

        # Osoba pobierająca
        self.szukaj_pojazd_osoba_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                            text='     Osoba pobierająca:', font='Arial 10')
        self.szukaj_pojazd_osoba_pobranie_label.grid(column=2, row=0)

        self.szukaj_pojazd_osoba_pobranie_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_osoba_values)
        self.szukaj_pojazd_osoba_pobranie_entry.grid(column=3, row=0)

        # Osoba zwracająca
        self.szukaj_pojazd_osoba_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                         text='     Osoba zwracająca:', font='Arial 10')
        self.szukaj_pojazd_osoba_zwrot_label.grid(column=2, row=1)

        self.szukaj_pojazd_osoba_zwrot_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_osoba_values)
        self.szukaj_pojazd_osoba_zwrot_entry.grid(column=3, row=1)

        # Operator pobranie
        self.szukaj_pojazd_operator_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                               text='     Operator pobranie:', font='Arial 10')
        self.szukaj_pojazd_operator_pobranie_label.grid(column=4, row=0)

        self.szukaj_pojazd_operator_pobranie_entry = ttk.Combobox(self.wyszukaj_pojazd_frame,
                                                                  values=self.operator_values)
        self.szukaj_pojazd_operator_pobranie_entry.grid(column=5, row=0)

        # Operator zwrot
        self.szukaj_pojazd_operator_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                            text='     Operator zwrot:', font='Arial 10')
        self.szukaj_pojazd_operator_zwrot_label.grid(column=4, row=1, sticky='E')

        self.szukaj_pojazd_operator_zwrot_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.operator_values)
        self.szukaj_pojazd_operator_zwrot_entry.grid(column=5, row=1)

        # Data pobrania od
        self.szukaj_pojazd_data_od_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                              text='   Data pobrania od:', font='Arial 10')
        self.szukaj_pojazd_data_od_pobranie_label.grid(column=6, row=0, pady=10)

        self.szukaj_pojazd_data_od_pobranie_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_od_pobranie_entry.grid(column=7, row=0)

        # Data pobrania do
        self.szukaj_pojazd_data_do_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                              text='   Data pobrania do:', font='Arial 10')
        self.szukaj_pojazd_data_do_pobranie_label.grid(column=8, row=0, pady=10)

        self.szukaj_pojazd_data_do_pobranie_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_do_pobranie_entry.grid(column=9, row=0)

        # Data zwrotu od
        self.szukaj_pojazd_data_od_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                           text='   Data zwrotu od:', font='Arial 10')
        self.szukaj_pojazd_data_od_zwrot_label.grid(column=6, row=1, pady=10, sticky='E')

        self.szukaj_pojazd_data_od_zwrot_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_od_zwrot_entry.grid(column=7, row=1)

        # Data zwrotu do
        self.szukaj_pojazd_data_do_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                           text='   Data zwrotu do:', font='Arial 10')
        self.szukaj_pojazd_data_do_zwrot_label.grid(column=8, row=1, pady=10, sticky='E')

        self.szukaj_pojazd_data_do_zwrot_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_do_zwrot_entry.grid(column=9, row=1)

        # @@@@ KIEROWCA @@@
        self.wyszukaj_kierowca_frame = tk.Frame(self.wyszukiwanie_options)
        self.wyszukaj_kierowca_frame.grid(column=0, row=1)

        # Szukaj KIEROWCA PESEL
        self.szukaj_kierowca_pesel_label = ttk.Label(self.wyszukaj_kierowca_frame, text='     PESEL ')
        self.szukaj_kierowca_pesel_label.grid(column=0, row=0, sticky='E')

        self.szukaj_kierowca_pesel_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_pesel_entry.grid(column=1, row=0)

        # Szukaj KIEROWCA NR KK
        self.szukaj_kierowca_nr_kk_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                     text='     numek KK ', font='Arial 10')
        self.szukaj_kierowca_nr_kk_label.grid(column=0, row=1, pady=10, sticky='E')

        self.szukaj_kierowca_nr_kk_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_nr_kk_entry.grid(column=1, row=1)

        # Szukaj KIEROWCA IMIĘ
        self.szukaj_kierowca_imie_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                             text='     Imię ', font='Arial 10')
        self.szukaj_kierowca_imie_pobranie_label.grid(column=2, row=0, sticky='E')

        self.szukaj_kierowca_imie_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_imie_pobranie_entry.grid(column=3, row=0)

        # Szukaj KIEROWCA NAZWISKO
        self.szukaj_kierowca_nazwisko_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                 text='     Nazwisko ', font='Arial 10')
        self.szukaj_kierowca_nazwisko_pobranie_label.grid(column=2, row=1)

        self.szukaj_kierowca_nazwisko_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_nazwisko_pobranie_entry.grid(column=3, row=1)

        # Szukaj KIEROWCA Osoba pobierająca
        self.szukaj_kierowca_osoba_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                              text='     Osoba pobierająca ', font='Arial 10')
        self.szukaj_kierowca_osoba_pobranie_label.grid(column=4, row=0)

        self.szukaj_kierowca_osoba_pobranie_entry = ttk.Combobox(self.wyszukaj_kierowca_frame,
                                                                 values=self.kp_osoba_values)
        self.szukaj_kierowca_osoba_pobranie_entry.grid(column=5, row=0)

        # Szukaj KIEROWCA Osoba zwracająca
        self.szukaj_kierowca_osoba_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                           text='     Osoba zwracająca ', font='Arial 10')
        self.szukaj_kierowca_osoba_zwrot_label.grid(column=4, row=1)

        self.szukaj_kierowca_osoba_zwrot_entry = ttk.Combobox(self.wyszukaj_kierowca_frame, values=self.kz_osoba_values)
        self.szukaj_kierowca_osoba_zwrot_entry.grid(column=5, row=1)

        # Szukaj KIEROWCA Operator pobranie
        self.szukaj_kierowca_operator_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                 text='     Operator pobranie ', font='Arial 10')
        self.szukaj_kierowca_operator_pobranie_label.grid(column=6, row=0)

        self.szukaj_kierowca_operator_pobranie_entry = ttk.Combobox(self.wyszukaj_kierowca_frame,
                                                                    values=self.operator_values)
        self.szukaj_kierowca_operator_pobranie_entry.grid(column=7, row=0)

        # Szukaj KIEROWCA Operator zwrot
        self.szukaj_kierowca_operator_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                              text='     Operator zwrot ', font='Arial 10')
        self.szukaj_kierowca_operator_zwrot_label.grid(column=6, row=1, sticky='E')

        self.szukaj_kierowca_operator_zwrot_entry = ttk.Combobox(self.wyszukaj_kierowca_frame,
                                                                 values=self.operator_values)
        self.szukaj_kierowca_operator_zwrot_entry.grid(column=7, row=1)

        # Szukaj KIEROWCA Data pobrania od
        self.szukaj_kierowca_data_od_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                text='   Data pobrania od ', font='Arial 10')
        self.szukaj_kierowca_data_od_pobranie_label.grid(column=8, row=0, pady=10)

        self.szukaj_kierowca_data_od_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_data_od_pobranie_entry.grid(column=9, row=0)

        # Szukaj KIEROWCA Data pobrania do
        self.szukaj_kierowca_data_do_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                text='   Data pobrania do ', font='Arial 10')
        self.szukaj_kierowca_data_do_pobranie_label.grid(column=10, row=0, pady=10)

        self.szukaj_kierowca_data_do_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_data_do_pobranie_entry.grid(column=11, row=0)

        # Szukaj KIEROWCA Data zwrotu od
        self.szukaj_kierowca_data_od_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                             text='   Data zwrotu od ', font='Arial 10')
        self.szukaj_kierowca_data_od_zwrot_label.grid(column=8, row=1, pady=10, sticky='E')

        self.szukaj_kierowca_data_od_zwrot_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_data_od_zwrot_entry.grid(column=9, row=1)

        # Szukaj KIEROWCA Data zwrotu do
        self.szukaj_kierowca_data_do_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                             text='   Data zwrotu do ', font='Arial 10')
        self.szukaj_kierowca_data_do_zwrot_label.grid(column=10, row=1, pady=10, sticky='E')

        self.szukaj_kierowca_data_do_zwrot_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=20)
        self.szukaj_kierowca_data_do_zwrot_entry.grid(column=11, row=1)

        # Szukaj - PRZYCISKI
        self.szukaj_przyciski_frame = ttk.LabelFrame(self.wyszukiwanie)
        self.szukaj_przyciski_frame.grid(column=0, row=2, sticky='W', padx=15, ipady=5)

        self.szukaj_wyszukaj_button = tk.Button(self.szukaj_przyciski_frame, text='Wyszukaj',
                                                command=self.wyszukaj_kierowca_click)
        self.szukaj_wyszukaj_button.grid(column=0, row=0, padx=20, ipadx=10, pady=5)

        self.szukaj_edytuj_button = tk.Button(self.szukaj_przyciski_frame, text='Edytuj', command=self.edit_kierowca)
        self.szukaj_edytuj_button.grid(column=1, row=0, padx=20, ipadx=10, pady=5)

        self.szukaj_wyczysc_button = tk.Button(self.szukaj_przyciski_frame, text='Wyczyść', command=self.clear_entries)
        self.szukaj_wyczysc_button.grid(column=2, row=0, padx=20, ipadx=10, pady=5)

        # SZUKAJ DB VIEW FRAME POJAZD
        self.szukaj_pojazd_wyniki_frame = ttk.LabelFrame(self.wyszukiwanie, text='Wyniki wyszukiwania')
        # self.szukaj_pojazd_wyniki_frame.grid(column=0, row=3, pady=10, padx=30, ipadx=10)

        # SZUKAJ DATABASE VIEW POJAZD
        self.szukaj_pojazd_db_columns = (
            "id", "TR", "Data pobrania", "Pobierający", "Operator - pobranie", "Data zwrotu",
            "Zwracający", "Operator - zwrot")
        self.szukaj_pojazd_db_view = ttk.Treeview(self.szukaj_pojazd_wyniki_frame,
                                                  columns=self.szukaj_pojazd_db_columns,
                                                  show='headings', height=25)
        col_width_pojazd = int(self.window_width / 8)
        for column in self.szukaj_pojazd_db_columns:
            self.szukaj_pojazd_db_view.heading(column, text=column, anchor='center')
            self.szukaj_pojazd_db_view.column(column, width=col_width_pojazd)

        self.szukaj_pojazd_db_view.column('id', width=80)

        self.szukaj_pojazd_db_view.grid(column=0, row=4, sticky='NEWS')

        # SCROLLBAR
        self.szukaj_pojazd_db_scrollbar = ttk.Scrollbar(self.szukaj_pojazd_wyniki_frame, orient=tk.VERTICAL,
                                                        command=self.szukaj_pojazd_db_view.yview)
        self.szukaj_pojazd_db_view.configure(yscrollcommand=self.szukaj_pojazd_db_scrollbar.set)
        self.szukaj_pojazd_db_scrollbar.grid(column=2, row=4, sticky='NS')

        # SZUKAJ DB VIEW FRAME KIEROWCA
        self.szukaj_kierowca_wyniki_frame = ttk.LabelFrame(self.wyszukiwanie, text='Wyniki wyszukiwania')
        self.szukaj_kierowca_wyniki_frame.grid(column=0, row=3, pady=10, padx=30)

        # SZUKAJ DATABASE VIEW KIEROWCA
        self.szukaj_kierowca_db_columns = ('id', 'PESEL', 'Nazwisko', 'Imię', 'nr_kk', 'Data pobrania', 'Pobierający',
                                           'Operator pobranie', 'Data zwrotu', 'Zwracający', 'Operator zwrot')
        self.szukaj_kierowca_db_view = ttk.Treeview(self.szukaj_kierowca_wyniki_frame,
                                                    columns=self.szukaj_kierowca_db_columns, show='headings', height=25)

        col_width_kier = int(self.window_width / 11)
        for column in self.szukaj_kierowca_db_columns:
            self.szukaj_kierowca_db_view.heading(column, text=column, anchor='center')
            self.szukaj_kierowca_db_view.column(column, width=col_width_kier)

        self.szukaj_kierowca_db_view.column('id', width=80)

        self.szukaj_kierowca_db_view.grid(column=0, row=4, sticky='NEWS')

        # SCROLLBAR
        self.szukaj_kierowca_db_scrollbar = ttk.Scrollbar(self.szukaj_kierowca_wyniki_frame, orient=tk.VERTICAL,
                                                          command=self.szukaj_kierowca_db_view.yview)
        self.szukaj_kierowca_db_view.configure(yscrollcommand=self.szukaj_kierowca_db_scrollbar.set)
        self.szukaj_kierowca_db_scrollbar.grid(column=1, row=4, sticky='NS')

        # CLOSE BUTTON
        self.zamknij_button3 = ttk.Button(self.wyszukiwanie, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button3.grid(column=0, row=6, padx=10, pady=10)

        self.root.mainloop()

    def edit_pojazd(self):
        """Function to update data in DB. Binded to 'Edytuj' button in 'kierowca' searching engine.
        Function open a new window with fields filled with selected row data.
        When all search fields are empty show a Showinfo with short message """
        try:
            okno_edycji = EditPojazd()
            entries = okno_edycji.entries_frame.winfo_children()
            for item in self.szukaj_pojazd_db_view.selection():
                values = self.szukaj_pojazd_db_view.item(item, 'values')
            for i, entry in enumerate(entries):
                entry.insert(0, values[i + 1])
            okno_edycji.id_entry.insert(0, values[0])
            okno_edycji.id_entry.configure(state='disabled')
        except UnboundLocalError:
            okno_edycji.root.destroy()
            showinfo('Brak danych', 'Nie zaznaczono żadnego wpisu.')

    def edit_kierowca(self):
        """Function to update data in DB. Binded to 'Edytuj' button in 'kierowca' searching engine.
        Function open a new window with fields filled with selected row data.
        When all search fields are empty show a Showinfo with short message """
        try:
            okno_edycji = EditKierowca()
            entries = okno_edycji.entries_frame.winfo_children()
            for item in self.szukaj_kierowca_db_view.selection():
                values = self.szukaj_kierowca_db_view.item(item, 'values')
            for i, entry in enumerate(entries):
                entry.insert(0, values[i + 1])
            okno_edycji.id_entry.insert(0, values[0])
            okno_edycji.id_entry.configure(state='disabled')
        except UnboundLocalError:
            okno_edycji.root.destroy()
            showinfo('Brak danych', 'Nie zaznaczono żadnego wpisu.')

    def wyszukaj_pojazd_click(self):
        tr = self.szukaj_tr_entry.get().upper()
        os_pob = self.szukaj_pojazd_osoba_pobranie_entry.get().title()
        os_zw = self.szukaj_pojazd_osoba_zwrot_entry.get().title()
        op_pob = self.szukaj_pojazd_operator_pobranie_entry.get().title()
        op_zw = self.szukaj_pojazd_operator_zwrot_entry.get().title()
        data_pob_od = self.szukaj_pojazd_data_od_pobranie_entry.get()
        data_pob_do = self.szukaj_pojazd_data_do_pobranie_entry.get()
        data_zw_od = self.szukaj_pojazd_data_od_zwrot_entry.get()
        data_zw_do = self.szukaj_pojazd_data_do_zwrot_entry.get()
        keys = ['tr', 'osoba_pobranie', 'operator_pobranie',
                'osoba_zwrot', 'operator_zwrot', 'data_pobrania', 'data_zwrotu']
        values = [tr, os_pob, op_pob, os_zw, op_zw]
        warunki = {k: v for k, v in zip(keys, values)}
        sql = self.sql_select('pojazdy', **warunki)
        daty = []
        if data_pob_od:
            daty.append(f"data_pobrania >= '{data_pob_od} 00:00'")
        if data_pob_do:
            daty.append(f"data_pobrania <= '{data_pob_do} 23:59'")
        if data_zw_od:
            daty.append(f"data_zwrotu >= '{data_zw_od} 00:00'")
        if data_zw_do:
            daty.append(f"data_zwrotu >= '{data_zw_do} 23:59'")
        sql = sql[:-1] + " AND ".join(daty) + ";"
        print(sql)
        self.szukaj_pojazd_db_view.delete(*self.szukaj_pojazd_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        try:
            for n in self.cursor.execute(sql):
                self.szukaj_pojazd_db_view.insert("", tk.END, values=n)
        except sqlite3.OperationalError:
            for n in self.cursor.execute("SELECT * FROM pojazdy"):
                self.szukaj_pojazd_db_view.insert("", tk.END, values=n)
        self.db.close()

    def wyszukaj_kierowca_click(self):
        pesel = self.szukaj_kierowca_pesel_entry.get()
        nr_kk = self.szukaj_kierowca_nr_kk_entry.get()
        imie = self.szukaj_kierowca_imie_pobranie_entry.get()
        nazwisko = self.szukaj_kierowca_nazwisko_pobranie_entry.get()
        op_pob = self.szukaj_kierowca_operator_pobranie_entry.get()
        op_zw = self.szukaj_kierowca_operator_zwrot_entry.get()
        os_pob = self.szukaj_kierowca_osoba_pobranie_entry.get()
        os_zw = self.szukaj_kierowca_osoba_zwrot_entry.get()
        data_pob_od = self.szukaj_kierowca_data_od_pobranie_entry.get()
        data_pob_do = self.szukaj_kierowca_data_do_pobranie_entry.get()
        data_zw_od = self.szukaj_kierowca_data_od_zwrot_entry.get()
        data_zw_do = self.szukaj_kierowca_data_do_zwrot_entry.get()
        keys = ['pesel', 'nr_kk', 'imie', 'nazwisko', 'operator_pobranie',
                'operator_zwrot', 'osoba_pobranie', 'osoba_zwrot']
        values = [pesel, nr_kk, imie, nazwisko, op_pob, op_zw, os_pob, os_zw]
        warunki = {k: v for k, v in zip(keys, values)}
        sql = self.sql_select('kierowcy', **warunki)
        daty = []
        if data_pob_od:
            daty.append(f"data_pobrania >= '{data_pob_od} 00:00'")
        if data_pob_do:
            daty.append(f"data_pobrania <= '{data_pob_do} 23:59'")
        if data_zw_od:
            daty.append(f"data_zwrotu >= '{data_zw_od} 00:00'")
        if data_zw_do:
            daty.append(f"data_zwrotu >= '{data_zw_do} 23:59'")
        if len(sql) > 30:
            sql = sql[:-1] + " AND  "
        sql = sql[:-1] + " AND ".join(daty) + ";"
        print(sql)
        self.szukaj_kierowca_db_view.delete(*self.szukaj_kierowca_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        try:
            for n in self.cursor.execute(sql):
                self.szukaj_kierowca_db_view.insert("", tk.END, values=n)
        except sqlite3.OperationalError:
            for n in self.cursor.execute("SELECT * FROM kierowcy"):
                self.szukaj_kierowca_db_view.insert("", tk.END, values=n)
        self.db.close()

    def clear_entries(self):
        for widget in self.wyszukaj_kierowca_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)

    def sql_select(self, tabela, **kwargs):
        """Generate SQL queries for a SELECT statement matching the kwargs passed"""
        sql = list()
        sql.append(f"SELECT * FROM {tabela} ")
        if kwargs:
            sql.append(f"WHERE " + " AND ".join(f"{k} = '{v}'" for k, v in kwargs.items() if v != ''))
        sql.append(";")
        return "".join(sql)

    def sql_update(self, tabela, **kwargs):
        """Update rows in table"""
        keys = [f"{k}" for k in kwargs]
        values = [f"{v}" for v in kwargs.values()]
        sql = list()
        sql.append(f"UPDATE {tabela}")

    def wybierz_rejestr(self):
        if self.selected_value.get():
            self.wyszukaj_kierowca_frame.grid_forget()
            self.szukaj_kierowca_wyniki_frame.grid_forget()
            self.wyszukaj_pojazd_frame.grid(column=0, row=0)
            self.szukaj_pojazd_wyniki_frame.grid(column=0, row=3, sticky='NEWS', pady=10, padx=30)
            self.szukaj_wyszukaj_button.configure(command=self.wyszukaj_pojazd_click)
            self.szukaj_edytuj_button.configure(command=self.edit_pojazd)
        else:
            self.wyszukaj_pojazd_frame.grid_forget()
            self.szukaj_pojazd_wyniki_frame.grid_forget()
            self.wyszukaj_kierowca_frame.grid(column=0, row=0)
            self.szukaj_kierowca_wyniki_frame.grid(column=0, row=3, sticky='NEWS', pady=10, padx=30)
            self.szukaj_wyszukaj_button.configure(command=self.wyszukaj_kierowca_click)
            self.szukaj_edytuj_button.configure(command=self.edit_kierowca)

    def kp_data_urodzenia(self):
        if self.kp_data_ur_var:
            self.kp_pesel_entry.config(state='disabled')
            self.kp_data_ur_entry.config(state='normal')
            self.kp_data_ur_entry.delete(0, "end")
            self.kp_data_ur_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem
        if not self.kp_data_ur_var.get():
            self.kp_data_ur_entry.insert(0, "RRRR-MM-DD")
            self.kp_data_ur_entry.config(state="disabled")
            self.kp_pesel_entry.config(state='normal')
            self.kp_pesel_entry.focus_set()

    def sprawdz_pesel_pobranie(self, event):
        if len(self.kp_pesel_string.get()) == 11:
            self.kp_pesel_entry.configure(background='light green')
        else:
            self.kp_pesel_entry.configure(background='pink')

    def sprawdz_pesel_zwrot(self, event):
        if len(self.kz_pesel_string.get()) == 11:
            self.kz_pesel_entry.configure(background='light green')
        else:
            self.kz_pesel_entry.configure(background='pink')

    def show_all(self):
        # Funkcja do przycisku "Pokaż wszystko", żeby wyświetlić wszystkie dane z bazy
        self.pojazd_db_view.delete(*self.pojazd_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        for n in self.cursor.execute(""" SELECT * FROM pojazdy """):
            self.pojazd_db_view.insert("", tk.END, values=n)
        self.db.close()

    def show_all_kierowca(self):
        # Funkcja do przycisku "Pokaż wszystko", żeby wyświetlić wszystkie dane z bazy
        self.kierowca_db_view.delete(*self.kierowca_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        for n in self.cursor.execute(""" SELECT * FROM kierowcy """):
            self.kierowca_db_view.insert("", tk.END, values=n)
        self.db.close()

    def enable_frames(self, event):
        # Funkcja aktywująca okienka po wybraniu operatora
        self.pp_tablica_entry.config(state='normal')
        self.pp_osoba_combobox.config(state='normal')
        self.pz_tablica_entry.config(state='normal')
        self.pz_osoba_combobox.config(state='normal')
        self.kp_pesel_entry.config(state='normal')
        self.kp_imie_entry.config(state='normal')
        self.kp_nazwisko_entry.config(state='normal')
        self.kp_nr_kk_entry.config(state='normal')
        self.kp_osoba_combobox.config(state='normal')
        self.kp_uwagi.config(state='normal', background='white')
        self.kz_pesel_entry.config(state='normal')
        # self.kz_imie_entry.config(state='normal')
        # self.kz_nazwisko_entry.config(state='normal')
        # self.kz_nr_kk_entry.config(state='normal')
        self.kz_osoba_combobox.config(state='normal')

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

    def kp_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.kp_data.get():
            self.kp_data_entry.config(state='normal')
            self.kp_data_entry.delete(0, "end")
            self.kp_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem
        if not self.kp_data.get():
            self.kp_data_entry.insert(0, "RRRR-MM-DD")
            self.kp_data_entry.config(state="disabled")

    def kz_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.kz_data.get():
            self.kz_data_entry.config(state='normal')
            self.kz_data_entry.delete(0, "end")
            self.kz_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem
        if not self.kz_data.get():
            self.kz_data_entry.insert(0, "RRRR-MM-DD")
            self.kz_data_entry.config(state="disabled")

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
        format_daty = re.compile(r"^[1-2][019]\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[1-2]\d|3[0-1])$")
        if format_daty.search(data):
            return True
        else:
            return False

    def insert_pobranie_to_db(self, tr, data, osoba, operator):
        return f""" INSERT INTO pojazdy (tr, data_pobrania, osoba_pobranie, operator_pobranie) 
                                VALUES("{tr}", "{data}", "{osoba}", "{operator}"); """

    def pp_potwierdzenie_zapisu(self, tr, data, pobierajacy, operator):
        # Funkcja wyszukuje czy w bazie jest zapisany podany rekord,
        # jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych,
        # jeśli nie to obrazek błędu i tekst o braku zapisu
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
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        teczka = self.pp_tablica_entry.get().upper()
        osoba = self.pp_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        if self.pp_data.get():
            if self.format_inna_data(self.pp_data_entry.get()):
                now = self.pp_data_entry.get() + ' 12:00'
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
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        teczka = self.pz_tablica_entry.get().upper()
        osoba = self.pz_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        if self.pz_data.get():
            if self.format_inna_data(self.pz_data_entry.get()):
                now = self.pz_data_entry.get() + ' 12:00'
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

    def kp_czy_dubel(self, pesel):
        # Funkcja sprawdza, czy w bazie istnieje już wpis z podanymi danymi bez daty zwrotu
        wyszukanie_wpisu = self.kierowca_select_query(pesel, '', '', '', '', '', 'IS NULL')
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False

    def check_pesel(self, pesel):
        # Funkcja sprawdzająca czy nr PESEL składa się z cyfr i ma 11 znaków
        return pesel.isdigit() and len(pesel) == 11

    def insert_kierowca_pobranie_to_db(self, pesel, imie, nazwisko, nr_kk, data, osoba, operator):
        return f'''INSERT INTO kierowcy (pesel, nazwisko, imie, nr_kk, data_pobrania, osoba_pobranie, operator_pobranie) 
                            VALUES("{pesel}", "{nazwisko}", "{imie}", "{nr_kk}", "{data}", "{osoba}", "{operator}");'''

    def kierowca_select_query(self, pesel='', imie='', nazwisko='', data='', osoba='', oper='', data_zwrot=''):
        query = "SELECT * FROM kierowcy WHERE"
        if pesel != '':
            query += f" pesel = '{pesel}'"
        if imie != '':
            query += f" AND imie = '{imie}'"
        if nazwisko != '':
            query += f" AND nazwisko = '{nazwisko}'"
        if data != '':
            query += f" AND data_pobrania = '{data}'"
        if osoba != '':
            query += f" AND osoba_pobranie = '{osoba}'"
        if oper != '':
            query += f" AND operator_pobranie = '{oper}'"
        if data_zwrot != '':
            if data_zwrot == 'IS NULL':
                query += " AND data_zwrotu IS NULL"
            else:
                query += f" AND data_zwrotu = '{data_zwrot}'"
        return query

    def kp_potwierdzenie_zapisu(self, pesel, imie, nazwisko, data, pobierajacy, operator):
        # Funkcja wyszukuje czy w tabeli kierowcy jest zapisany podany rekord,
        # jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych,
        # jeśli nie to obrazek błędu i tekst o braku zapisu
        wyszukanie_wpisu = self.kierowca_select_query(pesel, imie, nazwisko, data, pobierajacy, operator, 'IS NULL')
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) == 1:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.kierowca_db_view.insert("", tk.END, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.kp_potwierdzenie_label.configure(
                image=img,
                text=f"   Prawidłowo zapisano pobranie teczki osoby o "
                     f"nr PESEL: '{pesel}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.kp_potwierdzenie_label.image = img
        else:
            wrong = tk.PhotoImage(file='wrong.jpg')
            self.kp_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki o nr PESEL: {pesel}.",
                compound="left", font="Helvetica 8"
            )
            self.kp_potwierdzenie_label.image = wrong

    def kierowca_zastosuj_pobranie(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        pesel = self.kp_pesel_string.get()
        imie = self.kp_imie_entry.get().title()
        nazwisko = self.kp_nazwisko_entry.get().title()
        nr_kk = self.kp_nr_kk_entry.get()
        osoba = self.kp_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()

        if self.kp_data_ur_var.get():
            if self.format_inna_data(self.kp_data_ur_entry.get()):
                pesel = self.kp_data_ur_entry.get()
            else:
                return showerror("Błąd", "Sprawdź czy podana data urodzenia jest prawidłowa. "
                                         "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")
        if self.kp_data.get():
            if self.format_inna_data(self.kp_data_entry.get()):
                now = self.kp_data_entry.get() + ' 12:00'
            else:
                return showerror("Błąd", "Sprawdź czy podana data jest prawidłowa. "
                                         "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")

        if pesel == '' or osoba == '' or imie == '' or nazwisko == '':
            # Jeśli nie wpisze się TR lub pobierającego wyskoczy błąd
            return showinfo("Błąd", "Pola 'PESEL', 'Imię', 'Nazwisko' i 'Osoba pobierająca' są obowiązkowe!")

        elif self.kp_czy_dubel(pesel):
            return showwarning("Warning", f"Teczka osoby {imie} {nazwisko} o nr PESEL: '{pesel}' "
                                          f"została już pobrana i nie odnotowano jej zwrotu.")

        elif self.check_pesel(pesel):
            # Jeśli nr TR jest poprawny - wstaw dane do bazy
            self.cursor.execute(self.insert_kierowca_pobranie_to_db(pesel, imie, nazwisko, nr_kk, now, osoba, operator))
            self.db.commit()

        elif not self.check_pesel(pesel):
            # Jeśli nr TR jest błędny pokaż zapytanie
            poprawny_pesel = askyesno("Błąd",
                                      f"Numer PESEL powinien składać się z 11 cyfr.\n"
                                      f"Czy nr PESEL: '{pesel}' jest prawidłowy?")
            if poprawny_pesel:
                # Po zatwierdzeniu wprowadzi dane do bazy
                self.cursor.execute(
                    self.insert_kierowca_pobranie_to_db(pesel, imie, nazwisko, nr_kk, now, osoba, operator))
                self.db.commit()

        self.kp_potwierdzenie_zapisu(pesel, imie, nazwisko, now, osoba, operator)
        self.db.close()

    def kierowca_potwierdzenie_zwrotu(self, pesel, data, pobierajacy, operator):
        # Funkcja wyszukuje czy podana teczka występuje z podaną datą zwrotu.
        # Jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych
        wyszukanie_wpisu = f""" SELECT * FROM kierowcy WHERE pesel = "{pesel}" 
                                                        AND data_zwrotu >= "{data}" 
                                                        AND osoba_zwrot = "{pobierajacy}" 
                                                        AND operator_zwrot = "{operator}"; """
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) >= 1:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.kierowca_db_view.insert("", tk.END, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.kz_potwierdzenie_label.configure(
                image=img,
                text=f"Prawidłowo odnotowano zwrot teczki osoby o nr PESEL: '{pesel}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.kz_potwierdzenie_label.image = img
        else:
            wrong = tk.PhotoImage(file='wrong.jpg')
            self.kz_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki osoby o nr PESEL: {pesel}.",
                compound="left", font="Helvetica 8"
            )
            self.kz_potwierdzenie_label.image = wrong

    def kierowca_zastosuj_zwrot(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        pesel = self.kz_pesel_string.get()
        # imie = self.kz_imie_entry.get().title()
        # nazwisko = self.kz_nazwisko_entry.get().title()
        osoba = self.kz_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        if self.kz_data.get():
            if self.format_inna_data(self.kz_data_entry.get()):
                now = self.kz_data_entry.get() + ' 12:00'
            else:
                return showerror("Błąd", "Sprawdź czy podana data jest prawidłowa. "
                                         "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")

        if pesel == "":
            # Jeśli nie wpisze się PESELu  wyskoczy błąd
            return showerror("Błąd", "Pole 'PESEL' jest obowiązkowe!. W przypadku braku nr PESEL podaj datę urodzenia.")
        if osoba == "":
            return showerror("Błąd", "Pole 'Osoba zwracająca' jest obowiązkowe!")

        self.cursor.execute(self.kierowca_select_query(pesel, '', '', '', '', '', 'IS NULL'))
        if len(self.cursor.fetchall()) == 0:
            showinfo("Informacja", f"Nie znaleziono niezwróconej teczki osoby o nr PESEL: '{pesel}'.")
        else:
            self.cursor.execute(f""" UPDATE kierowcy 
            SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", operator_zwrot = "{operator}" 
            WHERE pesel = "{pesel}" AND data_zwrotu IS NULL; """)
            self.db.commit()

        self.kierowca_potwierdzenie_zwrotu(pesel, now, osoba, operator)
        self.db.close()

    def operator_edit_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja operatorów")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Operator', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Operator', text='Operator', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usuń', command=self.delete_operator)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj operatora")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imię i nazwisko')
        self.dodaj_label.grid(column=0, row=0, pady=10, padx=10)

        self.dodaj_entry = ttk.Entry(self.dodaj_frame, width=25)
        self.dodaj_entry.grid(column=1, row=0, padx=10)

        self.dodaj_button = ttk.Button(self.dodaj_frame, text='Dodaj', command=self.add_operator)
        self.dodaj_button.grid(column=0, columnspan=2, row=1, pady=10)

        self.zamknij_button4 = ttk.Button(self.window, text='Zamknij', command=lambda: self.window.destroy())
        self.zamknij_button4.grid(column=0, row=4, pady=20)

        for name in self.operator_values:
            self.lista_operatorow.insert("", tk.END, values=[name])

    def delete_operator(self):
        ''' Function to removing elements from list of operators'''
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')
            self.operator_values.remove(values[0])
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.operator_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.operator_combobox.config(values=self.operator_values)
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_operator(self):
        ''' Function to adding elements to the list of operators'''
        try:
            oper = self.dodaj_entry.get()
            self.operator_values.append(oper)
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.operator_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.operator_combobox.config(values=self.operator_values)
            self.dodaj_entry.delete(0, tk.END)
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def osoba_pojazd_edit_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja osób pobierających akta pojazdu")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Operator', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Operator', text='Operator', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usuń', command=self.delete_pojazd_osoba)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj operatora")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imię i nazwisko')
        self.dodaj_label.grid(column=0, row=0, pady=10, padx=10)

        self.dodaj_entry = ttk.Entry(self.dodaj_frame, width=25)
        self.dodaj_entry.grid(column=1, row=0, padx=10)

        self.dodaj_button = ttk.Button(self.dodaj_frame, text='Dodaj', command=self.add_pojazd_osoba)
        self.dodaj_button.grid(column=0, columnspan=2, row=1, pady=10)

        self.zamknij_button4 = ttk.Button(self.window, text='Zamknij', command=lambda: self.window.destroy())
        self.zamknij_button4.grid(column=0, row=4, pady=20)

        for name in self.pp_osoba_values:
            self.lista_operatorow.insert("", tk.END, values=[name])

    def delete_pojazd_osoba(self):
        ''' Function to removing elements from list of persons'''
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')
            self.pp_osoba_values.remove(values[0])
            self.pz_osoba_values.remove(values[0])
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_osoba_combobox.config(values=self.pp_osoba_values)
            self.pz_osoba_combobox.config(values=self.pz_osoba_values)
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_pojazd_osoba(self):
        ''' Function to adding elements to the list of operators'''
        try:
            oper = self.dodaj_entry.get()
            self.pp_osoba_values.append(oper)
            self.pz_osoba_values.append(oper)
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_osoba_combobox.config(values=self.pp_osoba_values)
            self.pz_osoba_combobox.config(values=self.pz_osoba_values)
            self.dodaj_entry.delete(0, tk.END)
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def osoba_kierowca_edit_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja osób pobierających akta kierowcy")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Operator', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Operator', text='Operator', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usuń', command=self.delete_kierowca_osoba)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj osobę")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imię i nazwisko')
        self.dodaj_label.grid(column=0, row=0, pady=10, padx=10)

        self.dodaj_entry = ttk.Entry(self.dodaj_frame, width=25)
        self.dodaj_entry.grid(column=1, row=0, padx=10)

        self.dodaj_button = ttk.Button(self.dodaj_frame, text='Dodaj', command=self.add_kierowca_osoba)
        self.dodaj_button.grid(column=0, columnspan=2, row=1, pady=10)

        self.zamknij_button4 = ttk.Button(self.window, text='Zamknij', command=lambda: self.window.destroy())
        self.zamknij_button4.grid(column=0, row=4, pady=20)

        for name in self.kp_osoba_values:
            self.lista_operatorow.insert("", tk.END, values=[name])

    def delete_kierowca_osoba(self):
        ''' Function to removing elements from list of persons'''
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')
            self.kp_osoba_values.remove(values[0])
            self.kz_osoba_values.remove(values[0])
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_osoba_combobox.config(values=self.kp_osoba_values)
            self.kz_osoba_combobox.config(values=self.kz_osoba_values)
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_kierowca_osoba(self):
        ''' Function to adding elements to the list of operators'''
        try:
            oper = self.dodaj_entry.get()
            self.kp_osoba_values.append(oper)
            self.kz_osoba_values.append(oper)
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_osoba_combobox.config(values=self.kp_osoba_values)
            self.kz_osoba_combobox.config(values=self.kz_osoba_values)
            self.dodaj_entry.delete(0, tk.END)
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def info(self):
        self.window = tk.Toplevel(self.root)
        self.window.title('Informacje')

        info_label1 = tk.Label(self.window, text='Wersja programu:')
        info_label3 = tk.Label(self.window, text='Autor:')
        info_label5 = tk.Label(self.window, text='Data wydania:')
        info_label1.grid(column=0, row=0, pady=5, sticky='E')
        info_label3.grid(column=0, row=1, pady=5, sticky='E')
        info_label5.grid(column=0, row=2, pady=5, sticky='E')

        info_label2 = tk.Label(self.window, text='1.0')
        info_label4 = tk.Label(self.window, text='Martin Brzeziński')
        info_label6 = tk.Label(self.window, text='1 października 2022')
        info_label2.grid(column=1, row=0, pady=5, sticky='W')
        info_label4.grid(column=1, row=1, pady=5, sticky='W')
        info_label6.grid(column=1, row=2, pady=5, sticky='W')

        self.window.columnconfigure('all', pad=50)
        self.window.rowconfigure('all', pad=10)


class EditKierowca(App):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Edycja wpisu")
        self.root.attributes('-topmost', 1)
        self.root.geometry('400x450+400+400')

        self.id_label = tk.Label(self.root, text='ID')
        self.id_label.grid(column=0, row=0, sticky='E')

        self.id_entry = tk.Entry(self.root, width=10, font='Arial 11')
        self.id_entry.grid(column=1, row=0, sticky='W', pady=5)

        self.labels_frame = tk.Label(self.root)
        self.labels_frame.grid(column=0, row=1, ipadx=30)

        self.entries_frame = tk.Label(self.root)
        self.entries_frame.grid(column=1, row=1, ipadx=50)

        labels = {'pesel': 'PESEL',
                  'nazwisko': 'Nazwisko',
                  'imie': 'Imię',
                  'nr_kk': 'nr_kk',
                  'data_pob': 'Data pobrania',
                  'osoba_pob': 'Pobierający',
                  'operator_pob': 'Operator Pobranie',
                  'data_zw': 'Data zwrotu',
                  'osoba_zw': 'Zwracający',
                  'operator_zw': 'Operator zwrot'}
        for k, v in labels.items():
            self.k = tk.Label(self.labels_frame, text=v).pack(anchor='e', pady=5)

        self.pesel_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.pesel_entry.pack(anchor='w', pady=5)
        self.nazwisko_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.nazwisko_entry.pack(anchor='w', pady=5)
        self.imie_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.imie_entry.pack(anchor='w', pady=5)
        self.nr_kk_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.nr_kk_entry.pack(anchor='w', pady=5)
        self.data_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.data_pob_entry.pack(anchor='w', pady=5)
        self.osoba_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.osoba_pob_entry.pack(anchor='w', pady=5)
        self.operator_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_pob_entry.pack(anchor='w', pady=5)
        self.data_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.data_zw_entry.pack(anchor='w', pady=5)
        self.osoba_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.osoba_zw_entry.pack(anchor='w', pady=5)
        self.operator_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_zw_entry.pack(anchor='w', pady=5)

        self.edycja_zamknij_button = ttk.Button(self.root, text='Zamknij', command=lambda: self.root.destroy())
        self.edycja_zamknij_button.grid(column=0, row=2, pady=10)

        self.edycja_accept_button = ttk.Button(self.root, text='Akceptuj', command=self.accept)
        self.edycja_accept_button.grid(column=1, row=2, pady=10)

        self.edycja_delete_button = ttk.Button(self.root, text='Usuń', command=self.delete)
        self.edycja_delete_button.grid(column=1, row=3, pady=10)

    def accept(self):
        values = []
        columns = ['pesel', 'nazwisko', 'imie', 'nr_kk', 'data_pobrania', 'osoba_pobranie',
                   'operator_pobranie', 'data_zwrotu', 'osoba_zwrot', 'operator_zwrot']
        a = self.entries_frame.winfo_children()
        for entry1 in a:
            values.append(entry1.get())
        pairs = {}
        for p in zip(columns, values):
            pairs[p[0]] = p[1]
        print(self.sql_edit('kierowcy', **pairs))
        try:
            sql = self.sql_edit('kierowcy', **pairs)
            with sqlite3.connect('archeo.db') as self.db:
                self.cursor = self.db.cursor()
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
            showinfo('Zapisano', 'Wprowadzone zmiany zostały zapisane.')
            self.root.destroy()
        except:
            showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.')

    def delete(self):
        potwierdzenie = askyesno('Ostrzeżenie!', 'Usuwasz wpis z bazy danych, ta czynność jest NIEODWRACALNA!\n'
                                                 'Czy na pewno chcesz usunąć ten wpis?')
        if potwierdzenie:
            try:
                sql = self.sql_delete('kierowcy')
                with sqlite3.connect('archeo.db') as self.db:
                    self.cursor = self.db.cursor()
                self.cursor.execute(sql)
                self.db.commit()
                self.db.close()
                showinfo('Usunięto', 'Zaznaczony wpis został usunięty z bazy danych.')
                self.root.destroy()
            except:
                showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.')

    def sql_edit(self, tabela: str, **kwargs) -> str:
        db_id = self.id_entry.get()
        sql = f"UPDATE {tabela} SET "
        values = []
        for k, v in kwargs.items():
            values.append(f"{k} = '{v}'")
        sql = sql + ", ".join(values) + f" WHERE id = '{db_id}';"
        return sql

    def sql_delete(self, tabela: str) -> str:
        db_id = self.id_entry.get()
        sql = f"DELETE FROM {tabela} WHERE id = '{db_id}';"
        return sql


class EditPojazd(App):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Edycja wpisu")
        self.root.attributes('-topmost', 1)
        self.root.geometry('400x450+400+400')

        self.id_label = tk.Label(self.root, text='ID')
        self.id_label.grid(column=0, row=0, sticky='E')

        self.id_entry = tk.Entry(self.root, width=10, font='Arial 11')
        self.id_entry.grid(column=1, row=0, sticky='W', pady=5)

        self.labels_frame = tk.Label(self.root)
        self.labels_frame.grid(column=0, row=1, ipadx=30)

        self.entries_frame = tk.Label(self.root)
        self.entries_frame.grid(column=1, row=1, ipadx=50)

        labels = {'tr': 'TR',
                  'data_pobrania': 'Data pobrania',
                  'osoba_pobranie': 'Pobierający',
                  'operator_pobranie': 'Operator pobranie',
                  'data_zwrotu': 'Data zwrotu',
                  'osoba_zwrot': 'Zwracający',
                  'operator_zwrot': 'Operator zwrot'}

        for k, v in labels.items():
            self.k = tk.Label(self.labels_frame, text=v).pack(anchor='e', pady=5)

        self.tr_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.tr_entry.pack(anchor='w', pady=5)
        self.data_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.data_pob_entry.pack(anchor='w', pady=5)
        self.osoba_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.osoba_pob_entry.pack(anchor='w', pady=5)
        self.operator_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_pob_entry.pack(anchor='w', pady=5)
        self.data_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.data_zw_entry.pack(anchor='w', pady=5)
        self.osoba_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.osoba_zw_entry.pack(anchor='w', pady=5)
        self.operator_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_zw_entry.pack(anchor='w', pady=5)

        self.edycja_zamknij_button = ttk.Button(self.root, text='Zamknij', command=lambda: self.root.destroy())
        self.edycja_zamknij_button.grid(column=0, row=2, pady=10)

        self.edycja_accept_button = ttk.Button(self.root, text='Akceptuj', command=self.accept)
        self.edycja_accept_button.grid(column=1, row=2, pady=10)

        self.edycja_delete_button = ttk.Button(self.root, text='Usuń', command=self.delete)
        self.edycja_delete_button.grid(column=1, row=3, pady=10)

    def accept(self):
        values = []
        columns = ['tr', 'data_pobrania', 'osoba_pobranie',
                   'operator_pobranie', 'data_zwrotu', 'osoba_zwrot', 'operator_zwrot']
        a = self.entries_frame.winfo_children()
        for entry1 in a:
            values.append(entry1.get())
        pairs = {}
        for p in zip(columns, values):
            pairs[p[0]] = p[1]
        print(self.sql_edit('pojazdy', **pairs))
        try:
            sql = self.sql_edit('pojazdy', **pairs)
            with sqlite3.connect('archeo.db') as self.db:
                self.cursor = self.db.cursor()
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
            showinfo('Zapisano', 'Wprowadzone zmiany zostały zapisane.')
            self.root.destroy()
        except:
            showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.')

    def delete(self):
        potwierdzenie = askyesno('Ostrzeżenie!', 'Usuwasz wpis z bazy danych, ta czynność jest NIEODWRACALNA!\n'
                                                 'Czy na pewno chcesz usunąć ten wpis?')
        if potwierdzenie:
            try:
                sql = self.sql_delete('pojazdy')
                with sqlite3.connect('archeo.db') as self.db:
                    self.cursor = self.db.cursor()
                self.cursor.execute(sql)
                self.db.commit()
                self.db.close()
                showinfo('Usunięto', 'Zaznaczony wpis został usunięty z bazy danych.')
                self.root.destroy()
            except:
                showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.')

    def sql_edit(self, tabela: str, **kwargs) -> str:
        db_id = self.id_entry.get()
        sql = f"UPDATE {tabela} SET "
        values = []
        for k, v in kwargs.items():
            values.append(f"{k} = '{v}'")
        sql = sql + ", ".join(values) + f" WHERE id = '{db_id}';"
        return sql

    def sql_delete(self, tabela: str) -> str:
        db_id = self.id_entry.get()
        sql = f"DELETE FROM {tabela} WHERE id = '{db_id}';"
        return sql


if __name__ == '__main__':
    app = App()
