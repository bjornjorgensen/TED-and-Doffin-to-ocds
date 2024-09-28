# tests/test_OPT_301_part_EmployLegis.py

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_301_part_employlegis_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">PART-0001</cbc:ID>
            <cac:TenderingTerms>
                <cac:EmploymentLegislationDocumentReference>
                    <cbc:ID>Empl2</cbc:ID>
                    <cac:Attachment>
                        <cac:ExternalReference>
                            <cbc:URI>http://employment-legislation.gov.stat/part</cbc:URI>
                        </cac:ExternalReference>
                    </cac:Attachment>
                </cac:EmploymentLegislationDocumentReference>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_employlegis.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None
    assert "tender" in result
    assert "documents" in result["tender"]
    assert len(result["tender"]["documents"]) == 1
    document = result["tender"]["documents"][0]
    assert document["id"] == "Empl2"
    assert document["url"] == "http://employment-legislation.gov.stat/part"


if __name__ == "__main__":
    pytest.main()
