# tests/test_OPT_301_part_ReviewOrg.py

import pytest
import sys
from pathlib import Path

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


def test_opt_301_part_revieworg_integration(tmp_path):
    xml_content = """
    <root xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
        <cac:ProcurementProjectLot>
            <cbc:ID schemeName="part">1</cbc:ID>
            <cac:TenderingTerms>
                <cac:AppealTerms>
                    <cac:AppealReceiverparty>
                        <cac:partyIdentification>
                            <cbc:ID schemeName="touchpoint">TPO-0003</cbc:ID>
                        </cac:partyIdentification>
                    </cac:AppealReceiverparty>
                </cac:AppealTerms>
            </cac:TenderingTerms>
        </cac:ProcurementProjectLot>
    </root>
    """
    xml_file = tmp_path / "test_input_part_revieworg.xml"
    xml_file.write_text(xml_content)

    result = main(str(xml_file), "ocds-test-prefix")

    assert result is not None
    assert "parties" in result
    assert len(result["parties"]) == 1
    party = result["parties"][0]
    assert party["id"] == "TPO-0003"
    assert "roles" in party
    assert "reviewBody" in party["roles"]


if __name__ == "__main__":
    pytest.main()