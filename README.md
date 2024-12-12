# FreeCAD AI Chat Addon

A FreeCAD addon that enables users to chat with AI models through a Facebook-like chat interface. The addon supports both cloud-based (HuggingFace) and local (LM Studio) AI backends.

## Features

- Modern, Facebook-like chat interface
- Support for multiple AI backends:
  - HuggingFace (cloud-based)
  - LM Studio (local)
- Customizable settings:
  - UI theme and colors
  - Chat history management
  - AI backend configuration
- Chat history export/import
- Automatic conversation saving

## Installation

1. Clone this repository into your FreeCAD Mod directory:
   ```bash
   cd ~/.FreeCAD/Mod  # Linux/Mac
   # or
   cd %APPDATA%/FreeCAD/Mod  # Windows
   
   git clone https://github.com/yourusername/freecad-ai-chat.git
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### HuggingFace Setup
1. Get your HuggingFace API key from https://huggingface.co/settings/tokens
2. Open the addon settings in FreeCAD
3. Select "HuggingFace" as the AI backend
4. Enter your API key and preferred model

### LM Studio Setup
1. Install LM Studio from https://lmstudio.ai/
2. Start the local server in LM Studio
3. Open the addon settings in FreeCAD
4. Select "LM Studio" as the AI backend
5. Configure the host, port, and model path

## Usage

1. Open FreeCAD
2. Go to View → Workbenches and enable "AI Chat"
3. Click the chat icon in the toolbar to open the chat interface
4. Type your message and press Enter or click Send
5. The AI will respond based on your selected backend

## Settings

Access the settings dialog through the gear icon in the chat interface to configure:

- AI Backend Settings
  - Backend selection (HuggingFace/LM Studio)
  - API keys and endpoints
  - Model selection
  - Local server configuration

- UI Settings
  - Theme (Light/Dark)
  - Chat bubble colors
  - Font size
  - Window position

- History Settings
  - Maximum message history
  - Auto-save options
  - Export/Import functionality

## Development

The addon is structured as follows:

```
freecad-ai-chat/
├── __init__.py           # Addon initialization and FreeCAD integration
├── gui/                  # User interface components
│   ├── chat_widget.py    # Main chat interface
│   └── settings_dialog.py# Settings management UI
├── core/                 # Core functionality
│   ├── ai_service.py     # AI service abstraction
│   ├── huggingface_backend.py # HuggingFace implementation
│   └── lmstudio_backend.py    # LM Studio implementation
├── utils/                # Utility functions
│   └── settings.py       # Settings management
└── config/              # Configuration files
    └── default_settings.json  # Default settings
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on the Query2Cad concept
- Uses HuggingFace's API for cloud-based AI
- Integrates with LM Studio for local AI processing
