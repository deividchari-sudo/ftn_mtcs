"""
Callback Registry

Centraliza o registro de todos os callbacks do Dash.
Importe e chame register_all_callbacks(app) em app.py
"""
from .export_callbacks import register_export_callbacks
from .config_callbacks import register_config_callbacks
from .calendar_callbacks import register_calendar_callbacks
from .zones_callbacks import register_zones_callbacks
from .chat_callbacks import register_chat_callbacks


def register_all_callbacks(app):
    """
    Register all Dash callbacks.
    
    Args:
        app: Dash application instance
    """
    # Export callbacks
    register_export_callbacks(app)
    
    # Configuration callbacks
    register_config_callbacks(app)
    
    # Calendar callbacks
    register_calendar_callbacks(app)
    
    # Zones callbacks
    register_zones_callbacks(app)
    
    # Chat callbacks
    register_chat_callbacks(app)
    
    # Add more callback groups here as needed
    
    print("✅ All callbacks registered successfully")
