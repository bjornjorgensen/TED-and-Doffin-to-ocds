# converters/bt_754_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_accessibility_criteria(xml_content: str | bytes) -> dict | None:
    """Parse the XML content to extract the accessibility criteria information for each lot.

    Args:
        xml_content (Union[str, bytes]): The XML content to parse.

    Returns:
        Optional[Dict]: A dictionary containing the parsed data, or None if no relevant data is found.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
    }

    result: dict[str, dict[str, list]] = {"tender": {"lots": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id: str = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        accessibility_code = lot.xpath(
            "cac:ProcurementProject/cac:ProcurementAdditionalType[cbc:ProcurementTypeCode/@listName='accessibility']/cbc:ProcurementTypeCode/text()",
            namespaces=namespaces,
        )

        lot_data: dict[str, str | bool | None] = {
            "id": lot_id,
            "hasAccessibilityCriteria": False,
            "noAccessibilityCriteriaRationale": None,
        }

        if accessibility_code:
            code = accessibility_code[0]
            if code == "inc":
                lot_data["hasAccessibilityCriteria"] = True
            elif code == "n-inc":
                lot_data["noAccessibilityCriteriaRationale"] = (
                    "Procurement is not intended for use by natural persons"
                )

        result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_accessibility_criteria(release_json: dict, parsed_data: dict | None) -> None:
    """Merge the parsed accessibility criteria data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        parsed_data (Optional[Dict]): The parsed accessibility criteria data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not parsed_data:
        logger.warning("No Accessibility Criteria data to merge")
        return

    tender_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in parsed_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in tender_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot["hasAccessibilityCriteria"] = new_lot[
                "hasAccessibilityCriteria"
            ]
            if new_lot["noAccessibilityCriteriaRationale"]:
                existing_lot["noAccessibilityCriteriaRationale"] = new_lot[
                    "noAccessibilityCriteriaRationale"
                ]
        else:
            tender_lots.append(new_lot)

    logger.info(
        "Merged Accessibility Criteria data for %d lots",
        len(parsed_data["tender"]["lots"]),
    )