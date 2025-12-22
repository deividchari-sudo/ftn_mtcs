import streamlit as st
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from pathlib import Path
import time
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Fitness Metrics",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para responsividade mobile
st.markdown("""
<style>
    /* Responsividade para mobile */
    @media (max-width: 768px) {
        .stMetric {
            padding: 10px !important;
        }
        .stButton button {
            width: 100% !important;
            padding: 12px !important;
            font-size: 14px !important;
        }
        .stDataFrame {
            font-size: 12px !important;
        }
        h1, h2, h3 {
            font-size: 1.2em !important;
        }
    }
    
    /* Cards melhorados */
    .metric-card {
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Cores dos temas */
    body {
        background-color: #f8f9fa;
    }
    
    /* Melhorias gerais */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Diretório para armazenar credenciais localmente
LOCAL_STORAGE_DIR = Path.home() / ".fitness_metrics"
LOCAL_STORAGE_DIR.mkdir(exist_ok=True)

CONFIG_FILE = LOCAL_STORAGE_DIR / "user_config.json"
CREDENTIALS_FILE = LOCAL_STORAGE_DIR / "garmin_credentials.json"
METRICS_FILE = LOCAL_STORAGE_DIR / "fitness_metrics.json"
WORKOUTS_FILE = LOCAL_STORAGE_DIR / "workouts_42_dias.json"

def load_config():
    """Carrega configurações de fitness do armazenamento local"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {
        "age": 29,
        "ftp": 250,
        "pace_threshold": "4:22",
        "swim_pace_threshold": "2:01",
        "hr_rest": 50,
        "hr_max": 191
    }

def save_config(config):
    """Salva configurações de fitness no armazenamento local"""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_credentials():
    """Carrega credenciais do Garmin do armazenamento local"""
    if CREDENTIALS_FILE.exists():
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    return {"email": "", "password": ""}

def save_credentials(email, password):
    """Salva credenciais do Garmin no armazenamento local (apenas no device)"""
    # Definir permissões restritas no arquivo
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump({"email": email, "password": password}, f, indent=4)
    # Tentar restringir permissões de leitura (em Windows, Linux/Mac)
    try:
        os.chmod(CREDENTIALS_FILE, 0o600)
    except:
        pass

def load_metrics():
    """Carrega métricas de fitness do armazenamento local"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE, "r") as f:
            return json.load(f)
    return []

def save_metrics(metrics):
    """Salva métricas de fitness no armazenamento local"""
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=4)

def load_workouts():
    """Carrega lista de workouts do armazenamento local"""
    if WORKOUTS_FILE.exists():
        with open(WORKOUTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_workouts(workouts):
    """Salva lista de workouts no armazenamento local"""
    with open(WORKOUTS_FILE, "w") as f:
        json.dump(workouts, f, indent=4)

def calculate_trimp(activity, config):
    """Calcula TRIMP (Training Impulse) para uma atividade"""
    import math
    
    activity_type = activity.get('activityType', {}).get('typeKey', '')
    duration_sec = activity.get('duration', 0)
    duration_min = duration_sec / 60
    duration_h = duration_sec / 3600
    
    hr_rest = config.get('hr_rest', 50)
    hr_max = config.get('hr_max', 191)
    
    if activity_type in ['cycling', 'indoor_cycling']:
        avg_power = activity.get('averagePower', 0)
        if avg_power and config.get('ftp'):
            if_ = avg_power / config['ftp']
            trimp = duration_h * (if_ ** 2) * 100
        else:
            avg_hr = activity.get('averageHR', 0)
            if avg_hr:
                hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
                trimp = duration_min * hr_reserve * 0.64 * math.exp(1.92 * hr_reserve)
            else:
                trimp = 0
    elif activity_type in ['running', 'trail_running']:
        avg_hr = activity.get('averageHR', 0)
        if avg_hr:
            hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
            trimp = duration_min * hr_reserve * 0.64 * math.exp(1.92 * hr_reserve)
        else:
            avg_speed = activity.get('averageSpeed', 0)
            if avg_speed:
                pace_s_km = 1000 / avg_speed
                threshold_str = config.get('pace_threshold', '5:00')
                min_sec = threshold_str.split(':')
                threshold_sec = int(min_sec[0]) * 60 + int(min_sec[1])
                intensity = threshold_sec / pace_s_km
                trimp = duration_h * (intensity ** 2) * 100
            else:
                trimp = 0
    elif activity_type in ['swimming', 'lap_swimming']:
        distance_m = activity.get('distance', 0)
        if distance_m > 0:
            pace_sec_100m = (duration_sec / distance_m) * 100
            threshold_str = config.get('swim_pace_threshold', '2:30')
            min_sec = threshold_str.split(':')
            threshold_sec = int(min_sec[0]) * 60 + int(min_sec[1])
            intensity = threshold_sec / pace_sec_100m
            trimp = duration_h * (intensity ** 2) * 100
        else:
            trimp = duration_h * 25
    else:
        trimp = 0
    
    return trimp

def calculate_fitness_metrics(activities, config, start_date, end_date):
    """Calcula métricas de fitness (CTL, ATL, TSB) baseado em atividades"""
    daily_loads = {}
    for activity in activities:
        start_time = activity.get('startTimeLocal', '')
        if start_time:
            try:
                if 'T' not in start_time:
                    start_time = start_time.replace(' ', 'T')
                if not start_time.endswith('Z'):
                    start_time += 'Z'
                date = datetime.fromisoformat(start_time.replace('Z', '+00:00')).date()
                trimp = calculate_trimp(activity, config)
                daily_loads[date] = daily_loads.get(date, 0) + trimp
            except ValueError:
                continue
    
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += timedelta(days=1)
    
    ctl = 0
    atl = 0
    metrics = []
    for date in days:
        load = daily_loads.get(date, 0)
        ctl = ctl + (load - ctl) / 42
        atl = atl + (load - atl) / 7
        tsb = ctl - atl
        metrics.append({
            'date': date.isoformat(),
            'daily_load': load,
            'ctl': ctl,
            'atl': atl,
            'tsb': tsb
        })
    
    return metrics

def fetch_garmin_data(email, password, config):
    """Busca dados do Garmin Connect e atualiza métricas"""
    try:
        from garminconnect import Garmin
        
        client = Garmin(email, password)
        client.login()
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=42)
        
        activities = client.get_activities_by_date(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        # Salvar atividades localmente
        save_workouts(activities)
        
        # Calcular métricas
        metrics = calculate_fitness_metrics(activities, config, start_date, end_date)
        save_metrics(metrics)
        
        return True, f"✅ Dados atualizados com sucesso! {len(activities)} atividades carregadas."
    
    except ImportError:
        return False, "❌ Erro: garminconnect não instalado. Instale com: pip install garminconnect"
    except Exception as e:
        return False, f"❌ Erro ao buscar dados: {str(e)}"

# Inicializar session state
if 'update_status' not in st.session_state:
    st.session_state.update_status = None

# Sidebar - Navegação
st.sidebar.title("📱 Fitness Metrics")
page = st.sidebar.radio(
    "Navegação",
    ["📊 Dashboard", "⚙️ Configuração", "🔄 Atualizar Dados"]
)

# PAGE 1: DASHBOARD
if page == "📊 Dashboard":
    st.title("📊 Dashboard de Fitness")
    
    metrics = load_metrics()
    
    if not metrics:
        st.warning("⚠️ Nenhum dado disponível. Vá para 'Atualizar Dados' para sincronizar com Garmin Connect.")
    else:
        last_metric = metrics[-1]
        
        # ============ CARDS COM MÉTRICAS PRINCIPAIS ============
        st.markdown("### 📈 Resumo Atual")
        
        col1, col2, col3 = st.columns(3)
        
        # Calcular deltas
        ctl_delta = last_metric['ctl'] - metrics[-2]['ctl'] if len(metrics) > 1 else 0
        atl_delta = last_metric['atl'] - metrics[-2]['atl'] if len(metrics) > 1 else 0
        tsb_delta = last_metric['tsb'] - metrics[-2]['tsb'] if len(metrics) > 1 else 0
        
        ctl_pct = (ctl_delta / metrics[-2]['ctl'] * 100) if len(metrics) > 1 and metrics[-2]['ctl'] > 0 else 0
        atl_pct = (atl_delta / metrics[-2]['atl'] * 100) if len(metrics) > 1 and metrics[-2]['atl'] > 0 else 0
        tsb_pct = (tsb_delta / metrics[-2]['tsb'] * 100) if len(metrics) > 1 and metrics[-2]['tsb'] > 0 else 0
        
        with col1:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 20px; border-radius: 10px; text-align: center; border-left: 5px solid #1976d2;'>
                <h4 style='color: #1976d2; margin: 0;'>💪 Fitness (CTL)</h4>
                <h2 style='color: #1976d2; margin: 10px 0;'>{last_metric['ctl']:.1f}</h2>
                <p style='margin: 5px 0; color: #666;'>
                    {'📈 +' if ctl_delta >= 0 else '📉 '}{abs(ctl_delta):.1f} ({abs(ctl_pct):.1f}%)
                </p>
                <small style='color: #999;'>Forma Física Crônica</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%); padding: 20px; border-radius: 10px; text-align: center; border-left: 5px solid #d32f2f;'>
                <h4 style='color: #d32f2f; margin: 0;'>😴 Fadiga (ATL)</h4>
                <h2 style='color: #d32f2f; margin: 10px 0;'>{last_metric['atl']:.1f}</h2>
                <p style='margin: 5px 0; color: #666;'>
                    {'📈 +' if atl_delta >= 0 else '📉 '}{abs(atl_delta):.1f} ({abs(atl_pct):.1f}%)
                </p>
                <small style='color: #999;'>Fadiga Aguda (7 dias)</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 20px; border-radius: 10px; text-align: center; border-left: 5px solid #388e3c;'>
                <h4 style='color: #388e3c; margin: 0;'>⚖️ Equilíbrio (TSB)</h4>
                <h2 style='color: #388e3c; margin: 10px 0;'>{last_metric['tsb']:.1f}</h2>
                <p style='margin: 5px 0; color: #666;'>
                    {'📈 +' if tsb_delta >= 0 else '📉 '}{abs(tsb_delta):.1f} ({abs(tsb_pct):.1f}%)
                </p>
                <small style='color: #999;'>CTL - ATL</small>
            </div>
            """, unsafe_allow_html=True)
        
        # ============ INDICADOR DE STATUS ============
        st.markdown("### 📊 Status de Treinamento")
        
        tsb_value = last_metric['tsb']
        if tsb_value > 10:
            status = "✅ Recuperado"
            status_color = "#4caf50"
            description = "Você está bem descansado, ótimo para treinos intensos!"
        elif tsb_value >= -10:
            status = "⚖️ Equilibrado"
            status_color = "#ff9800"
            description = "Bom equilíbrio entre forma e fadiga, continue assim!"
        elif tsb_value >= -30:
            status = "⚠️ Fadiga"
            status_color = "#ff5722"
            description = "Você está cansado, considere reduzir volume/intensidade."
        else:
            status = "🚫 Overtraining"
            status_color = "#f44336"
            description = "CUIDADO! Você precisa descansar para evitar lesões."
        
        st.markdown(f"""
        <div style='background: {status_color}20; padding: 15px; border-radius: 8px; border-left: 4px solid {status_color};'>
            <h3 style='color: {status_color}; margin: 0;'>{status}</h3>
            <p style='color: #333; margin: 5px 0;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # ============ EXPLICAÇÃO DAS MÉTRICAS ============
        with st.expander("📚 O que significa cada métrica?"):
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                st.markdown("""
                **💪 CTL (Forma Física Crônica)**
                - Representa sua forma física geral, construída ao longo de ~6 semanas
                - Valores mais altos = você está mais preparado para provas longas
                - Para amador bem treinado em Ironman: ideal 50-90
                
                **😴 ATL (Fadiga Aguda)**
                - Mostra a fadiga recente (últimos 7 dias)
                - Valores altos = você precisa de descanso
                - Idealmente ATL < CTL para evitar overtraining
                """)
            
            with col_exp2:
                st.markdown("""
                **⚖️ TSB (Equilíbrio de Treino)**
                - Diferença entre CTL e ATL: TSB = CTL - ATL
                - Positivo = recuperação (bom para treinar duro)
                - Negativo = fadiga (precisa descansar)
                - É como um "saldo" de energia
                """)
        
        # ============ GRÁFICO COMPLETO COM MÚLTIPLOS SUBPLOTS ============
        st.markdown("### 📈 Análise Detalhada das Métricas (42 dias)")
        
        dates = [m['date'] for m in metrics]
        ctl = [m['ctl'] for m in metrics]
        atl = [m['atl'] for m in metrics]
        tsb = [m['tsb'] for m in metrics]
        
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
            ctl_ma = np.convolve(ctl, np.ones(7)/7, mode='valid')
            atl_ma = np.convolve(atl, np.ones(7)/7, mode='valid')
            tsb_ma = np.convolve(tsb, np.ones(7)/7, mode='valid')
            ma_dates = dates[6:]
        else:
            ctl_ma = atl_ma = tsb_ma = []
            ma_dates = []
        
        # Criar figura com múltiplos subplots
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 1, height_ratios=[4, 1.2, 1.2], hspace=0.3)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        ax3 = fig.add_subplot(gs[2])
        
        # ========== SUBPLOT 1: Gráfico Principal ==========
        ax1.plot(dates, ctl, label='Forma Física (CTL)', color='#1976d2', linewidth=2.5, marker='o', markersize=6, markevery=[-8, -2, -1])
        ax1.plot(dates, atl, label='Fadiga (ATL)', color='#d32f2f', linewidth=2.5, marker='s', markersize=6, markevery=[-8, -2, -1])
        ax1.plot(dates, tsb, label='Equilíbrio (TSB)', color='#388e3c', linewidth=2.5, marker='^', markersize=6, markevery=[-8, -2, -1])
        
        # Média móvel
        if len(ctl_ma) > 0:
            ax1.plot(ma_dates, ctl_ma, linestyle='--', color='#1976d2', alpha=0.6, linewidth=1.5, label='MA-7 CTL')
            ax1.plot(ma_dates, atl_ma, linestyle='--', color='#d32f2f', alpha=0.6, linewidth=1.5, label='MA-7 ATL')
            ax1.plot(ma_dates, tsb_ma, linestyle='--', color='#388e3c', alpha=0.6, linewidth=1.5, label='MA-7 TSB')
        
        # Zonas preenchidas
        ax1.fill_between(range(len(dates)), -50, 120, where=(np.array(ctl) >= 0), color='#bbdefb', alpha=0.2)
        ax1.fill_between(range(len(dates)), -50, 120, where=(np.array(ctl) >= 40), color='#1976d2', alpha=0.15)
        ax1.fill_between(range(len(dates)), -50, 120, where=(np.array(ctl) >= 80), color='#0d47a1', alpha=0.15)
        
        # Setas de tendência
        if len(dates) >= 8:
            ax1.annotate('', xy=(len(dates)-1, ctl[-1]), xytext=(len(dates)-8, ctl[-8]), 
                        arrowprops=dict(arrowstyle='->', color='#1976d2', lw=2, alpha=0.7))
            ax1.annotate('', xy=(len(dates)-1, atl[-1]), xytext=(len(dates)-8, atl[-8]), 
                        arrowprops=dict(arrowstyle='->', color='#d32f2f', lw=2, alpha=0.7))
            ax1.annotate('', xy=(len(dates)-1, tsb[-1]), xytext=(len(dates)-8, tsb[-8]), 
                        arrowprops=dict(arrowstyle='->', color='#388e3c', lw=2, alpha=0.7))
        
        ax1.set_xlabel('Data', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Pontuação', fontsize=11, fontweight='bold')
        ax1.set_title('Métricas de Performance - Análise Completa com Tendências', fontsize=13, fontweight='bold')
        ax1.legend(fontsize=9, loc='upper left', ncol=2)
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_xticks(range(0, len(dates), max(1, len(dates)//8)))
        ax1.set_xticklabels([dates[i] if i < len(dates) else '' for i in range(0, len(dates), max(1, len(dates)//8))], rotation=45, ha='right')
        
        # Texto de tendência e status
        trend_ctl = "📈" if delta_ctl > 0 else "📉" if delta_ctl < 0 else "➡️"
        trend_atl = "📈" if delta_atl > 0 else "📉" if delta_atl < 0 else "➡️"
        trend_tsb = "📈" if delta_tsb > 0 else "📉" if delta_tsb < 0 else "➡️"
        trend_text = f"Tendência Semanal:\nCTL: {trend_ctl} {delta_ctl:+.1f} ({pct_ctl:+.1f}%) | ATL: {trend_atl} {delta_atl:+.1f} ({pct_atl:+.1f}%) | TSB: {trend_tsb} {delta_tsb:+.1f} ({pct_tsb:+.1f}%)"
        ax1.text(0.02, 0.97, trend_text, transform=ax1.transAxes, fontsize=9, verticalalignment='top', 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="#bbdefb", alpha=0.85, edgecolor='#1976d2'))
        
        # ========== SUBPLOT 2: Deltas Semanais ==========
        labels = ['CTL', 'ATL', 'TSB']
        deltas = [delta_ctl, delta_atl, delta_tsb]
        colors = ['#1976d2', '#d32f2f', '#388e3c']
        bars = ax2.bar(labels, deltas, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # Adicionar valores nas barras
        for bar, delta in zip(bars, deltas):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{delta:+.1f}',
                    ha='center', va='bottom' if delta >= 0 else 'top', fontweight='bold', fontsize=10)
        
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_ylabel('Delta Semanal', fontsize=10, fontweight='bold')
        ax2.set_title('Mudanças na Última Semana', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
        
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
            x_pos = np.arange(len(months))
            ax3.plot(x_pos, ctl_monthly, label='CTL Médio', color='#1976d2', marker='o', linewidth=2, markersize=8)
            ax3.plot(x_pos, atl_monthly, label='ATL Médio', color='#d32f2f', marker='s', linewidth=2, markersize=8)
            ax3.plot(x_pos, tsb_monthly, label='TSB Médio', color='#388e3c', marker='^', linewidth=2, markersize=8)
            
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels(months)
            ax3.set_ylabel('Pontuação', fontsize=10, fontweight='bold')
            ax3.set_xlabel('Mês', fontsize=10, fontweight='bold')
            ax3.set_title('Progresso Mensal (Médias)', fontsize=11, fontweight='bold')
            ax3.legend(fontsize=9)
            ax3.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        
        # ============ REFERÊNCIAS PARA IRONMAN ============
        with st.expander("🎯 Referências para Amador Bem Treinado - Meio Ironman"):
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                st.markdown("""
                **8 semanas antes da prova:**
                - Forma Física (CTL): ~50
                - Fadiga (ATL): ~25
                - Equilíbrio (TSB): ~25
                
                **2 semanas antes da prova:**
                - Forma Física (CTL): ~80
                - Fadiga (ATL): ~40
                - Equilíbrio (TSB): ~40
                """)
            with col_ref2:
                st.markdown("""
                **Semana da prova:**
                - Forma Física (CTL): ~90
                - Fadiga (ATL): ~45
                - Equilíbrio (TSB): ~45
                
                **Valores atuais:**
                - CTL: {:.1f}
                - ATL: {:.1f}
                - TSB: {:.1f}
                """.format(ctl[-1], atl[-1], tsb[-1]))
        
        
        # ============ TABELA DE ATIVIDADES RECENTES ============
        st.markdown("### 📋 Últimas Métricas Diárias")
        
        workouts = load_workouts()
        if workouts:
            # Pegar últimas 7 atividades
            recent_workouts = sorted(workouts, key=lambda x: x.get('startTimeInSeconds', 0), reverse=True)[:7]
            
            workout_df = []
            for w in recent_workouts:
                try:
                    activity_name = w.get('activityName', 'Atividade Desconhecida')
                    distance = w.get('distance', 0)
                    duration_mins = w.get('duration', 0) // 60
                    
                    # Formatar distância
                    if distance >= 1000:
                        distance_str = f"{distance/1000:.2f} km"
                    else:
                        distance_str = f"{distance:.0f} m"
                    
                    # Converter timestamp
                    from datetime import datetime as dt
                    activity_date = dt.fromtimestamp(w.get('startTimeInSeconds', 0)).strftime('%d/%m/%Y')
                    
                    workout_df.append({
                        '📅 Data': activity_date,
                        '🏃 Atividade': activity_name[:25],
                        '📏 Distância': distance_str,
                        '⏱️ Duração': f"{duration_mins} min"
                    })
                except Exception:
                    continue
            
            if workout_df:
                st.dataframe(workout_df, use_container_width=True, hide_index=True)
        
        # ============ TABELA COM ÚLTIMAS MÉTRICAS ============
        st.markdown("### 📊 Histórico de Métricas (Últimos 7 dias)")
        
        display_metrics = metrics[-7:] if len(metrics) >= 7 else metrics
        display_df = []
        for m in reversed(display_metrics):
            display_df.append({
                '📅 Data': m['date'],
                '💪 Fitness (CTL)': f"{m['ctl']:.1f}",
                '😴 Fadiga (ATL)': f"{m['atl']:.1f}",
                '⚖️ Equilíbrio (TSB)': f"{m['tsb']:.1f}",
                '🎯 Carga Diária': f"{m['daily_load']:.1f}"
            })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# PAGE 2: CONFIGURAÇÃO
elif page == "⚙️ Configuração":
    st.title("⚙️ Configuração")
    
    st.markdown("""
    Configure suas credenciais do Garmin Connect e parâmetros de fitness.
    
    **⚠️ Segurança:** Suas credenciais são armazenadas **apenas no seu dispositivo** e 
    nunca são enviadas para servidores. Você pode deletá-las a qualquer momento.
    """)
    
    # Seção de Credenciais
    st.subheader("🔐 Credenciais Garmin Connect")
    st.info("Seus dados de login são armazenados de forma segura apenas neste dispositivo.")
    
    creds = load_credentials()
    
    col1, col2 = st.columns(2)
    with col1:
        email = st.text_input(
            "Email Garmin Connect",
            value=creds.get('email', ''),
            key='email_input'
        )
    with col2:
        password = st.text_input(
            "Senha Garmin Connect",
            value=creds.get('password', ''),
            type='password',
            key='password_input'
        )
    
    # Seção de Parâmetros de Fitness
    st.subheader("💪 Parâmetros de Fitness")
    
    config = load_config()
    
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input(
            "Idade",
            min_value=15,
            max_value=100,
            value=config.get('age', 29)
        )
        ftp = st.number_input(
            "FTP (Functional Threshold Power) - Watts",
            min_value=50,
            max_value=500,
            value=config.get('ftp', 250),
            step=5
        )
        hr_rest = st.number_input(
            "Frequência Cardíaca em Repouso (bpm)",
            min_value=40,
            max_value=100,
            value=config.get('hr_rest', 50)
        )
    
    with col2:
        hr_max = st.number_input(
            "Frequência Cardíaca Máxima (bpm)",
            min_value=150,
            max_value=220,
            value=config.get('hr_max', 191)
        )
        pace_threshold = st.text_input(
            "Limiar de Pace - Corrida (mm:ss)",
            value=config.get('pace_threshold', '4:22')
        )
        swim_pace_threshold = st.text_input(
            "Limiar de Pace - Natação (mm:ss)",
            value=config.get('swim_pace_threshold', '2:01')
        )
    
    # Botão para salvar
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Salvar Configurações", use_container_width=True):
            # Salvar credenciais
            save_credentials(email, password)
            
            # Salvar config
            new_config = {
                'age': age,
                'ftp': ftp,
                'hr_rest': hr_rest,
                'hr_max': hr_max,
                'pace_threshold': pace_threshold,
                'swim_pace_threshold': swim_pace_threshold
            }
            save_config(new_config)
            
            st.success("✅ Configurações salvas com sucesso!")
    
    with col2:
        if st.button("🗑️ Deletar Credenciais", use_container_width=True):
            if CREDENTIALS_FILE.exists():
                os.remove(CREDENTIALS_FILE)
            st.success("✅ Credenciais deletadas com sucesso!")
            st.rerun()
    
    with col3:
        if st.button("📂 Ver Local de Armazenamento", use_container_width=True):
            st.info(f"Arquivos armazenados em:\n`{LOCAL_STORAGE_DIR}`")

# PAGE 3: ATUALIZAR DADOS
else:  # "🔄 Atualizar Dados"
    st.title("🔄 Atualizar Dados do Garmin Connect")
    
    st.markdown("""
    Clique no botão abaixo para sincronizar seus dados com Garmin Connect.
    Este processo busca todas as atividades dos últimos 42 dias e recalcula 
    as métricas de fitness (CTL, ATL, TSB).
    """)
    
    # Verificar se credenciais estão configuradas
    creds = load_credentials()
    
    if not creds.get('email') or not creds.get('password'):
        st.warning("⚠️ Credenciais não configuradas. Vá para 'Configuração' para adicionar suas credenciais do Garmin Connect.")
    else:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔄 Atualizar Dados Agora", use_container_width=True):
                with st.spinner("Sincronizando com Garmin Connect..."):
                    config = load_config()
                    success, message = fetch_garmin_data(
                        creds['email'],
                        creds['password'],
                        config
                    )
                    
                    if success:
                        st.success(message)
                        st.session_state.update_status = ("success", message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                        st.session_state.update_status = ("error", message)
        
        with col2:
            # Informações sobre a última atualização
            workouts = load_workouts()
            if workouts:
                st.info(f"📊 Dados disponíveis:\n- **{len(workouts)}** atividades carregadas\n- Última atualização: Verifice a página Dashboard")
            else:
                st.info("📊 Nenhum dado carregado ainda.")
        
        # Status da última atualização
        if st.session_state.update_status:
            status_type, message = st.session_state.update_status
            if status_type == "success":
                st.success(message)
            else:
                st.error(message)
    
    # Instruções
    st.subheader("📖 Instruções")
    st.markdown("""
    1. **Configure suas credenciais** na página de Configuração
    2. **Clique em "Atualizar Dados Agora"** para sincronizar
    3. **Visualize os resultados** na página Dashboard
    
    A aplicação buscará todas as atividades dos últimos 42 dias e calculará:
    - **CTL (Forma Física)**: Carga de treino crônica (promédio de 42 dias)
    - **ATL (Fadiga)**: Carga de treino aguda (promédio de 7 dias)
    - **TSB (Equilíbrio)**: Diferença entre forma e fadiga (CTL - ATL)
    """)
