import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_dps_termination(xml_content: str | bytes) -> dict | None:
    """Parse dynamic purchasing system termination information from XML.

    Extract information about whether the dynamic purchasing system is terminated
    as defined in BT-119.

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
                            "dynamicPurchasingSystem": {
                                "status": "terminated"
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

    lot_results = root.xpath(
        "//efac:NoticeResult/efac:LotResult",
        namespaces=namespaces,
    )

    for lot_result in lot_results:
        dps_termination = lot_result.xpath(
            "efbc:DPSTerminationIndicator/text()",
            namespaces=namespaces,
        )

        if dps_termination and dps_termination[0].lower() == "true":
            lot_id = lot_result.xpath(
                "../efac:TenderLot/cbc:ID[@schemeName='Lot']/text()",
                namespaces=namespaces,
            )
            if lot_id:
                result["tender"]["lots"].append(
                    {
                        "id": lot_id[0],
                        "techniques": {
                            "dynamicPurchasingSystem": {"status": "terminated"}
                        },
                    }
                )

    return result if result["tender"]["lots"] else None


def merge_dps_termination(
    release_json: dict, dps_termination_data: dict | None
) -> None:
    """Merge DPS termination data into the OCDS release.

    Updates the release JSON in-place by adding or updating dynamic purchasing system
    information for each lot specified in the input data.

    Args:
        release_json: The main OCDS release JSON to be updated. Must contain
            a 'tender' object with a 'lots' array.
        dps_termination_data: The parsed DPS termination data
            in the same format as returned by parse_dps_termination().
            If None, no changes will be made.

    Returns:
        None: The function modifies release_json in-place.
    """
    if not dps_termination_data:
        logger.info("No DPS termination data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_lots = tender.setdefault("lots", [])

    for new_lot in dps_termination_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            techniques = existing_lot.setdefault("techniques", {})
            techniques["dynamicPurchasingSystem"] = new_lot["techniques"][
                "dynamicPurchasingSystem"
            ]
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged DPS termination data for %d lots",
        len(dps_termination_data["tender"]["lots"]),
    )
