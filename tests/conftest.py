import pytest
from hr_agentic.agent.cognitive_loop import get_orchestrator
from hr_agentic.connectors.workweek import get_workweek_client
from hr_agentic.connectors.service_immediately import get_service_immediately_client

@pytest.fixture
def agent():
    return get_orchestrator()

@pytest.fixture
def ww():
    return get_workweek_client()

@pytest.fixture
def si():
    return get_service_immediately_client()
