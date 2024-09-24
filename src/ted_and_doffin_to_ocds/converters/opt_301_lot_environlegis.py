# converters/OPT_301_Lot_EnvironLegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_environmental_legislation_document_reference(xml_content):
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

    result = {"parties": [], "tender": {"documents": [], "lots": []}}

    lots = root.xpath("//cac:ProcurementProjectLot", namespaces=namespaces)

    for lot in lots:
        lot_ids = lot.xpath("cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        if not lot_ids:
            logger.warning("No Lot ID found with schemeName='Lot'")
            continue
        lot_id = lot_ids[0]

        document_reference_ids = lot.xpath(
            "cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference/cbc:ID/text()",
            namespaces=namespaces,
        )
        if not document_reference_ids:
            logger.warning("No Environmental Legislation Document Reference ID found")
            continue
        document_reference_id = document_reference_ids[0]

        organization_ids = lot.xpath(
            "cac:TenderingTerms/cac:EnvironmentalLegislationDocumentReference/cac:Issuerparty/cac:partyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        if not organization_ids:
            logger.warning("No organization ID found with schemeName='organization'")
            continue
        org_id = organization_ids[0]

        # Add the organization to the result
        party = {"id": org_id, "roles": ["informationService"]}
        result["parties"].append(party)

        # Add the document to the result
        document = {
            "id": document_reference_id,
            "publisher": {"id": org_id},
            "relatedLots": [lot_id],
        }
        result["tender"]["documents"].append(document)

        # Add the lot to the result
        lot_obj = {"id": lot_id}
        result["tender"]["lots"].append(lot_obj)

    # Clean up empty fields
    if not result["tender"]["documents"]:
        result.pop("tender")
    else:
        if not result["tender"]["lots"]:
            result["tender"].pop("lots")

    if not result["parties"]:
        result.pop("parties")

    return result if result else None


def merge_environmental_legislation_document_reference(
    release_json,
    environmental_legislation_data,
):
    if not environmental_legislation_data:
        logger.warning("No Environmental Legislation Document Reference data to merge")
        return

    # Merge parties
    existing_parties = release_json.setdefault("parties", [])

    for new_party in environmental_legislation_data.get("parties", []):
        existing_party = next(
            (party for party in existing_parties if party["id"] == new_party["id"]),
            None,
        )
        if existing_party:
            if "informationService" not in existing_party.get("roles", []):
                existing_party.setdefault("roles", []).append("informationService")
        else:
            existing_parties.append(new_party)

    # Merge documents
    existing_documents = release_json.setdefault("tender", {}).setdefault(
        "documents",
        [],
    )

    for new_document in environmental_legislation_data["tender"].get("documents", []):
        existing_document = next(
            (doc for doc in existing_documents if doc["id"] == new_document["id"]),
            None,
        )
        if existing_document:
            existing_document["publisher"] = new_document["publisher"]
            existing_document.setdefault("relatedLots", []).extend(
                lot
                for lot in new_document["relatedLots"]
                if lot not in existing_document.get("relatedLots", [])
            )
        else:
            existing_documents.append(new_document)

    # Merge lots
    existing_lots = release_json.setdefault("tender", {}).setdefault("lots", [])

    for new_lot in environmental_legislation_data["tender"].get("lots", []):
        if not any(lot["id"] == new_lot["id"] for lot in existing_lots):
            existing_lots.append(new_lot)

    logger.info(
        "Merged Environmental Legislation Document Reference for %d parties",
        len(environmental_legislation_data.get("parties", [])),
    )
