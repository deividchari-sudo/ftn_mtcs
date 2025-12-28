"""
Layouts e estrutura da interface do Fitness Metrics Dashboard
"""
import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime

def create_main_layout():
    """Cria o layout principal da aplicação"""
    return html.Div(id='app-container', children=[
        # Store para modo escuro
        dcc.Store(id='dark-mode-store', data=False),

        # Location para forçar reload
        dcc.Location(id='url', refresh=False),

        # Botão de toggle modo escuro
        html.Button(
            id='dark-mode-toggle',
            children='🌙 Modo Escuro',
            className='dark-mode-toggle',
            n_clicks=0
        ),

        # Helper de atalhos (sempre visível)
        html.Div([
            html.Div([
                "💡 ",
                html.Kbd("Ctrl+D"),
                " Modo Escuro | ",
                html.Kbd("Ctrl+K"),
                " Atalhos"
            ], style={
                'position': 'fixed',
                'bottom': '20px',
                'left': '20px',
                'zIndex': '9998',
                'background': 'rgba(45, 45, 49, 0.9)',
                'color': 'white',
                'padding': '8px 16px',
                'borderRadius': '8px',
                'fontSize': '0.75rem',
                'boxShadow': '0 4px 16px rgba(0,0,0,0.3)'
            })
        ]),

        dbc.Container([

        # Header com informações úteis
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.H1("💪 Fitness Metrics Dashboard", className="mb-2", style={'fontWeight': '800', 'display': 'inline-block'}),
                        html.Span([
                            html.Span("ℹ️", className="tooltip-icon", style={
                                'display': 'inline-flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'width': '22px',
                                'height': '22px',
                                'borderRadius': '50%',
                                'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                                'color': 'white',
                                'fontSize': '12px',
                                'fontWeight': 'bold',
                                'marginLeft': '10px',
                                'cursor': 'help'
                            }),
                            html.Span([
                                html.Strong("CTL (Chronic Training Load):"), " Carga de treino acumulada nos últimos 42 dias. Representa sua forma física atual.",
                                html.Br(), html.Br(),
                                html.Strong("ATL (Acute Training Load):"), " Carga de treino dos últimos 7 dias. Indica o cansaço recente.",
                                html.Br(), html.Br(),
                                html.Strong("TSB (Training Stress Balance):"), " CTL - ATL. Valores negativos = fatigado, positivos = descansado.",
                                html.Br(), html.Br(),
                                html.Strong("TSS (Training Stress Score):"), " Pontuação de estresse do treino baseado em intensidade e duração."
                            ], style={
                                'visibility': 'hidden',
                                'width': '320px',
                                'backgroundColor': '#2D2D31',
                                'color': '#FFFFFF',
                                'textAlign': 'left',
                                'borderRadius': '8px',
                                'padding': '16px',
                                'position': 'absolute',
                                'zIndex': '10000',
                                'bottom': '130%',
                                'left': '50%',
                                'marginLeft': '-160px',
                                'opacity': '0',
                                'transition': 'opacity 0.3s',
                                'boxShadow': '0 4px 16px rgba(0,0,0,0.4)',
                                'fontSize': '0.85rem',
                                'lineHeight': '1.5'
                            }, className='tooltip-text')
                        ], style={'position': 'relative', 'display': 'inline-block'}, className='info-tooltip')
                    ]),
                    html.P([
                        "Análise completa de treinamento | ",
                        html.Span(f"📅 {datetime.now().strftime('%d/%m/%Y')}", className="me-3"),
                        html.Span("🔥 Sistema de Conquistas", className="me-3"),
                        html.Span("📊 Exportação CSV", className="me-3"),
                        html.Span("🔮 Previsões IA", className="me-3"),
                        html.Span(id='last-update-badge', children=[
                            "🔄 Última atualização: Carregando..."
                        ], className="last-update-badge")
                    ], className="text-muted", style={'fontSize': '0.9rem'})
                ], className="text-center py-3")
            ])
        ], className="mb-3"),

        html.Hr(className="mb-4"),

        # Navegação por abas
        dbc.Tabs([
            dbc.Tab(label="📊 Dashboard", tab_id="dashboard"),
            dbc.Tab(label="📅 Calendário", tab_id="calendar"),
            dbc.Tab(label="🎯 Metas", tab_id="goals"),
            dbc.Tab(label="⚙️ Configuração", tab_id="config")
        ], id="tabs", active_tab="dashboard"),

        # Conteúdo das abas
        html.Div(id="tab-content", className="mt-4")
        ], fluid=False, style={'maxWidth': '1400px'})
    ])