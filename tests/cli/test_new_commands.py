"""Tests for new CLI command structure."""
from click.testing import CliRunner
from ai_configurator.cli_enhanced import cli


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'AI Configurator' in result.output


def test_agent_list():
    """Test agent list command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['agent', 'list'])
    # Should not crash even if no agents exist
    assert result.exit_code == 0


def test_library_status():
    """Test library status command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['library', 'status'])
    # Should not crash
    assert result.exit_code == 0


def test_mcp_list():
    """Test MCP list command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['mcp', 'list'])
    # Should not crash
    assert result.exit_code == 0


def test_status_command():
    """Test status command."""
    runner = CliRunner()
    result = runner.invoke(cli, ['status'])
    assert result.exit_code == 0
    assert 'AI Configurator' in result.output
