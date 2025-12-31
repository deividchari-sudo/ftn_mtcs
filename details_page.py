"""
details_page.py - Página de Mais Detalhes
Contém funções para renderizar seções que não agregam ao dashboard principal:
- Alertas Inteligentes
- Recordes Pessoais
- Conquistas Desbloqueadas
- Exportar Dados
- Referências
- Aprendizado
- Evolução Mensal
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go


def create_records_section(metrics, workouts, calculate_personal_records):
    """Renderiza seção de Recordes Pessoais"""
    records = calculate_personal_records(metrics, workouts) if workouts else None

    def _format_value(value, unit: str) -> str:
        try:
            value = float(value)
        except Exception:
            return str(value)
        if unit in ["pts", "h"]:
            return f"{value:.2f}"
        if unit in ["TSS"]:
            return f"{value:.0f}"
        return f"{value:.1f}"

    header = dbc.Row([
        dbc.Col([
            html.Div([
                html.H3("🏆 Recordes Pessoais", className="mb-3 text-warning", style={"fontWeight": "700"}),
                html.P("Seus melhores resultados e conquistas", className="text-muted mb-4", style={"fontSize": "0.95rem"}),
            ], className="text-center")
        ])
    ])

    if not workouts or not records:
        body = dbc.Alert([
            html.H5("🏆 Sem Recordes Ainda", className="alert-heading mb-2"),
            html.P("Continue treinando para estabelecer seus recordes pessoais!", className="mb-0"),
        ], color="light", className="shadow-sm", style={"borderRadius": "12px"})
    else:
        cards = []
        for record in records.values():
            unit = record.get("unit", "")
            value = record.get("value", 0)
            cards.append(
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            html.Div([
                                html.Div(record.get("icon", "🏆"), style={"fontSize": "2.5rem"}, className="mb-2"),
                                html.H6(record.get("label", ""), className="text-muted mb-2", style={"fontSize": "0.8rem", "fontWeight": "600"}),
                                html.H3([
                                    _format_value(value, unit),
                                    html.Small(f" {unit}", className="text-muted", style={"fontSize": "0.6em"}),
                                ], className="mb-2", style={"fontWeight": "800"}),
                                html.Div([
                                    html.Small(f"📅 {record.get('date', 'N/A')}", className="text-muted d-block", style={"fontSize": "0.75rem"}),
                                    html.Small(record.get("activity", ""), className="text-primary d-block mt-1", style={"fontSize": "0.7rem", "fontWeight": "500"}) if record.get("activity") else None,
                                ]),
                            ], className="text-center")
                        ),
                        className="shadow-sm border-0 h-100",
                        style={
                            "borderRadius": "12px",
                            "background": "linear-gradient(135deg, #fff 0%, #f8f9fa 100%)",
                            "borderTop": "4px solid #ffc107",
                        },
                    ),
                    xs=12,
                    sm=6,
                    md=4,
                    lg=3,
                    xl=2,
                    className="mb-3",
                )
            )
        body = dbc.Row(cards, justify="center", className="g-3")

    return [
        header,
        dbc.Row([
            dbc.Col([body])
        ], className="mb-5"),
    ]


def create_achievements_section(metrics, workouts, calculate_achievements):
    """Renderiza seção de Conquistas Desbloqueadas"""
    achievements = calculate_achievements(metrics, workouts) if workouts else None
    
    return [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("🏅 Conquistas Gamificadas", className="mb-3 text-warning", style={'fontWeight': '700'}),
                    html.P("Desbloqueie conquistas alcançando marcos de treinamento", className="text-muted mb-4", style={'fontSize': '0.95rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            *[dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div(achievement['icon'], style={'fontSize': '2.5rem', 'marginBottom': '10px'}),
                            html.H5(achievement['title'], className="card-title", style={'fontWeight': '700'}),
                            html.P(achievement['description'], className="card-text text-muted small"),
                            html.Hr(className="my-2"),
                            dbc.Progress(
                                value=achievement['progress'],
                                className="mb-2",
                                style={'height': '6px'}
                            ),
                            html.P([
                                "✅ Desbloqueada" if achievement['unlocked'] else "🔒 Bloqueada"
                            ], className="text-center small", style={'fontWeight': '600'})
                        ], className="text-center")
                    ])
                ], className="shadow-sm border-0", style={
                    'borderRadius': '12px',
                    'background': 'linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%)' if achievement['unlocked'] else 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
                    'borderTop': f"4px solid {'#28a745' if achievement['unlocked'] else '#6c757d'}"
                })
            ], xs=12, sm=6, md=4, lg=3, xl=2, className="mb-3") for achievement in (achievements or [])]
        ], justify="center", className="mb-5 g-3")
    ]


def create_monthly_evolution_section(metrics, workouts, create_monthly_trend_chart):
    """Renderiza seção de Evolução Mensal"""
    return [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("📊 Evolução Mensal", className="mb-3 text-primary", style={'fontWeight': '700'}),
                    html.P("Visualize a distribuição de treinos e evolução do CTL nos últimos 6 meses", className="text-muted mb-4", style={'fontSize': '0.95rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_monthly_trend_chart(metrics, workouts),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-5")
    ]


def create_references_section():
    """Renderiza seção de Referências para Ironman"""
    return [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("📚 Referências para Ironman", className="mb-3 text-info", style={'fontWeight': '700'}),
                    html.P("Diretrizes baseadas em pesquisa científica para otimizar seu desempenho", className="text-muted mb-4", style={'fontSize': '0.95rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🎯 Métricas Alvo por Perfil", className="mb-3", style={'fontWeight': '700'}),
                        html.Div([
                            html.Div([
                                html.H6("Iniciante", style={'fontWeight': '600', 'color': '#6c757d'}),
                                html.Ul([
                                    html.Li("CTL: 30-40 pts"),
                                    html.Li("ATL: 25-35 pts"),
                                    html.Li("Volume: 8-10 h/semana")
                                ])
                            ], className="mb-3"),
                            html.Div([
                                html.H6("Intermediário", style={'fontWeight': '600', 'color': '#17a2b8'}),
                                html.Ul([
                                    html.Li("CTL: 40-60 pts"),
                                    html.Li("ATL: 35-50 pts"),
                                    html.Li("Volume: 12-16 h/semana")
                                ])
                            ], className="mb-3"),
                            html.Div([
                                html.H6("Avançado", style={'fontWeight': '600', 'color': '#28a745'}),
                                html.Ul([
                                    html.Li("CTL: 60-80 pts"),
                                    html.Li("ATL: 50-70 pts"),
                                    html.Li("Volume: 16-20 h/semana")
                                ])
                            ]),
                        ])
                    ])
                ], className="shadow-sm border-0 mb-3", style={'borderRadius': '12px'}),
                
                dbc.Card([
                    dbc.CardBody([
                        html.H6("⚖️ Equilíbrio TSB Ideal", className="mb-3", style={'fontWeight': '700'}),
                        html.Div([
                            html.Div([
                                html.Strong("TSB > +10:"),
                                html.P("Muito descansado - aumentar volume")
                            ], className="mb-2"),
                            html.Div([
                                html.Strong("+5 a +10:"),
                                html.P("Descansado - ideal para competição")
                            ], className="mb-2"),
                            html.Div([
                                html.Strong("-10 a +5:"),
                                html.P("Ideal para treino - balanço perfeito")
                            ], className="mb-2"),
                            html.Div([
                                html.Strong("-20 a -10:"),
                                html.P("Fatigado - necessário recuperação")
                            ], className="mb-2"),
                            html.Div([
                                html.Strong("< -20:"),
                                html.P("Sobretreinado - risco de lesão")
                            ])
                        ])
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ], md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H6("🏊‍♂️ Distribuição Recomendada", className="mb-3", style={'fontWeight': '700'}),
                        html.Div([
                            html.Div([
                                html.Strong("Natação: 10-15%"),
                                html.P("6-12 h/semana", className="text-muted small")
                            ], className="mb-3"),
                            html.Div([
                                html.Strong("Ciclismo: 40-50%"),
                                html.P("6-10 h/semana", className="text-muted small")
                            ], className="mb-3"),
                            html.Div([
                                html.Strong("Corrida: 30-40%"),
                                html.P("5-8 h/semana", className="text-muted small")
                            ], className="mb-3"),
                            html.Div([
                                html.Strong("Força: 5-10%"),
                                html.P("2-4 h/semana", className="text-muted small")
                            ]),
                        ])
                    ])
                ], className="shadow-sm border-0 mb-3", style={'borderRadius': '12px'}),
                
                dbc.Card([
                    dbc.CardBody([
                        html.H6("📈 Periodização Macrociclo (26-30 semanas)", className="mb-3", style={'fontWeight': '700'}),
                        html.Div([
                            html.Div([
                                html.Strong("Base (6-8 semanas):"),
                                html.P("Desenvolvimento geral, CTL ↑", className="text-muted small")
                            ], className="mb-2"),
                            html.Div([
                                html.Strong("Construção (4-6 semanas):"),
                                html.P("Especificidade, VO2 max", className="text-muted small")
                            ], className="mb-2"),
                            html.Div([
                                html.Strong("Pico (4-6 semanas):"),
                                html.P("Simulações, intensidade", className="text-muted small")
                            ], className="mb-2"),
                            html.Div([
                                html.Strong("Recuperação/Taper (2 semanas):"),
                                html.P("Redução volume, manutenção intensidade", className="text-muted small")
                            ])
                        ])
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ], md=6)
        ], className="mb-5")
    ]


def create_learning_section():
    """Renderiza seção de Aprendizado"""
    return [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("📖 Aprendizado", className="mb-3 text-success", style={'fontWeight': '700'}),
                    html.P("Conceitos e explicações sobre métricas de treinamento", className="text-muted mb-4", style={'fontSize': '0.95rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Accordion([
                    dbc.AccordionItem([
                        html.P("O CTL representa a carga de treino cumulativa dos últimos 42 dias. Um CTL maior indica melhor forma aeróbica e capacidade de treinar em intensidades altas. Atletas bem treinados têm CTL entre 50-80 pontos."),
                        html.P("Para aumentar CTL, você precisa realizar treinos consistentes com volume adequado e respeitar os períodos de recuperação."),
                    ], title="💪 O que é CTL (Chronic Training Load)?"),
                    dbc.AccordionItem([
                        html.P("ATL mede a fadiga acumulada dos últimos 7 dias. Valores altos indicam cansaço acumulado, enquanto valores baixos indicam boa recuperação."),
                        html.P("Uma estratégia eficaz é manter ATL entre 40-60 durante períodos de treino base, e reduzir para 30-40 na semana antes de uma competição."),
                    ], title="😴 O que é ATL (Acute Training Load)?"),
                    dbc.AccordionItem([
                        html.P("TSB = CTL - ATL. É o indicador mais importante para saber seu estado atual:"),
                        html.Ul([
                            html.Li("TSB > +10: Muito descansado (aumentar volume)"),
                            html.Li("TSB +5 a +10: Descansado (ideal para competição)"),
                            html.Li("TSB -10 a +5: Ótimo para treinar (balanço equilibrado)"),
                            html.Li("TSB -20 a -10: Fatigado (priorizar recuperação)"),
                            html.Li("TSB < -20: Sobretreinado (alto risco de lesão)")
                        ]),
                    ], title="⚖️ O que é TSB (Training Stress Balance)?"),
                    dbc.AccordionItem([
                        html.P("TSS quantifica o esforço de um único treino. Usa duração e intensidade. Uma sessão típica gera 50-150 TSS."),
                        html.P("Exemplo: 1 hora de treino no limiar com FTP 250W = ~80-100 TSS."),
                    ], title="📊 O que é TSS (Training Stress Score)?"),
                    dbc.AccordionItem([
                        html.P("TRIMP (TRaining IMPulse) mede a carga diária de treino usando frequência cardíaca. É a base para calcular CTL e ATL."),
                        html.P("Fórmula básica: TRIMP = duração (min) × FC_reserve% × 0.64 × e^(1.92 × FC_reserve%)"),
                    ], title="❤️ O que é TRIMP (Training Impulse)?"),
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-5")
    ]


def create_export_section():
    """Renderiza seção de Exportar Dados"""
    return [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("📥 Exportar Dados", className="mb-3 text-primary", style={'fontWeight': '700'}),
                    html.P("Baixe seus dados em formato CSV para análise em Excel ou ferramentas externas", className="text-muted mb-4", style={'fontSize': '0.95rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H5("📊 Métricas de Fitness", className="mb-2"),
                                    html.P("CTL, ATL, TSB e carga diária dos últimos 42 dias", className="text-muted small"),
                                    html.Hr(className="my-2"),
                                    dbc.Button(
                                        [html.I(className="bi bi-download me-2"), "Baixar CSV"],
                                        id="btn-export-metrics",
                                        color="primary",
                                        className="w-100",
                                        style={'borderRadius': '8px'}
                                    )
                                ])
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                html.Div([
                                    html.H5("⏃ Atividades de Treino", className="mb-2"),
                                    html.P("Todas as atividades com distância, duração, TSS e modalidade", className="text-muted small"),
                                    html.Hr(className="my-2"),
                                    dbc.Button(
                                        [html.I(className="bi bi-download me-2"), "Baixar CSV"],
                                        id="btn-export-workouts",
                                        color="success",
                                        className="w-100",
                                        style={'borderRadius': '8px'}
                                    )
                                ])
                            ], md=6)
                        ]),
                        html.Hr(className="my-3"),
                        dcc.Download(id="download-metrics"),
                        dcc.Download(id="download-workouts"),
                        html.Div([
                            html.Small([
                                "💡 ",
                                html.Strong("Dica: "),
                                "Use os dados exportados para criar gráficos personalizados em Excel, Google Sheets ou Power BI"
                            ], className="text-muted")
                        ])
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-5")
    ]


def render_details(
    metrics,
    workouts,
    config,
    *,
    calculate_personal_records,
    calculate_achievements,
    create_monthly_trend_chart,
):
    """Renderiza a página completa de Mais Detalhes"""
    metrics = metrics or []
    workouts = workouts or []
    config = config or {}

    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("📋 Mais Detalhes", className="text-primary mb-2", style={'fontWeight': '700'}),
                    html.P("Análise aprofundada, recordes, referências e exportação de dados", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                ], className="text-center py-4")
            ])
        ], className="bg-light rounded-3 mb-5"),
        
        # Recordes Pessoais
        *create_records_section(metrics, workouts, calculate_personal_records),
        
        # Conquistas
        *create_achievements_section(metrics, workouts, calculate_achievements),
        
        # Evolução Mensal
        *create_monthly_evolution_section(metrics, workouts, create_monthly_trend_chart),
        
        # Referências
        *create_references_section(),
        
        # Aprendizado
        *create_learning_section(),
        
        # Exportar
        *create_export_section()
    ], fluid=False, style={'maxWidth': '1400px'})
