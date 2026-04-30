"""
Implementações de repositories usando JSON files.

Esta implementação mantém compatibilidade com o storage.py existente,
mas adiciona uma camada de abstração para facilitar futura migração.
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from repositories.interfaces import (
    WorkoutRepositoryInterface,
    MetricsRepositoryInterface,
    ConfigRepositoryInterface,
)


class JsonWorkoutRepository(WorkoutRepositoryInterface):
    """
    Repository de workouts usando JSON file.
    
    Compatível com formato existente em storage.py
    """
    
    def __init__(self, file_path: Path):
        """
        Inicializa o repository.
        
        Args:
            file_path: Caminho para o arquivo JSON de workouts
        """
        self._file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Garante que o arquivo existe."""
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_data([])
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Carrega dados do arquivo."""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Salva dados no arquivo."""
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todos os workouts."""
        return self._load_data()
    
    def get_by_id(self, workout_id: str) -> Optional[Dict[str, Any]]:
        """Retorna workout por ID."""
        workouts = self._load_data()
        for workout in workouts:
            wid = str(workout.get('activityId', workout.get('id', '')))
            if wid == workout_id:
                return workout
        return None
    
    def save(self, workout: Dict[str, Any]) -> None:
        """Salva um workout (atualiza se existir)."""
        workouts = self._load_data()
        workout_id = str(workout.get('activityId', workout.get('id', '')))
        
        # Procura e atualiza se existir
        for i, existing in enumerate(workouts):
            existing_id = str(existing.get('activityId', existing.get('id', '')))
            if existing_id == workout_id:
                workouts[i] = workout
                break
        else:
            # Não encontrado, adiciona
            workouts.append(workout)
        
        self._save_data(workouts)
    
    def save_many(self, workouts: List[Dict[str, Any]]) -> None:
        """Salva múltiplos workouts."""
        for workout in workouts:
            self.save(workout)
    
    def delete(self, workout_id: str) -> bool:
        """Remove um workout."""
        workouts = self._load_data()
        original_len = len(workouts)
        
        workouts = [
            w for w in workouts
            if str(w.get('activityId', w.get('id', ''))) != workout_id
        ]
        
        if len(workouts) < original_len:
            self._save_data(workouts)
            return True
        return False
    
    def get_by_date_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[Dict[str, Any]]:
        """Retorna workouts em um intervalo de datas."""
        workouts = self._load_data()
        result = []
        
        for workout in workouts:
            start_time_str = workout.get('startTimeLocal', workout.get('startTime'))
            if not start_time_str:
                continue
            
            try:
                # Parse da data
                if isinstance(start_time_str, str):
                    if 'T' in start_time_str:
                        workout_date = datetime.fromisoformat(start_time_str.replace('Z', '+00:00').replace('T', ' ').split('+')[0])
                    else:
                        workout_date = datetime.strptime(start_time_str.split()[0], '%Y-%m-%d')
                else:
                    continue
                
                if start <= workout_date <= end:
                    result.append(workout)
            except (ValueError, TypeError):
                continue
        
        return result


class JsonMetricsRepository(MetricsRepositoryInterface):
    """
    Repository de métricas usando JSON file.
    """
    
    def __init__(self, file_path: Path):
        """
        Inicializa o repository.
        
        Args:
            file_path: Caminho para o arquivo JSON de métricas
        """
        self._file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Garante que o arquivo existe."""
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_data([])
    
    def _load_data(self) -> List[Dict[str, Any]]:
        """Carrega dados do arquivo."""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Salva dados no arquivo."""
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Retorna todas as métricas."""
        return self._load_data()
    
    def get_latest(self, n: int = 1) -> List[Dict[str, Any]]:
        """Retorna as n métricas mais recentes."""
        metrics = self._load_data()
        
        # Ordena por data se disponível
        try:
            metrics.sort(
                key=lambda x: x.get('date', ''),
                reverse=True
            )
        except:
            pass
        
        return metrics[:n]
    
    def save(self, metrics: Dict[str, Any]) -> None:
        """Salva métricas."""
        data = self._load_data()
        
        # Adiciona timestamp se não tiver
        if 'date' not in metrics:
            metrics['date'] = datetime.now().isoformat()
        
        data.append(metrics)
        self._save_data(data)
    
    def save_many(self, metrics_list: List[Dict[str, Any]]) -> None:
        """Salva múltiplas métricas."""
        for metrics in metrics_list:
            self.save(metrics)


class JsonConfigRepository(ConfigRepositoryInterface):
    """
    Repository de configurações usando JSON file.
    """
    
    def __init__(self, file_path: Path):
        """
        Inicializa o repository.
        
        Args:
            file_path: Caminho para o arquivo JSON de configurações
        """
        self._file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Garante que o arquivo existe."""
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_data({})
    
    def _load_data(self) -> Dict[str, Any]:
        """Carrega dados do arquivo."""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """Salva dados no arquivo."""
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load(self) -> Dict[str, Any]:
        """Carrega configurações."""
        return self._load_data()
    
    def save(self, config: Dict[str, Any]) -> None:
        """Salva configurações."""
        self._save_data(config)
