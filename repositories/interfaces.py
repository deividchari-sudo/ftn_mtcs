"""
Interfaces (Ports) para repositories.

Define contratos que todas as implementações de repository devem seguir.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime


class WorkoutRepositoryInterface(ABC):
    """Interface para persistência de workouts."""
    
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os workouts."""
        pass
    
    @abstractmethod
    def get_by_id(self, workout_id: str) -> Optional[Dict[str, Any]]:
        """Retorna workout por ID."""
        pass
    
    @abstractmethod
    def save(self, workout: Dict[str, Any]) -> None:
        """Salva um workout."""
        pass
    
    @abstractmethod
    def save_many(self, workouts: List[Dict[str, Any]]) -> None:
        """Salva múltiplos workouts."""
        pass
    
    @abstractmethod
    def delete(self, workout_id: str) -> bool:
        """Remove um workout. Retorna True se encontrado."""
        pass
    
    @abstractmethod
    def get_by_date_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[Dict[str, Any]]:
        """Retorna workouts em um intervalo de datas."""
        pass


class MetricsRepositoryInterface(ABC):
    """Interface para persistência de métricas."""
    
    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todas as métricas."""
        pass
    
    @abstractmethod
    def get_latest(self, n: int = 1) -> List[Dict[str, Any]]:
        """Retorna as n métricas mais recentes."""
        pass
    
    @abstractmethod
    def save(self, metrics: Dict[str, Any]) -> None:
        """Salva métricas."""
        pass
    
    @abstractmethod
    def save_many(self, metrics_list: List[Dict[str, Any]]) -> None:
        """Salva múltiplas métricas."""
        pass


class ConfigRepositoryInterface(ABC):
    """Interface para persistência de configurações."""
    
    @abstractmethod
    def load(self) -> Dict[str, Any]:
        """Carrega configurações."""
        pass
    
    @abstractmethod
    def save(self, config: Dict[str, Any]) -> None:
        """Salva configurações."""
        pass
