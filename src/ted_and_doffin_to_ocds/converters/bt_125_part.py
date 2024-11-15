# converters/bt_125_part.py

from lxml import etree
import logging
import json

logger = logging.getLogger(__name__)


def parse_previous_planning_identifier_part(xml_content):
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

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='part']",
        namespaces=namespaces,
    )
    logger.info("Found %d parts", len(parts))

    for part in parts:
        notice_refs = part.xpath(
            "cac:TenderingProcess/cac:noticeDocumentReference",
            namespaces=namespaces,
        )
        logger.info("Found %d notice references for part", len(notice_refs))

        for notice_ref in notice_refs:
            identifier = notice_ref.xpath(
                "cbc:ID[@schemeName='notice-id-ref']/text()",
                namespaces=namespaces,
            )
            part_identifier = notice_ref.xpath(
                "cbc:ReferencedDocumentInternalAddress/text()",
                namespaces=namespaces,
            )

            logger.info(
                "Identifier: %s, part Identifier: %s", identifier, part_identifier
            )

            if identifier and part_identifier:
                full_identifier = f"{identifier[0]}-{part_identifier[0]}"
                related_process = {
                    "id": str(related_process_id),
                    "relationship": ["planning"],
                    "scheme": "eu-oj",
                    "identifier": full_identifier,
                }
                result["relatedProcesses"].append(related_process)
                related_process_id += 1
                logger.info("Added related process for part: %s", related_process)

    logger.info(
        "Total related processes for parts: %d", len(result["relatedProcesses"])
    )
    return result if result["relatedProcesses"] else None


def merge_previous_planning_identifier_part(release_json, previous_planning_data):
    if not previous_planning_data:
        logger.warning("No Previous Planning Identifier (part) data to merge")
        return

    existing_related_processes = release_json.setdefault("relatedProcesses", [])

    for new_process in previous_planning_data["relatedProcesses"]:
        existing_process = next(
            (p for p in existing_related_processes if p["id"] == new_process["id"]),
            None,
        )
        if existing_process:
            existing_process.update(new_process)
        else:
            existing_related_processes.append(new_process)

    # Ensure the changes are reflected in the release_json object
    release_json["relatedProcesses"] = existing_related_processes

    logger.info(
        "Merged Previous Planning Identifier (part) data for %d related processes",
        len(previous_planning_data["relatedProcesses"]),
    )
    logger.info("Updated release_json: %s", json.dumps(release_json, indent=2))
