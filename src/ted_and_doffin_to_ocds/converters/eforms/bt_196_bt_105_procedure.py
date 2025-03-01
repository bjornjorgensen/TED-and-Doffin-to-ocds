# converters/bt_196_bt_105_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_bt196_bt105_unpublished_justification(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the XML content to extract procedure type unpublished justification.

    Processes XML content to find unpublished justification related to procedure type
    and creates a structured dictionary containing withheld information.

    Args:
        xml_content: The XML content to parse, either as string or bytes.

    Returns:
        Optional[Dict]: A dictionary containing withheld information with structure:
            {
                "withheldInformation": [
                    {
                        "field": str,
                        "rationale": str or dict
                    }
                ]
            }
        Returns None if no relevant data is found.
        For multilingual text, rationale will be a dict with language codes as keys.

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

    xpath_query = (
        "/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension"
        "/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy"
        "[efbc:FieldIdentifierCode/text()='pro-typ']"
        "/efbc:ReasonDescription"
    )

    reason_description_elements = root.xpath(xpath_query, namespaces=namespaces)

    result = {"withheldInformation": []}
    if reason_description_elements:
        rationale = {}
        single_value = None

        for element in reason_description_elements:
            lang_id = element.get("languageID")
            text = element.text

            if lang_id:
                rationale[lang_id] = text
            else:
                single_value = text

        withheld_info = {
            "field": "pro-typ",
            "rationale": rationale if rationale else single_value,
        }
        result["withheldInformation"].append(withheld_info)

    return result if result["withheldInformation"] else None


def merge_bt196_bt105_unpublished_justification(
    release_json: dict, unpublished_justification_data: dict | None
) -> None:
    """Merge the parsed unpublished justification data into the main OCDS release JSON.

    Takes the unpublished justification data and merges it into the main OCDS release JSON
    by updating existing withheld information items with matching field values.

    Args:
        release_json: The main OCDS release JSON to be updated.
        unpublished_justification_data: The parsed unpublished justification data to be merged.
            Should contain a 'withheldInformation' list of dictionaries with rationale.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not unpublished_justification_data:
        logger.warning("No unpublished justification data to merge")
        return

    withheld_info = release_json.setdefault("withheldInformation", [])

    for new_item in unpublished_justification_data["withheldInformation"]:
        existing_item = next(
            (item for item in withheld_info if item["field"] == new_item["field"]),
            None,
        )
        if existing_item:
            existing_item["rationale"] = new_item["rationale"]
        else:
            withheld_info.append(new_item)

    logger.info("Merged unpublished justification data")
