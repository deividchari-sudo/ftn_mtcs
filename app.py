import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import os
import numpy as np
import math
from datetime import datetime, timedelta
from pathlib import Path
import calendar

from utils import *
from ai_chat import FitnessAI
from details_page import render_details
from calculations import calculate_trimp, compute_tss_variants, calculate_fitness_metrics, _activity_category, _parse_mmss_to_seconds
from storage import (
    DATA_DIR, CONFIG_FILE, CREDENTIALS_FILE, METRICS_FILE, WORKOUTS_FILE,
    load_config, save_config,
    load_credentials, save_credentials,
    load_garmin_tokens, validate_garmin_tokens_locally, save_garmin_tokens,
    load_metrics, save_metrics,
    load_workouts, save_workouts
)

# Função para enriquecer workouts com TSS calculado dinamicamente
def enrich_workouts_with_tss(workouts, config=None):
    """Calcula TSS dinamicamente para cada workout (não salva)"""
    if config is None:
        config = load_config()
    
    enriched = []
    for w in workouts:
        w_copy = dict(w)
        
        # Remover TSS antigo se existir
        if 'tss' in w_copy:
            old_tss = w_copy['tss']
            del w_copy['tss']
        else:
            old_tss = None
        
        # Calcular TSS novo
        tss_result = compute_tss_variants(w_copy, config)
        new_tss = tss_result.get('tss', 0.0)
        w_copy['tss'] = new_tss
        w_copy['tss_type'] = tss_result.get('tss_type', 'unknown')
        w_copy['category'] = tss_result.get('category', _activity_category(w))
        
        enriched.append(w_copy)

    return enriched

# Função auxiliar para converter horas decimais em hh:mm:ss
def format_hours_to_hms(hours):
    """Converte horas decimais para formato hh:mm:ss"""
    if hours == 0:
        return "00:00:00"
    h = int(hours)
    m = int((hours - h) * 60)
    s = int(((hours - h) * 60 - m) * 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Fitness Metrics Dashboard"
# Expor WSGI server para provedores como Render/Gunicorn
server = app.server

# Script JavaScript para funcionalidades extras
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <script>
        // Persistência do modo escuro
        window.addEventListener('DOMContentLoaded', function() {
            const savedDarkMode = localStorage.getItem('darkMode');
            if (savedDarkMode === 'true') {
                // Aguarda o componente carregar
                setTimeout(() => {
                    const toggleBtn = document.getElementById('dark-mode-toggle');
                    if (toggleBtn) toggleBtn.click();
                }, 100);
            }
            
            // Atalhos de teclado
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + D = Toggle modo escuro
                if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
                    e.preventDefault();
                    const toggleBtn = document.getElementById('dark-mode-toggle');
                    if (toggleBtn) toggleBtn.click();
                }
                
                // Ctrl/Cmd + K = Mostrar atalhos
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    alert('Atalhos de Teclado:\n\n' +
                          'Ctrl+D: Alternar modo escuro\n' +
                          'Ctrl+R: Atualizar dados\n' +
                          'Ctrl+1/2/3/4: Navegar abas');
                }
                
                // Ctrl/Cmd + 1-4 = Navegar entre abas
                if ((e.ctrlKey || e.metaKey) && ['1','2','3','4'].includes(e.key)) {
                    e.preventDefault();
                    const tabs = ['dashboard', 'calendar', 'goals', 'config'];
                    const tabIndex = parseInt(e.key) - 1;
                    const tabButtons = document.querySelectorAll('[role="tab"]');
                    if (tabButtons[tabIndex]) tabButtons[tabIndex].click();
                }
            });
        });
        
        // Salvar preferência quando modo escuro mudar
        window.saveDarkModePreference = function(isDark) {
            localStorage.setItem('darkMode', isDark);
        };
        </script>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout principal com header melhorado
app.layout = html.Div(id='app-container', children=[
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
        dbc.Tab(label="🤖 AI Chat", tab_id="ai_chat"),
        dbc.Tab(label="📋 Mais Detalhes", tab_id="details"),
        dbc.Tab(label="⚙️ Configuração", tab_id="config")
    ], id="tabs", active_tab="dashboard"),
    
    # Conteúdo das abas
    html.Div(id="tab-content", className="mt-4")
    ], fluid=False, style={'maxWidth': '1400px'})
])

# Callback para trocar conteúdo das abas
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
    elif active_tab == "ai_chat":
        return render_ai_chat()
    elif active_tab == "details":
        return render_details()
    elif active_tab == "config":
        return render_config()
    return html.P("Selecione uma aba.")

# Callbacks para exportação de dados
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
        workouts = enrich_workouts_with_tss(load_workouts())
        workouts = enrich_workouts_with_tss(workouts)  # Calcular TSS dinamicamente
        _, csv_data = export_to_csv([], workouts)
        if csv_data:
            return dict(content=csv_data, filename=f"workouts_{datetime.now().strftime('%Y%m%d')}.csv")
    return None

# Função auxiliar para calcular resumo semanal
def calculate_weekly_summary():
    """Calcula resumo da semana atual (segunda a domingo)"""
    workouts = enrich_workouts_with_tss(load_workouts())
    config = load_config()
    
    # Definir semana atual
    now = datetime.now()
    days_since_monday = now.isoweekday() - 1  # 0=segunda, 6=domingo
    week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    
    total_hours = 0.0
    total_tss = 0.0
    total_activities = 0
    total_distance = 0.0
    
    for workout in workouts:
        try:
            start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
            if not start_time:
                continue
                
            activity_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            
            if week_start <= activity_date <= week_end:
                duration_h = float(workout.get('duration', 0) or 0) / 3600
                tss = float(workout.get('tss', 0) or 0)
                distance = float(workout.get('distance', 0) or 0) / 1000
                name = workout.get('activityName', 'N/A')[:40]
                
                total_hours += duration_h
                total_tss += tss
                total_activities += 1
                total_distance += distance
        except Exception as e:
            continue
    
    # Formatar período
    week_str = f"{week_start.strftime('%d %b')} - {week_end.strftime('%d %b')}"
    
    # Formatar horas como hh:mm:ss
    hours_formatted = format_hours_to_hms(total_hours)
    
    return {
        'period': week_str,
        'hours': total_hours,
        'hours_formatted': hours_formatted,
        'tss': total_tss,
        'activities': total_activities,
        'distance': total_distance
    }

# Função para calcular alertas inteligentes
def calculate_smart_alerts(metrics):
    """Gera alertas baseados nas métricas de treinamento"""
    alerts = []
    
    if len(metrics) < 3:
        return alerts
    
    last_metric = metrics[-1]
    last_3_metrics = metrics[-3:]
    last_14_metrics = metrics[-14:] if len(metrics) >= 14 else metrics
    
    # Alerta 1: Risco de Overtraining (ATL > CTL por 3+ dias)
    overtraining_days = sum(1 for m in last_3_metrics if m['atl'] > m['ctl'])
    if overtraining_days >= 3:
        alerts.append({
            'icon': '🚨',
            'title': 'Risco de Overtraining',
            'message': f'Fadiga maior que forma por {overtraining_days} dias consecutivos',
            'action': 'Considere reduzir intensidade ou volume dos treinos',
            'color': 'danger',
            'priority': 1
        })
    
    # Alerta 2: Necessita Descanso (TSB muito negativo)
    if last_metric['tsb'] < -15:
        alerts.append({
            'icon': '😴',
            'title': 'Necessita Descanso',
            'message': f'TSB está em {last_metric["tsb"]:.1f}, muito abaixo do ideal',
            'action': 'Programe 2-3 dias de descanso ou treinos leves',
            'color': 'warning',
            'priority': 2
        })
    
    # Alerta 3: Pronto para Intensidade
    if last_metric['tsb'] > 15 and last_metric['ctl'] >= 40:
        alerts.append({
            'icon': '⚡',
            'title': 'Pronto para Intensidade',
            'message': f'TSB em {last_metric["tsb"]:.1f} - você está bem descansado',
            'action': 'Momento ideal para treinos de alta intensidade',
            'color': 'success',
            'priority': 3
        })
    
    # Alerta 4: Forma em Declínio
    if len(last_14_metrics) >= 14:
        ctl_14_days_ago = last_14_metrics[0]['ctl']
        ctl_decline = ((last_metric['ctl'] - ctl_14_days_ago) / ctl_14_days_ago * 100) if ctl_14_days_ago > 0 else 0
        if ctl_decline < -10:
            alerts.append({
                'icon': '📉',
                'title': 'Forma em Declínio',
                'message': f'CTL caiu {abs(ctl_decline):.1f}% nas últimas 2 semanas',
                'action': 'Aumente gradualmente volume ou intensidade dos treinos',
                'color': 'info',
                'priority': 4
            })
    
    # Alerta 5: Manutenção de Forma
    if -5 <= last_metric['tsb'] <= 5 and last_metric['ctl'] >= 45:
        alerts.append({
            'icon': '✅',
            'title': 'Zona Ideal de Treinamento',
            'message': f'CTL {last_metric["ctl"]:.1f} e TSB {last_metric["tsb"]:.1f} estão perfeitos',
            'action': 'Continue com o plano atual de treinamento',
            'color': 'success',
            'priority': 5
        })
    
    # Ordenar por prioridade
    alerts.sort(key=lambda x: x['priority'])
    return alerts[:3]  # Retornar apenas os 3 mais importantes

# Função para calcular recordes pessoais
def calculate_personal_records(metrics, workouts):
    """Calcula recordes pessoais do atleta"""
    records = {}
    
    # Maior CTL alcançado
    if metrics:
        max_ctl_metric = max(metrics, key=lambda m: m['ctl'])
        records['max_ctl'] = {
            'value': max_ctl_metric['ctl'],
            'date': max_ctl_metric['date'],
            'icon': '💪',
            'label': 'Maior CTL',
            'unit': 'pts'
        }
    
    # Maior TSS em um dia
    if workouts:
        max_tss_workout = max(workouts, key=lambda w: float(w.get('tss', 0) or 0))
        records['max_tss'] = {
            'value': float(max_tss_workout.get('tss', 0) or 0),
            'date': max_tss_workout.get('startTimeLocal', 'N/A')[:10],
            'icon': '🔥',
            'label': 'Maior TSS',
            'unit': 'pts',
            'activity': max_tss_workout.get('activityName', 'N/A')[:30]
        }
        
        # Maior distância
        max_distance_workout = max(workouts, key=lambda w: float(w.get('distance', 0) or 0))
        records['max_distance'] = {
            'value': float(max_distance_workout.get('distance', 0) or 0) / 1000,
            'date': max_distance_workout.get('startTimeLocal', 'N/A')[:10],
            'icon': '🏃',
            'label': 'Maior Distância',
            'unit': 'km',
            'activity': max_distance_workout.get('activityName', 'N/A')[:30]
        }
        
        # Maior duração
        max_duration_workout = max(workouts, key=lambda w: float(w.get('duration', 0) or 0))
        records['max_duration'] = {
            'value': float(max_duration_workout.get('duration', 0) or 0) / 3600,
            'date': max_duration_workout.get('startTimeLocal', 'N/A')[:10],
            'icon': '⏱️',
            'label': 'Maior Duração',
            'unit': 'h',
            'activity': max_duration_workout.get('activityName', 'N/A')[:30]
        }
    
    # Calcular maior semana (TSS)
    try:
        weekly_tss = {}
        for workout in workouts:
            start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
            if not start_time:
                continue
            activity_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            week_key = activity_date.strftime('%Y-W%U')
            weekly_tss[week_key] = weekly_tss.get(week_key, 0) + float(workout.get('tss', 0) or 0)
        
        if weekly_tss:
            max_week = max(weekly_tss.items(), key=lambda x: x[1])
            records['max_week_tss'] = {
                'value': max_week[1],
                'date': max_week[0],
                'icon': '📊',
                'label': 'Maior Semana',
                'unit': 'TSS'
            }
    except:
        pass
    
    return records

# Função para calcular comparações de períodos
def calculate_period_comparison(metrics):
    """Compara semana atual vs anterior"""
    if len(metrics) < 14:
        return None
    
    # Últimos 7 dias (semana atual)
    current_week = metrics[-7:]
    # 7 dias anteriores (semana passada)
    previous_week = metrics[-14:-7]
    
    # Calcular médias
    current_avg = {
        'ctl': sum(m['ctl'] for m in current_week) / len(current_week),
        'atl': sum(m['atl'] for m in current_week) / len(current_week),
        'tsb': sum(m['tsb'] for m in current_week) / len(current_week)
    }
    
    previous_avg = {
        'ctl': sum(m['ctl'] for m in previous_week) / len(previous_week),
        'atl': sum(m['atl'] for m in previous_week) / len(previous_week),
        'tsb': sum(m['tsb'] for m in previous_week) / len(previous_week)
    }
    
    # Calcular variações
    comparison = {
        'ctl': {
            'current': current_avg['ctl'],
            'previous': previous_avg['ctl'],
            'change': current_avg['ctl'] - previous_avg['ctl'],
            'change_pct': ((current_avg['ctl'] - previous_avg['ctl']) / previous_avg['ctl'] * 100) if previous_avg['ctl'] > 0 else 0
        },
        'atl': {
            'current': current_avg['atl'],
            'previous': previous_avg['atl'],
            'change': current_avg['atl'] - previous_avg['atl'],
            'change_pct': ((current_avg['atl'] - previous_avg['atl']) / previous_avg['atl'] * 100) if previous_avg['atl'] > 0 else 0
        },
        'tsb': {
            'current': current_avg['tsb'],
            'previous': previous_avg['tsb'],
            'change': current_avg['tsb'] - previous_avg['tsb'],
            'change_pct': ((current_avg['tsb'] - previous_avg['tsb']) / abs(previous_avg['tsb']) * 100) if previous_avg['tsb'] != 0 else 0
        }
    }
    
    return comparison

# Função para calcular conquistas/achievements
def calculate_achievements(metrics, workouts):
    """Calcula conquistas gamificadas do usuário"""
    achievements = []
    
    # Conquista 1: Sequência de dias consecutivos
    if workouts:
        dates_with_workouts = set()
        for workout in workouts:
            try:
                start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
                if start_time:
                    activity_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").date()
                    dates_with_workouts.add(activity_date)
            except:
                pass
        
        # Calcular maior sequência
        if dates_with_workouts:
            sorted_dates = sorted(dates_with_workouts, reverse=True)
            current_streak = 1
            max_streak = 1
            
            for i in range(len(sorted_dates) - 1):
                if (sorted_dates[i] - sorted_dates[i+1]).days == 1:
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                else:
                    current_streak = 1
            
            if max_streak >= 7:
                achievements.append({
                    'icon': '🔥',
                    'title': 'Sequência de Fogo',
                    'description': f'{max_streak} dias consecutivos de treino',
                    'unlocked': True,
                    'color': 'danger',
                    'progress': 100
                })
            else:
                achievements.append({
                    'icon': '🔥',
                    'title': 'Sequência de Fogo',
                    'description': f'Treine 7 dias seguidos ({max_streak}/7)',
                    'unlocked': False,
                    'color': 'secondary',
                    'progress': int(max_streak / 7 * 100)
                })
    
    # Conquista 2: Centurião (100+ TSS em um dia)
    max_daily_tss = 0
    if workouts:
        daily_tss = {}
        for workout in workouts:
            try:
                start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
                if start_time:
                    date_key = start_time[:10]
                    tss = float(workout.get('tss', 0) or 0)
                    daily_tss[date_key] = daily_tss.get(date_key, 0) + tss
            except:
                pass
        
        if daily_tss:
            max_daily_tss = max(daily_tss.values())
    
    if max_daily_tss >= 100:
        achievements.append({
            'icon': '💯',
            'title': 'Centurião',
            'description': f'Maior dia: {max_daily_tss:.0f} TSS',
            'unlocked': True,
            'color': 'success',
            'progress': 100
        })
    else:
        achievements.append({
            'icon': '💯',
            'title': 'Centurião',
            'description': f'Alcance 100 TSS em um dia ({max_daily_tss:.0f}/100)',
            'unlocked': False,
            'color': 'secondary',
            'progress': int(max_daily_tss)
        })
    
    # Conquista 3: Maratonista (42km+ em corrida)
    max_running_distance = 0
    if workouts:
        for workout in workouts:
            try:
                activity_type = workout.get('activityType', {}).get('typeKey', '').lower()
                if 'running' in activity_type or 'corrida' in activity_type:
                    distance = float(workout.get('distance', 0) or 0) / 1000
                    max_running_distance = max(max_running_distance, distance)
            except:
                pass
    
    if max_running_distance >= 42:
        achievements.append({
            'icon': '🏃',
            'title': 'Maratonista',
            'description': f'Corrida de {max_running_distance:.1f}km',
            'unlocked': True,
            'color': 'primary',
            'progress': 100
        })
    else:
        achievements.append({
            'icon': '🏃',
            'title': 'Maratonista',
            'description': f'Corra 42km em uma atividade ({max_running_distance:.1f}/42km)',
            'unlocked': False,
            'color': 'secondary',
            'progress': int(max_running_distance / 42 * 100)
        })
    
    # Conquista 4: Sprint Master (5+ treinos na semana)
    max_weekly_activities = 0
    if workouts:
        weekly_count = {}
        for workout in workouts:
            try:
                start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
                if start_time:
                    activity_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    week_key = activity_date.strftime('%Y-W%U')
                    weekly_count[week_key] = weekly_count.get(week_key, 0) + 1
            except:
                pass
        
        if weekly_count:
            max_weekly_activities = max(weekly_count.values())
    
    if max_weekly_activities >= 5:
        achievements.append({
            'icon': '⚡',
            'title': 'Sprint Master',
            'description': f'Melhor semana: {max_weekly_activities} treinos',
            'unlocked': True,
            'color': 'warning',
            'progress': 100
        })
    else:
        achievements.append({
            'icon': '⚡',
            'title': 'Sprint Master',
            'description': f'Complete 5 treinos em uma semana ({max_weekly_activities}/5)',
            'unlocked': False,
            'color': 'secondary',
            'progress': int(max_weekly_activities / 5 * 100)
        })
    
    # Conquista 5: Elite (CTL >= 60)
    max_ctl = 0
    if metrics:
        max_ctl = max(m['ctl'] for m in metrics)
    
    if max_ctl >= 60:
        achievements.append({
            'icon': '👑',
            'title': 'Elite',
            'description': f'CTL máximo: {max_ctl:.1f}',
            'unlocked': True,
            'color': 'info',
            'progress': 100
        })
    else:
        achievements.append({
            'icon': '👑',
            'title': 'Elite',
            'description': f'Alcance CTL de 60 ({max_ctl:.1f}/60)',
            'unlocked': False,
            'color': 'secondary',
            'progress': int(max_ctl / 60 * 100)
        })
    
    return achievements

# Função para gerar previsões e recomendações
def generate_predictions(metrics, config):
    """Gera previsões baseadas nas tendências atuais"""
    predictions = []
    
    if len(metrics) < 14:
        return predictions
    
    last_metric = metrics[-1]
    last_14_metrics = metrics[-14:]
    
    # Calcular tendência de CTL (últimos 14 dias)
    ctl_values = [m['ctl'] for m in last_14_metrics]
    if len(ctl_values) >= 2:
        # Regressão linear simples
        x = list(range(len(ctl_values)))
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(ctl_values)
        sum_xy = sum(xi * yi for xi, yi in zip(x, ctl_values))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x) if (n * sum_x2 - sum_x * sum_x) != 0 else 0
        
        # Projetar CTL para 7, 14 e 30 dias
        current_ctl = last_metric['ctl']
        ctl_7_days = current_ctl + (slope * 7)
        ctl_14_days = current_ctl + (slope * 14)
        ctl_30_days = current_ctl + (slope * 30)
        
        ctl_target = config.get('ctl_target', 50.0)
        
        # Previsão 1: Quando atingirá meta de CTL
        if slope > 0 and current_ctl < ctl_target:
            days_to_target = int((ctl_target - current_ctl) / slope)
            if days_to_target > 0 and days_to_target < 90:
                target_date = (datetime.now() + timedelta(days=days_to_target)).strftime('%d/%m/%Y')
                predictions.append({
                    'icon': '🎯',
                    'title': 'Meta de CTL',
                    'prediction': f'Você atingirá CTL {ctl_target:.0f} em aproximadamente {days_to_target} dias',
                    'date': target_date,
                    'confidence': 'média' if slope > 0.5 else 'baixa',
                    'type': 'goal'
                })
        
        # Previsão 2: Projeções de curto/médio prazo
        predictions.append({
            'icon': '📈',
            'title': 'Projeção de Forma',
            'prediction': f'Em 7 dias: CTL {ctl_7_days:.1f} | Em 14 dias: CTL {ctl_14_days:.1f} | Em 30 dias: CTL {ctl_30_days:.1f}',
            'trend': 'alta' if slope > 0 else 'baixa',
            'confidence': 'média',
            'type': 'projection'
        })
    
    # Recomendação 3: TSS sugerido para próxima semana
    recent_tss = [m.get('daily_tss', 0) for m in last_14_metrics[-7:]]
    avg_weekly_tss = sum(recent_tss)
    
    if last_metric['tsb'] < -10:
        # TSB muito negativo - recomendar redução
        recommended_tss = avg_weekly_tss * 0.7
        predictions.append({
            'icon': '😴',
            'title': 'Recomendação de Carga',
            'prediction': f'Reduza o TSS semanal para ~{recommended_tss:.0f} (30% a menos) para recuperação',
            'reason': f'Seu TSB está em {last_metric["tsb"]:.1f}, indicando fadiga acumulada',
            'confidence': 'alta',
            'type': 'recommendation'
        })
    elif last_metric['tsb'] > 15:
        # TSB muito positivo - pode aumentar
        recommended_tss = avg_weekly_tss * 1.2
        predictions.append({
            'icon': '⚡',
            'title': 'Oportunidade de Carga',
            'prediction': f'Você pode aumentar o TSS semanal para ~{recommended_tss:.0f} (20% a mais)',
            'reason': f'Seu TSB está em {last_metric["tsb"]:.1f}, você está bem descansado',
            'confidence': 'alta',
            'type': 'recommendation'
        })
    else:
        # TSB ideal - manter
        predictions.append({
            'icon': '✅',
            'title': 'Carga Ideal',
            'prediction': f'Mantenha o TSS semanal em torno de {avg_weekly_tss:.0f}',
            'reason': f'Seu TSB está em {last_metric["tsb"]:.1f}, na zona ideal',
            'confidence': 'alta',
            'type': 'recommendation'
        })
    
    # Previsão 4: Melhor janela para prova/evento
    atl_trend = [m['atl'] for m in last_14_metrics]
    if len(atl_trend) >= 2:
        atl_slope = (atl_trend[-1] - atl_trend[0]) / len(atl_trend)
        
        if atl_slope < 0:  # Fadiga declinando
            days_to_peak = int(abs(last_metric['atl'] / atl_slope)) if atl_slope != 0 else 7
            peak_date = (datetime.now() + timedelta(days=min(days_to_peak, 21))).strftime('%d/%m/%Y')
            predictions.append({
                'icon': '🏁',
                'title': 'Janela de Performance',
                'prediction': f'Melhor momento para evento: ~{peak_date}',
                'reason': 'Fadiga em declínio, forma mantida',
                'confidence': 'média',
                'type': 'timing'
            })
    
    return predictions

# Função para exportar relatório CSV
def export_to_csv(metrics, workouts):
    """Exporta métricas e workouts para CSV"""
    try:
        import io
        
        # Criar CSV de métricas
        metrics_csv = io.StringIO()
        metrics_csv.write("Data,CTL,ATL,TSB\n")
        for m in metrics:
            metrics_csv.write(f"{m['date']},{m['ctl']:.2f},{m['atl']:.2f},{m['tsb']:.2f}\n")
        
        # Criar CSV de workouts
        workouts_csv = io.StringIO()
        workouts_csv.write("Data,Nome,Tipo,Distância(km),Duração(h),TSS\n")
        for w in workouts:
            start_time = w.get('startTimeLocal', w.get('startTime', 'N/A'))
            name = w.get('activityName', 'N/A').replace(',', ';')
            activity_type = w.get('activityType', {}).get('typeKey', 'N/A')
            distance = float(w.get('distance', 0) or 0) / 1000
            duration = float(w.get('duration', 0) or 0) / 3600
            tss = float(w.get('tss', 0) or 0)
            workouts_csv.write(f"{start_time},{name},{activity_type},{distance:.2f},{duration:.2f},{tss:.1f}\n")
        
        return metrics_csv.getvalue(), workouts_csv.getvalue()
    except Exception as e:
        return None, None

# Função para criar tendência mensal (últimos 6 meses)
def create_monthly_trend_chart(metrics, workouts):
    """Cria gráfico de evolução mensal com barras por modalidade"""
    try:
        from datetime import datetime as dt_parse
        import calendar
        
        # Organizar dados por mês
        monthly_data = {}
        
        # Agrupar workouts por mês e modalidade
        for workout in workouts:
            try:
                start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
                if not start_time:
                    continue
                
                activity_date = dt_parse.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                month_key = activity_date.strftime('%Y-%m')
                month_label = activity_date.strftime('%b/%y')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {
                        'label': month_label,
                        'running': 0,
                        'cycling': 0,
                        'swimming': 0,
                        'strength': 0,
                        'other': 0,
                        'total_tss': 0,
                        'avg_ctl': 0,
                        'count_ctl': 0
                    }
                
                # Categorizar atividade
                activity_type = workout.get('activityType', {}).get('typeKey', '').lower()
                tss = float(workout.get('tss', 0) or 0)
                
                if 'running' in activity_type:
                    monthly_data[month_key]['running'] += tss
                elif 'cycling' in activity_type or 'biking' in activity_type:
                    monthly_data[month_key]['cycling'] += tss
                elif 'swimming' in activity_type:
                    monthly_data[month_key]['swimming'] += tss
                elif 'strength' in activity_type or 'training' in activity_type:
                    monthly_data[month_key]['strength'] += tss
                else:
                    monthly_data[month_key]['other'] += tss
                
                monthly_data[month_key]['total_tss'] += tss
            except:
                pass
        
        # Adicionar CTL médio por mês
        for metric in metrics:
            try:
                month_key = metric['date'][:7]
                if month_key in monthly_data:
                    monthly_data[month_key]['avg_ctl'] += metric['ctl']
                    monthly_data[month_key]['count_ctl'] += 1
            except:
                pass
        
        # Calcular média de CTL
        for month_key in monthly_data:
            if monthly_data[month_key]['count_ctl'] > 0:
                monthly_data[month_key]['avg_ctl'] /= monthly_data[month_key]['count_ctl']
        
        # Pegar últimos 6 meses
        sorted_months = sorted(monthly_data.keys())[-6:]
        
        months_labels = [monthly_data[m]['label'] for m in sorted_months]
        running_data = [monthly_data[m]['running'] for m in sorted_months]
        cycling_data = [monthly_data[m]['cycling'] for m in sorted_months]
        swimming_data = [monthly_data[m]['swimming'] for m in sorted_months]
        strength_data = [monthly_data[m]['strength'] for m in sorted_months]
        other_data = [monthly_data[m]['other'] for m in sorted_months]
        ctl_data = [monthly_data[m]['avg_ctl'] for m in sorted_months]
        
        # Criar figura com eixo secundário
        from plotly.subplots import make_subplots
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Barras empilhadas de TSS por modalidade
        fig.add_trace(
            go.Bar(name='🏃 Corrida', x=months_labels, y=running_data, marker_color='#fd7e14'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(name='🚴 Ciclismo', x=months_labels, y=cycling_data, marker_color='#28a745'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(name='🏊 Natação', x=months_labels, y=swimming_data, marker_color='#007bff'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(name='💪 Força', x=months_labels, y=strength_data, marker_color='#6f42c1'),
            secondary_y=False
        )
        fig.add_trace(
            go.Bar(name='⚽ Outros', x=months_labels, y=other_data, marker_color='#6c757d'),
            secondary_y=False
        )
        
        # Linha de CTL médio
        fig.add_trace(
            go.Scatter(
                name='💪 CTL Médio',
                x=months_labels,
                y=ctl_data,
                mode='lines+markers',
                line=dict(color='#e74c3c', width=3),
                marker=dict(size=10, symbol='diamond'),
                yaxis='y2'
            ),
            secondary_y=True
        )
        
        fig.update_layout(
            title='Evolução Mensal - TSS por Modalidade e CTL',
            barmode='stack',
            height=450,
            hovermode='x unified',
            font={'family': 'Inter, -apple-system, sans-serif', 'size': 12},
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5
            )
        )
        
        fig.update_xaxes(title_text='Mês')
        fig.update_yaxes(title_text='TSS Total', secondary_y=False)
        fig.update_yaxes(title_text='CTL Médio', secondary_y=True)
        
        return fig
    except Exception as e:
        # Retornar gráfico vazio em caso de erro
        fig = go.Figure()
        fig.update_layout(title="Sem dados suficientes para tendência mensal", height=450)
        return fig

# Funções para renderizar cada aba
def render_dashboard():
    # Recalcular métricas dinamicamente com TSS correto
    config = load_config()
    workouts = enrich_workouts_with_tss(load_workouts())
    
    # Calcular métricas dos últimos 42 dias
    from datetime import datetime, timedelta, date as dt_date
    end_date = dt_date.today()
    start_date = end_date - timedelta(days=42)
    
    metrics = calculate_fitness_metrics(workouts, config, start_date, end_date)
    
    # Salvar para outras partes do app usarem
    save_metrics(metrics)
    
    if not metrics:
        # Dados mock para demonstração
        metrics = [
            {"date": "2025-12-01", "ctl": 45.0, "atl": 35.0, "tsb": 10.0},
            {"date": "2025-12-02", "ctl": 46.0, "atl": 36.0, "tsb": 10.0},
            {"date": "2025-12-03", "ctl": 47.0, "atl": 37.0, "tsb": 10.0},
            {"date": "2025-12-04", "ctl": 48.0, "atl": 38.0, "tsb": 10.0},
            {"date": "2025-12-05", "ctl": 49.0, "atl": 39.0, "tsb": 10.0},
            {"date": "2025-12-06", "ctl": 50.0, "atl": 40.0, "tsb": 10.0},
            {"date": "2025-12-07", "ctl": 51.0, "atl": 41.0, "tsb": 10.0},
        ]
    
    last_metric = metrics[-1]
    prev_metric = metrics[-8] if len(metrics) >= 8 else metrics[0]
    
    # Calcular variações
    ctl_change = ((last_metric['ctl'] - prev_metric['ctl']) / prev_metric['ctl'] * 100) if prev_metric['ctl'] > 0 else 0
    atl_change = ((last_metric['atl'] - prev_metric['atl']) / prev_metric['atl'] * 100) if prev_metric['atl'] > 0 else 0
    tsb_change = ((last_metric['tsb'] - prev_metric['tsb']) / abs(prev_metric['tsb']) * 100) if prev_metric['tsb'] != 0 else 0
    
    # Símbolos de tendência
    ctl_arrow = "📈" if ctl_change > 0 else "📉" if ctl_change < 0 else "➡️"
    atl_arrow = "📈" if atl_change > 0 else "📉" if atl_change < 0 else "➡️"
    tsb_arrow = "📈" if tsb_change > 0 else "📉" if tsb_change < 0 else "➡️"
    
    # Status baseado em valores (para amador bem treinado)
    def get_ctl_status(ctl):
        if ctl >= 50: return {"label": "Excelente", "color": "#28a745", "badge": "success"}
        elif ctl >= 40: return {"label": "Bom", "color": "#17a2b8", "badge": "info"}
        elif ctl >= 30: return {"label": "Moderado", "color": "#ffc107", "badge": "warning"}
        else: return {"label": "Iniciante", "color": "#6c757d", "badge": "secondary"}
    
    def get_atl_status(atl):
        if atl > 80: return {"label": "Atenção!", "color": "#dc3545", "badge": "danger"}
        elif atl > 60: return {"label": "Alta", "color": "#fd7e14", "badge": "warning"}
        elif atl > 40: return {"label": "Moderada", "color": "#ffc107", "badge": "warning"}
        else: return {"label": "Baixa", "color": "#28a745", "badge": "success"}
    
    def get_tsb_status(tsb):
        if tsb > 25: return {"label": "Descansado", "color": "#28a745", "badge": "success"}
        elif tsb > 5: return {"label": "Fresco", "color": "#17a2b8", "badge": "info"}
        elif tsb > -10: return {"label": "Ideal", "color": "#ffc107", "badge": "warning"}
        else: return {"label": "Cansado", "color": "#dc3545", "badge": "danger"}
    
    ctl_status = get_ctl_status(last_metric['ctl'])
    atl_status = get_atl_status(last_metric['atl'])
    tsb_status = get_tsb_status(last_metric['tsb'])
    
    # Pegar últimos 7 dias para mini sparkline
    last_7_metrics = metrics[-7:] if len(metrics) >= 7 else metrics
    ctl_sparkline = [m['ctl'] for m in last_7_metrics]
    atl_sparkline = [m['atl'] for m in last_7_metrics]
    tsb_sparkline = [m['tsb'] for m in last_7_metrics]
    
    # Calcular resumo semanal uma vez
    weekly_summary = calculate_weekly_summary()
    
    # Calcular progresso das metas
    workouts = enrich_workouts_with_tss(load_workouts())
    config = load_config()
    goals_progress = calculate_goals_progress(workouts, config)
    
    return dbc.Container([
        # ============ STATUS ATUAL: ONDE VOCÊ ESTÁ ============
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("🎯 Status Atual", className="text-primary mb-2", style={'fontWeight': '700'}),
                    html.P("Seu estado de forma física atual e tendências recentes", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                ], className="text-center py-4")
            ])
        ], className="bg-light rounded-3 mb-5"),

        # Cards de métricas principais
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.Div("💪", style={'fontSize': '2.5rem'}),
                                dbc.Badge(ctl_status['label'], color=ctl_status['badge'], className="mb-2", style={'fontSize': '0.7rem'})
                            ], className="mb-2"),
                            html.H5("Fitness (CTL)", className="text-primary mb-2", style={'fontWeight': '600'}),
                            html.H1(f"{last_metric['ctl']:.2f}", className="display-4 mb-2", style={'fontWeight': '800', 'color': ctl_status['color']}),
                            html.P(f"{ctl_arrow} {ctl_change:+.2f}% vs semana anterior", className="text-muted mb-2 small"),
                            # Mini sparkline
                            dcc.Graph(
                                figure=go.Figure(
                                    data=[go.Scatter(
                                        y=ctl_sparkline,
                                        mode='lines',
                                        line=dict(color=ctl_status['color'], width=2),
                                        fill='tozeroy',
                                        fillcolor=f"rgba({int(ctl_status['color'][1:3], 16)}, {int(ctl_status['color'][3:5], 16)}, {int(ctl_status['color'][5:7], 16)}, 0.2)"
                                    )],
                                    layout=go.Layout(
                                        height=60,
                                        margin=dict(l=0, r=0, t=0, b=0),
                                        xaxis=dict(visible=False),
                                        yaxis=dict(visible=False),
                                        showlegend=False,
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)'
                                    )
                                ),
                                config={'displayModeBar': False},
                                style={'height': '60px'}
                            )
                        ], className="text-center")
                    ])
                ], className="mb-4 shadow-sm border-0 status-card", style={'borderRadius': '15px', 'background': 'white'})
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.Div("😴", style={'fontSize': '2.5rem'}),
                                dbc.Badge(atl_status['label'], color=atl_status['badge'], className="mb-2", style={'fontSize': '0.7rem'})
                            ], className="mb-2"),
                            html.H5("Fadiga (ATL)", className="text-danger mb-2", style={'fontWeight': '600'}),
                            html.H1(f"{last_metric['atl']:.2f}", className="display-4 mb-2", style={'fontWeight': '800', 'color': atl_status['color']}),
                            html.P(f"{atl_arrow} {atl_change:+.2f}% vs semana anterior", className="text-muted mb-2 small"),
                            # Mini sparkline
                            dcc.Graph(
                                figure=go.Figure(
                                    data=[go.Scatter(
                                        y=atl_sparkline,
                                        mode='lines',
                                        line=dict(color=atl_status['color'], width=2),
                                        fill='tozeroy',
                                        fillcolor=f"rgba({int(atl_status['color'][1:3], 16)}, {int(atl_status['color'][3:5], 16)}, {int(atl_status['color'][5:7], 16)}, 0.2)"
                                    )],
                                    layout=go.Layout(
                                        height=60,
                                        margin=dict(l=0, r=0, t=0, b=0),
                                        xaxis=dict(visible=False),
                                        yaxis=dict(visible=False),
                                        showlegend=False,
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)'
                                    )
                                ),
                                config={'displayModeBar': False},
                                style={'height': '60px'}
                            )
                        ], className="text-center")
                    ])
                ], className="mb-4 shadow-sm border-0 status-card", style={'borderRadius': '15px', 'background': 'white'})
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            html.Div([
                                html.Div("⚖️", style={'fontSize': '2.5rem'}),
                                dbc.Badge(tsb_status['label'], color=tsb_status['badge'], className="mb-2", style={'fontSize': '0.7rem'})
                            ], className="mb-2"),
                            html.H5("Forma (TSB)", className="text-success mb-2", style={'fontWeight': '600'}),
                            html.H1(f"{last_metric['tsb']:.2f}", className="display-4 mb-2", style={'fontWeight': '800', 'color': tsb_status['color']}),
                            html.P(f"{tsb_arrow} {tsb_change:+.2f}% vs semana anterior", className="text-muted mb-2 small"),
                            # Mini sparkline
                            dcc.Graph(
                                figure=go.Figure(
                                    data=[go.Scatter(
                                        y=tsb_sparkline,
                                        mode='lines',
                                        line=dict(color=tsb_status['color'], width=2),
                                        fill='tozeroy',
                                        fillcolor=f"rgba({int(tsb_status['color'][1:3], 16)}, {int(tsb_status['color'][3:5], 16)}, {int(tsb_status['color'][5:7], 16)}, 0.2)" if tsb_status['color'].startswith('#') else 'rgba(40, 167, 69, 0.2)'
                                    )],
                                    layout=go.Layout(
                                        height=60,
                                        margin=dict(l=0, r=0, t=0, b=0),
                                        xaxis=dict(visible=False),
                                        yaxis=dict(visible=False),
                                        showlegend=False,
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)'
                                    )
                                ),
                                config={'displayModeBar': False},
                                style={'height': '60px'}
                            )
                        ], className="text-center")
                    ])
                ], className="mb-4 shadow-sm border-0 status-card", style={'borderRadius': '15px', 'background': 'white'})
            ], md=4)
        ], className="mb-5"),
        
        # ============ ANÁLISE: TENDÊNCIAS HISTÓRICAS ============
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("📈 Análise", className="text-info mb-2", style={'fontWeight': '700'}),
                    html.P("Tendências históricas e evolução do seu treinamento (42 dias)", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                ], className="text-center py-3")
            ])
        ], className="bg-light rounded-3 mb-4"),

        # Gráfico de análise completa
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_metrics_chart(metrics),
                            style={'height': '600px'},
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-4"),

        # Separador visual
        html.Hr(className="my-5", style={'border': '2px solid #e9ecef', 'borderRadius': '2px'}),







# ============ ÚLTIMAS ATIVIDADES ============
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("📋 Atividades", className="text-success mb-2", style={'fontWeight': '700'}),
                    html.P("Suas atividades de treinamento mais recentes", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                ], className="text-center py-3")
            ])
        ], className="bg-light rounded-3 mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("🏃‍♂️ Atividades Recentes", className="card-title mb-3 text-center", style={'fontWeight': '600'}),
                        create_recent_activities_table()
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-4"),

        # Separador visual com gradiente
        html.Div([
            html.Hr(style={
                'border': 'none',
                'height': '3px',
                'background': 'linear-gradient(90deg, transparent, #667eea, #764ba2, transparent)',
                'margin': '4rem 0',
                'borderRadius': '3px'
            })
        ]),

        # ============ TREINOS DA SEMANA ============
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4("📈 Treinos da Semana", className="mb-2", style={'fontWeight': '700'}),
                    html.Div(style={'width': '50px', 'height': '3px', 'background': 'linear-gradient(90deg, #667eea, #764ba2)', 'marginBottom': '1rem', 'borderRadius': '2px'})
                ]),
                dcc.Graph(
                    figure=create_weekly_chart(),
                    style={'height': '400px', 'width': '100%'},
                    config={'displayModeBar': False, 'responsive': True}
                )
            ], md=12, style={'padding': '0 15px'})
        ], className="mb-4"),

        # ============ DISTRIBUIÇÃO DOS TIPOS DE TREINO ============
        dbc.Row([
            dbc.Col([
                html.H4("🥧 Distribuição dos Tipos de Treino", className="mb-3"),
                dcc.Graph(
                    figure=create_distribution_chart(),
                    style={'height': '350px'},
                    config={'displayModeBar': False}
                )
            ])
        ], className="mb-4"),

        # Separador visual
        html.Hr(className="my-5", style={'border': '2px solid #e9ecef', 'borderRadius': '2px'}),

        # ============ HISTÓRICO DE MÉTRICAS ============
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("📊 Histórico", className="text-dark mb-2", style={'fontWeight': '700'}),
                    html.P("Evolução das suas métricas nos últimos 7 dias", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                ], className="text-center py-3")
            ])
        ], className="bg-light rounded-3 mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📈 Métricas dos Últimos 7 Dias", className="card-title mb-3 text-center", style={'fontWeight': '600'}),
                        create_metrics_history_table(metrics)
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-4"),

        # Separador visual com gradiente
        html.Div([
            html.Hr(style={
                'border': 'none',
                'height': '3px',
                'background': 'linear-gradient(90deg, transparent, #f093fb, #f5576c, transparent)',
                'margin': '4rem 0',
                'borderRadius': '3px'
            })
        ]),

        # ============ ANÁLISE POR MODALIDADE ============
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("🏃 Análise", className="text-primary mb-2", style={'fontWeight': '700'}),
                    html.P("Desempenho detalhado por modalidade esportiva", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                ], className="text-center py-3")
            ])
        ], className="bg-light rounded-3 mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        create_modality_analysis_tabs()
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-4"),

    ])

def create_metrics_chart(metrics):
    try:
        # Preparar dados
        dates = [m['date'] for m in metrics]
        ctl = [m['ctl'] for m in metrics]
        atl = [m['atl'] for m in metrics]
        tsb = [m['tsb'] for m in metrics]
        
        # Carregar configuração para metas
        config = load_config()
        ctl_target = config.get('ctl_target', 50.0)  # Meta de CTL ideal
        atl_max = config.get('atl_max', 80.0)  # ATL máximo recomendado

        # Calcular deltas semanais e percentuais
        if len(metrics) >= 8:
            delta_ctl = ctl[-1] - ctl[-8]
            pct_ctl = (ctl[-1] / ctl[-8] - 1) * 100 if ctl[-8] != 0 else 0
            delta_atl = atl[-1] - atl[-8]
            pct_atl = (atl[-1] / atl[-8] - 1) * 100 if atl[-8] != 0 else 0
            delta_tsb = tsb[-1] - tsb[-8]
            pct_tsb = (tsb[-1] / tsb[-8] - 1) * 100 if tsb[-8] != 0 else 0
        else:
            delta_ctl = delta_atl = delta_tsb = pct_ctl = pct_atl = pct_tsb = 0

        # Calcular média móvel 7 dias
        if len(ctl) >= 7:
            ctl_ma = np.convolve(ctl, np.ones(7)/7, mode='valid').tolist()
            atl_ma = np.convolve(atl, np.ones(7)/7, mode='valid').tolist()
            tsb_ma = np.convolve(tsb, np.ones(7)/7, mode='valid').tolist()
            ma_dates = dates[6:]
        else:
            ctl_ma = atl_ma = tsb_ma = []
            ma_dates = []

        # Criar figura com subplots usando Plotly
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Métricas de Performance - Análise Completa', 'Mudanças na Última Semana', 'Progresso Mensal (Médias)'),
            row_heights=[0.55, 0.22, 0.23],
            vertical_spacing=0.15
        )

        # ========== SUBPLOT 1: Gráfico Principal ==========
        # Destacar finais de semana
        for date_str in dates:
            try:
                from datetime import datetime as dt_parse
                date_obj = dt_parse.fromisoformat(date_str)
                # 5=sábado, 6=domingo
                if date_obj.weekday() in [5, 6]:
                    fig.add_vrect(
                        x0=date_str, x1=date_str,
                        fillcolor="rgba(128, 128, 128, 0.1)",
                        layer="below",
                        line_width=0,
                        row=1, col=1
                    )
            except:
                pass
        
        # Linhas de referência (metas)
        # CTL ideal
        fig.add_trace(
            go.Scatter(
                x=[dates[0], dates[-1]], 
                y=[ctl_target, ctl_target],
                mode='lines',
                name=f'🎯 Meta CTL ({ctl_target:.0f})',
                line=dict(color='#1976d2', width=2, dash='dot'),
                opacity=0.6,
                hovertemplate=f'<b>Meta CTL</b><br>Valor: {ctl_target:.0f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # ATL máximo
        fig.add_trace(
            go.Scatter(
                x=[dates[0], dates[-1]], 
                y=[atl_max, atl_max],
                mode='lines',
                name=f'⚠️ ATL Máximo ({atl_max:.0f})',
                line=dict(color='#d32f2f', width=2, dash='dot'),
                opacity=0.6,
                hovertemplate=f'<b>ATL Máximo</b><br>Valor: {atl_max:.0f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # TSB ideal (zona entre -10 e 5)
        fig.add_trace(
            go.Scatter(
                x=dates + dates[::-1],
                y=[-10]*len(dates) + [5]*len(dates[::-1]),
                fill='toself',
                fillcolor='rgba(56, 142, 60, 0.15)',
                line=dict(width=0),
                name='🟢 Zona TSB Ideal',
                showlegend=True,
                hoverinfo='skip'
            ),
            row=1, col=1
        )
        
        # Linhas principais com tooltips aprimorados
        fig.add_trace(
            go.Scatter(
                x=dates, y=ctl, mode='lines+markers',
                name='💪 CTL (Forma Física)',
                line=dict(color='#1976d2', width=3),
                marker=dict(size=6, symbol='circle'),
                customdata=[[f"{c:.2f}", f"{(c/ctl_target*100):.0f}%" if ctl_target > 0 else "N/A"] for c in ctl],
                hovertemplate='<b>💪 CTL - Forma Física</b><br>' +
                             'Data: %{x}<br>' +
                             'Valor: %{customdata[0]}<br>' +
                             'Meta: %{customdata[1]}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=dates, y=atl, mode='lines+markers',
                name='😴 ATL (Fadiga)',
                line=dict(color='#d32f2f', width=3),
                marker=dict(size=6, symbol='square'),
                customdata=[[f"{a:.2f}", f"{(a/atl_max*100):.0f}%" if atl_max > 0 else "N/A"] for a in atl],
                hovertemplate='<b>😴 ATL - Fadiga</b><br>' +
                             'Data: %{x}<br>' +
                             'Valor: %{customdata[0]}<br>' +
                             'vs Máximo: %{customdata[1]}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=dates, y=tsb, mode='lines+markers',
                name='⚖️ TSB (Equilíbrio)',
                line=dict(color='#388e3c', width=3),
                marker=dict(size=6, symbol='triangle-up'),
                customdata=[[f"{t:.2f}", "Descansado" if t > 25 else "Fresco" if t > 5 else "Ideal" if t > -10 else "Cansado"] for t in tsb],
                hovertemplate='<b>⚖️ TSB - Equilíbrio</b><br>' +
                             'Data: %{x}<br>' +
                             'Valor: %{customdata[0]}<br>' +
                             'Status: %{customdata[1]}<extra></extra>'
            ),
            row=1, col=1
        )

        # Médias móveis
        if ctl_ma:
            fig.add_trace(
                go.Scatter(
                    x=ma_dates, y=ctl_ma, mode='lines',
                    name='MA-7 CTL',
                    line=dict(color='#1976d2', width=2, dash='dash', shape='spline'),
                    opacity=0.7,
                    hovertemplate='<b>MA-7 CTL</b><br>Data: %{x}<br>Valor: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=ma_dates, y=atl_ma, mode='lines',
                    name='MA-7 ATL',
                    line=dict(color='#d32f2f', width=2, dash='dash', shape='spline'),
                    opacity=0.7,
                    hovertemplate='<b>MA-7 ATL</b><br>Data: %{x}<br>Valor: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=ma_dates, y=tsb_ma, mode='lines',
                    name='MA-7 TSB',
                    line=dict(color='#388e3c', width=2, dash='dash', shape='spline'),
                    opacity=0.7,
                    hovertemplate='<b>MA-7 TSB</b><br>Data: %{x}<br>Valor: %{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )

        # ========== SUBPLOT 2: Deltas Semanais ==========
        labels_delta = ['CTL', 'ATL', 'TSB']
        deltas = [delta_ctl, delta_atl, delta_tsb]
        colors_delta = ['#1976d2', '#d32f2f', '#388e3c']

        fig.add_trace(
            go.Bar(
                x=labels_delta,
                y=deltas,
                marker_color=colors_delta,
                text=[f'{d:+.1f}' for d in deltas],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Delta: %{y:+.1f}<extra></extra>'
            ),
            row=2, col=1
        )

        # ========== SUBPLOT 3: Progresso Mensal ==========
        months = []
        ctl_monthly = []
        atl_monthly = []
        tsb_monthly = []
        current_month = None
        month_data = {'ctl': [], 'atl': [], 'tsb': []}

        for m in metrics:
            try:
                from datetime import datetime as dt_parse
                date = dt_parse.fromisoformat(m['date'])
                month = date.strftime('%b')  # Abreviado (Jan, Fev, etc)
                if current_month != month:
                    if current_month is not None:
                        ctl_monthly.append(np.mean(month_data['ctl']))
                        atl_monthly.append(np.mean(month_data['atl']))
                        tsb_monthly.append(np.mean(month_data['tsb']))
                        months.append(current_month)
                    current_month = month
                    month_data = {'ctl': [], 'atl': [], 'tsb': []}
                month_data['ctl'].append(m['ctl'])
                month_data['atl'].append(m['atl'])
                month_data['tsb'].append(m['tsb'])
            except:
                continue

        if month_data['ctl']:
            ctl_monthly.append(np.mean(month_data['ctl']))
            atl_monthly.append(np.mean(month_data['atl']))
            tsb_monthly.append(np.mean(month_data['tsb']))
            months.append(current_month)

        if months:
            fig.add_trace(
                go.Scatter(
                    x=months, y=ctl_monthly, mode='lines+markers',
                    name='CTL Médio',
                    line=dict(color='#1976d2', width=3),
                    marker=dict(size=8, symbol='circle'),
                    hovertemplate='<b>CTL Médio</b><br>Mês: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=months, y=atl_monthly, mode='lines+markers',
                    name='ATL Médio',
                    line=dict(color='#d32f2f', width=3),
                    marker=dict(size=8, symbol='square'),
                    hovertemplate='<b>ATL Médio</b><br>Mês: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=3, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=months, y=tsb_monthly, mode='lines+markers',
                    name='TSB Médio',
                    line=dict(color='#388e3c', width=3),
                    marker=dict(size=8, symbol='triangle-up'),
                    hovertemplate='<b>TSB Médio</b><br>Mês: %{x}<br>Valor: %{y:.1f}<extra></extra>'
                ),
                row=3, col=1
            )

        # Configurar layout geral
        trend_ctl = "📈" if delta_ctl > 0 else "📉" if delta_ctl < 0 else "➡️"
        trend_atl = "📈" if delta_atl > 0 else "📉" if delta_atl < 0 else "➡️"
        trend_tsb = "📈" if delta_tsb > 0 else "📉" if delta_tsb < 0 else "➡️"

        fig.update_layout(
            height=1000,
            autosize=True,  # Permitir responsividade horizontal
            title={
                'text': f'Análise Completa das Métricas de Performance<br><span style="font-size:14px;color:#6c757d;">Tendência Semanal: CTL {trend_ctl} {delta_ctl:+.1f} ({pct_ctl:+.1f}%) | ATL {trend_atl} {delta_atl:+.1f} ({pct_atl:+.1f}%) | TSB {trend_tsb} {delta_tsb:+.1f} ({pct_tsb:+.1f}%)</span>',
                'y': 0.985,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 16, 'color': '#212529'}
            },
            font={'family': 'Inter, -apple-system, sans-serif', 'size': 12},
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            hovermode='x unified',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.08,
                xanchor='center',
                x=0.5,
                font={'size': 11}
            ),
            margin=dict(t=100, b=80, l=60, r=40)
        )

        # Configurar eixos
        fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)
        fig.update_yaxes(title_text='Pontuação', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)
        fig.update_yaxes(title_text='Delta Semanal', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=2, col=1)
        fig.update_xaxes(title_text='Mês', showgrid=False, row=3, col=1)
        fig.update_yaxes(title_text='Pontuação', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=3, col=1)

        # Adicionar linha zero no subplot 2
        fig.add_hline(y=0, line_width=1, line_color='black', row=2, col=1)

        return fig
        
    except Exception as e:
        # Retornar gráfico vazio em caso de erro
        fig = go.Figure()
        fig.update_layout(
            title="Erro ao carregar dados",
            height=800,
            autosize=True
        )
        return fig

def create_weekly_chart():
    try:
        workouts = enrich_workouts_with_tss(load_workouts())
        
        # Definir semana atual (segunda a domingo)
        now = datetime.now()
        days_since_monday = now.isoweekday() - 1  # 0=segunda, 6=domingo
        week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # Inicializar arrays para cada dia da semana (seg-dom)
        dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        corrida = [0.0] * 7
        ciclismo = [0.0] * 7
        natacao = [0.0] * 7
        forca = [0.0] * 7
        
        # Processar atividades da semana
        for workout in workouts:
            try:
                start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
                if not start_time:
                    continue
                    
                activity_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                
                # Verificar se está na semana atual
                if week_start <= activity_date <= week_end:
                    # Calcular dia da semana (0=segunda, 6=domingo)
                    day_index = activity_date.isoweekday() - 1
                    
                    # Duração em horas
                    duration_hours = float(workout.get('duration', 0) or 0) / 3600
                    
                    # Categorizar por modalidade
                    category = _activity_category(workout)
                    if category == 'running':
                        corrida[day_index] += duration_hours
                    elif category == 'cycling':
                        ciclismo[day_index] += duration_hours
                    elif category == 'swimming':
                        natacao[day_index] += duration_hours
                    elif category == 'strength':
                        forca[day_index] += duration_hours
            except Exception as e:
                continue
        
        # Converter arrays para formato hh:mm:ss
        corrida_hms = [format_hours_to_hms(h) for h in corrida]
        ciclismo_hms = [format_hours_to_hms(h) for h in ciclismo]
        natacao_hms = [format_hours_to_hms(h) for h in natacao]
        forca_hms = [format_hours_to_hms(h) for h in forca]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='🏃 Corrida', 
            x=dias, 
            y=corrida,
            customdata=corrida_hms,
            marker_color='#fd7e14',
            hovertemplate='<b>Corrida</b><br>%{x}<br>%{customdata}<extra></extra>'
        ))
        fig.add_trace(go.Bar(
            name='🚴 Ciclismo', 
            x=dias, 
            y=ciclismo,
            customdata=ciclismo_hms,
            marker_color='#28a745',
            hovertemplate='<b>Ciclismo</b><br>%{x}<br>%{customdata}<extra></extra>'
        ))
        fig.add_trace(go.Bar(
            name='🏊 Natação', 
            x=dias, 
            y=natacao,
            customdata=natacao_hms,
            marker_color='#007bff',
            hovertemplate='<b>Natação</b><br>%{x}<br>%{customdata}<extra></extra>'
        ))
        fig.add_trace(go.Bar(
            name='💪 Força', 
            x=dias, 
            y=forca,
            customdata=forca_hms,
            marker_color='#6f42c1',
            hovertemplate='<b>Força</b><br>%{x}<br>%{customdata}<extra></extra>'
        ))
        
        # Formatar título com datas da semana
        week_start_str = week_start.strftime("%d %b")
        week_end_str = week_end.strftime("%d %b")
        
        fig.update_layout(
            barmode='stack',
            title=f'Treinos da Semana ({week_start_str} - {week_end_str})',
            xaxis_title='Dia da Semana',
            yaxis_title='Horas de Treino',
            height=400,
            autosize=True,  # Habilitar autosize para usar toda largura
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.3,
                xanchor='center',
                x=0.5,
                font={'size': 11}
            ),
            margin=dict(l=50, r=30, t=80, b=120)
        )
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.update_layout(
            title="Erro ao carregar gráfico semanal",
            height=400
        )
        return fig

def create_distribution_chart():
    try:
        workouts = enrich_workouts_with_tss(load_workouts())
        
        # Definir semana atual (segunda a domingo)
        now = datetime.now()
        days_since_monday = now.isoweekday() - 1  # 0=segunda, 6=domingo
        week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        # Calcular distribuição da semana atual
        from collections import defaultdict
        distribuicao = defaultdict(lambda: {'horas': 0, 'atividades': 0})
        
        for w in workouts:
            try:
                start_time = w.get('startTimeLocal', w.get('startTime', ''))
                if not start_time:
                    continue
                    
                activity_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                
                # Verificar se está na semana atual
                if not (week_start <= activity_date <= week_end):
                    continue
                
                tipo = w.get('activityType', {}).get('typeKey', '').lower()
                duracao_horas = (w.get('duration', 0) or 0) / 3600
                
                if tipo in ['running', 'treadmill_running', 'track_running', 'trail_running', 'indoor_running', 'virtual_running']:
                    distribuicao['🏃 Corrida']['horas'] += duracao_horas
                    distribuicao['🏃 Corrida']['atividades'] += 1
                elif tipo in ['cycling', 'road_cycling', 'mountain_biking', 'indoor_cycling', 'gravel_cycling', 'virtual_cycling', 'virtual_ride', 'indoor_biking', 'bike', 'biking']:
                    distribuicao['🚴 Ciclismo']['horas'] += duracao_horas
                    distribuicao['🚴 Ciclismo']['atividades'] += 1
                elif tipo in ['swimming', 'pool_swimming', 'open_water_swimming', 'indoor_swimming', 'lap_swimming']:
                    distribuicao['🏊 Natação']['horas'] += duracao_horas
                    distribuicao['🏊 Natação']['atividades'] += 1
                elif tipo in ['strength_training', 'weight_training', 'functional_strength_training', 'gym_strength_training', 'crossfit', 'hiit']:
                    distribuicao['💪 Força']['horas'] += duracao_horas
                    distribuicao['💪 Força']['atividades'] += 1
                else:
                    distribuicao['⚽ Outros']['horas'] += duracao_horas
                    distribuicao['⚽ Outros']['atividades'] += 1
            except:
                continue
        
        # Preparar dados para o gráfico
        tipos = []
        horas = []
        atividades = []
        
        for tipo, dados in distribuicao.items():
            if dados['horas'] > 0:
                tipos.append(tipo)
                horas.append(dados['horas'])
                atividades.append(dados['atividades'])
        
        # Se não houver dados, mostrar vazio
        if not tipos:
            tipos = ['Sem dados']
            horas = [0]
            atividades = [0]
        
        # Criar gráfico de barras horizontais
        fig = go.Figure()
        
        # Mapeamento de cores
        cores = {
            '🏃 Corrida': '#fd7e14',
            '🚴 Ciclismo': '#28a745', 
            '🏊 Natação': '#007bff',
            '💪 Força': '#6f42c1',
            '⚽ Outros': '#6c757d'
        }
        
        fig.add_trace(go.Bar(
            x=horas,
            y=tipos,
            orientation='h',
            marker=dict(
                color=[cores.get(t, '#6c757d') for t in tipos],
                line=dict(width=0)
            ),
            text=[f'{h:.1f}h<br>{a} atividades' for h, a in zip(horas, atividades)],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Horas: %{x:.1f}h<br>Atividades: %{customdata}<extra></extra>',
            customdata=atividades
        ))
        
        # Calcular total
        total_horas = sum(horas)
        total_atividades = sum(atividades)
        
        fig.update_layout(
            title={
                'text': f'Distribuição dos Tipos de Treino<br><span style="font-size:14px;color:#6c757d;">Total: {total_horas:.1f}h | {total_atividades} atividades</span>',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 16, 'color': '#212529'}
            },
            xaxis_title='Horas de Treino',
            font={'family': 'Inter, -apple-system, sans-serif', 'size': 12},
            plot_bgcolor='rgba(248,249,250,0.5)',
            paper_bgcolor='white',
            showlegend=False,
            margin=dict(l=120, r=50, t=80, b=50),
            height=300
        )
        
        # Melhorar aparência dos eixos
        fig.update_xaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False)
        fig.update_yaxes(showgrid=False)
        
        return fig
        
    except Exception as e:
        fig = go.Figure()
        fig.update_layout(
            title="Erro ao carregar distribuição",
            height=300
        )
        return fig

def create_recent_activities_table():
    try:
        workouts = enrich_workouts_with_tss(load_workouts())
        if not workouts:
            return html.Div("Nenhuma atividade encontrada.", className="text-muted")
        
        config_for_tss = load_config()
        
        def _modality_tss(category: str, tss_data: dict) -> float:
            if category == 'running':
                return float(tss_data.get('rtss', 0) or 0) or float(tss_data.get('hrtss', 0) or 0) or float(tss_data.get('tss', 0) or 0)
            if category == 'swimming':
                return float(tss_data.get('stss', 0) or 0) or float(tss_data.get('hrtss', 0) or 0) or float(tss_data.get('tss', 0) or 0)
            if category == 'cycling':
                return float(tss_data.get('tss', 0) or 0)
            return float(tss_data.get('hrtss', 0) or 0) or float(tss_data.get('tss', 0) or 0) or 0.0
        
        def get_activity_datetime(w):
            from datetime import datetime as dt
            if w.get('startTimeLocal'):
                try:
                    return dt.strptime(w['startTimeLocal'], '%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            if w.get('startTimeGMT'):
                try:
                    return dt.strptime(w['startTimeGMT'], '%Y-%m-%d %H:%M:%S')
                except Exception:
                    pass
            if w.get('startTimeInSeconds'):
                return dt.fromtimestamp(w['startTimeInSeconds'])
            return dt(1970,1,1)
        
        recent_workouts = sorted(workouts, key=get_activity_datetime, reverse=True)[:10]
        
        table_rows = []
        for w in recent_workouts:
            try:
                activity_name = w.get('activityName', 'Atividade Desconhecida')
                distance = w.get('distance', 0) or 0
                duration_hours = float(w.get('duration', 0) or 0) / 3600
                
                type_key = (w.get('activityType') or {}).get('typeKey', '')
                category = _activity_category(w)
                tss_calc = compute_tss_variants(w, config_for_tss)
                tss_value = _modality_tss(category, tss_calc)
                
                modality_label = {
                    'cycling': '🚴 Bike',
                    'running': '🏃 Corrida',
                    'swimming': '🏊 Natação',
                    'strength': '💪 Força',
                    'other': '⚽ Outros'
                }.get(category, '⚽ Outros')
                
                # Determinar intensidade baseada em TSS
                def get_intensity_badge(tss):
                    if tss < 50:
                        return dbc.Badge("Leve", color="success", className="me-1", style={'fontSize': '0.7rem'})
                    elif tss < 100:
                        return dbc.Badge("Moderado", color="info", className="me-1", style={'fontSize': '0.7rem'})
                    elif tss < 150:
                        return dbc.Badge("Intenso", color="warning", className="me-1", style={'fontSize': '0.7rem'})
                    else:
                        return dbc.Badge("Muito Intenso", color="danger", className="me-1", style={'fontSize': '0.7rem'})
                
                # Calcular pace/velocidade se disponível
                pace_info = ""
                if distance > 0 and duration_hours > 0:
                    try:
                        if category == 'running':
                            # Calcular pace (min/km)
                            pace_min_per_km = (duration_hours * 60) / (distance / 1000)
                            pace_mins = int(pace_min_per_km)
                            pace_secs = int((pace_min_per_km - pace_mins) * 60)
                            pace_info = f"{pace_mins}:{pace_secs:02d}/km"
                        elif category in ['cycling', 'swimming']:
                            # Calcular velocidade (km/h)
                            speed = (distance / 1000) / duration_hours
                            pace_info = f"{speed:.1f} km/h"
                    except:
                        pace_info = ""
                
                # Formatar distância
                if distance >= 1000:
                    distance_str = f"{distance/1000:.2f} km"
                else:
                    distance_str = f"{distance:.0f} m"
                
                table_rows.append(html.Tr([
                    html.Td([
                        html.Div(activity_name[:35] + "..." if len(activity_name) > 35 else activity_name, 
                                style={'fontWeight': '500', 'marginBottom': '2px'}),
                        html.Small(pace_info, className="text-muted") if pace_info else None
                    ]),
                    html.Td(modality_label),
                    html.Td(distance_str),
                    html.Td(format_hours_to_hms(duration_hours)),
                    html.Td([
                        get_intensity_badge(tss_value),
                        html.Span(f"{tss_value:.0f}", style={'fontWeight': '600'})
                    ])
                ]))
                
            except Exception as e:
                # Continuar mesmo com erro, para garantir que exibimos todas as atividades possíveis
                print(f"Erro ao processar atividade: {e}")
                continue
        
        return dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Atividade", style={'width': '35%'}),
                    html.Th("Modalidade", style={'width': '15%'}),
                    html.Th("Distância", style={'width': '15%'}),
                    html.Th("Duração", style={'width': '15%'}),
                    html.Th("TSS / Intensidade", style={'width': '20%'})
                ], style={'background': '#f8f9fa'})
            ]),
            html.Tbody(table_rows)
        ], bordered=True, hover=True, responsive=True, size="sm", className="mb-0", 
           style={'background': 'white'})
        
    except Exception as e:
        return html.Div("Erro ao carregar atividades recentes.", className="text-danger")

def create_metrics_history_table(metrics):
    try:
        if not metrics or len(metrics) < 7:
            return html.Div("Dados insuficientes para mostrar histórico de 7 dias.", className="text-muted")
        
        # Pegar os últimos 7 dias e ordenar do mais recente para o mais antigo
        recent_metrics = metrics[-7:][::-1]
        
        table_rows = []
        for m in recent_metrics:
            try:
                date_obj = datetime.fromisoformat(m['date'])
                date_str = date_obj.strftime('%d/%m')
                weekday = date_obj.strftime('%a')  # Mon, Tue, etc.
                daily_load = m.get('daily_load', 0.0)
                
                table_rows.append(html.Tr([
                    html.Td(f"{date_str} ({weekday})"),
                    html.Td(f"{m['ctl']:.2f}"),
                    html.Td(f"{m['atl']:.2f}"),
                    html.Td(f"{m['tsb']:.2f}"),
                    html.Td(f"{daily_load:.1f}")
                ]))
                
            except Exception as e:
                continue
        
        return dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Data"),
                    html.Th("CTL"),
                    html.Th("ATL"),
                    html.Th("TSB"),
                    html.Th("Carga Diária")
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, bordered=True, hover=True, responsive=True, size="sm", className="mb-0")
        
    except Exception as e:
        return html.Div("Erro ao carregar histórico de métricas.", className="text-danger")

def calculate_modality_progress(activities):
    """Calcula progresso por modalidade agrupado por semana (42 dias)"""
    if not activities:
        return {}

    # Usar a data da atividade mais recente como referência
    if activities:
        most_recent = max(activities, key=lambda x: datetime.strptime(x.get('startTimeLocal', x.get('startTime', '1900-01-01')), "%Y-%m-%d %H:%M:%S"))
        now = datetime.strptime(most_recent.get('startTimeLocal', most_recent.get('startTime', '1900-01-01')), "%Y-%m-%d %H:%M:%S")
    else:
        now = datetime.now()

    # Ajustar para o domingo mais recente (fim da semana)
    days_since_monday = now.isoweekday() - 1  # 0=segunda, 6=domingo
    end_of_current_week = now + timedelta(days=(6 - days_since_monday))
    
    # Calcular 42 dias (6 semanas completas) para trás a partir do domingo
    start_date = end_of_current_week - timedelta(days=41)  # 41 dias = 6 semanas - 1 dia
    # Ajustar para segunda-feira mais próxima
    start_date = start_date - timedelta(days=start_date.isoweekday() - 1)

    # Inicializar estrutura de dados
    modalities = ['cycling', 'running', 'swimming', 'strength']
    modality_data = {mod: [] for mod in modalities}

    # Agrupar atividades por modalidade e semana
    for activity in activities:
        try:
            activity_date = datetime.strptime(
                activity.get('startTimeLocal', activity.get('startTime', '1900-01-01')),
                "%Y-%m-%d %H:%M:%S"
            )

            # Pular atividades fora do período de 42 dias
            if activity_date < start_date:
                continue

            # Categorizar atividade
            activity_type = _activity_category(activity)
            if activity_type not in modalities:
                continue

            # Calcular semana (0-5, onde 0 é a semana mais antiga, começando na segunda)
            days_diff = (activity_date - start_date).days
            week_num = min(days_diff // 7, 5)  # Limitar a 6 semanas (0-5)

            # Dados da atividade
            distance = float(activity.get('distance', 0) or 0) / 1000  # km
            tss = float(activity.get('tss', 0) or 0)
            duration = float(activity.get('duration', 0) or 0) / 3600  # horas

            # Adicionar à modalidade correspondente
            if week_num < 6:  # Apenas 6 semanas (42 dias)
                modality_data[activity_type].append({
                    'week': week_num,
                    'distance': distance,
                    'tss': tss,
                    'duration': duration,
                    'date': activity_date.date()
                })

        except Exception as e:
            continue

    # Agregar por semana para cada modalidade
    result = {}
    for modality in modalities:
        weekly_data = {}
        for activity in modality_data[modality]:
            week = activity['week']
            if week not in weekly_data:
                weekly_data[week] = {
                    'distance': 0,
                    'tss': 0,
                    'duration': 0,
                    'activities': 0,
                    'week_start': start_date + timedelta(days=week*7)
                }
            weekly_data[week]['distance'] += activity['distance']
            weekly_data[week]['tss'] += activity['tss']
            weekly_data[week]['duration'] += activity['duration']
            weekly_data[week]['activities'] += 1

        # Converter para lista ordenada por semana
        result[modality] = []
        for week in range(6):
            if week in weekly_data:
                result[modality].append(weekly_data[week])
            else:
                result[modality].append({
                    'distance': 0,
                    'tss': 0,
                    'duration': 0,
                    'activities': 0,
                    'week_start': start_date + timedelta(days=week*7)
                })

    return result

def create_modality_analysis_tabs():
    try:
        workouts = enrich_workouts_with_tss(load_workouts())
        config = load_config()
        
        if not workouts:
            return html.Div("Nenhum dado de treino disponível para análise.", className="text-muted")
        
        # Calcular progresso por modalidade
        modality_progress = calculate_modality_progress(workouts)
        
        tabs = []
        
        # Cores padronizadas por modalidade
        modality_colors = {
            'cycling': {'primary': '#28a745', 'secondary': '#d4edda', 'name': '🚴 Ciclismo'},
            'running': {'primary': '#fd7e14', 'secondary': '#ffe5d0', 'name': '🏃 Corrida'},
            'swimming': {'primary': '#007bff', 'secondary': '#cce5ff', 'name': '🏊 Natação'},
            'strength': {'primary': '#6f42c1', 'secondary': '#e7d9ff', 'name': '💪 Força'}
        }
        
        for modality_key, modality_info in modality_colors.items():
            data = modality_progress.get(modality_key, [])
            
            if not data:
                tab_content = html.Div("Nenhum dado encontrado para esta modalidade.", className="text-muted p-3")
            else:
                # Calcular métricas totais
                total_distance = sum(week['distance'] for week in data)
                total_tss = sum(week['tss'] for week in data)
                total_hours = sum(week['duration'] for week in data)
                total_activities = sum(week['activities'] for week in data)
                
                # Criar tabela semanal
                table_rows = []
                for i, week_data in enumerate(data):
                    week_start = week_data['week_start']
                    week_end = week_start + timedelta(days=6)
                    table_rows.append(html.Tr([
                        html.Td(f'Semana {i+1}'),
                        html.Td(f'{week_start.strftime("%d/%m")} - {week_end.strftime("%d/%m")}'),
                        html.Td(f"{week_data['distance']:.1f} km"),
                        html.Td(f"{week_data['tss']:.2f}"),
                        html.Td(format_hours_to_hms(week_data['duration'])),
                        html.Td(week_data['activities'])
                    ]))
                
                tab_content = dbc.Container([
                    # Cards de métricas
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("📏 Distância Total", className="card-title text-center"),
                                    html.H4(f"{total_distance:.1f} km", className="text-center", style={'color': modality_info['primary']})
                                ])
                            ], className="mb-3")
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("🎯 TSS Total", className="card-title text-center"),
                                    html.H4(f"{total_tss:.2f}", className="text-center", style={'color': modality_info['primary']})
                                ])
                            ], className="mb-3")
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("⏱️ Horas Totais", className="card-title text-center"),
                                    html.H4(format_hours_to_hms(total_hours), className="text-center", style={'color': modality_info['primary']})
                                ])
                            ], className="mb-3")
                        ], md=3),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardBody([
                                    html.H6("📊 Atividades", className="card-title text-center"),
                                    html.H4(f"{total_activities}", className="text-center", style={'color': modality_info['primary']})
                                ])
                            ], className="mb-3")
                        ], md=3)
                    ]),
                    
                    # Tabela de progresso semanal
                    dbc.Row([
                        dbc.Col([
                            html.H5("📅 Progresso Semanal", className="mb-3"),
                            dbc.Table([
                                html.Thead([
                                    html.Tr([
                                        html.Th("Semana"),
                                        html.Th("Período"),
                                        html.Th("Distância"),
                                        html.Th("TSS"),
                                        html.Th("Horas"),
                                        html.Th("Atividades")
                                    ])
                                ]),
                                html.Tbody(table_rows)
                            ], striped=True, bordered=True, hover=True, responsive=True, size="sm")
                        ])
                    ]),
                    
                    # Gráficos de evolução semanal
                    dbc.Row([
                        dbc.Col([
                            html.H5("📈 Evolução Semanal Completa", className="mb-3"),
                            dcc.Graph(
                                figure=create_modality_subplot_chart(data, modality_info, modality_key),
                                style={'height': '600px'},
                                config={'displayModeBar': False}
                            )
                        ])
                    ]),
                    
                    # Gráfico de tendência consolidada
                    dbc.Row([
                        dbc.Col([
                            html.H5("📊 Tendência Consolidada (42 dias)", className="mb-3"),
                            dcc.Graph(
                                figure=create_modality_trend_chart(data, modality_info, modality_info['name']),
                                style={'height': '400px'},
                                config={'displayModeBar': False}
                            )
                        ])
                    ])
                ], fluid=False)
            
            tabs.append(
                dbc.Tab(tab_content, label=modality_info['name'], tab_id=f"tab-{modality_key}")
            )
        
        return dbc.Tabs(tabs, active_tab="tab-cycling")
        
    except Exception as e:
        return html.Div("Erro ao carregar análise por modalidade.", className="text-danger")

# Função para criar heatmap de TSS (últimos 90 dias)
def create_tss_heatmap(workouts):
    """Cria heatmap visual de TSS por dia (últimos 90 dias)"""
    try:
        # Organizar TSS por dia
        daily_tss = {}
        for workout in workouts:
            try:
                start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
                if not start_time:
                    continue
                
                activity_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").date()
                date_str = activity_date.strftime('%Y-%m-%d')
                tss = float(workout.get('tss', 0) or 0)
                daily_tss[date_str] = daily_tss.get(date_str, 0) + tss
            except:
                pass
        
        if not daily_tss:
            fig = go.Figure()
            fig.update_layout(
                title="Sem dados de TSS disponíveis para os últimos 90 dias",
                height=300,
                font={'family': 'Inter, -apple-system, sans-serif'}
            )
            return fig
        
        # Últimos 90 dias
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(89, -1, -1)]
        
        # Organizar em semanas (13 semanas x 7 dias)
        weeks = []
        week_labels = []
        for i in range(0, len(dates), 7):
            week = dates[i:i+7]
            if len(week) < 7:  # Preencher semana incompleta com zeros
                week = week + [''] * (7 - len(week))
            weeks.append([daily_tss.get(d, 0) if d else 0 for d in week])
            if week[0]:
                week_start = datetime.strptime(week[0], '%Y-%m-%d')
                week_labels.append(week_start.strftime('%d/%m'))
            else:
                week_labels.append('')
        
        # Transpor para ter dias da semana nas linhas
        if weeks:
            days_data = list(map(list, zip(*weeks)))
        else:
            days_data = [[0] * 13 for _ in range(7)]
        
        # Criar heatmap
        fig = go.Figure(data=go.Heatmap(
            z=days_data,
            x=week_labels,
            y=['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
            colorscale=[
                [0, '#f8f9fa'],
                [0.2, '#d1ecf1'],
                [0.4, '#bee5eb'],
                [0.6, '#7fc8d9'],
                [0.8, '#17a2b8'],
                [1, '#138496']
            ],
            colorbar=dict(
                title=dict(text='TSS', side='right'),
                tickmode='linear',
                tick0=0,
                dtick=50
            ),
            hovertemplate='<b>%{y}</b><br>Semana: %{x}<br>TSS: %{z:.0f}<extra></extra>',
            showscale=True
        ))
        
        fig.update_layout(
            title='Heatmap de TSS - Últimos 90 Dias',
            xaxis_title='Semana (início)',
            yaxis_title='Dia da Semana',
            height=300,
            font={'family': 'Inter, -apple-system, sans-serif', 'size': 11},
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(
                side='bottom',
                tickangle=45
            ),
            yaxis=dict(
                autorange='reversed'
            )
        )
        
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.update_layout(
            title=f"Erro ao criar heatmap",
            height=300,
            font={'family': 'Inter, -apple-system, sans-serif'},
            annotations=[{
                'text': f'Detalhes: {str(e)[:100]}',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False,
                'font': {'size': 12, 'color': '#dc3545'}
            }]
        )
        return fig
        return fig

def render_calendar():
    workouts = enrich_workouts_with_tss(load_workouts())
    config = load_config()
    
    if not workouts:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H1("📅 Calendário", className="text-primary mb-2", style={'fontWeight': '700'}),
                        html.P("Visualize suas atividades dia a dia", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                    ], className="text-center py-3")
                ])
            ], className="bg-light rounded-3 mb-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Alert([
                        html.H5("⚠️ Nenhum treino disponível", className="alert-heading"),
                        html.P("Vá para 'Configuração' para sincronizar com Garmin Connect.")
                    ], color="warning")
                ])
            ])
        ])
    
    # Data atual
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Organizar treinos por data
    workouts_by_date = {}
    monthly_stats = {
        'total_workouts': 0,
        'total_tss': 0,
        'total_distance': 0,
        'total_duration': 0,
        'by_category': {}
    }
    
    for workout in workouts:
        try:
            start_time = workout.get('startTimeLocal', workout.get('startTime', ''))
            if not start_time:
                continue
                
            # Parsear data
            if 'T' in start_time:
                date_obj = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
            else:
                date_obj = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()
            
            # Adicionar ao dicionário
            date_str = date_obj.strftime('%Y-%m-%d')
            if date_str not in workouts_by_date:
                workouts_by_date[date_str] = []
            workouts_by_date[date_str].append(workout)
            
            # Estatísticas do mês atual
            if date_obj.month == current_month and date_obj.year == current_year:
                monthly_stats['total_workouts'] += 1
                monthly_stats['total_tss'] += float(workout.get('tss', 0) or 0)
                monthly_stats['total_distance'] += float(workout.get('distance', 0) or 0) / 1000
                monthly_stats['total_duration'] += float(workout.get('duration', 0) or 0) / 3600
                
                # Por categoria
                category = _activity_category(workout)
                if category not in monthly_stats['by_category']:
                    monthly_stats['by_category'][category] = {'count': 0, 'distance': 0, 'duration': 0, 'tss': 0}
                monthly_stats['by_category'][category]['count'] += 1
                monthly_stats['by_category'][category]['distance'] += float(workout.get('distance', 0) or 0) / 1000
                monthly_stats['by_category'][category]['duration'] += float(workout.get('duration', 0) or 0) / 3600
                monthly_stats['by_category'][category]['tss'] += float(workout.get('tss', 0) or 0)
        except:
            continue
    
    # Criar calendário do mês
    cal = calendar.monthcalendar(current_year, current_month)
    month_name = calendar.month_name[current_month]
    
    # Mapear categorias para emojis
    category_emoji = {
        'running': '🏃',
        'cycling': '🚴',
        'swimming': '🏊',
        'strength': '💪',
        'other': '⚽'
    }
    
    category_names = {
        'running': 'Corrida',
        'cycling': 'Ciclismo',
        'swimming': 'Natação',
        'strength': 'Força',
        'other': 'Outros'
    }
    
    # Construir grade do calendário
    calendar_grid = []
    
    # Cabeçalho dos dias da semana (incluindo coluna de resumo)
    weekday_header = html.Tr([
        html.Th("SEG", className="text-center py-2 px-1", style={'background': '#f8f9fa', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057'}),
        html.Th("TER", className="text-center py-2 px-1", style={'background': '#f8f9fa', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057'}),
        html.Th("QUA", className="text-center py-2 px-1", style={'background': '#f8f9fa', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057'}),
        html.Th("QUI", className="text-center py-2 px-1", style={'background': '#f8f9fa', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057'}),
        html.Th("SEX", className="text-center py-2 px-1", style={'background': '#f8f9fa', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057'}),
        html.Th("SÁB", className="text-center py-2 px-1", style={'background': '#f8f9fa', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057'}),
        html.Th("DOM", className="text-center py-2 px-1", style={'background': '#f8f9fa', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057'}),
        html.Th("RESUMO", className="text-center py-2 px-1", style={'background': '#e9ecef', 'border': '1px solid #dee2e6', 'fontSize': '0.7rem', 'fontWeight': '600', 'color': '#495057', 'minWidth': '120px'})
    ])
    
    # Linhas do calendário
    for week in cal:
        week_cells = []
        week_stats = {'workouts': 0, 'tss': 0, 'distance': 0, 'duration': 0}
        
        for day in week:
            if day == 0:
                # Dia vazio
                week_cells.append(html.Td("", style={'height': '110px', 'background': '#fafafa', 'border': '1px solid #dee2e6'}))
            else:
                date_obj = datetime(current_year, current_month, day).date()
                date_str = date_obj.strftime('%Y-%m-%d')
                
                # Verificar se há treinos neste dia
                day_workouts = workouts_by_date.get(date_str, [])
                
                # Calcular TSS do dia
                day_tss = sum(float(w.get('tss', 0) or 0) for w in day_workouts)
                
                # Acumular estatísticas da semana
                for w in day_workouts:
                    week_stats['workouts'] += 1
                    week_stats['tss'] += float(w.get('tss', 0) or 0)
                    week_stats['distance'] += float(w.get('distance', 0) or 0) / 1000
                    week_stats['duration'] += float(w.get('duration', 0) or 0) / 3600
                
                is_today = date_obj == now.date()
                
                cell_style = {
                    'height': '110px',
                    'verticalAlign': 'top',
                    'background': '#e8f4f8' if is_today else 'white',
                    'border': '2px solid #2196F3' if is_today else '1px solid #dee2e6',
                    'padding': '6px'
                }
                
                # Cabeçalho do dia
                day_header = html.Div([
                    html.Div([
                        html.Span(str(day), style={
                            'fontSize': '0.95rem',
                            'fontWeight': '600',
                            'color': '#2196F3' if is_today else '#212529'
                        }),
                        html.Span(f" • {day_tss:.0f}" if day_tss > 0 else "", style={
                            'fontSize': '0.7rem',
                            'color': '#6c757d',
                            'marginLeft': '4px'
                        })
                    ])
                ], style={'marginBottom': '6px', 'borderBottom': '1px solid #e9ecef', 'paddingBottom': '4px'})
                
                cell_content = [day_header]
                
                if day_workouts:
                    # Cores por categoria (padrão do dashboard)
                    cat_colors = {
                        'running': '#fd7e14',    # Laranja
                        'cycling': '#28a745',    # Verde
                        'swimming': '#007bff',   # Azul
                        'strength': '#6f42c1',   # Roxo
                        'other': '#6c757d'       # Cinza
                    }
                    
                    # Mostrar atividades de forma simples com marcação de cor
                    for i, w in enumerate(day_workouts[:3]):
                        cat = _activity_category(w)
                        emoji = category_emoji.get(cat, '⚽')
                        name = w.get('activityName', 'Treino')[:18]
                        duration_h = float(w.get('duration', 0) or 0) / 3600
                        tss = float(w.get('tss', 0) or 0)
                        color = cat_colors.get(cat, '#95a5a6')
                        
                        activity_item = html.Div([
                            # Linha superior: nome
                            html.Div([
                                html.Span(emoji, style={'marginRight': '3px', 'fontSize': '0.75rem'}),
                                html.Span(name, style={'fontSize': '0.7rem', 'color': '#212529', 'fontWeight': '500'})
                            ], style={'marginBottom': '2px'}),
                            # Linha inferior: tempo e TSS
                            html.Div([
                                html.Span(format_hours_to_hms(duration_h), style={'fontSize': '0.65rem', 'color': '#6c757d', 'marginRight': '6px'}),
                                html.Span(f"TSS: {tss:.0f}", style={'fontSize': '0.65rem', 'color': '#6c757d'})
                            ])
                        ], style={
                            'padding': '3px 4px',
                            'marginBottom': '3px',
                            'borderLeft': f'3px solid {color}',
                            'background': '#f8f9fa',
                            'fontSize': '0.7rem'
                        })
                        
                        cell_content.append(activity_item)
                    
                    if len(day_workouts) > 3:
                        cell_content.append(
                            html.Div(
                                f"+{len(day_workouts)-3} mais",
                                style={
                                    'fontSize': '0.65rem',
                                    'color': '#6c757d',
                                    'marginTop': '2px',
                                    'fontStyle': 'italic'
                                }
                            )
                        )
                
                week_cells.append(html.Td(cell_content, style=cell_style))
        
        # Adicionar célula de resumo semanal
        summary_cell = html.Td([
            html.Div([
                html.Div(str(week_stats['workouts']), style={'fontSize': '1.5rem', 'fontWeight': '700', 'color': '#495057', 'marginBottom': '8px'}),
                html.Div([
                    html.Small("TSS: ", style={'color': '#6c757d', 'fontSize': '0.7rem'}),
                    html.Span(f"{week_stats['tss']:.0f}", style={'fontWeight': '600', 'fontSize': '0.8rem', 'color': '#495057'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Small("Dist: ", style={'color': '#6c757d', 'fontSize': '0.7rem'}),
                    html.Span(f"{week_stats['distance']:.1f}km", style={'fontWeight': '600', 'fontSize': '0.8rem', 'color': '#495057'})
                ], style={'marginBottom': '3px'}),
                html.Div([
                    html.Small("Tempo: ", style={'color': '#6c757d', 'fontSize': '0.7rem'}),
                    html.Span(format_hours_to_hms(week_stats['duration']), style={'fontWeight': '600', 'fontSize': '0.75rem', 'color': '#495057'})
                ])
            ])
        ], style={
            'height': '110px',
            'verticalAlign': 'top',
            'background': '#f8f9fa',
            'padding': '10px',
            'border': '1px solid #dee2e6',
            'textAlign': 'center'
        })
        
        week_cells.append(summary_cell)
        calendar_grid.append(html.Tr(week_cells))
    
    return dbc.Container([
        # Cabeçalho
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("📅 Calendário", className="text-primary mb-2", style={'fontWeight': '700'}),
                    html.P("Visualize suas atividades dia a dia", className="text-muted mb-4", style={'fontSize': '1.1rem'})
                ], className="text-center py-3")
            ])
        ], className="bg-light rounded-3 mb-4"),
        
        # Heatmap de TSS
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H3("🔥 Mapa de Calor - Intensidade dos Treinos", className="mb-3 text-danger", style={'fontWeight': '700'}),
                    html.P("Visualização de TSS diário dos últimos 90 dias", className="text-muted mb-3", style={'fontSize': '0.9rem'})
                ], className="text-center")
            ])
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(
                            figure=create_tss_heatmap(workouts),
                            config={'displayModeBar': False}
                        )
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ], className="mb-5"),
        
        # Título do mês
        dbc.Row([
            dbc.Col([
                html.H3(f"{month_name} {current_year}", className="text-center mb-4", style={'fontWeight': '600'})
            ])
        ]),
        
        # Resumo mensal
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📊 Resumo do Mês", className="card-title mb-3 text-center", style={'fontWeight': '600'}),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.Div("🏋️", style={'fontSize': '2rem'}),
                                    html.H4(f"{monthly_stats['total_workouts']}", className="text-primary mb-0"),
                                    html.Small("Treinos", className="text-muted")
                                ], className="text-center")
                            ], md=3),
                            dbc.Col([
                                html.Div([
                                    html.Div("🎯", style={'fontSize': '2rem'}),
                                    html.H4(f"{monthly_stats['total_tss']:.0f}", className="text-primary mb-0"),
                                    html.Small("TSS Total", className="text-muted")
                                ], className="text-center")
                            ], md=3),
                            dbc.Col([
                                html.Div([
                                    html.Div("📏", style={'fontSize': '2rem'}),
                                    html.H4(f"{monthly_stats['total_distance']:.1f} km", className="text-primary mb-0"),
                                    html.Small("Distância", className="text-muted")
                                ], className="text-center")
                            ], md=3),
                            dbc.Col([
                                html.Div([
                                    html.Div("⏱️", style={'fontSize': '2rem'}),
                                    html.H4(format_hours_to_hms(monthly_stats['total_duration']), className="text-primary mb-0"),
                                    html.Small("Tempo Total", className="text-muted")
                                ], className="text-center")
                            ], md=3)
                        ])
                    ])
                ], className="shadow-sm border-0 mb-4", style={'borderRadius': '12px'})
            ])
        ]),
        
        # Grade do calendário
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Table([
                        html.Thead([weekday_header]),
                        html.Tbody(calendar_grid)
                    ], className="table table-bordered mb-0", style={
                        'width': '100%',
                        'tableLayout': 'fixed'
                    })
                ], style={'overflowX': 'auto'})
            ])
        ], className="mb-4"),
        
        # Detalhes por modalidade
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📈 Estatísticas por Modalidade", className="card-title mb-3 text-center", style={'fontWeight': '600'}),
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6(f"{category_emoji.get(cat, '⚽')} {category_names.get(cat, cat.title())}", className="text-center mb-3", style={'fontWeight': '600'}),
                                        html.Hr(),
                                        html.Div([
                                            html.Small("Treinos: ", className="text-muted"),
                                            html.Strong(f"{stats['count']}")
                                        ], className="mb-2"),
                                        html.Div([
                                            html.Small("Distância: ", className="text-muted"),
                                            html.Strong(f"{stats['distance']:.1f} km")
                                        ], className="mb-2"),
                                        html.Div([
                                            html.Small("Tempo: ", className="text-muted"),
                                            html.Strong(format_hours_to_hms(stats['duration']))
                                        ], className="mb-2"),
                                        html.Div([
                                            html.Small("TSS: ", className="text-muted"),
                                            html.Strong(f"{stats['tss']:.0f}")
                                        ])
                                    ])
                                ], className="mb-3 shadow-sm", style={'borderRadius': '10px'})
                            ], md=4)
                            for cat, stats in sorted(monthly_stats['by_category'].items(), key=lambda x: x[1]['count'], reverse=True)
                        ])
                    ])
                ], className="shadow-sm border-0", style={'borderRadius': '12px'})
            ])
        ])
    ])

def render_goals():
    workouts = enrich_workouts_with_tss(load_workouts())
    config = load_config()
    goals_progress = calculate_goals_progress(workouts, config)
    
    # Calcular períodos para exibição
    now = datetime.now()
    days_since_monday = now.isoweekday() - 1  # 0=segunda, 6=domingo
    week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=6)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    week_period = f"{week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m')}"
    month_name = now.strftime('%B %Y')
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("🎯 Configuração de Metas", className="mb-4"),
                html.P("Defina suas metas de treinamento semanal, mensal e de performance.", className="text-muted mb-4"),
                html.Div([
                    html.P("💡 Dicas:", className="mb-2"),
                    html.Ul([
                        html.Li("Metas realistas: Comece com objetivos alcançáveis e aumente gradualmente"),
                        html.Li("Equilíbrio: Mantenha ATL abaixo de 80 para evitar overtraining"),
                        html.Li("Progressão: Acompanhe seu progresso e ajuste conforme necessário")
                    ])
                ], className="alert alert-info mb-4")
            ])
        ]),
        
        # Metas semanais
        dbc.Card([
            dbc.CardHeader("📅 Metas Semanais"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Distância (km)"),
                        dbc.Input(id="weekly-distance-goal", type="number", value=config.get("weekly_distance_goal", 50.0), min=0.0, max=500.0, step=5.0),
                        html.Small("Distância total semanal em quilômetros", className="text-muted")
                    ], md=3),
                    dbc.Col([
                        dbc.Label("TSS Total"),
                        dbc.Input(id="weekly-tss-goal", type="number", value=config.get("weekly_tss_goal", 300), min=0, max=2000),
                        html.Small("Training Stress Score semanal total", className="text-muted")
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Horas de Treino"),
                        dbc.Input(id="weekly-hours-goal", type="number", value=config.get("weekly_hours_goal", 7.0), min=0.0, max=50.0, step=0.5),
                        html.Small("Tempo total de treinamento semanal em horas", className="text-muted")
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Número de Atividades"),
                        dbc.Input(id="weekly-activities-goal", type="number", value=config.get("weekly_activities_goal", 5), min=0, max=20),
                        html.Small("Número de sessões de treino por semana", className="text-muted")
                    ], md=3)
                ])
            ])
        ], className="mb-4"),
        
        # Metas mensais
        dbc.Card([
            dbc.CardHeader("📊 Metas Mensais"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Distância (km)"),
                        dbc.Input(id="monthly-distance-goal", type="number", value=config.get("monthly_distance_goal", 200.0), min=0.0, max=2000.0, step=10.0),
                        html.Small("Distância total mensal em quilômetros", className="text-muted")
                    ], md=3),
                    dbc.Col([
                        dbc.Label("TSS Total"),
                        dbc.Input(id="monthly-tss-goal", type="number", value=config.get("monthly_tss_goal", 1200), min=0, max=8000),
                        html.Small("Training Stress Score mensal total", className="text-muted")
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Horas de Treino"),
                        dbc.Input(id="monthly-hours-goal", type="number", value=config.get("monthly_hours_goal", 30.0), min=0.0, max=200.0, step=1.0),
                        html.Small("Tempo total de treinamento mensal em horas", className="text-muted")
                    ], md=3),
                    dbc.Col([
                        dbc.Label("Número de Atividades"),
                        dbc.Input(id="monthly-activities-goal", type="number", value=config.get("monthly_activities_goal", 20), min=0, max=100),
                        html.Small("Número de sessões de treino por mês", className="text-muted")
                    ], md=3)
                ])
            ])
        ], className="mb-4"),
        
        # Metas de performance
        dbc.Card([
            dbc.CardHeader("🏆 Metas de Performance"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dbc.Label("CTL Alvo (Forma Física)"),
                        dbc.Input(id="target-ctl", type="number", value=config.get("target_ctl", 50), min=0, max=150),
                        html.Small("Nível de forma física desejado (Chronic Training Load)", className="text-muted")
                    ], md=6),
                    dbc.Col([
                        dbc.Label("ATL Máximo Permitido"),
                        dbc.Input(id="target-atl-max", type="number", value=config.get("target_atl_max", 80), min=0, max=200),
                        html.Small("Limite máximo de fadiga aguda para evitar overtraining", className="text-muted")
                    ], md=6)
                ])
            ])
        ], className="mb-4"),
        
        # Botão salvar
        dbc.Row([
            dbc.Col([
                dbc.Button("💾 Salvar Metas", id="save-goals-btn", color="success", size="lg", className="w-100")
            ], md=6, className="mx-auto")
        ], className="mb-4"),
        
        # Progresso atual
        dbc.Card([
            dbc.CardHeader("📈 Progresso Atual"),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        html.H5(f"Semanal ({week_period})", className="text-center mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("🏃 Distância"),
                                    html.P(f"{goals_progress['weekly']['distance']:.1f}km / {config.get('weekly_distance_goal', 50.0):.0f}km"),
                                    dbc.Progress(value=min(100, (goals_progress['weekly']['distance'] / config.get('weekly_distance_goal', 50.0) * 100) if config.get('weekly_distance_goal', 50.0) > 0 else 0), color="success" if goals_progress['weekly']['distance'] >= config.get('weekly_distance_goal', 50.0) else "primary")
                                ], className="mb-3")
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("🎯 TSS"),
                                    html.P(f"{goals_progress['weekly']['tss']:.0f} / {config.get('weekly_tss_goal', 300)}"),
                                    dbc.Progress(value=min(100, (goals_progress['weekly']['tss'] / config.get('weekly_tss_goal', 300) * 100) if config.get('weekly_tss_goal', 300) > 0 else 0), color="success" if goals_progress['weekly']['tss'] >= config.get('weekly_tss_goal', 300) else "primary")
                                ], className="mb-3")
                            ], md=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("⏱️ Horas"),
                                    html.P(f"{format_hours_to_hms(goals_progress['weekly']['hours'])} / {format_hours_to_hms(config.get('weekly_hours_goal', 7.0))}"),
                                    dbc.Progress(value=min(100, (goals_progress['weekly']['hours'] / config.get('weekly_hours_goal', 7.0) * 100) if config.get('weekly_hours_goal', 7.0) > 0 else 0), color="success" if goals_progress['weekly']['hours'] >= config.get('weekly_hours_goal', 7.0) else "primary")
                                ], className="mb-3")
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("📊 Atividades"),
                                    html.P(f"{goals_progress['weekly']['activities']} / {config.get('weekly_activities_goal', 5)}"),
                                    dbc.Progress(value=min(100, (goals_progress['weekly']['activities'] / config.get('weekly_activities_goal', 5) * 100) if config.get('weekly_activities_goal', 5) > 0 else 0), color="success" if goals_progress['weekly']['activities'] >= config.get('weekly_activities_goal', 5) else "primary")
                                ])
                            ], md=6)
                        ])
                    ], md=6),
                    dbc.Col([
                        html.H5(f"Mensal ({month_name})", className="text-center mb-3"),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("🏃 Distância"),
                                    html.P(f"{goals_progress['monthly']['distance']:.1f}km / {config.get('monthly_distance_goal', 200.0):.0f}km"),
                                    dbc.Progress(value=min(100, (goals_progress['monthly']['distance'] / config.get('monthly_distance_goal', 200.0) * 100) if config.get('monthly_distance_goal', 200.0) > 0 else 0), color="success" if goals_progress['monthly']['distance'] >= config.get('monthly_distance_goal', 200.0) else "primary")
                                ], className="mb-3")
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("🎯 TSS"),
                                    html.P(f"{goals_progress['monthly']['tss']:.0f} / {config.get('monthly_tss_goal', 1200)}"),
                                    dbc.Progress(value=min(100, (goals_progress['monthly']['tss'] / config.get('monthly_tss_goal', 1200) * 100) if config.get('monthly_tss_goal', 1200) > 0 else 0), color="success" if goals_progress['monthly']['tss'] >= config.get('monthly_tss_goal', 1200) else "primary")
                                ], className="mb-3")
                            ], md=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("⏱️ Horas"),
                                    html.P(f"{format_hours_to_hms(goals_progress['monthly']['hours'])} / {format_hours_to_hms(config.get('monthly_hours_goal', 30.0))}"),
                                    dbc.Progress(value=min(100, (goals_progress['monthly']['hours'] / config.get('monthly_hours_goal', 30.0) * 100) if config.get('monthly_hours_goal', 30.0) > 0 else 0), color="success" if goals_progress['monthly']['hours'] >= config.get('monthly_hours_goal', 30.0) else "primary")
                                ], className="mb-3")
                            ], md=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("📊 Atividades"),
                                    html.P(f"{goals_progress['monthly']['activities']} / {config.get('monthly_activities_goal', 20)}"),
                                    dbc.Progress(value=min(100, (goals_progress['monthly']['activities'] / config.get('monthly_activities_goal', 20) * 100) if config.get('monthly_activities_goal', 20) > 0 else 0), color="success" if goals_progress['monthly']['activities'] >= config.get('monthly_activities_goal', 20) else "primary")
                                ])
                            ], md=6)
                        ])
                    ], md=6)
                ])
            ])
        ])
    ])

def render_config():
    config = load_config()
    credentials = load_credentials()
    tokens_valid = validate_garmin_tokens_locally()
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("⚙️ Configuração", className="mb-4"),
                
                # Credenciais Garmin
                dbc.Card([
                    dbc.CardHeader("🔐 Credenciais Garmin Connect"),
                    dbc.CardBody([
                        html.P("Seus dados de login são armazenados de forma segura apenas neste dispositivo.", className="text-muted mb-3"),
                        
                        html.Div([
                            dbc.Alert(
                                "✅ Tokens do Garmin válidos! Você pode fazer login sem inserir email/senha.",
                                color="success",
                                className="mb-3"
                            ) if tokens_valid else None
                        ], id="tokens-status"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Email"),
                                dbc.Input(id="garmin-email", type="email", value=credentials.get("email", ""), placeholder="seu@email.com")
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Senha"),
                                dbc.Input(id="garmin-password", type="password", value=credentials.get("password", ""), placeholder="••••••••")
                            ], md=6)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button("💾 Salvar Credenciais", id="save-credentials-btn", color="primary", className="mt-3")
                            ], md=6),
                            dbc.Col([
                                dbc.Button("🔄 Atualizar Tokens", id="refresh-tokens-btn", color="info", className="mt-3")
                            ], md=6)
                        ]),
                        html.Div(id="credentials-status", className="mt-3")
                    ])
                ], className="mb-4"),
                
                # Configurações de Fitness
                dbc.Card([
                    dbc.CardHeader("🏃 Parâmetros de Fitness"),
                    dbc.CardBody([
                        html.P("💡 Sobre o hrTSS: O cálculo do hrTSS usa o LTHR (Limiar de Frequência Cardíaca) como referência, seguindo a fórmula do TrainingPeaks. Configure corretamente seu LTHR para obter valores precisos.", className="text-muted mb-3"),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Idade"),
                                dbc.Input(id="config-age", type="number", value=config.get("age", 29), min=15, max=100)
                            ], md=3),
                            dbc.Col([
                                dbc.Label("FTP (watts)"),
                                dbc.Input(id="config-ftp", type="number", value=config.get("ftp", 250), min=50, max=500, step=5)
                            ], md=3),
                            dbc.Col([
                                dbc.Label("FC Máx (bpm)"),
                                dbc.Input(id="config-hr-max", type="number", value=config.get("hr_max", 191), min=150, max=220)
                            ], md=3),
                            dbc.Col([
                                dbc.Label("FC Repouso (bpm)"),
                                dbc.Input(id="config-hr-rest", type="number", value=config.get("hr_rest", 50), min=40, max=100)
                            ], md=3)
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("LTHR - FC Limiar (bpm)"),
                                dbc.Input(id="config-hr-threshold", type="number", value=config.get("hr_threshold", 162), min=100, max=200),
                                html.Small("Usado para calcular hrTSS (TrainingPeaks)", className="text-muted")
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Pace Threshold - Corrida (mm:ss)"),
                                dbc.Input(id="config-pace-threshold", type="text", value=config.get("pace_threshold", "4:22"))
                            ], md=4),
                            dbc.Col([
                                dbc.Label("Swim Pace Threshold - Natação (mm:ss)"),
                                dbc.Input(id="config-swim-pace-threshold", type="text", value=config.get("swim_pace_threshold", "2:01"))
                            ], md=4)
                        ], className="mt-3"),
                        dbc.Button("💾 Salvar Configurações", id="save-config-btn", color="success", className="mt-3")
                    ])
                ], className="mb-4"),
                
                # Atualização de Dados
                dbc.Card([
                    dbc.CardHeader("🔄 Atualizar Dados do Garmin Connect"),
                    dbc.CardBody([
                        html.P("Clique no botão abaixo para sincronizar seus dados com Garmin Connect. Este processo busca todas as atividades dos últimos 42 dias e recalcula as métricas de fitness (CTL, ATL, TSB).", className="mb-3"),
                        dbc.Button("📊 Atualizar Dados", id="update-data-btn", color="info", size="lg", className="me-2"),
                        dbc.Button("🧹 Reiniciar Dados", id="reset-data-btn", color="danger"),
                        html.Div(id="update-status", className="mt-3")
                    ])
                ])
            ])
        ]),
        
        # Status de salvamento
        dbc.Row([
            dbc.Col([
                html.Div(id="config-status", className="mt-3")
            ])
        ])
    ])

def render_ai_chat():
    """Renderiza a interface de chat com IA"""
    try:
        # Inicializar AI se possível
        ai = FitnessAI()
        
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("🤖 Assistente de Fitness IA", className="mb-4"),
                    html.P("Converse com nossa IA especializada em treinamento físico. Faça perguntas sobre suas métricas, treinos, progresso e receba insights personalizados!", className="text-muted mb-4"),
                    
                    # Área de chat
                    dbc.Card([
                        dbc.CardHeader("💬 Conversa com a IA"),
                        dbc.CardBody([
                            # Histórico de mensagens
                            html.Div(id="chat-history", style={
                                'height': '400px',
                                'overflowY': 'auto',
                                'border': '1px solid #dee2e6',
                                'borderRadius': '8px',
                                'padding': '15px',
                                'marginBottom': '15px',
                                'backgroundColor': '#f8f9fa'
                            }, children=[
                                html.Div("🤖 Olá! Sou seu assistente de fitness. Faça uma pergunta sobre seus treinos, métricas ou progresso!", 
                                        style={'fontStyle': 'italic', 'color': '#6c757d', 'marginBottom': '10px'})
                            ]),
                            
                            # Input de mensagem
                            dbc.Row([
                                dbc.Col([
                                    dbc.Input(id="chat-input", type="text", 
                                             placeholder="Digite sua pergunta sobre fitness...",
                                             style={'borderRadius': '20px'})
                                ], md=10),
                                dbc.Col([
                                    dbc.Button("📤 Enviar", id="send-chat-btn", color="primary", 
                                             style={'borderRadius': '20px'})
                                ], md=2)
                            ])
                        ])
                    ]),
                    
                    # Sugestões de perguntas
                    dbc.Card([
                        dbc.CardHeader("💡 Sugestões de Perguntas"),
                        dbc.CardBody([
                            html.P("Clique em uma sugestão para começar:", className="mb-3"),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Como está meu equilíbrio entre modalidades?", 
                                             id="suggestion-1", color="outline-primary", size="sm", className="me-2 mb-2"),
                                    dbc.Button("Preciso ajustar minha periodização?", 
                                             id="suggestion-2", color="outline-primary", size="sm", className="me-2 mb-2"),
                                    dbc.Button("Preparação para prova de triathlon", 
                                             id="suggestion-3", color="outline-primary", size="sm", className="me-2 mb-2")
                                ]),
                                dbc.Col([
                                    dbc.Button("Qual modalidade precisa de mais foco?", 
                                             id="suggestion-4", color="outline-primary", size="sm", className="me-2 mb-2"),
                                    dbc.Button("Otimizar treinamento de transição", 
                                             id="suggestion-5", color="outline-primary", size="sm", className="me-2 mb-2"),
                                    dbc.Button("Análise de distribuição de volume", 
                                             id="suggestion-6", color="outline-primary", size="sm", className="me-2 mb-2")
                                ])
                            ])
                        ])
                    ], className="mt-4")
                ])
            ])
        ])
    except Exception as e:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2("🤖 Assistente de Fitness IA", className="mb-4"),
                    dbc.Alert([
                        html.H4("⚠️ Configuração Necessária", className="alert-heading"),
                        html.P("Para usar o assistente de IA, você precisa configurar sua chave da API Groq:"),
                        html.Ol([
                            html.Li("Acesse https://console.groq.com/"),
                            html.Li("Crie uma conta gratuita"),
                            html.Li("Gere uma chave API"),
                            html.Li("Crie um arquivo .env na pasta do projeto"),
                            html.Li("Adicione: GROQ_API_KEY=sua_chave_aqui")
                        ]),
                        html.P("Após configurar, reinicie o aplicativo.", className="mb-0")
                    ], color="warning")
                ])
            ])
        ])

# Funções auxiliares
def calculate_goals_progress(activities, config):
    """Calcula progresso das metas baseado nas atividades"""
    if not activities:
        return {
            'weekly': {'distance': 0, 'tss': 0, 'hours': 0, 'activities': 0},
            'monthly': {'distance': 0, 'tss': 0, 'hours': 0, 'activities': 0},
            'current_ctl': 0,
            'current_atl': 0
        }

    now = datetime.now()
    # Semana atual: segunda-feira da semana atual até domingo da semana atual
    days_since_monday = now.isoweekday() - 1  # 0=segunda, 6=domingo
    week_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    weekly_activities = []
    monthly_activities = []

    for activity in activities:
        try:
            start_time_raw = activity.get('startTimeLocal', activity.get('startTime', '1900-01-01'))
            activity_date = datetime.strptime(start_time_raw, "%Y-%m-%d %H:%M:%S")

            if week_start <= activity_date <= week_end:
                weekly_activities.append(activity)
            elif activity_date >= month_start:
                monthly_activities.append(activity)
        except Exception as e:
            continue

    def calculate_metrics(activity_list):
        total_distance = sum(float(a.get('distance', 0) or 0) / 1000 for a in activity_list)
        total_tss = sum(float(a.get('tss', 0) or 0) for a in activity_list)
        total_hours = sum(float(a.get('duration', 0) or 0) / 3600 for a in activity_list)
        total_activities = len(activity_list)
        return {
            'distance': total_distance,
            'tss': total_tss,
            'hours': total_hours,
            'activities': total_activities
        }

    weekly_metrics = calculate_metrics(weekly_activities)
    monthly_metrics = calculate_metrics(monthly_activities)

    metrics = load_metrics()
    current_ctl = metrics[-1]['ctl'] if metrics else 0
    current_atl = metrics[-1]['atl'] if metrics else 0

    return {
        'weekly': weekly_metrics,
        'monthly': monthly_metrics,
        'current_ctl': current_ctl,
        'current_atl': current_atl
    }

def fetch_garmin_data(email=None, password=None, config=None, use_tokens=True):
    """Busca dados do Garmin Connect com lógica inteligente de atualização
    
    Parâmetros:
    - email: email do Garmin (opcional se usar tokens)
    - password: senha do Garmin (opcional se usar tokens)
    - config: configurações de fitness
    - use_tokens: tentar usar tokens salvos primeiro (padrão: True)
    """
    try:
        from garminconnect import Garmin
        
        client = None
        
        # Tentar login com tokens se disponível
        if use_tokens:
            # Primeiro validar tokens localmente (sem conectar ao servidor)
            if validate_garmin_tokens_locally():
                try:
                    client = Garmin()
                    client.garth.load(str(token_dir))
                    print("✅ Login com tokens bem-sucedido")
                except Exception as e:
                    print(f"⚠️ Login com tokens falhou: {e}")
                    client = None
            else:
                print("⚠️ Tokens não encontrados ou inválidos localmente")
        
        # Se falhar com tokens ou não disponível, tentar com email/password
        if client is None:
            if not email or not password:
                return False, "❌ Email e senha necessários ou tokens não disponíveis"
            
            client = Garmin(email, password)
            client.login()
            print("✅ Login com email/senha bem-sucedido")
            
            # Salvar os novos tokens após login bem-sucedido
            save_garmin_tokens(client)

        end_date = datetime.now().date()

        # Carregar histórico salvo
        old_activities = load_workouts()

        if not old_activities:
            # Se não há dados armazenados, buscar os últimos 42 dias
            start_date = end_date - timedelta(days=42)
            fetch_start_date = start_date
        else:
            # Se há dados, pegar o último dia mais atualizado, subtrair 1 dia e buscar até hoje
            # Encontrar a data mais recente dos dados armazenados
            latest_dates = []
            for a in old_activities:
                start_time = a.get('startTimeLocal', a.get('startTime', ''))
                if start_time:
                    try:
                        if 'T' in start_time:
                            date_obj = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                        else:
                            date_obj = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()
                        latest_dates.append(date_obj)
                    except:
                        continue

            if latest_dates:
                most_recent_date = max(latest_dates)
                # Subtrair 1 dia da data mais recente
                fetch_start_date = most_recent_date - timedelta(days=1)
            else:
                # Fallback para 42 dias se não conseguir parsear datas
                fetch_start_date = end_date - timedelta(days=42)

        # Buscar atividades do período determinado
        if fetch_start_date <= end_date:
            new_activities = client.get_activities_by_date(
                fetch_start_date.isoformat(),
                end_date.isoformat()
            )
        else:
            new_activities = []

        # Unir atividades antigas com novas, sobrescrevendo duplicatas
        # Usar activityId ou startTimeLocal como chave única
        activities_dict = {}

        # Primeiro, adicionar atividades antigas
        for a in old_activities:
            key = a.get('activityId') or a.get('activityUUID') or a.get('startTimeLocal') or a.get('startTime')
            if key:
                activities_dict[key] = a

        # Depois, adicionar/sobrescrever com atividades novas
        for a in new_activities:
            key = a.get('activityId') or a.get('activityUUID') or a.get('startTimeLocal') or a.get('startTime')
            if key:
                activities_dict[key] = a

        # Converter de volta para lista
        all_activities = list(activities_dict.values())

        # Salvar as atividades brutas do Garmin (TSS é calculado dinamicamente nas views)
        save_workouts(all_activities)

        # Para métricas do Dashboard, usar apenas os últimos 42 dias
        dashboard_cutoff = end_date - timedelta(days=42)
        dashboard_activities = []
        for a in all_activities:
            start_time = a.get('startTimeLocal', a.get('startTime', ''))
            if start_time:
                try:
                    if 'T' in start_time:
                        activity_date = datetime.strptime(start_time.split('T')[0], '%Y-%m-%d').date()
                    else:
                        activity_date = datetime.strptime(start_time.split(' ')[0], '%Y-%m-%d').date()

                    if activity_date >= dashboard_cutoff:
                        dashboard_activities.append(a)
                except:
                    # Se não conseguir parsear, incluir na dúvida
                    dashboard_activities.append(a)

        dashboard_with_tss = []
        
        for a in dashboard_activities:
            a_copy = dict(a)
            tss_data = compute_tss_variants(a_copy, config)
            a_copy['tss'] = tss_data.get('tss', 0.0)
            
            dashboard_with_tss.append(a_copy)

        # Calcular métricas apenas com dados dos últimos 42 dias
        metrics = calculate_fitness_metrics(dashboard_with_tss, config, dashboard_cutoff, end_date)
        save_metrics(metrics)

        new_count = len(new_activities)
        total_count = len(all_activities)
        dashboard_count = len(dashboard_activities)

        return True, f"✅ Dados atualizados! {new_count} novas atividades, {total_count} total armazenadas, {dashboard_count} para Dashboard (42 dias)."

    except ImportError:
        return False, "❌ Erro: garminconnect não instalado. Instale com: pip install garminconnect"
    except Exception as e:
        return False, f"❌ Erro ao buscar dados: {str(e)}"

def compute_tss_variants(activity: dict, config: dict) -> dict:
    """Calcula TSS usando a função correta do calculations.py
    
    Delega para calculations.compute_tss_variants que implementa:
    - TSS (power-based) para ciclismo
    - rTSS (pace-based) para corrida
    - hrTSS (heart rate-based) para natação e força
    """
    from calculations import compute_tss_variants as calc_tss
    
    # Chamar função correta do calculations.py passando activity e config
    result = calc_tss(activity, config)
    
    # A função do calculations.py retorna: {'tss': float, 'tss_type': str, 'category': str, 'breakdown': dict}
    # Manter compatibilidade retornando tss e category
    return {
        'tss': result.get('tss', 0.0),
        'category': result.get('category', _activity_category(activity))
    }

def calculate_fitness_metrics(activities, config, start_date, end_date):
    """Calcula métricas de fitness (CTL, ATL, TSB) baseadas em TSS diário.

    Isso garante que Dashboard e Calendário usem a mesma base (TSS dinâmico)
    e evita depender de arquivos com métricas antigas.
    """
    # Agrupar TSS por data
    daily_loads = {}
    for activity in activities:
        start_time = activity.get('startTimeLocal') or activity.get('startTime') or ''
        if not start_time:
            continue

        try:
            # startTimeLocal pode ser "YYYY-MM-DD HH:MM:SS" ou ISO
            if 'T' not in start_time:
                start_time = start_time.replace(' ', 'T')
            if not start_time.endswith('Z') and '+' not in start_time:
                start_time += 'Z'
            date = datetime.fromisoformat(start_time.replace('Z', '+00:00')).date()
        except Exception:
            continue

        # Usar TSS (se já estiver enriquecido); se não, calcular agora.
        try:
            tss_val = float(activity.get('tss') or 0)
        except Exception:
            tss_val = 0.0

        if tss_val <= 0:
            try:
                tss_val = float(compute_tss_variants(dict(activity), config).get('tss', 0.0) or 0.0)
            except Exception:
                tss_val = 0.0

        daily_loads[date] = daily_loads.get(date, 0.0) + tss_val
    
    # Lista de dias
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += timedelta(days=1)
    
    # Calcular métricas cumulativas
    metrics = []
    ctl = 0.0
    atl = 0.0
    
    for day in days:
        daily_tss = daily_loads.get(day, 0.0)
        
        # CTL (Chronic Training Load) - tempo de meia-vida de 42 dias
        ctl = ctl + (daily_tss - ctl) / 42.0
        
        # ATL (Acute Training Load) - tempo de meia-vida de 7 dias
        atl = atl + (daily_tss - atl) / 7.0
        
        # TSB (Training Stress Balance) = CTL - ATL
        tsb = ctl - atl
        
        metrics.append({
            'date': day.isoformat(),
            'ctl': round(ctl, 1),
            'atl': round(atl, 1),
            'tsb': round(tsb, 1),
            'daily_load': round(daily_tss, 1)
        })
    
    return metrics

def create_modality_subplot_chart(data, modality_info, modality_key):
    """Cria gráfico com subplots 2x2 para evolução semanal da modalidade"""
    
    # Preparar dados
    semanas = [f'S{i+1}' for i in range(len(data))]
    distancia = [week['distance'] for week in data]
    tss = [week['tss'] for week in data]
    horas = [week['duration'] for week in data]
    atividades = [week['activities'] for week in data]
    
    # Cores temáticas por modalidade
    cores_modalidade = {
        'swimming': {'primary': '#007bff', 'secondary': '#cce5ff'},  # Azul - Natação
        'cycling': {'primary': '#28a745', 'secondary': '#d4edda'},   # Verde - Ciclismo
        'running': {'primary': '#fd7e14', 'secondary': '#ffe5d0'},   # Laranja - Corrida
        'strength': {'primary': '#6f42c1', 'secondary': '#e7d9ff'}   # Roxo - Musculação
    }
    
    cores = cores_modalidade.get(modality_key, {'primary': '#666', 'secondary': '#ccc'})
    
    # Criar subplot com 2x2
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distância por Semana', 'TSS por Semana', 'Horas por Semana', 'Atividades por Semana'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Gráfico 1: Distância
    fig.add_trace(
        go.Bar(
            x=semanas,
            y=distancia,
            name='Distância',
            marker_color=cores['primary'],
            marker_line_color=cores['secondary'],
            marker_line_width=1,
            hovertemplate='<b>%{x}</b><br>Distância: %{y:.1f} km<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Gráfico 2: TSS
    fig.add_trace(
        go.Scatter(
            x=semanas,
            y=tss,
            mode='lines+markers',
            name='TSS',
            line=dict(color=cores['primary'], width=3),
            marker=dict(size=8, color=cores['primary'], symbol='circle'),
            hovertemplate='<b>%{x}</b><br>TSS: %{y:.0f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Gráfico 3: Horas
    fig.add_trace(
        go.Scatter(
            x=semanas,
            y=horas,
            mode='lines+markers',
            name='Horas',
            line=dict(color=cores['primary'], width=3, dash='dot'),
            marker=dict(size=8, color=cores['primary'], symbol='square'),
            hovertemplate='<b>%{x}</b><br>Horas: %{customdata}<extra></extra>',
            customdata=[format_hours_decimal(h) for h in horas]
        ),
        row=2, col=1
    )
    
    # Gráfico 4: Atividades
    fig.add_trace(
        go.Bar(
            x=semanas,
            y=atividades,
            name='Atividades',
            marker_color=cores['secondary'],
            marker_line_color=cores['primary'],
            marker_line_width=1,
            hovertemplate='<b>%{x}</b><br>Atividades: %{y}<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Configurar layout
    fig.update_layout(
        height=600,
        showlegend=False,
        font=dict(family='Inter, -apple-system, sans-serif', size=11),
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    # Configurar eixos
    fig.update_xaxes(showgrid=False, row=1, col=1)
    fig.update_yaxes(title_text='Distância (km)', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=1)
    
    fig.update_xaxes(showgrid=False, row=1, col=2)
    fig.update_yaxes(title_text='TSS', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=1, col=2)
    
    fig.update_xaxes(showgrid=False, row=2, col=1)
    fig.update_yaxes(title_text='Horas', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=2, col=1)
    
    fig.update_xaxes(showgrid=False, row=2, col=2)
    fig.update_yaxes(title_text='Atividades', showgrid=True, gridcolor='rgba(0,0,0,0.1)', row=2, col=2)
    
    return fig

def create_modality_trend_chart(data, modality_info, modality_name):
    """Cria gráfico de tendência consolidada com eixo duplo"""
    
    # Preparar dados
    semanas = [f'S{i+1}' for i in range(len(data))]
    distancia = [week['distance'] for week in data]
    tss = [week['tss'] for week in data]
    
    # Cores temáticas por modalidade
    cores_modalidade = {
        'swimming': {'primary': '#007bff', 'secondary': '#cce5ff'},  # Azul - Natação
        'cycling': {'primary': '#28a745', 'secondary': '#d4edda'},   # Verde - Ciclismo
        'running': {'primary': '#fd7e14', 'secondary': '#ffe5d0'},   # Laranja - Corrida
        'strength': {'primary': '#6f42c1', 'secondary': '#e7d9ff'}   # Roxo - Musculação
    }
    
    modality_key = modality_info.get('key', 'unknown')
    cores = cores_modalidade.get(modality_key, {'primary': '#666', 'secondary': '#ccc'})
    
    # Gráfico de tendência
    fig = go.Figure()
    
    # Área preenchida para distância
    fig.add_trace(
        go.Scatter(
            x=semanas,
            y=distancia,
            mode='lines+markers',
            name='Distância (km)',
            line=dict(color=cores['primary'], width=3),
            marker=dict(size=6, color=cores['primary']),
            fill='tozeroy',
            fillcolor='rgba(25, 118, 210, 0.2)',  # Azul com transparência
            hovertemplate='<b>Distância</b><br>Semana %{x}<br>%{y:.1f} km<extra></extra>'
        )
    )
    
    # Linha para TSS
    fig.add_trace(
        go.Scatter(
            x=semanas,
            y=tss,
            mode='lines+markers',
            name='TSS',
            line=dict(color=cores['secondary'], width=3, dash='dash'),
            marker=dict(size=6, color=cores['secondary'], symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>TSS</b><br>Semana %{x}<br>%{y:.0f}<extra></extra>'
        )
    )
    
    # Configurar layout com eixo duplo
    fig.update_layout(
        title=f'Tendência de Progresso - {modality_name}',
        height=400,
        font=dict(family='Inter, -apple-system, sans-serif', size=12),
        plot_bgcolor='rgba(248,249,250,0.5)',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(l=50, r=50, t=80, b=50),
        yaxis=dict(
            title='Distância (km)',
            tickfont=dict(color=cores['primary'])
        ),
        yaxis2=dict(
            title='TSS',
            tickfont=dict(color=cores['secondary']),
            anchor='x',
            overlaying='y',
            side='right'
        )
    )
    
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)')
    
    return fig

# Callback para modo escuro com persistência
@app.callback(
    [Output('dark-mode-store', 'data'),
     Output('dark-mode-toggle', 'children'),
     Output('app-container', 'style')],
    Input('dark-mode-toggle', 'n_clicks'),
    State('dark-mode-store', 'data'),
    prevent_initial_call=True
)
def toggle_dark_mode(n_clicks, current_mode):
    """Alterna entre modo claro e escuro"""
    new_mode = not current_mode
    button_text = '☀️ Modo Claro' if new_mode else '🌙 Modo Escuro'
    
    if new_mode:
        container_style = {
            'backgroundColor': '#242428',
            'color': '#FFFFFF',
            'minHeight': '100vh',
            'transition': 'all 0.3s ease'
        }
    else:
        container_style = {
            'backgroundColor': 'white',
            'color': '#212529',
            'minHeight': '100vh',
            'transition': 'all 0.3s ease'
        }
    
    return new_mode, button_text, container_style

# Callback para atualizar badge de última atualização
@app.callback(
    Output('last-update-badge', 'children'),
    Input('tabs', 'active_tab')
)
def update_last_sync_badge(active_tab):
    """Atualiza o badge mostrando quando foi a última sincronização"""
    try:
        if METRICS_FILE.exists():
            modified_time = datetime.fromtimestamp(METRICS_FILE.stat().st_mtime)
            time_diff = datetime.now() - modified_time
            
            if time_diff.total_seconds() < 60:
                time_str = "agora há pouco"
            elif time_diff.total_seconds() < 3600:
                mins = int(time_diff.total_seconds() / 60)
                time_str = f"há {mins} min"
            elif time_diff.total_seconds() < 86400:
                hours = int(time_diff.total_seconds() / 3600)
                time_str = f"há {hours}h"
            else:
                days = int(time_diff.total_seconds() / 86400)
                time_str = f"há {days} dia(s)"
            
            return f"🔄 Última atualização: {time_str}"
        else:
            return "🔄 Nenhuma sincronização ainda"
    except Exception as e:
        return "🔄 Status desconhecido"

# Callbacks para o chat de IA
@app.callback(
    [Output("chat-history", "children"),
     Output("chat-input", "value")],
    [Input("send-chat-btn", "n_clicks"),
     Input("suggestion-1", "n_clicks"),
     Input("suggestion-2", "n_clicks"),
     Input("suggestion-3", "n_clicks"),
     Input("suggestion-4", "n_clicks"),
     Input("suggestion-5", "n_clicks"),
     Input("suggestion-6", "n_clicks")],
    [State("chat-input", "value"),
     State("chat-history", "children")],
    prevent_initial_call=True
)
def handle_chat_message(send_clicks, s1, s2, s3, s4, s5, s6, input_value, current_history):
    """Processa mensagens do chat de IA"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return current_history, input_value
    
    # Determinar qual botão foi clicado
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Definir mensagem baseada no botão clicado
    if triggered_id == "send-chat-btn" and input_value:
        user_message = input_value
    elif triggered_id == "suggestion-1":
        user_message = "Como está meu equilíbrio entre as três modalidades?"
    elif triggered_id == "suggestion-2":
        user_message = "Preciso ajustar minha periodização de treinamento?"
    elif triggered_id == "suggestion-3":
        user_message = "Como está minha preparação para uma prova de triathlon?"
    elif triggered_id == "suggestion-4":
        user_message = "Qual modalidade precisa de mais foco?"
    elif triggered_id == "suggestion-5":
        user_message = "Como otimizar meu treinamento de transição?"
    elif triggered_id == "suggestion-6":
        user_message = "Análise da distribuição de volume por modalidade"
    else:
        return current_history, ""
    
    try:
        # Inicializar AI
        ai = FitnessAI()
        
        # Carregar dados
        metrics = load_metrics()
        workouts = enrich_workouts_with_tss(load_workouts())
        config = load_config()
        
        # Gerar resposta da IA
        response = ai.answer_question(user_message, metrics, workouts, config)
        
        # Adicionar mensagens ao histórico
        new_history = list(current_history) if current_history else []
        
        # Adicionar mensagem do usuário
        new_history.append(
            html.Div([
                html.Strong("👤 Você: ", style={'color': '#007bff'}),
                user_message
            ], style={'marginBottom': '10px', 'padding': '8px', 'backgroundColor': '#e3f2fd', 'borderRadius': '8px'})
        )
        
        # Adicionar resposta da IA
        new_history.append(
            html.Div([
                html.Strong("🤖 IA: ", style={'color': '#28a745'}),
                html.Div(response, style={'whiteSpace': 'pre-wrap', 'marginTop': '5px'})
            ], style={'marginBottom': '15px', 'padding': '8px', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'borderLeft': '4px solid #28a745'})
        )
        
        return new_history, ""
        
    except Exception as e:
        # Em caso de erro, mostrar mensagem de erro
        error_history = list(current_history) if current_history else []
        error_history.append(
            html.Div([
                html.Strong("❌ Erro: ", style={'color': '#dc3545'}),
                f"Não foi possível processar sua pergunta. Erro: {str(e)}"
            ], style={'marginBottom': '10px', 'padding': '8px', 'backgroundColor': '#f8d7da', 'borderRadius': '8px'})
        )
        return error_history, input_value

# Callbacks para configurações
@app.callback(
    Output("credentials-status", "children"),
    Input("save-credentials-btn", "n_clicks"),
    State("garmin-email", "value"),
    State("garmin-password", "value"),
    prevent_initial_call=True
)
def save_credentials_callback(n_clicks, email, password):
    """Salva credenciais do Garmin"""
    if n_clicks:
        try:
            if not email or not password:
                return html.Div("❌ Preencha email e senha.", className="alert alert-warning mt-3")
            
            save_credentials(email, password)
            return html.Div("✅ Credenciais salvas com sucesso!", className="alert alert-success mt-3")
        except Exception as e:
            return html.Div(f"❌ Erro ao salvar credenciais: {str(e)}", className="alert alert-danger mt-3")
    return html.Div()

@app.callback(
    Output("credentials-status", "children", allow_duplicate=True),
    Input("refresh-tokens-btn", "n_clicks"),
    prevent_initial_call=True
)
def refresh_tokens_callback(n_clicks):
    """Atualiza tokens do Garmin usando credenciais salvas"""
    if n_clicks:
        try:
            credentials = load_credentials()
            email = credentials.get("email")
            password = credentials.get("password")
            
            if not email or not password:
                return html.Div("❌ Configure email e senha primeiro.", className="alert alert-warning mt-3")
            
            from garminconnect import Garmin
            client = Garmin(email, password)
            client.login()
            save_garmin_tokens(client)
            
            return html.Div("✅ Tokens atualizados com sucesso!", className="alert alert-success mt-3")
        except Exception as e:
            return html.Div(f"❌ Erro ao atualizar tokens: {str(e)}", className="alert alert-danger mt-3")
    return html.Div()


@app.callback(
    Output("config-status", "children"),
    Input("save-config-btn", "n_clicks"),
    State("config-age", "value"),
    State("config-ftp", "value"),
    State("config-hr-max", "value"),
    State("config-hr-rest", "value"),
    State("config-hr-threshold", "value"),
    State("config-pace-threshold", "value"),
    State("config-swim-pace-threshold", "value"),
    prevent_initial_call=True
)
def save_config_callback(n_clicks, age, ftp, hr_max, hr_rest, hr_threshold, pace_threshold, swim_pace_threshold):
    """Salva configurações de fitness"""
    if n_clicks:
        try:
            config = {
                "age": int(age) if age else 29,
                "ftp": int(ftp) if ftp else 250,
                "hr_max": int(hr_max) if hr_max else 191,
                "hr_rest": int(hr_rest) if hr_rest else 50,
                "hr_threshold": int(hr_threshold) if hr_threshold else 162,
                "pace_threshold": pace_threshold or "4:22",
                "swim_pace_threshold": swim_pace_threshold or "2:01",
                "weekly_distance_goal": 50.0,
                "weekly_tss_goal": 300,
                "weekly_hours_goal": 7.0,
                "weekly_activities_goal": 5,
                "monthly_distance_goal": 200.0,
                "monthly_tss_goal": 1200,
                "monthly_hours_goal": 30.0,
                "monthly_activities_goal": 20,
                "target_ctl": 50,
                "target_atl_max": 80,
            }
            
            save_config(config)
            return html.Div("✅ Configurações salvas com sucesso!", className="alert alert-success mt-3")
        except Exception as e:
            return html.Div(f"❌ Erro ao salvar configurações: {str(e)}", className="alert alert-danger mt-3")
    return html.Div()

@app.callback(
    Output("update-status", "children"),
    Input("update-data-btn", "n_clicks"),
    Input("reset-data-btn", "n_clicks"),
    prevent_initial_call=True
)
def handle_update_reset(update_clicks, reset_clicks):
    """Atualiza dados do Garmin ou reinicia dados - detecta qual botão foi clicado"""
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Div()
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == "update-data-btn":
        try:
            credentials = load_credentials()
            config = load_config()
            
            # Tentar com tokens primeiro, depois com email/senha se disponível
            success, message = fetch_garmin_data(
                email=credentials.get('email'),
                password=credentials.get('password'),
                config=config,
                use_tokens=True
            )
            
            if success:
                return html.Div(message, className="alert alert-success mt-3")
            else:
                return html.Div(message, className="alert alert-danger mt-3")
                
        except Exception as e:
            return html.Div(f"❌ Erro inesperado: {str(e)}", className="alert alert-danger mt-3")
    
    elif triggered_id == "reset-data-btn":
        try:
            if METRICS_FILE.exists():
                METRICS_FILE.unlink()
            if WORKOUTS_FILE.exists():
                WORKOUTS_FILE.unlink()
            
            return html.Div("✅ Dados reiniciados com sucesso!", className="alert alert-success mt-3")
        except Exception as e:
            return html.Div(f"❌ Erro ao reiniciar dados: {str(e)}", className="alert alert-danger mt-3")
    
    return html.Div()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8050)





