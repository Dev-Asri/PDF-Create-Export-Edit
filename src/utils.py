# -*- coding: utf-8 -*-
import tkinter as tk
from .translations import _t

_btn_style = {
    "font": ("Segoe UI", 10, "bold"),
    "relief": "flat",
    "cursor": "hand2",
    "bd": 0,
    "highlightthickness": 0,
    "padx": 4,
}


def _mkbtn(parent, text, command, bg="#3498db", fg="white", width=16, state=None):
    text = _t(text)
    btn = tk.Button(
        parent, text=text, command=command,
        bg=bg, fg=fg, activebackground=bg, activeforeground=fg,
        width=width, **_btn_style,
    )
    if state is not None:
        btn.config(state=state)

    def _on_enter(e):
        btn.config(bg=_darken(bg))

    def _on_leave(e):
        btn.config(bg=bg)

    btn.bind("<Enter>", _on_enter)
    btn.bind("<Leave>", _on_leave)
    return btn


def _darken(hex_color, factor=0.85):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r, g, b = int(r * factor), int(g * factor), int(b * factor)
    return f"#{r:02x}{g:02x}{b:02x}"


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = _t(text)
        self.tip = None
        self.after_id = None
        widget.bind("<Enter>", self._enter)
        widget.bind("<Leave>", self._leave)

    def _enter(self, e):
        self._schedule()

    def _leave(self, e):
        self._hide()

    def _schedule(self):
        self.after_id = self.widget.after(3000, self._hide)

    def _show(self):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 4
        y = self.widget.winfo_rooty()
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self.tip, text=self.text, bg="#ffffcc", fg="#333",
                 font=("Segoe UI", 9), padx=6, pady=2, relief="solid",
                 bd=1).pack()

    def _hide(self):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        if self.tip:
            self.tip.destroy()
            self.tip = None

