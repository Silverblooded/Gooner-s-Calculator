import tkinter as tk
from PIL import Image, ImageTk
import os

class GoonersCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gooner's Calculator")
        self.root.geometry("300x400")
        self.root.configure(bg="#1e1e1e")

        self.expression = ""
        self.selected_theme = tk.StringVar()
        self.border_img = None

        self.canvas = tk.Canvas(self.root, width=300, height=400)
        self.canvas.pack(fill="both", expand=True)

        self.create_widgets()
        self.load_border_image("default_border.png")

    def create_widgets(self):
        self.display = tk.Entry(self.root, font=("Consolas", 20), bd=5, relief=tk.RIDGE, justify="right")
        self.canvas.create_window(150, 50, window=self.display, width=260, height=40)

        # Button layout
        buttons = [
            ('7', 100, 100), ('8', 150, 100), ('9', 200, 100), ('/', 250, 100),
            ('4', 100, 150), ('5', 150, 150), ('6', 200, 150), ('*', 250, 150),
            ('1', 100, 200), ('2', 150, 200), ('3', 200, 200), ('-', 250, 200),
            ('C', 100, 250), ('0', 150, 250), ('=', 200, 250), ('+', 250, 250),
        ]
        for (text, x, y) in buttons:
            btn = tk.Button(self.root, text=text, width=4, height=1, font=("Arial", 14),
                            command=lambda t=text: self.on_click(t))
            self.canvas.create_window(x, y, window=btn)

        # Theme dropdown
        themes = [f for f in os.listdir("themes") if f.endswith(".png")]
        if themes:
            self.selected_theme.set(themes[0])
            dropdown = tk.OptionMenu(self.root, self.selected_theme, *themes, command=self.change_theme)
            self.canvas.create_window(150, 320, window=dropdown, width=180)

    def load_border_image(self, filename):
        path = os.path.join("themes", filename)
        if os.path.exists(path):
            img = Image.open(path)
            img = img.resize((300, 400))
            self.border_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.border_img, anchor="nw")

    def change_theme(self, filename):
        self.load_border_image(filename)

    def on_click(self, char):
        if char == 'C':
            self.expression = ""
        elif char == '=':
            try:
                self.expression = str(eval(self.expression))
            except Exception:
                self.expression = "Error"
        else:
            self.expression += char
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.expression)

if __name__ == "__main__":
    root = tk.Tk()
    app = GoonersCalculator(root)
    root.mainloop()

