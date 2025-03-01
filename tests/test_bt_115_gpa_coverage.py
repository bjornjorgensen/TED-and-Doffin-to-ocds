# tests/test_bt_115_GPA_Coverage.py
import json
import logging
import sys
import tempfile
from pathlib import Path

import pytest
from lxml import etree

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main
from src.ted_and_doffin_to_ocds.converters.eforms.bt_115_gpa_coverage import parse_gpa_coverage


@pytest.fixture(scope="module")
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    return logger


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


def run_main_and_get_result(xml_file, output_dir):
    sys.argv = [
        "main.py",
        str(xml_file),  # input
        output_dir,     # output
        "ocds-123abc"   # ocid_prefix
    ]
    main()
    json_files = list(Path(output_dir).glob("*.json"))
    assert len(json_files) > 0, "No JSON files generated"
    with open(json_files[0]) as f:
        return json.load(f)


def test_parse_gpa_coverage():
    """Test parsing GPA coverage without integration."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>true</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    result = parse_gpa_coverage(xml_content)
    assert result is not None
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    assert result["tender"]["lots"][0]["id"] == "LOT-0001"
    assert "coveredBy" in result["tender"]["lots"][0]
    assert result["tender"]["lots"][0]["coveredBy"] == ["GPA"]


def test_parse_gpa_coverage_false():
    """Test parsing when GPA coverage is false."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>false</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    result = parse_gpa_coverage(xml_content)
    assert result is None


def test_parse_gpa_coverage_missing():
    """Test parsing when GPA coverage indicator is missing."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """
    result = parse_gpa_coverage(xml_content)
    assert result is None


def test_bt_115_gpa_coverage_integration(
    tmp_path, setup_logging, temp_output_dir
) -> None:
    """Integration test for GPA coverage."""
    logger = setup_logging

    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>true</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>false</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingProcess>
                <cbc:GovernmentAgreementConstraintIndicator>true</cbc:GovernmentAgreementConstraintIndicator>
            </cac:TenderingProcess>
        </cac:ProcurementProjectLot>
    </ContractAwardNotice>
    """

    xml_file = tmp_path / "test_input_gpa_coverage.xml"
    xml_file.write_text(xml_content)

    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in result['tender']"
    assert len(result["tender"]["lots"]) == 2, f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot_1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    assert "coveredBy" in lot_1, "Expected 'coveredBy' in LOT-0001"
    assert "GPA" in lot_1["coveredBy"], "Expected 'GPA' in LOT-0001 coveredBy"

    lot_2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")
    assert "coveredBy" not in lot_2, "Unexpected 'coveredBy' in LOT-0002"

    assert "coveredBy" in result["tender"], "Expected 'coveredBy' in tender"
    assert "GPA" in result["tender"]["coveredBy"], "Expected 'GPA' in tender coveredBy"


def test_invalid_xml():
    """Test handling of invalid XML."""
    with pytest.raises(etree.XMLSyntaxError):
        parse_gpa_coverage("invalid xml")


if __name__ == "__main__":
    pytest.main(["-v"])
