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
        self.icon = tk.PhotoImage(file='graphics/ikona2.png')
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
        # Set Treeview Style
        self.tv_style = ttk.Style(self.root)
        self.tv_style.configure('Treeview', rowheight=25)
        self.tv_style.configure('Treeview', font=('Tahoma', 11))
        # Set Treeview Headings Style
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
        self.center_y = int(self.screen_height / 2 - self.window_height / 1.84)
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
        # self.file_menu.add_command(label='Pomniejsz', command=self.pomniejsz)
        # self.file_menu.add_separator()
        self.file_menu.add_command(label='Zamknij', command=self.root.destroy)

        # Options items
        self.help_menu.add_command(label='Edytuj operator??w', command=self.operator_edit_window)
        self.help_menu.add_command(label='Edytuj osoby - Kierowca', command=self.osoba_kierowca_edit_window)
        self.help_menu.add_command(label='Edytuj osoby - Pojazd', command=self.osoba_pojazd_edit_window)
        self.help_menu.add_command(label='Edytuj prowadz??cych - Kierowca', command=self.prowadzacy_kierowca_edit_window)
        self.help_menu.add_command(label='Edytuj prowadz??cych - Pojazd', command=self.prowadzacy_pojazd_edit_window)

        self.menubar.add_cascade(label='Menu', menu=self.file_menu)
        self.menubar.add_cascade(label='Opcje', menu=self.help_menu)

        # Welcome label
        self.welcome = tk.Label(self.root,
                                background='green2',
                                foreground='white',
                                font='Arial 15 bold',
                                text='Witaj w Archeo 2022!')
        self.welcome.pack(fill='both', ipady=5)

        # OPERATOR SELECT
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.operator_values = obj['operator']
        osoby_json.close()

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

        # Configure columns
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

        # Register Plate
        self.pp_tablica_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Numer TR:', background='yellow')
        self.pp_tablica_label.grid(column=1, row=0, sticky='E', pady=20, padx=10)

        self.pp_tablica_img = tk.PhotoImage(file='graphics/tablica.gif')
        self.pp_tablica_img_label = ttk.Label(self.pojazd_pobranie_labelframe, image=self.pp_tablica_img)
        self.pp_tablica_img_label.grid(column=2, row=0, sticky='W')

        self.pp_tr_entry_var = tk.StringVar()
        self.pp_tablica_entry = ttk.Entry(self.pojazd_pobranie_labelframe, state='disabled', width=12,
                                          justify='center', font='Arial 13 bold', textvariable=self.pp_tr_entry_var)
        self.pp_tablica_entry.grid(column=2, row=0, sticky='W', padx=14)
        self.pp_tr_entry_var.trace_add('write', self.to_uppercase)

        # Osoba pobieraj??ca
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.pp_osoba_values = obj['pojazd']
        osoby_json.close()

        self.pp_osoba_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Osoba pobieraj??ca:', background='pink')
        self.pp_osoba_label.grid(column=1, row=2, sticky='E', pady=10, padx=10)

        self.pp_osoba_combobox = ttk.Combobox(self.pojazd_pobranie_labelframe, values=self.pp_osoba_values,
                                              state='disabled', width=25, font='Arial 13 bold')
        self.pp_osoba_combobox.grid(column=2, row=2, sticky='W')

        # Osoba prowadz??ca spraw??
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.pp_prow_values = obj['prowadzacy']
        osoby_json.close()

        self.pp_prow_label = ttk.Label(self.pojazd_pobranie_labelframe, text='Osoba prowadz??ca spraw??:',
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

        self.pz_tablica_img = tk.PhotoImage(file='graphics/tablica.gif')
        self.pz_tablica_img_label = ttk.Label(self.pojazd_zwrot_labelframe, image=self.pz_tablica_img)
        self.pz_tablica_img_label.grid(column=2, row=0, sticky='W')

        self.pz_tr_entry_var = tk.StringVar()
        self.pz_tablica_entry = ttk.Entry(self.pojazd_zwrot_labelframe, state='disabled', width=12,
                                          justify='center', font='Arial 13 bold', textvariable=self.pz_tr_entry_var)
        self.pz_tablica_entry.grid(column=2, row=0, sticky='W', padx=14)
        self.pz_tr_entry_var.trace_add('write', self.to_uppercase)

        # Osoba zwracaj??ca
        self.pz_osoba_label = ttk.Label(self.pojazd_zwrot_labelframe, text='Osoba zwracaj??ca:', background='pink')
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

        # Set pojazd table height based on screen resolution
        self.notebook.update()
        note = self.notebook.winfo_reqheight()
        tab_poj = int((self.window_height - (140 + note)) / 30)

        # DATABASE VIEW
        self.pojazd_db_columns = ("id", "TR", "Data pobrania", "Pobieraj??cy", "Prowadz??cy spraw??",
                                  "Operator - pobranie", "Data zwrotu", "Zwracaj??cy", "Operator - zwrot", "Uwagi")
        self.pojazd_db_view = ttk.Treeview(self.pojazd, columns=self.pojazd_db_columns, show='headings', height=tab_poj)
        # Set columns width
        for column in self.pojazd_db_columns:
            self.pojazd_db_view.heading(column, text=column, anchor='center')
        self.pojazd_db_view.column("id", width=60)
        self.pojazd_db_view.column("TR", width=120)
        self.pojazd_db_view.column("Data pobrania", width=120)
        self.pojazd_db_view.column("Data zwrotu", width=120)
        self.pojazd_db_view.column("Operator - pobranie", width=140)

        self.pojazd_db_view.grid(column=1, columnspan=3, row=4, sticky='NEWS')

        # Vertical Scrollbar
        self.pojazd_db_scrollbar = ttk.Scrollbar(self.pojazd, orient=tk.VERTICAL, command=self.pojazd_db_view.yview)
        self.pojazd_db_view.configure(yscrollcommand=self.pojazd_db_scrollbar.set)
        self.pojazd_db_scrollbar.grid(column=4, row=4, sticky='NS')
        # Horizontal Scrollbar
        self.pojazd_db_scrollbar_x = ttk.Scrollbar(self.pojazd, orient=tk.HORIZONTAL, command=self.pojazd_db_view.xview)
        self.pojazd_db_view.configure(xscrollcommand=self.pojazd_db_scrollbar_x.set)
        self.pojazd_db_scrollbar_x.grid(column=1, columnspan=3, row=5, sticky='WE')

        # CLOSE BUTTON
        self.zamknij_button = ttk.Button(self.pojazd, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button.grid(column=2, row=6, sticky="WE", padx=10, pady=10)
        # Show all Button
        self.pokaz_wszystko = ttk.Button(self.pojazd, text='Poka?? wszystko', command=self.show_all)
        self.pokaz_wszystko.grid(column=3, row=6)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ KIEROWCA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # Configure columns size
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

        # DATA URODZENIA ??? KIEROWCA (w przypadku braku PESEL)
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

        # Nazwisko i imi?? ??? POBRANIE AKT
        self.kp_nazwisko_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Nazwisko:', background='yellow')
        self.kp_nazwisko_label.grid(column=0, row=0, sticky='E')

        self.kp_nazwisko_entry = tk.Entry(self.kierowca_pobranie_left_frame,
                                          state='disabled', width=17, font='Arial 13 bold')
        self.kp_nazwisko_entry.grid(column=1, row=0, sticky='W', pady=5)

        self.kp_imie_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Imi??:', background='yellow')
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

        # NR Karty Kierowcy ??? POBRANIE AKT
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

        self.kp_uwagi = tk.Entry(self.kierowca_pobranie_right_frame, width=16,
                                 state='disabled', background='gray90', font='Arial 15')
        self.kp_uwagi.grid(column=1, row=4, rowspan=2, sticky='W', pady=30)

        # Osoba Pobieraj??ca
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.kp_osoba_values = obj['kierowca']
        osoby_json.close()

        self.kp_osoba_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Osoba pobieraj??ca:', background='pink')
        self.kp_osoba_label.grid(column=0, row=4, sticky='E', pady=10)

        self.kp_osoba_combobox = ttk.Combobox(self.kierowca_pobranie_left_frame, values=self.kp_osoba_values,
                                              state='disabled', font='Arial 13 bold', width=17)
        self.kp_osoba_combobox.grid(column=1, row=4, sticky='W')

        # Osoba prowadz??ca spraw??
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.kp_prow_values = obj['prowadzacy_kier']
        osoby_json.close()

        self.kp_prow_label = ttk.Label(self.kierowca_pobranie_left_frame, text='Osoba prowadz??ca spraw??:',
                                       background='pink')
        self.kp_prow_label.grid(column=0, row=5, sticky='E', pady=2, padx=0)

        self.kp_prow_combobox = ttk.Combobox(self.kierowca_pobranie_left_frame, values=self.kp_prow_values,
                                             state='disabled', width=17, font='Arial 13 bold')
        self.kp_prow_combobox.grid(column=1, row=5, sticky='W')

        # ????DANIE AKT
        self.kp_zadanie_akt_var = tk.BooleanVar()
        self.kp_zadanie_akt = ttk.Checkbutton(self.kierowca_pobranie_right_frame,
                                              onvalue=True,
                                              offvalue=False,
                                              text='????danie akt',
                                              variable=self.kp_zadanie_akt_var)
        self.kp_zadanie_akt.grid(column=0, row=6, sticky='E', pady=2)
        self.kp_zadanie_akt.state(['!alternate'])

        # PRZYCISK ZASTOSUJ - KIEROWCA POBRANIE
        self.kp_zastosuj_button = tk.Button(self.kierowca_pobranie_labelframe, text='Zastosuj',
                                            width=40, command=self.kierowca_zastosuj_pobranie)
        self.kp_zastosuj_button.grid(column=1, columnspan=2, row=12, pady=10)

        # Potwierdzenie zapisu ??? Kierowca pobranie
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

        # Imi?? i Nazwisko osoby z teczki zwracanej.
        self.kz_dane = ttk.Label(self.kierowca_zwrot_labelframe, text="")
        self.kz_dane.grid(columnspan=2, column=1, row=4, pady=5)

        # Osoba zwracaj??ca
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.kz_osoba_values = obj['kierowca']
        osoby_json.close()

        self.kz_osoba_label = ttk.Label(self.kierowca_zwrot_labelframe, text='Osoba zwracaj??ca:', background='pink')
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

        # Potwierdzenie zapisu ??? Kierowca pobranie
        self.kz_potwierdzenie_label = tk.Label(self.kierowca_zwrot_labelframe)
        self.kz_potwierdzenie_label.grid(column=0, columnspan=4, row=14)

        # KIEROWCA HORIZONTAL SEPARATOR
        self.kierowca_hor_separator = ttk.Separator(self.kierowca, orient='horizontal')
        self.kierowca_hor_separator.grid(column=1, columnspan=3, row=2, ipadx=self.window_width, pady=10)

        self.kierowca.update()
        note = self.kierowca.winfo_reqheight()
        tab_kier = int((self.window_height - (140 + note)) / 30)

        # KIEROWCA DATABASE VIEW
        self.kierowca_db_columns = ('id', 'PESEL', 'Nazwisko', 'Imi??', 'Nr Karty Kierowcy', 'Data pobrania',
                                    'Pobieraj??cy', 'Osoba prowadz??ca', 'Operator - pobranie', 'Data zwrotu',
                                    'Zwracaj??cy', 'Operator - zwrot', 'uwagi')
        self.kierowca_db_view = ttk.Treeview(self.kierowca, columns=self.kierowca_db_columns,
                                             show='headings', height=tab_kier)

        # Set columns width
        for column in self.kierowca_db_columns:
            self.kierowca_db_view.heading(column, text=column, anchor='center')
            self.kierowca_db_view.column(column, width=150)
        self.kierowca_db_view.column("id", width=50)
        self.kierowca_db_view.column("PESEL", width=100)
        self.kierowca_db_view.column("Imi??", width=100)

        self.kierowca_db_view.grid(column=1, columnspan=3, row=4, sticky='NEWS')

        # KIEROWCA Vertical Scrollbar
        self.kierowca_db_scrollbar = ttk.Scrollbar(self.kierowca,
                                                   orient=tk.VERTICAL,
                                                   command=self.kierowca_db_view.yview)
        self.kierowca_db_view.configure(yscrollcommand=self.kierowca_db_scrollbar.set)
        self.kierowca_db_scrollbar.grid(column=4, row=4, sticky='NS')

        # KIEROWCA Horizontal Scrollbar
        self.kierowca_db_scrollbar_x = ttk.Scrollbar(self.kierowca,
                                                    orient=tk.HORIZONTAL,
                                                    command=self.kierowca_db_view.xview)
        self.kierowca_db_view.configure(xscrollcommand=self.kierowca_db_scrollbar_x.set)
        self.kierowca_db_scrollbar_x.grid(column=1, columnspan=3, row=5, sticky='WE')

        # CLOSE BUTTON
        self.zamknij_button2 = ttk.Button(self.kierowca, text="Zamknij", command=lambda: self.root.quit())
        self.zamknij_button2.grid(column=2, row=6, sticky="WE", padx=10, pady=0)
        # Show all Button
        self.pokaz_wszystko2 = ttk.Button(self.kierowca, text='Poka?? wszystko', command=self.show_all_kierowca)
        self.pokaz_wszystko2.grid(column=3, row=6)

        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ WYSZUKIWARKA @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        # @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

        # Configure columns
        self.wyszukiwanie.columnconfigure(0, weight=1)
        self.wyszukiwanie.columnconfigure(1, minsize=10)

        # Registry select LabelFrame
        self.rejestr_labelframe = ttk.Labelframe(self.wyszukiwanie, text='Wybierz rejestr')
        self.rejestr_labelframe.grid(column=0, row=0, pady=5, padx=15, sticky='W')

        # Radiobutton Variable
        self.selected_value = tk.IntVar(value=0)

        # Radiobutton Pojazd i Kierowca
        self.rejestr_pojazd_radio = ttk.Radiobutton(self.rejestr_labelframe, text='Pojazd', value=1,
                                                    variable=self.selected_value, command=self.wybierz_rejestr)
        self.rejestr_pojazd_radio.grid(column=0, row=0, pady=5, padx=10)

        self.rejestr_kierowca_radio = ttk.Radiobutton(self.rejestr_labelframe, text='Kierowca', value=0,
                                                      variable=self.selected_value, command=self.wybierz_rejestr)
        self.rejestr_kierowca_radio.grid(column=1, row=0, pady=5, padx=10)

        # Search options LabelFrame
        self.wyszukiwanie_options = ttk.Labelframe(self.wyszukiwanie, text='Opcje wyszukiwania')
        self.wyszukiwanie_options.grid(column=0, row=1, sticky='W', padx=15, ipadx=15)

        # SEARCH OPTIONS

        # @@@ POJAZD @@@
        self.wyszukaj_pojazd_frame = tk.Frame(self.wyszukiwanie_options)
        # self.wyszukaj_pojazd_frame.grid(column=0, row=0)

        # Register Plate number
        self.szukaj_tr_label = ttk.Label(self.wyszukaj_pojazd_frame, text='     Numer TR:', font='Arial 10')
        self.szukaj_tr_label.grid(column=0, row=0, pady=10, sticky='E')

        self.szukaj_tr_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=15)
        self.szukaj_tr_entry.grid(column=1, row=0, sticky='W')

        # Prowadz??cy spraw??
        self.szukaj_pojazd_prowadzacy_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                        text='     Prowadz??cy spraw??:',
                                                        font='Arial 10')
        self.szukaj_pojazd_prowadzacy_label.grid(column=2, row=0)

        self.szukaj_pojazd_prowadzacy_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_prow_values)
        self.szukaj_pojazd_prowadzacy_entry.grid(column=3, row=0)

        # Osoba pobieraj??ca
        self.szukaj_pojazd_osoba_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                            text='     Osoba pobieraj??ca:',
                                                            font='Arial 10')
        self.szukaj_pojazd_osoba_pobranie_label.grid(column=0, row=1)

        self.szukaj_pojazd_osoba_pobranie_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_osoba_values)
        self.szukaj_pojazd_osoba_pobranie_entry.grid(column=1, row=1)

        # Osoba zwracaj??ca
        self.szukaj_pojazd_osoba_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                         text='     Osoba zwracaj??ca:', font='Arial 10')
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

        # Data pobrania OD
        self.szukaj_pojazd_data_od_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                              text='   Data pobrania od:', font='Arial 10')
        self.szukaj_pojazd_data_od_pobranie_label.grid(column=4, row=1, pady=10)

        self.szukaj_pojazd_data_od_pobranie_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_od_pobranie_entry.grid(column=5, row=1)

        # Data pobrania DO
        self.szukaj_pojazd_data_do_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                              text='   Data pobrania do:', font='Arial 10')
        self.szukaj_pojazd_data_do_pobranie_label.grid(column=6, row=1, pady=10)

        self.szukaj_pojazd_data_do_pobranie_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_do_pobranie_entry.grid(column=7, row=1)

        # Data zwrotu OD
        self.szukaj_pojazd_data_od_zwrot_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                           text='   Data zwrotu od:', font='Arial 10')
        self.szukaj_pojazd_data_od_zwrot_label.grid(column=4, row=2, pady=10, sticky='E')

        self.szukaj_pojazd_data_od_zwrot_entry = ttk.Entry(self.wyszukaj_pojazd_frame, width=20)
        self.szukaj_pojazd_data_od_zwrot_entry.grid(column=5, row=2)

        # Data zwrotu DO
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

        # Szukaj KIEROWCA IMI??
        self.szukaj_kierowca_imie_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                             text='Imi?? ', font='Arial 10')
        self.szukaj_kierowca_imie_pobranie_label.grid(column=2, row=0, sticky='E')

        self.szukaj_kierowca_imie_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=15)
        self.szukaj_kierowca_imie_pobranie_entry.grid(column=3, row=0)

        # Szukaj KIEROWCA NAZWISKO
        self.szukaj_kierowca_nazwisko_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                                 text='Nazwisko ', font='Arial 10')
        self.szukaj_kierowca_nazwisko_pobranie_label.grid(column=2, row=1, sticky='E')

        self.szukaj_kierowca_nazwisko_pobranie_entry = ttk.Entry(self.wyszukaj_kierowca_frame, width=15)
        self.szukaj_kierowca_nazwisko_pobranie_entry.grid(column=3, row=1)

        # Szukaj KIEROWCA Osoba pobieraj??ca.
        self.szukaj_kierowca_osoba_pobranie_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                              text='     Osoba pobieraj??ca ', font='Arial 10')
        self.szukaj_kierowca_osoba_pobranie_label.grid(column=4, row=0)

        self.szukaj_kierowca_osoba_pobranie_entry = ttk.Combobox(self.wyszukaj_kierowca_frame,
                                                                 values=self.kp_osoba_values)
        self.szukaj_kierowca_osoba_pobranie_entry.grid(column=5, row=0)

        # Szukaj KIEROWCA Osoba zwracaj??ca.
        self.szukaj_kierowca_osoba_zwrot_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                           text='     Osoba zwracaj??ca ', font='Arial 10')
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

        # Szukaj KIEROWCA Prowadz??cy spraw??.
        self.szukaj_kierowca_prowadzacy_label = ttk.Label(self.wyszukaj_kierowca_frame,
                                                          text='   Prowadz??cy spraw?? ', font='Arial 10')
        self.szukaj_kierowca_prowadzacy_label.grid(column=4, row=2, pady=6, sticky='E')

        self.szukaj_kierowca_prowadzacy_entry = ttk.Combobox(self.wyszukaj_kierowca_frame, values=self.kp_prow_values)
        self.szukaj_kierowca_prowadzacy_entry.grid(column=5, row=2)

        # Szukaj ??? PRZYCISKI
        self.szukaj_przyciski_frame = ttk.LabelFrame(self.wyszukiwanie)
        self.szukaj_przyciski_frame.grid(column=0, row=2, sticky='W', padx=15, ipady=5)

        self.szukaj_wyszukaj_button = tk.Button(self.szukaj_przyciski_frame, text='Wyszukaj',
                                                command=self.wyszukaj_kierowca_click)
        self.szukaj_wyszukaj_button.grid(column=0, row=0, padx=20, ipadx=10, pady=5)

        self.szukaj_edytuj_button = tk.Button(self.szukaj_przyciski_frame, text='Edytuj', command=self.edit_kierowca)
        self.szukaj_edytuj_button.grid(column=1, row=0, padx=20, ipadx=10, pady=5)

        self.szukaj_wyczysc_button = tk.Button(self.szukaj_przyciski_frame, text='Wyczy????', command=self.clear_entries)
        self.szukaj_wyczysc_button.grid(column=2, row=0, padx=20, ipadx=10, pady=5)

        self.tylko_niezwr_var = tk.BooleanVar()
        self.tylko_niezwr = ttk.Checkbutton(self.szukaj_przyciski_frame, text='Tylko niezwr??cone',
                                            onvalue=True, offvalue=False, variable=self.tylko_niezwr_var,
                                            command=self.tylko_niezwrocone_kier)
        self.tylko_niezwr.grid(column=0, row=1, columnspan=3, padx=20, sticky='W')

        # Number of records found LABEL
        self.informacja_label = tk.Label(self.wyszukiwanie, text=f"")
        self.informacja_label.grid(column=0, row=2, sticky='S')

        # Set pojazd table height
        self.wyszukiwanie.update()
        note = self.wyszukiwanie.winfo_reqheight()
        tab_wysz_poj = int((self.window_height - (140 + note)) / 30)

        # SZUKAJ DATABASE VIEW POJAZD
        self.szukaj_pojazd_db_columns = (
            "id", "TR", "Data pobrania", "Pobieraj??cy", "Prowadz??cy spraw??", "Operator - pobranie", "Data zwrotu",
            "Zwracaj??cy", "Operator - zwrot", "Uwagi")
        self.szukaj_pojazd_db_view = ttk.Treeview(self.wyszukiwanie,
                                                  columns=self.szukaj_pojazd_db_columns,
                                                  show='headings',
                                                  height=tab_wysz_poj)

        # Set columns width
        for column in self.szukaj_pojazd_db_columns:
            self.szukaj_pojazd_db_view.heading(column, text=column, anchor='center')
            self.szukaj_pojazd_db_view.column(column, width=180)

        self.szukaj_pojazd_db_view.column('id', width=70)
        self.szukaj_pojazd_db_view.column('TR', width=110)

        # self.szukaj_pojazd_db_view.grid(column=0, row=4, sticky='NEWS')

        # Set background color
        self.szukaj_pojazd_db_view.tag_configure('returnedodd', background='DarkSeaGreen1')
        self.szukaj_pojazd_db_view.tag_configure('notreturnedodd', background='MistyRose1')
        self.szukaj_pojazd_db_view.tag_configure('returnedeven', background='PaleGreen')
        self.szukaj_pojazd_db_view.tag_configure('notreturnedeven', background='pink1')

        # Set sorting data by clicking the header
        for col in self.szukaj_pojazd_db_columns:
            self.szukaj_pojazd_db_view.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(
                self.szukaj_pojazd_db_view, _col, False))

        # Vertical SCROLLBAR
        self.szukaj_pojazd_db_scrollbar = ttk.Scrollbar(self.wyszukiwanie,
                                                        orient=tk.VERTICAL,
                                                        command=self.szukaj_pojazd_db_view.yview)

        self.szukaj_pojazd_db_view.configure(yscrollcommand=self.szukaj_pojazd_db_scrollbar.set)
        # self.szukaj_pojazd_db_scrollbar.grid(column=1, row=4, sticky='NS')

        # Horizontal Scrollbar
        self.szukaj_pojazd_db_scrollbar_x = ttk.Scrollbar(self.wyszukiwanie,
                                                          orient=tk.HORIZONTAL,
                                                          command=self.szukaj_pojazd_db_view.xview)

        self.szukaj_pojazd_db_view.configure(xscrollcommand=self.szukaj_pojazd_db_scrollbar_x.set)
        # self.szukaj_pojazd_db_scrollbar_x.grid(column=0, row=5, sticky='WE')

        self.wyniki_label = tk.Label(self.wyszukiwanie, text="  Wyniki wyszukiwania")
        self.wyniki_label.grid(column=0, row=3, sticky='W')

        # Set kierowca table height
        self.wyszukiwanie.update()
        note = self.wyszukiwanie.winfo_reqheight()
        tab_wysz_kier = int((self.window_height - (140 + note)) / 30)

        # SZUKAJ DATABASE VIEW KIEROWCA
        self.szukaj_kierowca_db_columns = ('id', 'PESEL', 'Nazwisko', 'Imi??', 'nr_kk', 'Data pobrania', 'Pobieraj??cy',
                                           'Prowadz??cy spraw??', 'Operator pobranie', 'Data zwrotu', 'Zwracaj??cy',
                                           'Operator zwrot', 'uwagi')
        self.szukaj_kierowca_db_view = ttk.Treeview(self.wyszukiwanie,
                                                    columns=self.szukaj_kierowca_db_columns,
                                                    show='headings',
                                                    height=tab_wysz_kier)

        # Set columns width
        for column in self.szukaj_kierowca_db_columns:
            self.szukaj_kierowca_db_view.heading(column, text=column, anchor='center')
            self.szukaj_kierowca_db_view.column(column, width=150)

        self.szukaj_kierowca_db_view.column('id', width=60)
        self.szukaj_kierowca_db_view.column('nr_kk', width=70)
        self.szukaj_kierowca_db_view.column('PESEL', width=100)
        self.szukaj_kierowca_db_view.column('Imi??', width=120)

        self.szukaj_kierowca_db_view.grid(column=0, row=4, sticky='NEWS', padx=10)

        # Set background color
        self.szukaj_kierowca_db_view.tag_configure('returnedodd', background='DarkSeaGreen1')
        self.szukaj_kierowca_db_view.tag_configure('notreturnedodd', background='MistyRose1')
        self.szukaj_kierowca_db_view.tag_configure('returnedeven', background='PaleGreen')
        self.szukaj_kierowca_db_view.tag_configure('notreturnedeven', background='pink1')

        # Set sorting data by clicking the header
        for col in self.szukaj_kierowca_db_columns:
            self.szukaj_kierowca_db_view.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(
                self.szukaj_kierowca_db_view, _col, False))

        # Vertical SCROLLBAR
        self.szukaj_kierowca_db_scrollbar = ttk.Scrollbar(self.wyszukiwanie,
                                                          orient=tk.VERTICAL,
                                                          command=self.szukaj_kierowca_db_view.yview)
        self.szukaj_kierowca_db_view.configure(yscrollcommand=self.szukaj_kierowca_db_scrollbar.set)
        self.szukaj_kierowca_db_scrollbar.grid(column=1, row=4, sticky='NS')

        # Horizontal Scrollbar
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
        """Show name preview after entry pesel or nr KK"""
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
        """Disable/Enable return date entries in 'pojazd'"""
        if self.tylko_niezwr_var.get():
            self.szukaj_pojazd_data_do_zwrot_entry.delete(0, tk.END)
            self.szukaj_pojazd_data_do_zwrot_entry.config(state="disabled")
            self.szukaj_pojazd_data_od_zwrot_entry.delete(0, tk.END)
            self.szukaj_pojazd_data_od_zwrot_entry.config(state="disabled")
        else:
            self.szukaj_pojazd_data_do_zwrot_entry.config(state="normal")
            self.szukaj_pojazd_data_od_zwrot_entry.config(state="normal")

    def tylko_niezwrocone_kier(self):
        """Disable/Enable return date entries in 'kierowca'"""
        if self.tylko_niezwr_var.get():
            self.szukaj_kierowca_data_do_zwrot_entry.delete(0, tk.END)
            self.szukaj_kierowca_data_do_zwrot_entry.config(state="disabled")
            self.szukaj_kierowca_data_od_zwrot_entry.delete(0, tk.END)
            self.szukaj_kierowca_data_od_zwrot_entry.config(state="disabled")
        else:
            self.szukaj_kierowca_data_do_zwrot_entry.config(state="normal")
            self.szukaj_kierowca_data_od_zwrot_entry.config(state="normal")

    def treeview_sort_column(self, tv, col, reverse):
        """Function assigned to Treeview headers. Sort values alphabetically when clicked."""
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
            showinfo('Brak danych', 'Nie zaznaczono ??adnego wpisu.')

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
            showinfo('Brak danych', 'Nie zaznaczono ??adnego wpisu.')

    def wyszukaj_pojazd_click(self):
        """Search records in 'pojazdy' table that match given conditions"""
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
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('returnedeven',))
                elif count % 2 == 0 and n[6] == "":
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('notreturnedeven',))
                elif count % 2 == 1 and n[6] != "":
                    self.szukaj_pojazd_db_view.insert("", tk.END, values=n, tags=('returnedodd',))
                else:
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
        self.informacja_label = tk.Label(self.wyszukiwanie, text=f"Liczba znalezionych wynik??w: {suma_wyniki}")
        self.informacja_label.grid(column=0, row=2, sticky='S')

        self.db.close()

    def wyszukaj_kierowca_click(self):
        """Search records in 'kierowcy' table that match given conditions"""
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
            if not all(v == "" for v in warunki.values()):  # Je??li s?? jakie?? kryteria wyszukiwania i daty
                sql = sql[:-1] + " AND  "                   # to dodaje 'AND' pomi??dzy.
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
        self.informacja_label = tk.Label(self.wyszukiwanie, text=f"Liczba znalezionych wynik??w: {suma_wyniki}")
        self.informacja_label.grid(column=0, row=2, sticky='S')

        self.db.close()

    def clear_entries(self):
        """Clear all entries"""
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
        """Change condition entries, assign apropriate functions to 'szukaj' and 'edytuj' buttons
        and show sum of records after choose registry."""
        # Selected POJAZD
        if self.selected_value.get():
            self.wyszukaj_kierowca_frame.grid_forget()  # forget kierowca search inputs
            self.szukaj_kierowca_db_view.grid_forget()  # forget kierowca results table
            self.wyszukaj_pojazd_frame.grid(column=0, row=0)  # set pojazd search inputs
            self.szukaj_pojazd_db_view.grid(column=0, row=4, sticky='NEWS', padx=10)  # set pojazd result table
            self.szukaj_wyszukaj_button.configure(command=self.wyszukaj_pojazd_click)  # set pojazd search button command
            self.szukaj_edytuj_button.configure(command=self.edit_pojazd)  # set pojazd edit button command
            # self.informacja_label.grid_forget()
            self.suma_wyniki = len(self.szukaj_pojazd_db_view.get_children())
            self.informacja_label.config(text=f"Liczba znalezionych wynik??w: {self.suma_wyniki}")
            self.informacja_label.grid(column=0, row=2, sticky='S')
            self.tylko_niezwr.config(command=self.tylko_niezwrocone_pojazd)
            self.tylko_niezwr_var.set(False)
            self.tylko_niezwrocone_pojazd()
            self.szukaj_kierowca_db_scrollbar_x.grid_forget()
            self.szukaj_kierowca_db_scrollbar.grid_forget()
            self.szukaj_pojazd_db_scrollbar.grid(column=1, row=4, sticky='NS')
            self.szukaj_pojazd_db_scrollbar_x.grid(column=0, row=5, sticky='WE')
        # Selected KIEROWCA
        else:
            self.wyszukaj_pojazd_frame.grid_forget()  # forget pojazd search inputs
            self.szukaj_pojazd_db_view.grid_forget()  # forget pojazd results table
            self.wyszukaj_kierowca_frame.grid(column=0, row=0)  # set kierowca search inputs
            self.szukaj_kierowca_db_view.grid(column=0, row=4, sticky='NEWS', padx=10)  # set kierowca res tab
            self.szukaj_wyszukaj_button.configure(command=self.wyszukaj_kierowca_click)  # set search button command
            self.szukaj_edytuj_button.configure(command=self.edit_kierowca)  # set kierowca edit button command
            # self.informacja_label.grid_forget()
            self.suma_wyniki = len(self.szukaj_kierowca_db_view.get_children())
            self.informacja_label.config(text=f"Liczba znalezionych wynik??w: {self.suma_wyniki}")
            self.informacja_label.grid(column=0, row=2, sticky='S')
            self.tylko_niezwr.config(command=self.tylko_niezwrocone_kier)
            self.tylko_niezwr_var.set(False)
            self.tylko_niezwrocone_kier()
            self.szukaj_pojazd_db_scrollbar_x.grid_forget()
            self.szukaj_pojazd_db_scrollbar.grid_forget()
            self.szukaj_kierowca_db_scrollbar.grid(column=1, row=4, sticky='NS')
            self.szukaj_kierowca_db_scrollbar_x.grid(column=0, row=5, sticky='WE')

    def kp_data_urodzenia(self):
        """ Enable and focus on birthday entry after select checkbutton."""
        if self.kp_data_ur_var:
            self.kp_pesel_entry.config(state='disabled')
            self.kp_data_ur_entry.config(state='normal')
            self.kp_data_ur_entry.delete(0, "end")
            self.kp_data_ur_entry.focus_set()
        # Disable and fill with a valid date format after unchecked.
        if not self.kp_data_ur_var.get():
            self.kp_data_ur_entry.insert(0, "RRRR-MM-DD")
            self.kp_data_ur_entry.config(state="disabled")
            self.kp_pesel_entry.config(state='normal')
            self.kp_pesel_entry.focus_set()

    def sprawdz_pesel_pobranie(self, event):
        """Change PESEL background color to green if its have 11 signs, and to pink in other cases."""
        if len(self.kp_pesel_string.get()) == 11:
            self.kp_pesel_entry.configure(background='light green')
        else:
            self.kp_pesel_entry.configure(background='pink')

    def sprawdz_pesel_zwrot(self, event):
        """Change PESEL background color to green if its have 11 signs, and to pink in other cases."""
        if len(self.kz_pesel_string.get()) == 11:
            self.kz_pesel_entry.configure(background='light green')
        else:
            self.kz_pesel_entry.configure(background='pink')

    def show_all(self):
        """Assigned to 'Poka?? wszystko' in 'pojazd'. Display all record from table 'pojazdy'."""
        self.pojazd_db_view.delete(*self.pojazd_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        for n in self.cursor.execute(""" SELECT * FROM pojazdy """):
            self.pojazd_db_view.insert("", tk.END, values=n)
        self.db.close()

    def show_all_kierowca(self):
        """Assigned to 'Poka?? wszystko' in 'kierowca'. Display all record from table 'kierowcy'."""
        self.kierowca_db_view.delete(*self.kierowca_db_view.get_children())
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        for n in self.cursor.execute(""" SELECT * FROM kierowcy """):
            self.kierowca_db_view.insert("", tk.END, values=n)
        self.db.close()

    def enable_frames(self, event):
        """Enable entries after choose operator"""
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
        """Enable and focus on 'Inna data' after check Checkbox"""
        if self.pp_data.get():
            self.pp_data_entry.config(state='normal')
            self.pp_data_entry.delete(0, "end")
            self.pp_data_entry.focus_set()
        # Disable and fill with valid date format when unchecked
        if not self.pp_data.get():
            self.pp_data_entry.delete(0, "end")
            self.pp_data_entry.insert(0, "RRRR-MM-DD")
            self.pp_data_entry.config(state="disabled")

    def pz_inna_data(self):
        """Enable and focus on 'Inna data' after check Checkbox"""
        if self.pz_data.get():
            self.pz_data_entry.config(state='normal')
            self.pz_data_entry.delete(0, "end")
            self.pz_data_entry.focus_set()
        # Disable and fill with valid date format when unchecked
        if not self.pz_data.get():
            self.pz_data_entry.delete(0, "end")
            self.pz_data_entry.insert(0, "RRRR-MM-DD")
            self.pz_data_entry.config(state="disabled")

    def kp_inna_data(self):
        """Enable and focus on 'Inna data' after check Checkbox"""
        if self.kp_data.get():
            self.kp_data_entry.config(state='normal')
            self.kp_data_entry.delete(0, "end")
            self.kp_data_entry.focus_set()
        # Disable and fill with valid date format when unchecked
        if not self.kp_data.get():
            self.kp_data_entry.delete(0, "end")
            self.kp_data_entry.insert(0, "RRRR-MM-DD")
            self.kp_data_entry.config(state="disabled")

    def kz_inna_data(self):
        """Enable and focus on 'Inna data' after check Checkbox"""
        if self.kz_data.get():
            self.kz_data_entry.config(state='normal')
            self.kz_data_entry.delete(0, "end")
            self.kz_data_entry.focus_set()
        # Disable and fill with valid date format when unchecked
        if not self.kz_data.get():
            self.kz_data_entry.delete(0, "end")
            self.kz_data_entry.insert(0, "RRRR-MM-DD")
            self.kz_data_entry.config(state="disabled")

    def check_tr(self, nr_rej):
        """Check if register plate number is valid"""
        pattern = re.compile(r"^[A-Z]{1,3}\s[A-Z\d]{3,5}$|^[A-Z]\d\s[A-Z\d]{3,5}$")
        if pattern.search(nr_rej):
            return True
        else:
            return False

    def pp_czy_dubel(self, tr):
        """Check if given register plate number exists in DB with no return date"""
        wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE tr = "{tr}" 
                                AND (data_zwrotu IS NULL OR data_zwrotu = "None" OR data_zwrotu = ""); """
        self.cursor.execute(wyszukanie_wpisu)
        if len(self.cursor.fetchall()) > 0:
            return True
        else:
            return False

    def format_inna_data(self, data):
        """Check if date format is valid"""
        format_daty = re.compile(r"^[1-2][019]\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[1-2]\d|3[0-1])$")
        if format_daty.search(data):
            return True
        else:
            return False

    def insert_pobranie_to_db(self, tr, data, osoba, prowadzacy, operator, uwagi):
        return f""" INSERT INTO pojazdy (tr, data_pobrania, osoba_pobranie, prowadzacy, operator_pobranie, uwagi) 
                                VALUES("{tr}", "{data}", "{osoba}", "{prowadzacy}", "{operator}", "{uwagi}"); """

    def clear_tr(self, *args):
        """Clear tr, pesel, imie, nazwisko and nr kk entries after save."""
        for arg in args:
            arg.delete(0, "end")
            if arg == self.kp_nr_kk_entry:
                arg.insert(0, 'B/U')

    def pp_potwierdzenie_zapisu(self, tr, data, pobierajacy, operator):
        """Check if record with given values exist in DB"""
        wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE tr = "{tr}" 
                                                        AND data_pobrania >= "{data}" 
                                                        AND osoba_pobranie = "{pobierajacy}" 
                                                        AND operator_pobranie = "{operator}" 
                                                        AND data_zwrotu IS NULL; """
        self.cursor.execute(wyszukanie_wpisu)
        # je??li tak to wy??wietla go w podgl??dzie i wy??wietla tekst potwierdzaj??cy zapisanie danych,
        if len(self.cursor.fetchall()) == 1:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.pojazd_db_view.insert("", 0, values=n)
            img = tk.PhotoImage(file="graphics/green_check.png")
            self.pp_potwierdzenie_label.configure(
                image=img,
                text=f"   Prawid??owo zapisano pobranie teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.pp_potwierdzenie_label.image = img
            self.clear_tr(self.pp_tablica_entry)
        # je??li nie to obrazek b????du i tekst o braku zapisu
        else:
            wrong = tk.PhotoImage(file='graphics/wrong.jpg')
            self.pp_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki o nr {tr}.",
                compound="left", font="Helvetica 8"
            )
            self.pp_potwierdzenie_label.image = wrong

    def pojazd_zastosuj_pobranie(self):
        """Apply record to DB"""
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
                return showerror("B????d", "Sprawd?? czy podana data jest prawid??owa. "
                                         "Pami??taj, aby wpisa?? j?? w formacie rrrr-mm-dd.")

        if self.pp_czy_dubel(teczka):
            return showerror("B????d", f"Teczka o nr '{teczka}' zosta??a ju?? pobrana i nie odnotowano jej zwrotu.")

        if teczka == "" or osoba == "" or prowadzacy == "":
            # Je??li nie wpisze si?? TR lub pobieraj??cego wyskoczy b????d.
            return showerror("B????d", "Pola  'Numer TR', 'Pobieraj??cy akta' i 'Osoba prowadz??ca spraw??' s?? obowi??zkowe!")

        elif self.check_tr(teczka):
            # Je??li nr TR jest poprawny ??? wstaw dane do bazy.
            self.cursor.execute(self.insert_pobranie_to_db(teczka, now, osoba, prowadzacy, operator, uwagi))
            self.db.commit()

        elif not self.check_tr(teczka):
            # Je??li nr TR jest b????dny poka?? zapytanie
            poprawna_tr = askyesno("B????d",
                                   f"Numer TR powinien sk??ada?? si?? z wyr????nika powiatu, ODST??PU i pojemno??ci.\n",
                                   detail=f"Czy '{teczka}' to na pewno poprawny numer rejestracyjny?")
            if poprawna_tr:
                # Po zatwierdzeniu wprowadzi dane do bazy
                self.cursor.execute(self.insert_pobranie_to_db(teczka, now, osoba, prowadzacy, operator, uwagi))
                self.db.commit()

        self.pp_potwierdzenie_zapisu(teczka, now, osoba, operator)
        self.db.close()

    def pojazd_potwierdzenie_zwrotu(self, tr, data, pobierajacy, operator):
        """Check if record with given values exists in DB"""
        wyszukanie_wpisu = f""" SELECT * FROM pojazdy WHERE tr = "{tr}" 
                                                        AND data_zwrotu >= "{data}" 
                                                        AND osoba_zwrot = "{pobierajacy}" 
                                                        AND operator_zwrot = "{operator}"; """
        self.cursor.execute(wyszukanie_wpisu)
        # Je??li tak to wy??wietla go w podgl??dzie i wy??wietla tekst potwierdzaj??cy zapisanie danych
        if len(self.cursor.fetchall()) >= 1:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.pojazd_db_view.insert("", 0, values=n)
            img = tk.PhotoImage(file="graphics/green_check.png")
            self.pz_potwierdzenie_label.configure(
                image=img,
                text=f"Prawid??owo odnotowano zwrot teczki o nr '{tr}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.pz_potwierdzenie_label.image = img
            self.clear_tr(self.pz_tablica_entry)
        else:
            wrong = tk.PhotoImage(file='graphics/wrong.jpg')
            self.pz_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki o nr {tr}.",
                compound="left", font="Helvetica 8"
            )
            self.pz_potwierdzenie_label.image = wrong

    def pojazd_zastosuj_zwrot(self):
        """Apply return"""
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
                return showerror("B????d", "Sprawd?? czy podana data jest prawid??owa. "
                                         "Pami??taj, aby wpisa?? j?? w formacie rrrr-mm-dd.")

        if teczka == "" or osoba == "":
            # Je??li nie wpisze si?? TR lub pobieraj??cego wyskoczy b????d
            return showerror("B????d", "Pola  'Numer TR' i 'Pobieraj??cy akta' s?? obowi??zkowe!")

        self.cursor.execute(f""" SELECT * FROM pojazdy WHERE 
                            (data_zwrotu IS NULL OR data_zwrotu = "None" OR data_zwrotu = "") AND tr = "{teczka}"; """)
        if len(self.cursor.fetchall()) == 0:
            showerror("B????d", f"Nie znaleziono niezwr??conej teczki o nr '{teczka}'.")
        else:
            self.cursor.execute(f""" UPDATE pojazdy 
                    SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", operator_zwrot = "{operator}" 
                    WHERE tr = "{teczka}" AND (data_zwrotu IS NULL OR data_zwrotu = "" OR data_zwrotu = "None"); """)
            self.db.commit()

        self.pojazd_potwierdzenie_zwrotu(teczka, now, osoba, operator)
        self.db.close()

    def kp_czy_dubel(self, pesel):
        """Check if given pesel exists in DB with no return date."""
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
        """Check if PESEL have 11 digits"""
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
        """Check if record with given values exist in DB"""
        keys = ['pesel', 'imie', 'nazwisko', 'data_pobrania', 'osoba_pobranie', 'operator_pobranie']
        values = [pesel, imie, nazwisko, data, pobierajacy, operator]
        warunki = {k: v for k, v in zip(keys, values)}
        sql = self.kierowca_select_query(**warunki)
        sql1 = sql[:-1] + " AND (data_zwrotu IS NULL OR data_zwrotu = '');"
        wyszukanie_wpisu = sql1
        if self.kp_zadanie_akt_var.get():
            wyszukanie_wpisu = sql[:-1] + " AND data_zwrotu = '????danie akt';"
        self.cursor.execute(wyszukanie_wpisu)
        # je??li tak to wy??wietla go w podgl??dzie i wy??wietla tekst potwierdzaj??cy zapisanie danych,
        if len(self.cursor.fetchall()) > 0:
            for n in self.cursor.execute(wyszukanie_wpisu):
                self.kierowca_db_view.insert("", 0, values=n)
            img = tk.PhotoImage(file="graphics/green_check.png")
            self.kp_potwierdzenie_label.configure(
                image=img,
                text=f"   Prawid??owo zapisano pobranie teczki osoby o "
                     f"nr PESEL: '{pesel}' przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.kp_potwierdzenie_label.image = img
            self.clear_tr(self.kp_pesel_entry, self.kp_imie_entry, self.kp_nazwisko_entry, self.kp_nr_kk_entry)
            self.kp_zadanie_akt_var.set(False)
        # je??li nie to obrazek b????du i tekst o braku zapisu
        else:
            wrong = tk.PhotoImage(file='graphics/wrong.jpg')
            self.kp_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki o nr PESEL: {pesel}.",
                compound="left", font="Helvetica 8"
            )
            self.kp_potwierdzenie_label.image = wrong

    def kierowca_zastosuj_pobranie(self):
        """Apply record to DB"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        pesel = self.kp_pesel_string.get()
        imie = self.kp_imie_entry.get().title()
        nazwisko = self.kp_nazwisko_entry.get().title()
        nr_kk = self.kp_nr_kk_entry.get()
        osoba = self.kp_osoba_combobox.get().title()
        prow = self.kp_prow_combobox.get().title()
        operator = self.operator_combobox.get().title()
        uwagi = self.kp_uwagi.get()
        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()

        # Check if birthdate checkbox is checked.
        if self.kp_data_ur_var.get():
            # Check if format of given date is valid.
            if self.format_inna_data(self.kp_data_ur_entry.get()):
                pesel = self.kp_data_ur_entry.get()
            else:
                return showerror("B????d", "Sprawd?? czy podana data urodzenia jest prawid??owa. "
                                         "Pami??taj, aby wpisa?? j?? w formacie rrrr-mm-dd.")
        if self.kp_data.get():
            if self.format_inna_data(self.kp_data_entry.get()):
                now = self.kp_data_entry.get() + ' 12:00'
            else:
                return showerror("B????d", "Sprawd?? czy podana data jest prawid??owa. "
                                         "Pami??taj, aby wpisa?? j?? w formacie rrrr-mm-dd.")

        if pesel == '' or osoba == '' or imie == '' or nazwisko == '':
            # Je??li nie wpisze si?? PESEL-u lub pobieraj??cego, lum imienia lub nazwiska wyskoczy b????d.
            return showinfo("B????d", "Pola 'PESEL', 'Imi??', 'Nazwisko' i 'Osoba pobieraj??ca' s?? obowi??zkowe!")

        elif self.kp_czy_dubel(pesel):
            return showwarning("Warning", f"Teczka osoby {imie} {nazwisko} o nr PESEL: '{pesel}' "
                                          f"zosta??a ju?? pobrana i nie odnotowano jej zwrotu.")

        elif self.check_pesel(pesel):
            # Je??li nr PESEL jest poprawny ??? wstaw dane do bazy
            self.cursor.execute(
                self.insert_kierowca_pobranie_to_db(pesel, imie, nazwisko, nr_kk, now, osoba, prow, operator, uwagi)
            )
            self.db.commit()

        elif not self.check_pesel(pesel):
            # Je??li nr PESEL jest b????dny, poka?? zapytanie.
            poprawny_pesel = askyesno("B????d",
                                      f"Numer PESEL powinien sk??ada?? si?? z 11 cyfr.\n"
                                      f"Czy nr PESEL: '{pesel}' jest prawid??owy?")
            if poprawny_pesel:
                # Po zatwierdzeniu wprowadzi dane do bazy.
                self.cursor.execute(
                    self.insert_kierowca_pobranie_to_db(pesel, imie, nazwisko, nr_kk, now, osoba, prow, operator,
                                                        uwagi))
                self.db.commit()

        if self.kp_zadanie_akt_var.get():
            self.cursor.execute(
                f'UPDATE kierowcy SET data_zwrotu = "????danie akt" WHERE pesel = "{pesel}" AND data_pobrania = "{now}";')
            self.db.commit()

        self.kp_potwierdzenie_zapisu(pesel, imie, nazwisko, now, osoba, operator)

        self.db.close()

    def kierowca_potwierdzenie_zwrotu(self, pesel, nr_kk, data, pobierajacy, operator):
        # Funkcja wyszukuje czy podana teczka wyst??puje z podan?? dat?? zwrotu.
        # Je??li tak to wy??wietla go w podgl??dzie i wy??wietla tekst potwierdzaj??cy zapisanie danych.
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
            img = tk.PhotoImage(file="graphics/green_check.png")
            self.kz_potwierdzenie_label.configure(
                image=img,
                text=f"Prawid??owo odnotowano zwrot teczki osoby o nr {text} przez pracownika {pobierajacy}.",
                compound="left", font="Helvetica 8"
            )
            self.kz_potwierdzenie_label.image = img
            self.clear_tr(self.kz_pesel_entry, self.kz_nr_kk_entry)
            self.kz_dane.config(text="")
        else:
            wrong = tk.PhotoImage(file='graphics/wrong.jpg')
            self.kz_potwierdzenie_label.configure(
                image=wrong,
                text=f"   Nie dokonano zapisu teczki osoby o nr {text}.",
                compound="left", font="Helvetica 8"
            )
            self.kz_potwierdzenie_label.image = wrong

    def kierowca_zastosuj_zwrot(self):
        """Apply return"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        pesel = self.kz_pesel_string.get()
        nr_kk = self.kz_nr_kk_entry.get()
        osoba = self.kz_osoba_combobox.get().title()
        operator = self.operator_combobox.get().title()

        with sqlite3.connect('archeo.db') as self.db:
            self.cursor = self.db.cursor()
        # Je??li zaznaczona 'Inna data' sprawd?? format, je??li jest dobry ustaw jako 'now' je??li nie 'showerror'.
        if self.kz_data.get():
            if self.format_inna_data(self.kz_data_entry.get()):
                now = self.kz_data_entry.get() + ' 12:00'
            else:
                return showerror("B????d", "Sprawd?? czy podana data jest prawid??owa. "
                                         "Pami??taj, aby wpisa?? j?? w formacie rrrr-mm-dd.")

        if pesel == "":
            if nr_kk == "":
                # Je??li nie wpisze si?? PESEL-u lub nr 'KK', wyskoczy b????d.
                return showerror("B????d", "Pole 'PESEL' lub 'nr KK' jest obowi??zkowe!. "
                                         "W przypadku braku nr PESEL podaj dat?? urodzenia.")
        if osoba == "":
            return showerror("B????d", "Pole 'Osoba zwracaj??ca' jest obowi??zkowe!")

        keys = ['pesel', 'nr_kk']
        values = [pesel, nr_kk]
        warunki = {k: v for k, v in zip(keys, values)}
        sql = self.kierowca_select_query(**warunki)
        sql = sql[:-1] + " AND (data_zwrotu IS NULL OR data_zwrotu = '' OR data_zwrotu = 'None');"
        db_id = f'{sql[:7]}id{sql[8:-1]}'

        self.cursor.execute(sql)
        if len(self.cursor.fetchall()) == 0:
            # Je??li nie znajdzie wpisu z podanym nr PESEL i 'KK' wyszuka wpis z podanym PESEL i nr 'KK' = 'B/U'.
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
                             f"Nie znaleziono niezwr??conej teczki osoby o nr PESEL: '{pesel}' i nr kk {nr_kk}.")
            elif pesel:
                showinfo("Informacja", f"Nie znaleziono niezwr??conej teczki osoby o nr PESEL: '{pesel}'.")
            else:
                showinfo("Informacja", f"Nie znaleziono niezwr??conej teczki osoby o nr kk: '{nr_kk}'.")
        else:
            # Je??li podany tylko PESEL lub nr 'KK' zaktualizuje t?? pozycj?? o zwrot.
            self.cursor.execute(f""" UPDATE kierowcy 
            SET data_zwrotu = "{now}", osoba_zwrot = "{osoba}", operator_zwrot = "{operator}" 
            WHERE id = ({db_id}); """)
            self.db.commit()

        self.kierowca_potwierdzenie_zwrotu(pesel, nr_kk, now, osoba, operator)
        self.db.close()

    def operator_edit_window(self):
        """ Okno edycji operator??w """
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja operator??w")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Operator', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Operator', text='Operator', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usu??', command=self.delete_operator)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj operatora")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imi?? i nazwisko')
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
        """ Remove elements from list of operators
            'Opcje' -> 'Edytuj operator??w' -> 'Usu??'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        plik.close()
        lista = osoby['operator']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'operator'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usuni??cie z listy osoby zaznaczonej w widoku
            nowa_lista = {'operator': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'operator'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, ??eby wyzerowa?? zawarto????
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.operator_values = osoby['operator']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.operator_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.operator_combobox.config(values=self.operator_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij inne okna i spr??buj ponownie')

    def add_operator(self):
        """ Add elements to the list of operators
            'Opcje' -> 'Edytuj operator??w' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        lista = osoby['operator']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'operator'

        try:
            oper = self.dodaj_entry.get()
            lista.append(oper)  # Dodanie do listy osoby wpisanej przez u??ytkownika
            nowa_lista = {'operator': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'operator'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisa??o warto????, a nie doda??o now?? na koniec.
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.operator_values = osoby['operator']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.operator_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.operator_combobox.config(values=self.operator_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij wszystkie okna i spr??buj ponownie')

    def osoba_pojazd_edit_window(self):
        """ Okno edycji os??b pobieraj??cy/zwracaj??cych teczki pojazd??w"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja os??b pobieraj??cych akta pojazdu")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Operator', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Operator', text='Operator', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usu??', command=self.delete_pojazd_osoba)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj operatora")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imi?? i nazwisko')
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
            'Opcje' -> 'Edytuj osoby - Pojazd' -> 'Usu??'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        plik.close()
        lista = osoby['pojazd']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'pojazd'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usuni??cie z listy osoby zaznaczonej w widoku
            nowa_lista = {'pojazd': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, ??eby wyzerowa?? zawarto????
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.pp_osoba_values = osoby['pojazd']
            self.pz_osoba_values = osoby['pojazd']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_osoba_combobox.config(values=self.pp_osoba_values)
            self.pz_osoba_combobox.config(values=self.pz_osoba_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij inne okna i spr??buj ponownie')

    def add_pojazd_osoba(self):
        """ Adding elements to the list of operators
            'Opcje' -> 'Edytuj osoby - Pojazd' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        lista = osoby['pojazd']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'pojazd'
        try:
            oper = self.dodaj_entry.get()

            lista.append(oper)  # Dodanie do listy osoby wpisanej przez u??ytkownika
            nowa_lista = {'pojazd': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisa??o warto????, a nie doda??o now?? na koniec.
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

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
            showerror('B????d', 'Zamknij wszystkie okna i spr??buj ponownie')

    def osoba_kierowca_edit_window(self):
        """ Okno edycji os??b pobieraj??cy/zwracaj??cych teczki kierowc??w"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja os??b pobieraj??cych akta kierowcy")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Operator', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Operator', text='Operator', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usu??', command=self.delete_kierowca_osoba)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj osob??")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imi?? i nazwisko')
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
            'Opcje' -> 'Edytuj osoby - Kierowca' -> 'Usu??'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        plik.close()
        lista = osoby['kierowca']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'kierowca'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usuni??cie z listy osoby zaznaczonej w widoku
            nowa_lista = {'kierowca': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'kierowca'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, ??eby wyzerowa?? zawarto????
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.kp_osoba_values = osoby['kierowca']
            self.kz_osoba_values = osoby['kierowca']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_osoba_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_osoba_combobox.config(values=self.kp_osoba_values)
            self.kz_osoba_combobox.config(values=self.kz_osoba_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij inne okna i spr??buj ponownie')

    def add_kierowca_osoba(self):
        """ Function to adding elements to the list of operators
            'Opcje' -> 'Edytuj osoby - Kierowca' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        lista = osoby['kierowca']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'pojazd'
        try:
            oper = self.dodaj_entry.get()

            lista.append(oper)  # Dodanie do listy osoby wpisanej przez u??ytkownika
            nowa_lista = {'kierowca': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisa??o warto????, a nie doda??o now?? na koniec
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

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
            showerror('B????d', 'Zamknij wszystkie okna i spr??buj ponownie')

    def prowadzacy_kierowca_edit_window(self):
        """ Okno edycji os??b prowadz??cych sprawy kierowc??w"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja os??b prowadz??cych spraw?? kierowc??w")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Prowadz??cy', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Prowadz??cy', text='Prowadz??cy', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usu??', command=self.delete_kierowca_prowadzacy)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj osob??")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imi?? i nazwisko')
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
            'Opcje' -> 'Edytuj prowadz??cych - Kierowca' -> 'Usu??'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        plik.close()
        lista = osoby['prowadzacy_kier']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'prowadzacy_kier'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usuni??cie z listy osoby zaznaczonej w widoku
            nowa_lista = {'prowadzacy_kier': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'kierowca'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, ??eby wyzerowa?? zawarto????
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.kp_prow_values = osoby['prowadzacy_kier']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_prow_combobox.config(values=self.kp_prow_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij inne okna i spr??buj ponownie')

    def add_kierowca_prowadzacy(self):
        """ Function to adding elements to the list of operators
            'Opcje' -> 'Edytuj prowadz??cych - Kierowca' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        lista = osoby['prowadzacy_kier']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'prowadzacy_kier'
        try:
            oper = self.dodaj_entry.get()
            lista.append(oper)  # Dodanie do listy osoby wpisanej przez u??ytkownika
            nowa_lista = {'prowadzacy_kier': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'prowadzacy_kier'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisa??o warto????, a nie doda??o now?? na koniec
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.kp_prow_values = osoby['prowadzacy_kier']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.kp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.kp_prow_combobox.config(values=self.kp_prow_values)
            self.szukaj_kierowca_prowadzacy_entry.config(values=self.kp_prow_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij wszystkie okna i spr??buj ponownie')

    def prowadzacy_pojazd_edit_window(self):
        """ Okno edycji os??b prowadz??cych sprawy pojazd??w"""
        self.window = tk.Toplevel(self.root)
        self.window.title("Edycja os??b prowadz??cych spraw?? pojazd??w")
        self.window.attributes('-topmost', 1)
        self.window.geometry('400x450+400+400')

        self.lista_operatorow = ttk.Treeview(self.window, columns='Prowadz??cy', height=8, show='headings')
        self.lista_operatorow.grid(column=0, row=0, pady=20, sticky='WE', padx=100)
        self.lista_operatorow.heading(column='Prowadz??cy', text='Prowadz??cy', anchor='center')

        self.delete_button = ttk.Button(self.window, text='Usu??', command=self.delete_pojazd_prowadzacy)
        self.delete_button.grid(column=0, row=1, padx=50, pady=5)

        self.dodaj_frame = ttk.LabelFrame(self.window, text="Dodaj osob??")
        self.dodaj_frame.grid(column=0, row=2, pady=10)

        self.dodaj_label = ttk.Label(self.dodaj_frame, text='Imi?? i nazwisko')
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
            'Opcje' -> 'Edytuj prowadz??cych - Kierowca' -> 'Usu??'
        """
        plik = open('osoby.json', mode='r')  # Otwarcie jsona w trybie odczytu
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        plik.close()
        lista = osoby['prowadzacy']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'prowadzacy'
        try:
            for item in self.lista_operatorow.selection():
                values = self.lista_operatorow.item(item, 'values')  # krotka z danymi z zaznaczonego elementu
            lista.remove(values[0])  # Usuni??cie z listy osoby zaznaczonej w widoku
            nowa_lista = {'prowadzacy': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'pojazd'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik = open('osoby.json', mode='w+')  # Otwarcie pliku w trybie zapisu, ??eby wyzerowa?? zawarto????
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.pp_prow_values = osoby['prowadzacy']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_prow_combobox.config(values=self.pp_prow_values)
            self.szukaj_pojazd_prowadzacy_entry.config(values=self.pp_prow_values)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij inne okna i spr??buj ponownie')

    def add_pojazd_prowadzacy(self):
        """ Function to adding elements to the list of operators
            'Opcje' -> 'Edytuj prowadz??cych - Kierowca' -> 'Dodaj'
        """
        plik = open('osoby.json', mode='r+')  # Otwarcie jsona w trybie zapis + odczyt
        osoby = json.load(plik)  # Przypisanie do zmiennej zawarto??ci pliku
        lista = osoby['prowadzacy']  # Przypisanie do zmiennej 'lista' listy os??b z klucza 'prowadzacy'
        try:
            oper = self.dodaj_entry.get()
            lista.append(oper)  # Dodanie do listy osoby wpisanej przez u??ytkownika
            nowa_lista = {'prowadzacy': lista}  # Przypisanie do zmiennej nowej warto??ci klucza 'prowadzacy'
            osoby.update(nowa_lista)  # Aktualizacja zawarto??ci pliku
            plik.seek(0)  # Ustawienie pozycji, aby nadpisa??o warto????, a nie doda??o now?? na koniec.
            json.dump(osoby, plik)  # zapisanie w pliku json zmienionych warto??ci

            self.pp_prow_values = osoby['prowadzacy']
            self.lista_operatorow.delete(*self.lista_operatorow.get_children())
            for name in self.pp_prow_values:
                self.lista_operatorow.insert("", tk.END, values=[name])
            self.pp_prow_combobox.config(values=self.pp_prow_values)
            self.szukaj_pojazd_prowadzacy_entry.config(values=self.pp_prow_values)
            self.dodaj_entry.delete(0, tk.END)

            plik.close()
        except (_tkinter.TclError, UnboundLocalError, ValueError):
            showerror('B????d', 'Zamknij wszystkie okna i spr??buj ponownie')

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

        info_label2 = tk.Label(window, text='1.2')
        info_label4 = tk.Label(window, text='Martin Brzezi??ski')
        info_label6 = tk.Label(window, text='1 pa??dziernika 2022')
        info_label8 = tk.Label(window, text='28 listopada 2022')
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
        list_diff = [t2 - data for data in list_time]  # Lista z r????nicami dat z zapytania a dat?? aktualn??
        sum = timedelta(0)
        for data in list_diff:  # Suma wszystkich r????nic dat
            sum += data
        avg_time = sum / len(list_diff)  # ??rednia r????nica mi??dzy dat?? pobrania a teraz.

        # @@@@@@@@@@@@@@@@@@ STATYSTYKI KIEROWCY @@@@@@@@@@@@@@
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
        list_diff2 = [t2 - data for data in list_time2]  # Lista z r????nicami dat z zapytania a dat?? aktualn??
        sum2 = timedelta(0)
        for data in list_diff2:  # Suma wszystkich r????nic dat
            sum2 += data
        avg_time2 = sum2 / len(list_diff2)  # ??rednia r????nica mi??dzy dat?? pobrania a teraz.

        self.db.close()

        info_label1 = tk.Label(self.window, text='Suma rekord??w:')
        info_label3 = tk.Label(self.window, text='Suma niezwr??conych teczek:')
        info_label5 = tk.Label(self.window, text='Maksymalny czas przetrzymywania teczki:')
        info_label7 = tk.Label(self.window, text='??redni czas przetrzymywania teczki:')

        info_label10 = tk.Label(self.window, text='Suma rekord??w:')
        info_label30 = tk.Label(self.window, text='Suma niezwr??conych teczek:')
        info_label50 = tk.Label(self.window, text='Maksymalny czas przetrzymywania teczki:')
        info_label70 = tk.Label(self.window, text='??redni czas przetrzymywania teczki:')

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
    """This class create new window to edit records in DB in 'kierowcy' table"""
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
                  'imie': 'Imi??',
                  'nr_kk': 'nr_kk',
                  'data_pob': 'Data pobrania',
                  'osoba_pob': 'Pobieraj??cy',
                  'prowadzacy': 'Prowadz??cy spraw??',
                  'operator_pob': 'Operator Pobranie',
                  'data_zw': 'Data zwrotu',
                  'osoba_zw': 'Zwracaj??cy',
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

        self.edycja_delete_button = ttk.Button(self.root, text='Usu??', command=self.delete)
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
            showinfo('Zapisano', 'Wprowadzone zmiany zosta??y zapisane.')
            self.root.destroy()
        except Exception as E:
            showerror('B????d', 'Wyst??pi?? nieoczekiwany b????d. Spr??buj ponownie.', details=f'{E}')

    def delete(self):
        potwierdzenie = askyesno('Ostrze??enie!', 'Usuwasz wpis z bazy danych, ta czynno???? jest NIEODWRACALNA!\n',
                                 detail='Czy na pewno chcesz usun???? ten wpis?')
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
                showinfo('Usuni??to', 'Zaznaczony wpis zosta?? usuni??ty z bazy danych.')
                self.root.destroy()
            except Exception as E:
                showerror('B????d', 'Wyst??pi?? nieoczekiwany b????d. Spr??buj ponownie.', detail=f'{E}')

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
    """This class create new window to edit records in DB in 'pojazdy' table"""
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
                  'osoba_pobranie': 'Pobieraj??cy',
                  'prowadzacy': 'Prowadz??cy spraw??',
                  'operator_pobranie': 'Operator pobranie',
                  'data_zwrotu': 'Data zwrotu',
                  'osoba_zwrot': 'Zwracaj??cy',
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

        self.edycja_delete_button = ttk.Button(self.root, text='Usu??', command=self.delete)
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
            showinfo('Zapisano', 'Wprowadzone zmiany zosta??y zapisane.')
            self.root.destroy()
        except Exception as E:
            showerror('B????d', 'Wyst??pi?? nieoczekiwany b????d. Spr??buj ponownie.', details=f'{E}')

    def delete(self):
        potwierdzenie = askyesno('Ostrze??enie!', 'Usuwasz wpis z bazy danych, ta czynno???? jest NIEODWRACALNA!\n',
                                 detail='Czy na pewno chcesz usun???? ten wpis?')
        if potwierdzenie:
            try:
                sql = self.sql_delete('pojazdy')
                with sqlite3.connect('archeo.db') as self.db:
                    self.cursor = self.db.cursor()
                self.cursor.execute(sql)
                self.db.commit()
                self.db.close()
                self.root.lower()
                showinfo('Usuni??to', 'Zaznaczony wpis zosta?? usuni??ty z bazy danych.')
                self.root.destroy()
            except Exception as E:
                showerror('B????d', 'Wyst??pi?? nieoczekiwany b????d. Spr??buj ponownie.', detail=f'{E}')

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


# Create copy of DB in light version location for read-only users
try:
    size1 = os.path.getsize('archeo.db')  # Rozmiar oryginalnej bazy danych.
    size2 = os.path.getsize(r'\\fs1spp\kierowca\DB\archeo.db')  # Rozmiar kopii bazy danych.
    time1 = os.path.getmtime('archeo.db')  # Data modyfikacji oryg. bazy danych
    time2 = os.path.getmtime(r'\\fs1spp\kierowca\DB\archeo.db')  # Data modyfikacji kopii bazy danych.

    # Utworzenie kopii bazy danych dla wyszukiwarki w folderze kierowca.
    original = r'archeo.db'
    # target = r'W:\DB\archeo.db'
    target = r'\\fs1spp\kierowca\DB\archeo.db'
    if time1 > time2 and size1 > size2:
        shutil.copyfile(original, target)
except Exception as E:
    showerror('B????d', 'Wyst??pi?? problem ze skopiowaniem bazy danych do folderu "kierowca".', detail=f'{E}')


if __name__ == '__main__':
    app = App()
