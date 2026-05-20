"""Tests for .claude/hooks/mcp_check.py — MCP compliance guardrail."""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

HOOKS_DIR = Path(__file__).parent.parent.parent / ".claude" / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

import mcp_check  # noqa: E402


# ── helpers ────────────────────────────────────────────────────────────────────


def _payload(command: str) -> str:
    return json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})


def _run(stdin_text: str) -> tuple[int, str]:
    """Run main() with given stdin, return (exit_code, stderr)."""
    captured = StringIO()
    with patch("sys.stdin", StringIO(stdin_text)), patch("sys.stderr", captured):
        code = mcp_check.main()
    return code, captured.getvalue()


# ── _base_command ──────────────────────────────────────────────────────────────


class TestBaseCommand:
    def test_simple_command(self):
        assert mcp_check._base_command("curl https://example.com") == "curl"

    def test_command_with_path(self):
        assert mcp_check._base_command("/usr/bin/psql -U postgres") == "psql"

    def test_skips_env_assignments(self):
        assert mcp_check._base_command("DEBUG=1 NODE_ENV=test gh pr list") == "gh"

    def test_empty_string(self):
        assert mcp_check._base_command("") == ""

    def test_command_with_flags(self):
        assert mcp_check._base_command("redis-cli -h localhost -p 6379") == "redis-cli"


# ── check ──────────────────────────────────────────────────────────────────────


class TestCheck:
    @pytest.mark.parametrize(
        "cmd",
        [
            "curl https://api.example.com/v1/users",
            "wget https://example.com/file.tar.gz",
            "http GET https://api.example.com",
        ],
    )
    def test_http_clients_flagged(self, cmd):
        result = mcp_check.check(cmd)
        assert result is not None
        assert "HTTP request" in result
        assert "mcp__fetch" in result

    @pytest.mark.parametrize(
        "cmd",
        [
            "psql -U postgres -d mydb -c 'SELECT 1'",
            "pg_dump mydb > dump.sql",
        ],
    )
    def test_postgres_flagged(self, cmd):
        result = mcp_check.check(cmd)
        assert result is not None
        assert "PostgreSQL" in result
        assert "mcp__postgres" in result

    def test_mysql_flagged(self):
        result = mcp_check.check("mysql -u root -p mydb")
        assert result is not None
        assert "MySQL" in result

    def test_sqlite_flagged(self):
        result = mcp_check.check("sqlite3 ./data/myapp.db")
        assert result is not None
        assert "SQLite" in result

    def test_redis_flagged(self):
        result = mcp_check.check("redis-cli set mykey myvalue")
        assert result is not None
        assert "Redis" in result

    def test_mongo_flagged(self):
        result = mcp_check.check("mongosh mongodb://localhost:27017")
        assert result is not None
        assert "MongoDB" in result

    def test_kafka_flagged(self):
        result = mcp_check.check(
            "kafka-console-consumer --bootstrap-server localhost:9092"
        )
        assert result is not None
        assert "Kafka" in result

    def test_aws_flagged(self):
        result = mcp_check.check("aws s3 ls s3://my-bucket")
        assert result is not None
        assert "AWS CLI" in result

    def test_gh_flagged(self):
        result = mcp_check.check("gh pr list")
        assert result is not None
        assert "GitHub CLI" in result
        assert "mcp__github" in result

    def test_docker_flagged(self):
        result = mcp_check.check("docker ps -a")
        assert result is not None
        assert "container runtime" in result

    def test_terraform_flagged(self):
        result = mcp_check.check("terraform apply -auto-approve")
        assert result is not None
        assert "infrastructure CLI" in result

    @pytest.mark.parametrize(
        "cmd",
        [
            "git status",
            "make test",
            "python3 scripts/scaffold.py --target ../foo",
            "ruff check .",
            "pytest tests/",
            "ls -la",
            "cat README.md",
            "grep -r 'TODO' src/",
        ],
    )
    def test_safe_commands_not_flagged(self, cmd):
        assert mcp_check.check(cmd) is None

    def test_warning_is_advisory(self):
        result = mcp_check.check("curl https://example.com")
        assert result is not None
        assert "advisory" in result.lower() or "Continuing anyway" in result


# ── main ───────────────────────────────────────────────────────────────────────


class TestMain:
    def test_non_bash_tool_ignored(self):
        payload = json.dumps(
            {"tool_name": "Read", "tool_input": {"file_path": "foo.py"}}
        )
        code, stderr = _run(payload)
        assert code == 0
        assert stderr == ""

    def test_malformed_json_exits_zero(self):
        code, stderr = _run("not json")
        assert code == 0

    def test_no_command_exits_zero(self):
        payload = json.dumps({"tool_name": "Bash", "tool_input": {}})
        code, stderr = _run(payload)
        assert code == 0
        assert stderr == ""

    def test_safe_command_no_output(self):
        code, stderr = _run(_payload("git status"))
        assert code == 0
        assert stderr == ""

    def test_mcp_pattern_emits_warning(self):
        code, stderr = _run(_payload("curl https://api.example.com"))
        assert code == 0  # never blocks
        assert "MCP-first reminder" in stderr
        assert "curl" in stderr

    def test_postgres_warning_emitted(self):
        code, stderr = _run(_payload("psql -U postgres mydb"))
        assert code == 0
        assert "MCP-first reminder" in stderr
        assert "PostgreSQL" in stderr

    def test_always_exits_zero(self):
        """Even flagged commands must always exit 0 — hook must never block."""
        for cmd in ["curl https://x.com", "psql -U postgres", "redis-cli ping"]:
            code, _ = _run(_payload(cmd))
            assert code == 0, f"Expected exit 0 for '{cmd}', got {code}"


class TestCurlRegex:
    """Regression: ^curls?$ matched phantom command 'curls' (mcp_check.py:27)."""

    def test_curl_is_flagged(self):
        """The real command 'curl' must still trigger the MCP advisory."""
        assert mcp_check.check("curl https://example.com") is not None

    def test_curls_is_not_flagged(self):
        """'curls' is not a real command and must NOT trigger the MCP advisory."""
        result = mcp_check.check("curls https://example.com")
        assert result is None, (
            f"'curls' should not match the curl pattern but got: {result!r}"
        )
