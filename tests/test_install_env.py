from __future__ import annotations

from click.testing import CliRunner

from agentsmd.install import ENV_VAR_NAME, _resolve_shell_rc, _write_env_var, main


def test_fresh_write_creates_marker_block(tmp_path):
    rc = tmp_path / ".zshrc"
    _write_env_var(rc, "agentsmd-server")

    content = rc.read_text(encoding="utf-8")
    assert f'export {ENV_VAR_NAME}="agentsmd-server"' in content
    assert content.count("# agentsmd-install: begin") == 1


def test_rerun_updates_value_in_place(tmp_path):
    rc = tmp_path / ".zshrc"
    _write_env_var(rc, "agentsmd-server")
    _write_env_var(rc, "/abs/path/bin/agentsmd-serve")

    content = rc.read_text(encoding="utf-8")
    assert content.count("# agentsmd-install: begin") == 1
    assert f'export {ENV_VAR_NAME}="/abs/path/bin/agentsmd-serve"' in content
    assert "agentsmd-server" not in content


def test_unrelated_content_preserved(tmp_path):
    rc = tmp_path / ".zshrc"
    rc.write_text('export JAVA_HOME="/opt/homebrew/opt/openjdk@21"\n', encoding="utf-8")

    _write_env_var(rc, "agentsmd-server")

    content = rc.read_text(encoding="utf-8")
    assert 'export JAVA_HOME="/opt/homebrew/opt/openjdk@21"' in content
    assert f'export {ENV_VAR_NAME}="agentsmd-server"' in content


def test_resolve_shell_rc_bash(tmp_path):
    assert _resolve_shell_rc(tmp_path, "/bin/bash") == tmp_path / ".bashrc"


def test_resolve_shell_rc_defaults_to_zsh(tmp_path):
    assert _resolve_shell_rc(tmp_path, None) == tmp_path / ".zshrc"
    assert _resolve_shell_rc(tmp_path, "/usr/bin/fish") == tmp_path / ".zshrc"


def test_cli_no_shell_env_skips_write(tmp_path, monkeypatch):
    monkeypatch.setenv("SHELL", "/bin/zsh")
    runner = CliRunner()
    result = runner.invoke(main, ["--home", str(tmp_path), "--no-shell-env"])

    assert result.exit_code == 0, result.output
    assert not (tmp_path / ".zshrc").exists()


def test_cli_writes_shell_env_by_default(tmp_path, monkeypatch):
    monkeypatch.setenv("SHELL", "/bin/zsh")
    runner = CliRunner()
    result = runner.invoke(main, ["--home", str(tmp_path), "--server-command", "agentsmd-server"])

    assert result.exit_code == 0, result.output
    content = (tmp_path / ".zshrc").read_text(encoding="utf-8")
    assert f'export {ENV_VAR_NAME}="agentsmd-server"' in content
