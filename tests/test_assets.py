from pathlib import Path


def test_reporter_template_exists():
    path = Path("mt4_templates/MT4StatusReporter.mq4")
    assert path.exists()


def test_reporter_template_contains_required_fields():
    content = Path("mt4_templates/MT4StatusReporter.mq4").read_text(encoding="utf-8")
    assert "ManagerUrl" in content
    assert "InstanceId" in content
    assert "/api/report/status" in content
