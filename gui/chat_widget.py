import os
import json
import asyncio
from datetime import datetime
from PySide import QtGui, QtCore
import FreeCADGui
from utils.settings import settings
from core.ai_service import service_manager
from .settings_dialog import SettingsDialog

class ChatBubble(QtGui.QWidget):
    """Custom widget for chat message bubbles."""
    
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_user = is_user
        self.init_ui()
        
    def init_ui(self):
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)
        
        # Create message bubble
        bubble = QtGui.QLabel(self.text)
        bubble.setWordWrap(True)
        bubble.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        # Get colors from settings
        colors = settings.get("ui", "chat_colors")
        bubble_color = colors["user_bubble"] if self.is_user else colors["ai_bubble"]
        
        # Style the bubble
        bubble.setStyleSheet(f"""
            QLabel {{
                background-color: {bubble_color};
                border-radius: 10px;
                padding: 8px;
                color: white;
            }}
        """)
        
        # Add spacing and bubble to layout
        if self.is_user:
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            layout.addWidget(bubble)
            layout.addStretch()

class ChatWidget(QtGui.QDialog):
    """Main chat widget for the FreeCAD AI Chat addon."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Design Assistant")
        self.conversation = []
        self.init_ui()
        self.load_history()
        
    def init_ui(self):
        """Initialize the chat widget UI."""
        # Set window properties
        self.resize(400, 600)
        self.setWindowFlags(QtCore.Qt.Window)
        
        # Create main layout
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        
        # Create toolbar
        toolbar = QtGui.QToolBar()
        layout.addWidget(toolbar)
        
        # Add settings button
        settings_action = QtGui.QAction(QtGui.QIcon(), "Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(settings_action)
        
        # Add export button
        export_action = QtGui.QAction(QtGui.QIcon(), "Export Chat", self)
        export_action.triggered.connect(self.export_chat)
        toolbar.addAction(export_action)
        
        # Create scroll area for messages
        scroll = QtGui.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        layout.addWidget(scroll)
        
        # Create widget for messages
        self.message_widget = QtGui.QWidget()
        self.message_layout = QtGui.QVBoxLayout()
        self.message_widget.setLayout(self.message_layout)
        scroll.setWidget(self.message_widget)
        
        # Add stretch to push messages up
        self.message_layout.addStretch()
        
        # Create input area
        input_layout = QtGui.QHBoxLayout()
        layout.addLayout(input_layout)
        
        # Create message input
        self.message_input = QtGui.QTextEdit()
        self.message_input.setMaximumHeight(100)
        self.message_input.textChanged.connect(self.adjust_input_height)
        input_layout.addWidget(self.message_input)
        
        # Create send button
        send_button = QtGui.QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)
        
        # Set background color
        bg_color = settings.get("ui", "chat_colors")["background"]
        self.setStyleSheet(f"background-color: {bg_color};")
        
        # Setup shortcut for sending messages
        self.send_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Return"), self)
        self.send_shortcut.activated.connect(self.send_message)
        
        # Setup shortcut for new line in input
        self.newline_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Shift+Return"), self)
        self.newline_shortcut.activated.connect(self.insert_newline)
    
    def adjust_input_height(self):
        """Adjust the height of the input field based on content."""
        document_height = self.message_input.document().size().height()
        self.message_input.setMinimumHeight(min(document_height + 10, 100))
    
    def insert_newline(self):
        """Insert a new line in the input field."""
        cursor = self.message_input.textCursor()
        cursor.insertText("\\n")
    
    def add_message(self, text, is_user=True):
        """Add a message bubble to the chat."""
        bubble = ChatBubble(text, is_user)
        self.message_layout.insertWidget(self.message_layout.count() - 1, bubble)
        
        # Save message to conversation history
        self.conversation.append({
            "role": "user" if is_user else "assistant",
            "content": text,
            "timestamp": datetime.now().isoformat()
        })
        
        # Auto-save if enabled
        if settings.get("history", "auto_save"):
            self.save_history()
    
    async def get_ai_response(self, message):
        """Get response from the AI service."""
        try:
            response = await service_manager.generate_response(
                message,
                context=self.conversation[-10:]  # Send last 10 messages as context
            )
            return response.text
        except Exception as e:
            QtGui.QMessageBox.critical(
                self,
                "Error",
                f"Failed to get AI response: {str(e)}"
            )
            return None
    
    def send_message(self):
        """Send the current message."""
        message = self.message_input.toPlainText().strip()
        if not message:
            return
        
        # Clear input
        self.message_input.clear()
        
        # Add user message
        self.add_message(message, is_user=True)
        
        # Get AI response
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self.get_ai_response(message))
        
        if response:
            self.add_message(response, is_user=False)
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            # Refresh UI with new settings
            self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh the UI with current settings."""
        colors = settings.get("ui", "chat_colors")
        self.setStyleSheet(f"background-color: {colors['background']};")
        
        # Refresh all chat bubbles
        for i in range(self.message_layout.count() - 1):  # -1 to skip the stretch
            widget = self.message_layout.itemAt(i).widget()
            if isinstance(widget, ChatBubble):
                widget.refresh_style()
    
    def export_chat(self):
        """Export the conversation history."""
        file_path, _ = QtGui.QFileDialog.getSaveFileName(
            self,
            "Export Chat History",
            "",
            "JSON Files (*.json);;Text Files (*.txt)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w') as f:
                    json.dump(self.conversation, f, indent=2)
            else:
                with open(file_path, 'w') as f:
                    for msg in self.conversation:
                        f.write(f"{msg['role'].title()}: {msg['content']}\n\n")
                        
            QtGui.QMessageBox.information(
                self,
                "Success",
                "Chat history exported successfully!"
            )
        except Exception as e:
            QtGui.QMessageBox.critical(
                self,
                "Error",
                f"Failed to export chat history: {str(e)}"
            )
    
    def save_history(self):
        """Save conversation history."""
        history_dir = os.path.join(os.path.dirname(settings.addon_path), "chat_history")
        os.makedirs(history_dir, exist_ok=True)
        
        history_file = os.path.join(history_dir, "chat_history.json")
        try:
            with open(history_file, 'w') as f:
                json.dump(self.conversation, f, indent=2)
        except Exception as e:
            print(f"Failed to save chat history: {str(e)}")
    
    def load_history(self):
        """Load conversation history."""
        history_file = os.path.join(
            os.path.dirname(settings.addon_path),
            "chat_history",
            "chat_history.json"
        )
        
        if not os.path.exists(history_file):
            return
        
        try:
            with open(history_file, 'r') as f:
                self.conversation = json.load(f)
                
            # Recreate message bubbles
            for msg in self.conversation:
                self.add_message(
                    msg["content"],
                    is_user=(msg["role"] == "user")
                )
        except Exception as e:
            print(f"Failed to load chat history: {str(e)}")
    
    def closeEvent(self, event):
        """Handle widget close event."""
        self.save_history()
        event.accept()
