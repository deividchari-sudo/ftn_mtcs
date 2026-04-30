"""
Service de cálculos - orquestra operações de fitness metrics.

Este service atua como facade para as operações de domínio,
simplificando a interface para a camada de apresentação.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from domain.models import Activity, UserConfig, FitnessMetrics, TSSResult
from domain.calculations import (
    calculate_tss_for_activity,
    calculate_fitness_metrics,
    parse_activity_from_dict,
)


class CalculationsService:
    """
    Service para operações de cálculo de fitness.
    
    Responsabilidades:
    - Orquestrar cálculo de TSS para múltiplas atividades
    - Calcular métricas de fitness (CTL, ATL, TSB)
    - Converter dados brutos em objetos de domínio
    """
    
    def __init__(self, user_config: UserConfig):
        """
        Inicializa o service com configurações do usuário.
        
        Args:
            user_config: Configurações (FTP, thresholds, etc)
        """
        self._config = user_config
    
    def calculate_tss(
        self,
        activity_data: Dict[str, Any]
    ) -> TSSResult:
        """
        Calcula TSS para uma atividade a partir de dados brutos.
        
        Args:
            activity_data: Dicionário com dados da atividade
        
        Returns:
            TSSResult com valor e metadados
        """
        activity = parse_activity_from_dict(activity_data)
        return calculate_tss_for_activity(activity, self._config)
    
    def calculate_batch_tss(
        self,
        activities_data: List[Dict[str, Any]]
    ) -> List[TSSResult]:
        """
        Calcula TSS para múltiplas atividades.
        
        Args:
            activities_data: Lista de dicionários de atividades
        
        Returns:
            Lista de TSSResult
        """
        results = []
        for activity_data in activities_data:
            result = self.calculate_tss(activity_data)
            results.append(result)
        return results
    
    def calculate_fitness_trends(
        self,
        daily_tss: List[tuple[datetime, float]]
    ) -> List[FitnessMetrics]:
        """
        Calcula tendências de fitness a partir de TSS diário.
        
        Args:
            daily_tss: Lista de (data, tss) ordenada
        
        Returns:
            Lista de FitnessMetrics
        """
        return calculate_fitness_metrics(daily_tss)
    
    def enrich_workouts_with_tss(
        self,
        workouts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Enriquece workouts com TSS calculado.
        
        Args:
            workouts: Lista de workouts brutos
        
        Returns:
            Workouts enriquecidos com 'tss' e 'tss_type'
        """
        enriched = []
        for workout in workouts:
            workout_copy = dict(workout)
            
            # Remover TSS antigo se existir
            if 'tss' in workout_copy:
                del workout_copy['tss']
            
            # Calcular TSS novo
            tss_result = self.calculate_tss(workout_copy)
            
            workout_copy['tss'] = tss_result.value
            workout_copy['tss_type'] = tss_result.type.value
            workout_copy['intensity_factor'] = tss_result.intensity_factor
            
            enriched.append(workout_copy)
        
        return enriched
    
    def get_user_config(self) -> UserConfig:
        """Retorna configuração atual do usuário."""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """
        Atualiza configurações do usuário.
        
        Args:
            **kwargs: Campos a atualizar (ftp, lthr, etc)
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
