# tests/test_BT_801_Lot.py
import sys, os, logging
import subprocess
import pytest
from lxml import etree

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import main

import logging
import pytest
from lxml import etree
from main import main

logging.basicConfig(level=logging.INFO)

def create_xml(lot_id, nda_value):
    return f"""
    <TenderStatus xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
        <cbc:IssueDate>2023-06-29</cbc:IssueDate>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">{lot_id}</cbc:ID>
            <cbc:ID schemeName="InternalIdentifier">internal-{lot_id}</cbc:ID>
            <cac:ProcurementProject>
                <cbc:Name>Test Lot Name</cbc:Name>
                <cbc:Description>Test Lot Description</cbc:Description>
                <cbc:MainNatureCode>goods</cbc:MainNatureCode>
            </cac:ProcurementProject>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="nda">{nda_value}</cbc:ExecutionRequirementCode>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </TenderStatus>
    """

@pytest.fixture
def mock_xml_file(tmp_path):
    def _create_xml_file(content):
        xml_file = tmp_path / "test.xml"
        xml_file.write_text(content)
        return str(xml_file)
    return _create_xml_file

def test_main_non_disclosure_agreement_true(mock_xml_file):
    xml_content = create_xml("LOT-0001", "true")
    xml_file = mock_xml_file(xml_content)
    ocid_prefix = "ocds-123456"

    logging.info(f"Test XML content: {xml_content}")
    result = main(xml_file, ocid_prefix)

    logging.info(f"Test result: {result}")

    assert result is not None, "main function returned None"
    assert "tender" in result, "tender key not found in result"
    assert "lots" in result["tender"], "lots key not found in tender"
    assert len(result["tender"]["lots"]) == 1, f"unexpected number of lots: {len(result['tender']['lots'])}"
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001", f"unexpected lot id: {lot['id']}"
    assert lot["title"] == "Test Lot Name", f"unexpected lot title: {lot['title']}"
    assert "contractTerms" in lot, f"contractTerms not found in lot. Lot content: {lot}"
    assert lot["contractTerms"]["hasNonDisclosureAgreement"] is True, "hasNonDisclosureAgreement is not True"
    assert "identifiers" in lot, f"identifiers not found in lot. Lot content: {lot}"
    assert lot["identifiers"][0]["id"] == "internal-LOT-0001", f"unexpected internal identifier: {lot['identifiers'][0]['id']}"

def test_main_non_disclosure_agreement_false(mock_xml_file):
    xml_content = create_xml("LOT-0002", "false")
    xml_file = mock_xml_file(xml_content)
    ocid_prefix = "ocds-123456"

    result = main(xml_file, ocid_prefix)

    assert result is not None, "main function returned None"
    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0002"
    assert "contractTerms" in lot
    assert lot["contractTerms"]["hasNonDisclosureAgreement"] is False
    assert "identifiers" in lot
    assert lot["identifiers"][0]["id"] == "internal-LOT-0002"