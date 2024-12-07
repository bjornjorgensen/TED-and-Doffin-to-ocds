import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    "efbc": "http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1",
}


def parse_kilometers_public_transport(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """
    Parse kilometers public transport information (OPP-080) from XML content.

    Gets public transportation cumulated distance from lot tenders and maps them
    to corresponding contract's publicPassengerTransportServicesKilometers field.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing contracts with kilometers info or None if no data found
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        lot_tenders = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:LotTender",
            namespaces=NAMESPACES,
        )

        for lot_tender in lot_tenders:
            try:
                tender_id = lot_tender.xpath(
                    "cbc:ID[@schemeName='tender']/text()",
                    namespaces=NAMESPACES,
                )[0]

                kilometers = lot_tender.xpath(
                    "efbc:PublicTransportationCumulatedDistance/text()",
                    namespaces=NAMESPACES,
                )

                if tender_id and kilometers:
                    kilometers_value = int(kilometers[0])

                    # Find corresponding contract through SettledContract
                    contract = root.xpath(
                        f"/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
                        f"efext:EformsExtension/efac:NoticeResult/efac:SettledContract"
                        f"[efac:LotTender/cbc:ID[@schemeName='tender']/text()='{tender_id}']",
                        namespaces=NAMESPACES,
                    )

                    if contract:
                        contract_id = contract[0].xpath(
                            "cbc:ID[@schemeName='contract']/text()",
                            namespaces=NAMESPACES,
                        )[0]

                        # Find award ID through LotResult
                        award_id = root.xpath(
                            f"/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
                            f"efext:EformsExtension/efac:NoticeResult/efac:LotResult"
                            f"[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']"
                            f"/cbc:ID[@schemeName='result']/text()",
                            namespaces=NAMESPACES,
                        )

                        contract_data = {
                            "id": contract_id,
                            "publicPassengerTransportServicesKilometers": kilometers_value,
                        }
                        if award_id:
                            contract_data["awardID"] = award_id[0]

                        result["contracts"].append(contract_data)

            except (IndexError, AttributeError, ValueError) as e:
                logger.warning("Skipping incomplete lot tender data: %s", e)
                continue

        if result["contracts"]:
            return result

    except Exception:
        logger.exception("Error parsing public transport kilometers")
        return None

    return None


def merge_kilometers_public_transport(
    release_json: dict[str, Any], kilometers_data: dict[str, Any] | None
) -> None:
    """
    Merge kilometers public transport information into the release JSON.

    Updates or creates contracts with kilometers information.
    Preserves existing contract data while adding/updating kilometers info.

    Args:
        release_json: The target release JSON to update
        kilometers_data: The source data containing kilometers info to merge

    Returns:
        None
    """
    if not kilometers_data:
        logger.warning("No public transport kilometers data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in kilometers_data["contracts"]:
        existing_contract = next(
            (c for c in existing_contracts if c["id"] == new_contract["id"]),
            None,
        )
        if existing_contract:
            existing_contract.update(new_contract)
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged public transport kilometers for %d contracts",
        len(kilometers_data["contracts"]),
    )
