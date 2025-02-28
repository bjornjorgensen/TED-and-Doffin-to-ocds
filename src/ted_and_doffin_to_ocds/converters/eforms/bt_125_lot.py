# converters/bt_125_Lot.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_previous_planning_identifier_lot(
    xml_content: str | bytes,
) -> dict | None:
    """Parse the previous planning identifier information from lot-level XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing lot information

    Returns:
        Optional[Dict]: Dictionary containing related processes information, or None if no data found
        The structure follows the format:
        {
            "relatedProcesses": [
                {
                    "id": str,
                    "relationship": ["planning"],
                    "scheme": "eu-notice-id-ref",
                    "identifier": str,
                    "relatedLots": [str] # optional
                }
            ]
        }

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

    result = {"relatedProcesses": []}
    related_process_id = 1

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)
        lot_id = lot_id[0] if lot_id else None
        
        notice_refs = lot.xpath(
            "cac:TenderingProcess/cac:NoticeDocumentReference",
            namespaces=namespaces,
        )

        for notice_ref in notice_refs:
            identifier = notice_ref.xpath(
                "cbc:ID[@schemeName='notice-id-ref']/text()",
                namespaces=namespaces,
            )
            
            # Check if identifier matches the required pattern
            if identifier:
                # Pattern validation could be added here if needed
                # Pattern: ^([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}-(0[1-9]|[1-9]\d)|(\d{1,8})-(19|20)\d\d)$
                
                related_process = {
                    "id": str(related_process_id),
                    "relationship": ["planning"],
                    "scheme": "eu-notice-id-ref",
                    "identifier": identifier[0],
                }
                
                if lot_id:
                    related_process["relatedLots"] = [lot_id]

                result["relatedProcesses"].append(related_process)
                related_process_id += 1

    return result if result["relatedProcesses"] else None


def merge_previous_planning_identifier_lot(
    release_json: dict, previous_planning_data: dict | None
) -> None:
    """Merge previous planning identifier data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        previous_planning_data (Optional[Dict]): The source data containing related processes
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        relatedProcesses field with new planning identifiers.

    """
    if not previous_planning_data:
        logger.warning("No Previous Planning Identifier (Lot) data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])

    for new_process in previous_planning_data["relatedProcesses"]:
        existing_process = next(
            (
                p
                for p in existing_related_processes
                if p["identifier"] == new_process["identifier"]
            ),
            None,
        )
        if existing_process:
            if "relatedLots" in new_process:
                existing_process.setdefault("relatedLots", []).extend(
                    new_process["relatedLots"],
                )
                existing_process["relatedLots"] = list(
                    set(existing_process["relatedLots"]),
                )
        else:
            existing_related_processes.append(new_process)

    logger.info(
        "Merged Previous Planning Identifier (Lot) data for %d related processes",
        len(previous_planning_data["relatedProcesses"]),
    )
