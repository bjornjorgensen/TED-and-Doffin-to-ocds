# converters/bt_136_procedure.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)

# Direct Award Justification Code lookup table
JUSTIFICATION_CODES = {
    "additional": "Need for additional works or services by the original contractor",
    "artistic": "The contract can be provided only by a particular economic operator because of creation or acquisition of a unique work of art or artistic performance",
    "bargain": "Bargain purchase taking advantage of a particularly advantageous opportunity available for a very short time at a price considerably lower than market prices",
    "below-thres": "Contracts with estimated value below the procurement thresholds",
    "below-thres-sme": "Small contract with a small or medium-sized enterprise (article 5(4) 2nd paragraph of Regulation 1370/2007)",
    "char-imp": "Structural and geographical characteristics of market/network or improvement of quality of services or cost-efficiency – only for rail (article 5(4a) of Regulation 1370/2007)",
    "closure": "Purchase on particularly advantageous terms from an economic operator which is definitely winding up its business activities",
    "commodity": "Procurement of supplies quoted and purchased on a commodity market",
    "contest": "Service contract to be awarded to the winner or one of winners under the rules of a design contest",
    "crisis": "The periods for the restricted procedure and the negotiated procedure with prior publication of a contract notice are incompatible with the urgency resulting from a crisis",
    "defse-excl": "Defence-specific and security-specific exclusions",
    "dir24-list": "Contracts listed in Directive 2014/24/EU Art. 7, but not falling within the scope of Directive 2014/25/EU",
    "dir81-annexii": "The contract falls within the services listed in Annex II of the Directive 2009/81/EC",
    "dir81-transport": "Contract related to the provision of air and maritime transport services for the armed forces of a Member State deployed or to be deployed abroad, under the strict conditions stated in the Directive",
    "ecom-excl": "Specific exclusion in the field of electronic communications",
    "energy-supply": "Contracts awarded for the supply of energy or of fuels for the production of energy",
    "exc-circ-rail": "Exceptional circumstances – only for rail (article 5(3a) of Regulation 1370/2007)",
    "exclusive": "The contract can be provided only by a particular economic operator because of exclusive rights, including intellectual property rights",
    "existing": "partial replacement or extension of existing supplies or installations by the original supplier ordered under the strict conditions stated in the Directive",
    "in-house": "Public contract between organisations within the public sector ('in-house'), contracts awarded to affiliated undertakings, or contracts awarded to a joint venture or within a joint venture",
    "int-oper": "Internal operator (article 5(2) of Regulation 1370/2007)",
    "int-rules": "procedure according to international rules",
    "irregular": "Only irregular or unacceptable tenders were received in response to a previous notice. All and only those tenderers of the previous procedure which have satisfied the selection criteria, have not fulfilled the exclusion grounds and have satisfied formal requirements, were included in the negotiations",
    "liquidator": "Purchase on particularly advantageous terms from the liquidator in an insolvency procedure, an arrangement with creditors or a similar procedure under national laws and regulations",
    "non-buyer-aw": "Contract awarded by parties that are not buyers",
    "non-contr": "Certain cases of non-contractual nature",
    "non-p-int": "Contracts for non-pecuniary interest",
    "not-wss": "Contracts whose purpose is not the execution of works, the supply of products and the provision of services",
    "other-activity": "Contracts awarded for purposes other than the pursuit of a covered activity or for the pursuit of such an activity in a third country",
    "other-exclusive": "The contract can be provided only by a particular economic operator because of protection of other exclusive rights, including intellectual property rights, other than those defined in Directive 2014/23/EU Art. 5(10)",
    "other-legal": "The procurement falls outside the scope of application of the directive",
    "rail": "Railway transport",
    "rd": "The contract concerns research and development services other than those referred to in Directive 2009/81/EC Art. 13",
    "repetition": "New works or services, constituting a repetition of existing works or services and ordered in accordance with the strict conditions stated in the Directive",
    "resd": "Purpose of the contract is purely research, experiment, study or development under the conditions stated in the Directive",
    "rl-third": "Contracts awarded for purposes of resale or lease to third parties",
    "sc-right": "Service contract awarded on the basis of an exclusive right",
    "serv-excl": "Specific exclusions for service contracts",
    "sim-infra": "Simultaneous management of the entire or major part of the infrastructure – only for rail (article 5(4b) of Regulation 1370/2007)",
    "spe-arrang": "Activities directly exposed to competition and contracts subject to special arrangements",
    "technical": "The contract can be provided only by a particular economic operator because of an absence of competition for technical reasons",
    "tra-ser": "Concessions for air transport services based on the granting of an operating licence within the meaning of Regulation (EC) No 1008/2008",
    "unsuitable": "No suitable tenders, requests to participate, or applications were received in response to a previous notice",
    "urgency": "Extreme urgency brought about by events unforeseeable for the buyer",
    "water-purch": "Contracts awarded for the purchase of water",
}


def parse_direct_award_justification_code(
    xml_content: str | bytes,
) -> dict | None:
    """
    Parse the direct award justification code from XML data.

    Args:
        xml_content (Union[str, bytes]): The XML content containing justification information

    Returns:
        Optional[Dict]: Dictionary containing tender information, or None if no data found
        The structure follows the format:
        {
            "tender": {
                "procurementMethodRationaleClassifications": [
                    {
                        "scheme": "eu-direct-award-justification",
                        "id": str,
                        "description": str
                    }
                ]
            }
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

    codes = root.xpath(
        "/*/cac:TenderingProcess/cac:ProcessJustification"
        "[cbc:ProcessReasonCode/@listName='direct-award-justification']"
        "/cbc:ProcessReasonCode/text()",
        namespaces=namespaces,
    )

    if codes:
        classifications = [
            {
                "scheme": "eu-direct-award-justification",
                "id": code,
                "description": JUSTIFICATION_CODES.get(code, "Unknown"),
            }
            for code in codes
        ]

        return {
            "tender": {"procurementMethodRationaleClassifications": classifications}
        }

    return None


def merge_direct_award_justification_code(
    release_json: dict, justification_data: dict | None
) -> None:
    """
    Merge direct award justification code data into the release JSON.

    Args:
        release_json (Dict): The target release JSON to merge data into
        justification_data (Optional[Dict]): The source data containing justification codes
            to be merged. If None, function returns without making changes.

    Note:
        The function modifies release_json in-place by adding or updating the
        tender.procurementMethodRationaleClassifications field.
    """
    if not justification_data:
        return

    tender = release_json.setdefault("tender", {})
    tender["procurementMethodRationaleClassifications"] = justification_data["tender"][
        "procurementMethodRationaleClassifications"
    ]
    logger.info("Merged direct award justification code")
