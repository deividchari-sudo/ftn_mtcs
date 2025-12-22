import json
import matplotlib
matplotlib.use('Agg')  # Backend não interativo
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

try:
    # Carregar métricas
    with open("fitness_metrics.json", "r") as f:
        metrics = json.load(f)
    
    print(f"Carregadas {len(metrics)} métricas")
    
    # Extrair dados
    dates = [m['date'] for m in metrics]
    ctl = [m['ctl'] for m in metrics]
    atl = [m['atl'] for m in metrics]
    tsb = [m['tsb'] for m in metrics]
    
    print("Dados extraídos")
    
    # Calcular deltas semanais e percentuais
    if len(metrics) >= 8:
        delta_ctl = ctl[-1] - ctl[-8]
        pct_ctl = (ctl[-1] / ctl[-8] - 1) * 100 if ctl[-8] != 0 else 0
        delta_atl = atl[-1] - atl[-8]
        pct_atl = (atl[-1] / atl[-8] - 1) * 100 if atl[-8] != 0 else 0
        delta_tsb = tsb[-1] - tsb[-8]
        pct_tsb = (tsb[-1] / tsb[-8] - 1) * 100 if tsb[-8] != 0 else 0
    else:
        delta_ctl = pct_ctl = delta_atl = pct_atl = delta_tsb = pct_tsb = 0
    
    # Média móvel 7 dias
    if len(ctl) >= 7:
        ctl_ma = np.convolve(ctl, np.ones(7)/7, mode='valid')
        atl_ma = np.convolve(atl, np.ones(7)/7, mode='valid')
        tsb_ma = np.convolve(tsb, np.ones(7)/7, mode='valid')
        ma_dates = dates[6:]  # Ajustar datas
    else:
        ctl_ma = atl_ma = tsb_ma = []
        ma_dates = []
    
    # Plotar
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 18), gridspec_kw={'height_ratios': [4, 1, 1]})
    
    # Gráfico principal
    ax1.plot(dates, ctl, label='Forma Física (Fitness Crônica)', color='blue', linewidth=2, marker='o', markersize=6, markevery=[-8, -2, -1])
    ax1.plot(dates, atl, label='Fadiga Recente (Fadiga Aguda)', color='red', linewidth=2, marker='o', markersize=6, markevery=[-8, -2, -1])
    ax1.plot(dates, tsb, label='Equilíbrio (Equilíbrio de Treino)', color='green', linewidth=2, marker='o', markersize=6, markevery=[-8, -2, -1])
    
    # Média móvel
    if len(ctl_ma) > 0:
        ax1.plot(ma_dates, ctl_ma, linestyle='--', color='blue', alpha=0.7, label='Média Móvel CTL (7 dias)')
        ax1.plot(ma_dates, atl_ma, linestyle='--', color='red', alpha=0.7, label='Média Móvel ATL (7 dias)')
        ax1.plot(ma_dates, tsb_ma, linestyle='--', color='green', alpha=0.7, label='Média Móvel TSB (7 dias)')
    
    # Zonas preenchidas (inspirado em TrainingPeaks)
    ax1.fill_between(dates, 0, 40, where=(np.array(ctl) >= 0), color='lightblue', alpha=0.2, label='Zona Forma Baixa (<40)')
    ax1.fill_between(dates, 40, 80, where=(np.array(ctl) >= 40), color='blue', alpha=0.2, label='Zona Forma Boa (40-80)')
    ax1.fill_between(dates, 80, 120, where=(np.array(ctl) >= 80), color='darkblue', alpha=0.2, label='Zona Forma Excelente (>80)')
    
    # Zonas de fadiga
    ax1.fill_between(dates, 0, 20, where=(np.array(atl) >= 0), color='lightcoral', alpha=0.1, label='Fadiga Baixa (<20)')
    ax1.fill_between(dates, 20, 40, where=(np.array(atl) >= 20), color='red', alpha=0.1, label='Fadiga Moderada (20-40)')
    ax1.fill_between(dates, 40, 80, where=(np.array(atl) >= 40), color='darkred', alpha=0.1, label='Fadiga Alta (>40)')
    
    # Setas de tendência semanal
    if len(dates) >= 8:
        # Usar annotate com arrow
        ax1.annotate('', xy=(dates[-1], ctl[-1]), xytext=(dates[-8], ctl[-8]), arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7))
        ax1.annotate('', xy=(dates[-1], atl[-1]), xytext=(dates[-8], atl[-8]), arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))
        ax1.annotate('', xy=(dates[-1], tsb[-1]), xytext=(dates[-8], tsb[-8]), arrowprops=dict(arrowstyle='->', color='green', alpha=0.7))
    
    # Anotações com percentual
    last_idx = -1
    prev_idx = -2
    week_idx = -8
    ax1.annotate(f'{ctl[last_idx]:.1f} ({pct_ctl:.1f}%)', xy=(dates[last_idx], ctl[last_idx]), xytext=(0, 5), textcoords='offset points', color='blue', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{atl[last_idx]:.1f} ({pct_atl:.1f}%)', xy=(dates[last_idx], atl[last_idx]), xytext=(0, 5), textcoords='offset points', color='red', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{tsb[last_idx]:.1f} ({pct_tsb:.1f}%)', xy=(dates[last_idx], tsb[last_idx]), xytext=(0, 5), textcoords='offset points', color='green', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{ctl[prev_idx]:.1f}', xy=(dates[prev_idx], ctl[prev_idx]), xytext=(0, 5), textcoords='offset points', color='blue', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{atl[prev_idx]:.1f}', xy=(dates[prev_idx], atl[prev_idx]), xytext=(0, 5), textcoords='offset points', color='red', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{tsb[prev_idx]:.1f}', xy=(dates[prev_idx], tsb[prev_idx]), xytext=(0, 5), textcoords='offset points', color='green', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{ctl[week_idx]:.1f}', xy=(dates[week_idx], ctl[week_idx]), xytext=(0, 5), textcoords='offset points', color='blue', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{atl[week_idx]:.1f}', xy=(dates[week_idx], atl[week_idx]), xytext=(0, 5), textcoords='offset points', color='red', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    ax1.annotate(f'{tsb[week_idx]:.1f}', xy=(dates[week_idx], tsb[week_idx]), xytext=(0, 5), textcoords='offset points', color='green', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    
    ax1.set_xlabel('Data')
    ax1.set_ylabel('Pontuação')
    ax1.set_title('Métricas de Performance de Treinamento ao Longo do Tempo\n(Referências para Amador Bem Treinado - Meio Ironman)')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, alpha=0.3)
    
    # Texto de tendência
    trend_ctl = "Subindo" if delta_ctl > 0 else "Descendo" if delta_ctl < 0 else "Estável"
    trend_atl = "Subindo" if delta_atl > 0 else "Descendo" if delta_atl < 0 else "Estável"
    trend_tsb = "Subindo" if delta_tsb > 0 else "Descendo" if delta_tsb < 0 else "Estável"
    trend_text = f"Tendência Semanal:\nCTL: {trend_ctl} {delta_ctl:.1f} ({pct_ctl:.1f}%)\nATL: {trend_atl} {delta_atl:.1f} ({pct_atl:.1f}%)\nTSB: {trend_tsb} {delta_tsb:.1f} ({pct_tsb:.1f}%)"
    ax1.text(0.02, 0.98, trend_text, transform=ax1.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
    
    # Indicador de status de treino (inspirado em Strava/TrainingPeaks)
    status = "Recuperação" if tsb[-1] > 10 else "Equilibrado" if tsb[-1] > -10 else "Fadiga" if tsb[-1] > -30 else "Overtraining"
    status_color = "green" if status == "Recuperação" else "yellow" if status == "Equilibrado" else "orange" if status == "Fadiga" else "red"
    ax1.text(0.98, 0.98, f"Status Atual: {status}", transform=ax1.transAxes, fontsize=12, verticalalignment='top', horizontalalignment='right', bbox=dict(boxstyle="round,pad=0.3", facecolor=status_color, alpha=0.8))
    
    # Subplot para barras de deltas
    labels = ['CTL', 'ATL', 'TSB']
    deltas = [delta_ctl, delta_atl, delta_tsb]
    ax2.bar(labels, deltas, color=['blue', 'red', 'green'], alpha=0.7)
    ax2.set_title('Mudanças Semanais')
    ax2.set_ylabel('Delta')
    ax2.grid(True, alpha=0.3)
    
    # Subplot para progresso mensal (inspirado em Strava)
    months = []
    ctl_monthly = []
    atl_monthly = []
    tsb_monthly = []
    current_month = None
    month_data = {'ctl': [], 'atl': [], 'tsb': []}
    for i, m in enumerate(metrics):
        date = datetime.fromisoformat(m['date'])
        month = date.strftime('%Y-%m')
        if current_month != month:
            if current_month:
                ctl_monthly.append(np.mean(month_data['ctl']))
                atl_monthly.append(np.mean(month_data['atl']))
                tsb_monthly.append(np.mean(month_data['tsb']))
                months.append(current_month)
            current_month = month
            month_data = {'ctl': [], 'atl': [], 'tsb': []}
        month_data['ctl'].append(m['ctl'])
        month_data['atl'].append(m['atl'])
        month_data['tsb'].append(m['tsb'])
    if month_data['ctl']:
        ctl_monthly.append(np.mean(month_data['ctl']))
        atl_monthly.append(np.mean(month_data['atl']))
        tsb_monthly.append(np.mean(month_data['tsb']))
        months.append(current_month)
    
    ax3.plot(months, ctl_monthly, label='CTL Médio Mensal', color='blue', marker='o')
    ax3.plot(months, atl_monthly, label='ATL Médio Mensal', color='red', marker='o')
    ax3.plot(months, tsb_monthly, label='TSB Médio Mensal', color='green', marker='o')
    ax3.set_title('Progresso Mensal (Médias)')
    ax3.set_xlabel('Mês')
    ax3.set_ylabel('Pontuação')
    ax3.legend()
    ax3.tick_params(axis='x', rotation=45)
    ax3.grid(True, alpha=0.3)
    
    # Referências
    ref_text = "Referências para Amador Bem Treinado - Meio Ironman:\n" \
               "- 8 semanas antes: Forma Física ~50, Fadiga ~25, Equilíbrio ~25\n" \
               "- 2 semanas antes: Forma Física ~80, Fadiga ~40, Equilíbrio ~40\n" \
               "- Semana da prova: Forma Física ~90, Fadiga ~45, Equilíbrio ~45"
    
    fig.text(0.02, 0.02, ref_text, fontsize=9, verticalalignment='bottom', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('fitness_chart_completo.png', dpi=300)
    print("Gráfico completo salvo em fitness_chart_completo.png")
    
    # Carregar atividades para resumo
    try:
        with open("workouts_42_dias.json", "r") as f:
            activities = json.load(f)
        recent_activities = activities[:10]  # Últimas 10
    except:
        recent_activities = []
    
    # Gerar relatório HTML detalhado
    activities_html = ""
    if recent_activities:
        activities_html = "<table><tr><th>Data</th><th>Atividade</th><th>Distância</th><th>Duração</th></tr>"
        for act in recent_activities:
            name = act.get('activityName', 'Desconhecido')
            dist = f"{act.get('distance', 0)/1000:.2f} km" if act.get('distance') else "N/A"
            dur = f"{act.get('duration', 0)/60:.1f} min"
            date = act.get('startTimeLocal', 'N/A')[:10]
            activities_html += f"<tr><td>{date}</td><td>{name}</td><td>{dist}</td><td>{dur}</td></tr>"
        activities_html += "</table>"
    
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório de Métricas de Treinamento - Ironman</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); color: #333; }}
        h1, h2, h3 {{ color: #1976d2; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); }}
        .container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .full-width {{ grid-column: span 2; }}
        .section {{ background-color: rgba(255,255,255,0.95); padding: 20px; margin-bottom: 20px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .metric {{ margin-bottom: 15px; }}
        .metric h4 {{ color: #1976d2; }}
        .chart {{ text-align: center; }}
        .chart img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        .status {{ font-weight: bold; padding: 10px; border-radius: 5px; display: inline-block; }}
        .recuperacao {{ background-color: #c8e6c9; color: #2e7d32; }}
        .equilibrado {{ background-color: #fff9c4; color: #f57f17; }}
        .fadiga {{ background-color: #ffcdd2; color: #c62828; }}
        .overtraining {{ background-color: #f8bbd9; color: #ad1457; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; color: #333; }}
        .cards {{ display: flex; justify-content: space-around; flex-wrap: wrap; }}
        .card {{ background: #fff; border-radius: 8px; padding: 15px; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); text-align: center; flex: 1; min-width: 150px; border-left: 5px solid #1976d2; }}
        .card h3 {{ margin: 0; color: #1976d2; }}
        .card p {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
        .icon {{ font-size: 2em; margin-bottom: 10px; }}
        .blue {{ color: #1976d2; }}
        .red {{ color: #d32f2f; }}
        .green {{ color: #388e3c; }}
    </style>
</head>
<body>
    <h1><i class="fas fa-chart-line"></i> Relatório Detalhado de Métricas de Treinamento - Ironman</h1>
    <p>Olá! Este relatório foi gerado automaticamente com base nos seus dados de treinamento do Garmin. Como você é iniciante nessas métricas, vou explicar tudo passo a passo, de forma simples e clara. As métricas CTL (Chronic Training Load), ATL (Acute Training Load) e TSB (Training Stress Balance) ajudam a entender como seu corpo responde ao treinamento, evitando lesões e otimizando o desempenho.</p>
    
    <div class="container">
        <div class="section full-width">
            <h2><i class="fas fa-info-circle"></i> Resumo Atual</h2>
            <div class="cards">
                <div class="card">
                    <div class="icon blue"><i class="fas fa-dumbbell"></i></div>
                    <h3>CTL (Forma Física)</h3>
                    <p>{ctl[-1]:.1f}</p>
                    <small>{trend_ctl} {delta_ctl:.1f} ({pct_ctl:.1f}%)</small>
                </div>
                <div class="card">
                    <div class="icon red"><i class="fas fa-tired"></i></div>
                    <h3>ATL (Fadiga)</h3>
                    <p>{atl[-1]:.1f}</p>
                    <small>{trend_atl} {delta_atl:.1f} ({pct_atl:.1f}%)</small>
                </div>
                <div class="card">
                    <div class="icon green"><i class="fas fa-balance-scale"></i></div>
                    <h3>TSB (Equilíbrio)</h3>
                    <p>{tsb[-1]:.1f}</p>
                    <small>{trend_tsb} {delta_tsb:.1f} ({pct_tsb:.1f}%)</small>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2><i class="fas fa-chart-area"></i> 1. Introdução às Métricas</h2>
            <p>Essas métricas vêm da teoria de treinamento de Andrew Coggan e Hunter Allen. Elas medem o estresse do treinamento e a adaptação do corpo:</p>
            <div class="metric">
                <h4><i class="fas fa-heartbeat blue"></i> CTL (Chronic Training Load) - Forma Física Crônica</h4>
                <p>Representa sua forma física geral, construída ao longo do tempo (cerca de 6 semanas). É como a "base" do seu condicionamento. Valores mais altos significam que você está mais preparado para provas longas. Para um amador bem treinado em meio Ironman, o CTL ideal é em torno de 50-90.</p>
            </div>
            <div class="metric">
                <h4><i class="fas fa-exclamation-triangle red"></i> ATL (Acute Training Load) - Fadiga Aguda</h4>
                <p>Mostra a fadiga recente (últimos 7 dias). É o cansaço imediato do treinamento intenso. Valores altos indicam que você precisa de descanso. Idealmente, ATL deve ser menor que CTL para evitar overtraining.</p>
            </div>
            <div class="metric">
                <h4><i class="fas fa-balance-scale green"></i> TSB (Training Stress Balance) - Equilíbrio de Treino</h4>
                <p>É a diferença entre CTL e ATL (TSB = CTL - ATL). Valores positivos significam recuperação (bom para treinar duro), negativos indicam fadiga (precisa descansar). É como um "saldo" de energia.</p>
            </div>
        </div>
        
        <div class="section">
            <h2><i class="fas fa-list"></i> Atividades Recentes</h2>
            <p>Aqui estão suas últimas atividades registradas:</p>
            {activities_html}
        </div>
        
        <div class="section full-width chart">
            <h2><i class="fas fa-chart-bar"></i> 2. Gráfico Completo das Métricas</h2>
            <p>Abaixo está o gráfico visual das suas métricas ao longo do tempo. As linhas mostram a evolução, as zonas coloridas ajudam a interpretar os níveis, e as setas indicam tendências semanais.</p>
            <img src="fitness_chart_completo.png" alt="Gráfico de Métricas de Treinamento" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        </div>
        
        <div class="section">
            <h2>3. Interpretação do Gráfico Principal</h2>
            <p>O gráfico principal tem três linhas coloridas (azul para CTL, vermelho para ATL, verde para TSB) e médias móveis (linhas pontilhadas) para suavizar variações diárias.</p>
            <h3>Zonas Coloridas</h3>
            <p>As áreas preenchidas representam níveis de forma e fadiga:</p>
            <ul>
                <li><strong>Forma Física (CTL):</strong> Azul claro (<40) = baixa; Azul médio (40-80) = boa; Azul escuro (>80) = excelente.</li>
                <li><strong>Fadiga (ATL):</strong> Rosa claro (<20) = baixa; Vermelho médio (20-40) = moderada; Vermelho escuro (>40) = alta.</li>
            </ul>
            <p>Essas zonas são inspiradas em apps como TrainingPeaks e ajudam a ver se você está progredindo.</p>
            <h3>Setas de Tendência</h3>
            <p>As setas mostram se as métricas estão subindo, descendo ou estáveis na última semana. Por exemplo, uma seta para cima no CTL significa que sua forma está melhorando.</p>
            <h3>Anotações nos Pontos</h3>
            <p>Nos últimos pontos (hoje, ontem e há 7 dias), há números com percentuais. O percentual mostra a mudança semanal (ex: +10% significa aumento de 10% em uma semana).</p>
        </div>
        
        <div class="section">
            <h2>4. Tendências Semanais</h2>
            <p>No gráfico, há um texto com tendências semanais. Aqui está um resumo:</p>
            <table>
                <tr><th>Métrica</th><th>Tendência</th><th>Delta (Diferença)</th><th>Percentual</th></tr>
                <tr><td>CTL</td><td>{trend_ctl}</td><td>{delta_ctl:.1f}</td><td>{pct_ctl:.1f}%</td></tr>
                <tr><td>ATL</td><td>{trend_atl}</td><td>{delta_atl:.1f}</td><td>{pct_atl:.1f}%</td></tr>
                <tr><td>TSB</td><td>{trend_tsb}</td><td>{delta_tsb:.1f}</td><td>{pct_tsb:.1f}%</td></tr>
            </table>
            <p><strong>Dica:</strong> Se CTL estiver subindo e ATL não muito alto, você está progredindo bem. Se ATL subir demais, reduza o treino.</p>
        </div>
        
        <div class="section full-width">
            <h2>5. Status Atual de Treinamento</h2>
            <p>Baseado no TSB atual ({tsb[-1]:.1f}), seu status é:</p>
            <div class="status {status.lower()}">{status}</div>
            <ul>
                <li><strong>Recuperação (TSB > 10):</strong> Você está descansado, ótimo para treinos intensos ou provas.</li>
                <li><strong>Equilibrado (TSB -10 a 10):</strong> Bom equilíbrio, continue treinando normalmente.</li>
                <li><strong>Fadiga (TSB -10 a -30):</strong> Cuidado, você está cansado. Reduza volume ou intensidade.</li>
                <li><strong>Overtraining (TSB < -30):</strong> Pare! Você precisa de descanso para evitar lesões.</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>6. Mudanças Semanais (Subplot de Barras)</h2>
            <p>O segundo gráfico mostra deltas semanais em barras. Valores positivos significam aumento, negativos diminuição.</p>
            <p>Por exemplo, se CTL aumentou +5, sua forma melhorou 5 pontos na semana.</p>
        </div>
        
        <div class="section">
            <h2>7. Progresso Mensal (Subplot de Linhas)</h2>
            <p>O terceiro gráfico mostra médias mensais. Ajuda a ver progresso a longo prazo, inspirado em Strava.</p>
            <p>Se as linhas estiverem subindo suavemente, você está evoluindo bem para o Ironman.</p>
        </div>
        
        <div class="section full-width">
            <h2>8. Referências para Meio Ironman</h2>
            <p>Para um amador bem treinado, os valores ideais variam por fase:</p>
            <ul>
                <li><strong>8 semanas antes:</strong> CTL ~50, ATL ~25, TSB ~25 (construindo base).</li>
                <li><strong>2 semanas antes:</strong> CTL ~80, ATL ~40, TSB ~40 (pico de forma).</li>
                <li><strong>Semana da prova:</strong> CTL ~90, ATL ~45, TSB ~45 (pronto para competir).</li>
            </ul>
            <p>Compare com seus valores atuais para ajustar o treinamento.</p>
        </div>
        
        <div class="section full-width">
            <h2>9. Conclusões e Dicas</h2>
            <p>Seus valores atuais: CTL = {ctl[-1]:.1f}, ATL = {atl[-1]:.1f}, TSB = {tsb[-1]:.1f}.</p>
            <p><strong>Interpretação geral:</strong> {'Você está em boa forma!' if ctl[-1] > 40 else 'Trabalhe na construção de forma.'} {'Mas cuidado com a fadiga.' if atl[-1] > ctl[-1] else 'Fadiga sob controle.'}</p>
            <p><strong>Dicas para leigos:</strong></p>
            <ul>
                <li>Monitore o TSB: Treine quando positivo, descanse quando negativo.</li>
                <li>Aumente CTL gradualmente (não mais de 10% por semana) para evitar lesões.</li>
                <li>Use dias de recuperação quando ATL alto.</li>
                <li>Para Ironman, foque em equilíbrio: forma alta sem fadiga excessiva.</li>
            </ul>
            <p>Relatório gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}.</p>
        </div>
    </div>
</body>
</html>
"""
    
    with open("relatorio_treinamento.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Relatório HTML salvo em relatorio_treinamento.html")
    
except Exception as e:
    print(f"Erro: {e}")