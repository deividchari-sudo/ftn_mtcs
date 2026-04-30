"""
Callbacks for AI chat functionality.

Handles: Send message, chat history
"""
import dash
from dash import Output, Input, State, html


def register_chat_callbacks(app):
    """Register all chat-related callbacks."""
    
    @app.callback(
        [Output("chat-history", "children"),
         Output("chat-input", "value")],
        [Input("send-chat-btn", "n_clicks"),
         Input("chat-input", "n_submit")],
        [State("chat-input", "value"),
         State("chat-history", "children")],
        prevent_initial_call=True
    )
    def handle_chat(send_clicks, n_submit, input_value, chat_history):
        """Processa mensagem do chat"""
        if not input_value:
            return chat_history, ""
        
        try:
            from modules.services.ai_chat import FitnessAI
            
            # Adiciona mensagem do usuário
            user_msg = html.Div([
                html.Strong("Você: "),
                input_value
            ], className="chat-user-message mb-2")
            
            # Obtém resposta da IA
            ai = FitnessAI()
            response = ai.ask(input_value)
            
            ai_msg = html.Div([
                html.Strong("🤖 IA: "),
                response
            ], className="chat-ai-message mb-3")
            
            # Atualiza histórico
            if chat_history is None:
                chat_history = []
            
            new_history = chat_history + [user_msg, ai_msg]
            
            return new_history, ""  # Limpa input
            
        except Exception as e:
            error_msg = html.Div(f"❌ Erro: {str(e)}", className="alert alert-danger")
            if chat_history is None:
                chat_history = []
            return chat_history + [error_msg], input_value
