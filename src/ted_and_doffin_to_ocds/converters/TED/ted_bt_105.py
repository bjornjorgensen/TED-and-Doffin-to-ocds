"""
Module: ted_bt_105.py
Purpose: Convert TED procedure type (BT-105) to OCDS tender procedure fields.

Mapping for TED BT-105 Procedure:
    - Uses TED export XPaths to determine the appropriate
      tender.procurementMethod and tender.procurementMethodDetails.

Mapping rules:
    - "PT_AWARD_CONTRACT_WITHOUT_CALL" or any "DIRECTIVE_" (e.g. DIRECTIVE_2014_24_EU, DIRECTIVE_2014_25_EU, DIRECTIVE_2009_81_EC, DIRECTIVE_2014_23_EU, etc.)
      => limited / Award procedure without prior publication of a call for competition
    - "PT_OPEN"
      => open / Open procedure
    - "PT_COMPETITIVE_NEGOTIATION"
      => selective / Competitive procedure with negotiation
    - "PT_COMPETITIVE_DIALOGUE"
      => selective / Competitive dialogue
    - "PT_INNOVATION_PARTNERSHIP"
      => selective / Innovation partnership
    - "PT_NEGOTIATED_WITH_PRIOR_CALL" or "PT_NEGOTIATED_CHOICE"
      => selective / Negotiated procedure with prior call for competition
    - "PT_INVOLVING_NEGOTIATION"
      => selective / Procedure involving negotiations
    - "PT_RESTRICTED"
      => selective / Restricted procedure
"""


def map_ted_procedure(ted_xpath):
    """
    Map a TED export XPath to the corresponding OCDS procurement method and details.

    Parameters:
        ted_xpath (str): TED export XPath string.

    Returns:
        tuple: (procurementMethod, procurementMethodDetails) if matched, otherwise (None, None).
    """
    result = (None, None)
    if "PT_AWARD_CONTRACT_WITHOUT_CALL" in ted_xpath or "DIRECTIVE_" in ted_xpath:
        result = (
            "limited",
            "Award procedure without prior publication of a call for competition",
        )
    elif "PT_OPEN" in ted_xpath:
        result = ("open", "Open procedure")
    elif "PT_COMPETITIVE_NEGOTIATION" in ted_xpath:
        result = ("selective", "Competitive procedure with negotiation")
    elif "PT_COMPETITIVE_DIALOGUE" in ted_xpath:
        result = ("selective", "Competitive dialogue")
    elif "PT_INNOVATION_PARTNERSHIP" in ted_xpath:
        result = ("selective", "Innovation partnership")
    elif (
        "PT_NEGOTIATED_WITH_PRIOR_CALL" in ted_xpath
        or "PT_NEGOTIATED_CHOICE" in ted_xpath
    ):
        result = ("selective", "Negotiated procedure with prior call for competition")
    elif "PT_INVOLVING_NEGOTIATION" in ted_xpath:
        result = ("selective", "Procedure involving negotiations")
    elif "PT_RESTRICTED" in ted_xpath:
        result = ("selective", "Restricted procedure")
    return result


def convert_bt105_ted(ted_xpath):
    """
    Convert a TED procedure type to the OCDS tender procedure representation.

    Parameters:
        ted_xpath (str): The TED XPath indicator from the export.

    Returns:
        dict: Dictionary with keys 'tender.procurementMethod' and 'tender.procurementMethodDetails' if mapping is found,
              otherwise returns an empty dictionary.
    """
    method, details = map_ted_procedure(ted_xpath)
    if method is None:
        return {}
    return {
        "tender": {"procurementMethod": method, "procurementMethodDetails": details}
    }
