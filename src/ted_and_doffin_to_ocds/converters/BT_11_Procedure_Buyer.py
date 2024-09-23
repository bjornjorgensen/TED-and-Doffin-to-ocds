# converters/BT_11_Procedure_Buyer.py

from lxml import etree
import logging

logger = logging.getLogger(__name__)

BUYER_LEGAL_TYPE_CODES = {
    "body-pl": "Body governed by public law",
    "body-pl-cga": "Body governed by public law, controlled by a central government authority",
    "body-pl-la": "Body governed by public law, controlled by a local authority",
    "body-pl-ra": "Body governed by public law, controlled by a regional authority",
    "cga": "Central government authority",
    "def-cont": "Defence contractor",
    "eu-ins-bod-ag": "EU institution, body or agency",
    "eu-int-org": "European Institution/Agency or International Organisation",
    "grp-p-aut": "Group of public authorities",
    "int-org": "International organisation",
    "la": "Local authority",
    "org-sub": "Organisation awarding a contract subsidised by a contracting authority",
    "org-sub-cga": "Organisation awarding a contract subsidised by a central government authority",
    "org-sub-la": "Organisation awarding a contract subsidised by a local authority",
    "org-sub-ra": "Organisation awarding a contract subsidised by a regional authority",
    "pub-undert": "Public undertaking",
    "pub-undert-cga": "Public undertaking, controlled by a central government authority",
    "pub-undert-la": "Public undertaking, controlled by a local authority",
    "pub-undert-ra": "Public undertaking, controlled by a regional authority",
    "ra": "Regional authority",
    "rl-aut": "Regional or local authority",
    "spec-rights-entity": "Entity with special or exclusive rights",
}


def parse_buyer_legal_type(xml_content):
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

    result = {"parties": []}
    contracting_parties = root.xpath("//cac:ContractingParty", namespaces=namespaces)

    for party in contracting_parties:
        org_id = party.xpath(
            ".//cac:PartyIdentification/cbc:ID[@schemeName='organization']/text()",
            namespaces=namespaces,
        )
        legal_type = party.xpath(
            ".//cac:ContractingPartyType/cbc:PartyTypeCode[@listName='buyer-legal-type']/text()",
            namespaces=namespaces,
        )

        if org_id and legal_type:
            org_id = org_id[0]
            legal_type = legal_type[0]
            description = BUYER_LEGAL_TYPE_CODES.get(
                legal_type, "Unknown buyer legal type",
            )

            party_data = {
                "id": org_id,
                "details": {
                    "classifications": [
                        {
                            "scheme": "TED_CA_TYPE",
                            "id": legal_type,
                            "description": description,
                        },
                    ],
                },
            }
            result["parties"].append(party_data)

    return result if result["parties"] else None


def merge_buyer_legal_type(release_json, buyer_legal_type_data):
    if not buyer_legal_type_data:
        logger.warning("No Buyer Legal Type data to merge")
        return

    if "parties" not in release_json:
        release_json["parties"] = []

    for new_party in buyer_legal_type_data["parties"]:
        existing_party = next(
            (
                party
                for party in release_json["parties"]
                if party["id"] == new_party["id"]
            ),
            None,
        )
        if existing_party:
            if "details" not in existing_party:
                existing_party["details"] = {}
            if "classifications" not in existing_party["details"]:
                existing_party["details"]["classifications"] = []
            existing_party["details"]["classifications"].append(
                new_party["details"]["classifications"][0],
            )
        else:
            release_json["parties"].append(new_party)

    logger.info(
        f"Merged Buyer Legal Type data for {len(buyer_legal_type_data['parties'])} parties",
    )
