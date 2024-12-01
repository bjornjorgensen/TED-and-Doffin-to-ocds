import pytest

from ted_and_doffin_to_ocds.converters.bt_682_tender import (
    merge_foreign_subsidies_measures,
    parse_foreign_subsidies_measures,
)


def test_parse_foreign_subsidies_measures():
    xml_content = """
    <ext:UBLExtensions xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
                       xmlns:efext="http://data.europa.eu/p27/eforms-ubl-extensions/1"
                       xmlns:efac="http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1"
                       xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
                       xmlns:efbc="http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1">
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <efext:EformsExtension>
                    <efac:NoticeResult>
                        <efac:LotTender>
                            <cbc:ID schemeName="tender">TEN-0001</cbc:ID>
                            <efbc:ForeignSubsidiesMeasuresCode listName="foreign-subsidy-measure-conclusion">fsr-adm-clos</efbc:ForeignSubsidiesMeasuresCode>
                            <efac:TenderLot>
                                <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
                            </efac:TenderLot>
                        </efac:LotTender>
                    </efac:NoticeResult>
                </efext:EformsExtension>
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    """
    expected_result = {
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "foreignSubsidyMeasures": "fsr-adm-clos",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }
    result = parse_foreign_subsidies_measures(xml_content)
    assert result == expected_result


def test_merge_foreign_subsidies_measures():
    release_json = {
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                }
            ]
        }
    }
    measures_data = {
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "foreignSubsidyMeasures": "fsr-adm-clos",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }
    merge_foreign_subsidies_measures(release_json, measures_data)
    expected_result = {
        "bids": {
            "details": [
                {
                    "id": "TEN-0001",
                    "foreignSubsidyMeasures": "fsr-adm-clos",
                    "relatedLots": ["LOT-0001"],
                }
            ]
        }
    }
    assert release_json == expected_result


if __name__ == "__main__":
    pytest.main()
