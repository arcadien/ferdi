"""
Integration tests for NFR-003: Ruff linter and formatter.

Each test verifies one acceptance criterion from the requirement.
Tests check configuration files, dependency presence, and tool execution.
"""

import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def pyproject_toml(project_root):
    """Load and parse pyproject.toml."""
    with open(project_root / "pyproject.toml") as f:
        content = f.read()
    # Simple TOML parsing for dependencies
    return content


@pytest.fixture
def precommit_config(project_root):
    """Load and parse .pre-commit-config.yaml."""
    with open(project_root / ".pre-commit-config.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def ci_workflow(project_root):
    """Load and parse .github/workflows/ci.yml."""
    with open(project_root / ".github/workflows/ci.yml") as f:
        return yaml.safe_load(f)


def test_nfr003_ruff_installed_as_dev_dependency(pyproject_toml):
    """Verify ruff is listed as a dev dependency in pyproject.toml."""
    # Look for ruff in the optional-dependencies dev section
    assert "[project.optional-dependencies]" in pyproject_toml, \
        "pyproject.toml must have optional-dependencies section"

    # Extract the dev dependencies block
    dev_section = re.search(
        r'\[project\.optional-dependencies\].*?dev\s*=\s*\[(.*?)\]',
        pyproject_toml,
        re.DOTALL
    )
    assert dev_section, "Could not find dev dependencies in pyproject.toml"

    dev_deps = dev_section.group(1)
    assert "ruff" in dev_deps.lower(), \
        "ruff must be listed in [project.optional-dependencies] dev section"


def test_nfr003_ruff_check_exits_zero(project_root):
    """Verify ruff check ferdi/ tests/ exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "uv", "run", "ruff", "check", "ferdi/", "tests/"],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"ruff check failed with code {result.returncode}:\n{result.stdout}\n{result.stderr}"


def test_nfr003_ruff_format_check_exits_zero(project_root):
    """Verify ruff format --check ferdi/ tests/ exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "uv", "run", "ruff", "format", "--check", "ferdi/", "tests/"],
        cwd=project_root,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"ruff format --check failed with code {result.returncode}:\n{result.stdout}\n{result.stderr}"


def test_nfr003_precommit_ruff_check_configured(precommit_config):
    """Verify .pre-commit-config.yaml has ruff hook with check --fix args."""
    assert precommit_config is not None, ".pre-commit-config.yaml must be valid YAML"
    assert "repos" in precommit_config, ".pre-commit-config.yaml must have repos key"

    repos = precommit_config["repos"]
    ruff_hooks = []

    for repo in repos:
        if "hooks" in repo:
            for hook in repo["hooks"]:
                if hook.get("id") == "ruff":
                    ruff_hooks.append(hook)

    assert len(ruff_hooks) > 0, \
        "No ruff hook with id 'ruff' found in .pre-commit-config.yaml"

    ruff_hook = ruff_hooks[0]
    assert "args" in ruff_hook, "ruff hook must have args"
    args = ruff_hook["args"]
    assert "check" in args, "ruff hook args must contain 'check'"
    assert "--fix" in args, "ruff hook args must contain '--fix'"


def test_nfr003_precommit_ruff_format_configured(precommit_config):
    """Verify .pre-commit-config.yaml has ruff-format hook."""
    assert precommit_config is not None, ".pre-commit-config.yaml must be valid YAML"
    assert "repos" in precommit_config, ".pre-commit-config.yaml must have repos key"

    repos = precommit_config["repos"]
    format_hooks = []

    for repo in repos:
        if "hooks" in repo:
            for hook in repo["hooks"]:
                if hook.get("id") == "ruff-format":
                    format_hooks.append(hook)

    assert len(format_hooks) > 0, \
        "No ruff-format hook found in .pre-commit-config.yaml"


def test_nfr003_ci_includes_ruff_check_step(ci_workflow):
    """Verify .github/workflows/ci.yml includes ruff check step."""
    assert ci_workflow is not None, ".github/workflows/ci.yml must be valid YAML"
    assert "jobs" in ci_workflow, "CI workflow must have jobs"

    test_job = None
    for job_name, job_config in ci_workflow["jobs"].items():
        if "steps" in job_config:
            test_job = job_config
            break

    assert test_job is not None, "CI workflow must have steps in at least one job"

    steps = test_job["steps"]
    ruff_check_step = None

    for step in steps:
        if "run" in step and "ruff check" in step["run"]:
            ruff_check_step = step
            break

    assert ruff_check_step is not None, \
        "CI workflow must include a step with 'ruff check' in its run field"


def test_nfr003_ci_includes_ruff_format_step(ci_workflow):
    """Verify .github/workflows/ci.yml includes ruff format --check step."""
    assert ci_workflow is not None, ".github/workflows/ci.yml must be valid YAML"
    assert "jobs" in ci_workflow, "CI workflow must have jobs"

    test_job = None
    for job_name, job_config in ci_workflow["jobs"].items():
        if "steps" in job_config:
            test_job = job_config
            break

    assert test_job is not None, "CI workflow must have steps in at least one job"

    steps = test_job["steps"]
    ruff_format_step = None

    for step in steps:
        if "run" in step and "ruff format" in step["run"] and "--check" in step["run"]:
            ruff_format_step = step
            break

    assert ruff_format_step is not None, \
        "CI workflow must include a step with 'ruff format --check' in its run field"


def test_nfr003_default_ruff_config_applies(pyproject_toml):
    """Verify [tool.ruff] section exists in pyproject.toml."""
    assert "[tool.ruff]" in pyproject_toml, \
        "pyproject.toml must have [tool.ruff] section for ruff configuration"
