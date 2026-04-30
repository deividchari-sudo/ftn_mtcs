"""
Callbacks for calendar functionality.

Handles: Month navigation, calendar rendering
"""
import dash
from dash import Output, Input, html
from datetime import datetime


def register_calendar_callbacks(app):
    """Register all calendar-related callbacks."""
    
    @app.callback(
        Output("calendar-month-store", "data"),
        Input("btn-calendar-prev-month", "n_clicks"),
        Input("btn-calendar-next-month", "n_clicks"),
        dash.State("calendar-month-store", "data")
    )
    def navigate_calendar(prev_clicks, next_clicks, current_data):
        """Navega entre meses do calendário"""
        if not current_data:
            now = datetime.now()
            current_data = {"year": now.year, "month": now.month}
        
        year = current_data.get("year", datetime.now().year)
        month = current_data.get("month", datetime.now().month)
        
        ctx = dash.callback_context
        if not ctx.triggered:
            return current_data
        
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if button_id == "btn-calendar-prev-month":
            month -= 1
            if month < 1:
                month = 12
                year -= 1
        elif button_id == "btn-calendar-next-month":
            month += 1
            if month > 12:
                month = 1
                year += 1
        
        return {"year": year, "month": month}
    
    @app.callback(
        Output("calendar-month-content", "children"),
        Input("calendar-month-store", "data"),
    )
    def render_calendar(month_data):
        """Renderiza o calendário mensal"""
        if not month_data:
            return html.Div("Selecione um mês")
        
        # Aqui viria a lógica de renderização do calendário
        # Por enquanto, retornamos um placeholder
        return html.Div(f"Calendário: {month_data['month']}/{month_data['year']}")
