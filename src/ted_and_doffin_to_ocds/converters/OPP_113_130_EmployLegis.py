# converters/OPP_113_130_EmployLegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_employment_legislation(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")

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

    result = {"tender": {"documents": []}}

    # Process Lot-specific employment legislation
    lot_employ_docs = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:EmploymentLegislationDocumentReference",
        namespaces=namespaces,
    )

    for doc in lot_employ_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        url = doc.xpath(
            "cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces
        )
        lot_id = doc.xpath("../../cbc:ID/text()", namespaces=namespaces)

        if doc_id:
            document = {
                "id": doc_id[0],
                "documentType": "legislation",
                "relatedLots": [lot_id[0]] if lot_id else [],
            }
            if url:
                document["url"] = url[0]
            result["tender"]["documents"].append(document)

    # Process Part-specific employment legislation
    part_employ_docs = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Part']/cac:TenderingTerms/cac:EmploymentLegislationDocumentReference",
        namespaces=namespaces,
    )

    for doc in part_employ_docs:
        doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
        url = doc.xpath(
            "cac:Attachment/cac:ExternalReference/cbc:URI/text()", namespaces=namespaces
        )

        if doc_id:
            document = {"id": doc_id[0], "documentType": "legislation"}
            if url:
                document["url"] = url[0]
            result["tender"]["documents"].append(document)

    return result if result["tender"]["documents"] else None


def merge_employment_legislation(release_json, employment_legislation_data):
    if not employment_legislation_data:
        logger.warning("No Employment Legislation data to merge")
        return

    tender = release_json.setdefault("tender", {})
    existing_documents = tender.setdefault("documents", [])

    for new_doc in employment_legislation_data["tender"]["documents"]:
        existing_doc = next(
            (doc for doc in existing_documents if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc.update(new_doc)
            if "relatedLots" in new_doc:
                existing_doc.setdefault("relatedLots", []).extend(
                    lot
                    for lot in new_doc["relatedLots"]
                    if lot not in existing_doc.get("relatedLots", [])
                )
        else:
            existing_documents.append(new_doc)

    logger.info(
        f"Merged Employment Legislation data for {len(employment_legislation_data['tender']['documents'])} documents"
    )