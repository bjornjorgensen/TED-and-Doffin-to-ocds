# tests/test_bt_11_procedure_buyer.py
import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_11_procedure_buyer_integration(
    tmp_path, temp_output_dir
) -> None:
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cbc:ID>notice-1</cbc:ID>
        <cbc:ContractFolderID>cf-1</cbc:ContractFolderID>
        <cac:Contractingparty>
            <cac:party>
                <cac:partyIdentification>
                    <cbc:ID schemeName="organization">ORG-0001</cbc:ID>
                </cac:partyIdentification>
            </cac:party>
            <cac:ContractingpartyType>
                <cbc:partyTypeCode listName="buyer-legal-type">body-pl</cbc:partyTypeCode>
            </cac:ContractingpartyType>
        </cac:Contractingparty>
    </ContractAwardNotice>
    """

    # Create input XML file
    xml_file = tmp_path / "test_input_buyer_legal_type.xml"
    xml_file.write_text(xml_content)

    # Run main and get result
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Verify the results
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "ORG-0001"
    assert "details" in party
    assert "classifications" in party["details"]
    assert len(party["details"]["classifications"]) == 1
    classification = party["details"]["classifications"][0]
    assert classification["scheme"] == "TED_CA_TYPE"
    assert classification["id"] == "body-pl"
    assert classification["description"] == "Body governed by public law"


if __name__ == "__main__":
    pytest.main(["-v"])
