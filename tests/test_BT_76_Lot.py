# tests/test_BT_76_Lot.py

import pytest
import json
import os
import sys
import logging

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main, configure_logging


@pytest.fixture(scope="module")
def setup_logging():
    configure_logging()
    return logging.getLogger(__name__)


def test_bt_76_lot_integration(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">The tenderer must be a registered company</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0002</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">The tenderer must be a partnership</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_tenderer_legal_form.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 2
    ), f"Expected 2 lots, got {len(result['tender']['lots'])}"

    lot1 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0001")
    lot2 = next(lot for lot in result["tender"]["lots"] if lot["id"] == "LOT-0002")

    assert "contractTerms" in lot1, "Expected 'contractTerms' in LOT-0001"
    assert (
        "tendererLegalForm" in lot1["contractTerms"]
    ), "Expected 'tendererLegalForm' in LOT-0001 contractTerms"
    assert (
        lot1["contractTerms"]["tendererLegalForm"]
        == "The tenderer must be a registered company"
    ), "Unexpected tendererLegalForm content for LOT-0001"

    assert "contractTerms" in lot2, "Expected 'contractTerms' in LOT-0002"
    assert (
        "tendererLegalForm" in lot2["contractTerms"]
    ), "Expected 'tendererLegalForm' in LOT-0002 contractTerms"
    assert (
        lot2["contractTerms"]["tendererLegalForm"]
        == "The tenderer must be a partnership"
    ), "Unexpected tendererLegalForm content for LOT-0002"


def test_bt_76_lot_missing_company_legal_form(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <!-- CompanyLegalForm is missing -->
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_missing_company_legal_form.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", "Expected lot id 'LOT-0001'"
    assert "contractTerms" not in lot or "tendererLegalForm" not in lot.get(
        "contractTerms", {}
    ), "Did not expect 'tendererLegalForm' when CompanyLegalForm is missing"


def test_bt_76_lot_empty_company_legal_form(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG"></cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_empty_company_legal_form.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", "Expected lot id 'LOT-0001'"
    assert "contractTerms" not in lot or "tendererLegalForm" not in lot.get(
        "contractTerms", {}
    ), "Did not expect 'tendererLegalForm' when CompanyLegalForm is empty"


def test_bt_76_lot_multiple_qualification_requests(tmp_path, setup_logging):
    logger = setup_logging
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">First legal form requirement</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
                <cac:TendererQualificationRequest>
                    <cbc:CompanyLegalForm languageID="ENG">Second legal form requirement</cbc:CompanyLegalForm>
                </cac:TendererQualificationRequest>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_multiple_qualification_requests.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    logger.info(f"Result: {json.dumps(result, indent=2)}")

    assert "tender" in result, "Expected 'tender' in result"
    assert "lots" in result["tender"], "Expected 'lots' in tender"
    assert (
        len(result["tender"]["lots"]) == 1
    ), f"Expected 1 lot, got {len(result['tender']['lots'])}"

    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", "Expected lot id 'LOT-0001'"
    assert "contractTerms" in lot, "Expected 'contractTerms' in lot"
    assert (
        "tendererLegalForm" in lot["contractTerms"]
    ), "Expected 'tendererLegalForm' in lot contractTerms"
    assert lot["contractTerms"]["tendererLegalForm"] in [
        "First legal form requirement",
        "Second legal form requirement",
    ], "Unexpected tendererLegalForm content"


if __name__ == "__main__":
    pytest.main(["-v", "-s"])
