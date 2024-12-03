# converters/bt_111_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_framework_buyer_categories(xml_content: str | bytes) -> dict | None:
    """Parse framework agreement buyer categories from XML for each lot.

    Extract information about additional categories of buyers participating in the
    framework agreement as defined in BT-111.

    Args:
        xml_content: The XML content to parse, either as a string or bytes.

    Returns:
        A dictionary containing the parsed data in OCDS format with the following structure:
        {
            "tender": {
                "lots": [
                    {
                        "id": str,
                        "techniques": {
                            "frameworkAgreement": {
                                "buyerCategories": str
                            }
                        }
                    }
                ]
            }
        }
        Returns None if no relevant data is found.

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

    result = {"tender": {"lots": []}}
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        buyer_categories = lot.xpath(
            ".//cac:TenderingProcess/cac:FrameworkAgreement/cac:SubsequentProcessTenderRequirement[cbc:Name/text()='buyer-categories']/cbc:Description/text()",
            namespaces=namespaces,
        )

        if buyer_categories:
            lot_data = {
                "id": lot_id,
                "techniques": {
                    "frameworkAgreement": {"buyerCategories": buyer_categories[0]},
                },
            }
            result["tender"]["lots"].append(lot_data)

    return result if result["tender"]["lots"] else None


def merge_framework_buyer_categories(
    release_json: dict, framework_buyer_categories_data: dict | None
) -> None:
    """Merge framework buyer categories data into the OCDS release.

    Updates the release JSON in-place by adding or updating framework agreement
    information for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        framework_buyer_categories_data: The parsed buyer categories data
            in the same format as returned by parse_framework_buyer_categories().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not framework_buyer_categories_data:
        logger.warning("No Framework buyer Categories data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in framework_buyer_categories_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("techniques", {}).setdefault(
                "frameworkAgreement",
                {},
            ).update(new_lot["techniques"]["frameworkAgreement"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Framework buyer Categories data for %d lots",
        len(framework_buyer_categories_data["tender"]["lots"]),
    )
