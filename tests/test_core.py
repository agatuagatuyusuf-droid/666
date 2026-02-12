from pathlib import Path

import pytest

pytest.importorskip("sqlmodel")

from mt4_manager.core import (
    clone_instance_folder,
    create_instance_from_template,
    discover_instance_paths,
    distribute_file,
    ensure_mt4_layout,
    mq4_to_ex4_filename,
)
from mt4_manager.models import MT4Instance


def test_create_and_layout(tmp_path: Path):
    template = tmp_path / "template"
    template.mkdir()
    (template / "terminal.exe").write_text("bin")
    created = create_instance_from_template("A1", "g", template, tmp_path / "instances")
    _, experts, indicators = ensure_mt4_layout(created)
    assert (created / "terminal.exe").exists()
    assert experts.exists()
    assert indicators.exists()


def test_discover_instance_paths(tmp_path: Path):
    inst_a = tmp_path / "mt4_a"
    inst_b = tmp_path / "x" / "mt4_b"
    inst_a.mkdir(parents=True)
    inst_b.mkdir(parents=True)
    (inst_a / "terminal.exe").write_text("a")
    (inst_b / "terminal.exe").write_text("b")

    found = discover_instance_paths(tmp_path, max_depth=4)
    assert inst_a in found
    assert inst_b in found


def test_discover_depth_limit(tmp_path: Path):
    deep = tmp_path / "a" / "b" / "c" / "d" / "e"
    deep.mkdir(parents=True)
    (deep / "terminal.exe").write_text("x")
    found = discover_instance_paths(tmp_path, max_depth=3)
    assert deep not in found


def test_mq4_to_ex4_filename():
    assert mq4_to_ex4_filename("MyEA.mq4") == "MyEA.ex4"
    assert mq4_to_ex4_filename("abc") == "abc.ex4"


def test_create_instance_missing_template(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        create_instance_from_template("A1", "g", tmp_path / "missing", tmp_path / "instances")


def test_clone_keep_mql(tmp_path: Path):
    source = tmp_path / "src"
    (source / "MQL4" / "Experts").mkdir(parents=True)
    (source / "MQL4" / "Experts" / "x.ex4").write_text("x")
    (source / "MQL4" / "Indicators").mkdir(parents=True)
    (source / "terminal.exe").write_text("bin")
    (source / "logs" / "noise.txt").parent.mkdir(parents=True)
    (source / "logs" / "noise.txt").write_text("noise")

    target = tmp_path / "dst"
    clone_instance_folder(source, target, keep_only_mql_assets=True)

    assert (target / "MQL4" / "Experts" / "x.ex4").exists()
    assert not (target / "logs").exists()


def test_distribute(tmp_path: Path):
    file = tmp_path / "robot.ex4"
    file.write_text("demo")
    dst = tmp_path / "inst" / "MQL4" / "Experts"
    ins = MT4Instance(
        id=1,
        name="i1",
        group_name="default",
        base_path=str(tmp_path / "inst"),
        terminal_path=str(tmp_path / "inst" / "terminal.exe"),
        experts_path=str(dst),
        indicators_path=str(tmp_path / "inst" / "MQL4" / "Indicators"),
    )
    res = distribute_file([ins], file, "experts")
    assert len(res) == 1
    assert (dst / "robot.ex4").exists()


def test_distribute_invalid_type(tmp_path: Path):
    file = tmp_path / "robot.ex4"
    file.write_text("demo")
    ins = MT4Instance(
        id=1,
        name="i1",
        group_name="default",
        base_path=str(tmp_path / "inst"),
        terminal_path=str(tmp_path / "inst" / "terminal.exe"),
        experts_path=str(tmp_path / "inst" / "MQL4" / "Experts"),
        indicators_path=str(tmp_path / "inst" / "MQL4" / "Indicators"),
    )
    with pytest.raises(ValueError):
        distribute_file([ins], file, "bad_type")
