"""
Factory para criação de repositories.

Facilita a criação de repositories com as dependências corretas.
"""
from pathlib import Path
from typing import Union

from repositories.interfaces import (
    WorkoutRepositoryInterface,
    MetricsRepositoryInterface,
    ConfigRepositoryInterface,
)
from repositories.json_repositories import (
    JsonWorkoutRepository,
    JsonMetricsRepository,
    JsonConfigRepository,
)


def create_workout_repository(
    file_path: Union[str, Path] = None
) -> WorkoutRepositoryInterface:
    """
    Factory para criar repository de workouts.
    
    Args:
        file_path: Caminho para arquivo JSON. Se None, usa default.
    
    Returns:
        WorkoutRepositoryInterface
    """
    if file_path is None:
        # Default path (compatível com storage.py)
        from pathlib import Path
        file_path = Path.home() / ".fitness_metrics" / "workouts_42_dias.json"
    
    return JsonWorkoutRepository(Path(file_path))


def create_metrics_repository(
    file_path: Union[str, Path] = None
) -> MetricsRepositoryInterface:
    """
    Factory para criar repository de métricas.
    
    Args:
        file_path: Caminho para arquivo JSON. Se None, usa default.
    
    Returns:
        MetricsRepositoryInterface
    """
    if file_path is None:
        from pathlib import Path
        file_path = Path.home() / ".fitness_metrics" / "fitness_metrics.json"
    
    return JsonMetricsRepository(Path(file_path))


def create_config_repository(
    file_path: Union[str, Path] = None
) -> ConfigRepositoryInterface:
    """
    Factory para criar repository de configurações.
    
    Args:
        file_path: Caminho para arquivo JSON. Se None, usa default.
    
    Returns:
        ConfigRepositoryInterface
    """
    if file_path is None:
        from pathlib import Path
        file_path = Path.home() / ".fitness_metrics" / "user_config.json"
    
    return JsonConfigRepository(Path(file_path))
