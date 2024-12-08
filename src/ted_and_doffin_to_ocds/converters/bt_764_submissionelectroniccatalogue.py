# converters/bt_764_SubmissionElectronicCatalogue.py

import logging

from lxml import etree

logger = logging.getLogger(__name__)


def parse_submission_electronic_catalogue(xml_content: str) -> list[dict] | None:
    """Parse the XML content to extract the Submission Electronic Catalogue policy for each lot.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        Optional[List[Dict]]: A list of dictionaries containing the parsed data if found, None otherwise.

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

    policy_mapping = {
        "required": "required",
        "allowed": "allowed",
        "not-allowed": "notAllowed",
    }

    lots_data = []
    lots = root.xpath(
        "//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']",
        namespaces=namespaces,
    )

    for lot in lots:
        lot_id = lot.xpath("cbc:ID/text()", namespaces=namespaces)[0]
        policy = lot.xpath(
            "cac:TenderingTerms/cac:ContractExecutionRequirement[cbc:ExecutionRequirementCode/@listName='ecatalog-submission']/cbc:ExecutionRequirementCode/text()",
            namespaces=namespaces,
        )

        if policy:
            mapped_policy = policy_mapping.get(policy[0], policy[0])
            lots_data.append(
                {
                    "id": lot_id,
                    "submissionTerms": {"electronicCatalogPolicy": mapped_policy},
                },
            )

    return lots_data if lots_data else None


def merge_submission_electronic_catalogue(
    release_json: dict,
    submission_electronic_catalogue_data: list[dict] | None,
) -> None:
    """Merge the parsed Submission Electronic Catalogue data into the main OCDS release JSON.

    Args:
        release_json (Dict): The main OCDS release JSON to be updated.
        submission_electronic_catalogue_data (Optional[List[Dict]]): The parsed Submission Electronic Catalogue data to be merged.

    Returns:
        None: The function updates the release_json in-place.

    """
    if not submission_electronic_catalogue_data:
        logger.warning("No Submission Electronic Catalogue data to merge")
        return

    tender = release_json.setdefault("tender", {})
    lots = tender.setdefault("lots", [])

    for lot_data in submission_electronic_catalogue_data:
        existing_lot = next(
            (lot for lot in lots if lot.get("id") == lot_data["id"]),
            None,
        )
        if existing_lot:
            existing_lot.setdefault("submissionTerms", {}).update(
                lot_data["submissionTerms"],
            )
        else:
            lots.append(lot_data)

    logger.info(
        "Merged Submission Electronic Catalogue data for %d lots",
        len(submission_electronic_catalogue_data),
    )
