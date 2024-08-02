# converters/BT_636_LotResult.py

import logging
from lxml import etree

logger = logging.getLogger(__name__)

IRREGULARITY_TYPE_MAPPING = {
    "ab-low": "Unjustified rejection of abnormally low tenders",
    "ar-split": "Artificial splitting of contracts",
    "bid-rigging": "Bid-rigging (established by a competition / anti-cartel office, a court or other competent body)",
    "change-eval": "Negotiation during the award procedure, including modification of the winning tender during evaluation",
    "conf-int": "Conflict of interest with impact on the outcome of the procurement procedure",
    "cp-mod-cond": "Competitive procedure with negotiation, with substantial modification of the conditions set out in the contract notice or tender specifications",
    "elem-mod": "Modifications of the contract elements set out in the contract notice or tender specifications, not in compliance with the relevant rules",
    "eva-add-crit": "Evaluation using additional award criteria that were not published",
    "eva-diff-crit": "Evaluation of tenders using award criteria that are different from the ones stated in the contract notice or tender specifications",
    "formal": "Formal",
    "ins-audit": "Insufficient audit trail for the award of the contract",
    "insuf-timl": "Insufficient time for potential tenderers/candidates to obtain the procurement documents",
    "irr-involv": "Irregular prior involvement of candidates or tenderers with the buyer",
    "mod-inco": "Selection criteria or technical specifications were modified after opening of tenders or were incorrectly applied",
    "nc-proc-eap": "Non-compliance with the procedure for electronic and aggregated procurement",
    "nc-timl": "Non-compliance with time limits for receipt of tenders or time limits for receipt of requests to participate",
    "ncompl-awcrit": "Failure to describe in sufficient detail the award criteria and their weighting",
    "ncompl-cn": "Failure to publish in the contract notice the technical specifications, selection criteria, award criteria (and their weighing), or contract performance conditions",
    "ncompl-com": "Failure to communicate and/or publish clarifications and/or additional information",
    "ncompl-sub": "Insufficient or imprecise definition of the subject matter of the contract",
    "no-notice": "Lack of publication of contract notice or unjustified direct award",
    "noex-addinfo": "Failure to extend time limits for receipt of tenders or requests to participate where additional information, although requested by the economic operator in good time, is not supplied at the latest six days before the time limit",
    "noex-timl": "Failure to extend time limits for receipt of tenders or requests to participate where significant changes are made to the procurement documents",
    "nojust-nolots": "Lack of justification for not subdividing contract into lots",
    "npub-limit": "Lack of publication of extended time limits for receipt of tenders or requests to participate",
    "other": "Other",
    "restr-not-tlim": "Restrictions to obtaining the procurement documents, other than insufficient time",
    "unj-comp-pro": "Unjustified use of competitive procedure with negotiation, competitive dialogue or innovative partnership",
    "unj-excl": "Unjustified exclusion of tenderers or candidates",
    "unj-lim-subc": "Unjustified limitation of subcontracting",
    "unj-na-ppr": "Unjustified non-application of public procurement rules",
    "unj-nrl": "Use of technical specification, selection criterion, award criterion, exclusion criterion, or contract performance condition that are discriminatory because of unjustified national, regional or local preferences",
    "unj-nrl-other": "Use of technical specifications, selection criteria, award criteria, exclusion criteria, or contract performance conditions that are discriminatory (i.e. restrict access for economic operators) for other reasons than unjustified national, regional or local preferences"
}

def parse_irregularity_type(xml_content):
    """
    Parse the XML content to extract the irregularity type information for each lot result.

    Args:
        xml_content (str): The XML content to parse.

    Returns:
        dict: A dictionary containing the parsed irregularity type data in the format:
              {
                  "statistics": [
                      {
                          "id": "unique_id",
                          "measure": "irregularity_code",
                          "scope": "complaints",
                          "notes": "irregularity_description",
                          "relatedLot": "lot_id"
                      }
                  ]
              }
        None: If no relevant data is found.

    Raises:
        etree.XMLSyntaxError: If the input is not valid XML.
    """
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
        'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
        'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1',
        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
    }

    result = {"statistics": []}
    statistic_id = 1

    lot_results = root.xpath("//efac:NoticeResult/efac:LotResult", namespaces=namespaces)
    
    for lot_result in lot_results:
        lot_id = lot_result.xpath("efac:TenderLot/cbc:ID[@schemeName='Lot']/text()", namespaces=namespaces)
        irregularity_types = lot_result.xpath("efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efbc:StatisticsCode/text()", namespaces=namespaces)
        
        if lot_id and irregularity_types:
            for irregularity_type in irregularity_types:
                statistic = {
                    "id": str(statistic_id),
                    "measure": irregularity_type,
                    "scope": "complaints",
                    "notes": IRREGULARITY_TYPE_MAPPING.get(irregularity_type, "Unknown irregularity type"),
                    "relatedLot": lot_id[0]
                }
                result["statistics"].append(statistic)
                statistic_id += 1

    return result if result["statistics"] else None

def merge_irregularity_type(release_json, irregularity_type_data):
    """
    Merge the parsed irregularity type data into the main OCDS release JSON.

    Args:
        release_json (dict): The main OCDS release JSON to be updated.
        irregularity_type_data (dict): The parsed irregularity type data to be merged.

    Returns:
        None: The function updates the release_json in-place.
    """
    if not irregularity_type_data:
        logger.warning("No irregularity type data to merge")
        return

    existing_statistics = release_json.setdefault("statistics", [])
    
    for new_statistic in irregularity_type_data["statistics"]:
        existing_statistic = next((stat for stat in existing_statistics if stat["id"] == new_statistic["id"]), None)
        if existing_statistic:
            existing_statistic.update(new_statistic)
        else:
            existing_statistics.append(new_statistic)

    logger.info(f"Merged irregularity type data for {len(irregularity_type_data['statistics'])} statistics")