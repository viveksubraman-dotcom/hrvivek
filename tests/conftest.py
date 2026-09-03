import pytest

from hr_agentic.agent.cognitive_loop import get_orchestrator
from hr_agentic.connectors.service_immediately import get_service_immediately_client
from hr_agentic.connectors.workweek import get_workweek_client
from hr_agentic.saga.coordinator import get_saga_coordinator


@pytest.fixture(autouse=True)
def reset_state():
    get_workweek_client().reset()
    get_service_immediately_client().reset()
    get_saga_coordinator().reset()
    get_orchestrator().reset()
    yield
    get_workweek_client().reset()
    get_service_immediately_client().reset()
    get_saga_coordinator().reset()
    get_orchestrator().reset()


@pytest.fixture
def agent():
    return get_orchestrator()


@pytest.fixture
def ww():
    return get_workweek_client()


@pytest.fixture
def si():
    return get_service_immediately_client()
