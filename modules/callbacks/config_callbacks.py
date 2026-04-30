"""
Callbacks for configuration and settings.

Handles: Save credentials, save config, save zones, etc.
"""
import dash
from dash import Output, Input, State, html


def register_config_callbacks(app):
    """Register all configuration-related callbacks."""
    
    @app.callback(
        Output("credentials-status", "children"),
        Input("save-credentials-btn", "n_clicks"),
        State("garmin-email", "value"),
        State("garmin-password", "value"),
        prevent_initial_call=True
    )
    def save_credentials(n_clicks, email, password):
        """Salva credenciais do Garmin"""
        if n_clicks and email and password:
            try:
                from storage import save_credentials
                save_credentials(email, password)
                return html.Div("✅ Credenciais salvas com sucesso!", className="alert alert-success mt-3")
            except Exception as e:
                return html.Div(f"❌ Erro ao salvar credenciais: {str(e)}", className="alert alert-danger mt-3")
        return html.Div()
    
    @app.callback(
        Output("config-status", "children"),
        Input("save-config-btn", "n_clicks"),
        State("config-age", "value"),
        State("config-ftp", "value"),
        State("config-lthr", "value"),
        State("config-max-hr", "value"),
        State("config-rest-hr", "value"),
        prevent_initial_call=True
    )
    def save_configuration(n_clicks, age, ftp, lthr, max_hr, rest_hr):
        """Salva configurações do usuário"""
        if n_clicks:
            try:
                from storage import load_config, save_config
                config = load_config()
                
                if age:
                    config['age'] = int(age)
                if ftp:
                    config['ftp'] = int(ftp)
                if lthr:
                    config['lthr'] = int(lthr)
                if max_hr:
                    config['max_hr'] = int(max_hr)
                if rest_hr:
                    config['rest_hr'] = int(rest_hr)
                
                save_config(config)
                return html.Div("✅ Configurações salvas com sucesso!", className="alert alert-success mt-3")
            except Exception as e:
                return html.Div(f"❌ Erro ao salvar configurações: {str(e)}", className="alert alert-danger mt-3")
        return html.Div()
