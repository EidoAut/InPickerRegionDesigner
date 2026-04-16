from __future__ import annotations

from tkinter import ttk


class BasePanel(ttk.Frame):
    """Small UI helper base class.

    Each panel receives a reference to the host application. The host exposes
    callbacks and shared tkinter variables, while the panel only builds widgets.
    This keeps widget construction local and prevents the main window class from
    becoming another monolith.
    """

    def __init__(self, master, app, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.app = app

    @property
    def palette(self):
        """Shortcut used by child panels when styling custom Tk widgets."""
        return self.app.palette
