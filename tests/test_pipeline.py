"""Integration test running the full pipeline on real sample resumes."""

from pathlib import Path
from pipeline import analyze_resume
from config import SAMPLES_DIR


def test_pipeline_on_software_engineer_sample():
    sample_file = SAMPLES_DIR / "sample_software_engineer.docx"
    assert sample_file.exists()

    with open(sample_file, "rb") as f:
        result = analyze_resume(f.read(), "sample_software_engineer.docx", top_n_roles=5)

    assert result.overall_score >= 70
    assert result.contact["email"] == "alex.morgan@email.com"
    assert "React" in result.skills
    assert "Python" in result.skills
    assert len(result.roles) == 5
    assert len(result.jobs) > 0


def test_pipeline_on_data_analyst_sample():
    sample_file = SAMPLES_DIR / "sample_data_analyst.pdf"
    assert sample_file.exists()

    with open(sample_file, "rb") as f:
        result = analyze_resume(f.read(), "sample_data_analyst.pdf", top_n_roles=5)

    assert result.overall_score >= 65
    assert "Rohan" in result.contact["name"]
    assert "SQL" in result.skills
    assert any("Data" in r["role"] for r in result.roles[:3])

