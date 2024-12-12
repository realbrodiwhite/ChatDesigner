"""FreeCAD AI Chat Addon

This addon provides an AI-powered chat interface for FreeCAD, allowing users to
interact with AI models through a Facebook-like chat widget. It supports both
cloud-based (HuggingFace) and local (LM Studio) AI backends.
"""

import os
import FreeCAD
import FreeCADGui
from PySide import QtGui
from gui.chat_widget import ChatWidget

# Global chat widget instance
chat_widget = None

class AIChatWorkbench(FreeCADGui.Workbench):
    """FreeCAD AI Chat Workbench"""
    
    MenuText = "AI Chat"
    ToolTip = "AI-powered chat interface for FreeCAD"
    Icon = """
        /* XPM */
        static char * chat_icon_xpm[] = {
        "16 16 3 1",
        " 	c None",
        ".	c #000000",
        "+	c #FFFFFF",
        "                ",
        "     .....      ",
        "   ..+++++..    ",
        "  .+++++++++.   ",
        " .+++++++++++.  ",
        ".++++++++++++.  ",
        ".++++++++++++.  ",
        ".++++++++++++.  ",
        ".++++++++++++.  ",
        " .+++++++++++.  ",
        "  .+++++++++.   ",
        "   ..+++++..    ",
        "     .....      ",
        "      ...       ",
        "       .        ",
        "                "};
        """
    
    def Initialize(self):
        """Initialize the workbench."""
        # Create command list
        self.command_list = ["AIChatToggle"]
        
        # Register commands
        FreeCADGui.addCommand("AIChatToggle", AIChatCommand())
        
        # Create menu
        self.appendMenu("AI Chat", self.command_list)
        
        # Create toolbar
        self.appendToolbar("AI Chat", self.command_list)
    
    def Activated(self):
        """Called when workbench is activated."""
        pass
    
    def Deactivated(self):
        """Called when workbench is deactivated."""
        pass
    
    def GetClassName(self):
        """Return the workbench class name."""
        return "Gui::PythonWorkbench"

class AIChatCommand:
    """Command to toggle the AI chat widget."""
    
    def GetResources(self):
        """Return command resources."""
        return {
            'Pixmap': """
                /* XPM */
                static char * chat_icon_xpm[] = {
                "16 16 3 1",
                " 	c None",
                ".	c #000000",
                "+	c #FFFFFF",
                "                ",
                "     .....      ",
                "   ..+++++..    ",
                "  .+++++++++.   ",
                " .+++++++++++.  ",
                ".++++++++++++.  ",
                ".++++++++++++.  ",
                ".++++++++++++.  ",
                ".++++++++++++.  ",
                " .+++++++++++.  ",
                "  .+++++++++.   ",
                "   ..+++++..    ",
                "     .....      ",
                "      ...       ",
                "       .        ",
                "                "};
                """,
            'MenuText': "Toggle AI Chat",
            'ToolTip': "Show/hide the AI chat interface"
        }
    
    def Activated(self):
        """Execute the command."""
        global chat_widget
        
        if chat_widget is None:
            # Create new chat widget instance
            chat_widget = ChatWidget(FreeCADGui.getMainWindow())
        
        # Toggle visibility
        if chat_widget.isVisible():
            chat_widget.hide()
        else:
            chat_widget.show()
    
    def IsActive(self):
        """Return True to enable the command, False to disable it."""
        return True

def initialize():
    """Initialize the workbench when FreeCAD starts."""
    FreeCADGui.addWorkbench(AIChatWorkbench())

# Initialize the workbench
initialize()
