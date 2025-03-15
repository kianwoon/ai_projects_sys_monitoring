import tkinter as tk

root = tk.Tk()
root.title("Test Window")

# Omit bg/fg, let macOS/Tk choose defaults
label = tk.Label(root, text="Hello from Tkinter!", font=("Helvetica", 16))
label.pack(padx=50, pady=50)

root.mainloop()
