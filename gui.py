from tkinter import Tk, Button, Frame, Entry, LEFT, RIGHT, Label, Listbox
# tkinter._test()

# Initiate GUI window
top = Tk()
top.title('Autocompleter GUI')

L1 = Label(top, text="Select autocompletion engine:")
L1.pack(side = LEFT)

Lb1 = Listbox(top, height=3)
Lb1.insert(1, "Word autocompleter")
Lb1.insert(2, "Sentence autocompleter")
Lb1.insert(3, "Melody autocompleter")

Lb1.pack()

# Code to add widgets
L2 = Label(top, text="Text to autocomplete:")
L2.pack(side = LEFT)
E1 = Entry(top, bd =5)
E1.pack(side = RIGHT)

# Enter main event loop to take input from user and act on it
top.mainloop()