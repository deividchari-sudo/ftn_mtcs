"""
Callbacks for data export functionality.

Exports: CSV metrics, CSV workouts, PDF weekly, PDF monthly
"""
import dash
from dash import Output, Input, html
from datetime import datetime


def register_export_callbacks(app):
    """Register all export-related callbacks."""
    
    @app.callback(
        Output("download-metrics", "data"),
        Input("btn-export-metrics", "n_clicks"),
        prevent_initial_call=True
    )
    def export_metrics_csv(n_clicks):
        """Exporta métricas para CSV"""
        if n_clicks:
            try:
                import io
                import csv
                from modules.infra.cache_manager import get_cached
                
                metrics = get_cached('fitness_metrics', [])[-60:]  # últimos 60 dias
                if metrics:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=['date', 'ctl', 'atl', 'tsb'])
                    writer.writeheader()
                    for m in metrics:
                        writer.writerow({
                            'date': m.get('date', ''),
                            'ctl': m.get('ctl', 0),
                            'atl': m.get('atl', 0),
                            'tsb': m.get('tsb', 0)
                        })
                    
                    return dict(
                        content=output.getvalue(),
                        filename=f"fitness_metrics_{datetime.now().strftime('%Y%m%d')}.csv"
                    )
            except Exception as e:
                print(f"Erro ao exportar métricas: {e}")
        return None
    
    @app.callback(
        Output("download-workouts", "data"),
        Input("btn-export-workouts", "n_clicks"),
        prevent_initial_call=True
    )
    def export_workouts_csv(n_clicks):
        """Exporta atividades para CSV"""
        if n_clicks:
            try:
                import io
                import csv
                from modules.infra.cache_manager import get_cached
                
                workouts = get_cached('enriched_workouts', [])
                if workouts:
                    output = io.StringIO()
                    writer = csv.DictWriter(output, fieldnames=[
                        'date', 'type', 'duration', 'distance', 'tss', 'category'
                    ])
                    writer.writeheader()
                    for w in workouts[:100]:  # últimas 100 atividades
                        writer.writerow({
                            'date': w.get('startTimeLocal', ''),
                            'type': w.get('activityType', {}).get('typeKey', ''),
                            'duration': w.get('duration', 0),
                            'distance': w.get('distance', 0),
                            'tss': w.get('tss', 0),
                            'category': w.get('category', '')
                        })
                    
                    return dict(
                        content=output.getvalue(),
                        filename=f"workouts_{datetime.now().strftime('%Y%m%d')}.csv"
                    )
            except Exception as e:
                print(f"Erro ao exportar workouts: {e}")
        return None
