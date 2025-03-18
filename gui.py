import tkinter as tk
# tkinter._test()

# Initiate GUI window
window = tk.Tk()
window.title('Autocompleter GUI')
window.geometry("690x420")

L1 = tk.Label(window, text="Select autocompletion engine:").grid(row=0)
# L1.pack(side=LEFT)

Lb1 = tk.Listbox(window, height=3)
Lb1.insert(1, "Word autocompleter")
Lb1.insert(2, "Sentence autocompleter")
Lb1.insert(3, "Melody autocompleter")
Lb1.grid(row=0, column=1)

# Code to add widgets
L2 = tk.Label(window, text="Text to autocomplete:")
L2.grid(row=1, column=0)
E1 = tk.Entry(window, bd=5)
E1.grid(row=1, column=1)

def give_back_text():
    print(L2)

B1 = tk.Button(window, text="Run Autocompleter", command=give_back_text).grid(row=2, column=2)

# Enter main event loop to take input from user and act on it
window.mainloop()