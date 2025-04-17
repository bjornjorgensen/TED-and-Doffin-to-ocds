# tests/test_bt_739_organization_touchpoint.py
import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add the parent directory to sys.path to import main
sys.path.append(str(Path(__file__).parent.parent))
from src.ted_and_doffin_to_ocds.main import configure_logging, main


@pytest.fixture
def temp_output_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def run_main_and_get_result(xml_file, output_dir):
    main(str(xml_file), str(output_dir), "ocds-test-prefix", "test-scheme")
    # Get the stem of the input file (filename without extension)
    input_file_stem = Path(xml_file).stem
    # Look specifically for the output file that matches the input file name
    output_files = list(output_dir.glob(f"{input_file_stem}_release_0.json"))
    assert len(output_files) == 1, f"Expected 1 output file for {input_file_stem}, got {len(output_files)}"
    with output_files[0].open() as f:
        return json.load(f)


def test_bt_739_organization_touchpoint_integration(
    tmp_path, temp_output_dir
) -> None:
    """
    Test the mapping of BT-739-Organization-TouchPoint (Contact Fax) from TED to OCDS format.
    
    BT-739 maps the organization's fax number from the XPath:
    /*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:Organizations/efac:Organization/efac:TouchPoint/cac:Contact/cbc:Telefax
    
    Expected mapping: organization.contactPoint.faxNumber
    """
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
          xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
          xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
          xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
          xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
          xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
        <ext:UBLExtensions>
            <ext:UBLExtension>
                <ext:ExtensionContent>
                    <efext:EformsExtension>
                        <efac:Organizations>
                            <efac:Organization>
                                <efac:Company>
                                    <cac:PartyLegalEntity>
                                        <cbc:companyID>AB12345</cbc:companyID>
                                    </cac:PartyLegalEntity>
                                </efac:Company>
                                <efac:TouchPoint>
                                    <cac:PartyIdentification>
                                        <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                    </cac:PartyIdentification>
                                    <cac:Contact>
                                        <cbc:Telefax>(+33) 2 34 56 78 91</cbc:Telefax>
                                    </cac:Contact>
                                </efac:TouchPoint>
                            </efac:Organization>
                        </efac:Organizations>
                    </efext:EformsExtension>
                </ext:ExtensionContent>
            </ext:UBLExtension>
        </ext:UBLExtensions>
    </ContractAwardNotice>
    """
    xml_file = tmp_path / "test_input_touchpoint_contact_fax.xml"
    xml_file.write_text(xml_content)

    # Execute the transformation
    result = run_main_and_get_result(xml_file, temp_output_dir)

    # Validate the output structure
    assert "parties" in result, "Expected 'parties' in result"
    assert len(result["parties"]) == 1, f"Expected 1 party, got {len(result['parties'])}"

    # Check the party details
    party = result["parties"][0]
    
    # Check TouchPoint ID is correctly mapped
    assert party["id"] == "TPO-0001", f"Expected party id 'TPO-0001', got {party['id']}"
    
    # Check contactPoint and faxNumber mapping from BT-739
    assert "contactPoint" in party, "Expected 'contactPoint' in party"
    assert "faxNumber" in party["contactPoint"], "Expected 'faxNumber' in contactPoint"
    assert party["contactPoint"]["faxNumber"] == "(+33) 2 34 56 78 91", \
           f"Expected faxNumber '(+33) 2 34 56 78 91', got {party['contactPoint']['faxNumber']}"
    
    # Validate faxNumber format meets pattern requirement
    # Pattern: ^((\(\+?[0-9]+\))|\+?[0-9]+)( - |-| )?(((\(\d+\))|\d+)( - |-| )?)*(\d+)( )?$
    fax_number = party["contactPoint"]["faxNumber"]
    import re
    pattern = r"^((\(\+?[0-9]+\))|\+?[0-9]+)( - |-| )?(((\(\d+\))|\d+)( - |-| )?)*(\d+)( )?$"
    assert re.match(pattern, fax_number), f"Fax number '{fax_number}' does not match required pattern"
    
    # Check company identifier mapping
    assert "identifier" in party, "Expected 'identifier' in party"
    assert party["identifier"]["id"] == "AB12345", \
           f"Expected identifier id 'AB12345', got {party['identifier']['id']}"
    assert party["identifier"]["scheme"] == "GB-COH", \
           f"Expected identifier scheme 'GB-COH', got {party['identifier']['scheme']}"


def test_bt_739_organization_touchpoint_different_formats(
    tmp_path, temp_output_dir
) -> None:
    """
    Test different valid formats for BT-739-Organization-TouchPoint (Contact Fax).
    Tests the pattern: "^((\\(\\+?[0-9]+\\))|\\+?[0-9]+)( - |-| )?(((\\(\\d+\\))|\\d+)( - |-| )?)*(\\d+)( )?$"
    """
    
    # Test various valid fax number formats
    test_cases = [
        "+44 1234 567890",
        "(+44) 1234-567890",
        "+44-1234-567890",
        "+44 - 1234 - 567890",
        "(+44) (1234) 567890"
    ]
    
    for fax_number in test_cases:
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <ContractAwardNotice xmlns="urn:oasis:names:specification:ubl:schema:xsd:ContractAwardNotice-2"
              xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
              xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
              xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
              xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
              xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1">
            <ext:UBLExtensions>
                <ext:UBLExtension>
                    <ext:ExtensionContent>
                        <efext:EformsExtension>
                            <efac:Organizations>
                                <efac:Organization>
                                    <efac:Company>
                                        <cac:PartyLegalEntity>
                                            <cbc:companyID>AB12345</cbc:companyID>
                                        </cac:PartyLegalEntity>
                                    </efac:Company>
                                    <efac:TouchPoint>
                                        <cac:PartyIdentification>
                                            <cbc:ID schemeName="touchpoint">TPO-0001</cbc:ID>
                                        </cac:PartyIdentification>
                                        <cac:Contact>
                                            <cbc:Telefax>{fax_number}</cbc:Telefax>
                                        </cac:Contact>
                                    </efac:TouchPoint>
                                </efac:Organization>
                            </efac:Organizations>
                        </efext:EformsExtension>
                    </ext:ExtensionContent>
                </ext:UBLExtension>
            </ext:UBLExtensions>
        </ContractAwardNotice>
        """
        xml_file = tmp_path / f"test_input_touchpoint_fax_{fax_number.replace(' ', '_').replace('(', '').replace(')', '').replace('+', '').replace('-', '')}.xml"
        xml_file.write_text(xml_content)
        
        # Execute the transformation
        result = run_main_and_get_result(xml_file, temp_output_dir)
        
        # Verify the fax number is correctly mapped
        party = result["parties"][0]
        assert party["contactPoint"]["faxNumber"] == fax_number, \
               f"Expected faxNumber '{fax_number}', got {party['contactPoint']['faxNumber']}"

if __name__ == "__main__":
    pytest.main(["-v", "-s"])
