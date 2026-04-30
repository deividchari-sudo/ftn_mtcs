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
                    html.P("Baixe seus dados em formato CSV ou relatórios profissionais em PDF", className="text-muted mb-4", style={'fontSize': '0.95rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📄 Relatórios PDF", className="mb-0 text-white"), style={'backgroundColor': '#1f77b4'}),
                    dbc.CardBody([
                        html.P("Gere relatórios profissionais em PDF com análise completa de métricas e treinos", className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("📅 Relatório Semanal", className="mb-2"),
                                    html.P("Últimos 7 dias com resumo, métricas e recomendações", className="text-muted small"),
                                    dbc.Button(
                                        [html.I(className="bi bi-file-earmark-pdf me-2"), "Gerar PDF Semanal"],
                                        id="btn-export-weekly-pdf",
                                        color="primary",
                                        className="w-100",
                                        style={'borderRadius': '8px'}
                                    )
                                ])
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                html.Div([
                                    html.H6("📊 Relatório Mensal", className="mb-2"),
                                    html.P("Análise completa do mês com evolução e conquistas", className="text-muted small"),
                                    dbc.Button(
                                        [html.I(className="bi bi-file-earmark-pdf me-2"), "Gerar PDF Mensal"],
                                        id="btn-export-monthly-pdf",
                                        color="info",
                                        className="w-100",
                                        style={'borderRadius': '8px'}
                                    )
                                ])
                            ], md=6)
                        ]),
                        html.Div(id="pdf-export-status", className="mt-3")
                    ])
                ], className="shadow-sm border-0 mb-4", style={'borderRadius': '12px'})
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("📊 Exportar CSV", className="mb-0 text-white"), style={'backgroundColor': '#2ecc71'}),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("📈 Métricas de Fitness", className="mb-2"),
                                    html.P("CTL, ATL, TSB e carga diária dos últimos 42 dias", className="text-muted small"),
                                    dbc.Button(
                                        [html.I(className="bi bi-download me-2"), "Baixar CSV"],
                                        id="btn-export-metrics",
                                        color="success",
                                        className="w-100",
                                        style={'borderRadius': '8px'}
                                    )
                                ])
                            ], md=6, className="mb-3"),
                            dbc.Col([
                                html.Div([
                                    html.H6("🏃 Atividades de Treino", className="mb-2"),
                                    html.P("Todas as atividades com distância, duração, TSS e modalidade", className="text-muted small"),
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
                        dcc.Download(id="download-weekly-pdf"),
                        dcc.Download(id="download-monthly-pdf"),
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


def create_advanced_analysis_section(workouts, config):
    """Renderiza seção de Análise Avançada de Treinos"""
    
    # Nota: Esta seção mostra exemplos de análises que seriam possíveis
    # com dados stream de potência e pace (quando disponíveis)
    
    return [
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("💪 Análise Avançada de Treinos", className="mb-3 text-primary", style={'fontWeight': '700'}),
                    html.P("Métricas profissionais para análise aprofundada de performance", className="text-muted mb-4", style={'fontSize': '0.95rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📊 Métricas Avançadas Disponíveis", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            # Ciclismo
                            dbc.Col([
                                html.Div([
                                    html.H6([html.I(className="fas fa-bicycle me-2"), "Ciclismo"], className="text-primary mb-3"),
                                    html.Ul([
                                        html.Li([html.Strong("NP (Normalized Power): "), "Potência normalizada que considera a fadiga não-linear"]),
                                        html.Li([html.Strong("IF (Intensity Factor): "), "Intensidade relativa ao FTP (NP/FTP)"]),
                                        html.Li([html.Strong("VI (Variability Index): "), "Consistência do esforço (NP/Avg Power)"]),
                                        html.Li([html.Strong("TSS Preciso: "), "Training Stress Score calculado com NP"]),
                                        html.Li([html.Strong("Distribuição de Zonas: "), "Tempo gasto em cada zona de potência"]),
                                        html.Li([html.Strong("Power Curve: "), "Picos de 5s, 1min, 5min, 20min"])
                                    ], className="small")
                                ], className="mb-4")
                            ], md=4),
                            
                            # Corrida
                            dbc.Col([
                                html.Div([
                                    html.H6([html.I(className="fas fa-running me-2"), "Corrida"], className="text-success mb-3"),
                                    html.Ul([
                                        html.Li([html.Strong("GAP (Grade Adjusted Pace): "), "Pace ajustado por elevação do terreno"]),
                                        html.Li([html.Strong("Pace Variability: "), "Coeficiente de variação do pace (CV%)"]),
                                        html.Li([html.Strong("Distribuição de Zonas: "), "Tempo em cada zona de pace"]),
                                        html.Li([html.Strong("Consistência: "), "Análise de estabilidade do ritmo"]),
                                        html.Li([html.Strong("Min/Max Pace: "), "Paces mais rápido e mais lento"]),
                                        html.Li([html.Strong("Desvio Padrão: "), "Variação do pace durante o treino"])
                                    ], className="small")
                                ], className="mb-4")
                            ], md=4),
                            
                            # Natação
                            dbc.Col([
                                html.Div([
                                    html.H6([html.I(className="fas fa-swimmer me-2"), "Natação"], className="text-info mb-3"),
                                    html.Ul([
                                        html.Li([html.Strong("SWOLF: "), "Índice de eficiência técnica (braçadas + tempo)"]),
                                        html.Li([html.Strong("Braçadas/25m: "), "Eficiência de braçada por piscina"]),
                                        html.Li([html.Strong("Pace Consistency: "), "Consistência do pace por volta"]),
                                        html.Li([html.Strong("Velocidade (m/s): "), "Velocidade média na água"]),
                                        html.Li([html.Strong("DPS (Distance Per Stroke): "), "Distância por braçada"]),
                                        html.Li([html.Strong("Stroke Rate: "), "Frequência de braçada (SPM)"])
                                    ], className="small")
                                ])
                            ], md=4)
                        ])
                    ])
                ], className="shadow-sm border-0 mb-4", style={'borderRadius': '12px'})
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5("📖 Guia de Interpretação", className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Intensity Factor (IF)", className="mb-2"),
                                html.Ul([
                                    html.Li([html.Strong("< 0.75: "), "Recuperação/Endurance"], className="small"),
                                    html.Li([html.Strong("0.75-0.85: "), "Tempo"], className="small"),
                                    html.Li([html.Strong("0.85-0.95: "), "Sweetspot"], className="small"),
                                    html.Li([html.Strong("0.95-1.05: "), "Threshold"], className="small"),
                                    html.Li([html.Strong("> 1.05: "), "VO2max+"], className="small")
                                ])
                            ], md=3),
                            dbc.Col([
                                html.H6("Variability Index (VI)", className="mb-2"),
                                html.Ul([
                                    html.Li([html.Strong("1.00-1.05: "), "Muito consistente (TT, indoor)"], className="small"),
                                    html.Li([html.Strong("1.05-1.10: "), "Consistente"], className="small"),
                                    html.Li([html.Strong("1.10-1.15: "), "Moderadamente variável"], className="small"),
                                    html.Li([html.Strong("> 1.15: "), "Muito variável (critério, montanha)"], className="small")
                                ])
                            ], md=3),
                            dbc.Col([
                                html.H6("Pace Variability (CV%)", className="mb-2"),
                                html.Ul([
                                    html.Li([html.Strong("< 5%: "), "Muito consistente"], className="small"),
                                    html.Li([html.Strong("5-10%: "), "Consistente"], className="small"),
                                    html.Li([html.Strong("10-15%: "), "Moderadamente variável"], className="small"),
                                    html.Li([html.Strong("> 15%: "), "Muito variável"], className="small")
                                ])
                            ], md=3),
                            dbc.Col([
                                html.H6("SWOLF (Natação)", className="mb-2"),
                                html.Ul([
                                    html.Li([html.Strong("< 35: "), "Excelente eficiência"], className="small"),
                                    html.Li([html.Strong("35-40: "), "Boa eficiência"], className="small"),
                                    html.Li([html.Strong("40-45: "), "Eficiência moderada"], className="small"),
                                    html.Li([html.Strong("> 45: "), "Precisa melhorar técnica"], className="small")
                                ])
                            ], md=3)
                        ])
                    ])
                ], className="shadow-sm border-0 mb-4", style={'borderRadius': '12px'})
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    html.Strong("Nota: "),
                    "As análises avançadas requerem dados detalhados de stream (potência por segundo, pace por segundo, etc.) ",
                    "que são obtidos quando disponíveis nas atividades do Garmin. O módulo ",
                    html.Code("power_pace_analysis.py"),
                    " está pronto para processar esses dados quando sincronizados."
                ], color="info", className="mb-4")
            ])
        ])
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
        
        # Análise Avançada
        *create_advanced_analysis_section(workouts, config),
        
        # Aprendizado
        *create_learning_section(),
        
        # Exportar
        *create_export_section()
    ], fluid=False, style={'maxWidth': '1400px'})
