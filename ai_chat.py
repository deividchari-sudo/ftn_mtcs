"""
Assistente de IA para o Fitness Metrics Dashboard
Usa Groq (gratuito) para responder perguntas sobre os dados de treinamento
"""
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
from langchain_groq import ChatGroq
from config import GROQ_API_KEY

class FitnessAI:
    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY não encontrada. Configure no arquivo .env")

        # Inicializar Groq
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant",  # Modelo gratuito atual da Groq
            temperature=0.3,
            max_tokens=1024,
            api_key=GROQ_API_KEY
        )

    def answer_question(self, question: str, metrics: List[Dict], workouts: List[Dict], config: Dict) -> str:
        """Responde perguntas sobre os dados de fitness usando IA"""
        try:
            # Preparar dados do usuário
            user_data = self.prepare_user_data(metrics, workouts, config)
            
            # Criar prompt
            prompt = f"""
Você é um treinador especialista em triathlon, com formação em fisiologia do exercício e ciência do treinamento esportivo.
Como coach certificado em triathlon, você analisa dados usando métodos científicos baseados em periodização, treinamento cruzado e adaptações fisiológicas específicas das três modalidades: natação, ciclismo e corrida.

DADOS DO ATLETA DE TRIATHLON:
{user_data}

PERGUNTA DO ATLETA: {question}

INSTRUÇÕES PARA ANÁLISE CIENTÍFICA:
- Use conhecimento de periodização de treinamento (preparação geral, específica, competição, transição)
- Considere adaptações fisiológicas específicas de cada modalidade (VO2max, limiar anaeróbico, economia de movimento)
- Analise o equilíbrio entre volume e intensidade baseado em princípios científicos
- Considere fadiga neuromuscular, inflamação e recuperação específica do triathlon
- Use dados de CTL/ATL/TSB com interpretação específica para treinamento cruzado
- Forneça recomendações baseadas em evidências científicas quando apropriado
- Mantenha linguagem técnica acessível mas precisa
- Foque em estratégias de treinamento integradas para as três modalidades

RESPOSTA PROFISSIONAL:
"""
            
            # Fazer chamada para a IA
            response = self.llm.invoke(prompt)
            
            return response.content.strip()
            
        except Exception as e:
            return f"Desculpe, ocorreu um erro ao processar sua pergunta: {str(e)}"

    def prepare_user_data(self, metrics: List[Dict], workouts: List[Dict], config: Dict) -> str:
        """Prepara um resumo dos dados do atleta de triathlon para análise científica"""
        try:
            if not metrics:
                return "Nenhum dado de métricas encontrado."

            # Dados básicos
            last_metric = metrics[-1]
            total_workouts = len(workouts) if workouts else 0

            # Estatísticas recentes (últimos 7 dias)
            recent_metrics = metrics[-7:] if len(metrics) >= 7 else metrics
            avg_ctl = sum(m['ctl'] for m in recent_metrics) / len(recent_metrics)
            avg_atl = sum(m['atl'] for m in recent_metrics) / len(recent_metrics)
            avg_tsb = sum(m['tsb'] for m in recent_metrics) / len(recent_metrics)

            # Análise por modalidade de triathlon
            modality_stats = self._analyze_triathlon_modalities(workouts)

            # Estatísticas gerais
            total_tss = sum(float(w.get('tss', 0) or 0) for w in workouts) if workouts else 0
            total_duration = sum(float(w.get('duration', 0) or 0) for w in workouts) if workouts else 0
            total_distance = sum(float(w.get('distance', 0) or 0) for w in workouts) if workouts else 0

            # Metas específicas para triathlon
            ctl_target = config.get('ctl_target', 60)  # Meta mais alta para triathlon
            atl_max = config.get('atl_max', 100)   # Limite mais alto para triathlon

            # Calcular proporção de treinamento por modalidade
            swim_pct = modality_stats['swimming']['percentage']
            bike_pct = modality_stats['cycling']['percentage']
            run_pct = modality_stats['running']['percentage']

            summary = f"""
🏊‍♂️ **PERFIL DO ATLETA DE TRIATHLON**

📊 **MÉTRICAS DE FORMA FÍSICA (mais recente):**
- CTL (Fitness Crônico): {last_metric['ctl']:.1f} pts (meta: {ctl_target})
- ATL (Fadiga Aguda): {last_metric['atl']:.1f} pts (máximo: {atl_max})
- TSB (Equilíbrio): {last_metric['tsb']:.1f} pts
- Data: {last_metric['date']}

📈 **TENDÊNCIAS DOS ÚLTIMOS 7 DIAS:**
- CTL médio: {avg_ctl:.1f} (tendência: {'crescente' if avg_ctl > last_metric['ctl'] * 0.95 else 'estável'})
- ATL médio: {avg_atl:.1f} (fadiga: {'alta' if avg_atl > 70 else 'moderada' if avg_atl > 50 else 'baixa'})
- TSB médio: {avg_tsb:.1f} (recuperação: {'boa' if avg_tsb > 5 else 'regular' if avg_tsb > -10 else 'precária'})

🏊‍♂️ **DISTRIBUIÇÃO POR MODALIDADE (42 dias):**
- 🏊 Natação: {swim_pct:.1f}% do volume ({modality_stats['swimming']['hours']:.1f}h, {modality_stats['swimming']['sessions']} sessões)
- 🚴 Ciclismo: {bike_pct:.1f}% do volume ({modality_stats['cycling']['hours']:.1f}h, {modality_stats['cycling']['sessions']} sessões)
- 🏃 Corrida: {run_pct:.1f}% do volume ({modality_stats['running']['hours']:.1f}h, {modality_stats['running']['sessions']} sessões)

📊 **ESTATÍSTICAS GERAIS:**
- Total de treinos: {total_workouts}
- TSS total acumulado: {total_tss:.0f} (intensidade média: {total_tss/total_workouts:.1f} por sessão)
- Tempo total de treino: {total_duration/3600:.1f} horas
- Distância total: {total_distance/1000:.1f} km

🎯 **METAS DE PERFORMANCE:**
- CTL alvo: {ctl_target} pts (fitness para competições)
- ATL máximo: {atl_max} pts (limite de fadiga)
- Frequência ideal: 8-12 sessões/semana
- Período de adaptação: 6-8 semanas por macrociclo

⚠️ **ANÁLISE DE RISCO:**
- Risco de overtraining: {'Alto' if last_metric['atl'] > 80 else 'Moderado' if last_metric['atl'] > 60 else 'Baixo'}
- Necessidade de recuperação: {'Urgente' if last_metric['tsb'] < -20 else 'Recomendada' if last_metric['tsb'] < -10 else 'Opcional'}
"""

            return summary.strip()

        except Exception as e:
            return f"Erro ao preparar dados: {str(e)}"

    def _analyze_triathlon_modalities(self, workouts: List[Dict]) -> Dict:
        """Analisa distribuição de treinamento por modalidade de triathlon"""
        if not workouts:
            return {
                'swimming': {'hours': 0, 'sessions': 0, 'percentage': 0},
                'cycling': {'hours': 0, 'sessions': 0, 'percentage': 0},
                'running': {'hours': 0, 'sessions': 0, 'percentage': 0}
            }

        modality_data = {
            'swimming': {'hours': 0, 'sessions': 0},
            'cycling': {'hours': 0, 'sessions': 0},
            'running': {'hours': 0, 'sessions': 0}
        }

        for workout in workouts:
            try:
                activity_type = workout.get('activityType', {}).get('typeKey', '').lower()
                duration_hours = float(workout.get('duration', 0) or 0) / 3600

                # Categorização específica para triathlon
                if any(keyword in activity_type for keyword in ['swimming', 'pool_swimming', 'open_water_swimming']):
                    modality_data['swimming']['hours'] += duration_hours
                    modality_data['swimming']['sessions'] += 1
                elif any(keyword in activity_type for keyword in ['cycling', 'biking', 'road_cycling', 'mountain_biking']):
                    modality_data['cycling']['hours'] += duration_hours
                    modality_data['cycling']['sessions'] += 1
                elif any(keyword in activity_type for keyword in ['running', 'treadmill_running', 'track_running']):
                    modality_data['running']['hours'] += duration_hours
                    modality_data['running']['sessions'] += 1

            except Exception:
                continue

        # Calcular percentuais
        total_hours = sum(mod['hours'] for mod in modality_data.values())

        for modality in modality_data:
            if total_hours > 0:
                modality_data[modality]['percentage'] = (modality_data[modality]['hours'] / total_hours) * 100
            else:
                modality_data[modality]['percentage'] = 0

        return modality_data