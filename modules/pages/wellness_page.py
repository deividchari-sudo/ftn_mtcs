"""
Módulo para renderizar a aba de Saúde & Wellness com dados do Garmin.
Versão robusta com tratamento de dados incompletos.
"""
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from storage import load_health_metrics, load_training_status
import json
import logging

logger = logging.getLogger(__name__)


def render_wellness():
    """Renderiza aba 'Saúde & Wellness' com HRV, Stress, Sleep, VO2, Body Composition, Training Status"""
    
    try:
        health_data = load_health_metrics() or {}
        training_data = load_training_status() or {}
    except Exception as e:
        logger.error(f"Erro ao carregar dados de saúde: {e}")
        health_data = {}
        training_data = {}
    
    if not health_data and not training_data:
        return _render_no_data_alert()
    
    # Container principal
    components = [
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("❤️ Saúde & Wellness", className="text-danger mb-2", style={'fontWeight': '700'}),
                    html.P("Métricas avançadas de saúde sincronizadas com Garmin", className="text-muted", style={'fontSize': '1rem'})
                ], className="text-center py-2")
            ])
        ], className="bg-light rounded-3 mb-3"),
    ]
    
    # Training Status Card
    ts_card = _render_training_status_card(training_data)
    if ts_card:
        components.append(dbc.Row([dbc.Col([ts_card])], className="mb-3"))
    
    # VO2 + Body Composition Cards
    vo2_card = _render_vo2_card(health_data)
    body_card = _render_body_comp_card(health_data)
    components.append(dbc.Row([
        dbc.Col([vo2_card], md=6),
        dbc.Col([body_card], md=6)
    ], className="mb-3"))
    
    # Charts (HRV, Stress, Sleep)
    hrv_chart = _create_hrv_chart(health_data.get('hrv', {}))
    stress_chart = _create_stress_chart(health_data.get('stress', {}))
    sleep_chart = _create_sleep_chart(health_data.get('sleep', {}))
    
    if hrv_chart:
        components.append(dbc.Row([
            dbc.Col([dcc.Graph(figure=hrv_chart)], md=12)
        ], className="mb-3"))
    
    if stress_chart:
        components.append(dbc.Row([
            dbc.Col([dcc.Graph(figure=stress_chart)], md=12)
        ], className="mb-3"))
    
    if sleep_chart:
        components.append(dbc.Row([
            dbc.Col([dcc.Graph(figure=sleep_chart)], md=12)
        ], className="mb-3"))
    
    return dbc.Container(components, fluid=False)


def _render_no_data_alert():
    """Renderiza alerta quando não há dados"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("❤️ Saúde & Wellness", className="text-danger mb-2", style={'fontWeight': '700'}),
                    html.P("Métricas avançadas de saúde", className="text-muted", style={'fontSize': '1rem'})
                ], className="text-center py-2")
            ])
        ], className="bg-light rounded-3 mb-3"),
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H5("📊 Nenhum dado de saúde disponível", className="alert-heading"),
                    html.P("Sincronize com o Garmin para ver seus dados de:"),
                    html.Ul([
                        html.Li("HRV (Variabilidade Cardíaca)"),
                        html.Li("Stress (Nível de Estresse)"),
                        html.Li("Sleep (Qualidade do Sono)"),
                        html.Li("VO2 Max (Capacidade Aeróbica)"),
                        html.Li("Composição Corporal"),
                        html.Li("Status de Treinamento"),
                    ]),
                    html.Hr(),
                    html.P("Vá para ⚙️ Configuração → 🔄 Atualizar Dados", className="mb-0")
                ], color="info", className="mt-3")
            ])
        ])
    ], fluid=False)


def _render_training_status_card(training_data):
    """Renderiza card de Training Status"""
    try:
        training_status = training_data.get('training_status', {})
        if not training_status or not isinstance(training_status, dict):
            return dbc.Card([
                dbc.CardBody([
                    html.H5("🎯 Status de Treinamento", className="card-title"),
                    html.P("Sem dados", className="text-muted text-center")
                ])
            ], className="shadow-sm border-0")
        
        status_type = training_status.get('trainingPeakLoadFormatted', 'N/A')
        status_color = _get_training_status_color(status_type)
        
        return dbc.Card([
            dbc.CardBody([
                html.H5("🎯 Status de Treinamento", className="card-title", style={'fontWeight': '700'}),
                html.H2(status_type, className="text-center mb-2", style={'color': status_color, 'fontWeight': 'bold'}),
                html.P("Baseado nas últimas 28 dias", className="text-muted text-center small")
            ])
        ], className="shadow-sm border-0", style={'borderRadius': '12px', 'borderLeft': f'4px solid {status_color}'})
    except Exception as e:
        logger.error(f"Erro ao renderizar training status: {e}")
        return None


def _render_vo2_card(health_data):
    """Renderiza card de VO2 Max"""
    try:
        vo2_max = health_data.get('vo2_max')
        
        if vo2_max is None:
            return dbc.Card([
                dbc.CardBody([
                    html.H5("🫁 VO2 Máximo", className="card-title"),
                    html.P("Sem dados", className="text-muted text-center")
                ])
            ], className="shadow-sm border-0")
        
        # Extrair valor
        if isinstance(vo2_max, dict):
            vo2_value = vo2_max.get('vo2Max') or vo2_max.get('vo2_max')
        else:
            vo2_value = vo2_max
        
        if vo2_value is None:
            return dbc.Card([
                dbc.CardBody([
                    html.H5("🫁 VO2 Máximo", className="card-title"),
                    html.P("Sem dados", className="text-muted text-center")
                ])
            ], className="shadow-sm border-0")
        
        try:
            vo2_float = float(vo2_value)
        except:
            return dbc.Card([
                dbc.CardBody([
                    html.H5("🫁 VO2 Máximo", className="card-title"),
                    html.P("Dados inválidos", className="text-muted text-center")
                ])
            ], className="shadow-sm border-0")
        
        return dbc.Card([
            dbc.CardBody([
                html.H5("🫁 VO2 Máximo", className="card-title", style={'fontWeight': '700'}),
                html.H2(f"{vo2_float:.1f}", className="text-center", style={'color': '#28a745', 'fontWeight': 'bold'}),
                html.P("mL/kg/min", className="text-muted text-center small")
            ])
        ], className="shadow-sm border-0", style={'borderRadius': '12px'})
    except Exception as e:
        logger.error(f"Erro ao renderizar VO2: {e}")
        return None


def _render_body_comp_card(health_data):
    """Renderiza card de Composição Corporal"""
    try:
        body_comp = health_data.get('body_composition', {})
        
        if not body_comp or isinstance(body_comp, list):
            return dbc.Card([
                dbc.CardBody([
                    html.H5("⚖️ Composição Corporal", className="card-title"),
                    html.P("Sem dados", className="text-muted text-center")
                ])
            ], className="shadow-sm border-0")
        
        # Extrair valores com fallback
        total_avg = body_comp.get('totalAverage', body_comp)
        weight = total_avg.get('weight')
        bmi = total_avg.get('bodyMassIndex')
        muscle = total_avg.get('muscleMass') or total_avg.get('muscle')
        body_fat = total_avg.get('bodyFatPercentage') or total_avg.get('bodyFat')
        
        metrics = []
        if weight:
            try:
                metrics.append(html.Div([
                    html.Small("Peso", className="text-muted d-block"),
                    html.H6(f"{float(weight):.1f} kg", className="text-primary")
                ], className="text-center"))
            except:
                pass
        
        if bmi:
            try:
                metrics.append(html.Div([
                    html.Small("IMC", className="text-muted d-block"),
                    html.H6(f"{float(bmi):.1f}", className="text-info")
                ], className="text-center"))
            except:
                pass
        
        if muscle:
            try:
                metrics.append(html.Div([
                    html.Small("Massa Muscular", className="text-muted d-block"),
                    html.H6(f"{float(muscle):.1f}%", className="text-success")
                ], className="text-center"))
            except:
                pass
        
        if body_fat:
            try:
                metrics.append(html.Div([
                    html.Small("% Gordura", className="text-muted d-block"),
                    html.H6(f"{float(body_fat):.1f}%", className="text-warning")
                ], className="text-center"))
            except:
                pass
        
        if not metrics:
            return dbc.Card([
                dbc.CardBody([
                    html.H5("⚖️ Composição Corporal", className="card-title"),
                    html.P("Sem dados válidos", className="text-muted text-center")
                ])
            ], className="shadow-sm border-0")
        
        return dbc.Card([
            dbc.CardBody([
                html.H5("⚖️ Composição Corporal", className="card-title", style={'fontWeight': '700'}),
                dbc.Row([dbc.Col(m) for m in metrics])
            ])
        ], className="shadow-sm border-0", style={'borderRadius': '12px'})
    except Exception as e:
        logger.error(f"Erro ao renderizar body composition: {e}")
        return None


def _get_training_status_color(status_type):
    """Retorna cor baseada no status de treinamento"""
    if not status_type:
        return '#666666'
    
    status = str(status_type).lower()
    
    if 'overreach' in status or 'overload' in status:
        return '#dc3545'  # Red
    elif 'high' in status:
        return '#fd7e14'  # Orange
    elif 'balanced' in status or 'balance' in status:
        return '#28a745'  # Green
    elif 'low' in status:
        return '#0066cc'  # Blue
    elif 'detraining' in status:
        return '#9b59b6'  # Purple
    
    return '#666666'  # Default gray


def _create_hrv_chart(hrv_data):
    """Cria gráfico de HRV"""
    try:
        if not hrv_data or isinstance(hrv_data, list):
            return None
        
        dates = []
        values = []
        
        # Iterar sobre dados por data
        if isinstance(hrv_data, dict):
            for date_str, data in hrv_data.items():
                if not isinstance(data, dict):
                    continue
                
                # Tentar extrair valor HRV
                hrv_summary = data.get('hrvSummary', {})
                if isinstance(hrv_summary, dict):
                    value = hrv_summary.get('lastNightAverage') or hrv_summary.get('value')
                    if value:
                        try:
                            dates.append(date_str)
                            values.append(float(value))
                        except:
                            pass
        
        if not dates or not values:
            return None
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=values,
            mode='lines+markers',
            name='HRV',
            line=dict(color='#0066cc', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(0, 102, 204, 0.1)'
        ))
        
        fig.update_layout(
            title='HRV (Variabilidade da Frequência Cardíaca)',
            xaxis_title='Data',
            yaxis_title='HRV (ms)',
            hovermode='x unified',
            template='plotly_white',
            height=350
        )
        return fig
    except Exception as e:
        logger.error(f"Erro ao criar gráfico HRV: {e}")
        return None


def _create_stress_chart(stress_data):
    """Cria gráfico de Stress"""
    try:
        if not stress_data or isinstance(stress_data, list):
            return None
        
        dates = []
        avg_values = []
        max_values = []
        
        # Iterar sobre dados por data
        if isinstance(stress_data, dict):
            for date_str, data in stress_data.items():
                if not isinstance(data, dict):
                    continue
                
                avg = data.get('avgStressLevel')
                max_val = data.get('maxStressLevel')
                
                if avg is not None:
                    try:
                        dates.append(date_str)
                        avg_values.append(float(avg))
                        max_values.append(float(max_val) if max_val else None)
                    except:
                        pass
        
        if not dates or not avg_values:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates, y=avg_values,
            mode='lines+markers',
            name='Stress Médio',
            line=dict(color='#ff6b6b', width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(255, 107, 107, 0.1)'
        ))
        
        if any(v is not None for v in max_values):
            fig.add_trace(go.Scatter(
                x=dates, y=max_values,
                mode='lines',
                name='Stress Máximo',
                line=dict(color='#cc0000', width=1, dash='dash'),
                opacity=0.7
            ))
        
        fig.update_layout(
            title='Nível de Stress',
            xaxis_title='Data',
            yaxis_title='Stress (0-100)',
            hovermode='x unified',
            template='plotly_white',
            height=350,
            yaxis=dict(range=[0, 100])
        )
        return fig
    except Exception as e:
        logger.error(f"Erro ao criar gráfico Stress: {e}")
        return None


def _create_sleep_chart(sleep_data):
    """Cria gráfico de Sleep"""
    try:
        if not sleep_data or isinstance(sleep_data, list):
            return None
        
        dates = []
        total_sleep = []
        deep_sleep = []
        rem_sleep = []
        
        # Iterar sobre dados por data
        if isinstance(sleep_data, dict):
            for date_str, data in sleep_data.items():
                if not isinstance(data, dict):
                    continue
                
                daily = data.get('dailySleepDTO', {})
                if isinstance(daily, dict):
                    total = daily.get('sleepTimeSeconds', 0)
                    deep = daily.get('deepSleepSeconds', 0)
                    rem = daily.get('remSleepSeconds', 0)
                    
                    if total:
                        try:
                            dates.append(date_str)
                            total_sleep.append(total / 3600)  # Converter para horas
                            deep_sleep.append(deep / 3600)
                            rem_sleep.append(rem / 3600)
                        except:
                            pass
        
        if not dates:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=dates, y=deep_sleep,
            name='Sleep Profundo',
            marker=dict(color='#4c63ff')
        ))
        
        fig.add_trace(go.Bar(
            x=dates, y=rem_sleep,
            name='REM',
            marker=dict(color='#00d4ff')
        ))
        
        fig.update_layout(
            barmode='stack',
            title='Qualidade do Sono',
            xaxis_title='Data',
            yaxis_title='Duração (horas)',
            hovermode='x unified',
            template='plotly_white',
            height=350
        )
        return fig
    except Exception as e:
        logger.error(f"Erro ao criar gráfico Sleep: {e}")
        return None
