import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_foreign_subsidies_regulation(xml_content: str) -> dict | None:
    """Parses the XML content to extract the Foreign Subsidies Regulation (FSR) applicability.

    Args:
        xml_content (str): The XML content as a string.

    Returns:
        dict | None: A dictionary containing the parsed data or None if no lots are found.

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
    except etree.XMLSyntaxError:
        logger.exception("Failed to parse XML content")
        return None

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
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        if not lot_id:
            logger.warning("Lot ID not found")
            continue

        lot_id = lot_id[0]
        fsr_code = lot.xpath(
            "cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='fsr']/cbc:ExecutionRequirementCode/text()",
            namespaces=namespaces,
        )

        if fsr_code and fsr_code[0].lower() == "true":
            result["tender"]["lots"].append(
                {
                    "id": lot_id,
                    "coveredBy": ["EU-FSR"],
                }
            )

    return result if result["tender"]["lots"] else None


def merge_foreign_subsidies_regulation(
    release_json: dict, fsr_data: dict | None
) -> None:
    """Merges the parsed Foreign Subsidies Regulation (FSR) data into the existing release JSON structure.

    Args:
        release_json (dict): The existing release JSON structure.
        fsr_data (dict | None): The parsed FSR data.

    Returns:
        None

    """
    if not fsr_data:
        logger.warning("No Foreign Subsidies Regulation data to merge")
        return

    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in fsr_data["tender"]["lots"]:
        existing_lot = next(
            (lot for lot in existing_lots if lot["id"] == new_lot["id"]),
            None,
        )
        if existing_lot:
            if "coveredBy" not in existing_lot:
                existing_lot["coveredBy"] = new_lot["coveredBy"]
            else:
                existing_lot["coveredBy"].extend(new_lot["coveredBy"])
        else:
            existing_lots.append(new_lot)

    logger.info(
        "Merged Foreign Subsidies Regulation data for %d lots",
        len(fsr_data["tender"]["lots"]),
    )
