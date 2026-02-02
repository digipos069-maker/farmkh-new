
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt

class SelectionInput(QComboBox):
    def __init__(self, items=None, width=None, height=25, parent=None):
        """
        A reusable ComboBox component.
        
        Args:
            items (list): List of strings to populate the dropdown.
            width (int): Fixed width of the component.
            height (int): Fixed height of the component.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        
        if items:
            self.addItems(items)
        
        if width:
            self.setFixedWidth(width)
            
        if height:
            self.setFixedHeight(height)
            
        # Optional: Add specific cursor or interaction styles here if needed
        # The main visual style is handled by the global stylesheet in styles.py
