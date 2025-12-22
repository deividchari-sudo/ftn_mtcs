import os
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
from garminconnect import Garmin, GarminConnectConnectionError

# Credenciais (use variáveis de ambiente para segurança)
EMAIL = os.getenv("GARMIN_EMAIL", "")
PASSWORD = os.getenv("GARMIN_PASSWORD", "")

def calculate_trimp(activity, config):
    import math
    activity_type = activity.get('activityType', {}).get('typeKey', '')
    duration_sec = activity.get('duration', 0)
    duration_min = duration_sec / 60
    duration_h = duration_sec / 3600
    
    hr_rest = config.get('hr_rest', 50)
    hr_max = config.get('hr_max', 191)
    
    if activity_type in ['cycling', 'indoor_cycling']:
        avg_power = activity.get('averagePower', 0)
        if avg_power and config['ftp']:
            if_ = avg_power / config['ftp']
            trimp = duration_h * (if_ ** 2) * 100
        else:
            # Fallback to HR if no power
            avg_hr = activity.get('averageHR', 0)
            if avg_hr:
                hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
                trimp = duration_min * hr_reserve * 0.64 * math.exp(1.92 * hr_reserve)
            else:
                trimp = 0
    elif activity_type in ['running', 'trail_running']:
        avg_hr = activity.get('averageHR', 0)
        if avg_hr:
            # Use HR-based TRIMP
            hr_reserve = (avg_hr - hr_rest) / (hr_max - hr_rest)
            trimp = duration_min * hr_reserve * 0.64 * math.exp(1.92 * hr_reserve)
        else:
            # Fallback to pace
            avg_speed = activity.get('averageSpeed', 0)  # m/s
            if avg_speed:
                pace_s_km = 1000 / avg_speed  # seconds per km
                # pace_threshold: "4:22" -> 4*60+22 = 262 s/km
                threshold_str = config.get('pace_threshold', '5:00')
                min_sec = threshold_str.split(':')
                threshold_sec = int(min_sec[0]) * 60 + int(min_sec[1])
                # intensity = threshold / actual_pace (if actual < threshold, intensity >1)
                intensity = threshold_sec / pace_s_km
                trimp = duration_h * (intensity ** 2) * 100
            else:
                trimp = 0
    elif activity_type in ['swimming', 'lap_swimming']:
        # Para natação, usar pace-based TRIMP
        distance_m = activity.get('distance', 0)  # metros
        if distance_m > 0:
            pace_sec_100m = (duration_sec / distance_m) * 100  # segundos por 100m
            # swim_pace_threshold: "2:03" -> 123 s/100m
            threshold_str = config.get('swim_pace_threshold', '2:30')
            min_sec = threshold_str.split(':')
            threshold_sec = int(min_sec[0]) * 60 + int(min_sec[1])
            # intensity = threshold / actual_pace (if actual < threshold, intensity >1)
            intensity = threshold_sec / pace_sec_100m
            trimp = duration_h * (intensity ** 2) * 100
        else:
            # Fallback: estimativa baseada em duração (baixo esforço)
            trimp = duration_h * 25  # Valor baixo para natação sem dados
    else:
        trimp = 0
    return trimp

def calculate_fitness_metrics(activities, config, start_date, end_date):
    # Agrupar TRIMP por data
    daily_loads = {}
    for activity in activities:
        start_time = activity.get('startTimeLocal', '')
        if start_time:
            try:
                # startTimeLocal pode ser "2025-12-21 11:43:55" ou com Z
                if 'T' not in start_time:
                    start_time = start_time.replace(' ', 'T')
                if not start_time.endswith('Z'):
                    start_time += 'Z'
                date = datetime.fromisoformat(start_time.replace('Z', '+00:00')).date()
                trimp = calculate_trimp(activity, config)
                daily_loads[date] = daily_loads.get(date, 0) + trimp
            except ValueError as e:
                print(f"Erro ao parsear data {start_time}: {e}")
                continue
    
    # Lista de dias
    days = []
    current_date = start_date
    while current_date <= end_date:
        days.append(current_date)
        current_date += timedelta(days=1)
    
    # Calcular CTL, ATL
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
def main():
    try:
        # Carregar config
        with open("user_config.json", "r") as f:
            config = json.load(f)
        
        # Inicializar cliente
        client = Garmin(EMAIL, PASSWORD)
        
        # Login (salva tokens automaticamente)
        client.login()
        print("Login bem-sucedido!")
        
        # Calcular datas: últimos 42 dias
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=42)
        print(f"Extraindo atividades de {start_date} a {end_date}")
        
        # Extrair atividades (workouts registrados)
        activities = client.get_activities_by_date(
            start_date.isoformat(),
            end_date.isoformat()
        )
        
        print(f"Encontradas {len(activities)} atividades.")
        
        # Processar e exibir exemplo
        for activity in activities[:5]:  # Limite para exemplo
            print(f"- {activity.get('activityName', 'Desconhecido')}: "
                  f"{activity.get('distance', 0)/1000:.2f} km, "
                  f"{activity.get('duration', 0)/60:.1f} min, "
                  f"Data: {activity.get('startTimeLocal', 'N/A')}")
        
        # Salvar atividades
        with open("workouts_42_dias.json", "w") as f:
            json.dump(activities, f, indent=4)
        print("Dados salvos em workouts_42_dias.json")
        
        # Calcular métricas de fitness
        metrics = calculate_fitness_metrics(activities, config, start_date, end_date)
        
        # Salvar métricas
        with open("fitness_metrics.json", "w") as f:
            json.dump(metrics, f, indent=4)
        print("Métricas de fitness salvas em fitness_metrics.json")
        
        # Gerar gráfico
        dates = [m['date'] for m in metrics]
        ctl = [m['ctl'] for m in metrics]
        atl = [m['atl'] for m in metrics]
        tsb = [m['tsb'] for m in metrics]
        
        plt.figure(figsize=(12, 6))
        plt.plot(dates, ctl, label='CTL (Chronic Training Load - Fitness)', color='blue', linewidth=2)
        plt.plot(dates, atl, label='ATL (Acute Training Load - Fatigue)', color='red', linewidth=2)
        plt.plot(dates, tsb, label='TSB (Training Stress Balance - Form)', color='green', linewidth=2)
        plt.xlabel('Data')
        plt.ylabel('Pontuação')
        plt.title('Métricas de Performance de Treinamento ao Longo do Tempo')
        plt.legend()
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('fitness_chart.png', dpi=300)
        print("Gráfico salvo em fitness_chart.png")
        
        # Gerar gráfico completo e relatório HTML
        import subprocess
        subprocess.run(["python", "plot_fitness_completo.py"])
        
    except GarminConnectConnectionError as e:
        print(f"Erro de conexão: {e}")
    except Exception as e:
        print(f"Erro geral: {e}")

if __name__ == "__main__":
    main()