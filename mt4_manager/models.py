from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class MT4Instance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    group_name: str = Field(default="default", index=True)
    base_path: str
    terminal_path: str
    experts_path: str
    indicators_path: str
    notes: str = ""
    running: bool = False
    account_id: str = ""
    account_balance: float = 0.0
    equity: float = 0.0
    ea_status: str = "unknown"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OperationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    action: str
    target: str
    detail: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class VersionRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    version: str
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class BacktestReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    instance_id: Optional[int] = Field(default=None, index=True)
    strategy_name: str
    symbol: str
    timeframe: str
    net_profit: float
    drawdown: float
    profit_factor: float
    payload_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class CloudSyncEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str
    payload_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
