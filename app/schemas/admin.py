from pydantic import BaseModel
from typing import List
from datetime import datetime

class AdminUserResponse(BaseModel):
    id: str
    name: str
    email: str
    plan: str
    status: str
    joinDate: str
    documentsGenerated: int
    classesCount: int

class ChartDataPoint(BaseModel):
    name: str
    revenue: float
    users: int

class AdminMetricsResponse(BaseModel):
    totalUsers: int
    activeUsers: int
    mrr: float
    totalCreditsUsed: int
    churnRate: float
    chartData: List[ChartDataPoint]

class TransactionResponse(BaseModel):
    id: str
    userId: str
    userName: str
    amount: float
    date: str
    status: str
    plan: str
