# converters/bt_197_bt_191_Tender.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Lookup table for justification codes
JUSTIFICATION_CODES = {
    "eo-int": {
        "description": "Commercial interests of an economic operator",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/eo-int",
    },
    "fair-comp": {
        "description": "Fair competition",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/fair-comp",
    },
    "law-enf": {
        "description": "Law enforcement",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/law-enf",
    },
    "oth-int": {
        "description": "Other public interest",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/oth-int",
    },
    "rd-ser": {
        "description": "Research and development (R&D) services",
        "uri": "http://publications.europa.eu/resource/authority/non-publication-justification/rd-ser",
    },
}


def parse_bt197_bt191_unpublished_justification_code(xml_content):
    """Parse the XML content to extract the unpublished justification code for the country origin.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed unpublished justification code data.
        None: If no relevant data is found.

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

    result = {"withheldInformation": []}

    lot_tenders = root.xpath(
        "//efac:NoticeResult/efac:LotTender",
        namespaces=namespaces,
    )

    for lot_tender in lot_tenders:
        lot_tender_id = lot_tender.xpath("cbc:ID/text()", namespaces=namespaces)
        reason_code = lot_tender.xpath(
            "efac:Origin/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cou-ori']/cbc:ReasonCode/text()",
            namespaces=namespaces,
        )

        if lot_tender_id and reason_code:
            code = reason_code[0]
            if code in JUSTIFICATION_CODES:
                withheld_info = {
                    "id": f"cou-ori-{lot_tender_id[0]}",
                    "field": "cou-ori",
                    "rationaleClassifications": [
                        {
                            "scheme": "eu-non-publication-justification",
                            "id": code,
                            "description": JUSTIFICATION_CODES[code]["description"],
                            "uri": JUSTIFICATION_CODES[code]["uri"],
                        },
                    ],
                }
                result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt197_bt191_unpublished_justification_code(
    release_json,
    unpublished_justification_code_data,
) -> None:
    """Merge the parsed unpublished justification code data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        unpublished_justification_code_data (dict): The parsed unpublished justification code data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not unpublished_justification_code_data:
        logger.warning(
            "No unpublished justification code data to merge for BT-197(BT-191)",
        )
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_justification_code_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item.get("id") == new_item["id"]),
            None,
        )
        if existing_item:
            existing_item.setdefault("rationaleClassifications", []).extend(
                new_item["rationaleClassifications"],
            )
        else:
            withheld_info.append(new_item)

    logger.info(
        "Merged unpublished justification code data for BT-197(BT-191): %d items",
        len(unpublished_justification_code_data["withheldInformation"]),
    )
