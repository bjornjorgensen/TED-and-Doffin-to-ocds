# converters/opt_301_lot_fiscallegis.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)


def parse_fiscal_legislation_org(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "efext": "http://data.europa.eu/p27/eforms-ubl-extensions/1",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    result = {"parties": [], "tender": {"documents": []}}

    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']", namespaces=namespaces
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        fiscal_docs = lot.xpath(
            "cac:TenderingTerms/cac:FiscalLegislationDocumentReference",
            namespaces=namespaces,
        )

        for doc in fiscal_docs:
            doc_id = doc.xpath("cbc:ID/text()", namespaces=namespaces)
            org_id = doc.xpath(
                "cac:IssuerParty/cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
                namespaces=namespaces,
            )

            if doc_id and org_id:
                result["tender"]["documents"].append(
                    {
                        "id": doc_id[0],
                        "publisher": {"id": org_id[0]},
                        "relatedLots": [lot_id],
                    }
                )

                if not any(party["id"] == org_id[0] for party in result["parties"]):
                    result["parties"].append(
                        {"id": org_id[0], "roles": ["informationService"]}
                    )

    return result if (result["parties"] or result["tender"]["documents"]) else None


def merge_fiscal_legislation_org(release_json, fiscal_legis_data):
    if not fiscal_legis_data:
        logger.info(
            "No Fiscal Legislation Organization Technical Identifier Reference data to merge"
        )
        return

    parties = release_json.setdefault("parties", [])
    tender_docs = release_json.setdefault("tender", {}).setdefault("documents", [])

    for new_party in fiscal_legis_data.get("parties", []):
        existing_party = next(
            (party for party in parties if party["id"] == new_party["id"]), None
        )
        if existing_party:
            existing_roles = set(existing_party.get("roles", []))
            existing_roles.update(new_party["roles"])
            existing_party["roles"] = list(existing_roles)
        else:
            parties.append(new_party)

    for new_doc in fiscal_legis_data.get("tender", {}).get("documents", []):
        existing_doc = next(
            (doc for doc in tender_docs if doc["id"] == new_doc["id"]), None
        )
        if existing_doc:
            existing_doc["publisher"] = new_doc["publisher"]
            existing_doc.setdefault("relatedLots", []).extend(new_doc["relatedLots"])
            existing_doc["relatedLots"] = list(set(existing_doc["relatedLots"]))
        else:
            tender_docs.append(new_doc)

    logger.info(
        "Merged Fiscal Legislation Organization Technical Identifier Reference data for %s parties and %s documents",
        len(fiscal_legis_data.get("parties", [])),
        len(fiscal_legis_data.get("tender", {}).get("documents", [])),
    )
