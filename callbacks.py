"""
Callbacks do Dash para o Fitness Metrics Dashboard
"""
from dash import Input, Output, State, html
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
from components import *
from pages import *
from utils import *

# Callback para trocar conteúdo das abas
def register_tab_callbacks(app):
    @app.callback(
        Output("tab-content", "children"),
        Input("tabs", "active_tab")
    )
    def render_tab_content(active_tab):
        if active_tab == "dashboard":
            return render_dashboard()
        elif active_tab == "calendar":
            return render_calendar()
        elif active_tab == "goals":
            return render_goals()
        elif active_tab == "config":
            return render_config()
        return html.P("Selecione uma aba.")

# Callbacks para exportação de dados
def register_export_callbacks(app):
    @app.callback(
        Output("download-metrics", "data"),
        Input("btn-export-metrics", "n_clicks"),
        prevent_initial_call=True
    )
    def export_metrics_csv(n_clicks):
        """Exporta métricas para CSV"""
        if n_clicks:
            metrics = load_metrics()
            csv_data, _ = export_to_csv(metrics, [])
            if csv_data:
                return dict(content=csv_data, filename=f"fitness_metrics_{datetime.now().strftime('%Y%m%d')}.csv")
        return None

    @app.callback(
        Output("download-workouts", "data"),
        Input("btn-export-workouts", "n_clicks"),
        prevent_initial_call=True
    )
    def export_workouts_csv(n_clicks):
        """Exporta atividades para CSV"""
        if n_clicks:
            workouts = load_workouts()
            _, csv_data = export_to_csv([], workouts)
            if csv_data:
                return dict(content=csv_data, filename=f"workouts_{datetime.now().strftime('%Y%m%d')}.csv")
        return None

# Callback para modo escuro
def register_dark_mode_callbacks(app):
    @app.callback(
        [Output('app-container', 'style'),
         Output('dark-mode-toggle', 'children'),
         Output('dark-mode-store', 'data')],
        [Input('dark-mode-toggle', 'n_clicks')],
        [State('dark-mode-store', 'data')]
    )
    def toggle_dark_mode(n_clicks, current_dark_mode):
        if n_clicks and n_clicks > 0:
            is_dark = not current_dark_mode
            if is_dark:
                return [
                    {'backgroundColor': '#242428', 'color': '#FFFFFF'},
                    '☀️ Modo Claro',
                    True
                ]
            else:
                return [
                    {'backgroundColor': 'white', 'color': '#212529'},
                    '🌙 Modo Escuro',
                    False
                ]
        return [
            {'backgroundColor': 'white', 'color': '#212529'},
            '🌙 Modo Escuro',
            False
        ]

# Callback para atualizar badge de última sincronização
def register_update_callbacks(app):
    @app.callback(
        Output('last-update-badge', 'children'),
        Input('url', 'pathname'),
        Input('tabs', 'active_tab')
    )
    def update_last_sync_badge(pathname, active_tab):
        try:
            # Verificar se há dados recentes
            metrics = load_metrics()
            workouts = load_workouts()

            if metrics and workouts:
                last_metric_date = max(m['date'] for m in metrics)
                last_workout_date = max(
                    datetime.strptime(w.get('startTimeLocal', w.get('startTime', '')), "%Y-%m-%d %H:%M:%S").date()
                    for w in workouts if w.get('startTimeLocal') or w.get('startTime')
                )

                most_recent = max(last_metric_date, str(last_workout_date))

                # Calcular dias desde última atualização
                days_since = (datetime.now().date() - datetime.fromisoformat(most_recent).date()).days

                if days_since == 0:
                    return "🔄 Hoje"
                elif days_since == 1:
                    return "🔄 Ontem"
                elif days_since <= 7:
                    return f"🔄 {days_since} dias atrás"
                else:
                    return f"🔄 {most_recent}"
            else:
                return "🔄 Nenhuma sincronização ainda"
        except Exception as e:
            return "🔄 Status desconhecido"

# Função para registrar todos os callbacks
def register_all_callbacks(app):
    register_tab_callbacks(app)
    register_export_callbacks(app)
    register_dark_mode_callbacks(app)
    register_update_callbacks(app)