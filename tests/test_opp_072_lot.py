# tests/test_OPP_072_Lot.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opp_072_lot_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="customer-service">clean</cbc:ExecutionRequirementCode>
                    <cbc:Description>Cleanliness standards for trains and stations</cbc:Description>
                </cac:ContractExecutionRequirement>
                <cac:ContractExecutionRequirement>
                    <cbc:ExecutionRequirementCode listName="customer-service">info</cbc:ExecutionRequirementCode>
                    <cbc:Description>Information provision requirements</cbc:Description>
                </cac:ContractExecutionRequirement>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_quality_target_description.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "tender" in result
    assert "lots" in result["tender"]
    assert len(result["tender"]["lots"]) == 1
    lot = result["tender"]["lots"][0]
    assert lot["id"] == "LOT-0001"
    assert "contractTerms" in lot
    assert "customerServices" in lot["contractTerms"]
    assert len(lot["contractTerms"]["customerServices"]) == 2

    clean_service = next(
        (
            service
            for service in lot["contractTerms"]["customerServices"]
            if service["type"] == "clean"
        ),
        None,
    )
    assert clean_service is not None
    assert clean_service["type"] == "clean"
    assert (
        clean_service["description"] == "Cleanliness standards for trains and stations"
    )
    assert "name" in clean_service  # Check that name exists, but don't assert its value

    info_service = next(
        (
            service
            for service in lot["contractTerms"]["customerServices"]
            if service["type"] == "info"
        ),
        None,
    )
    assert info_service is not None
    assert info_service["type"] == "info"
    assert info_service["description"] == "Information provision requirements"
    assert "name" in info_service  # Check that name exists, but don't assert its value


if __name__ == "__main__":
    pytest.main()