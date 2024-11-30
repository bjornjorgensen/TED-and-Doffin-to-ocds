# converters/opt_130_part_employlegis.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_employment_legislation_url_part(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"documents": []}}

    parts = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']", namespaces=namespaces
    )

    for part in parts:
        empl_docs = part.xpath(
            "cac:TenderingTerms/cac:EmploymentLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in empl_docs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
            url = doc.xpath(
                "cac:Attachment/cac:ExternalReference/cbc:URI/text()",
                namespaces=namespaces,
            )

            if doc_id and url:
                result["tender"]["documents"].append({"id": doc_id[0], "url": url[0]})

    return result if result["tender"]["documents"] else None


def merge_employment_legislation_url_part(release_json, empl_legislation_data) -> None:
    if not empl_legislation_data:
        logger.info("No employment legislation URL data for parts to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in empl_legislation_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_docs if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["url"] = new_doc["url"]
        else:
            existing_docs.append(new_doc)

    logger.info(
        "Merged employment legislation URL data for %d documents (parts)",
        len(empl_legislation_data["tender"]["documents"]),
    )
