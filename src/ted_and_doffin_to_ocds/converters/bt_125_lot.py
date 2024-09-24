# converters/bt_125_Lot.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_previous_planning_identifier_lot(xml_content):
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
        notice_refs = lot.xpath(
            "cac:TenderingProcess/cac:noticeDocumentReference",
            namespaces=namespaces,
        )

        for notice_ref in notice_refs:
            identifier = notice_ref.xpath("cbc:ID/text()", namespaces=namespaces)
            part_identifier = notice_ref.xpath(
                "cbc:ReferencedDocumentInternalAddress/text()",
                namespaces=namespaces,
            )

            if identifier:
                related_process = {
                    "id": str(related_process_id),
                    "relationship": ["planning"],
                    "scheme": "eu-oj",
                    "identifier": identifier[0],
                }
                if part_identifier:
                    related_process["relatedLots"] = [part_identifier[0]]

                result["relatedProcesses"].append(related_process)
                related_process_id += 1

    return result if result["relatedProcesses"] else None


def merge_previous_planning_identifier_lot(release_json, previous_planning_data):
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
