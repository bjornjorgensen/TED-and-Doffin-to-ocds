# tests/test_bt_113_Lot.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.converters.eforms.bt_113_lot import (
    parse_framework_max_participants,
    merge_framework_max_participants,
)


def test_parse_framework_max_participants_eforms() -> None:
    """Test parsing framework maximum participants from eForms XML."""
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <cbc:MaximumOperatorQuantity>50</cbc:MaximumOperatorQuantity>
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_framework_max_participants(xml_content)
    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert result["tender"]["lots"][0]["techniques"]["frameworkAgreement"]["maximumParticipants"] == 50


def test_parse_framework_max_participants_ted() -> None:
    """Test parsing framework maximum participants from legacy TED XML."""
    xml_content = """
    <root xmlns:ted="http://publications.europa.eu/resource/schema/ted/R2.0.9/publication">
        <ted:FORM_SECTION>
            <ted:F02_2014>
                <ted:PROCEDURE>
                    <ted:FRAMEWORK>
                        <ted:NB_PARTICIPANTS>30</ted:NB_PARTICIPANTS>
                    </ted:FRAMEWORK>
                </ted:PROCEDURE>
            </ted:F02_2014>
        </ted:FORM_SECTION>
    </root>
    """
    result = parse_framework_max_participants(xml_content)
    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "1"
    assert result["tender"]["lots"][0]["techniques"]["frameworkAgreement"]["maximumParticipants"] == 30


def test_parse_framework_max_participants_defence() -> None:
    """Test parsing framework maximum participants from TED defence form XML."""
    xml_content = """
    <root xmlns:ted="http://publications.europa.eu/resource/schema/ted/R2.0.9/publication">
        <ted:FORM_SECTION>
            <ted:CONTRACT_DEFENCE>
                <ted:FD_CONTRACT_DEFENCE>
                    <ted:OBJECT_CONTRACT_INFORMATION_DEFENCE>
                        <ted:DESCRIPTION_CONTRACT_INFORMATION_DEFENCE>
                            <ted:F17_FRAMEWORK>
                                <ted:SEVERAL_OPERATORS>
                                    <ted:MAX_NUMBER_PARTICIPANTS>25</ted:MAX_NUMBER_PARTICIPANTS>
                                </ted:SEVERAL_OPERATORS>
                            </ted:F17_FRAMEWORK>
                        </ted:DESCRIPTION_CONTRACT_INFORMATION_DEFENCE>
                    </ted:OBJECT_CONTRACT_INFORMATION_DEFENCE>
                </ted:FD_CONTRACT_DEFENCE>
            </ted:CONTRACT_DEFENCE>
        </ted:FORM_SECTION>
    </root>
    """
    result = parse_framework_max_participants(xml_content)
    assert result is not None
    assert result["tender"]["lots"][0]["id"] == "1"
    assert result["tender"]["lots"][0]["techniques"]["frameworkAgreement"]["maximumParticipants"] == 25


def test_parse_framework_max_participants_no_data() -> None:
    """Test parsing XML without framework maximum participants data."""
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
        </cac:ProcurementProjectLot>
    </root>
    """
    result = parse_framework_max_participants(xml_content)
    assert result is None


def test_merge_framework_max_participants() -> None:
    """Test merging framework maximum participants data into release JSON."""
    release_json = {
        "tender": {
            "lots": [
                {"id": "LOT-0001", "title": "Test Lot"}
            ]
        }
    }

    max_participants_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "techniques": {
                        "frameworkAgreement": {
                            "maximumParticipants": 50
                        }
                    }
                }
            ]
        }
    }

    merge_framework_max_participants(release_json, max_participants_data)

    lot = release_json["tender"]["lots"][0]
    assert "techniques" in lot
    assert "frameworkAgreement" in lot["techniques"]
    assert lot["techniques"]["frameworkAgreement"]["maximumParticipants"] == 50


def test_merge_framework_max_participants_none_data() -> None:
    """Test merging with None data."""
    release_json = {"tender": {"lots": [{"id": "LOT-0001"}]}}
    merge_framework_max_participants(release_json, None)
    assert release_json == {"tender": {"lots": [{"id": "LOT-0001"}]}}


def test_merge_framework_max_participants_new_lot() -> None:
    """Test merging when lot doesn't exist in release JSON."""
    release_json = {"tender": {"lots": []}}
    max_participants_data = {
        "tender": {
            "lots": [
                {
                    "id": "LOT-0001",
                    "techniques": {
                        "frameworkAgreement": {
                            "maximumParticipants": 50
                        }
                    }
                }
            ]
        }
    }

    merge_framework_max_participants(release_json, max_participants_data)
    assert len(release_json["tender"]["lots"]) == 1
    lot = release_json["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert lot["techniques"]["frameworkAgreement"]["maximumParticipants"] == 50


@pytest.fixture(scope="module")
def setup_logging():
    logger = logging.getLogger(__name__)
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    from src.ted_and_doffin_to_ocds.main import main

    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_113_lot_integration(tmp_path, setup_logging, temp_output_dir) -> None:
    """Integration test for BT-113-Lot framework maximum participants."""
    logger = setup_logging
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cac:FrameworkAgreement>
                    <cbc:MaximumOperatorQuantity>50</cbc:MaximumOperatorQuantity>
                </cac:FrameworkAgreement>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_framework_max_participants.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "techniques" in lot
    assert "frameworkAgreement" in lot["techniques"]
    assert lot["techniques"]["frameworkAgreement"]["maximumParticipants"] == 50


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
