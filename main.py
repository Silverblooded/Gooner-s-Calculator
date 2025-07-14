import tkinter as tk
from PIL import Image, ImageTk
import os
import json


class GoonersCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gooner's Calculator")
        self.root.geometry("300x450")
        self.root.configure(bg="#1e1e1e")

        self.canvas = tk.Canvas(self.root, width=300, height=450)
        self.canvas.pack(fill="both", expand=True)

        self.expression = ""
        self.tabs = {}  # tab_name: expression
        self.current_tab = None
        self.selected_theme = tk.StringVar()
        self.border_img = None
        self.drag_data = {"tab": None}

        self.create_tab_bar()
        self.create_widgets()
        self.load_border_image("default_border.png")
        self.add_new_tab()

    def create_tab_bar(self):
        self.tab_frame = tk.Frame(self.root)
        self.canvas.create_window(150, 20, window=self.tab_frame)

        self.new_tab_btn = tk.Button(
            self.tab_frame, text="+ New Tab", command=self.add_new_tab, width=10
        )
        self.new_tab_btn.pack(side="left", padx=2)
        self.tab_buttons = []

    def refresh_tab_buttons(self):
        for widget in self.tab_frame.winfo_children():
            if widget != self.new_tab_btn:
                widget.destroy()

        self.tab_buttons.clear()

        for tab in self.tabs.keys():
            frame = tk.Frame(self.tab_frame)
            frame.pack(side="left", padx=2)

            tab_btn = tk.Button(frame, text=tab, width=7)
            tab_btn.pack(side="left")

            # Left-click drag setup
            tab_btn.bind("<ButtonPress-1>", lambda e, t=tab: self.start_drag(t))
            tab_btn.bind("<ButtonRelease-1>", lambda e, t=tab: self.end_drag(t))

            # Normal left click to switch
            tab_btn.bind("<Button-1>", lambda e, t=tab: self.switch_tab(t))

            # Right click to rename
            tab_btn.bind(
                "<Button-3>", lambda e, t=tab, b=tab_btn: self.rename_tab(t, b)
            )

            if len(self.tabs) > 1:
                close_btn = tk.Button(
                    frame,
                    text="X",
                    command=lambda t=tab: self.delete_tab(t),
                    width=2,
                    fg="red",
                )
                close_btn.pack(side="left")

            self.tab_buttons.append(frame)

    def start_drag(self, tab_name):
        self.drag_data["tab"] = tab_name

    def end_drag(self, target_tab_name):
        source_tab = self.drag_data.get("tab")
        if not source_tab or source_tab == target_tab_name:
            return

        tab_items = list(self.tabs.items())
        source_idx = next(i for i, (k, _) in enumerate(tab_items) if k == source_tab)
        target_idx = next(
            i for i, (k, _) in enumerate(tab_items) if k == target_tab_name
        )

        moved = tab_items.pop(source_idx)
        tab_items.insert(target_idx, moved)

        self.tabs = dict(tab_items)

        if self.current_tab == source_tab:
            self.current_tab = source_tab

        print(f"Moved '{source_tab}' to position {target_idx}")
        self.refresh_tab_buttons()
        self.drag_data["tab"] = None

    def add_new_tab(self):
        i = 1
        while f"Tab {i}" in self.tabs:
            i += 1
        tab_name = f"Tab {i}"
        self.tabs[tab_name] = ""
        self.refresh_tab_buttons()
        self.switch_tab(tab_name)

    def delete_tab(self, tab_name):
        if len(self.tabs) <= 1:
            return

        del self.tabs[tab_name]

        if self.current_tab == tab_name:
            self.current_tab = list(self.tabs.keys())[0]
            self.expression = self.tabs[self.current_tab]
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, self.expression)

        self.refresh_tab_buttons()

    def rename_tab(self, tab_name, button_widget):
        entry = tk.Entry(self.tab_frame, width=10)
        entry.insert(0, tab_name)
        entry.select_range(0, tk.END)
        entry.place(x=button_widget.winfo_x(), y=button_widget.winfo_y())

        def apply_rename(event=None):
            new_name = entry.get().strip()
            if new_name and new_name != tab_name and new_name not in self.tabs:
                self.tabs[new_name] = self.tabs.pop(tab_name)
                if self.current_tab == tab_name:
                    self.current_tab = new_name
            entry.destroy()
            self.refresh_tab_buttons()

        entry.bind("<Return>", apply_rename)
        entry.focus_set()

    def switch_tab(self, tab_name):
        if self.current_tab:
            # Save current expression before switching
            self.tabs[self.current_tab] = self.expression

        self.current_tab = tab_name
        self.expression = self.tabs[tab_name]
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.expression)

        print(f"Switched to tab: {tab_name}")

    def create_widgets(self):
        self.display = tk.Entry(
            self.root, font=("Consolas", 20), bd=5, relief=tk.RIDGE, justify="right"
        )
        self.canvas.create_window(150, 70, window=self.display, width=260, height=40)

        buttons = [
            ("7", 100, 130),
            ("8", 150, 130),
            ("9", 200, 130),
            ("/", 250, 130),
            ("4", 100, 180),
            ("5", 150, 180),
            ("6", 200, 180),
            ("*", 250, 180),
            ("1", 100, 230),
            ("2", 150, 230),
            ("3", 200, 230),
            ("-", 250, 230),
            ("C", 100, 280),
            ("0", 150, 280),
            ("=", 200, 280),
            ("+", 250, 280),
        ]

        for text, x, y in buttons:
            btn = tk.Button(
                self.root,
                text=text,
                width=4,
                height=1,
                font=("Arial", 14),
                command=lambda t=text: self.on_click(t),
            )
            self.canvas.create_window(x, y, window=btn)

        themes = [f for f in os.listdir("themes") if f.endswith(".png")]
        if themes:
            self.selected_theme.set(themes[0])
            dropdown = tk.OptionMenu(
                self.root, self.selected_theme, *themes, command=self.change_theme
            )
            self.canvas.create_window(150, 350, window=dropdown, width=180)

        save_btn = tk.Button(self.root, text="💾 Save Tabs", command=self.save_tabs)
        load_btn = tk.Button(self.root, text="📂 Load Tabs", command=self.load_tabs)
        self.canvas.create_window(80, 400, window=save_btn, width=100)
        self.canvas.create_window(220, 400, window=load_btn, width=100)

    def load_border_image(self, filename):
        path = os.path.join("themes", filename)
        if os.path.exists(path):
            img = Image.open(path).resize((300, 450))
            self.border_img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, image=self.border_img, anchor="nw")

    def change_theme(self, filename):
        self.load_border_image(filename)

    def on_click(self, char):
        if char == "C":
            self.expression = ""
        elif char == "=":
            try:
                self.expression = str(eval(self.expression))
            except Exception:
                self.expression = "Error"
        else:
            self.expression += char
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.expression)

    def save_tabs(self):
        try:
            with open("tabs.json", "w") as f:
                json.dump({"tabs": self.tabs, "current_tab": self.current_tab}, f)
        except Exception as e:
            print("Save failed:", e)

    def load_tabs(self):
        try:
            with open("tabs.json", "r") as f:
                data = json.load(f)
                self.tabs = data.get("tabs", {})
                self.current_tab = data.get("current_tab", next(iter(self.tabs), None))

                if self.current_tab:
                    self.expression = self.tabs[self.current_tab]
                    self.display.delete(0, tk.END)
                    self.display.insert(tk.END, self.expression)

                self.refresh_tab_buttons()
        except Exception as e:
            print("Load failed:", e)


if __name__ == "__main__":
    root = tk.Tk()
    app = GoonersCalculator(root)
    root.mainloop()
