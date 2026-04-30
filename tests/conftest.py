"""Pytest configuration and fixtures."""
import pytest
import json
from pathlib import Path


@pytest.fixture
def sample_workout_cycling():
    """Sample cycling workout for testing."""
    return {
        'activityType': {'typeKey': 'cycling'},
        'duration': 3600,  # 1 hour in seconds
        'averagePower': 200,
        'normalizedPower': 210,
        'averageHR': 150,
    }


@pytest.fixture
def sample_workout_running():
    """Sample running workout for testing."""
    return {
        'activityType': {'typeKey': 'running'},
        'duration': 1800,  # 30 minutes
        'distance': 5000,  # 5km
        'averageSpeed': 2.78,  # m/s (~5:00/km)
        'averageHR': 160,
    }


@pytest.fixture
def sample_config():
    """Sample user configuration."""
    return {
        'ftp': 250,
        'threshold_pace_running': 300,  # 5:00/km in seconds
        'threshold_pace_swimming': 100,   # 1:40/100m in seconds
        'lthr': 170,
        'hr_max': 185,
        'hr_rest': 50,
    }


@pytest.fixture
def golden_masters_dir():
    """Path to golden masters directory."""
    return Path(__file__).parent / 'golden_masters'
