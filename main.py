import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Archeo 2022")
root.attributes("-topmost", 1)

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

left_frame = ttk.LabelFrame(root, text="aaa")
separator_frame = ttk.Frame(root)
right_frame = ttk.LabelFrame(root, text="bbb")

left_frame.grid(column=0, row=5)
separator_frame.grid(column=1, row=5)
right_frame.grid(column=2, row=5)

# SEPARATOR FRAME
'''
Wstawienie separatora jako widget osobnego frame'a
vertical_separator = ttk.Separator(
    separator_frame,
    orient="vertical",
    cursor="man",
    )

vertical_separator.grid(ipady=200, pady=10)'''

ttk.Separator(
    root,
    orient="vertical",
    style='yellow.TSeparator'
).place(x=window_width/2, y=100, relheight=0.7)

# LEFT FRAME
pobranie_label = ttk.Label(left_frame, text="Pobranie AKT", background="yellow")
pobranie_label.grid(column=0, row=0, sticky="N", pady=50)

pobranie_label2 = ttk.Label(left_frame, text="Pobranie AKT")
pobranie_label2.grid(column=0, row=1, sticky="N", pady=50)


pobranie_label3 = ttk.Label(left_frame, text="Pobranie AKT")
pobranie_label3.grid(column=0, row=2, sticky="N", pady=100)


# RIGHT FRAME
zwrot_label = ttk.Label(right_frame,
                        text="Zwrot AKT",
                        background="pink",
                        )

zwrot_label.grid(column=0, row=0, sticky="NE", ipadx=50)

# HORIZONTAL SEPARATOR
horizontal_separator = ttk.Separator(root,
                                     orient="horizontal",
                                     cursor="man",
                                     )

horizontal_separator.grid(columnspan=3, row=8, ipadx=200, padx=10)

#CLOSE BUTTON
zamknij_button = ttk.Button(root, text="Zamknij", command=lambda: root.quit())
zamknij_button.grid(column=1, row=10, sticky="WE")
root.mainloop()

# TEST COMMIT