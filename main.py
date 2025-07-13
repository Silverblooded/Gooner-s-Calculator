import tkinter as tk

class GoonersCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gooner's Calculator")
        self.root.geometry("300x400")
        self.root.configure(bg="#1e1e1e")  # Dark theme for now

        self.expression = ""
        self.create_widgets()

    def create_widgets(self):
        # Display
        self.display = tk.Entry(self.root, font=("Consolas", 20), bd=10, relief=tk.RIDGE, justify="right")
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="we")

        # Buttons
        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('C', 4, 0), ('0', 4, 1), ('=', 4, 2), ('+', 4, 3),
        ]

        for (text, row, col) in buttons:
            btn = tk.Button(self.root, text=text, width=5, height=2, font=("Arial", 14),
                            command=lambda t=text: self.on_click(t))
            btn.grid(row=row, column=col, padx=5, pady=5)

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
