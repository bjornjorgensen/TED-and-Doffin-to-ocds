# converters/BT_105_Procedure.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)


def parse_procedure_type(xml_content):
    """
    Parse the XML content to extract the procedure type.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed procedure type data.
        None: If no relevant data is found.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode("utf-8")
    root = etree.fromstring(xml_content)
    namespaces = {
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
    }

    procedure_code = root.xpath(
        "//cac:TenderingProcess/cbc:ProcedureCode[@listName='procurement-procedure-type']/text()",
        namespaces=namespaces,
    )

    if procedure_code:
        procedure_code = procedure_code[0]
        procedure_code_mapping = {
            "open": "open",
            "restricted": "selective",
            "comp-dial": "selective",
            "comp-tend": "selective",
            "innovation": "selective",
            "neg-w-call": "selective",
            "neg-wo-call": "limited",
            "exp-int-rail": "selective",
            "oth-mult": None,
            "oth-single": None,
        }
        procedure_details_mapping = {
            "open": "Open procedure",
            "restricted": "Restricted procedure",
            "comp-dial": "Competitive dialogue",
            "comp-tend": "Competitive tendering (article 5(3) of Regulation 1370/2007)",
            "innovation": "Innovation partnership",
            "neg-w-call": "Negotiated with prior publication of a call for competition / competitive with negotiation",
            "neg-wo-call": "Negotiated without prior call for competition",
            "exp-int-rail": "Request for expression of interest – only for rail (article 5(3b) of Regulation 1370/2007)",
            "oth-mult": "Other multiple stage procedure",
            "oth-single": "Other single stage procedure",
        }

        result = {
            "tender": {
                "procurementMethodDetails": procedure_details_mapping.get(
                    procedure_code
                )
            }
        }

        procurement_method = procedure_code_mapping.get(procedure_code)
        if procurement_method:
            result["tender"]["procurementMethod"] = procurement_method

        return result

    return None


def merge_procedure_type(release_json, procedure_type_data):
    """
    Merge the parsed procedure type data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        procedure_type_data (dict): The parsed procedure type data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not procedure_type_data:
        logger.warning("No procedure type data to merge")
        return

    tender = release_json.setdefault("tender", {})
    tender.update(procedure_type_data["tender"])

    logger.info("Merged procedure type data")
