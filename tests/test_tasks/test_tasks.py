import pytest
from app.tasks.campaign_tasks import run_update_campaigns

@pytest.mark.asyncio
async def test_run_update_campaigns():
    await run_update_campaigns()