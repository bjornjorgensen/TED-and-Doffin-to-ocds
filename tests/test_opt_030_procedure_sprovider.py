# tests/test_OPT_030_procedure_sprovider.py
from pathlib import Path
import pytest
import json
import sys
import tempfile

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    output_files = list(output_dir.glob("*.json"))
    assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_opt_030_procedure_sprovider_integration(tmp_path, temp_output_dir):
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

    result = run_main_and_get_result(xml_file, temp_output_dir)

    assert "parties" in result
    assert len(result["parties"]) == 2

    assert {"id": "ORG-0001", "roles": ["eSender"]} in result["parties"]

    assert {"id": "ORG-0002", "roles": ["procurementServiceProvider"]} in result[
        "parties"
    ]


if __name__ == "__main__":
    pytest.main()
