from __future__ import annotations

from pydantic import BaseModel


class InstanceCreate(BaseModel):
    name: str
    group_name: str = "default"
    template_path: str
    target_root: str


class InstanceClone(BaseModel):
    source_id: int
    new_name: str
    group_name: str = "default"
    target_root: str
    keep_only_mql_assets: bool = True


class InstanceRename(BaseModel):
    name: str


class NotesUpdate(BaseModel):
    notes: str


class GroupUpdate(BaseModel):
    group_name: str


class DiscoverRequest(BaseModel):
    root_path: str
    group_name: str = "default"
    max_depth: int = 4


class DistributeRequest(BaseModel):
    file_path: str
    target_type: str  # experts | indicators
    instance_ids: list[int] | None = None
    group_name: str | None = None
    all_instances: bool = False


class SymlinkRequest(BaseModel):
    master_experts_path: str
    master_indicators_path: str
    instance_ids: list[int] | None = None
    all_instances: bool = True


class StatusReport(BaseModel):
    instance_id: int
    running: bool
    account_id: str = ""
    account_balance: float = 0.0
    equity: float = 0.0
    ea_status: str = "unknown"


class BacktestUpload(BaseModel):
    instance_id: int | None = None
    strategy_name: str
    symbol: str
    timeframe: str
    net_profit: float
    drawdown: float
    profit_factor: float
    payload_json: str = "{}"


class VersionCreate(BaseModel):
    version: str
    title: str
    content: str
