import tkinter as tk
from PIL import Image, ImageTk
import os
import json


class GoonersCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Gooner's Calculator")
        self.root.geometry("300x450")

        self.theme_mode = "dark"  # Default to dark mode
        self.load_ui_theme()

        self.bg_canvas = tk.Canvas(
            self.root, width=300, height=450, highlightthickness=0
        )
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.expression = ""
        self.tabs = {}  # {tab_name: expression}
        self.current_tab = None
        self.selected_theme = tk.StringVar()
        self.border_img = None
        self.border_path = None
        self.original_border_img = None

        self.keypad_visible = True
        self.button_frame = None

        self.create_widgets()
        self.create_tab_bar()
        self.load_theme_persistence()
        self.add_new_tab()

        self.root.bind("<Return>", self.evaluate_expression)  # Keyboard input support
        self.root.bind("=", self.evaluate_expression)  # Support = key as Enter

    def create_tab_bar(self):
        self.tab_bar_canvas = tk.Canvas(
            self.root, height=30, bg=self.bg_color, highlightthickness=0
        )
        self.tab_bar_frame = tk.Frame(self.tab_bar_canvas, bg=self.bg_color)
        self.tab_scroll = tk.Scrollbar(
            self.root, orient="horizontal", command=self.tab_bar_canvas.xview
        )

        self.tab_bar_canvas.configure(xscrollcommand=self.tab_scroll.set)
        self.tab_bar_canvas.create_window(
            (0, 0), window=self.tab_bar_frame, anchor="nw"
        )
        self.tab_bar_frame.bind(
            "<Configure>",
            lambda e: self.tab_bar_canvas.configure(
                scrollregion=self.tab_bar_canvas.bbox("all")
            ),
        )

        self.tab_bar_canvas.pack(fill="x")
        self.tab_scroll.pack(fill="x")

        self.new_tab_btn = tk.Button(
            self.tab_bar_frame,
            text="+ New Tab",
            command=self.add_new_tab,
            width=10,
            bg=self.button_bg,
            fg=self.fg_color,
        )
        self.new_tab_btn.pack(side="left", padx=2)

        self.toggle_keypad_btn = tk.Button(
            self.tab_bar_frame,
            text="⌨️",
            command=self.toggle_keypad,
            bg=self.button_bg,
            fg=self.fg_color,
            width=2,
        )
        self.toggle_keypad_btn.pack(side="left", padx=4)

        self.tab_buttons = []

    def refresh_tab_buttons(self):
        for widget in self.tab_bar_frame.winfo_children():
            if widget not in (self.new_tab_btn, self.toggle_keypad_btn):
                widget.destroy()

        self.tab_buttons.clear()

        for tab in self.tabs:
            frame = tk.Frame(self.tab_bar_frame, bg=self.bg_color)
            frame.pack(side="left", padx=2)

            tab_var = tk.StringVar(value=tab)
            entry = tk.Entry(
                frame,
                textvariable=tab_var,
                width=7,
                bg=self.entry_bg,
                fg=self.fg_color,
                relief="flat",
                justify="center",
            )
            entry.pack(side="left")

            def rename_callback(event=None, var=tab_var, old_name=tab):
                new_name = var.get().strip()
                if (
                    new_name
                    and new_name != old_name
                    and new_name not in self.tabs
                    and len(new_name) <= 15
                    and new_name.isalnum()
                ):
                    self.tabs[new_name] = self.tabs.pop(old_name)
                    if self.current_tab == old_name:
                        self.current_tab = new_name
                    self.refresh_tab_buttons()
                else:
                    var.set(old_name)  # Revert

            entry.bind("<FocusOut>", rename_callback)
            entry.bind("<Return>", rename_callback)
            entry.bind("<Button-1>", lambda e, t=tab: self.switch_tab(t))

            if len(self.tabs) > 1:
                close_btn = tk.Button(
                    frame,
                    text="X",
                    command=lambda t=tab: self.delete_tab(t),
                    width=2,
                    fg="red",
                    bg=self.button_bg,
                )
                close_btn.pack(side="left")

            self.tab_buttons.append(frame)

    def toggle_keypad(self):
        self.keypad_visible = not self.keypad_visible
        if self.button_frame:
            if self.keypad_visible:
                self.button_frame.pack()
            else:
                self.button_frame.pack_forget()

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
            self.display.insert(0, self.expression)

        self.refresh_tab_buttons()

    def switch_tab(self, tab_name):
        if self.current_tab:
            self.tabs[self.current_tab] = self.expression

        self.current_tab = tab_name
        self.expression = self.tabs[tab_name]
        self.display.delete(0, tk.END)
        self.display.insert(0, self.expression)
        print(f"Switched to tab: {tab_name}")

    def create_widgets(self):
        self.display = tk.Entry(
            self.root,
            font=("Consolas", 20),
            bd=5,
            relief=tk.RIDGE,
            justify="right",
            bg=self.entry_bg,
            fg=self.fg_color,
        )
        self.display.pack(pady=(35, 5), padx=20, fill="x")

        self.display.bind("<Return>", self.evaluate_expression)
        self.display.bind("=", self.evaluate_expression)

        self.button_frame = tk.Frame(self.root, bg=self.bg_color)
        self.button_frame.pack()

        buttons = [
            ("7", 0, 0),
            ("8", 0, 1),
            ("9", 0, 2),
            ("/", 0, 3),
            ("4", 1, 0),
            ("5", 1, 1),
            ("6", 1, 2),
            ("*", 1, 3),
            ("1", 2, 0),
            ("2", 2, 1),
            ("3", 2, 2),
            ("-", 2, 3),
            ("C", 3, 0),
            ("0", 3, 1),
            ("=", 3, 2),
            ("+", 3, 3),
        ]

        for text, r, c in buttons:
            btn = tk.Button(
                self.button_frame,
                text=text,
                width=4,
                height=1,
                font=("Arial", 14),
                command=lambda t=text: self.on_click(t),
                bg=self.button_bg,
                fg=self.fg_color,
            )
            btn.grid(row=r, column=c, padx=5, pady=5)

        themes = [f for f in os.listdir("themes") if f.endswith(".png")]
        if themes:
            self.selected_theme.set(themes[0])
            dropdown = tk.OptionMenu(
                self.root, self.selected_theme, *themes, command=self.change_theme
            )
            dropdown.pack(pady=5)

        controls = tk.Frame(self.root, bg=self.bg_color)
        controls.pack(pady=5)
        save_btn = tk.Button(
            controls,
            text="📂 Save Tabs",
            command=self.save_tabs,
            bg=self.button_bg,
            fg=self.fg_color,
        )
        load_btn = tk.Button(
            controls,
            text="📂 Load Tabs",
            command=self.load_tabs,
            bg=self.button_bg,
            fg=self.fg_color,
        )
        toggle_theme_btn = tk.Button(
            controls,
            text="🌓 Toggle Mode",
            command=self.toggle_mode,
            bg=self.button_bg,
            fg=self.fg_color,
        )
        save_btn.pack(side="left", padx=10)
        load_btn.pack(side="left", padx=10)
        toggle_theme_btn.pack(side="left", padx=10)

    def toggle_mode(self):
        self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
        self.load_ui_theme()
        self.refresh_ui_theme()
        self.save_theme_persistence()

    def load_ui_theme(self):
        if self.theme_mode == "dark":
            self.bg_color = "#1e1e1e"
            self.fg_color = "white"
            self.button_bg = "#333333"
            self.entry_bg = "#222222"
        else:
            self.bg_color = "#f0f0f0"
            self.fg_color = "black"
            self.button_bg = "#dddddd"
            self.entry_bg = "white"

        self.root.configure(bg=self.bg_color)

    def refresh_ui_theme(self):
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=self.bg_color, fg=self.fg_color)
            except:
                pass
        self.refresh_tab_buttons()
        self.display.configure(bg=self.entry_bg, fg=self.fg_color)

    def evaluate_expression(self, event=None):
        try:
            expression = self.display.get()
            result = str(eval(expression))
            self.display.delete(0, tk.END)
            self.display.insert(0, result)
            self.expression = result
            self.tabs[self.current_tab] = result
        except Exception as e:
            self.display.delete(0, tk.END)
            self.display.insert(0, "Error")
            print(f"[Eval error]: {e}")

    def load_border_image(self, filename):
        path = os.path.join("themes", filename)
        if os.path.exists(path):
            self.border_path = path
            self.original_border_img = Image.open(path)
            self.redraw_border_image()
            self.root.bind("<Configure>", lambda e: self.redraw_border_image())

    def redraw_border_image(self):
        if not self.original_border_img:
            return

        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width < 10 or height < 10:
            return

        resized_img = self.original_border_img.resize((width, height), Image.LANCZOS)
        self.border_img = ImageTk.PhotoImage(resized_img)
        self.bg_canvas.delete("bg")
        self.bg_canvas.create_image(0, 0, image=self.border_img, anchor="nw", tags="bg")
        self.bg_canvas.lower("bg")

    def change_theme(self, filename):
        self.selected_theme.set(filename)
        self.load_border_image(filename)
        self.save_theme_persistence()

    def save_theme_persistence(self):
        try:
            with open("theme.json", "w") as f:
                json.dump(
                    {"theme": self.selected_theme.get(), "mode": self.theme_mode}, f
                )
        except Exception as e:
            print("Failed to save theme:", e)

    def load_theme_persistence(self):
        try:
            with open("theme.json", "r") as f:
                data = json.load(f)
                theme = data.get("theme")
                mode = data.get("mode")
                if theme:
                    self.selected_theme.set(theme)
                    self.load_border_image(theme)
                if mode:
                    self.theme_mode = mode
                    self.load_ui_theme()
        except Exception as e:
            print("No saved theme found:", e)

    def on_click(self, char):
        if char == "C":
            self.expression = ""
        elif char == "=":
            self.evaluate_expression()
            return
        else:
            self.expression += char
        self.display.delete(0, tk.END)
        self.display.insert(tk.END, self.expression)

    def save_tabs(self):
        try:
            with open("tabs.json", "w") as f:
                json.dump({"tabs": self.tabs, "current_tab": self.current_tab}, f)
            print("Tabs saved.")
        except Exception as e:
            print("Save failed:", e)

    def load_tabs(self):
        try:
            with open("tabs.json", "r") as f:
                data = json.load(f)
                self.tabs = data.get("tabs", {})
                self.current_tab = data.get(
                    "current_tab", list(self.tabs.keys())[0] if self.tabs else None
                )
                if self.current_tab:
                    self.expression = self.tabs[self.current_tab]
                    self.display.delete(0, tk.END)
                    self.display.insert(0, self.expression)
                self.refresh_tab_buttons()
            print("Tabs loaded.")
        except Exception as e:
            print("Load failed:", e)


if __name__ == "__main__":
    root = tk.Tk()
    app = GoonersCalculator(root)
    root.mainloop()
