"""
Componentes e funções de criação de gráficos para o Fitness Metrics Dashboard
"""
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import calendar
from utils import *

# Função auxiliar para converter horas decimais em hh:mm:ss
def format_hours_to_hms(hours):
    """Converte horas decimais para formato hh:mm:ss"""
    if hours == 0:
        return "00:00:00"
    h = int(hours)
    m = int((hours - h) * 60)
    s = int(((hours - h) * 60 - m) * 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

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

def create_distribution_chart():
    try:
        workouts = load_workouts()

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
    try:
        workouts = load_workouts()

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