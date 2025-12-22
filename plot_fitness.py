import json
import matplotlib
matplotlib.use('Agg')  # Backend não interativo
import matplotlib.pyplot as plt

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
    
    # Plotar
    plt.figure(figsize=(14, 8))
    plt.plot(dates, ctl, label='Forma Física (Fitness Crônica)', color='blue', linewidth=2, marker='o', markersize=6, markevery=[-8, -2, -1])
    plt.plot(dates, atl, label='Fadiga Recente (Fadiga Aguda)', color='red', linewidth=2, marker='o', markersize=6, markevery=[-8, -2, -1])
    plt.plot(dates, tsb, label='Equilíbrio (Equilíbrio de Treino)', color='green', linewidth=2, marker='o', markersize=6, markevery=[-8, -2, -1])
    
    # Anotações nos marcadores
    last_idx = -1
    prev_idx = -2
    week_idx = -8
    plt.annotate(f'{ctl[last_idx]:.1f}', xy=(dates[last_idx], ctl[last_idx]), xytext=(0, 5), textcoords='offset points', color='blue', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{atl[last_idx]:.1f}', xy=(dates[last_idx], atl[last_idx]), xytext=(0, 5), textcoords='offset points', color='red', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{tsb[last_idx]:.1f}', xy=(dates[last_idx], tsb[last_idx]), xytext=(0, 5), textcoords='offset points', color='green', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{ctl[prev_idx]:.1f}', xy=(dates[prev_idx], ctl[prev_idx]), xytext=(0, 5), textcoords='offset points', color='blue', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{atl[prev_idx]:.1f}', xy=(dates[prev_idx], atl[prev_idx]), xytext=(0, 5), textcoords='offset points', color='red', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{tsb[prev_idx]:.1f}', xy=(dates[prev_idx], tsb[prev_idx]), xytext=(0, 5), textcoords='offset points', color='green', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{ctl[week_idx]:.1f}', xy=(dates[week_idx], ctl[week_idx]), xytext=(0, 5), textcoords='offset points', color='blue', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{atl[week_idx]:.1f}', xy=(dates[week_idx], atl[week_idx]), xytext=(0, 5), textcoords='offset points', color='red', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    plt.annotate(f'{tsb[week_idx]:.1f}', xy=(dates[week_idx], tsb[week_idx]), xytext=(0, 5), textcoords='offset points', color='green', fontsize=10, rotation=45, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none", alpha=0))
    
    # Adicionar referências para amador bem treinado em meio Ironman
    # Assumindo pico na data atual (semana da prova)
    from datetime import datetime, timedelta
    end_date = datetime.fromisoformat(dates[-1])
    ref_dates = {
        '8 semanas antes': end_date - timedelta(weeks=8),
        '6 semanas antes': end_date - timedelta(weeks=6),
        '4 semanas antes': end_date - timedelta(weeks=4),
        '2 semanas antes': end_date - timedelta(weeks=2),
        'Semana da prova': end_date
    }
    ref_ctl = {
        '8 semanas antes': 50,
        '6 semanas antes': 60,
        '4 semanas antes': 70,
        '2 semanas antes': 80,
        'Semana da prova': 90
    }
    
    # Removido: linhas verticais e anotações no gráfico
    plt.xlabel('Data')
    plt.ylabel('Pontuação')
    plt.title('Métricas de Performance de Treinamento ao Longo do Tempo\n(Referências para Amador Bem Treinado - Meio Ironman)')
    plt.legend()
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Adicionar caixa de referências
    ref_text = "Referências para Amador Bem Treinado - Meio Ironman:\n" \
               "- 8 semanas antes: Forma Física ~50, Fadiga ~25, Equilíbrio ~25\n" \
               "- 2 semanas antes: Forma Física ~80, Fadiga ~40, Equilíbrio ~40\n" \
               "- Semana da prova: Forma Física ~90, Fadiga ~45, Equilíbrio ~45"
    
    plt.text(0.02, 0.02, ref_text, transform=plt.gca().transAxes, fontsize=9, verticalalignment='bottom', 
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightyellow", alpha=0.8))
    
    plt.savefig('fitness_chart.png', dpi=300)
    print("Gráfico salvo em fitness_chart.png")
except Exception as e:
    print(f"Erro: {e}")