from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .core import (
    append_log,
    clone_instance_folder,
    compile_mq4,
    create_instance_from_template,
    distribute_file,
    ensure_mt4_layout,
    launch_instance,
    select_instances,
    setup_symlinks,
)
from .db import get_session, init_db
from .models import BacktestReport, CloudSyncEvent, MT4Instance, OperationLog, VersionRecord
from .schemas import (
    BacktestUpload,
    DistributeRequest,
    GroupUpdate,
    InstanceClone,
    InstanceCreate,
    InstanceRename,
    NotesUpdate,
    StatusReport,
    SymlinkRequest,
    VersionCreate,
)

app = FastAPI(title="MT4 多开管理工具", version="0.1.0")
app.mount("/static", StaticFiles(directory="mt4_manager/static"), name="static")
templates = Jinja2Templates(directory="mt4_manager/templates")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    instances = list(session.exec(select(MT4Instance).order_by(MT4Instance.id.desc())))
    logs = list(session.exec(select(OperationLog).order_by(OperationLog.id.desc()).limit(50)))
    versions = list(session.exec(select(VersionRecord).order_by(VersionRecord.created_at.desc()).limit(20)))
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "instances": instances,
            "logs": logs,
            "versions": versions,
        },
    )


@app.post("/api/instances")
def create_instance(payload: InstanceCreate, session: Session = Depends(get_session)):
    target_dir = create_instance_from_template(payload.name, payload.group_name, Path(payload.template_path), Path(payload.target_root))
    terminal, experts, indicators = ensure_mt4_layout(target_dir)
    ins = MT4Instance(
        name=payload.name,
        group_name=payload.group_name,
        base_path=str(target_dir),
        terminal_path=str(terminal),
        experts_path=str(experts),
        indicators_path=str(indicators),
    )
    session.add(ins)
    session.commit()
    session.refresh(ins)
    append_log(session, "create_instance", ins.name, {"id": ins.id, "path": str(target_dir)})
    return ins


@app.post("/api/instances/clone")
def clone_instance(payload: InstanceClone, session: Session = Depends(get_session)):
    source = session.get(MT4Instance, payload.source_id)
    if not source:
        raise HTTPException(404, "source instance not found")
    target_dir = Path(payload.target_root) / payload.new_name
    clone_instance_folder(Path(source.base_path), target_dir, payload.keep_only_mql_assets)
    terminal, experts, indicators = ensure_mt4_layout(target_dir)
    ins = MT4Instance(
        name=payload.new_name,
        group_name=payload.group_name,
        base_path=str(target_dir),
        terminal_path=str(terminal),
        experts_path=str(experts),
        indicators_path=str(indicators),
    )
    session.add(ins)
    session.commit()
    session.refresh(ins)
    append_log(session, "clone_instance", ins.name, {"from": source.id, "id": ins.id})
    return ins


@app.get("/api/instances")
def list_instances(session: Session = Depends(get_session)):
    return list(session.exec(select(MT4Instance)))


@app.patch("/api/instances/{instance_id}/rename")
def rename_instance(instance_id: int, payload: InstanceRename, session: Session = Depends(get_session)):
    ins = session.get(MT4Instance, instance_id)
    if not ins:
        raise HTTPException(404, "instance not found")
    ins.name = payload.name
    ins.updated_at = datetime.utcnow()
    session.add(ins)
    session.commit()
    append_log(session, "rename_instance", payload.name, {"id": ins.id})
    return ins


@app.patch("/api/instances/{instance_id}/group")
def update_group(instance_id: int, payload: GroupUpdate, session: Session = Depends(get_session)):
    ins = session.get(MT4Instance, instance_id)
    if not ins:
        raise HTTPException(404, "instance not found")
    ins.group_name = payload.group_name
    ins.updated_at = datetime.utcnow()
    session.add(ins)
    session.commit()
    append_log(session, "update_group", ins.name, {"group": payload.group_name})
    return ins


@app.patch("/api/instances/{instance_id}/notes")
def update_notes(instance_id: int, payload: NotesUpdate, session: Session = Depends(get_session)):
    ins = session.get(MT4Instance, instance_id)
    if not ins:
        raise HTTPException(404, "instance not found")
    ins.notes = payload.notes
    ins.updated_at = datetime.utcnow()
    session.add(ins)
    session.commit()
    session.add(CloudSyncEvent(event_type="notes_update", payload_json=json.dumps({"instance_id": instance_id, "notes": payload.notes})))
    session.commit()
    append_log(session, "update_notes", ins.name, {"chars": len(payload.notes)})
    return ins


@app.post("/api/distribute")
def distribute(payload: DistributeRequest, session: Session = Depends(get_session)):
    selected = select_instances(session, payload.instance_ids, payload.group_name, payload.all_instances)
    if not selected:
        raise HTTPException(400, "no target instances selected")
    results = distribute_file(selected, Path(payload.file_path), payload.target_type)
    append_log(session, "distribute_file", payload.file_path, {"targets": len(results), "type": payload.target_type})
    return {"results": results}


@app.post("/api/symlink")
def symlink(payload: SymlinkRequest, session: Session = Depends(get_session)):
    selected = select_instances(session, payload.instance_ids, None, payload.all_instances)
    if not selected:
        raise HTTPException(400, "no target instances selected")
    results = setup_symlinks(selected, Path(payload.master_experts_path), Path(payload.master_indicators_path))
    append_log(session, "setup_symlink", "bulk", {"targets": len(results)})
    return {"results": results}


@app.post("/api/instances/{instance_id}/launch")
def launch(instance_id: int, session: Session = Depends(get_session)):
    ins = session.get(MT4Instance, instance_id)
    if not ins:
        raise HTTPException(404, "instance not found")
    res = launch_instance(ins)
    if res["ok"]:
        ins.running = True
        session.add(ins)
        session.commit()
        append_log(session, "launch_instance", ins.name, res)
    return res


@app.post("/api/launch")
def launch_bulk(group_name: str | None = None, session: Session = Depends(get_session)):
    selected = select_instances(session, None, group_name, group_name is None)
    results = []
    for ins in selected:
        res = launch_instance(ins)
        if res["ok"]:
            ins.running = True
            session.add(ins)
        results.append({"id": ins.id, "name": ins.name, **res})
    session.commit()
    append_log(session, "launch_bulk", group_name or "all", {"count": len(results)})
    return {"results": results}


@app.post("/api/compile/{instance_id}")
def compile_for_instance(instance_id: int, mq4_filename: str, session: Session = Depends(get_session)):
    ins = session.get(MT4Instance, instance_id)
    if not ins:
        raise HTTPException(404, "instance not found")
    result = compile_mq4(ins, mq4_filename)
    append_log(session, "compile_mq4", ins.name, result)
    return result


@app.post("/api/report/status")
def report_status(payload: StatusReport, session: Session = Depends(get_session)):
    ins = session.get(MT4Instance, payload.instance_id)
    if not ins:
        raise HTTPException(404, "instance not found")
    ins.running = payload.running
    ins.account_id = payload.account_id
    ins.account_balance = payload.account_balance
    ins.equity = payload.equity
    ins.ea_status = payload.ea_status
    ins.updated_at = datetime.utcnow()
    session.add(ins)
    session.commit()
    session.add(CloudSyncEvent(event_type="status_update", payload_json=payload.model_dump_json()))
    session.commit()
    return {"ok": True}


@app.post("/api/backtests")
def upload_backtest(payload: BacktestUpload, session: Session = Depends(get_session)):
    rec = BacktestReport(**payload.model_dump())
    session.add(rec)
    session.commit()
    session.refresh(rec)
    append_log(session, "upload_backtest", payload.strategy_name, {"id": rec.id})
    return rec


@app.get("/api/backtests/compare")
def compare_backtests(strategy_name: str, session: Session = Depends(get_session)):
    rows = list(session.exec(select(BacktestReport).where(BacktestReport.strategy_name == strategy_name)))
    rows_sorted = sorted(rows, key=lambda x: x.net_profit, reverse=True)
    return {
        "strategy_name": strategy_name,
        "count": len(rows_sorted),
        "best": rows_sorted[0] if rows_sorted else None,
        "items": rows_sorted,
    }


@app.post("/api/versions")
def add_version(payload: VersionCreate, session: Session = Depends(get_session)):
    rec = VersionRecord(**payload.model_dump())
    session.add(rec)
    session.commit()
    session.refresh(rec)
    append_log(session, "add_version", payload.version, {"title": payload.title})
    return rec


@app.get("/api/versions")
def list_versions(session: Session = Depends(get_session)):
    return list(session.exec(select(VersionRecord).order_by(VersionRecord.created_at.desc())))


@app.get("/api/logs")
def list_logs(session: Session = Depends(get_session), limit: int = 200):
    return list(session.exec(select(OperationLog).order_by(OperationLog.id.desc()).limit(limit)))


@app.get("/api/cloud/events")
def cloud_events(session: Session = Depends(get_session), limit: int = 200):
    return list(session.exec(select(CloudSyncEvent).order_by(CloudSyncEvent.id.desc()).limit(limit)))
