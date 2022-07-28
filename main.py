import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Archeo 2022")
root.attributes("-topmost", 1)


def zastosuj_pobranie():
    pass


def zastosuj_zwrot():
    pass


# WINDOW SIZE & LOCATION
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = int(screen_width * 0.8)
window_height = int(screen_height * 0.80)

center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 1.8)

root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(True, True)

# CONFIGURE THE GRID
root.columnconfigure(0, weight=3)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=3)

# WELCOME LABEL
welcome_label = ttk.Label(
    root,
    text="Witaj w Archeo 2022!",
    background="green",
    foreground="white",
    font="Arial 15 bold",
    anchor="center",
)

welcome_label.grid(columnspan=3, row=0, sticky="WE", pady=5, ipady=5)

# COMBOBOX FRAME
combobox_frame = ttk.Frame(
    root,
    borderwidth=15,
)

combobox_frame.grid(columnspan=3, row=3, )

# LABEL & COMBOBOX IN COMBOBOX FRAME - SELECT OPERATOR
combobox_label = ttk.Label(
    combobox_frame,
    text="Wybierz operatora:",
    background="blue",
    foreground="white",
    font="Arial 13"
)

selected_operator = tk.StringVar()
combobox_operator = ttk.Combobox(combobox_frame,
                                 textvariable=selected_operator,
                                 )

combobox_operator["values"] = ["Arkadiusz Wieloch",
                               "Barbara Naruszewicz",
                               "Dorota Sikora",
                               ]

combobox_label.grid(column=0, row=0, sticky="E")
combobox_operator.grid(column=1, row=0, sticky="W")

# CENTER FRAMES

left_frame = ttk.LabelFrame(root, text="Pobranie akt")
left_frame.columnconfigure(0, minsize=100)
left_frame.columnconfigure(1, weight=1)
left_frame.columnconfigure(2, weight=1)
left_frame.columnconfigure(3, minsize=100)

separator_frame = ttk.Frame(root)

right_frame = ttk.LabelFrame(root, text="Zwrot akt")
right_frame.columnconfigure(0, minsize=100)
right_frame.columnconfigure(1, weight=1)
right_frame.columnconfigure(2, weight=1)
right_frame.columnconfigure(3, minsize=100)

left_frame.grid(column=0, row=5, sticky="E")
separator_frame.grid(column=1, row=5)
right_frame.grid(column=2, row=5, sticky="W")

# SEPARATOR FRAME
vertical_separator = ttk.Separator(
    separator_frame,
    orient="vertical",
    cursor="man",
)

vertical_separator.grid(pady=10, ipady=100)

# LEFT FRAME
pobranie_label = ttk.Label(left_frame, text="Numer TR:", background="yellow")

pobrana_teczka = tk.StringVar()
pobranie_entry = ttk.Entry(left_frame, textvariable=pobrana_teczka)

pobierajacy_label = ttk.Label(left_frame, text="Pobierający akta:")

selected_pobierajacy = tk.StringVar()
combobox_pobierajacy = ttk.Combobox(left_frame,
                                    textvariable=selected_pobierajacy,
                                    )

combobox_pobierajacy["values"] = ["Błażej Prajs",
                                  "Marzena Ciszek",
                                  "Wojciech Kaczmarek",
                                  ]

zastosuj_pobranie_button = ttk.Button(left_frame, text="Zastosuj", command=zastosuj_pobranie)

pobranie_label.grid(column=1, row=1, sticky="E", pady=30)
pobranie_entry.grid(column=2, row=1, sticky="W")
pobierajacy_label.grid(column=1, row=2, sticky="E", pady=20)
combobox_pobierajacy.grid(column=2, row=2, sticky="W")
zastosuj_pobranie_button.grid(column=1, columnspan=2, row=3, sticky="WE", pady=5)

# RIGHT FRAME
zwrot_label = ttk.Label(right_frame,
                        text="Numer TR",
                        background="pink",
                        )

zwracana_teczka = tk.StringVar()
zwrot_entry = ttk.Entry(right_frame,
                        textvariable=zwracana_teczka,
                        )

zwracajacy_label = ttk.Label(right_frame, text="Zwracający akta:")

selected_zwracajacy = tk.StringVar()
combobox_zwracajacy = ttk.Combobox(right_frame, textvariable=selected_zwracajacy)

combobox_zwracajacy["values"] = ["Błażej Prajs",
                                 "Marzena Ciszek",
                                 "Wojciech Kaczmarek",
                                 ]

zastosuj_zwrot_button = ttk.Button(right_frame, text="Zastosuj", command=zastosuj_zwrot)

zwrot_label.grid(column=1, row=0, sticky="E", pady=30)
zwrot_entry.grid(column=2, row=0, sticky="W")
zwracajacy_label.grid(column=1, row=1, sticky="E", pady=20)
combobox_zwracajacy.grid(column=2, row=1, sticky="W")
zastosuj_zwrot_button.grid(column=1, columnspan=2, row=2, pady=5, sticky="WE")

# HORIZONTAL SEPARATOR
horizontal_separator = ttk.Separator(root,
                                     orient="horizontal",
                                     cursor="man",
                                     )

horizontal_separator.grid(columnspan=3,
                          row=8,
                          ipadx=window_width,
                          pady=15,
                          )

# TEXT AREA
archeo_data = tk.Text(root, height=10)

archeo_data.grid(columnspan=3, row=10, padx=10, pady=10, ipady=50, ipadx=100)

# CLOSE BUTTON
zamknij_button = ttk.Button(root, text="Zamknij", command=lambda: root.quit())
zamknij_button.grid(column=1, row=12, sticky="WE", padx=10, pady=10)

root.mainloop()
