from unittest.mock import patch
from app.services import Services
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "mock_services.yaml"

def test_services_get_by_name():
    services = Services(config_path=str(CONFIG_FILE))
    service = services.get_by_name("fisioterapia")
    assert service is not None
    assert service.get_name() == "Fisioterapia"

def test_service_basic_getters():
    services = Services(config_path=str(CONFIG_FILE))
    service = services.get_by_name("fisioterapia")
    assert service.get_name() == "Fisioterapia"
    assert service.get_price() == 100
    assert service.get_duration() == 60
    assert service.get_description() == "Os fisioterapeutas utilizam diversas técnicas, como exercícios terapêuticos, terapia manual, eletroterapia e termoterapia, para ajudar os pacientes a recuperarem sua função física e qualidade de vida. Além do tratamento, a fisioterapia também desempenha um papel importante na prevenção de lesões e doenças, através de orientações sobre postura, ergonomia e hábitos saudáveis."
    assert service.get_professionals()[0]["name"] == "Ana Souza"


@patch("app.services.is_slot_available", return_value=True)
def test_service_get_available_professionals(mock_is_slot_available):
    services = Services(config_path=str(CONFIG_FILE))
    service = services.get_by_name("fisioterapia")
    result = service.get_available_professionals("quarta-feira", "10:00")
    assert "Ana Souza" in result


@patch("app.services.is_slot_available", return_value=True)
def test_service_get_available_slots(mock_is_slot_available):
    services = Services(config_path=str(CONFIG_FILE))
    service = services.get_by_name("fisioterapia")
    slots = service.get_available_slots()
    assert any(slot["professional"] == "Ana Souza" for slot in slots)


@patch("app.services.is_slot_available", return_value=True)
@patch("app.services.create_event", return_value="mock_event_id")
def test_service_schedule_success(mock_create_event, mock_is_slot_available):
    services = Services(config_path=str(CONFIG_FILE))
    service = services.get_by_name("fisioterapia")
    result = service.schedule("Juan Perez", "quarta-feira", "10:00")
    assert result["status"] == "success"
    assert "event_id" in result
    mock_create_event.assert_called_once()



