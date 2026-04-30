"""
Callbacks for training zones modal.

Handles: Open/close zones modal, save zones
"""
import dash
from dash import Output, Input, State, html


def register_zones_callbacks(app):
    """Register all zones-related callbacks."""
    
    @app.callback(
        Output('zones-modal', 'is_open'),
        [Input('view-zones-btn', 'n_clicks'),
         Input('close-zones-modal', 'n_clicks')],
        [State('zones-modal', 'is_open')]
    )
    def toggle_zones_modal(view_clicks, close_clicks, is_open):
        """Abre/fecha modal de zonas"""
        if view_clicks or close_clicks:
            return not is_open
        return is_open
    
    @app.callback(
        Output('config-status', 'children', allow_duplicate=True),
        Input('save-zones-btn', 'n_clicks'),
        [State('config-swim-css', 'value'),
         State('config-run-threshold', 'value'),
         State('config-cycling-ftp', 'value')],
        prevent_initial_call=True
    )
    def save_training_zones(n_clicks, swim_css, run_threshold, cycling_ftp):
        """Salva zonas de treinamento"""
        if n_clicks:
            try:
                from storage import load_config, save_config
                from utils.common import _parse_mmss_to_seconds
                
                config = load_config()
                
                if swim_css:
                    config['swim_css'] = _parse_mmss_to_seconds(swim_css, default_seconds=100)
                if run_threshold:
                    config['threshold_pace_running'] = _parse_mmss_to_seconds(run_threshold, default_seconds=300)
                if cycling_ftp:
                    config['ftp'] = int(cycling_ftp)
                
                save_config(config)
                return html.Div("✅ Zonas de treinamento salvas!", className="alert alert-success mt-3")
            except Exception as e:
                return html.Div(f"❌ Erro: {str(e)}", className="alert alert-danger mt-3")
        
        return dash.no_update
