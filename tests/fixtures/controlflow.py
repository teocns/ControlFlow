import chromadb
import pytest

import controlflow
from controlflow.events.history import InMemoryHistory
from controlflow.memory.providers.chroma import ChromaMemory
from controlflow.settings import temporary_settings
from controlflow.utilities.testing import FakeLLM


@pytest.fixture(autouse=True, scope="session")
def temp_controlflow_settings():
    with temporary_settings(
        enable_default_print_handler=False,
        log_all_messages=True,
        log_level="DEBUG",
        orchestrator_max_agent_turns=10,
        orchestrator_max_llm_calls=10,
    ):
        yield


@pytest.fixture(autouse=True)
def reset_settings_after_each_test():
    with temporary_settings():
        yield


@pytest.fixture(autouse=True)
def temp_controlflow_defaults(tmp_path, monkeypatch):
    # use in-memory history
    monkeypatch.setattr(
        controlflow.defaults,
        "history",
        InMemoryHistory(),
    )

    monkeypatch.setattr(
        controlflow.defaults,
        "memory_provider",
        ChromaMemory(
            client=chromadb.PersistentClient(path=str(tmp_path / "controlflow-memory"))
        ),
    )

    yield


@pytest.fixture(autouse=True)
def reset_defaults_before_each_test(monkeypatch):
    """
    Monkeypatch defaults to themselves, which will automatically reset them before every test
    """
    for k, v in controlflow.defaults.__dict__.items():
        monkeypatch.setattr(controlflow.defaults, k, v)
    yield  # <-- This is where execution is paused and given back to the test
    # This is where the teardown code goes


@pytest.fixture()
def fake_llm() -> FakeLLM:
    return FakeLLM(responses=[])


@pytest.fixture()
def default_fake_llm(fake_llm) -> FakeLLM:
    controlflow.defaults.model = fake_llm
    return fake_llm
