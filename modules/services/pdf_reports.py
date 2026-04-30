"""
Módulo de Geração de Relatórios PDF Profissionais
Cria relatórios semanais e mensais com métricas de fitness
"""
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie

import plotly.graph_objects as go
from PIL import Image as PILImage

# =============================================================================
# CONFIGURAÇÕES GLOBAIS
# =============================================================================

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 20 * mm

# Cores do tema
PRIMARY_COLOR = colors.HexColor('#1f77b4')
SECONDARY_COLOR = colors.HexColor('#ff7f0e')
SUCCESS_COLOR = colors.HexColor('#2ecc71')
DANGER_COLOR = colors.HexColor('#e74c3c')
WARNING_COLOR = colors.HexColor('#f39c12')
INFO_COLOR = colors.HexColor('#3498db')
LIGHT_GRAY = colors.HexColor('#f8f9fa')
DARK_GRAY = colors.HexColor('#343a40')

# =============================================================================
# CLASSES DE FORMATAÇÃO
# =============================================================================

class PDFHeaderFooter:
    """Classe para adicionar cabeçalho e rodapé em todas as páginas"""
    
    def __init__(self, title: str, athlete_name: str):
        self.title = title
        self.athlete_name = athlete_name
    
    def __call__(self, canvas_obj, doc):
        """Chamado para cada página"""
        canvas_obj.saveState()
        
        # Cabeçalho
        canvas_obj.setFont('Helvetica-Bold', 12)
        canvas_obj.setFillColor(PRIMARY_COLOR)
        canvas_obj.drawString(MARGIN, PAGE_HEIGHT - 15*mm, self.title)
        
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(DARK_GRAY)
        canvas_obj.drawRightString(
            PAGE_WIDTH - MARGIN, 
            PAGE_HEIGHT - 15*mm, 
            f"Atleta: {self.athlete_name}"
        )
        
        # Linha separadora
        canvas_obj.setStrokeColor(LIGHT_GRAY)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(MARGIN, PAGE_HEIGHT - 18*mm, PAGE_WIDTH - MARGIN, PAGE_HEIGHT - 18*mm)
        
        # Rodapé
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.gray)
        canvas_obj.drawString(
            MARGIN, 
            15*mm, 
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        canvas_obj.drawRightString(
            PAGE_WIDTH - MARGIN, 
            15*mm, 
            f"Página {doc.page}"
        )
        
        canvas_obj.restoreState()


# =============================================================================
# FUNÇÕES DE GERAÇÃO DE RELATÓRIOS
# =============================================================================

def create_weekly_report(
    workouts: List[Dict],
    metrics: Dict,
    config: Dict,
    start_date: datetime,
    end_date: datetime,
    output_path: str
) -> str:
    """
    Cria relatório semanal em PDF
    
    Args:
        workouts: Lista de treinos da semana
        metrics: Métricas calculadas (CTL, ATL, TSB)
        config: Configuração do usuário
        start_date: Data inicial
        end_date: Data final
        output_path: Caminho para salvar PDF
        
    Returns:
        Caminho do arquivo gerado
    """
    # Preparar documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=25*mm,
        bottomMargin=25*mm,
        leftMargin=MARGIN,
        rightMargin=MARGIN
    )
    
    # Criar story (conteúdo)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=DARK_GRAY,
        spaceAfter=10,
        spaceBefore=15
    )
    
    # Título
    story.append(Paragraph("📊 Relatório Semanal de Treinamento", title_style))
    story.append(Paragraph(
        f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}",
        styles['Normal']
    ))
    story.append(Spacer(1, 15))
    
    # === RESUMO EXECUTIVO ===
    story.append(Paragraph("📈 Resumo Executivo", heading_style))
    
    # Calcular estatísticas da semana
    total_activities = len(workouts)
    total_distance = sum(float(w.get('distance', 0) or 0) for w in workouts) / 1000  # em km
    total_duration = sum(float(w.get('duration', 0) or 0) for w in workouts) / 3600  # em horas
    total_tss = sum(float(w.get('training_stress_score', 0) or 0) for w in workouts)
    
    # Separar por modalidade
    swim_count = len([w for w in workouts if w.get('activityType', {}).get('typeKey') == 'lap_swimming'])
    bike_count = len([w for w in workouts if w.get('activityType', {}).get('typeKey') == 'cycling'])
    run_count = len([w for w in workouts if w.get('activityType', {}).get('typeKey') == 'running'])
    
    summary_data = [
        ['Métrica', 'Valor', 'Status'],
        ['Atividades Totais', f'{total_activities}', '✓' if total_activities >= 5 else '⚠'],
        ['Distância Total', f'{total_distance:.1f} km', '✓' if total_distance >= 50 else '⚠'],
        ['Tempo Total', f'{total_duration:.1f} h', '✓' if total_duration >= 7 else '⚠'],
        ['TSS Total', f'{total_tss:.0f}', '✓' if total_tss >= 300 else '⚠'],
        ['', '', ''],
        ['🏊 Natação', f'{swim_count} treinos', ''],
        ['🚴 Ciclismo', f'{bike_count} treinos', ''],
        ['🏃 Corrida', f'{run_count} treinos', ''],
    ]
    
    summary_table = Table(summary_data, colWidths=[120, 100, 50])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, 4), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # === MÉTRICAS DE CARGA ===
    story.append(Paragraph("💪 Métricas de Carga de Treinamento", heading_style))
    
    latest_metrics = metrics.get('latest', {}) if isinstance(metrics, dict) else {}
    ctl = latest_metrics.get('ctl', 0)
    atl = latest_metrics.get('atl', 0)
    tsb = latest_metrics.get('tsb', 0)
    
    # Determinar status de forma
    if tsb > 5:
        form_status = "Fresco / Recuperado"
        form_color = SUCCESS_COLOR
    elif tsb >= -10:
        form_status = "Forma Ideal / Race Ready"
        form_color = INFO_COLOR
    elif tsb >= -30:
        form_status = "Produtivo / Treinando"
        form_color = WARNING_COLOR
    else:
        form_status = "Fadiga Elevada"
        form_color = DANGER_COLOR
    
    metrics_data = [
        ['Métrica', 'Valor', 'Interpretação'],
        ['CTL (Fitness)', f'{ctl:.1f}', 'Carga crônica de treinamento (42 dias)'],
        ['ATL (Fadiga)', f'{atl:.1f}', 'Carga aguda de treinamento (7 dias)'],
        ['TSB (Forma)', f'{tsb:.1f}', form_status],
    ]
    
    metrics_table = Table(metrics_data, colWidths=[100, 80, 190])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 10))
    
    # Box de status de forma
    form_text = f"<b>Status Atual:</b> {form_status} (TSB: {tsb:.1f})"
    story.append(Paragraph(form_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # === DETALHAMENTO DOS TREINOS ===
    story.append(Paragraph("📋 Detalhamento dos Treinos", heading_style))
    
    if workouts:
        workouts_data = [['Data', 'Tipo', 'Duração', 'Distância', 'TSS']]
        
        for workout in sorted(workouts, key=lambda x: x.get('startTimeLocal', ''), reverse=True):
            date_str = workout.get('startTimeLocal', '')[:10] if workout.get('startTimeLocal') else 'N/A'
            activity_type = workout.get('activityType', {}).get('typeKey', 'N/A')
            
            # Emojis por tipo
            type_emoji = {
                'lap_swimming': '🏊',
                'cycling': '🚴',
                'running': '🏃',
                'walking': '🚶',
                'strength_training': '🏋️'
            }.get(activity_type, '🏃')
            
            duration_min = int(float(workout.get('duration', 0) or 0) / 60)
            distance_km = float(workout.get('distance', 0) or 0) / 1000
            tss = float(workout.get('training_stress_score', 0) or 0)
            
            workouts_data.append([
                date_str[-5:],  # Apenas MM-DD
                f"{type_emoji} {activity_type.replace('_', ' ').title()}",
                f"{duration_min} min",
                f"{distance_km:.2f} km" if distance_km > 0 else '-',
                f"{tss:.0f}" if tss > 0 else '-'
            ])
        
        workouts_table = Table(workouts_data, colWidths=[50, 120, 60, 70, 50])
        workouts_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),
        ]))
        
        story.append(workouts_table)
    else:
        story.append(Paragraph("Nenhum treino registrado nesta semana.", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # === RECOMENDAÇÕES ===
    story.append(Paragraph("💡 Recomendações", heading_style))
    
    recommendations = []
    
    # Baseado em TSB
    if tsb > 10:
        recommendations.append("• Você está bem recuperado. Bom momento para treinos de alta intensidade.")
    elif tsb > 0:
        recommendations.append("• Forma ideal! Considere manter essa carga ou fazer uma prova.")
    elif tsb > -15:
        recommendations.append("• Carga produtiva. Continue treinando, mas monitore sinais de fadiga.")
    else:
        recommendations.append("• ⚠️ Fadiga elevada. Considere reduzir o volume ou adicionar mais recuperação.")
    
    # Baseado em volume
    if total_activities < 3:
        recommendations.append("• Aumente a frequência de treinos para 4-6x por semana.")
    elif total_activities > 10:
        recommendations.append("• Volume alto de atividades. Certifique-se de ter recuperação adequada.")
    
    # Baseado em TSS
    if total_tss < 200:
        recommendations.append("• TSS baixo. Considere aumentar a intensidade ou duração dos treinos.")
    elif total_tss > 600:
        recommendations.append("• TSS muito alto! Monitore recuperação e considere semana de regeneração.")
    
    # Equilíbrio de modalidades
    total_modalities = sum([1 for x in [swim_count, bike_count, run_count] if x > 0])
    if total_modalities == 1:
        recommendations.append("• Considere adicionar treinos cruzados para desenvolvimento equilibrado.")
    
    for rec in recommendations:
        story.append(Paragraph(rec, styles['Normal']))
    
    # Gerar PDF
    athlete_name = config.get('athlete_name', 'Atleta')
    doc.build(
        story,
        onFirstPage=PDFHeaderFooter("Relatório Semanal", athlete_name),
        onLaterPages=PDFHeaderFooter("Relatório Semanal", athlete_name)
    )
    
    return output_path


def create_monthly_report(
    workouts: List[Dict],
    metrics: Dict,
    config: Dict,
    month: int,
    year: int,
    output_path: str
) -> str:
    """
    Cria relatório mensal em PDF (mais detalhado que o semanal)
    
    Args:
        workouts: Lista de treinos do mês
        metrics: Métricas calculadas
        config: Configuração do usuário
        month: Mês (1-12)
        year: Ano
        output_path: Caminho para salvar PDF
        
    Returns:
        Caminho do arquivo gerado
    """
    from calendar import month_name
    
    # Preparar documento
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=25*mm,
        bottomMargin=25*mm,
        leftMargin=MARGIN,
        rightMargin=MARGIN
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=PRIMARY_COLOR,
        spaceAfter=12,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=DARK_GRAY,
        spaceAfter=10,
        spaceBefore=15
    )
    
    # Título
    month_names = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    story.append(Paragraph(f"📊 Relatório Mensal - {month_names[month]} {year}", title_style))
    story.append(Spacer(1, 20))
    
    # === RESUMO DO MÊS ===
    story.append(Paragraph("📈 Resumo do Mês", heading_style))
    
    # Estatísticas
    total_activities = len(workouts)
    total_distance = sum(float(w.get('distance', 0) or 0) for w in workouts) / 1000
    total_duration = sum(float(w.get('duration', 0) or 0) for w in workouts) / 3600
    total_tss = sum(float(w.get('training_stress_score', 0) or 0) for w in workouts)
    
    # Por modalidade
    swim_workouts = [w for w in workouts if w.get('activityType', {}).get('typeKey') == 'lap_swimming']
    bike_workouts = [w for w in workouts if w.get('activityType', {}).get('typeKey') == 'cycling']
    run_workouts = [w for w in workouts if w.get('activityType', {}).get('typeKey') == 'running']
    
    swim_distance = sum(float(w.get('distance', 0) or 0) for w in swim_workouts) / 1000
    bike_distance = sum(float(w.get('distance', 0) or 0) for w in bike_workouts) / 1000
    run_distance = sum(float(w.get('distance', 0) or 0) for w in run_workouts) / 1000
    
    swim_time = sum(float(w.get('duration', 0) or 0) for w in swim_workouts) / 3600
    bike_time = sum(float(w.get('duration', 0) or 0) for w in bike_workouts) / 3600
    run_time = sum(float(w.get('duration', 0) or 0) for w in run_workouts) / 3600
    
    summary_data = [
        ['Métrica Geral', 'Valor'],
        ['Total de Atividades', f'{total_activities}'],
        ['Distância Total', f'{total_distance:.1f} km'],
        ['Tempo Total', f'{total_duration:.1f} h'],
        ['TSS Total', f'{total_tss:.0f}'],
        ['', ''],
        ['🏊 Natação', ''],
        ['   Treinos', f'{len(swim_workouts)}'],
        ['   Distância', f'{swim_distance:.1f} km'],
        ['   Tempo', f'{swim_time:.1f} h'],
        ['', ''],
        ['🚴 Ciclismo', ''],
        ['   Treinos', f'{len(bike_workouts)}'],
        ['   Distância', f'{bike_distance:.1f} km'],
        ['   Tempo', f'{bike_time:.1f} h'],
        ['', ''],
        ['🏃 Corrida', ''],
        ['   Treinos', f'{len(run_workouts)}'],
        ['   Distância', f'{run_distance:.1f} km'],
        ['   Tempo', f'{run_time:.1f} h'],
    ]
    
    summary_table = Table(summary_data, colWidths=[150, 120])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BACKGROUND', (0, 6), (0, 6), LIGHT_GRAY),
        ('BACKGROUND', (0, 11), (0, 11), LIGHT_GRAY),
        ('BACKGROUND', (0, 16), (0, 16), LIGHT_GRAY),
        ('FONTNAME', (0, 6), (0, 6), 'Helvetica-Bold'),
        ('FONTNAME', (0, 11), (0, 11), 'Helvetica-Bold'),
        ('FONTNAME', (0, 16), (0, 16), 'Helvetica-Bold'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # === EVOLUÇÃO DAS MÉTRICAS ===
    story.append(Paragraph("📊 Evolução das Métricas", heading_style))
    
    latest_metrics = metrics.get('latest', {}) if isinstance(metrics, dict) else {}
    story.append(Paragraph(
        f"CTL (Fitness): {latest_metrics.get('ctl', 0):.1f} | "
        f"ATL (Fadiga): {latest_metrics.get('atl', 0):.1f} | "
        f"TSB (Forma): {latest_metrics.get('tsb', 0):.1f}",
        styles['Normal']
    ))
    story.append(Spacer(1, 20))
    
    # === ANÁLISE E CONCLUSÃO ===
    story.append(Paragraph("💡 Análise e Recomendações", heading_style))
    
    avg_activities_per_week = total_activities / 4.3  # Aproximadamente 4.3 semanas/mês
    avg_tss_per_week = total_tss / 4.3
    
    analysis = [
        f"• Você completou {total_activities} atividades neste mês, com uma média de {avg_activities_per_week:.1f} treinos por semana.",
        f"• A carga de treinamento média foi de {avg_tss_per_week:.0f} TSS por semana.",
        f"• Distância total percorrida: {total_distance:.1f} km em {total_duration:.1f} horas."
    ]
    
    # Distribuição de modalidades
    if len(swim_workouts) > 0:
        swim_percent = (len(swim_workouts) / total_activities) * 100
        analysis.append(f"• Natação representou {swim_percent:.0f}% dos treinos ({len(swim_workouts)} sessões).")
    
    if len(bike_workouts) > 0:
        bike_percent = (len(bike_workouts) / total_activities) * 100
        analysis.append(f"• Ciclismo representou {bike_percent:.0f}% dos treinos ({len(bike_workouts)} sessões).")
    
    if len(run_workouts) > 0:
        run_percent = (len(run_workouts) / total_activities) * 100
        analysis.append(f"• Corrida representou {run_percent:.0f}% dos treinos ({len(run_workouts)} sessões).")
    
    for item in analysis:
        story.append(Paragraph(item, styles['Normal']))
        story.append(Spacer(1, 5))
    
    # Gerar PDF
    athlete_name = config.get('athlete_name', 'Atleta')
    doc.build(
        story,
        onFirstPage=PDFHeaderFooter(f"Relatório Mensal - {month_names[month]} {year}", athlete_name),
        onLaterPages=PDFHeaderFooter(f"Relatório Mensal - {month_names[month]} {year}", athlete_name)
    )
    
    return output_path


# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def get_default_output_dir() -> Path:
    """Retorna diretório padrão para salvar relatórios"""
    output_dir = Path.home() / '.fitness_metrics' / 'reports'
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def generate_filename(report_type: str, start_date: datetime, end_date: Optional[datetime] = None) -> str:
    """Gera nome de arquivo padronizado"""
    if end_date:
        return f"relatorio_{report_type}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.pdf"
    else:
        return f"relatorio_{report_type}_{start_date.strftime('%Y%m%d')}.pdf"
