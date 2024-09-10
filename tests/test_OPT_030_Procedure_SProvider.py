# tests/test_OPT_030_Procedure_SProvider.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_030_procedure_sprovider_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ContractingParty>
            <cac:Party>
                <cac:ServiceProviderParty>
                    <cbc:ServiceTypeCode listName="organisation-role">ted-esen</cbc:ServiceTypeCode>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID>ORG-0001</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:Party>
                </cac:ServiceProviderParty>
            </cac:Party>
        </cac:ContractingParty>
        <cac:ContractingParty>
            <cac:Party>
                <cac:ServiceProviderParty>
                    <cbc:ServiceTypeCode listName="organisation-role">serv-prov</cbc:ServiceTypeCode>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID>ORG-0002</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:Party>
                </cac:ServiceProviderParty>
            </cac:Party>
        </cac:ContractingParty>
    </root>
    """
    xml_file = tmp_path / "test_input_provided_service_type.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open("output.json") as f:
        result = json.load(f)

    assert "parties" in result
    assert len(result["parties"]) == 2

    assert {"id": "ORG-0001", "roles": ["eSender"]} in result["parties"]

    assert {"id": "ORG-0002", "roles": ["procurementServiceProvider"]} in result[
        "parties"
    ]


if __name__ == "__main__":
    pytest.main()
