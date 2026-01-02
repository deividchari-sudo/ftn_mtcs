"""
Módulo enriquecido de integração Garmin com cache e tratamento de erros robusto.

Expõe métodos de saúde, training status, e exercícios com fallback gracioso.
"""
from garminconnect import Garmin
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List, Any
from cache_manager import get_or_fetch, invalidate_type

import logging

logger = logging.getLogger(__name__)


class GarminEnhanced:
    """Wrapper enriquecido do cliente Garmin com cache e novos endpoints"""
    
    def __init__(self, client: Garmin):
        self.client = client
    
    # ========== HEALTH METRICS (Saúde Avançada) ==========
    
    def get_heart_rate_variability(self, cdate: Optional[date] = None) -> Optional[Dict]:
        """Busca dados de Variabilidade de Frequência Cardíaca (HRV) para uma data"""
        if cdate is None:
            cdate = datetime.now().date()
        cache_key = f"hrv_{cdate}"
        return get_or_fetch(
            cache_key,
            'hrv_data',
            lambda: self._fetch_hrv(cdate)
        )
    
    def _fetch_hrv(self, cdate: date) -> Optional[Dict]:
        try:
            if hasattr(self.client, 'get_hrv_data'):
                return self.client.get_hrv_data(cdate.isoformat())
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar HRV: {e}")
            return None
    
    def get_vo2_max_estimate(self) -> Optional[float]:
        """Obtém estimativa de VO2 Máx do Garmin"""
        cache_key = "vo2_max_latest"
        return get_or_fetch(
            cache_key,
            'vo2_max',
            lambda: self._fetch_vo2_max()
        )
    
    def _fetch_vo2_max(self) -> Optional[float]:
        try:
            if hasattr(self.client, 'get_vo2_max'):
                data = self.client.get_vo2_max()
                if isinstance(data, dict):
                    return data.get('vo2Max') or data.get('vo2_max')
                return data
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar VO2Max: {e}")
            return None
    
    def get_stress_data(self, cdate: Optional[date] = None) -> Optional[Dict]:
        """Busca dados de nível de estresse para uma data"""
        if cdate is None:
            cdate = datetime.now().date()
        cache_key = f"stress_{cdate}"
        return get_or_fetch(
            cache_key,
            'stress_data',
            lambda: self._fetch_stress(cdate)
        )
    
    def _fetch_stress(self, cdate: date) -> Optional[Dict]:
        try:
            if hasattr(self.client, 'get_stress_data'):
                return self.client.get_stress_data(cdate.isoformat())
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar Stress: {e}")
            return None
    
    def get_sleep_data(self, cdate: Optional[date] = None) -> Optional[Dict]:
        """Busca dados de sono para uma data"""
        if cdate is None:
            cdate = datetime.now().date()
        cache_key = f"sleep_{cdate}"
        return get_or_fetch(
            cache_key,
            'sleep_data',
            lambda: self._fetch_sleep(cdate)
        )
    
    def _fetch_sleep(self, cdate: date) -> Optional[Dict]:
        try:
            if hasattr(self.client, 'get_sleep_data'):
                return self.client.get_sleep_data(cdate.isoformat())
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar Sleep: {e}")
            return None
    
    def get_body_composition(self) -> Optional[Dict]:
        """Busca dados de composição corporal (peso, % gordura, músculos)"""
        cache_key = "body_composition_latest"
        return get_or_fetch(
            cache_key,
            'body_composition',
            lambda: self._fetch_body_composition()
        )
    
    def _fetch_body_composition(self) -> Optional[Dict]:
        try:
            today = datetime.now().date().isoformat()
            if hasattr(self.client, 'get_body_composition'):
                return self.client.get_body_composition(today)
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar Body Composition: {e}")
            return None
    
    # ========== TRAINING STATUS & PERFORMANCE ==========
    
    def get_training_status(self, date_str: Optional[str] = None) -> Optional[Dict]:
        """Obtém status de treinamento (Overreach, High, Balanced, Low, Detraining)"""
        if date_str is None:
            date_str = datetime.now().date().isoformat()
        cache_key = f"training_status_{date_str}"
        return get_or_fetch(
            cache_key,
            'training_status',
            lambda: self._fetch_training_status(date_str)
        )
    
    def _fetch_training_status(self, date_str: str) -> Optional[Dict]:
        try:
            if hasattr(self.client, 'get_training_status'):
                return self.client.get_training_status(date_str)
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar Training Status: {e}")
            return None
    
    def get_daily_training_status(self, date_str: Optional[str] = None) -> Optional[Dict]:
        """Obtém status detalhado do dia"""
        if date_str is None:
            date_str = datetime.now().date().isoformat()
        cache_key = f"daily_training_{date_str}"
        return get_or_fetch(
            cache_key,
            'training_status',
            lambda: self._fetch_daily_training_status(date_str)
        )
    
    def _fetch_daily_training_status(self, date_str: str) -> Optional[Dict]:
        try:
            if hasattr(self.client, 'get_daily_training_status'):
                return self.client.get_daily_training_status(date_str)
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar Daily Training Status: {e}")
            return None
    
    def get_performance_metrics(self) -> Optional[Dict]:
        """Obtém métricas de performance agregadas"""
        cache_key = "performance_metrics_latest"
        return get_or_fetch(
            cache_key,
            'training_status',
            lambda: self._fetch_performance_metrics()
        )
    
    def _fetch_performance_metrics(self) -> Optional[Dict]:
        try:
            if hasattr(self.client, 'get_performance_metrics'):
                return self.client.get_performance_metrics()
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar Performance Metrics: {e}")
            return None
    
    # ========== EXERCÍCIOS & DETALHES DE WORKOUT ==========
    
    def get_workout_exercises(self, activity_id: str) -> Optional[Dict]:
        """Busca detalhes de exercícios (séries, reps, peso) para uma atividade"""
        cache_key = f"exercises_{activity_id}"
        return get_or_fetch(
            cache_key,
            'exercises',
            lambda: self._fetch_workout_exercises(activity_id)
        )
    
    def _fetch_workout_exercises(self, activity_id: str) -> Optional[Dict]:
        try:
            if hasattr(self.client, 'get_workout_details'):
                details = self.client.get_workout_details(activity_id)
                if isinstance(details, dict):
                    # Extrair apenas os exercícios
                    return {
                        'activity_id': activity_id,
                        'exercises': details.get('exercises', []),
                        'exercise_count': len(details.get('exercises', [])),
                        'total_reps': sum(
                            e.get('reps', 0) for e in details.get('exercises', [])
                        ),
                        'total_sets': sum(
                            e.get('sets', 0) for e in details.get('exercises', [])
                        )
                    }
            return None
        except Exception as e:
            logger.warning(f"Erro ao buscar Workout Details {activity_id}: {e}")
            return None
    
    def get_all_exercises_range(
        self,
        start_date: date,
        end_date: date,
        activity_list: List[Dict]
    ) -> Dict[str, Dict]:
        """
        Busca exercícios para todas as atividades de força em um período.
        
        Args:
            start_date, end_date: Período
            activity_list: Lista de atividades do Garmin
        
        Returns:
            {activity_id: {...exercicio_details...}}
        """
        all_exercises = {}
        
        # Filtrar apenas atividades de força
        strength_activities = [
            a for a in activity_list
            if a.get('activityType', {}).get('typeKey', '').lower() in [
                'strength_training', 'weight_training', 'functional_strength_training',
                'gym_strength_training', 'crossfit', 'hiit'
            ]
        ]
        
        for activity in strength_activities:
            activity_id = activity.get('activityId') or activity.get('activityUUID')
            if activity_id:
                exercises = self.get_workout_exercises(activity_id)
                if exercises:
                    all_exercises[activity_id] = exercises
        
        return all_exercises
    
    # ========== UTILITÁRIOS ==========
    
    def invalidate_all_caches(self):
        """Limpa todos os caches de saúde/training/exercícios"""
        invalidate_type('health_metrics')
        invalidate_type('training_status')
        invalidate_type('exercises')
        invalidate_type('vo2_max')
        invalidate_type('body_composition')
        invalidate_type('sleep_data')
        invalidate_type('stress_data')
        invalidate_type('hrv_data')
