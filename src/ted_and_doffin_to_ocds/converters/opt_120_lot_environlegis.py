# converters/opt_120_lot_environlegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_environmental_legislation_url(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    result = {"tender": {"documents": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        env_docs = lot.xpath(
            "cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in env_docs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
            url = doc.xpath(
                "cac:Attachment/cac:ExternalReference/cbc:URI/text()",
                namespaces=namespaces,
            )

            if doc_id and url:
                result["tender"]["documents"].append(
                    {"id": doc_id[0], "url": url[0], "relatedLots": [lot_id]}
                )

    return result if result["tender"]["documents"] else None


def merge_environmental_legislation_url(release_json, env_legislation_data):
    if not env_legislation_data:
        logger.info("No environmental legislation URL data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_docs = tender.setdefault("documents", [])

    for new_doc in env_legislation_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_docs if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["url"] = new_doc["url"]
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(
                set(existing_doc["relatedLots"])
            )  # Remove duplicates
        else:
            existing_docs.append(new_doc)

    logger.info(
        "Merged environmental legislation URL data for %d documents",
        len(env_legislation_data["tender"]["documents"]),
    )
