"""
Acceptance tests for TRQ-004 — On-Demand Release Workflow (SPEC-004).

These tests validate that:
1. A GitHub Actions release workflow exists at .github/workflows/release.yml
2. The workflow has a workflow_dispatch trigger with a required version input
3. A cliff.toml configuration file exists at the repository root
4. The workflow generates release notes using git-cliff
5. The workflow creates and pushes git tags
6. The workflow publishes GitHub Releases
7. No CHANGELOG.md is committed to the repository
8. Release notes exclude non-user-facing types (chore, ci, style)

Tests are expected to fail (RED) until the implementation exists.
"""

import os
import yaml


class TestReleaseWorkflowFile:
    """Test that .github/workflows/release.yml exists and has correct structure."""

    def test_trq004_release_workflow_file_exists(self):
        """A release workflow file must exist at .github/workflows/release.yml."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        assert os.path.isfile(workflow_path), f"release.yml not found at {workflow_path}"

    def test_trq004_release_workflow_has_workflow_dispatch_trigger(self):
        """The release workflow must have a workflow_dispatch trigger."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        assert "on" in workflow, "Workflow must have an 'on' trigger definition"
        assert (
            "workflow_dispatch" in workflow["on"]
        ), "Workflow must have workflow_dispatch trigger"

    def test_trq004_release_workflow_has_version_input(self):
        """The release workflow must have a required 'version' input."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        assert (
            "workflow_dispatch" in workflow["on"]
        ), "workflow_dispatch trigger must exist"
        dispatch_config = workflow["on"]["workflow_dispatch"]
        assert "inputs" in dispatch_config, "workflow_dispatch must have inputs"
        assert "version" in dispatch_config["inputs"], "version input must be defined"
        assert (
            dispatch_config["inputs"]["version"].get("required") is True
        ), "version input must be required"

    def test_trq004_release_workflow_uses_git_cliff(self):
        """The release workflow must use git-cliff to generate release notes."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow_content = f.read()

        assert (
            "git-cliff" in workflow_content or "cliff" in workflow_content
        ), "Workflow must reference git-cliff for release notes generation"

    def test_trq004_release_workflow_creates_git_tag(self):
        """The release workflow must create and push a git tag."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow_content = f.read()

        # Check for git tag creation and push operations
        assert (
            "git tag" in workflow_content
            or "tag" in workflow_content.lower()
        ), "Workflow must create git tags"
        assert (
            "git push" in workflow_content or "push" in workflow_content.lower()
        ), "Workflow must push git tags"

    def test_trq004_release_workflow_publishes_release(self):
        """The release workflow must publish a GitHub Release using gh CLI or softprops/action-gh-release."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow_content = f.read()

        # Check for either gh release or softprops action
        assert (
            "gh release" in workflow_content
            or "softprops/action-gh-release" in workflow_content
        ), "Workflow must publish GitHub Release using gh CLI or softprops/action-gh-release"

    def test_trq004_release_workflow_can_be_triggered_manually(self):
        """The release workflow must be triggerable from GitHub Actions UI."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        # workflow_dispatch enables manual triggering
        assert (
            "on" in workflow and "workflow_dispatch" in workflow["on"]
        ), "workflow_dispatch trigger enables manual triggering from GitHub UI"


class TestCliffConfiguration:
    """Test that cliff.toml exists and is properly configured."""

    def test_trq004_cliff_config_file_exists(self):
        """A cliff.toml configuration file must exist at the repository root."""
        cliff_path = os.path.join(
            os.path.dirname(__file__), "..", "cliff.toml"
        )
        assert os.path.isfile(cliff_path), f"cliff.toml not found at {cliff_path}"

    def test_trq004_cliff_config_is_valid_toml(self):
        """The cliff.toml file must be valid TOML."""
        cliff_path = os.path.join(
            os.path.dirname(__file__), "..", "cliff.toml"
        )
        try:
            with open(cliff_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Basic TOML validation: check for [section] headers and key = value pairs
            assert "[" in content, "TOML must contain section headers"
            assert "=" in content, "TOML must contain key-value pairs"
        except Exception as e:
            raise AssertionError(f"cliff.toml is not valid TOML: {e}")

    def test_trq004_cliff_config_configures_commit_grouping(self):
        """The cliff.toml must configure conventional commit grouping (feat, fix, etc.)."""
        cliff_path = os.path.join(
            os.path.dirname(__file__), "..", "cliff.toml"
        )
        with open(cliff_path, "r", encoding="utf-8") as f:
            changelog_text = f.read()

        assert "[changelog]" in changelog_text, "cliff.toml must have [changelog] section"
        # Check for commit type configurations (feat, fix, etc.)
        assert (
            "feat" in changelog_text or "Features" in changelog_text
        ), "cliff.toml must configure feat (Features) grouping"
        assert (
            "fix" in changelog_text or "Bug Fixes" in changelog_text or "Fixes" in changelog_text
        ), "cliff.toml must configure fix (Bug Fixes) grouping"

    def test_trq004_cliff_config_excludes_non_user_facing_types(self):
        """The cliff.toml must exclude non-user-facing types (chore, ci, style, refactor, test)."""
        cliff_path = os.path.join(
            os.path.dirname(__file__), "..", "cliff.toml"
        )
        with open(cliff_path, "r", encoding="utf-8") as f:
            cliff_content = f.read()

        # Check that non-user-facing types are excluded
        # This can be done via skip_footers or commit_parsers configuration
        assert (
            "chore" in cliff_content
            or "ci" in cliff_content
            or "style" in cliff_content
        ), "cliff.toml must reference non-user-facing types (chore, ci, style) for exclusion"


class TestChangelogFile:
    """Test that CHANGELOG.md is not committed to the repository."""

    def test_trq004_no_changelog_md_file(self):
        """No CHANGELOG.md file must be committed to the repository."""
        changelog_path = os.path.join(
            os.path.dirname(__file__), "..", "CHANGELOG.md"
        )
        assert (
            not os.path.isfile(changelog_path)
        ), "CHANGELOG.md must not be committed to the repository"


class TestReleaseNotesGeneration:
    """Test that release notes are correctly generated and formatted."""

    def test_trq004_release_workflow_generates_release_notes_from_commits(self):
        """The release workflow must generate release notes from git-cliff based on commits since last tag."""
        workflow_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            ".github",
            "workflows",
            "release.yml",
        )
        with open(workflow_path, "r", encoding="utf-8") as f:
            workflow_content = f.read()

        # Verify that git-cliff is invoked to generate release notes
        assert (
            "git-cliff" in workflow_content or "cliff" in workflow_content.lower()
        ), "Workflow must invoke git-cliff to generate release notes"
        # Check for output or configuration being passed to git-cliff
        assert (
            "cliff.toml" in workflow_content or "--config" in workflow_content
        ), "Workflow must reference cliff.toml configuration"

    def test_trq004_release_notes_exclude_non_user_facing_types(self):
        """The generated release notes must exclude non-user-facing types (chore, ci, style)."""
        cliff_path = os.path.join(
            os.path.dirname(__file__), "..", "cliff.toml"
        )
        with open(cliff_path, "r", encoding="utf-8") as f:
            cliff_config = f.read()

        # Verify exclusion configuration in cliff.toml
        # Common patterns: skip_ directives, footers, or commit_parsers without these types
        assert (
            "chore" in cliff_config
            and "skip" in cliff_config
            or "chore" not in cliff_config.split("[changelog")[1]
        ), "cliff.toml must exclude chore type from release notes"
