import logging
from collections.abc import Callable, Sequence
from typing import Any

from ted_and_doffin_to_ocds.converters.TED.ted_bt_05 import (
    merge_notice_dispatch_date,
    parse_notice_dispatch_date,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_09 import (
    merge_cross_border_law,
    parse_cross_border_law,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_10 import (
    merge_authority_activity,
    parse_authority_activity,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_11 import (
    parse_ted_buyer_legal_type,
    # merge is missing
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_13_lot import (
    merge_additional_info_deadline,
    parse_additional_info_deadline,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_14_lot import (
    merge_lot_documents_restricted,
    parse_lot_documents_restricted,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_21_lot import (
    merge_lot_title,
    parse_lot_title,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_105 import (
    convert_bt105_ted,
    map_ted_procedure,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_106 import (
    merge_procedure_accelerated,
    parse_procedure_accelerated,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_109 import (
    merge_framework_duration_justification,
    parse_framework_duration_justification,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_113_lot import (
    merge_framework_max_participants,
    parse_framework_max_participants,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_115_lot import (
    merge_gpa_coverage,
    parse_gpa_coverage,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_115_part import (
    merge_gpa_coverage_part,
    parse_gpa_coverage_part,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_119 import (
    merge_dps_termination,
    parse_dps_termination,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_120 import (
    merge_no_negotiation_necessary,
    parse_no_negotiation_necessary,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_122 import (
    merge_electronic_auction_description,
    parse_electronic_auction_description,
)
from ted_and_doffin_to_ocds.converters.TED.ted_bt_124_lot import (
    merge_tool_atypical_url,
    parse_tool_atypical_url,
)


def process_bt_section(
    release_json: dict[str, Any],
    xml_content: bytes,
    parse_funcs: Sequence[Callable],
    merge_func: Callable,
    section_name: str,
) -> None:
    """Process a single business term section."""
    logger = logging.getLogger(__name__)

    try:
        logger.info("Starting %s processing", section_name)
        for parse_function in parse_funcs:
            parsed_data = parse_function(xml_content)
            if parsed_data:
                merge_func(release_json, parsed_data)
                logger.info("Successfully merged data for %s", section_name)
                return
        logger.warning("No data found for %s", section_name)
    except Exception:
        logger.exception("Error processing %s data", section_name)


def process_bt_sections(release_json: dict[str, Any], xml_content: bytes) -> None:
    """Process all business term sections."""
    bt_sections = [
        (
            parse_notice_dispatch_date,
            merge_notice_dispatch_date,
            "BT-05 Notice Dispatch Date",
        ),
        (
            parse_cross_border_law,
            merge_cross_border_law,
            "BT-09 Cross Border Law",
        ),
        (
            parse_authority_activity,
            merge_authority_activity,
            "BT-10 Authority Activity",
        ),
        (
            parse_ted_buyer_legal_type,
            "BT-11 ",
        ),
        (
            parse_additional_info_deadline,
            merge_additional_info_deadline,
            "BT-13 Lot Additional Information Deadline",
        ),
        (
            parse_lot_documents_restricted,
            merge_lot_documents_restricted,
            "BT-14 Lot Documents Restricted",
        ),
        (
            parse_lot_title,
            merge_lot_title,
            "BT-21 Lot Title",
        ),
        (
            map_ted_procedure,
            convert_bt105_ted,
            "BT-105 Procedure Type",
        ),
        (
            parse_procedure_accelerated,
            merge_procedure_accelerated,
            "BT-106 procedure_accelerated",
        ),
        (
            parse_framework_duration_justification,
            merge_framework_duration_justification,
            "BT-109 framework_duration_justification",
        ),
        (
            parse_framework_max_participants,
            merge_framework_max_participants,
            "BT-113 Lot Maximum Participants",
        ),
        (
            parse_gpa_coverage,
            merge_gpa_coverage,
            "BT-115 Lot GPA Coverage",
        ),
        (
            parse_gpa_coverage_part,
            merge_gpa_coverage_part,
            "BT-115 part GPA Coverage",
        ),
        (
            parse_dps_termination,
            merge_dps_termination,
            "BT-119 Dynamic Purchasing System Termination",
        ),
        (
            parse_no_negotiation_necessary,
            merge_no_negotiation_necessary,
            "BT-120 No Negotiation Necessary",
        ),
        (
            parse_electronic_auction_description,
            merge_electronic_auction_description,
            "BT-122 Electronic Auction Description",
        ),
        (
            parse_tool_atypical_url,
            merge_tool_atypical_url,
            "BT-124 Lot Atypical Tool URL",
        ),
    ]

    for parse_func, merge_func, section_name in bt_sections:
        process_bt_section(
            release_json, xml_content, [parse_func], merge_func, section_name
        )
