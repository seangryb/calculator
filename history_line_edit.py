from PySide6.QtWidgets import QLineEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent

class HistoryLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []
        self.history_index = -1 # -1 indicates we are not currently browsing history
        self.current_input = "" # Stores text typed before navigating history

    def add_to_history(self, text):
        """Adds a non-empty, non-duplicate entry to the history."""
        if text and (not self.history or self.history[-1] != text):
            self.history.append(text)
        self.history_index = -1 # Reset history navigation index

    def keyPressEvent(self, event: QKeyEvent):
        """Handles Up and Down arrow keys for history navigation."""
        key = event.key()

        if not self.history: # No history, act like a normal QLineEdit
            super().keyPressEvent(event)
            return

        if key == Qt.Key.Key_Up:
            if self.history_index == -1: # Started navigating up
                self.current_input = self.text() # Save current text
                self.history_index = len(self.history) - 1
            elif self.history_index > 0:
                self.history_index -= 1
            else: # Reached the top of history
                self.history_index = 0

            if 0 <= self.history_index < len(self.history):
                self.setText(self.history[self.history_index])
                self.selectAll() # Optional: select text for easy replacement
            event.accept() # Consume the event

        elif key == Qt.Key.Key_Down:
            if self.history_index == -1: # Pressed Down without navigating Up first
                event.accept() # Do nothing, consume the event
                return
            elif self.history_index < len(self.history) - 1:
                self.history_index += 1
                self.setText(self.history[self.history_index])
                self.selectAll()
            else: # Reached the bottom or went past it
                self.history_index = -1 # Stop navigating
                self.setText(self.current_input) # Restore original text
            event.accept() # Consume the event

        else:
            # For any other key press, reset history navigation
            self.history_index = -1
            self.current_input = "" # Clear saved input when user types normally
            super().keyPressEvent(event) # Handle other keys normally
