from pathlib import Path

from mt4_manager.core import clone_instance_folder, create_instance_from_template, distribute_file, ensure_mt4_layout
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
