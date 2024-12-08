# converters/opt_100_contract.py

import logging
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)

NAMESPACES = {
    "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
    "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def parse_framework_notice_identifier(
    xml_content: str | bytes,
) -> dict[str, Any] | None:
    """Parse framework notice identifier information (OPT-100) from XML content.

    Gets notice reference information from settled contracts and creates
    corresponding RelatedProcess objects with framework relationships.

    Args:
        xml_content: XML content as string or bytes containing procurement data

    Returns:
        Dictionary containing contracts with related processes or None if no data found

    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

    try:
        root = etree.fromstring(xml_content)
        result = {"contracts": []}

        settled_contracts = root.xpath(
            "/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
            "efext:EformsExtension/efac:NoticeResult/efac:SettledContract",
            namespaces=NAMESPACES,
        )

        for contract in settled_contracts:
            try:
                contract_id = contract.xpath(
                    "cbc:ID[@schemeName='contract']/text()",
                    namespaces=NAMESPACES,
                )[0]

                notice_ref = contract.xpath(
                    "cac:NoticeDocumentReference/cbc:ID",
                    namespaces=NAMESPACES,
                )

                if contract_id and notice_ref:
                    notice_id = notice_ref[0]
                    scheme = notice_id.get("schemeName", "")
                    identifier = notice_id.text

                    contract_data = {
                        "id": contract_id,
                        "relatedProcesses": [
                            {
                                "id": "1",
                                "scheme": "ocid" if scheme == "ocds" else scheme,
                                "identifier": identifier,
                                "relationship": ["framework"],
                            }
                        ],
                    }

                    # Find award ID through LotResult
                    award_id = root.xpath(
                        f"/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/"
                        f"efext:EformsExtension/efac:NoticeResult/efac:LotResult"
                        f"[efac:SettledContract/cbc:ID[@schemeName='contract']/text()='{contract_id}']"
                        f"/cbc:ID[@schemeName='result']/text()",
                        namespaces=NAMESPACES,
                    )
                    if award_id:
                        contract_data["awardID"] = award_id[0]

                    result["contracts"].append(contract_data)

            except (IndexError, AttributeError) as e:
                logger.warning("Skipping incomplete contract data: %s", e)
                continue

        if result["contracts"]:
            return result

    except Exception:
        logger.exception("Error parsing framework notice identifiers")
        return None

    return None


def merge_framework_notice_identifier(
    release_json: dict[str, Any], framework_data: dict[str, Any] | None
) -> None:
    """Merge framework notice identifier information into the release JSON.

    Updates or creates contracts with related processes information.
    Preserves existing contract data while adding/updating related processes.

    Args:
        release_json: The target release JSON to update
        framework_data: The source data containing framework references to merge

    Returns:
        None

    """
    if not framework_data:
        logger.info("No framework notice identifier data to merge")
        return

    existing_contracts = release_json.setdefault("contracts", [])

    for new_contract in framework_data["contracts"]:
        existing_contract = next(
            (
                contract
                for contract in existing_contracts
                if contract["id"] == new_contract["id"]
            ),
            None,
        )
        if existing_contract:
            existing_related_processes = existing_contract.setdefault(
                "relatedProcesses", []
            )
            new_related_process = new_contract["relatedProcesses"][0]
            existing_related_process = next(
                (
                    rp
                    for rp in existing_related_processes
                    if rp["id"] == new_related_process["id"]
                ),
                None,
            )
            if existing_related_process:
                existing_related_process.update(new_related_process)
            else:
                existing_related_processes.append(new_related_process)

            if "awardID" in new_contract:
                existing_contract["awardID"] = new_contract["awardID"]
        else:
            existing_contracts.append(new_contract)

    logger.info(
        "Merged framework notice identifier data for %d contracts",
        len(framework_data["contracts"]),
    )
