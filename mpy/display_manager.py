# display_manager.py
from micropython import const

# Constants for layout
_HEADER_HEIGHT = const(16)
_FOOTER_HEIGHT = const(8)
_PADDING = const(2)

class DisplayManager:
    def __init__(self, display):
        self.display = display
        self.display.poweron()
        self.display.contrast(255)
        self.clear()

    def clear(self):
        self.display.fill(0)

    def draw_header(self, text):
        """Draws a solid header bar with inverted text."""
        self.display.fill_rect(0, 0, self.display.width, _HEADER_HEIGHT, 1)
        self.display.text(text, _PADDING, 0, 0)

    def draw_primary(self, top_line, bottom_line):
        """Draws two lines of primary text."""
        self.display.text(top_line, _PADDING, _HEADER_HEIGHT + _PADDING, 1)
        self.display.text(bottom_line, _PADDING, self.display.height - _FOOTER_HEIGHT - _PADDING - 8, 1)

    def draw_footer(self, text):
        """Draws small footer text at the very bottom."""
        y = self.display.height - _FOOTER_HEIGHT
        self.display.text(text, _PADDING, y, 1)

    def update(self):
        try:
            self.display.show()
        except BaseException as e:
            print("Display update error:", e)