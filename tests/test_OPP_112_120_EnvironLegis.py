# tests/test_OPP_112_120_EnvironLegis.py

import pytest
import json
import os
import sys

# Add the parent directory to sys.path to import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import main

def test_opp_112_120_environ_legis_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EnvironmentalLegislationDocumentReference>
                    <cbc:ID>Env1</cbc:ID>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>http://environmental-legislation.gov.stat/lot</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:EnvironmentalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="Part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EnvironmentalLegislationDocumentReference>
                    <cbc:ID>Env2</cbc:ID>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>http://environmental-legislation.gov.stat/part</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:EnvironmentalLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_environmental_legislation.xml"
    xml_file.write_text(xml_content)

    main(str(xml_file), "ocds-test-prefix")

    with open('output.json', 'r') as f:
        result = json.load(f)

    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 2

    lot_doc = next((doc for doc in result["tender"]["documents"] if doc["id"] == "Env1"), None)
    assert lot_doc is not None
    assert lot_doc["documentType"] == "legislation"
    assert lot_doc["url"] == "http://environmental-legislation.gov.stat/lot"
    assert "relatedLots" in lot_doc
    assert lot_doc["relatedLots"] == ["LOT-0001"]

    part_doc = next((doc for doc in result["tender"]["documents"] if doc["id"] == "Env2"), None)
    assert part_doc is not None
    assert part_doc["documentType"] == "legislation"
    assert part_doc["url"] == "http://environmental-legislation.gov.stat/part"
    assert "relatedLots" not in part_doc

if __name__ == "__main__":
    pytest.main()