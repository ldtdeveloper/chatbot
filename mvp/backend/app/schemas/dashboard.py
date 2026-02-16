"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.assistant_config import NoiseReductionMode


# Dashboard Statistics schemas
class KeyStatItem(BaseModel):
    key_id: int
    key_name: str
    value: float

class ChartDataPoint(BaseModel):
    date: str
    data: dict  # Dynamic keys based on API key names

class DashboardStats(BaseModel):
    # Summary cards
    total_interactions: int
    total_minutes: int
    total_expense: Optional[int] = None
    total_agents: int
    active_keys: int
    
    # Superadmin only - Total Charging and Profit
    total_charging: Optional[float] = None  # Sum of total_cost (estimated_cost + 10%)
    profit: Optional[float] = None  # Sum of (total_cost - estimated_cost)
    charging_change: Optional[float] = None  # Percentage change from previous period
    
    # Percentage changes from previous period
    interactions_change: float
    expenses_change: float
    minutes_change: int = 0
    
    # Chart data
    interactions_chart: List[dict]  # [{date, key1_count, key2_count, ...}]
    # minutes_chart: List[dict]
    expenses_chart: List[dict]  # [{date, key1_cost, key2_cost, ...}]
    agents_per_key: List[dict]  # [{name, value, color}]
    
    # Available keys for filter dropdown
    available_keys: List[dict]  # [{id, name}]