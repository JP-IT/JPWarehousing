import sys
import os
import json
import openai
import pyperclip
import subprocess
import threading
import traceback
import ctypes
import time

try:
    import keyboard  # Hotkey handling for system-wide usage
except ModuleNotFoundError:
    print("keyboard module not found. Installing...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'keyboard'])
    import keyboard

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
        QMessageBox, QSystemTrayIcon, QMenu, QAction, QDialog,
        QInputDialog, QLineEdit, QLabel
    )
    from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
    from PyQt5.QtCore import Qt, QTimer, QMetaObject, Q_ARG
except ModuleNotFoundError:
    print("PyQt5 not found. Installing...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'PyQt5'])
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit,
        QMessageBox, QSystemTrayIcon, QMenu, QAction, QDialog,
        QInputDialog, QLineEdit, QLabel
    )
    from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
    from PyQt5.QtCore import Qt, QTimer, QMetaObject, Q_ARG


def is_user_admin():
    """
    Check if the current user is an administrator on Windows.
    Returns True if admin, False otherwise (or on non-Windows).
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def resource_path(filename: str) -> str:
    """
    Returns the absolute path to a resource file whether running in dev
    or via PyInstaller (which uses a temp folder in sys._MEIPASS).
    """
    if getattr(sys, 'frozen', False):  # Running as a PyInstaller .exe
        return os.path.join(sys._MEIPASS, filename)
    else:
        return os.path.join(os.path.dirname(__file__), filename)


class TextCorrectionApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle('Text Correction Tool')

        # Adjust window size as desired:
        self.window.setFixedSize(550, 500)

        self.apply_styles()

        # Create the main layout with extra top margin to accommodate the label
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 35, 10, 10)  # (left, top, right, bottom)

        # Main text editor
        self.text_edit = QTextEdit(self.window)
        self.text_edit.setPlaceholderText(
            'Paste or type text here...\n'
            'Type "/help" or "/about" for more information.'
        )
        layout.addWidget(self.text_edit)

        # Buttons
        self.fix_grammar_button = QPushButton('Fix Grammar', self.window)
        self.fix_grammar_button.clicked.connect(
            lambda: self.start_processing_local('Correct the grammar of the following text:')
        )
        layout.addWidget(self.fix_grammar_button)

        self.improve_text_button = QPushButton('Improve Text', self.window)
        self.improve_text_button.clicked.connect(
            lambda: self.start_processing_local('Improve the following text to sound more professional and natural:')
        )
        layout.addWidget(self.improve_text_button)

        self.api_key_button = QPushButton('Set API Key', self.window)
        self.api_key_button.clicked.connect(self.set_api_key)
        layout.addWidget(self.api_key_button)

        self.minimize_button = QPushButton('Minimize to Tray', self.window)
        self.minimize_button.clicked.connect(self.minimize_to_tray)
        layout.addWidget(self.minimize_button)

        # Apply the layout to the window
        self.window.setLayout(layout)

        # Load/OpenAI setup
        self.load_api_key()

        # Timer & loading animation
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)
        self.loading_state = 0

        # Set up the system tray icon
        self.setup_tray_icon()

        # Check admin status
        self.user_is_admin = is_user_admin()
        print(f"Is user admin? {self.user_is_admin}")
        self.setup_hotkeys()

        # Add a label in the top-right corner for Admin/Non-Admin Mode
        self.mode_label = QLabel(self.window)
        if self.user_is_admin:
            self.mode_label.setText("Admin Mode")
            self.mode_label.setStyleSheet("color: purple; font-weight: bold;")
        else:
            self.mode_label.setText("Non-Admin Mode")
            self.mode_label.setStyleSheet("color: red; font-weight: bold;")

        # Let Qt compute the proper label size
        self.mode_label.adjustSize()

        # Position the label near the top-right corner
        x_pos = self.window.width() - self.mode_label.width() - 10
        y_pos = 10
        self.mode_label.move(x_pos, y_pos)

    def apply_styles(self):
        """Apply a dark palette and custom fonts/styles to the whole app."""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(70, 70, 70))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(20, 20, 20))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))

        self.app.setPalette(palette)

        font = QFont("Courier New", 11)
        self.app.setFont(font)

        self.window.setStyleSheet(
            "QPushButton { border: 2px solid #00ff00; border-radius: 5px; padding: 5px; } "
            "QPushButton:hover { background-color: #007700; } "
            "QTextEdit { border: 2px solid #00ff00; padding: 10px; } "
        )

    def setup_tray_icon(self):
        """
        Load the tray icon from a relative path so it works on other devices,
        even after PyInstaller bundling.
        """
        icon_file = resource_path('menu-bar.png')  # or menu-bar.ico if you prefer
        if os.path.exists(icon_file):
            icon = QIcon(icon_file)
            # Also set the window icon
            self.app.setWindowIcon(icon)
            self.window.setWindowIcon(icon)
        else:
            icon = QIcon()

        self.tray_icon = QSystemTrayIcon(icon, self.app)
        tray_menu = QMenu()

        restore_action = QAction("Restore", self.window)
        restore_action.triggered.connect(self.restore_window)
        tray_menu.addAction(restore_action)

        exit_action = QAction("Exit", self.window)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.restore_window)

    def setup_hotkeys(self):
        """Register system-wide hotkeys if the user is admin, otherwise skip."""
        if self.user_is_admin:
            keyboard.add_hotkey('ctrl+g', self.global_fix_grammar, suppress=True)
            keyboard.add_hotkey('ctrl+shift+g', self.global_improve_text, suppress=True)

            print("Global Hotkeys Registered:\n"
                  " - Ctrl+G (Fix Grammar)\n"
                  " - Ctrl+Shift+G (Improve Text)\n"
                  "Admin privileges detected. System-wide hotkeys should work.")
        else:
            print("No admin privileges. System-wide hotkeys will NOT be registered.")
            print("Users can still use the app's interface for text correction.")

    # -----------
    # GLOBAL (Admin)
    # -----------
    def global_fix_grammar(self):
        """Triggered when user presses Ctrl+G system-wide."""
        self.copy_process_paste("Correct the grammar of the following text:")

    def global_improve_text(self):
        """Triggered when user presses Ctrl+Shift+G system-wide."""
        self.copy_process_paste("Improve the following text to sound more professional and natural:")

    def copy_process_paste(self, prompt: str):
        """
        1) Press Ctrl+C to copy highlighted text in the external app
        2) Wait, read from clipboard
        3) Process with OpenAI
        4) Copy result to clipboard
        5) Press Ctrl+V to paste new text in the external app
        """
        if not openai.api_key:
            self.show_error_message('Warning', 'API key is not set. Please set it first.')
            return

        keyboard.send('ctrl+c')
        time.sleep(0.2)  # Give OS time to update clipboard

        original_text = pyperclip.paste().strip()
        if not original_text:
            print("[ERROR] No text found in clipboard (global hotkey).")
            return

        threading.Thread(
            target=self.do_copy_process_paste,
            args=(prompt, original_text)
        ).start()

    def do_copy_process_paste(self, prompt, text):
        """Background worker to call OpenAI, then paste result back."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=500,
                temperature=0.7
            )
            result = response.choices[0].message['content'].strip()

            # Copy result, then paste
            pyperclip.copy(result)
            keyboard.send('ctrl+v')

            print("[INFO] Successfully replaced text in the external app (global).")
        except Exception as e:
            error_trace = traceback.format_exc()
            print("[ERROR] Global copy–process–paste:\n", error_trace)

    # -----------
    # LOCAL USAGE
    # -----------
    def start_processing_local(self, prompt: str):
        """Called when user clicks 'Fix Grammar' or 'Improve Text' inside the app."""
        input_text = self.text_edit.toPlainText().strip()

        if not input_text:
            self.show_error_message('Warning', 'Please enter some text to process.')
            return

        # Check for local /help or /about commands
        if input_text.lower() == '/help':
            self.show_help_prompt()
            return
        elif input_text.lower() == '/about':
            self.show_about_prompt()
            return

        if not openai.api_key:
            self.show_error_message('Warning', 'API key is not set. Please set it first.')
            return

        # Start local loading animation
        self.loading_state = 0
        self.loading_timer.start(500)

        threading.Thread(target=self.process_text_local, args=(prompt, input_text)).start()

    def process_text_local(self, prompt, input_text):
        """OpenAI call for text typed in the app's text box."""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text}
                ],
                max_tokens=500,
                temperature=0.7
            )
            result = response.choices[0].message['content'].strip()

            self.loading_timer.stop()
            QMetaObject.invokeMethod(self.text_edit, "setPlainText", Q_ARG(str, result))
            pyperclip.copy(result)

        except Exception as e:
            self.loading_timer.stop()
            error_trace = traceback.format_exc()
            print("Error while processing text (Local):\n", error_trace)

            self.show_error_message(
                'Error',
                f'Failed to process text: {str(e)}\n\nDetails:\n{error_trace}'
            )

    # -----------
    # UI Helpers
    # -----------
    def update_loading_animation(self):
        """Simple loading animation that updates the QTextEdit."""
        dots = '.' * (self.loading_state % 4)
        self.text_edit.setPlainText(f'Generating{dots}')
        self.loading_state += 1

    def minimize_to_tray(self):
        self.window.hide()
        self.tray_icon.show()

    def restore_window(self):
        self.window.showNormal()
        self.tray_icon.hide()

    def exit_app(self):
        self.tray_icon.hide()
        self.app.quit()

    def set_api_key(self):
        """
        Use a styled QInputDialog so the text is visible on a dark background.
        """
        dialog = QInputDialog(self.window)
        dialog.setWindowTitle("Set API Key")
        dialog.setLabelText("Enter your OpenAI API Key:")
        dialog.setTextEchoMode(QLineEdit.Normal)

        # Apply dark styles
        dialog.setStyleSheet(
            """
            QDialog { background-color: #303030; }
            QLineEdit { color: #ffffff; background-color: #505050; }
            QLabel { color: #ffffff; }
            QPushButton {
                background-color: #585858;
                color: #ffffff;
                border: 1px solid #cccccc;
            }
            """
        )

        ok = dialog.exec_()
        key = dialog.textValue().strip()

        if ok and key:
            openai.api_key = key
            with open('config.json', 'w') as f:
                json.dump({'api_key': key}, f)

    def load_api_key(self):
        """Loads API key from config.json if it exists."""
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                openai.api_key = config.get('api_key', '')

    def show_error_message(self, title, message):
        """Displays an error/warning message with a readable dark style."""
        msg_box = QMessageBox(self.window)
        msg_box.setWindowTitle(title)
        msg_box.setTextFormat(Qt.PlainText)
        msg_box.setText(message)
        msg_box.setPalette(self.app.palette())
        msg_box.setStyleSheet(
            """
            QMessageBox {
                background-color: #303030;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
            }
            QMessageBox QPushButton {
                background-color: #585858;
                color: #FFFFFF;
                border: 1px solid #CCCCCC;
            }
            """
        )
        msg_box.exec_()

    def show_about_prompt(self):
        """Displays information about the app with a readable style."""
        about_text = (
            "Text Correction Tool v1.1\n\n"
            "Created by Nathaniel Ruiz\n"
            "Email: nathan.r0200@gmail.com\n\n"
            "This app helps correct and improve text using OpenAI's GPT."
        )
        about_box = QMessageBox(self.window)
        about_box.setWindowTitle("About")
        about_box.setTextFormat(Qt.PlainText)
        about_box.setText(about_text)
        about_box.setPalette(self.app.palette())
        about_box.setStyleSheet(
            """
            QMessageBox {
                background-color: #303030;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
            }
            QMessageBox QPushButton {
                background-color: #585858;
                color: #FFFFFF;
                border: 1px solid #CCCCCC;
            }
            """
        )
        about_box.exec_()

    def show_help_prompt(self):
        """Displays instructions on how to use the app with a readable style."""
        help_text = (
            "How the App Works:\n\n"
            "1. Type or paste your text into the editor.\n"
            "2. Use the 'Fix Grammar' button to correct any grammatical errors.\n"
            "3. Use the 'Improve Text' button to make text sound more natural and professional.\n"
            "4. You can also type '/about' to see app info, or '/help' for these instructions.\n"
            "5. 'Minimize to Tray' hides the window to your system tray.\n"
            "6. To set your OpenAI API Key, click 'Set API Key'.\n\n"
            "System-Wide Hotkeys (Admin Only):\n"
            " - Ctrl+G to fix grammar from any app\n"
            " - Ctrl+Shift+G to improve text from any app\n"
            "\nWhen you press these hotkeys:\n"
            "  - The highlighted text is copied,\n"
            "  - Processed by GPT,\n"
            "  - And then pasted back over the original text.\n\n"
            "Admin vs. Non-Admin Mode:\n"
            " - If you have admin privileges, you'll see 'Admin Mode' in the corner.\n"
            " - Otherwise, 'Non-Admin Mode' means system-wide hotkeys won't work.\n\n"
            "How to run the app as Administrator:\n"
            " - Right-click the .exe and choose 'Run as administrator'.\n"
            " - Some users may not have access to admin rights.\n"
            "   If so, contact your IT Admin for assistance.\n"
        )
        help_box = QMessageBox(self.window)
        help_box.setWindowTitle("Help")
        help_box.setTextFormat(Qt.PlainText)
        help_box.setText(help_text)
        help_box.setPalette(self.app.palette())
        help_box.setStyleSheet(
            """
            QMessageBox {
                background-color: #303030;
            }
            QMessageBox QLabel {
                color: #FFFFFF;
            }
            QMessageBox QPushButton {
                background-color: #585858;
                color: #FFFFFF;
                border: 1px solid #CCCCCC;
            }
            """
        )
        help_box.exec_()

    def run(self):
        # Show the main window
        self.window.show()
        self.app.exec_()


if __name__ == '__main__':
    app = TextCorrectionApp()
    app.run()
