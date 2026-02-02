
THEME_COLOR = "#032EA1"
THEME_COLOR_HOVER = "#02268a"
BORDER_COLOR = "#999999"

def get_stylesheet():
    return f"""
    QMainWindow {{
        background-color: #f5f5f5;
    }}
    
    /* Navigation Bar */
    #TopBar {{
        background-color: #ffffff;
        border-bottom: 1px solid {BORDER_COLOR};
        min-height: 60px;
        max-height: 60px;
    }}
    
    #TopBar QPushButton {{
        background-color: transparent;
        border: none;
        border-bottom: 3px solid transparent;
        color: #333333;
        padding: 0 20px;
        font-size: 14px;
        font-weight: 500;
    }}
    
    #TopBar QPushButton:hover {{
        background-color: #f0f0f0;
    }}
    
    #TopBar QPushButton[active="true"] {{
        color: {THEME_COLOR};
        border-bottom: 3px solid {THEME_COLOR};
        font-weight: bold;
    }}
    
    /* Main Content Area */
    #MainContent {{
        background-color: #ffffff;
        border-radius: 10px;
        margin: 10px;
    }}
    
    /* Typography */
    QLabel {{
        color: #333333;
        font-family: 'Segoe UI', Arial, sans-serif;
    }}
    
    /* Input Fields (Themed Borders) */
    QLineEdit, QSpinBox, QTextEdit, QPlainTextEdit, QComboBox {{
        border: 1px solid #cccccc; /* Slightly lighter than main border */
        border-radius: 4px;
        padding: 5px;
        background-color: #ffffff;
        color: #333333;
        selection-background-color: {THEME_COLOR};
    }}

    QLineEdit:hover, QSpinBox:hover, QTextEdit:hover, QComboBox:hover {{
        border: 1px solid {THEME_COLOR};
    }}

    QLineEdit:focus, QSpinBox:focus, QTextEdit:focus, QComboBox:focus {{
        border: 1px solid {THEME_COLOR};
    }}
    
    /* Buttons */
    QPushButton#PrimaryButton {{
        background-color: {THEME_COLOR};
        color: white;
        border-radius: 5px;
        padding: 8px 15px;
        font-weight: bold;
        border: none;
    }}
    
    QPushButton#PrimaryButton:hover {{
        background-color: {THEME_COLOR_HOVER};
    }}
    
    QPushButton#PrimaryButton:pressed {{
        background-color: {THEME_COLOR};
        padding-top: 9px;
    }}
    
    /* Scrollbars */
    QScrollBar:vertical {{
        border: none;
        background: #f0f0f0;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #cdcdcd;
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        border: none;
        background: none;
    }}

    /* Cards */
    QFrame.Card {{
        background-color: #ffffff;
        border: 1px solid {BORDER_COLOR};
        border-radius: 8px;
    }}
    QFrame.Card QLabel {{
        font-weight: 600;
        font-size: 14px;
        color: #333;
        border: none;
    }}

    /* Group Boxes (Title on border) */
    QGroupBox {{
        border: 2px solid #555555; /* Thicker and darker border */
        border-radius: 6px;
        margin-top: 10px; 
        padding-top: 15px; /* More padding for clear separation */
        font-size: 11px;
        background-color: #ffffff;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 10px;
        padding: 0 5px;
        color: #032EA1;
        font-weight: bold;
        background-color: #ffffff; /* Ensure title has background to cover border */
    }}
    """
