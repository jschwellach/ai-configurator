"""Basic TUI application tests."""
import pytest
from ai_configurator.tui.app import AIConfiguratorApp


def test_app_creation():
    """Test TUI app can be created."""
    app = AIConfiguratorApp()
    assert app is not None
    assert app.title == "AI Configurator v4.0"


@pytest.mark.asyncio
async def test_app_mount():
    """Test TUI app mounts correctly."""
    app = AIConfiguratorApp()
    async with app.run_test() as pilot:
        # App should start with main menu
        assert app.screen is not None
