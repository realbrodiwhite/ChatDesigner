import os
import FreeCADGui
from PySide import QtGui, QtCore
from utils.settings import settings

class SettingsDialog(QtGui.QDialog):
    """Settings dialog for the FreeCAD AI Chat addon."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Chat Settings")
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        
        # Create tab widget
        tabs = QtGui.QTabWidget()
        layout.addWidget(tabs)
        
        # AI Backend tab
        backend_tab = QtGui.QWidget()
        backend_layout = QtGui.QVBoxLayout()
        backend_tab.setLayout(backend_layout)
        
        # Backend selection
        backend_group = QtGui.QGroupBox("AI Backend Selection")
        backend_group_layout = QtGui.QVBoxLayout()
        self.backend_combo = QtGui.QComboBox()
        self.backend_combo.addItems(["HuggingFace", "LM Studio"])
        self.backend_combo.currentIndexChanged.connect(self.on_backend_changed)
        backend_group_layout.addWidget(self.backend_combo)
        backend_group.setLayout(backend_group_layout)
        backend_layout.addWidget(backend_group)
        
        # HuggingFace settings
        self.hf_group = QtGui.QGroupBox("HuggingFace Settings")
        hf_layout = QtGui.QFormLayout()
        self.hf_api_key = QtGui.QLineEdit()
        self.hf_model = QtGui.QLineEdit()
        self.hf_endpoint = QtGui.QLineEdit()
        hf_layout.addRow("API Key:", self.hf_api_key)
        hf_layout.addRow("Model:", self.hf_model)
        hf_layout.addRow("Endpoint:", self.hf_endpoint)
        self.hf_group.setLayout(hf_layout)
        backend_layout.addWidget(self.hf_group)
        
        # LM Studio settings
        self.lm_group = QtGui.QGroupBox("LM Studio Settings")
        lm_layout = QtGui.QFormLayout()
        self.lm_host = QtGui.QLineEdit()
        self.lm_port = QtGui.QSpinBox()
        self.lm_port.setRange(1, 65535)
        self.lm_model_path = QtGui.QLineEdit()
        browse_btn = QtGui.QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_model)
        lm_layout.addRow("Host:", self.lm_host)
        lm_layout.addRow("Port:", self.lm_port)
        lm_layout.addRow("Model Path:", self.lm_model_path)
        lm_layout.addRow("", browse_btn)
        self.lm_group.setLayout(lm_layout)
        backend_layout.addWidget(self.lm_group)
        
        # UI Settings tab
        ui_tab = QtGui.QWidget()
        ui_layout = QtGui.QVBoxLayout()
        ui_tab.setLayout(ui_layout)
        
        # Theme selection
        theme_group = QtGui.QGroupBox("Theme")
        theme_layout = QtGui.QVBoxLayout()
        self.theme_combo = QtGui.QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        ui_layout.addWidget(theme_group)
        
        # Color settings
        colors_group = QtGui.QGroupBox("Colors")
        colors_layout = QtGui.QFormLayout()
        self.user_bubble_color = QtGui.QPushButton()
        self.ai_bubble_color = QtGui.QPushButton()
        self.bg_color = QtGui.QPushButton()
        self.user_bubble_color.clicked.connect(lambda: self.pick_color("user_bubble"))
        self.ai_bubble_color.clicked.connect(lambda: self.pick_color("ai_bubble"))
        self.bg_color.clicked.connect(lambda: self.pick_color("background"))
        colors_layout.addRow("User Bubble:", self.user_bubble_color)
        colors_layout.addRow("AI Bubble:", self.ai_bubble_color)
        colors_layout.addRow("Background:", self.bg_color)
        colors_group.setLayout(colors_layout)
        ui_layout.addWidget(colors_group)
        
        # Font settings
        font_group = QtGui.QGroupBox("Font")
        font_layout = QtGui.QFormLayout()
        self.font_size = QtGui.QSpinBox()
        self.font_size.setRange(8, 24)
        font_layout.addRow("Size:", self.font_size)
        font_group.setLayout(font_layout)
        ui_layout.addWidget(font_group)
        
        # History Settings tab
        history_tab = QtGui.QWidget()
        history_layout = QtGui.QVBoxLayout()
        history_tab.setLayout(history_layout)
        
        history_group = QtGui.QGroupBox("History Settings")
        history_form = QtGui.QFormLayout()
        self.max_messages = QtGui.QSpinBox()
        self.max_messages.setRange(10, 1000)
        self.auto_save = QtGui.QCheckBox()
        history_form.addRow("Max Messages:", self.max_messages)
        history_form.addRow("Auto-save:", self.auto_save)
        history_group.setLayout(history_form)
        history_layout.addWidget(history_group)
        
        # Add tabs
        tabs.addTab(backend_tab, "AI Backend")
        tabs.addTab(ui_tab, "UI")
        tabs.addTab(history_tab, "History")
        
        # Buttons
        button_box = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Apply | QtGui.QDialogButtonBox.Reset
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QtGui.QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        button_box.button(QtGui.QDialogButtonBox.Reset).clicked.connect(self.reset_settings)
        layout.addWidget(button_box)
        
        # Load current settings
        self.load_settings()
        
    def load_settings(self):
        """Load current settings into UI."""
        # Backend settings
        backend = settings.get("ai_backend", "active_backend")
        self.backend_combo.setCurrentText(backend.title())
        
        # HuggingFace settings
        hf_config = settings.get("ai_backend", "huggingface")
        self.hf_api_key.setText(hf_config["api_key"])
        self.hf_model.setText(hf_config["model"])
        self.hf_endpoint.setText(hf_config["endpoint"])
        
        # LM Studio settings
        lm_config = settings.get("ai_backend", "lmstudio")
        self.lm_host.setText(lm_config["host"])
        self.lm_port.setValue(lm_config["port"])
        self.lm_model_path.setText(lm_config["model_path"])
        
        # UI settings
        ui_config = settings.get("ui")
        self.theme_combo.setCurrentText(ui_config["theme"].title())
        self.update_color_buttons(ui_config["chat_colors"])
        self.font_size.setValue(ui_config["font"]["size"])
        
        # History settings
        history_config = settings.get("history")
        self.max_messages.setValue(history_config["max_messages"])
        self.auto_save.setChecked(history_config["auto_save"])
        
    def update_color_buttons(self, colors):
        """Update color button backgrounds."""
        self.user_bubble_color.setStyleSheet(f"background-color: {colors['user_bubble']}")
        self.ai_bubble_color.setStyleSheet(f"background-color: {colors['ai_bubble']}")
        self.bg_color.setStyleSheet(f"background-color: {colors['background']}")
        
    def on_backend_changed(self, index):
        """Handle backend selection change."""
        backend = self.backend_combo.currentText().lower()
        self.hf_group.setVisible(backend == "huggingface")
        self.lm_group.setVisible(backend == "lm studio")
        
    def pick_color(self, color_type):
        """Open color picker dialog."""
        current_color = QtGui.QColor(settings.get("ui", "chat_colors", color_type))
        color = QtGui.QColorDialog.getColor(current_color, self)
        if color.isValid():
            button = getattr(self, f"{color_type}_color")
            button.setStyleSheet(f"background-color: {color.name()}")
            
    def browse_model(self):
        """Open file dialog to select LM Studio model."""
        file_path, _ = QtGui.QFileDialog.getOpenFileName(
            self, "Select Model File", "",
            "Model Files (*.gguf *.bin);;All Files (*.*)"
        )
        if file_path:
            self.lm_model_path.setText(file_path)
            
    def apply_settings(self):
        """Apply current settings."""
        # Backend settings
        backend = self.backend_combo.currentText().lower()
        settings.set(backend, "ai_backend", "active_backend")
        
        # HuggingFace settings
        settings.set(self.hf_api_key.text(), "ai_backend", "huggingface", "api_key")
        settings.set(self.hf_model.text(), "ai_backend", "huggingface", "model")
        settings.set(self.hf_endpoint.text(), "ai_backend", "huggingface", "endpoint")
        
        # LM Studio settings
        settings.set(self.lm_host.text(), "ai_backend", "lmstudio", "host")
        settings.set(self.lm_port.value(), "ai_backend", "lmstudio", "port")
        settings.set(self.lm_model_path.text(), "ai_backend", "lmstudio", "model_path")
        
        # UI settings
        settings.set(self.theme_combo.currentText().lower(), "ui", "theme")
        settings.set({
            "user_bubble": self.user_bubble_color.palette().button().color().name(),
            "ai_bubble": self.ai_bubble_color.palette().button().color().name(),
            "background": self.bg_color.palette().button().color().name()
        }, "ui", "chat_colors")
        settings.set(self.font_size.value(), "ui", "font", "size")
        
        # History settings
        settings.set(self.max_messages.value(), "history", "max_messages")
        settings.set(self.auto_save.isChecked(), "history", "auto_save")
        
    def reset_settings(self):
        """Reset settings to default."""
        settings.reset()
        self.load_settings()
        
    def accept(self):
        """Handle dialog acceptance."""
        self.apply_settings()
        super().accept()
