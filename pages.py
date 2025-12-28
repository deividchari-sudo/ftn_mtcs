"""
Páginas e conteúdo das abas do dashboard
"""
import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime
from components import *
from utils import *

def render_dashboard():
    """Renderiza o conteúdo da aba Dashboard"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("📊 Dashboard - Em desenvolvimento"),
                html.P("Conteúdo do dashboard será implementado aqui.")
            ])
        ])
    ])

def render_calendar():
    """Renderiza o conteúdo da aba Calendário"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("📅 Calendário - Em desenvolvimento"),
                html.P("Conteúdo do calendário será implementado aqui.")
            ])
        ])
    ])

def render_goals():
    """Renderiza o conteúdo da aba Metas"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🎯 Metas - Em desenvolvimento"),
                html.P("Conteúdo das metas será implementado aqui.")
            ])
        ])
    ])

def render_config():
    """Renderiza o conteúdo da aba Configuração"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("⚙️ Configuração - Em desenvolvimento"),
                html.P("Conteúdo da configuração será implementado aqui.")
            ])
        ])
    ])