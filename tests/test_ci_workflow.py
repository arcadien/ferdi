"""
Tests for TRQ-002 — GitHub Actions CI workflow.

Acceptance criteria verified locally (file existence + YAML content):
  AC1: .github/workflows/ci.yml exists
  AC2: Workflow triggered on push and pull_request events
  AC3: Workflow runs on ubuntu-latest
  AC4: Python 3.11 is set up using actions/setup-python@v5
  AC5: Dependencies installed via pip install -e ".[dev]"
  AC6: Test suite executed with pytest tests/ -v

Acceptance criteria that CANNOT be verified locally (require GitHub infrastructure):
  AC7: Workflow passes (green) on the current codebase
       — skipped: requires the workflow to actually execute on GitHub runners
  AC8: Workflow success is visible in pull request checks and commit status
       — skipped: requires live GitHub UI / GitHub API access
"""

import pathlib
import pytest
import yaml

WORKFLOW_PATH = pathlib.Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


@pytest.fixture(scope="module")
def workflow_yaml():
    """Load and parse the CI workflow YAML file."""
    with WORKFLOW_PATH.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# AC1 — File existence
# ---------------------------------------------------------------------------

def test_trq002_workflow_file_exists():
    """AC1: .github/workflows/ci.yml must exist in the repository."""
    assert WORKFLOW_PATH.exists(), (
        f"Workflow file not found: {WORKFLOW_PATH}. "
        "Create .github/workflows/ci.yml to satisfy TRQ-002 AC1."
    )


# ---------------------------------------------------------------------------
# AC2 — Trigger: push and pull_request
# ---------------------------------------------------------------------------

def test_trq002_trigger_on_push(workflow_yaml):
    """AC2a: Workflow must be triggered on push events."""
    on_section = workflow_yaml.get(True, workflow_yaml.get("on", {}))
    # GitHub Actions 'on' can be a list or a dict
    if isinstance(on_section, list):
        triggers = on_section
    else:
        triggers = list(on_section.keys())
    assert "push" in triggers, (
        f"'push' trigger not found in workflow 'on' section. Got: {on_section}"
    )


def test_trq002_trigger_on_pull_request(workflow_yaml):
    """AC2b: Workflow must be triggered on pull_request events."""
    on_section = workflow_yaml.get(True, workflow_yaml.get("on", {}))
    if isinstance(on_section, list):
        triggers = on_section
    else:
        triggers = list(on_section.keys())
    assert "pull_request" in triggers, (
        f"'pull_request' trigger not found in workflow 'on' section. Got: {on_section}"
    )


# ---------------------------------------------------------------------------
# AC3 — Runner: ubuntu-latest
# ---------------------------------------------------------------------------

def test_trq002_runs_on_ubuntu_latest(workflow_yaml):
    """AC3: At least one job must declare runs-on: ubuntu-latest."""
    jobs = workflow_yaml.get("jobs", {})
    assert jobs, "No jobs defined in workflow."
    runs_on_values = [job.get("runs-on") for job in jobs.values()]
    assert "ubuntu-latest" in runs_on_values, (
        f"No job with 'runs-on: ubuntu-latest' found. Got: {runs_on_values}"
    )


# ---------------------------------------------------------------------------
# AC4 — Python 3.11 via actions/setup-python@v5
# ---------------------------------------------------------------------------

def test_trq002_setup_python_action_used(workflow_yaml):
    """AC4a: actions/setup-python@v5 must appear in at least one job step."""
    jobs = workflow_yaml.get("jobs", {})
    found = False
    for job in jobs.values():
        for step in job.get("steps", []):
            uses = step.get("uses", "")
            if uses.startswith("actions/setup-python@v5"):
                found = True
                break
    assert found, "No step uses 'actions/setup-python@v5'."


def test_trq002_python_version_is_311(workflow_yaml):
    """AC4b: The setup-python step must configure python-version '3.11'."""
    jobs = workflow_yaml.get("jobs", {})
    python_version = None
    for job in jobs.values():
        for step in job.get("steps", []):
            if step.get("uses", "").startswith("actions/setup-python"):
                with_block = step.get("with", {})
                python_version = str(with_block.get("python-version", ""))
                break
    assert python_version == "3.11", (
        f"Expected python-version '3.11', got '{python_version}'."
    )


# ---------------------------------------------------------------------------
# AC5 — Dependency installation via pip install -e ".[dev]"
# ---------------------------------------------------------------------------

def test_trq002_install_dev_dependencies(workflow_yaml):
    """AC5: A workflow step must run 'pip install -e \".[dev]\"'."""
    jobs = workflow_yaml.get("jobs", {})
    found = False
    for job in jobs.values():
        for step in job.get("steps", []):
            run_cmd = step.get("run", "")
            if 'pip install -e ".[dev]"' in run_cmd or "pip install -e '.[dev]'" in run_cmd:
                found = True
                break
    assert found, (
        "No step contains 'pip install -e \".[dev]\"'. "
        "Dependencies must be installed via pyproject.toml dev extras."
    )


# ---------------------------------------------------------------------------
# AC6 — Test execution with pytest tests/ -v
# ---------------------------------------------------------------------------

def test_trq002_pytest_command(workflow_yaml):
    """AC6: A workflow step must run 'pytest tests/ -v'."""
    jobs = workflow_yaml.get("jobs", {})
    found = False
    for job in jobs.values():
        for step in job.get("steps", []):
            run_cmd = step.get("run", "")
            if "pytest tests/ -v" in run_cmd:
                found = True
                break
    assert found, (
        "No step contains 'pytest tests/ -v'. "
        "The test suite must be executed with verbose output."
    )


# ---------------------------------------------------------------------------
# Skipped: GitHub-infrastructure-only criteria
# ---------------------------------------------------------------------------

@pytest.mark.skip(
    reason=(
        "AC7: Cannot be verified locally — requires the workflow to actually "
        "execute on GitHub Actions runners and report a green status."
    )
)
def test_trq002_workflow_passes_on_github():
    pass


@pytest.mark.skip(
    reason=(
        "AC8: Cannot be verified locally — requires live GitHub UI or API access "
        "to confirm workflow status appears in PR checks and commit status."
    )
)
def test_trq002_workflow_visible_in_pr_checks():
    pass
