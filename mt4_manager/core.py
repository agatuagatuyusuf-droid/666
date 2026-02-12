from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from sqlmodel import Session, select

from .models import MT4Instance, OperationLog


def ensure_mt4_layout(base_path: Path) -> tuple[Path, Path, Path]:
    terminal = base_path / "terminal.exe"
    mql4 = base_path / "MQL4"
    experts = mql4 / "Experts"
    indicators = mql4 / "Indicators"
    experts.mkdir(parents=True, exist_ok=True)
    indicators.mkdir(parents=True, exist_ok=True)
    (base_path / "config").mkdir(parents=True, exist_ok=True)
    return terminal, experts, indicators


def discover_instance_paths(root_path: Path, max_depth: int = 4) -> list[Path]:
    if not root_path.exists():
        raise FileNotFoundError(f"root path not found: {root_path}")
    roots: list[Path] = []
    for candidate in root_path.rglob("terminal.exe"):
        try:
            rel_depth = len(candidate.relative_to(root_path).parts)
        except ValueError:
            continue
        if rel_depth <= max_depth:
            roots.append(candidate.parent)
    return sorted(set(roots))


def create_instance_from_template(name: str, group_name: str, template_path: Path, target_root: Path) -> Path:
    _ = group_name
    if not template_path.exists():
        raise FileNotFoundError(f"template path not found: {template_path}")
    target_dir = target_root / name
    if target_dir.exists():
        raise FileExistsError(f"Instance folder already exists: {target_dir}")
    shutil.copytree(template_path, target_dir)
    ensure_mt4_layout(target_dir)
    return target_dir


def clone_instance_folder(source: Path, target: Path, keep_only_mql_assets: bool) -> None:
    if not source.exists():
        raise FileNotFoundError(f"source not found: {source}")
    if target.exists():
        raise FileExistsError(f"Clone target exists: {target}")
    if keep_only_mql_assets:
        target.mkdir(parents=True, exist_ok=False)
        for sub in ["terminal.exe", "config", "MQL4/Experts", "MQL4/Indicators", "MQL4/Libraries", "profiles"]:
            src = source / sub
            dst = target / sub
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
    else:
        shutil.copytree(source, target)
    ensure_mt4_layout(target)


def distribute_file(instances: list[MT4Instance], file_path: Path, target_type: str) -> list[dict]:
    if target_type not in {"experts", "indicators"}:
        raise ValueError("target_type must be experts or indicators")
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    results: list[dict] = []
    for ins in instances:
        dest_dir = Path(ins.experts_path if target_type == "experts" else ins.indicators_path)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / file_path.name
        shutil.copy2(file_path, dest)
        results.append({"instance_id": ins.id, "instance_name": ins.name, "dest": str(dest), "status": "ok"})
    return results


def setup_symlinks(instances: list[MT4Instance], master_experts: Path, master_indicators: Path) -> list[dict]:
    master_experts.mkdir(parents=True, exist_ok=True)
    master_indicators.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    for ins in instances:
        exp = Path(ins.experts_path)
        ind = Path(ins.indicators_path)
        for link, target in [(exp, master_experts), (ind, master_indicators)]:
            if link.is_symlink() or link.exists():
                if link.is_symlink() or link.is_file():
                    link.unlink()
                else:
                    shutil.rmtree(link)
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(target, target_is_directory=True)
        results.append({"instance_id": ins.id, "status": "ok"})
    return results


def compile_mq4(instance: MT4Instance, mq4_filename: str) -> dict:
    meteditor = Path(instance.base_path) / "metaeditor.exe"
    source = Path(instance.experts_path) / mq4_filename
    if not meteditor.exists():
        return {"ok": False, "reason": "metaeditor.exe not found"}
    if not source.exists():
        return {"ok": False, "reason": f"source not found: {source}"}

    compile_arg = f"/compile:{source}"
    proc = subprocess.run(
        [str(meteditor), compile_arg, "/log"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return {"ok": proc.returncode == 0, "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-2000:]}


def launch_instance(instance: MT4Instance) -> dict:
    terminal = Path(instance.terminal_path)
    if not terminal.exists():
        return {"ok": False, "reason": "terminal.exe missing"}
    try:
        subprocess.Popen([str(terminal)], cwd=str(Path(instance.base_path)))
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "reason": str(exc)}
    return {"ok": True}


def append_log(session: Session, action: str, target: str, detail: dict | str) -> None:
    payload = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    session.add(OperationLog(action=action, target=target, detail=payload, created_at=datetime.utcnow()))
    session.commit()


def select_instances(
    session: Session, instance_ids: list[int] | None = None, group_name: str | None = None, all_instances: bool = False
) -> list[MT4Instance]:
    stmt = select(MT4Instance)
    if all_instances:
        return list(session.exec(stmt))
    if group_name:
        return list(session.exec(stmt.where(MT4Instance.group_name == group_name)))
    if instance_ids:
        return list(session.exec(stmt.where(MT4Instance.id.in_(instance_ids))))
    return []
