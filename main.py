import _tkinter
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror, askyesno, showinfo, showwarning
import re
from datetime import datetime, timedelta
import sqlite3
import json
import shutil
import os


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Archeo 2022')
        self.icon = tk.PhotoImage(file='ikona2.png')
        self.root.iconphoto(True, self.icon)

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS pojazdy( id integer PRIMARY KEY AUTOINCREMENT, 
                                                                    tr text NOT NULL, 
                                                                    data_pobrania text NOT NULL, 
                                                                    osoba_pobranie text NOT NULL, 
                                                                    prowadzacy text NOT NULL, 
                                                                    operator_pobranie text NOT NULL, 
                                                                    data_zwrotu text, 
                                                                    osoba_zwrot text, 
                                                                    operator_zwrot text,
                                                                    uwagi text); """)

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS kierowcy( id integer PRIMARY KEY AUTOINCREMENT, 
                                                                    pesel text, 
                                                                    nazwisko text NOT NULL, 
                                                                    imie text NOT NULL,  
                                                                    nr_kk text NOT NULL, 
                                                                    data_pobrania text NOT NULL, 
                                                                    osoba_pobranie text NOT NULL, 
                                                                    prowadzacy text NOT NULL, 
                                                                    operator_pobranie text NOT NULL, 
                                                                    data_zwrotu text, 
                                                                    osoba_zwrot text, 
                                                                    operator_zwrot text, 
                                                                    uwagi text); """)
        self.db.close()

        # Set LABEL STYLE
        self.style = ttk.Style(self.root)
        self.style.configure('TLabel', font='Arial 12 bold')
        self.tv_style = ttk.Style(self.root)
        self.tv_style.configure('Treeview', rowheight=25)
        self.tv_style.configure('Treeview', font=('Tahoma', 11))

        self.tvh_style = ttk.Style(self.root)
        self.tvh_style.configure("Treeview.Heading", font="Helvetica 10 bold", foreground="black")

        # Screen size
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Window size
        self.window_width = int(self.screen_width * 0.9)
        self.window_height = int(self.screen_height * 0.87)

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
        self.file_menu.add_command(label='Statystyki', command=self.statystyki)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Pomniejsz', command=self.pomniejsz)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Zamknij', command=self.root.destroy)

        # Options items
        self.help_menu.add_command(label='Edytuj operatorów', command=self.operator_edit_window)
        self.help_menu.add_command(label='Edytuj osoby - Kierowca', command=self.osoba_kierowca_edit_window)
        self.help_menu.add_command(label='Edytuj osoby - Pojazd', command=self.osoba_pojazd_edit_window)
        self.help_menu.add_command(label='Edytuj prowadzących - Kierowca', command=self.prowadzacy_kierowca_edit_window)
        self.help_menu.add_command(label='Edytuj prowadzących - Pojazd', command=self.prowadzacy_pojazd_edit_window)

        self.menubar.add_cascade(label='Menu', menu=self.file_menu)
        self.menubar.add_cascade(label='Opcje', menu=self.help_menu)

        # Welcome label
        self.welcome = tk.Label(self.root,
                                background='green2',
                                foreground='white',
                                font='Arial 15 bold',
                                text='Witaj w Archeo 2022!'
                                )
        self.welcome.pack(fill='both', ipady=5)

        # OPERATOR select
        plik_json = open('osoby.json')
        obj = json.load(plik_json)
        self.operator_values = obj['operator']
        plik_json.close()

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
        self.operator_combobox = ttk.Combobox(self.operator_frame, values=self.operator_values, font='Arial 13 bold')
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

        self.pojazd.columnconfigure(0, minsize=10)
        self.pojazd.columnconfigure(1, weight=3)
        self.pojazd.columnconfigure(2, weight=1)
        self.pojazd.columnconfigure(3, weight=3)
        self.pojazd.columnconfigure(4, minsize=30)

        # POBRANIE AKT POJAZDU --> pp
        self.pojazd_pobranie_labelframe = tk.LabelFrame(self.pojazd, text='Pobranie akt pojazdu')
        self.pojazd_pobranie_labelframe.grid(column=1, row=0, padx=30, sticky='NEWS', pady=10)

        self.pojazd_pobranie_labelframe.columnconfigure(0, minsize=0)
        self.pojazd_pobranie_labelframe.columnconfigure(1, weight=2)
        self.pojazd_pobranie_labelframe.columnconfigure(2, weight=1)
        self.pojazd_pobranie_labelframe.columnconfigure(3, minsize=0)

        # Tablica rejestracyjna
        self.pp_tablica_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Numer TR:', background='yellow')
        self.pp_tablica_label.grid(column=1, row=0, sticky='E', pady=20, padx=10)

        self.pp_tablica_img = tk.PhotoImage(file='tablica.gif')
        self.pp_tablica_img_label = ttk.Label(self.pojazd_pobranie_labelframe, image=self.pp_tablica_img)
        self.pp_tablica_img_label.grid(column=2, row=0, sticky='W')

        self.pp_tr_entry_var = tk.StringVar()
        self.pp_tablica_entry = ttk.Entry(self.pojazd_pobranie_labelframe, state='disabled', width=12,
                                          justify='center', font='Arial 13 bold', textvariable=self.pp_tr_entry_var)
        self.pp_tablica_entry.grid(column=2, row=0, sticky='W', padx=14)
        self.pp_tr_entry_var.trace_add('write', self.to_uppercase)

        # Osoba pobierająca
        plik_json = open('osoby.json')
        obj = json.load(plik_json)
        self.pp_osoba_values = obj['pojazd']
        plik_json.close()

        self.pp_osoba_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Osoba pobierająca:', background='pink')
        self.pp_osoba_label.grid(column=1, row=2, sticky='E', pady=10, padx=10)

        self.pp_osoba_combobox = ttk.Combobox(self.pojazd_pobranie_labelframe, values=self.pp_osoba_values,
                                              state='disabled', width=25, font='Arial 13 bold')
        self.pp_osoba_combobox.grid(column=2, row=2, sticky='W')

        # Osoba prowadząca sprawę
        plik_json = open('osoby.json')
        obj = json.load(plik_json)
        self.pp_prow_values = obj['prowadzacy']
        plik_json.close()

        self.pp_prow_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Osoba prowadząca sprawę:',
                                       background='pink', font='Arial 13 bold')
        self.pp_prow_label.grid(column=1, row=3, sticky='E', pady=2, padx=10)

        self.pp_prow_combobox = ttk.Combobox(self.pojazd_pobranie_labelframe, values=self.pp_prow_values,
                                             state='disabled', width=25, font='Arial 13 bold')
        self.pp_prow_combobox.grid(column=2, row=3, sticky='W')

        # Inna data pobrania
        self.pp_data = tk.BooleanVar()
        self.pp_data_check = ttk.Checkbutton(self.pojazd_pobranie_labelframe,
                                             onvalue=True,
                                             offvalue=False,
                                             text='Inna data',
                                             variable=self.pp_data,
                                             command=self.pp_inna_data)
        self.pp_data_check.grid(column=1, row=4, sticky='E', pady=10, padx=10)

        self.pp_data_entry = tk.Entry(self.pojazd_pobranie_labelframe, font='Arial 13 bold')
        self.pp_data_entry.insert(0, 'RRRR-MM-DD')
        self.pp_data_entry.config(state='disabled')
        self.pp_data_entry.grid(column=2, row=4, sticky='W', padx=0)

        # Uwagi
        self.pp_uwagi_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Uwagi:', font="Helvetica 10")
        self.pp_uwagi_label.grid(column=1, row=5, sticky='E', pady=0, padx=10)

        self.pp_uwagi_entry = ttk.Entry(self.pojazd_pobranie_labelframe, state='disabled', width=25, font='Arial 11')
        self.pp_uwagi_entry.grid(column=2, row=5, sticky='W', padx=0)

        # Przycisk 'Zastosuj' POBRANIE
        self.pp_zastosuj_button = tk.Button(self.pojazd_pobranie_labelframe, text='Zastosuj', width=40,
                                            command=self.pojazd_zastosuj_pobranie)
        self.pp_zastosuj_button.grid(column=1, columnspan=2, row=6, pady=10)

        # Potwierdzenie zapisu
        self.pp_potwierdzenie_label = tk.Label(self.pojazd_pobranie_labelframe)
        self.pp_potwierdzenie_label.grid(column=0, columnspan=4, row=8)

        # VERTICAL SEPARATOR - POJAZD
        self.pojazd_ver_separator = ttk.Separator(self.pojazd, orient='vertical')
        self.pojazd_ver_separator.grid(column=2, row=0, ipady=130, pady=10)

        # ZWROT AKT POJAZDU --> pz
        self.pojazd_zwrot_labelframe = tk.LabelFrame(self.pojazd, text='Zwrot akt pojazdu')
        self.pojazd_zwrot_labelframe.grid(column=3, row=0, padx=30, sticky='NEWS', pady=10)

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

        self.pz_tr_entry_var = tk.StringVar()
        self.pz_tablica_entry = ttk.Entry(self.pojazd_zwrot_labelframe, state='disabled', width=12,
                                          justify='center', font='Arial 13 bold', textvariable=self.pz_tr_entry_var)
        self.pz_tablica_entry.grid(column=2, row=0, sticky='W', padx=14)
        self.pz_tr_entry_var.trace_add('write', self.to_uppercase)

        # Osoba zwracająca
        self.pz_osoba_label = ttk.Label(self.pojazd_zwrot_labelframe, text='Osoba zwracająca:', background='pink')
        self.pz_osoba_label.grid(column=1, row=1, sticky='E', pady=10, padx=10)

        self.pz_osoba_combobox = ttk.Combobox(self.pojazd_zwrot_labelframe, values=self.pp_osoba_values,
                                              state='disabled', font='Arial 13 bold')
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

        self.pz_data_entry = tk.Entry(self.pojazd_zwrot_labelframe, font='Arial 13 bold')
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
        self.pojazd_hor_separator.grid(column=1, columnspan=3, row=2, ipadx=self.window_width, pady=15)

        # SET TABLE HEIGHT BASED ON RESOLUTION
        self.notebook.update()
        note = self.notebook.winfo_reqheight()
        tab_poj = int((self.window_height - (140 + note)) / 30)

        # DATABASE VIEW
        self.pojazd_db_columns = ("id", "TR", "Data pobrania", "Pobierający", "Prowadzący sprawę",
                                  "Operator - pobranie", "Data zwrotu", "Zwracający", "Operator - zwrot", "Uwagi")
        self.pojazd_db_view = ttk.Treeview(self.pojazd, columns=self.pojazd_db_columns, show='headings', height=tab_poj)
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

        self.pojazd_db_scrollbar_x = ttk.Scrollbar(self.pojazd, orient=tk.HORIZONTAL, command=self.pojazd_db_view.xview)
        self.pojazd_db_view.configure(xscrollcommand=self.pojazd_db_scrollbar_x.set)
        self.pojazd_db_scrollbar_x.grid(column=1, columnspan=3, row=5, sticky='WE')

        # CLOSE BUTTON
        self.zamknij_button = ttk.Button(self.pojazd, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button.grid(column=2, row=6, sticky="WE", padx=10, pady=10)

        self.pokaz_wszystko = ttk.Button(self.pojazd, text='Pokaż wszystko', command=self.show_all)
        self.pokaz_wszystko.grid(column=3, row=6)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ KIEROWCA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.kierowca.columnconfigure(0, minsize=10)
        self.kierowca.columnconfigure(1, weight=1)
        self.kierowca.columnconfigure(2, minsize=1)
        self.kierowca.columnconfigure(3, weight=1)
        self.kierowca.columnconfigure(4, minsize=10)

        # POBRANIE AKT KIEROWCY --> kp
        self.kierowca_pobranie_labelframe = tk.LabelFrame(self.kierowca, text='Pobranie akt kierowcy')
        self.kierowca_pobranie_labelframe.grid(column=1, row=0, padx=10, sticky='NEWS', pady=10)

        self.kierowca_pobranie_labelframe.columnconfigure(0, minsize=10)
        self.kierowca_pobranie_labelframe.columnconfigure(1, weight=1)
        self.kierowca_pobranie_labelframe.columnconfigure(2, weight=1)
        self.kierowca_pobranie_labelframe.columnconfigure(3, minsize=10)

        self.kierowca_pobranie_left_frame = tk.Frame(self.kierowca_pobranie_labelframe)
        self.kierowca_pobranie_left_frame.grid(column=1, row=0)
        self.kierowca_pobranie_right_frame = tk.Frame(self.kierowca_pobranie_labelframe)
        self.kierowca_pobranie_right_frame.grid(column=2, row=0)

        # DATA URODZENIA — KIEROWCA (w przypadku braku PESEL)
        self.kp_data_ur_var = tk.BooleanVar()
        self.kp_data_ur_check = ttk.Checkbutton(self.kierowca_pobranie_right_frame,
                                                onvalue=True,
                                                offvalue=False,
                                                text='Data ur.',
                                                variable=self.kp_data_ur_var,
                                                command=self.kp_data_urodzenia)
        self.kp_data_ur_check.grid(column=0, row=0, sticky='E', pady=10, padx=13)

        self.kp_data_ur_entry = tk.Entry(self.kierowca_pobranie_right_frame, font='Arial 13 bold', width=14)
        self.kp_data_ur_entry.insert(0, 'RRRR-MM-DD')
        self.kp_data_ur_entry.config(state='disabled')
        self.kp_data_ur_entry.grid(column=1, row=0, sticky='W')

        # Nazwisko i imię — POBRANIE AKT
        self.kp_nazwisko_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Nazwisko:', background='yellow')
        self.kp_nazwisko_label.grid(column=0, row=0, sticky='E')

        self.kp_nazwisko_entry = tk.Entry(self.kierowca_pobranie_left_frame,
                                          state='disabled', width=17, font='Arial 13 bold')
        self.kp_nazwisko_entry.grid(column=1, row=0, sticky='W', pady=5)

        self.kp_imie_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Imię:', background='yellow')
        self.kp_imie_label.grid(column=0, row=1, sticky='E')

        self.kp_imie_entry = tk.Entry(self.kierowca_pobranie_left_frame,
                                      state='disabled', width=17, font='Arial 13 bold')
        self.kp_imie_entry.grid(column=1, row=1, sticky='W', pady=5)

        # PESEL - KIEROWCA POBRANIE AKT
        self.kp_pesel_label = ttk.Label(self.kierowca_pobranie_left_frame, text='PESEL:', background='yellow')
        self.kp_pesel_label.grid(column=0, row=2, sticky='E', pady=10)

        self.kp_pesel_string = tk.StringVar()
        self.kp_pesel_entry = tk.Entry(self.kierowca_pobranie_left_frame, width=15, state='disabled',
                                       font='Arial 13 bold', textvariable=self.kp_pesel_string)
        self.kp_pesel_entry.grid(column=1, row=2, sticky='W')
        self.kp_pesel_entry.bind('<FocusOut>', self.sprawdz_pesel_pobranie)

        # NR Karty Kierowcy — POBRANIE AKT
        self.kp_nr_kk_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Numer K/K:',
                                        background='yellow')
        self.kp_nr_kk_label.grid(column=0, row=3, sticky='E')

        self.kp_nr_kk_entry = tk.Entry(self.kierowca_pobranie_left_frame, width=12, font='Arial 13 bold')
        self.kp_nr_kk_entry.grid(column=1, row=3, sticky='W', pady=10)
        self.kp_nr_kk_entry.insert(0, 'B/U')
        self.kp_nr_kk_entry.config(state='disabled')

        # INNA DATA - KIEROWCA POBRANIE
        self.kp_data = tk.BooleanVar()
        self.kp_data_check = ttk.Checkbutton(self.kierowca_pobranie_right_frame,
                                             onvalue=True,
                                             offvalue=False,
                                             text='Inna data',
                                             variable=self.kp_data,
                                             command=self.kp_inna_data)
        self.kp_data_check.grid(column=0, row=2, sticky='E', pady=2, padx=5)

        self.kp_data_entry = tk.Entry(self.kierowca_pobranie_right_frame, font='Arial 13 bold', width=14)
        self.kp_data_entry.insert(0, 'RRRR-MM-DD')
        self.kp_data_entry.config(state='disabled')
        self.kp_data_entry.grid(column=1, row=2, sticky='W', pady=5)

        # UWAGI - KIEROWCA
        self.kp_uwagi_label = tk.Label(self.kierowca_pobranie_right_frame, text='Uwagi:')
        self.kp_uwagi_label.grid(column=0, row=4, sticky='E', pady=10, padx=5)

        self.kp_uwagi = tk.Text(self.kierowca_pobranie_right_frame, height=2, width=16,
                                state='disabled', background='gray90', font='Arial 11')
        self.kp_uwagi.grid(column=1, row=4, rowspan=2, sticky='W', pady=30)

        # Osoba Pobierająca
        plik_json = open('osoby.json')
        obj = json.load(plik_json)
        self.kp_osoba_values = obj['kierowca']
        plik_json.close()

        self.kp_osoba_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Osoba pobierająca:', background='pink')
        self.kp_osoba_label.grid(column=0, row=4, sticky='E', pady=10)

        self.kp_osoba_combobox = ttk.Combobox(self.kierowca_pobranie_left_frame, values=self.kp_osoba_values,
                                              state='disabled', font='Arial 13 bold', width=17)
        self.kp_osoba_combobox.grid(column=1, row=4, sticky='W')

        # Osoba prowadząca sprawę
        plik_json = open('osoby.json')
        obj = json.load(plik_json)
        self.kp_prow_values = obj['prowadzacy_kier']
        plik_json.close()

        self.kp_prow_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Osoba prowadząca sprawę:',
                                       background='pink')
        self.kp_prow_label.grid(column=0, row=5, sticky='E', pady=2, padx=0)

        self.kp_prow_combobox = ttk.Combobox(self.kierowca_pobranie_left_frame, values=self.kp_prow_values,
                                             state='disabled', width=17, font='Arial 13 bold')
        self.kp_prow_combobox.grid(column=1, row=5, sticky='W')

        # ŻĄDANIE AKT
        self.kp_zadanie_akt_var = tk.BooleanVar()
        self.kp_zadanie_akt = ttk.Checkbutton(self.kierowca_pobranie_right_frame,
                                              onvalue=True,
                                              offvalue=False,
                                              text='Żądanie akt',
                                              variable=self.kp_zadanie_akt_var)
        self.kp_zadanie_akt.grid(column=0, row=6, sticky='E', pady=2)
        self.kp_zadanie_akt.state(['!alternate'])

        # PRZYCISK ZASTOSUJ - KIEROWCA POBRANIE
        self.kp_zastosuj_button = tk.Button(self.kierowca_pobranie_labelframe, text='Zastosuj',
                                            width=40, command=self.kierowca_zastosuj_pobranie)
        self.kp_zastosuj_button.grid(column=1, columnspan=2, row=12, pady=10)

        # Potwierdzenie zapisu — Kierowca pobranie
        self.kp_potwierdzenie_label = tk.Label(self.kierowca_pobranie_labelframe)
        self.kp_potwierdzenie_label.grid(column=0, columnspan=4, row=14)

        # VERTICAL SEPARATOR - KIEROWCA
        self.kierowca_ver_separator = ttk.Separator(self.kierowca, orient='vertical')
        self.kierowca_ver_separator.grid(column=2, row=0, ipady=130, pady=10)

        # ZWROT AKT KIEROWCY --> kz
        self.kierowca_zwrot_labelframe = tk.LabelFrame(self.kierowca, text='Zwrot akt kierowcy')
        self.kierowca_zwrot_labelframe.grid(column=3, row=0, padx=20, sticky='NEWS', pady=10)

        self.kierowca_zwrot_labelframe.columnconfigure(0, minsize=20)
        self.kierowca_zwrot_labelframe.columnconfigure(1, weight=1)
        self.kierowca_zwrot_labelframe.columnconfigure(2, weight=1)
        self.kierowca_zwrot_labelframe.columnconfigure(3, minsize=20)

        # PESEL - ZWROT AKT
        self.kz_pesel_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Data ur. / PESEL:', background='yellow')
        self.kz_pesel_label.grid(column=1, row=0, sticky='E', pady=15)

        self.kz_pesel_string = tk.StringVar()
        self.kz_pesel_entry = tk.Entry(self.kierowca_zwrot_labelframe, width=15, state='disabled',
                                       font='Arial 14 bold', textvariable=self.kz_pesel_string)
        self.kz_pesel_entry.grid(column=2, row=0, sticky='W')
        self.kz_pesel_entry.bind('<FocusOut>', self.sprawdz_pesel_zwrot)
        self.kz_pesel_entry.bind('<FocusOut>', self.zwrot_podglad, add='+')

        # NR KK - ZWROT AKT
        self.kz_nr_kk_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Numer K/K:',
                                        background='yellow')
        self.kz_nr_kk_label.grid(column=1, row=2, sticky='E')

        self.kz_nr_kk_entry = tk.Entry(self.kierowca_zwrot_labelframe, width=12, font='Arial 14 bold')
        self.kz_nr_kk_entry.grid(column=2, row=2, sticky='W', pady=5)

        self.kz_nr_kk_entry.config(state='disabled')
        self.kz_nr_kk_entry.bind('<FocusOut>', self.zwrot_podglad)

        # Imię i Nazwisko osoby z teczki zwracanej.
        self.kz_dane = ttk.Label(self.kierowca_zwrot_labelframe, text="")
        self.kz_dane.grid(columnspan=2, column=1, row=4, pady=5)

        # Osoba zwracająca
        plik_json = open('osoby.json')
        obj = json.load(plik_json)
        self.kz_osoba_values = obj['kierowca']
        plik_json.close()

        self.kz_osoba_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Osoba zwracająca:', background='pink')
        self.kz_osoba_label.grid(column=1, row=8, sticky='E', pady=10)

        self.kz_osoba_combobox = ttk.Combobox(self.kierowca_zwrot_labelframe, values=self.kz_osoba_values,
                                              state='disabled', font='Arial 13 bold')
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
        self.kz_data_check.grid(column=1, row=10, sticky='E', pady=10, padx=10)

        self.kz_data_entry = tk.Entry(self.kierowca_zwrot_labelframe, font='Arial 13 bold')
        self.kz_data_entry.insert(0, 'RRRR-MM-DD')
        self.kz_data_entry.config(state='disabled')
        self.kz_data_entry.grid(column=2, row=10, sticky='W')

        # PRZYCISK ZASTOSUJ - KIEROWCA ZWROT
        self.kz_zastosuj_button = tk.Button(self.kierowca_zwrot_labelframe, text='Zastosuj',
                                            width=40, command=self.kierowca_zastosuj_zwrot)
        self.kz_zastosuj_button.grid(column=1, columnspan=2, row=12, pady=10)

        # Potwierdzenie zapisu — Kierowca pobranie
        self.kz_potwierdzenie_label = tk.Label(self.kierowca_zwrot_labelframe)
        self.kz_potwierdzenie_label.grid(column=0, columnspan=4, row=14)

        # KIEROWCA HORIZONTAL SEPARATOR
        self.kierowca_hor_separator = ttk.Separator(self.kierowca, orient='horizontal')
        self.kierowca_hor_separator.grid(column=1, columnspan=3, row=2, ipadx=self.window_width, pady=10)

        self.kierowca.update()
        note = self.kierowca.winfo_reqheight()
        tab_kier = int((self.window_height - (140 + note)) / 30)
        print(tab_kier, note)

        # KIEROWCA DATABASE VIEW
        self.kierowca_db_columns = ('id', 'PESEL', 'Nazwisko', 'Imię', 'Nr Karty Kierowcy', 'Data pobrania',
                                    'Pobierający', 'Osoba prowadząca', 'Operator - pobranie', 'Data zwrotu',
                                    'Zwracający', 'Operator - zwrot', 'uwagi')
        self.kierowca_db_view = ttk.Treeview(self.kierowca, columns=self.kierowca_db_columns,
                                             show='headings', height=tab_kier)

        for column in self.kierowca_db_columns:
            self.kierowca_db_view.heading(column, text=column, anchor='center')
            self.kierowca_db_view.column(column, width=150)
        self.kierowca_db_view.column("id", width=50)
        self.kierowca_db_view.column("PESEL", width=100)
        self.kierowca_db_view.column("Imię", width=100)

        self.kierowca_db_view.grid(column=1, columnspan=3, row=4, sticky='NEWS')

        # KIEROWCA SCROLLBAR
        self.kierowca_db_scrollbar = ttk.Scrollbar(self.kierowca,
                                                   orient=tk.VERTICAL,
                                                   command=self.kierowca_db_view.yview)
        self.kierowca_db_view.configure(yscrollcommand=self.kierowca_db_scrollbar.set)
        self.kierowca_db_scrollbar.grid(column=4, row=4, sticky='NS')

        self.kierowca_db_scrollbarx = ttk.Scrollbar(self.kierowca,
                                                    orient=tk.HORIZONTAL,
                                                    command=self.kierowca_db_view.xview)
        self.kierowca_db_view.configure(xscrollcommand=self.kierowca_db_scrollbarx.set)
        self.kierowca_db_scrollbarx.grid(column=1, columnspan=3, row=5, sticky='WE')

        # CLOSE BUTTON
        self.zamknij_button2 = ttk.Button(self.kierowca, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button2.grid(column=2, row=6, sticky="WE", padx=10, pady=0)

        self.pokaz_wszystko2 = ttk.Button(self.kierowca, text='Pokaż wszystko', command=self.show_all_kierowca)
        self.pokaz_wszystko2.grid(column=3, row=6)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ WYSZUKIWARKA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        self.wyszukiwanie.columnconfigure(0, weight=1)
        self.wyszukiwanie.columnconfigure(1, minsize=10)

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
        self.szukaj_tr_label.grid(column=0, row=0, pady=10, sticky='E')

        self.szukaj_tr_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=15)
        self.szukaj_tr_entry.grid(column=1, row=0, sticky='W')

        # Prowadzący sprawę
        self.szukaj_pojazd_prowadzacy_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                        text='     Prowadzący sprawę:', font='Arial 10')
        self.szukaj_pojazd_prowadzacy_label.grid(column=2, row=0)

        self.szukaj_pojazd_prowadzacy_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_prow_values)
        self.szukaj_pojazd_prowadzacy_entry.grid(column=3, row=0)

        # Osoba pobierająca
        self.szukaj_pojazd_osoba_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                            text='     Osoba pobierająca:', font='Arial 10')
        self.szukaj_pojazd_osoba_pobranie_label.grid(column=0, row=1)

        self.szukaj_pojazd_osoba_pobranie_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_osoba_values)
        self.szukaj_pojazd_osoba_pobranie_entry.grid(column=1, row=1)

        # Osoba zwracająca
        self.szukaj_pojazd_osoba_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                         text='     Osoba zwracająca:', font='Arial 10')
        self.szukaj_pojazd_osoba_zwrot_label.grid(column=0, row=2)

        self.szukaj_pojazd_osoba_zwrot_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_osoba_values)
        self.szukaj_pojazd_osoba_zwrot_entry.grid(column=1, row=2)

        # Operator pobranie
        self.szukaj_pojazd_operator_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                               text='     Operator pobranie:', font='Arial 10')
        self.szukaj_pojazd_operator_pobranie_label.grid(column=2, row=1)

        self.szukaj_pojazd_operator_pobranie_entry = ttk.Combobox(self.wyszukaj_pojazd_frame,
                                                                  values=self.operator_values)
        self.szukaj_pojazd_operator_pobranie_entry.grid(column=3, row=1)

        # Operator zwrot
        self.szukaj_pojazd_operator_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                            text='     Operator zwrot:', font='Arial 10')
        self.szukaj_pojazd_operator_zwrot_label.grid(column=2, row=2, sticky='E')

        self.szukaj_pojazd_operator_zwrot_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.operator_values)
        self.szukaj_pojazd_operator_zwrot_entry.grid(column=3, row=2)

        # Data pobrania od
        self.szukaj_pojazd_data_od_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                              text='   Data pobrania od:', font='Arial 10')
        self.szukaj_pojazd_data_od_pobranie_label.grid(column=4, row=1, pady=10)

        self.szukaj_pojazd_data_od_pobranie_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_od_pobranie_entry.grid(column=5, row=1)

        # Data pobrania do
        self.szukaj_pojazd_data_do_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                              text='   Data pobrania do:', font='Arial 10')
        self.szukaj_pojazd_data_do_pobranie_label.grid(column=6, row=1, pady=10)

        self.szukaj_pojazd_data_do_pobranie_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_do_pobranie_entry.grid(column=7, row=1)

        # Data zwrotu od
        self.szukaj_pojazd_data_od_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                           text='   Data zwrotu od:', font='Arial 10')
        self.szukaj_pojazd_data_od_zwrot_label.grid(column=4, row=2, pady=10, sticky='E')

        self.szukaj_pojazd_data_od_zwrot_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_od_zwrot_entry.grid(column=5, row=2)

        # Data zwrotu do
        self.szukaj_pojazd_data_do_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                           text='   Data zwrotu do:', font='Arial 10')
        self.szukaj_pojazd_data_do_zwrot_label.grid(column=6, row=2, pady=10, sticky='E')

        self.szukaj_pojazd_data_do_zwrot_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_do_zwrot_entry.grid(column=7, row=2)

        # @@@@ KIEROWCA @@@
        self.wyszukaj_kierowca_frame = tk.Frame(self.wyszukiwanie_options)
        self.wyszukaj_kierowca_frame.grid(column=0, row=1)

        # Szukaj KIEROWCA PESEL
        self.szukaj_kierowca_pesel_label = ttk.Label(self.wyszukaj_kierowca_frame, text='     PESEL ')
        self.szukaj_kierowca_pesel_label.grid(column=0, row=0, sticky='E')

        self.szukaj_kierowca_pesel_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=13)
        self.szukaj_kierowca_pesel_entry.grid(column=1, row=0)

        # Szukaj KIEROWCA NR KK
        self.szukaj_kierowca_nr_kk_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                     text='     numek KK ', font='Arial 10')
        self.szukaj_kierowca_nr_kk_label.grid(column=0, row=1, pady=10, sticky='E')

        self.szukaj_kierowca_nr_kk_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=13)
        self.szukaj_kierowca_nr_kk_entry.grid(column=1, row=1)

        # Szukaj KIEROWCA IMIĘ
        self.szukaj_kierowca_imie_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                             text='Imię ', font='Arial 10')
        self.szukaj_kierowca_imie_pobranie_label.grid(column=2, row=0, sticky='E')

        self.szukaj_kierowca_imie_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=15)
        self.szukaj_kierowca_imie_pobranie_entry.grid(column=3, row=0)

        # Szukaj KIEROWCA NAZWISKO
        self.szukaj_kierowca_nazwisko_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                 text='Nazwisko ', font='Arial 10')
        self.szukaj_kierowca_nazwisko_pobranie_label.grid(column=2, row=1, sticky='E')

        self.szukaj_kierowca_nazwisko_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=15)
        self.szukaj_kierowca_nazwisko_pobranie_entry.grid(column=3, row=1)

        # Szukaj KIEROWCA Osoba pobierająca.
        self.szukaj_kierowca_osoba_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                              text='     Osoba pobierająca ', font='Arial 10')
        self.szukaj_kierowca_osoba_pobranie_label.grid(column=4, row=0)

        self.szukaj_kierowca_osoba_pobranie_entry = ttk.Combobox(self.wyszukaj_kierowca_frame,
                                                                 values=self.kp_osoba_values)
        self.szukaj_kierowca_osoba_pobranie_entry.grid(column=5, row=0)

        # Szukaj KIEROWCA Osoba zwracająca.
        self.szukaj_kierowca_osoba_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                           text='     Osoba zwracająca ', font='Arial 10')
        self.szukaj_kierowca_osoba_zwrot_label.grid(column=4, row=1)

        self.szukaj_kierowca_osoba_zwrot_entry = ttk.Combobox(self.wyszukaj_kierowca_frame, values=self.kz_osoba_values)
        self.szukaj_kierowca_osoba_zwrot_entry.grid(column=5, row=1)

        # Szukaj KIEROWCA Operator pobranie.
        self.szukaj_kierowca_operator_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                 text='     Operator pobranie ', font='Arial 10')
        self.szukaj_kierowca_operator_pobranie_label.grid(column=6, row=0)

        self.szukaj_kierowca_operator_pobranie_entry = ttk.Combobox(self.wyszukaj_kierowca_frame,
                                                                    values=self.operator_values)
        self.szukaj_kierowca_operator_pobranie_entry.grid(column=7, row=0)

        # Szukaj KIEROWCA Operator zwrot.
        self.szukaj_kierowca_operator_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                              text='     Operator zwrot ', font='Arial 10')
        self.szukaj_kierowca_operator_zwrot_label.grid(column=6, row=1, sticky='E')

        self.szukaj_kierowca_operator_zwrot_entry = ttk.Combobox(self.wyszukaj_kierowca_frame,
                                                                 values=self.operator_values)
        self.szukaj_kierowca_operator_zwrot_entry.grid(column=7, row=1)

        # Szukaj KIEROWCA Data pobrania od.
        self.szukaj_kierowca_data_od_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                text='   Data pobrania od ', font='Arial 10')
        self.szukaj_kierowca_data_od_pobranie_label.grid(column=0, row=2, pady=6)

        self.szukaj_kierowca_data_od_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=13)
        self.szukaj_kierowca_data_od_pobranie_entry.grid(column=1, row=2)

        # Szukaj KIEROWCA Data pobrania do.
        self.szukaj_kierowca_data_do_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                text='   Data pobrania do ', font='Arial 10')
        self.szukaj_kierowca_data_do_pobranie_label.grid(column=2, row=2, pady=6)

        self.szukaj_kierowca_data_do_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=13)
        self.szukaj_kierowca_data_do_pobranie_entry.grid(column=3, row=2)

        # Szukaj KIEROWCA Data zwrotu od.
        self.szukaj_kierowca_data_od_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                             text='   Data zwrotu od ', font='Arial 10')
        self.szukaj_kierowca_data_od_zwrot_label.grid(column=0, row=3, pady=6, sticky='E')

        self.szukaj_kierowca_data_od_zwrot_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=13)
        self.szukaj_kierowca_data_od_zwrot_entry.grid(column=1, row=3)

        # Szukaj KIEROWCA Data zwrotu do.
        self.szukaj_kierowca_data_do_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                             text='   Data zwrotu do ', font='Arial 10')
        self.szukaj_kierowca_data_do_zwrot_label.grid(column=2, row=3, pady=6, sticky='E')

        self.szukaj_kierowca_data_do_zwrot_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=13)
        self.szukaj_kierowca_data_do_zwrot_entry.grid(column=3, row=3)

        # Szukaj KIEROWCA Prowadzący sprawę.
        self.szukaj_kierowca_prowadzacy_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                          text='   Prowadzący sprawę ', font='Arial 10')
        self.szukaj_kierowca_prowadzacy_label.grid(column=4, row=2, pady=6, sticky='E')

        self.szukaj_kierowca_prowadzacy_entry = ttk.Combobox(self.wyszukaj_kierowca_frame, values=self.kp_prow_values)
        self.szukaj_kierowca_prowadzacy_entry.grid(column=5, row=2)

        # Szukaj — PRZYCISKI
        self.szukaj_przyciski_frame = ttk.LabelFrame(self.wyszukiwanie)
        self.szukaj_przyciski_frame.grid(column=0, row=2, sticky='W', padx=15, ipady=5)

        self.szukaj_wyszukaj_button = tk.Button(self.szukaj_przyciski_frame, text='Wyszukaj',
                                                command=self.wyszukaj_kierowca_click)
        self.szukaj_wyszukaj_button.grid(column=0, row=0, padx=20, ipadx=10, pady=5)

        self.szukaj_edytuj_button = tk.Button(self.szukaj_przyciski_frame, text='Edytuj', command=self.edit_kierowca)
        self.szukaj_edytuj_button.grid(column=1, row=0, padx=20, ipadx=10, pady=5)

        self.szukaj_wyczysc_button = tk.Button(self.szukaj_przyciski_frame, text='Wyczyść', command=self.clear_entries)
        self.szukaj_wyczysc_button.grid(column=2, row=0, padx=20, ipadx=10, pady=5)

        self.tylko_niezwr_var = tk.BooleanVar()
        self.tylko_niezwr = ttk.Checkbutton(self.szukaj_przyciski_frame, text='Tylko niezwrócone',
                                            onvalue=True, offvalue=False, variable=self.tylko_niezwr_var,
                                            command=self.tylko_niezwrocone_kier)
        self.tylko_niezwr.grid(column=0, row=1, columnspan=3, padx=20, sticky='W')

        # Informacja o ilości wyszukanych rekordów
        self.informacja_label = tk.Label(self.wyszukiwanie, text=f"")
        self.informacja_label.grid(column=0, row=2, sticky='S')

        # Set table height
        self.wyszukiwanie.update()
        note = self.wyszukiwanie.winfo_reqheight()
        tab_wysz_poj = int((self.window_height - (140 + note)) / 30)

        # SZUKAJ DATABASE VIEW POJAZD
        self.szukaj_pojazd_db_columns = (
            "id", "TR", "Data pobrania", "Pobierający", "Prowadzący sprawę", "Operator - pobranie", "Data zwrotu",
            "Zwracający", "Operator - zwrot", "Uwagi")
        self.szukaj_pojazd_db_view = ttk.Treeview(self.wyszukiwanie,
                                                  columns=self.szukaj_pojazd_db_columns,
                                                  show='headings',
                                                  height=tab_wysz_poj)

        for column in self.szukaj_pojazd_db_columns:
            self.szukaj_pojazd_db_view.heading(column, text=column, anchor='center')
            self.szukaj_pojazd_db_view.column(column, width=180)

        self.szukaj_pojazd_db_view.column('id', width=70)
        self.szukaj_pojazd_db_view.column('TR', width=110)

        # self.szukaj_pojazd_db_view.grid(column=0, row=4, sticky='NEWS')

        self.szukaj_pojazd_db_view.tag_configure('returnedodd', background='DarkSeaGreen1')
        self.szukaj_pojazd_db_view.tag_configure('notreturnedodd', background='MistyRose1')
        self.szukaj_pojazd_db_view.tag_configure('returnedeven', background='PaleGreen')
        self.szukaj_pojazd_db_view.tag_configure('notreturnedeven', background='pink1')

        for col in self.szukaj_pojazd_db_columns:
            self.szukaj_pojazd_db_view.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(
                self.szukaj_pojazd_db_view, _col, False))

        # SCROLLBAR
        self.szukaj_pojazd_db_scrollbar = ttk.Scrollbar(self.wyszukiwanie,
                                                        orient=tk.VERTICAL,
                                                        command=self.szukaj_pojazd_db_view.yview)

        self.szukaj_pojazd_db_view.configure(yscrollcommand=self.szukaj_pojazd_db_scrollbar.set)
        # self.szukaj_pojazd_db_scrollbar.grid(column=1, row=4, sticky='NS')

        self.szukaj_pojazd_db_scrollbar_x = ttk.Scrollbar(self.wyszukiwanie,
                                                          orient=tk.HORIZONTAL,
                                                          command=self.szukaj_pojazd_db_view.xview)

        self.szukaj_pojazd_db_view.configure(xscrollcommand=self.szukaj_pojazd_db_scrollbar_x.set)
        # self.szukaj_pojazd_db_scrollbar_x.grid(column=0, row=5, sticky='WE')

        self.wyniki_label = tk.Label(self.wyszukiwanie, text="  Wyniki wyszukiwania")
        self.wyniki_label.grid(column=0, row=3, sticky='W')

        # Set table height
        self.wyszukiwanie.update()
        note = self.wyszukiwanie.winfo_reqheight()
        tab_wysz_kier = int((self.window_height - (140 + note)) / 30)

        # SZUKAJ DATABASE VIEW KIEROWCA
        self.szukaj_kierowca_db_columns = ('id', 'PESEL', 'Nazwisko', 'Imię', 'nr_kk', 'Data pobrania', 'Pobierający',
                                           'Prowadzący sprawę', 'Operator pobranie', 'Data zwrotu', 'Zwracający',
                                           'Operator zwrot', 'uwagi')
        self.szukaj_kierowca_db_view = ttk.Treeview(self.wyszukiwanie,
                                                    columns=self.szukaj_kierowca_db_columns,
                                                    show='headings',
                                                    height=tab_wysz_kier)

        for column in self.szukaj_kierowca_db_columns:
            self.szukaj_kierowca_db_view.heading(column, text=column, anchor='center')
            self.szukaj_kierowca_db_view.column(column, width=150)

        self.szukaj_kierowca_db_view.column('id', width=60)
        self.szukaj_kierowca_db_view.column('nr_kk', width=70)
        self.szukaj_kierowca_db_view.column('PESEL', width=100)
        self.szukaj_kierowca_db_view.column('Imię', width=120)

        self.szukaj_kierowca_db_view.grid(column=0, row=4, sticky='NEWS', padx=10)

        self.szukaj_kierowca_db_view.tag_configure('returnedodd', background='DarkSeaGreen1')
        self.szukaj_kierowca_db_view.tag_configure('notreturnedodd', background='MistyRose1')
        self.szukaj_kierowca_db_view.tag_configure('returnedeven', background='PaleGreen')
        self.szukaj_kierowca_db_view.tag_configure('notreturnedeven', background='pink1')

        for col in self.szukaj_kierowca_db_columns:
            self.szukaj_kierowca_db_view.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(
                self.szukaj_kierowca_db_view, _col, False))

        # SCROLLBAR
        self.szukaj_kierowca_db_scrollbar = ttk.Scrollbar(self.wyszukiwanie,
                                                          orient=tk.VERTICAL,
                                                          command=self.szukaj_kierowca_db_view.yview)
        self.szukaj_kierowca_db_view.configure(yscrollcommand=self.szukaj_kierowca_db_scrollbar.set)
        self.szukaj_kierowca_db_scrollbar.grid(column=1, row=4, sticky='NS')

        self.szukaj_kierowca_db_scrollbar_x = ttk.Scrollbar(self.wyszukiwanie,
                                                            orient=tk.HORIZONTAL,
                                                            command=self.szukaj_kierowca_db_view.xview)
        self.szukaj_kierowca_db_view.configure(xscrollcommand=self.szukaj_kierowca_db_scrollbar_x.set)
        self.szukaj_kierowca_db_scrollbar_x.grid(column=0, row=5, sticky='WE')

        # CLOSE BUTTON
        self.zamknij_button3 = ttk.Button(self.wyszukiwanie, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button3.grid(column=0, row=6, padx=10, pady=10)

        self.root.mainloop()

    def zwrot_podglad(self, event):
        pesel = self.kz_pesel_entry.get()
        kk = self.kz_nr_kk_entry.get()
        dane = []
        if pesel:
            with sqlite3.connect('archeo.db') as self.db:
                self.cursor = self.db.cursor()
            self.cursor.execute(f"SELECT nazwisko, imie FROM kierowcy WHERE pesel='{pesel}'")
            for element in self.cursor:
                dane = " ".join([f for f in element])
            self.kz_dane.config(text=dane)
            self.db.close()
        if kk:
            with sqlite3.connect('archeo.db') as self.db:
                self.cursor = self.db.cursor()
            self.cursor.execute(f"SELECT nazwisko, imie FROM kierowcy WHERE nr_kk='{kk}'")
            for element in self.cursor:
                dane = " ".join([f for f in element])
            self.kz_dane.config(text=dane)
            self.db.close()

    def pomniejsz(self):
        """ Modify size and configuration of rows, entries and labels"""
        # pojazd
        self.window_width = int(self.screen_width * 0.95)
        self.center_x = int(self.screen_width / 2 - self.window_width / 2)
        self.center_y = int(self.screen_height / 2 - self.window_height / 1.80)
        self.root.geometry(f'{self.window_width}x{self.window_height}+{self.center_x}+{self.center_y}')
        self.pojazd_hor_separator.grid(column=1, columnspan=3, row=2, ipadx=self.window_width, pady=10)
        self.pz_zastosuj_button.grid(column=1, columnspan=2, row=3, pady=10)
        self.pojazd_db_view.configure(height=8)
        # kierowca
        self.kierowca_hor_separator.grid(column=1, columnspan=3, row=2, ipadx=self.window_width, pady=10)
        self.kz_zastosuj_button.grid(column=1, columnspan=2, row=3, pady=10)
        self.kierowca_db_view.configure(height=7)
        self.kierowca_ver_separator.grid(column=2, row=0, ipady=130, pady=5)
        self.style.configure('TLabel', font='Helvetica 11 bold')
        self.kierowca_pobranie_labelframe.columnconfigure(0, minsize=0)
        self.kierowca_pobranie_labelframe.columnconfigure(3, minsize=0)
        self.kierowca_zwrot_labelframe.columnconfigure(0, minsize=20)
        self.kierowca_zwrot_labelframe.columnconfigure(3, minsize=20)
        self.kz_zastosuj_button.grid(column=1, columnspan=2, row=12)
        # wyszukiwarka
        self.szukaj_kierowca_db_view.configure(height=9)
        self.szukaj_pojazd_db_view.configure(height=11)
        self.szukaj_kierowca_prowadzacy_label.grid(column=0, row=2, pady=10, sticky='E')
        self.szukaj_kierowca_prowadzacy_entry.grid(column=1, row=2, sticky='W')
        self.szukaj_kierowca_data_od_pobranie_label.grid(column=2, row=2, sticky='E')
        self.szukaj_kierowca_data_od_pobranie_entry.grid(column=3, row=2, sticky='W')
        self.szukaj_kierowca_data_do_pobranie_label.grid(column=4, row=2, sticky='E')
        self.szukaj_kierowca_data_do_pobranie_entry.grid(column=5, row=2, sticky='W')
        self.szukaj_kierowca_data_od_zwrot_label.grid(column=8, row=0, sticky='E')
        self.szukaj_kierowca_data_od_zwrot_entry.grid(column=9, row=0, sticky='W')
        self.szukaj_kierowca_data_do_zwrot_label.grid(column=8, row=1, sticky='E')
        self.szukaj_kierowca_data_do_zwrot_entry.grid(column=9, row=1, sticky='W')

    def tylko_niezwrocone_pojazd(self):
        """ Add to 'pojazd' sql query condition to search only not returned documents."""
        if self.tylko_niezwr_var.get():
            self.szukaj_pojazd_data_do_zwrot_entry.delete(0, tk.END)
            self.szukaj_pojazd_data_do_zwrot_entry.config(state="disabled")
            self.szukaj_pojazd_data_od_zwrot_entry.delete(0, tk.END)
            self.szukaj_pojazd_data_od_zwrot_entry.config(state="disabled")
        else:
            self.szukaj_pojazd_data_do_zwrot_entry.config(state="normal")
            self.szukaj_pojazd_data_od_zwrot_entry.config(state="normal")

    def tylko_niezwrocone_kier(self):
        """ Add to 'kierowca' sql query condition to search only not returned documents."""
        if self.tylko_niezwr_var.get():
            self.szukaj_kierowca_data_do_zwrot_entry.delete(0, tk.END)
            self.szukaj_kierowca_data_do_zwrot_entry.config(state="disabled")
            self.szukaj_kierowca_data_od_zwrot_entry.delete(0, tk.END)
            self.szukaj_kierowca_data_od_zwrot_entry.config(state="disabled")
        else:
            self.szukaj_kierowca_data_do_zwrot_entry.config(state="normal")
            self.szukaj_kierowca_data_od_zwrot_entry.config(state="normal")

    def treeview_sort_column(self, tv, col, reverse):
        """Funkcja przypisana do kolumn w wyszukiwarce. Po kliknięciu nagłówka kolumny sortuje zawartość."""
        lista = [(tv.set(k, col), k) for k in tv.get_children('')]
        lista.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(lista):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda _col=col: self.treeview_sort_column(tv, _col, not reverse))

    def to_uppercase(self, *args):
        """Change inputting letter in 'tr entry' to uppercase"""
        self.pp_tr_entry_var.set(self.pp_tr_entry_var.get().upper())
        self.pz_tr_entry_var.set(self.pz_tr_entry_var.get().upper())

    def edit_pojazd(self):
        """Function to update data in DB. Binded to 'Edytuj' button in 'kierowca' searching engine.
        Function open a new window with fields filled with selected row data.
        When all search fields are empty show a Showinfo with short message. """
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
        When all search fields are empty show a Showinfo with short message. """
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
        prow = self.szukaj_pojazd_prowadzacy_entry.get().title()
        os_pob = self.szukaj_pojazd_osoba_pobranie_entry.get().title()
        os_zw = self.szukaj_pojazd_osoba_zwrot_entry.get().title()
        op_pob = self.szukaj_pojazd_operator_pobranie_entry.get().title()
        op_zw = self.szukaj_pojazd_operator_zwrot_entry.get().title()
        data_pob_od = self.szukaj_pojazd_data_od_pobranie_entry.get()
        data_pob_do = self.szukaj_pojazd_data_do_pobranie_entry.get()
        data_zw_od = self.szukaj_pojazd_data_od_zwrot_entry.get()
        data_zw_do = self.szukaj_pojazd_data_do_zwrot_entry.get()
        keys = ['tr', 'prowadzacy', 'osoba_pobranie', 'operator_pobranie',
                'osoba_zwrot', 'operator_zwrot', 'data_pobrania', 'data_zwrotu']
        values = [tr, prow, os_pob, op_pob, os_zw, op_zw]
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
            daty.append(f"data_zwrotu <= '{data_zw_do} 23:59'")
        if self.tylko_niezwr_var.get():
            daty.append("(data_zwrotu IS NULL OR data_zwrotu = '' OR data_zwrotu = 'None')")

        if daty:
            if not all(v == "" for v in warunki.values()):
                sql = sql[:-1] + " AND  "
                sql = sql[:-1] + " AND ".join(daty) + ";"
            else:
                sql = sql[:-1] + " AND ".join(daty) + ";"

        self.szukaj_pojazd_db_view.delete(*self.szukaj_pojazd_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        count = 1
        try:
            for n in self.cursor.execute(sql):
                n = list(n)
                for i, m in enumerate(n):
                    if m == None:
                        n[i] = ""
                if count % 2 == 0 and n[6] != "":
                    # self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('evenrow',))
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('returnedeven',))
                elif count % 2 == 0 and n[6] == "":
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('notreturnedeven',))
                elif count % 2 == 1 and n[6] != "":
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('returnedodd',))
                else:
                    # self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('oddrow',))
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('notreturnedodd',))
                count += 1
        except sqlite3.OperationalError:
            for n in self.cursor.execute("SELECT * FROM pojazdy"):
                n = list(n)
                for i, m in enumerate(n):
                    if m == None:
                        n[i] = ""
                if count % 2 == 0 and n[6] != "":
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('returnedeven',))
                elif count % 2 == 0 and n[6] == "":
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('notreturnedeven',))
                elif count % 2 == 1 and n[6] != "":
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('returnedodd',))
                else:
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('notreturnedodd',))
                count += 1

        self.informacja_label.grid_forget()
        suma_wyniki = len(self.szukaj_pojazd_db_view.get_children())
        self.informacja_label = tk.Label(self.wyszukiwanie, text=f"Liczba znalezionych wyników: {suma_wyniki}")
        self.informacja_label.grid(column=0, row=2, sticky='S')

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
        prow = self.szukaj_kierowca_prowadzacy_entry.get().title()
        keys = ['pesel', 'nr_kk', 'imie', 'nazwisko', 'operator_pobranie',
                'operator_zwrot', 'osoba_pobranie', 'osoba_zwrot', 'prowadzacy']
        values = [pesel, nr_kk, imie, nazwisko, op_pob, op_zw, os_pob, os_zw, prow]
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
            daty.append(f"data_zwrotu <= '{data_zw_do} 23:59'")
        if self.tylko_niezwr_var.get():
            daty.append("(data_zwrotu IS NULL OR data_zwrotu = '' OR data_zwrotu = 'None')")

        if daty:
            if not all(v == "" for v in warunki.values()):  # Jeśli są jakieś kryteria wyszukiwania i daty
                sql = sql[:-1] + " AND  "                   # to dodaje 'AND' pomiędzy.
                sql = sql[:-1] + " AND ".join(daty) + ";"
            else:
                sql = sql[:-1] + " AND ".join(daty) + ";"

        self.szukaj_kierowca_db_view.delete(*self.szukaj_kierowca_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        count = 1
        try:
            for n in self.cursor.execute(sql):
                n = list(n)
                for i, m in enumerate(n):
                    if m == None:
                        n[i] = ""
                if count % 2 == 0 and n[9] != "":
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('returnedeven',))
                elif count % 2 == 0 and n[9] == "":
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('notreturnedeven',))
                elif count % 2 == 1 and n[9] != "":
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('returnedodd',))
                else:
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('notreturnedodd',))
                count += 1
        except sqlite3.OperationalError:
            for n in self.cursor.execute("SELECT * FROM kierowcy"):
                n = list(n)
                for i, m in enumerate(n):
                    if m == None:
                        n[i] = ""
                if count % 2 == 0 and n[9] != "":
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('returnedeven',))
                elif count % 2 == 0 and n[9] == "":
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('notreturnedeven',))
                elif count % 2 == 1 and n[9] != "":
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('returnedodd',))
                else:
                    self.szukaj_kierowca_db_view.insert("", tk.END, values=n, tags=('notreturnedodd',))
                count += 1

        self.informacja_label.grid_forget()
        suma_wyniki = len(self.szukaj_kierowca_db_view.get_children())
        self.informacja_label = tk.Label(self.wyszukiwanie, text=f"Liczba znalezionych wyników: {suma_wyniki}")
        self.informacja_label.grid(column=0, row=2, sticky='S')

        self.db.close()

    def clear_entries(self):
        """Czyści wszystkie pola wyszukiwania"""
        for widget in self.wyszukaj_kierowca_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)
        for widget in self.wyszukaj_pojazd_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.delete(0, tk.END)

    def sql_select(self, tabela, **kwargs):
        """Generate SQL queries for a SELECT statement matching the kwargs passed."""
        sql = list()
        sql.append(f"SELECT * FROM {tabela} ")
        if kwargs:
            sql.append(f"WHERE " + " AND ".join(f"{k} LIKE '%{v}%'" for k, v in kwargs.items() if v != ''))
        sql.append(";")
        return "".join(sql)

    def wybierz_rejestr(self):
        """ Funkcja zmieniająca pola do wyszukiwania po wybraniu odpowiedniego rejestru
         i przypisująca odpowiednie funkcje do klawiszy 'szukaj' i 'edytuj' oraz pokazuje sumę wyników"""
        if self.selected_value.get():  # Selected POJAZD
            self.wyszukaj_kierowca_frame.grid_forget()  # forget kierowca search inputs
            self.szukaj_kierowca_db_view.grid_forget()  # forget kierowca results table
            self.wyszukaj_pojazd_frame.grid(column=0, row=0)  # set pojazd search inputs
            self.szukaj_pojazd_db_view.grid(column=0, row=4, sticky='NEWS', padx=10)  # set pojazd result table
            self.szukaj_wyszukaj_button.configure(command=self.wyszukaj_pojazd_click)  # set pojazd search button command
            self.szukaj_edytuj_button.configure(command=self.edit_pojazd)  # set pojazd edit button command
            # self.informacja_label.grid_forget()
            self.suma_wyniki = len(self.szukaj_pojazd_db_view.get_children())
            self.informacja_label.config(text=f"Liczba znalezionych wyników: {self.suma_wyniki}")
            self.informacja_label.grid(column=0, row=2, sticky='S')
            self.tylko_niezwr.config(command=self.tylko_niezwrocone_pojazd)
            self.tylko_niezwr_var.set(False)
            self.tylko_niezwrocone_pojazd()
            self.szukaj_kierowca_db_scrollbar_x.grid_forget()
            self.szukaj_kierowca_db_scrollbar.grid_forget()
            self.szukaj_pojazd_db_scrollbar.grid(column=1, row=4, sticky='NS')
            self.szukaj_pojazd_db_scrollbar_x.grid(column=0, row=5, sticky='WE')

        else:  # Selected KIEROWCA
            self.wyszukaj_pojazd_frame.grid_forget()  # forget pojazd search inputs
            self.szukaj_pojazd_db_view.grid_forget()  # forget pojazd results table
            self.wyszukaj_kierowca_frame.grid(column=0, row=0)  # set kierowca search inputs
            self.szukaj_kierowca_db_view.grid(column=0, row=4, sticky='NEWS', padx=10)  # set kierowca res tab
            self.szukaj_wyszukaj_button.configure(command=self.wyszukaj_kierowca_click)  # set search button command
            self.szukaj_edytuj_button.configure(command=self.edit_kierowca)  # set kierowca edit button command
            # self.informacja_label.grid_forget()
            self.suma_wyniki = len(self.szukaj_kierowca_db_view.get_children())
            self.informacja_label.config(text=f"Liczba znalezionych wyników: {self.suma_wyniki}")
            self.informacja_label.grid(column=0, row=2, sticky='S')
            self.tylko_niezwr.config(command=self.tylko_niezwrocone_kier)
            self.tylko_niezwr_var.set(False)
            self.tylko_niezwrocone_kier()
            self.szukaj_pojazd_db_scrollbar_x.grid_forget()
            self.szukaj_pojazd_db_scrollbar.grid_forget()
            self.szukaj_kierowca_db_scrollbar.grid(column=1, row=4, sticky='NS')
            self.szukaj_kierowca_db_scrollbar_x.grid(column=0, row=5, sticky='WE')

    def kp_data_urodzenia(self):
        """ Funkcja aktywująca pole daty urodzenia po zaznaczeniu checkbutton i ustawiająca tam focus"""
        if self.kp_data_ur_var:
            self.kp_pesel_entry.config(state='disabled')
            self.kp_data_ur_entry.config(state='normal')
            self.kp_data_ur_entry.delete(0, "end")
            self.kp_data_ur_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem.
        if not self.kp_data_ur_var.get():
            self.kp_data_ur_entry.insert(0, "RRRR-MM-DD")
            self.kp_data_ur_entry.config(state="disabled")
            self.kp_pesel_entry.config(state='normal')
            self.kp_pesel_entry.focus_set()

    def sprawdz_pesel_pobranie(self, event):
        """ Funkcja zmieniająca kolor tła PESEL-u na zielony, jeśli ma 11 znaków i różowy w pozostałych przypadkach."""
        if len(self.kp_pesel_string.get()) == 11:
            self.kp_pesel_entry.configure(background='light green')
        else:
            self.kp_pesel_entry.configure(background='pink')

    def sprawdz_pesel_zwrot(self, event):
        """ Funkcja zmieniająca kolor tła PESEL-u na zielony, jeśli ma 11 znaków i różowy w pozostałych przypadkach."""
        if len(self.kz_pesel_string.get()) == 11:
            self.kz_pesel_entry.configure(background='light green')
        else:
            self.kz_pesel_entry.configure(background='pink')

    def show_all(self):
        """ Funkcja do przycisku "Pokaż wszystko" w zakładce 'pojazd',
            żeby wyświetlić wszystkie dane z tabeli pojazdów."""
        self.pojazd_db_view.delete(*self.pojazd_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        for n in self.cursor.execute(""" SELECT * FROM pojazdy """):
            self.pojazd_db_view.insert("", tk.END, values=n)
        self.db.close()

    def show_all_kierowca(self):
        """ Funkcja do przycisku "Pokaż wszystko" w zakładce 'kierowca',
            żeby wyświetlić wszystkie dane z tabeli kierowca."""
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
        self.pp_prow_combobox.config(state='normal')
        self.pp_uwagi_entry.config(state='normal')
        self.pz_tablica_entry.config(state='normal')
        self.pz_osoba_combobox.config(state='normal')
        self.kp_pesel_entry.config(state='normal')
        self.kp_imie_entry.config(state='normal')
        self.kp_nazwisko_entry.config(state='normal')
        self.kp_nr_kk_entry.config(state='normal')
        self.kp_osoba_combobox.config(state='normal')
        self.kp_prow_combobox.config(state='normal')
        self.pp_uwagi_entry.config(state='normal')
        self.kp_uwagi.config(state='normal', background='white')
        self.kz_pesel_entry.config(state='normal')
        self.kz_osoba_combobox.config(state='normal')
        self.kz_nr_kk_entry.config(state='normal')

    def pp_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.pp_data.get():
            self.pp_data_entry.config(state='normal')
            self.pp_data_entry.delete(0, "end")
            self.pp_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem.
        if not self.pp_data.get():
            self.pp_data_entry.delete(0, "end")
            self.pp_data_entry.insert(0, "RRRR-MM-DD")
            self.pp_data_entry.config(state="disabled")

    def pz_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.pz_data.get():
            self.pz_data_entry.config(state='normal')
            self.pz_data_entry.delete(0, "end")
            self.pz_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem.
        if not self.pz_data.get():
            self.pz_data_entry.delete(0, "end")
            self.pz_data_entry.insert(0, "RRRR-MM-DD")
            self.pz_data_entry.config(state="disabled")

    def kp_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.kp_data.get():
            self.kp_data_entry.config(state='normal')
            self.kp_data_entry.delete(0, "end")
            self.kp_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem.
        if not self.kp_data.get():
            self.kp_data_entry.delete(0, "end")
            self.kp_data_entry.insert(0, "RRRR-MM-DD")
            self.kp_data_entry.config(state="disabled")

    def kz_inna_data(self):
        # Jeśli zaznaczy się checkbox, uaktywni się pole na date i przeniesie tam 'focus'
        if self.kz_data.get():
            self.kz_data_entry.config(state='normal')
            self.kz_data_entry.delete(0, "end")
            self.kz_data_entry.focus_set()
        # Po odznaczeniu zablokuje pole daty i wypełni prawidłowym formatem.
        if not self.kz_data.get():
            self.kz_data_entry.delete(0, "end")
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
        # Funkcja sprawdza, czy w bazie istnieje już wpis z podanymi danymi bez daty zwrotu.
        wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE tr = "{tr}" AND 
                                                (data_zwrotu IS NULL OR data_zwrotu = "None" OR data_zwrotu = ""); """
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False

    def format_inna_data(self, data):
        # Funkcja sprawdzająca, czy podana data ma prawidłowy format.
        format_daty = re.compile(r"^[1-2][019]\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[1-2]\d|3[0-1])$")
        if format_daty.search(data):
            return True
        else:
            return False

    def insert_pobranie_to_db(self, tr, data, osoba, prowadzacy, operator, uwagi):
        return f""" INSERT INTO pojazdy (tr, data_pobrania, osoba_pobranie, prowadzacy, operator_pobranie, uwagi) 
                                VALUES("{tr}", "{data}", "{osoba}", "{prowadzacy}", "{operator}", "{uwagi}"); """

    def clear_tr(self, *args):
        """Czyści okienka tr, pesel, imie, nazwisko i nr kk po zapisaniu wpisu."""
        for arg in args:
            arg.delete(0, "end")
            if arg == self.kp_nr_kk_entry:
                arg.insert(0, 'B/U')

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
                self.pojazd_db_view.insert("", 0, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.pp_potwierdzenie_label.configure(
                image=img,
                text=f"   Prawidłowo zapisano pobranie teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.pp_potwierdzenie_label.image = img
            self.clear_tr(self.pp_tablica_entry)
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
        prowadzacy = self.pp_prow_combobox.get().title()
        uwagi = self.pp_uwagi_entry.get()
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

        if teczka == "" or osoba == "" or prowadzacy == "":
            # Jeśli nie wpisze się TR lub pobierającego wyskoczy błąd.
            return showerror("Błąd", "Pola  'Numer TR', 'Pobierający akta' i 'Osoba prowadząca sprawę' są obowiązkowe!")

        elif self.check_tr(teczka):
            # Jeśli nr TR jest poprawny — wstaw dane do bazy.
            self.cursor.execute(self.insert_pobranie_to_db(teczka, now, osoba, prowadzacy, operator, uwagi))
            self.db.commit()

        elif not self.check_tr(teczka):
            # Jeśli nr TR jest błędny pokaż zapytanie
            poprawna_tr = askyesno("Błąd",
                                   f"Numer TR powinien składać się z wyróżnika powiatu, ODSTĘPU i pojemności.\n",
                                   detail=f"Czy '{teczka}' to na pewno poprawny numer rejestracyjny?")
            if poprawna_tr:
                # Po zatwierdzeniu wprowadzi dane do bazy
                self.cursor.execute(self.insert_pobranie_to_db(teczka, now, osoba, prowadzacy, operator, uwagi))
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
                self.pojazd_db_view.insert("", 0, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.pz_potwierdzenie_label.configure(
                image=img,
                text=f"Prawidłowo odnotowano zwrot teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.pz_potwierdzenie_label.image = img
            self.clear_tr(self.pz_tablica_entry)
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

        self.cursor.execute(f""" SELECT * FROM pojazdy WHERE 
                            (data_zwrotu IS NULL OR data_zwrotu = "None" OR data_zwrotu = "") AND tr = "{teczka}"; """)
        if len(self.cursor.fetchall()) == 0:
            showerror("Błąd", f"Nie znaleziono niezwróconej teczki o nr '{teczka}'.")
        else:
            self.cursor.execute(f""" UPDATE pojazdy 
                    SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", operator_zwrot = "{operator}" 
                    WHERE tr = "{teczka}" AND (data_zwrotu IS NULL OR data_zwrotu = "" OR data_zwrotu = "None"); """)
            self.db.commit()

        self.pojazd_potwierdzenie_zwrotu(teczka, now, osoba, operator)
        self.db.close()

    def kp_czy_dubel(self, pesel):
        # Funkcja sprawdza, czy w bazie istnieje już wpis z podanymi danymi bez daty zwrotu.
        keys = ['pesel']
        values = [pesel]
        warunki = {k: v for k, v in zip(keys, values)}
        sql = self.kierowca_select_query(**warunki)
        sql = sql[:-1] + " AND (data_zwrotu IS NULL OR data_zwrotu = '' OR data_zwrotu = 'None');"
        wyszukanie_wpisu = sql
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False

    def check_pesel(self, pesel):
        # Funkcja sprawdzająca, czy nr PESEL składa się z cyfr i ma 11 znaków.
        return pesel.isdigit() and len(pesel) == 11

    def insert_kierowca_pobranie_to_db(self, pesel, imie, nazwisko, nr_kk, data, osoba, prowadzacy, operator, uwagi):
        return f'''INSERT INTO 
                            kierowcy (pesel, nazwisko, imie, nr_kk, data_pobrania, 
                                        osoba_pobranie, prowadzacy, operator_pobranie, uwagi) 
                            VALUES("{pesel}", "{nazwisko}", "{imie}", "{nr_kk}", "{data}", 
                                    "{osoba}", "{prowadzacy}", "{operator}", "{uwagi}");'''

    def kierowca_select_query(self, **kwargs):
        sql = list()
        sql.append("SELECT * FROM kierowcy ")
        if kwargs:
            sql.append(f"WHERE " + " AND ".join(f"{k} = '{v}'" for k, v in kwargs.items() if v != ''))
        sql.append(";")
        return "".join(sql)

    def kp_potwierdzenie_zapisu(self, pesel, imie, nazwisko, data, pobierajacy, operator):
        # Funkcja wyszukuje czy w tabeli kierowcy jest zapisany podany rekord,
        # jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych,
        # jeśli nie to obrazek błędu i tekst o braku zapisu
        keys = ['pesel', 'imie', 'nazwisko', 'data_pobrania', 'osoba_pobranie', 'operator_pobranie']
        values = [pesel, imie, nazwisko, data, pobierajacy, operator]
        warunki = {k: v for k, v in zip(keys, values)}
        sql = self.kierowca_select_query(**warunki)
        sql1 = sql[:-1] + " AND (data_zwrotu IS NULL OR data_zwrotu = '');"
        wyszukanie_wpisu = sql1
        if self.kp_zadanie_akt_var.get():
            wyszukanie_wpisu = sql[:-1] + " AND data_zwrotu = 'Żądanie akt';"
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) > 0:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.kierowca_db_view.insert("", 0, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.kp_potwierdzenie_label.configure(
                image=img,
                text=f"   Prawidłowo zapisano pobranie teczki osoby o "
                     f"nr PESEL: '{pesel}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.kp_potwierdzenie_label.image = img
            self.clear_tr(self.kp_pesel_entry, self.kp_imie_entry, self.kp_nazwisko_entry, self.kp_nr_kk_entry)
            self.kp_zadanie_akt_var.set(False)
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
        prow = self.kp_prow_combobox.get().title()
        operator = self.operator_combobox.get().title()
        uwagi = self.kp_uwagi.get(1.0, tk.END)
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
            # Jeśli nie wpisze się PESEL-u lub pobierającego, lum imienia lub nazwiska wyskoczy błąd.
            return showinfo("Błąd", "Pola 'PESEL', 'Imię', 'Nazwisko' i 'Osoba pobierająca' są obowiązkowe!")

        elif self.kp_czy_dubel(pesel):
            return showwarning("Warning", f"Teczka osoby {imie} {nazwisko} o nr PESEL: '{pesel}' "
                                          f"została już pobrana i nie odnotowano jej zwrotu.")

        elif self.check_pesel(pesel):
            # Jeśli nr PESEL jest poprawny — wstaw dane do bazy
            self.cursor.execute(
                self.insert_kierowca_pobranie_to_db(pesel, imie, nazwisko, nr_kk, now, osoba, prow, operator, uwagi)
            )
            self.db.commit()

        elif not self.check_pesel(pesel):
            # Jeśli nr PESEL jest błędny, pokaż zapytanie.
            poprawny_pesel = askyesno("Błąd",
                                      f"Numer PESEL powinien składać się z 11 cyfr.\n"
                                      f"Czy nr PESEL: '{pesel}' jest prawidłowy?")
            if poprawny_pesel:
                # Po zatwierdzeniu wprowadzi dane do bazy.
                self.cursor.execute(
                    self.insert_kierowca_pobranie_to_db(pesel, imie, nazwisko, nr_kk, now, osoba, prow, operator,
                                                        uwagi))
                self.db.commit()

        if self.kp_zadanie_akt_var.get():
            self.cursor.execute(
                f'UPDATE kierowcy SET data_zwrotu = "Żądanie akt" WHERE pesel = "{pesel}" AND data_pobrania = "{now}";')
            self.db.commit()

        self.kp_potwierdzenie_zapisu(pesel, imie, nazwisko, now, osoba, operator)

        self.db.close()

    def kierowca_potwierdzenie_zwrotu(self, pesel, nr_kk, data, pobierajacy, operator):
        # Funkcja wyszukuje czy podana teczka występuje z podaną datą zwrotu.
        # Jeśli tak to wyświetla go w podglądzie i wyświetla tekst potwierdzający zapisanie danych.
        text = ""
        if pesel and nr_kk:
            text = f"PESEL: {pesel} i nr KK: {nr_kk}"
        elif pesel:
            text = f"PESEL: {pesel}"
        elif nr_kk:
            text = f"KK: {nr_kk}"
        wyszukanie_wpisu = f""" SELECT * FROM kierowcy WHERE (pesel = "{pesel}" OR nr_kk = "{nr_kk}")
                                                        AND data_zwrotu >= "{data}" 
                                                        AND osoba_zwrot = "{pobierajacy}" 
                                                        AND operator_zwrot = "{operator}"; """
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) >= 1:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.kierowca_db_view.insert("", 0, values=n)
            img = tk.PhotoImage(file="green_check.png")
            self.kz_potwierdzenie_label.configure(
                image=img,
                text=f"Prawidłowo odnotowano zwrot teczki osoby o nr {text} przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.kz_potwierdzenie_label.image = img
            self.clear_tr(self.kz_pesel_entry, self.kz_nr_kk_entry)
            self.kz_dane.config(text="")
        else:
            wrong = tk.PhotoImage(file='wrong.jpg')
            self.kz_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki osoby o nr {text}.",
                compound="left", font="Helvetica 8"
            )
            self.kz_potwierdzenie_label.image = wrong

    def kierowca_zastosuj_zwrot(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        pesel = self.kz_pesel_string.get()
        nr_kk = self.kz_nr_kk_entry.get()
        osoba = self.kz_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        # Jeśli zaznaczona 'Inna data' sprawdź format, jeśli jest dobry ustaw jako 'now' jeśli nie 'showerror'.
        if self.kz_data.get():
            if self.format_inna_data(self.kz_data_entry.get()):
                now = self.kz_data_entry.get() + ' 12:00'
            else:
                return showerror("Błąd", "Sprawdź czy podana data jest prawidłowa. "
                                         "Pamiętaj, aby wpisać ją w formacie rrrr-mm-dd.")

        if pesel == "":
            if nr_kk == "":
                # Jeśli nie wpisze się PESEL-u lub nr 'KK', wyskoczy błąd.
                return showerror("Błąd", "Pole 'PESEL' lub 'nr KK' jest obowiązkowe!. "
                                         "W przypadku braku nr PESEL podaj datę urodzenia.")
        if osoba == "":
            return showerror("Błąd", "Pole 'Osoba zwracająca' jest obowiązkowe!")

        keys = ['pesel', 'nr_kk']
        values = [pesel, nr_kk]
        warunki = {k: v for k, v in zip(keys, values)}
        sql = self.kierowca_select_query(**warunki)
        sql = sql[:-1] + " AND (data_zwrotu IS NULL OR data_zwrotu = '' OR data_zwrotu = 'None');"
        db_id = f'{sql[:7]}id{sql[8:-1]}'

        self.cursor.execute(sql)
        if len(self.cursor.fetchall()) == 0:
            # Jeśli nie znajdzie wpisu z podanym nr PESEL i 'KK' wyszuka wpis z podanym PESEL i nr 'KK' = 'B/U'.
            if pesel and nr_kk:
                bez_kk = self.kierowca_select_query(**{'pesel': pesel, 'nr_kk': 'B/U'})[:-1] + \
                         " AND (data_zwrotu IS NULL OR data_zwrotu = '' OR data_zwrotu = 'None');"
                self.cursor.execute(bez_kk)
                # Zaktualizuje wpis o dane zwrotu i nr 'KK' podany przez operatora.
                if len(self.cursor.fetchall()) == 1:
                    self.cursor.execute(f""" UPDATE kierowcy 
                    SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", operator_zwrot = "{operator}", nr_kk = "{nr_kk}"
                    WHERE id = ({bez_kk[:7]}id{bez_kk[8:-1]}); """)
                    self.db.commit()
                else:
                    showinfo("Informacja",
                             f"Nie znaleziono niezwróconej teczki osoby o nr PESEL: '{pesel}' i nr kk {nr_kk}.")
            elif pesel:
                showinfo("Informacja", f"Nie znaleziono niezwróconej teczki osoby o nr PESEL: '{pesel}'.")
            else:
                showinfo("Informacja", f"Nie znaleziono niezwróconej teczki osoby o nr kk: '{nr_kk}'.")
        else:
            # Jeśli podany tylko PESEL lub nr 'KK' zaktualizuje tę pozycję o zwrot.
            self.cursor.execute(f""" UPDATE kierowcy 
            SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", operator_zwrot = "{operator}" 
            WHERE id = ({db_id}); """)
            self.db.commit()

        self.kierowca_potwierdzenie_zwrotu(pesel, nr_kk, now, osoba, operator)
        self.db.close()

    def operator_edit_window(self):
        """ Okno edycji operatorów """
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
        """ Remove elements from list of persons
            'Opcje' -> 'Edytuj osoby - Pojazd' -> 'Usuń'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        plik.close()
        lista = osoby['operator']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'operator'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usunięcie z listy osoby zaznaczonej w widoku
            nowa_lista = {'operator': lista}  # Przypisanie do zmiennej nowej wartości klucza 'operator'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, żeby wyzerować zawartość
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.operator_values = osoby['operator']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.operator_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.operator_combobox.config(values=self.operator_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_operator(self):
        """ Add elements to the list of operators
            'Opcje' -> 'Edytuj osoby - Pojazd' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        lista = osoby['operator']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'operator'

        try:
            oper = self.dodaj_entry.get()
            lista.append(oper)  # Dodanie do listy osoby wpisanej przez użytkownika
            nowa_lista = {'operator': lista}  # Przypisanie do zmiennej nowej wartości klucza 'operator'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisało wartość, a nie dodało nową na koniec.
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.operator_values = osoby['operator']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.operator_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.operator_combobox.config(values=self.operator_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij wszystkie okna i spróbuj ponownie')

    def osoba_pojazd_edit_window(self):
        """ Okno edycji osób pobierający/zwracających teczki pojazdów"""
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
        """ Remove elements from list of persons
            'Opcje' -> 'Edytuj osoby - Pojazd' -> 'Usuń'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        plik.close()
        lista = osoby['pojazd']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'pojazd'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usunięcie z listy osoby zaznaczonej w widoku
            nowa_lista = {'pojazd': lista}  # Przypisanie do zmiennej nowej wartości klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, żeby wyzerować zawartość
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.pp_osoba_values = osoby['pojazd']
            self.pz_osoba_values = osoby['pojazd']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_osoba_combobox.config(values=self.pp_osoba_values)
            self.pz_osoba_combobox.config(values=self.pz_osoba_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_pojazd_osoba(self):
        """ Adding elements to the list of operators
            'Opcje' -> 'Edytuj osoby - Pojazd' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        lista = osoby['pojazd']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'pojazd'
        try:
            oper = self.dodaj_entry.get()

            lista.append(oper)  # Dodanie do listy osoby wpisanej przez użytkownika
            nowa_lista = {'pojazd': lista}  # Przypisanie do zmiennej nowej wartości klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisało wartość, a nie dodało nową na koniec.
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.pp_osoba_values = osoby['pojazd']
            self.pz_osoba_values = osoby['pojazd']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_osoba_combobox.config(values=self.pp_osoba_values)
            self.pz_osoba_combobox.config(values=self.pz_osoba_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij wszystkie okna i spróbuj ponownie')

    def osoba_kierowca_edit_window(self):
        """ Okno edycji osób pobierający/zwracających teczki kierowców"""
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
        """ Remove elements from list of persons
            'Opcje' -> 'Edytuj osoby - Kierowca' -> 'Usuń'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        plik.close()
        lista = osoby['kierowca']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'kierowca'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usunięcie z listy osoby zaznaczonej w widoku
            nowa_lista = {'kierowca': lista}  # Przypisanie do zmiennej nowej wartości klucza 'kierowca'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, żeby wyzerować zawartość
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.kp_osoba_values = osoby['kierowca']
            self.kz_osoba_values = osoby['kierowca']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_osoba_combobox.config(values=self.kp_osoba_values)
            self.kz_osoba_combobox.config(values=self.kz_osoba_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_kierowca_osoba(self):
        """ Function to adding elements to the list of operators
            'Opcje' -> 'Edytuj osoby - Kierowca' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        lista = osoby['kierowca']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'pojazd'
        try:
            oper = self.dodaj_entry.get()

            lista.append(oper)  # Dodanie do listy osoby wpisanej przez użytkownika
            nowa_lista = {'kierowca': lista}  # Przypisanie do zmiennej nowej wartości klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisało wartość, a nie dodało nową na koniec
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.kp_osoba_values = osoby['kierowca']
            self.kz_osoba_values = osoby['kierowca']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_osoba_combobox.config(values=self.kp_osoba_values)
            self.kz_osoba_combobox.config(values=self.kz_osoba_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij wszystkie okna i spróbuj ponownie')

    def prowadzacy_kierowca_edit_window(self):
        """ Okno edycji osób prowadzących sprawy kierowców"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja osób prowadzących sprawę kierowców")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Prowadzący', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Prowadzący', text='Prowadzący', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usuń', command=self.delete_kierowca_prowadzacy)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj osobę")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imię i nazwisko')
        self.dodaj_label.grid(column=0, row=0, pady=10, padx=10)

        self.dodaj_entry = ttk.Entry(self.dodaj_frame, width=25)
        self.dodaj_entry.grid(column=1, row=0, padx=10)

        self.dodaj_button = ttk.Button(self.dodaj_frame, text='Dodaj', command=self.add_kierowca_prowadzacy)
        self.dodaj_button.grid(column=0, columnspan=2, row=1, pady=10)

        self.zamknij_button4 = ttk.Button(self.window, text='Zamknij', command=lambda: self.window.destroy())
        self.zamknij_button4.grid(column=0, row=4, pady=20)

        for name in self.kp_prow_values:
            self.lista_operatorow.insert("", tk.END, values=[name])

    def delete_kierowca_prowadzacy(self):
        """ Function to removing elements from list of persons
            'Opcje' -> 'Edytuj prowadzących - Kierowca' -> 'Usuń'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        plik.close()
        lista = osoby['prowadzacy_kier']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'prowadzacy_kier'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usunięcie z listy osoby zaznaczonej w widoku
            nowa_lista = {'prowadzacy_kier': lista}  # Przypisanie do zmiennej nowej wartości klucza 'kierowca'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, żeby wyzerować zawartość
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.kp_prow_values = osoby['prowadzacy_kier']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_prow_combobox.config(values=self.kp_prow_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_kierowca_prowadzacy(self):
        """ Function to adding elements to the list of operators
            'Opcje' -> 'Edytuj prowadzących - Kierowca' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        lista = osoby['prowadzacy_kier']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'prowadzacy_kier'
        try:
            oper = self.dodaj_entry.get()
            lista.append(oper)  # Dodanie do listy osoby wpisanej przez użytkownika
            nowa_lista = {'prowadzacy_kier': lista}  # Przypisanie do zmiennej nowej wartości klucza 'prowadzacy_kier'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisało wartość, a nie dodało nową na koniec
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.kp_prow_values = osoby['prowadzacy_kier']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_prow_combobox.config(values=self.kp_prow_values)
            self.szukaj_kierowca_prowadzacy_entry.config(values=self.kp_prow_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij wszystkie okna i spróbuj ponownie')

    def prowadzacy_pojazd_edit_window(self):
        """ Okno edycji osób prowadzących sprawy pojazdów"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja osób prowadzących sprawę pojazdów")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Prowadzący', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Prowadzący', text='Prowadzący', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usuń', command=self.delete_pojazd_prowadzacy)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj osobę")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imię i nazwisko')
        self.dodaj_label.grid(column=0, row=0, pady=10, padx=10)

        self.dodaj_entry = ttk.Entry(self.dodaj_frame, width=25)
        self.dodaj_entry.grid(column=1, row=0, padx=10)

        self.dodaj_button = ttk.Button(self.dodaj_frame, text='Dodaj', command=self.add_pojazd_prowadzacy)
        self.dodaj_button.grid(column=0, columnspan=2, row=1, pady=10)

        self.zamknij_button4 = ttk.Button(self.window, text='Zamknij', command=lambda: self.window.destroy())
        self.zamknij_button4.grid(column=0, row=4, pady=20)

        for name in self.pp_prow_values:
            self.lista_operatorow.insert("", tk.END, values=[name])

    def delete_pojazd_prowadzacy(self):
        """ Function to removing elements from list of persons
            'Opcje' -> 'Edytuj prowadzących - Kierowca' -> 'Usuń'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        plik.close()
        lista = osoby['prowadzacy']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'prowadzacy'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usunięcie z listy osoby zaznaczonej w widoku
            nowa_lista = {'prowadzacy': lista}  # Przypisanie do zmiennej nowej wartości klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, żeby wyzerować zawartość
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.pp_prow_values = osoby['prowadzacy']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_prow_combobox.config(values=self.pp_prow_values)
            self.szukaj_pojazd_prowadzacy_entry.config(values=self.pp_prow_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij inne okna i spróbuj ponownie')

    def add_pojazd_prowadzacy(self):
        """ Function to adding elements to the list of operators
            'Opcje' -> 'Edytuj prowadzących - Kierowca' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawartości pliku
        lista = osoby['prowadzacy']  # Przypisanie do zmiennej 'lista' listy osób z klucza 'prowadzacy'
        try:
            oper = self.dodaj_entry.get()
            lista.append(oper)  # Dodanie do listy osoby wpisanej przez użytkownika
            nowa_lista = {'prowadzacy': lista}  # Przypisanie do zmiennej nowej wartości klucza 'prowadzacy'
            osoby.update(nowa_lista)  # Aktualizacja zawartości pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisało wartość, a nie dodało nową na koniec.
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych wartości

            self.pp_prow_values = osoby['prowadzacy']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_prow_combobox.config(values=self.pp_prow_values)
            self.szukaj_pojazd_prowadzacy_entry.config(values=self.pp_prow_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('Błąd', 'Zamknij wszystkie okna i spróbuj ponownie')

    def info(self):
        window = tk.Toplevel(self.root)
        window.title('Informacje')

        info_label1 = tk.Label(window, text='Wersja programu:')
        info_label3 = tk.Label(window, text='Autor:')
        info_label5 = tk.Label(window, text='Data wydania:')
        info_label7 = tk.Label(window, text='Data ostatniej aktualizacji:')
        info_label1.grid(column=0, row=0, pady=5, sticky='E')
        info_label3.grid(column=0, row=1, sticky='E')
        info_label5.grid(column=0, row=2, pady=5, sticky='E')
        info_label7.grid(column=0, row=3, pady=5, sticky='E')

        info_label2 = tk.Label(window, text='1.1')
        info_label4 = tk.Label(window, text='Martin Brzeziński')
        info_label6 = tk.Label(window, text='1 października 2022')
        info_label8 = tk.Label(window, text='7 października 2022')
        info_label2.grid(column=1, row=0, pady=5, sticky='W')
        info_label4.grid(column=1, row=1, sticky='W')
        info_label6.grid(column=1, row=2, pady=5, sticky='W')
        info_label8.grid(column=1, row=3, pady=5, sticky='W')

        window.columnconfigure('all', pad=50)
        window.rowconfigure('all', pad=10)

    def statystyki(self):
        self.window = tk.Toplevel(self.root)
        self.window.title('Statystyki')

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()

        # @@@@@@@@@@@@ STATYSTYKI POJAZDU @@@@@@@@@@@@
        suma = self.cursor.execute(""" SELECT COUNT(id) FROM pojazdy; """)
        for n in suma:
            suma = n[0]

        suma_niezwr = self.cursor.execute(
            """ SELECT COUNT(id) FROM pojazdy WHERE data_zwrotu IS NULL OR data_zwrotu = "";""")
        for n in suma_niezwr:
            suma_niezwr = n[0]

        max_czas = self.cursor.execute(
            """ SELECT MIN(data_pobrania) FROM pojazdy WHERE data_zwrotu IS NULL OR data_zwrotu = ""; """)
        for n in max_czas:
            max_czas = n[0]

        t1 = datetime.strptime(max_czas, '%Y-%m-%d %H:%M')
        t2 = datetime.now()
        diff = t2 - t1

        avg = self.cursor.execute(
            """ SELECT data_pobrania FROM pojazdy WHERE data_zwrotu IS NULL OR data_zwrotu = ""; """)
        list_time = [datetime.strptime(s, '%Y-%m-%d %H:%M') for a in avg for s in a]  # Lista z datami z zapytania SQL
        list_diff = [t2 - data for data in list_time]  # Lista z różnicami dat z zapytania a datą aktualną
        sum = timedelta(0)
        for data in list_diff:  # Suma wszystkich różnic dat
            sum += data
        avg_time = sum / len(list_diff)  # Średnia różnica między datą pobrania a teraz.

        # @@@@@@@@@@@@@@@@@@STATYSTYKI KIEROWCY @@@@@@@@@@@@@@
        suma2 = self.cursor.execute(""" SELECT COUNT(id) FROM kierowcy; """)
        for n in suma2:
            suma2 = n[0]

        suma_niezwr2 = self.cursor.execute(
            """ SELECT COUNT(id) FROM kierowcy WHERE data_zwrotu IS NULL OR data_zwrotu = "";""")
        for n in suma_niezwr2:
            suma_niezwr2 = n[0]

        max_czas2 = self.cursor.execute(
            """ SELECT MIN(data_pobrania) FROM kierowcy WHERE data_zwrotu IS NULL OR data_zwrotu = ""; """)
        for n in max_czas2:
            max_czas2 = n[0]

        t3 = datetime.strptime(max_czas2, '%Y-%m-%d %H:%M')
        diff2 = t2 - t3

        avg2 = self.cursor.execute(
            """ SELECT data_pobrania FROM kierowcy WHERE data_zwrotu IS NULL OR data_zwrotu = ""; """)
        list_time2 = [datetime.strptime(s, '%Y-%m-%d %H:%M') for a in avg2 for s in a]  # Lista z datami z zapytania SQL
        list_diff2 = [t2 - data for data in list_time2]  # Lista z różnicami dat z zapytania a datą aktualną
        sum2 = timedelta(0)
        for data in list_diff2:  # Suma wszystkich różnic dat
            sum2 += data
        avg_time2 = sum2 / len(list_diff2)  # Średnia różnica między datą pobrania a teraz.

        self.db.close()

        info_label1 = tk.Label(self.window, text='Suma rekordów:')
        info_label3 = tk.Label(self.window, text='Suma niezwróconych teczek:')
        info_label5 = tk.Label(self.window, text='Maksymalny czas przetrzymywania teczki:')
        info_label7 = tk.Label(self.window, text='Średni czas przetrzymywania teczki:')

        info_label10 = tk.Label(self.window, text='Suma rekordów:')
        info_label30 = tk.Label(self.window, text='Suma niezwróconych teczek:')
        info_label50 = tk.Label(self.window, text='Maksymalny czas przetrzymywania teczki:')
        info_label70 = tk.Label(self.window, text='Średni czas przetrzymywania teczki:')

        info_label1.grid(column=0, row=2, pady=0, sticky='E')
        info_label3.grid(column=0, row=3, sticky='E')
        info_label5.grid(column=0, row=4, pady=0, sticky='E')
        info_label7.grid(column=0, row=5, pady=0, sticky='E')

        info_label10.grid(column=0, row=8, pady=0, sticky='E')
        info_label30.grid(column=0, row=9, sticky='E')
        info_label50.grid(column=0, row=10, pady=0, sticky='E')
        info_label70.grid(column=0, row=11, pady=0, sticky='E')

        info_label2 = tk.Label(self.window, text=suma)
        info_label4 = tk.Label(self.window, text=suma_niezwr)
        info_label6 = tk.Label(self.window, text=f'{str(diff.days)} dni')
        info_label8 = tk.Label(self.window, text=f'{str(avg_time.days)} dni')

        info_label20 = tk.Label(self.window, text=suma2)
        info_label40 = tk.Label(self.window, text=suma_niezwr2)
        info_label60 = tk.Label(self.window, text=f'{str(diff2.days)} dni')
        info_label80 = tk.Label(self.window, text=f'{str(avg_time2.days)} dni')

        info_label2.grid(column=1, row=2, pady=0, sticky='W')
        info_label4.grid(column=1, row=3, sticky='W')
        info_label6.grid(column=1, row=4, pady=0, sticky='W')
        info_label8.grid(column=1, row=5, pady=0, sticky='W')

        info_label20.grid(column=1, row=8, pady=0, sticky='W')
        info_label40.grid(column=1, row=9, sticky='W')
        info_label60.grid(column=1, row=10, pady=0, sticky='W')
        info_label80.grid(column=1, row=11, pady=0, sticky='W')

        sep = ttk.Separator(self.window, orient='horizontal')
        sep.grid(columnspan=2, column=0, row=6, padx=10, pady=1, ipadx=200, ipady=10)

        pojazd_label = tk.Label(self.window, text='POJAZD')
        kierowca_label = tk.Label(self.window, text='KIEROWCA')

        pojazd_label.grid(columnspan=2, column=0, row=0)
        kierowca_label.grid(columnspan=2, column=0, row=7)

        self.window.columnconfigure('all', pad=50)
        self.window.rowconfigure('all', pad=10)


class EditKierowca:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Edycja wpisu")
        self.root.attributes('-topmost', 1)
        self.root.geometry('450x550+300+300')

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
                  'prowadzacy': 'Prowadzący sprawę',
                  'operator_pob': 'Operator Pobranie',
                  'data_zw': 'Data zwrotu',
                  'osoba_zw': 'Zwracający',
                  'operator_zw': 'Operator zwrot',
                  'uwagi': 'Uwagi'}
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
        self.prowadzacy_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.prowadzacy_entry.pack(anchor='w', pady=5)
        self.operator_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_pob_entry.pack(anchor='w', pady=5)
        self.data_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.data_zw_entry.pack(anchor='w', pady=5)
        self.osoba_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.osoba_zw_entry.pack(anchor='w', pady=5)
        self.operator_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_zw_entry.pack(anchor='w', pady=5)
        self.uwagi_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.uwagi_entry.pack(anchor='w', pady=5)

        self.edycja_zamknij_button = ttk.Button(self.root, text='Zamknij', command=lambda: self.root.destroy())
        self.edycja_zamknij_button.grid(column=0, row=2, pady=10)

        self.edycja_accept_button = ttk.Button(self.root, text='Akceptuj', command=self.accept)
        self.edycja_accept_button.grid(column=1, row=2, pady=10)

        self.edycja_delete_button = ttk.Button(self.root, text='Usuń', command=self.delete)
        self.edycja_delete_button.grid(column=1, row=3, pady=30)

    def accept(self):
        values = []
        columns = ['pesel', 'nazwisko', 'imie', 'nr_kk', 'data_pobrania', 'osoba_pobranie', 'prowadzacy',
                   'operator_pobranie', 'data_zwrotu', 'osoba_zwrot', 'operator_zwrot', 'uwagi']
        entries = self.entries_frame.winfo_children()
        for entry1 in entries:
            values.append(entry1.get())
        pairs = {}
        for p in zip(columns, values):
            pairs[p[0]] = p[1]
        try:
            sql = self.sql_edit('kierowcy', **pairs)
            with sqlite3.connect('archeo.db') as self.db:
                self.cursor = self.db.cursor()
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
            self.root.lower()
            showinfo('Zapisano', 'Wprowadzone zmiany zostały zapisane.')
            self.root.destroy()
        except Exception as E:
            showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.', details=f'{E}')

    def delete(self):
        potwierdzenie = askyesno('Ostrzeżenie!', 'Usuwasz wpis z bazy danych, ta czynność jest NIEODWRACALNA!\n',
                                 detail='Czy na pewno chcesz usunąć ten wpis?')
        self.root.lower()
        if potwierdzenie:
            try:
                sql = self.sql_delete('kierowcy')
                with sqlite3.connect('archeo.db') as self.db:
                    self.cursor = self.db.cursor()
                self.cursor.execute(sql)
                self.db.commit()
                self.db.close()
                self.root.lower()
                showinfo('Usunięto', 'Zaznaczony wpis został usunięty z bazy danych.')
                self.root.destroy()
            except Exception as E:
                showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.', detail=f'{E}')

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


class EditPojazd:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Edycja wpisu")
        self.root.attributes('-topmost', 1)
        self.root.geometry('450x450+300+300')

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
                  'prowadzacy': 'Prowadzący sprawę',
                  'operator_pobranie': 'Operator pobranie',
                  'data_zwrotu': 'Data zwrotu',
                  'osoba_zwrot': 'Zwracający',
                  'operator_zwrot': 'Operator zwrot',
                  'uwagi': 'Uwagi'}

        for k, v in labels.items():
            self.k = tk.Label(self.labels_frame, text=v).pack(anchor='e', pady=5)

        self.tr_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.tr_entry.pack(anchor='w', pady=5)
        self.data_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.data_pob_entry.pack(anchor='w', pady=5)
        self.osoba_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.osoba_pob_entry.pack(anchor='w', pady=5)
        self.prowadzacy_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.prowadzacy_entry.pack(anchor='w', pady=5)
        self.operator_pob_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_pob_entry.pack(anchor='w', pady=5)
        self.data_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.data_zw_entry.pack(anchor='w', pady=5)
        self.osoba_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.osoba_zw_entry.pack(anchor='w', pady=5)
        self.operator_zw_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.operator_zw_entry.pack(anchor='w', pady=5)
        self.uwagi_entry = tk.Entry(self.entries_frame, width=25, font='Arial 11')
        self.uwagi_entry.pack(anchor='w', pady=5)

        self.edycja_zamknij_button = ttk.Button(self.root, text='Zamknij', command=lambda: self.root.destroy())
        self.edycja_zamknij_button.grid(column=0, row=2, pady=10)

        self.edycja_accept_button = ttk.Button(self.root, text='Akceptuj', command=self.accept)
        self.edycja_accept_button.grid(column=1, row=2, pady=10)

        self.edycja_delete_button = ttk.Button(self.root, text='Usuń', command=self.delete)
        self.edycja_delete_button.grid(column=1, row=3, pady=30, sticky='S')

    def accept(self):
        values = []
        columns = ['tr', 'data_pobrania', 'osoba_pobranie', 'prowadzacy',
                   'operator_pobranie', 'data_zwrotu', 'osoba_zwrot', 'operator_zwrot', 'uwagi']
        a = self.entries_frame.winfo_children()
        for entry1 in a:
            values.append(entry1.get())
        pairs = {}
        for p in zip(columns, values):
            pairs[p[0]] = p[1]
        try:
            sql = self.sql_edit('pojazdy', **pairs)
            with sqlite3.connect('archeo.db') as self.db:
                self.cursor = self.db.cursor()
            self.cursor.execute(sql)
            self.db.commit()
            self.db.close()
            self.root.lower()
            showinfo('Zapisano', 'Wprowadzone zmiany zostały zapisane.')
            self.root.destroy()
        except Exception as E:
            showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.', details=f'{E}')

    def delete(self):
        potwierdzenie = askyesno('Ostrzeżenie!', 'Usuwasz wpis z bazy danych, ta czynność jest NIEODWRACALNA!\n',
                                 detail='Czy na pewno chcesz usunąć ten wpis?')
        if potwierdzenie:
            try:
                sql = self.sql_delete('pojazdy')
                with sqlite3.connect('archeo.db') as self.db:
                    self.cursor = self.db.cursor()
                self.cursor.execute(sql)
                self.db.commit()
                self.db.close()
                self.root.lower()
                showinfo('Usunięto', 'Zaznaczony wpis został usunięty z bazy danych.')
                self.root.destroy()
            except Exception as E:
                showerror('Błąd', 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.', detail=f'{E}')

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


# Dodanie wpisów z pliku csv do tabeli pojazdy
"""wpisy = open('poj.csv')
with sqlite3.connect('archeo.db') as db:
    cursor = db.cursor()
for line in wpisy:
    linia = line.split(';')
    if linia[5]:
        q = f"INSERT INTO pojazdy " \
            f"(tr, data_pobrania, osoba_pobranie, prowadzacy, operator_pobranie, data_zwrotu, " \
            f"osoba_zwrot, operator_zwrot, uwagi) " \
            f"VALUES ('{linia[1]}', '{linia[2]}', '{linia[3]}', '{linia[4]}', '{linia[7]}', " \
            f"'{linia[5]}', '{linia[6]}', '{linia[7]}', '{linia[8]}'); "
        cursor.execute(q)
        db.commit()
    else:
        q = f"INSERT INTO pojazdy " \
            f"(tr, data_pobrania, osoba_pobranie, prowadzacy, operator_pobranie, uwagi) " \
            f"VALUES ('{linia[1]}', '{linia[2]}', '{linia[3]}', '{linia[4]}', 'Arkadiusz Wieloch', '{linia[8]}'); "
        cursor.execute(q)
        db.commit()
    
db.close()"""

# Dodanie wpisów z pliku csv do tabeli kierowcy
"""wpisy = open('kier.csv')
with sqlite3.connect('archeo.db') as db:
    cursor = db.cursor()
for line in wpisy:
    linia = line.split(';')
    kk = 'B/U'
    if linia[5]:
        kk = linia[5]
    if linia[10]:
        q = f"INSERT INTO kierowcy " \
            f"(pesel, nazwisko, imie, nr_kk, data_pobrania, osoba_pobranie, prowadzacy, operator_pobranie, " \
            f"data_zwrotu, osoba_zwrot, operator_zwrot, uwagi) " \
            f"VALUES ('{linia[4]}', '{linia[2]}', '{linia[3]}', '{kk}', '{linia[7]}', '{linia[8]}', '{linia[9]}', " \
            f"'{linia[12]}', '{linia[10]}', '{linia[11]}', '{linia[12]}', '{linia[13]}'); "
        cursor.execute(q)
        db.commit()
    else:
        q = f"INSERT INTO kierowcy " \
            f"(pesel, nazwisko, imie, nr_kk, data_pobrania, osoba_pobranie, prowadzacy, operator_pobranie, uwagi) " \
            f"VALUES ('{linia[4]}', '{linia[2]}', '{linia[3]}', '{kk}', '{linia[7]}', '{linia[8]}', '{linia[9]}', " \
            f"'Arkadiusz Wieloch', '{linia[13]}'); "
        cursor.execute(q)
        db.commit()
db.close()"""

'''with sqlite3.connect('archeo.db') as db:
    cursor = db.cursor()
cursor.execute("SELECT id, data_pobrania FROM pojazdy WHERE LENGTH(data_pobrania) < 12;")
dates = []
for n in cursor:
    print(n)
    dates.append(n)

for d in dates:
    cursor.execute(f"""UPDATE pojazdy SET data_pobrania = '{d[1] + " 12:00"}' WHERE id == {d[0]}""")
    db.commit()
db.close()'''

'''with sqlite3.connect('archeo.db') as db:
    cursor = db.cursor()
cursor.execute("SELECT id, data_pobrania FROM kierowcy WHERE LENGTH(data_pobrania) < 12;")
dates2 = []
for n in cursor:
    # print(n)
    dates2.append(n)

for d in dates2:
    cursor.execute(f"""UPDATE kierowcy SET data_pobrania = '{d[1] + " 12:00"}' WHERE id == {d[0]}""")
    db.commit()
db.close()'''

'''with sqlite3.connect('archeo.db') as db:
    cursor = db.cursor()
cursor.execute("SELECT id, data_zwrotu FROM kierowcy WHERE LENGTH(data_zwrotu) < 12 AND data_zwrotu != 'Żądanie akt' ;")
dates2 = []
for n in cursor:
    # print(n)
    dates2.append(n)

for d in dates2:
    cursor.execute(f"""UPDATE kierowcy SET data_zwrotu = '{d[1] + " 12:00"}' WHERE id == {d[0]}""")
    db.commit()
db.close()'''

'''with sqlite3.connect('archeo.db') as db:
    cursor = db.cursor()
cursor.execute("SELECT id, data_zwrotu FROM pojazdy WHERE LENGTH(data_zwrotu) < 12;")
dates2 = []
for n in cursor:
    # print(n)
    dates2.append(n)

for d in dates2:
    cursor.execute(f"""UPDATE pojazdy SET data_zwrotu = '{d[1] + " 12:00"}' WHERE id == {d[0]}""")
    db.commit()
db.close()'''
# try:
#     size1 = os.path.getsize('archeo.db')  # Rozmiar oryginalnej bazy danych.
#     size2 = os.path.getsize(r'\\fs1spp\kierowca\DB\archeo.db')  # Rozmiar kopii bazy danych.
#     time1 = os.path.getmtime('archeo.db')  # Data modyfikacji oryg. bazy danych
#     time2 = os.path.getmtime(r'\\fs1spp\kierowca\DB\archeo.db')  # Data modyfikacji kopii bazy danych.
#
#     # Utworzenie kopii bazy danych dla wyszukiwarki w folderze kierowca.
#     original = r'archeo.db'
#     # target = r'W:\DB\archeo.db'
#     target = r'\\fs1spp\kierowca\DB\archeo.db'
#     if time1 > time2 and size1 > size2:
#         shutil.copyfile(original, target)
# except Exception as E:
#     showerror('Błąd', 'Wystąpił problem ze skopiowaniem bazy danych do folderu "kierowca".', detail=f'{E}')


# TODO Excel przed migracją: format daty, zmienić format daty urodzenia obcokrajowców,
#  Imię i Nazwisko operatora i innych ustawić w dobrej kolejności, operator pobranie tam gdzie nie ma zwrotu

if __name__ == '__main__':
    app = App()
