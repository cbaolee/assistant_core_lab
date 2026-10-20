import pytest
from assistant_core.config import Settings
from assistant_core.knowledge import OfficeDirectory, Office, Handbook, Rule
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

@pytest.fixture
def service():
    settings = Settings(llm_api_key="fake")
    offices = OfficeDirectory({"library": Office("library", "B.201", "Mon-Sat 07:00-20:00")})
    handbook = Handbook([Rule("H26-5.3", "Thesis", "thesis registration credits")])
    responder = StubLLMResponder()
    return AssistantService(settings, offices, handbook, responder)