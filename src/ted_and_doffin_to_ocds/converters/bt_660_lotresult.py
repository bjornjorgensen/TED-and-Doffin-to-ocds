# converters/bt_660_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_reestimated_value(xml_content):
    """
    Parse the XML content to extract the framework re-estimated value for each lot result.

    Args:
        xml_content (str or bytes): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed framework re-estimated value data.
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
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

    result = {"awards": []}

    lot_results = root.xpath(
        "//efac:noticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        award_id = lot_result.xpath(
            "cbc:ID[@schemeName='result']/text()",
            namespaces=namespaces,
        )
        reestimated_value = lot_result.xpath(
            "efac:FrameworkAgreementValues/efbc:ReestimatedValueAmount/text()",
            namespaces=namespaces,
        )
        currency = lot_result.xpath(
            "efac:FrameworkAgreementValues/efbc:ReestimatedValueAmount/@currencyID",
            namespaces=namespaces,
        )
        related_lot = lot_result.xpath(
            "efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
            namespaces=namespaces,
        )

        if award_id and reestimated_value and currency:
            award = {
                "id": award_id[0],
                "estimatedValue": {
                    "amount": float(reestimated_value[0]),
                    "currency": currency[0],
                },
            }
            if related_lot:
                award["relatedLots"] = [related_lot[0]]
            result["awards"].append(award)

    return result if result["awards"] else None


def merge_framework_reestimated_value(release_json, framework_reestimated_value_data):
    """
    Merge the parsed framework re-estimated value data into the main OCDS release JSON.

    This function updates the existing awards in the release JSON with the
    framework re-estimated value information. If an award doesn't exist, it adds a new award to the release.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        framework_reestimated_value_data (dict): The parsed framework re-estimated value data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not framework_reestimated_value_data:
        logger.warning("No Framework Re-estimated Value data to merge")
        return

    existing_awards = release_json.setdefault("awards", [])

    for new_award in framework_reestimated_value_data["awards"]:
        existing_award = next(
            (award for award in existing_awards if award["id"] == new_award["id"]),
            None,
        )
        if existing_award:
            existing_award["estimatedValue"] = new_award["estimatedValue"]
            if "relatedLots" in new_award:
                existing_award.setdefault("relatedLots", []).extend(
                    new_award["relatedLots"],
                )
                existing_award["relatedLots"] = list(
                    set(existing_award["relatedLots"]),
                )  # Remove duplicates
        else:
            existing_awards.append(new_award)

    logger.info(
        f"Merged Framework Re-estimated Value data for {len(framework_reestimated_value_data['awards'])} awards",
    )
