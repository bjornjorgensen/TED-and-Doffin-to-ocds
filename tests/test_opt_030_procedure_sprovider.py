# tests/test_OPT_030_procedure_sprovider.py
from pathlib import Path
import pytest
import json
import sys

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_030_procedure_sprovider_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:Contractingparty>
            <cac:party>
                <cac:ServiceProviderparty>
                    <cbc:ServiceTypeCode listName="organisation-role">ted-esen</cbc:ServiceTypeCode>
                    <cac:party>
                        <cac:partyIdentification>
                            <cbc:ID>ORG-0001</cbc:ID>
                        </cac:partyIdentification>
                    </cac:party>
                </cac:ServiceProviderparty>
            </cac:party>
        </cac:Contractingparty>
        <cac:Contractingparty>
            <cac:party>
                <cac:ServiceProviderparty>
                    <cbc:ServiceTypeCode listName="organisation-role">serv-prov</cbc:ServiceTypeCode>
                    <cac:party>
                        <cac:partyIdentification>
                            <cbc:ID>ORG-0002</cbc:ID>
                        </cac:partyIdentification>
                    </cac:party>
                </cac:ServiceProviderparty>
            </cac:party>
        </cac:Contractingparty>
    </root>
    """
    xml_file = tmp_path / "test_input_provided_service_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with Path("output.json").open() as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 2

    assert {"id": "ORG-0001", "roles": ["eSender"]} in result["parties"]

    assert {"id": "ORG-0002", "roles": ["procurementServiceProvider"]} in result[
        "parties"
    ]


if __name__ == "__main__":
    pytest.main()
