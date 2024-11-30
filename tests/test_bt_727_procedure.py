# tests/test_bt_727_procedure.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.bt_727_procedure import (
    merge_procedure_place_performance,
    parse_procedure_place_performance,
)
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_parse_procedure_place_performance() -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:Region>anyw-eea</cbc:Region>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </ContractNotice>
    """
    result = parse_procedure_place_performance(xml_content)

    assert result is not None
    assert "tender" in result
    assert "deliveryLocations" in result["tender"]
    assert len(result["tender"]["deliveryLocations"]) == 1
    assert (
        result["tender"]["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    )


def test_merge_procedure_place_performance() -> None:
    test_data = {
        "tender": {
            "deliveryLocations": [
                {"description": "Anywhere in the European Economic Area"}
            ]
        }
    }
    release_json = {"tender": {}}

    merge_procedure_place_performance(release_json, test_data)

    assert "deliveryLocations" in release_json["tender"]
    assert len(release_json["tender"]["deliveryLocations"]) == 1
    assert (
        release_json["tender"]["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    )


def test_bt_727_procedure_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProject>
            <cac:RealizedLocation>
                <cac:Address>
                    <cbc:Region>anyw-eea</cbc:Region>
                </cac:Address>
            </cac:RealizedLocation>
        </cac:ProcurementProject>
    </ContractNotice>
    """
    xml_file = tmp_path / "test_input_place_performance.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), str(temp_output_dir), "ocds-test-prefix", "test-scheme")

    output_files = list(temp_output_dir.glob("*.json"))
    assert len(output_files) == 1

    with output_files[0].open() as f:
        result = json.load(f)

    logger.info("Result: %s", json.dumps(result, indent=2))

    assert "tender" in result
    assert "deliveryLocations" in result["tender"]
    assert len(result["tender"]["deliveryLocations"]) == 1
    assert (
        result["tender"]["deliveryLocations"][0]["description"]
        == "Anywhere in the European Economic Area"
    )


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
