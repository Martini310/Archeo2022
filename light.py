import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import sqlite3
import json


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Archeo 2022')
        self.icon = tk.PhotoImage(file='graphics/ikona2.png')
        self.root.iconphoto(True, self.icon)

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
        self.file_menu.add_command(label='Zamknij', command=self.root.destroy)

        self.menubar.add_cascade(label='Menu', menu=self.file_menu)
        # self.menubar.add_cascade(label='Opcje', menu=self.help_menu, state='disabled')

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

        # NOTEBOOK WIDGET
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.wyszukiwanie = tk.Frame(self.notebook)

        self.wyszukiwanie.pack(fill="both", expand=True)

        self.notebook.add(self.wyszukiwanie, text="Wyszukiwanie")

        # # Osoba pobierająca
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.pp_osoba_values = obj['pojazd']
        osoby_json.close()

        # # Osoba prowadząca sprawę
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.pp_prow_values = obj['prowadzacy']
        osoby_json.close()

        # # Osoba Pobierająca
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.kp_osoba_values = obj['kierowca']
        osoby_json.close()

        # # Osoba prowadząca sprawę
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.kp_prow_values = obj['prowadzacy_kier']
        osoby_json.close()

        # # Osoba zwracająca
        osoby_json = open('osoby.json')
        obj = json.load(osoby_json)
        self.kz_osoba_values = obj['kierowca']
        osoby_json.close()


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

        # Prowadzący sprawę
        self.szukaj_pojazd_prowadzacy_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                        text='     Prowadzący sprawę:',
                                                        font='Arial 10')
        self.szukaj_pojazd_prowadzacy_label.grid(column=2, row=0)

        self.szukaj_pojazd_prowadzacy_entry = ttk.Combobox(self.wyszukaj_pojazd_frame, values=self.pp_prow_values)
        self.szukaj_pojazd_prowadzacy_entry.grid(column=3, row=0)

        # Osoba pobierająca
        self.szukaj_pojazd_osoba_pobranie_label = ttk.Label(self.wyszukaj_pojazd_frame,
                                                            text='     Osoba pobierająca:',
                                                            font='Arial 10')
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

        self.szukaj_edytuj_button = tk.Button(self.szukaj_przyciski_frame,
                                              text='Edytuj',
                                              state='disabled')
        self.szukaj_edytuj_button.grid(column=1, row=0, padx=20, ipadx=10, pady=5)

        self.szukaj_wyczysc_button = tk.Button(self.szukaj_przyciski_frame, text='Wyczyść', command=self.clear_entries)
        self.szukaj_wyczysc_button.grid(column=2, row=0, padx=20, ipadx=10, pady=5)

        self.tylko_niezwr_var = tk.BooleanVar()
        self.tylko_niezwr = ttk.Checkbutton(self.szukaj_przyciski_frame, text='Tylko niezwrócone',
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
            "id", "TR", "Data pobrania", "Pobierający", "Prowadzący sprawę", "Operator - pobranie", "Data zwrotu",
            "Zwracający", "Operator - zwrot", "Uwagi")
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
        self.szukaj_kierowca_db_columns = ('id', 'PESEL', 'Nazwisko', 'Imię', 'nr_kk', 'Data pobrania', 'Pobierający',
                                           'Prowadzący sprawę', 'Operator pobranie', 'Data zwrotu', 'Zwracający',
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
        self.szukaj_kierowca_db_view.column('Imię', width=120)

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
        self.informacja_label = tk.Label(self.wyszukiwanie, text=f"Liczba znalezionych wyników: {suma_wyniki}")
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
        # Selected KIEROWCA
        else:
            self.wyszukaj_pojazd_frame.grid_forget()  # forget pojazd search inputs
            self.szukaj_pojazd_db_view.grid_forget()  # forget pojazd results table
            self.wyszukaj_kierowca_frame.grid(column=0, row=0)  # set kierowca search inputs
            self.szukaj_kierowca_db_view.grid(column=0, row=4, sticky='NEWS', padx=10)  # set kierowca res tab
            self.szukaj_wyszukaj_button.configure(command=self.wyszukaj_kierowca_click)  # set search button command
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

        info_label2 = tk.Label(window, text='1.5')
        info_label4 = tk.Label(window, text='Martin Brzeziński')
        info_label6 = tk.Label(window, text='1 października 2022')
        info_label8 = tk.Label(window, text='14 czerwca 2022')
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


if __name__ == '__main__':
    app = App()
