# main.py
import json
import logging
from pathlib import Path
from ted_and_doffin_to_ocds.converters.common_operations import NoticeProcessor
from ted_and_doffin_to_ocds.converters.bt_01_procedure import (
    parse_procedure_legal_basis,
    merge_procedure_legal_basis,
)
from ted_and_doffin_to_ocds.converters.bt_03 import parse_form_type, merge_form_type
from ted_and_doffin_to_ocds.converters.bt_04_procedure import (
    parse_procedure_identifier,
    merge_procedure_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_05_notice import (
    parse_notice_dispatch_date_time,
    merge_notice_dispatch_date_time,
)
from ted_and_doffin_to_ocds.converters.bt_06_lot import (
    parse_strategic_procurement,
    merge_strategic_procurement,
)
from ted_and_doffin_to_ocds.converters.bt_09_procedure import (
    parse_cross_border_law,
    merge_cross_border_law,
)
from ted_and_doffin_to_ocds.converters.bt_10 import (
    parse_contract_xml,
    merge_contract_info,
)
from ted_and_doffin_to_ocds.converters.bt_11_procedure_buyer import (
    parse_buyer_legal_type,
    merge_buyer_legal_type,
)
from ted_and_doffin_to_ocds.converters.bt_88_procedure import (
    parse_procedure_features,
    merge_procedure_features,
)
from ted_and_doffin_to_ocds.converters.bt_105_procedure import (
    parse_procedure_type,
    merge_procedure_type,
)
from ted_and_doffin_to_ocds.converters.bt_106_procedure import (
    parse_procedure_accelerated,
    merge_procedure_accelerated,
)
from ted_and_doffin_to_ocds.converters.bt_109_lot import (
    parse_framework_duration_justification,
    merge_framework_duration_justification,
)
from ted_and_doffin_to_ocds.converters.bt_111_lot import (
    parse_framework_buyer_categories,
    merge_framework_buyer_categories,
)
from ted_and_doffin_to_ocds.converters.bt_113_lot import (
    parse_framework_max_participants,
    merge_framework_max_participants,
)
from ted_and_doffin_to_ocds.converters.bt_115_gpa_coverage import (
    parse_gpa_coverage,
    merge_gpa_coverage,
)
from ted_and_doffin_to_ocds.converters.bt_13713_lotresult import (
    parse_lot_result_identifier,
    merge_lot_result_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_13714_tender import (
    parse_tender_lot_identifier,
    merge_tender_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_1375_procedure import (
    parse_group_lot_identifier,
    merge_group_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_119_lotresult import (
    parse_dps_termination,
    merge_dps_termination,
)
from ted_and_doffin_to_ocds.converters.bt_120_lot import (
    parse_no_negotiation_necessary,
    merge_no_negotiation_necessary,
)
from ted_and_doffin_to_ocds.converters.bt_122_lot import (
    parse_electronic_auction_description,
    merge_electronic_auction_description,
)
from ted_and_doffin_to_ocds.converters.bt_123_lot import (
    parse_electronic_auction_url,
    merge_electronic_auction_url,
)
from ted_and_doffin_to_ocds.converters.bt_124_tool_atypical_url import (
    parse_tool_atypical_url,
    merge_tool_atypical_url,
)
from ted_and_doffin_to_ocds.converters.bt_125_lot import (
    parse_previous_planning_identifier_lot,
    merge_previous_planning_identifier_lot,
)
from ted_and_doffin_to_ocds.converters.bt_125_part import (
    parse_previous_planning_identifier_part,
    merge_previous_planning_identifier_part,
)
from ted_and_doffin_to_ocds.converters.bt_1252_procedure import (
    parse_direct_award_justification,
    merge_direct_award_justification,
)
from ted_and_doffin_to_ocds.converters.bt_127_notice import (
    parse_future_notice_date,
    merge_future_notice_date,
)
from ted_and_doffin_to_ocds.converters.bt_13_lot import (
    parse_additional_info_deadline,
    merge_additional_info_deadline,
)
from ted_and_doffin_to_ocds.converters.bt_13_part import (
    parse_additional_info_deadline_part,
    merge_additional_info_deadline_part,
)
from ted_and_doffin_to_ocds.converters.bt_130_lot import (
    parse_dispatch_invitation_tender,
    merge_dispatch_invitation_tender,
)
from ted_and_doffin_to_ocds.converters.bt_131_lot import (
    parse_deadline_receipt_tenders,
    merge_deadline_receipt_tenders,
)
from ted_and_doffin_to_ocds.converters.bt_1311_lot import (
    parse_deadline_receipt_requests,
    merge_deadline_receipt_requests,
)
from ted_and_doffin_to_ocds.converters.bt_132_lot import (
    parse_lot_public_opening_date,
    merge_lot_public_opening_date,
)
from ted_and_doffin_to_ocds.converters.bt_133_lot import (
    parse_lot_bid_opening_location,
    merge_lot_bid_opening_location,
)
from ted_and_doffin_to_ocds.converters.bt_134_lot import (
    parse_lot_public_opening_description,
    merge_lot_public_opening_description,
)
from ted_and_doffin_to_ocds.converters.bt_135_procedure import (
    parse_direct_award_justification_rationale,
    merge_direct_award_justification_rationale,
)
from ted_and_doffin_to_ocds.converters.bt_1351_procedure import (
    parse_accelerated_procedure_justification,
    merge_accelerated_procedure_justification,
)
from ted_and_doffin_to_ocds.converters.bt_136_procedure import (
    parse_direct_award_justification_code,
    merge_direct_award_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_137_lot import (
    parse_purpose_lot_identifier,
    merge_purpose_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_137_lotsgroup import (
    parse_lots_group_identifier,
    merge_lots_group_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_137_part import (
    parse_part_identifier,
    merge_part_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_14_lot import (
    parse_lot_documents_restricted,
    merge_lot_documents_restricted,
)
from ted_and_doffin_to_ocds.converters.bt_14_part import (
    parse_part_documents_restricted,
    merge_part_documents_restricted,
)
from ted_and_doffin_to_ocds.converters.bt_140_notice import (
    parse_change_reason_code,
    merge_change_reason_code,
)
from ted_and_doffin_to_ocds.converters.bt_142_lotresult import (
    parse_winner_chosen,
    merge_winner_chosen,
)
from ted_and_doffin_to_ocds.converters.bt_144_lotresult import (
    parse_not_awarded_reason,
    merge_not_awarded_reason,
)
from ted_and_doffin_to_ocds.converters.bt_145_contract import (
    parse_contract_conclusion_date,
    merge_contract_conclusion_date,
)
from ted_and_doffin_to_ocds.converters.bt_1451_contract import (
    parse_winner_decision_date,
    merge_winner_decision_date,
)
from ted_and_doffin_to_ocds.converters.bt_15_lot_part import (
    parse_documents_url,
    merge_documents_url,
)
from ted_and_doffin_to_ocds.converters.bt_150_contract import (
    parse_contract_identifier,
    merge_contract_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_151_contract import (
    parse_contract_url,
    merge_contract_url,
)
from ted_and_doffin_to_ocds.converters.bt_16_organization_company import (
    parse_organization_part_name,
    merge_organization_part_name,
)
from ted_and_doffin_to_ocds.converters.bt_16_organization_touchpoint import (
    parse_organization_touchpoint_part_name,
    merge_organization_touchpoint_part_name,
)
from ted_and_doffin_to_ocds.converters.bt_160_tender import (
    parse_concession_revenue_buyer,
    merge_concession_revenue_buyer,
)
from ted_and_doffin_to_ocds.converters.bt_162_tender import (
    parse_concession_revenue_user,
    merge_concession_revenue_user,
)
from ted_and_doffin_to_ocds.converters.bt_163_tender import (
    parse_concession_value_description,
    merge_concession_value_description,
)
from ted_and_doffin_to_ocds.converters.bt_165_organization_company import (
    parse_winner_size,
    merge_winner_size,
)
from ted_and_doffin_to_ocds.converters.bt_17_lot import (
    parse_submission_electronic,
    merge_submission_electronic,
)
from ted_and_doffin_to_ocds.converters.bt_171_tender import (
    parse_tender_rank,
    merge_tender_rank,
)
from ted_and_doffin_to_ocds.converters.bt_1711_tender import (
    parse_tender_ranked,
    merge_tender_ranked,
)
from ted_and_doffin_to_ocds.converters.bt_18_lot import (
    parse_submission_url,
    merge_submission_url,
)
from ted_and_doffin_to_ocds.converters.bt_19_lot import (
    parse_submission_nonelectronic_justification,
    merge_submission_nonelectronic_justification,
)
from ted_and_doffin_to_ocds.converters.bt_191_tender import (
    parse_country_origin,
    merge_country_origin,
)
from ted_and_doffin_to_ocds.converters.bt_193_tender import (
    parse_tender_variant,
    merge_tender_variant,
)
from ted_and_doffin_to_ocds.converters.bt_539_lotsgroup import (
    parse_award_criterion_type_lots_group,
    merge_award_criterion_type_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_5421_lot import (
    parse_award_criterion_number_weight_lot,
    merge_award_criterion_number_weight_lot,
)
from ted_and_doffin_to_ocds.converters.bt_5421_lotsgroup import (
    parse_award_criterion_number_weight_lots_group,
    merge_award_criterion_number_weight_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_5422_lot import (
    parse_award_criterion_number_fixed,
    merge_award_criterion_number_fixed,
)
from ted_and_doffin_to_ocds.converters.bt_5422_lotsgroup import (
    parse_award_criterion_number_fixed_lotsgroup,
    merge_award_criterion_number_fixed_lotsgroup,
)


# BT_195
from ted_and_doffin_to_ocds.converters.bt_195_bt_09_procedure import (
    bt_195_parse_unpublished_identifier_bt_09_procedure,
    bt_195_merge_unpublished_identifier_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_105_procedure import (
    parse_bt195_bt105_unpublished_identifier,
    merge_bt195_bt105_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_106_procedure import (
    parse_bt195_bt106_unpublished_identifier,
    merge_bt195_bt106_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_1252_procedure import (
    parse_bt195_bt1252_unpublished_identifier,
    merge_bt195_bt1252_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_135_procedure import (
    parse_bt195_bt135_unpublished_identifier,
    merge_bt195_bt135_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_1351_procedure import (
    parse_bt195_bt1351_unpublished_identifier,
    merge_bt195_bt1351_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_136_procedure import (
    parse_bt195_bt136_unpublished_identifier,
    merge_bt195_bt136_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_142_lotresult import (
    parse_bt195_bt142_unpublished_identifier,
    merge_bt195_bt142_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_144_lotresult import (
    parse_bt195_bt144_unpublished_identifier,
    merge_bt195_bt144_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_160_tender import (
    parse_bt195_bt160_unpublished_identifier,
    merge_bt195_bt160_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_162_tender import (
    parse_bt195_bt162_unpublished_identifier,
    merge_bt195_bt162_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_163_tender import (
    parse_bt195_bt163_unpublished_identifier,
    merge_bt195_bt163_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_171_tender import (
    parse_bt195_bt171_unpublished_identifier,
    merge_bt195_bt171_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_191_tender import (
    parse_bt195_bt191_unpublished_identifier,
    merge_bt195_bt191_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_193_tender import (
    parse_bt195_bt193_unpublished_identifier,
    merge_bt195_bt193_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_539_lot import (
    parse_bt195_bt539_unpublished_identifier,
    merge_bt195_bt539_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_539_lotsgroup import (
    parse_bt195_bt539_lotsgroup_unpublished_identifier,
    merge_bt195_bt539_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_540_lot import (
    parse_bt195_bt540_lot_unpublished_identifier,
    merge_bt195_bt540_lot_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_540_lotsgroup import (
    parse_bt195_bt540_lotsgroup_unpublished_identifier,
    merge_bt195_bt540_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lot_fixed import (
    parse_bt195_bt541_lot_fixed_unpublished_identifier,
    merge_bt195_bt541_lot_fixed_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lot_threshold import (
    parse_bt195_bt541_lot_threshold_unpublished_identifier,
    merge_bt195_bt541_lot_threshold_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lot_weight import (
    parse_bt195_bt541_lot_weight_unpublished_identifier,
    merge_bt195_bt541_lot_weight_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lotsgroup_fixed import (
    parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
    merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lotsgroup_threshold import (
    parse_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
    merge_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_541_lotsgroup_weight import (
    parse_bt195_bt541_lotsgroup_weight,
    merge_bt195_bt541_lotsgroup_weight,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_5421_lot import (
    parse_bt195_bt5421_lot,
    merge_bt195_bt5421_lot,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_5421_lotsgroup import (
    parse_bt195_bt5421_lotsgroup,
    merge_bt195_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_5422_lot import (
    parse_bt195_bt5422_lot,
    merge_bt195_bt5422_lot,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_5422_lotsgroup import (
    parse_bt195_bt5422_lotsgroup,
    merge_bt195_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_5423_lot import (
    parse_bt195_bt5423_lot,
    merge_bt195_bt5423_lot,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_5423_lotsgroup import (
    parse_bt195_bt5423_lotsgroup,
    merge_bt195_bt5423_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_543_lot import (
    parse_bt195_bt543_lot,
    merge_bt195_bt543_lot,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_543_lotsgroup import (
    parse_bt195_bt543_lotsgroup,
    merge_bt195_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_553_tender import (
    parse_bt195_bt553_tender,
    merge_bt195_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_554_tender import (
    parse_bt195_bt554_unpublished_identifier,
    merge_bt195_bt554_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_555_tender import (
    parse_bt195_bt555_unpublished_identifier,
    merge_bt195_bt555_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_635_lotresult import (
    parse_bt195_bt635_unpublished_identifier,
    merge_bt195_bt635_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.bt_195_bt_636_lotresult import (
    parse_bt195_bt636_unpublished_identifier,
    merge_bt195_bt636_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_660_lotresult import (
    parse_bt195_bt660_unpublished_identifier,
    merge_bt195_bt660_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_709_lotresult import (
    parse_bt195_bt709_unpublished_identifier,
    merge_bt195_bt709_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_710_lotresult import (
    parse_bt195_bt710_unpublished_identifier,
    merge_bt195_bt710_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_711_lotresult import (
    parse_bt195_bt711_unpublished_identifier,
    merge_bt195_bt711_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_712_lotresult import (
    parse_bt195_bt712_unpublished_identifier,
    merge_bt195_bt712_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_720_tender import (
    parse_bt195_bt720_unpublished_identifier,
    merge_bt195_bt720_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_733_lot import (
    parse_bt195_bt733_unpublished_identifier,
    merge_bt195_bt733_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_733_lotsgroup import (
    parse_bt195_bt733_lotsgroup_unpublished_identifier,
    merge_bt195_bt733_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_734_lot import (
    parse_bt195_bt734_lot_unpublished_identifier,
    merge_bt195_bt734_lot_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_734_lotsgroup import (
    parse_bt195_bt734_lotsgroup_unpublished_identifier,
    merge_bt195_bt734_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_759_lotresult import (
    parse_bt195_bt759_lotresult_unpublished_identifier,
    merge_bt195_bt759_lotresult_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_760_lotresult import (
    parse_bt195_bt760_lotresult_unpublished_identifier,
    merge_bt195_bt760_lotresult_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_773_tender import (
    parse_bt195_bt773_tender_unpublished_identifier,
    merge_bt195_bt773_tender_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_195_bt_88_procedure import (
    parse_bt195_bt88_procedure_unpublished_identifier,
    merge_bt195_bt88_procedure_unpublished_identifier,
)

# BT_196
from ted_and_doffin_to_ocds.converters.bt_196_bt_09_procedure import (
    bt_196_parse_unpublished_justification_bt_09_procedure,
    bt_196_merge_unpublished_justification_bt_09_procedure,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_105_procedure import (
    parse_bt196_bt105_unpublished_justification,
    merge_bt196_bt105_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_106_procedure import (
    parse_bt196_bt106_unpublished_justification,
    merge_bt196_bt106_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_1252_procedure import (
    parse_bt196_bt1252_unpublished_justification,
    merge_bt196_bt1252_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_135_procedure import (
    parse_bt196_bt135_unpublished_justification,
    merge_bt196_bt135_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_1351_procedure import (
    parse_bt196_bt1351_unpublished_justification,
    merge_bt196_bt1351_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_136_procedure import (
    parse_bt196_bt136_unpublished_justification,
    merge_bt196_bt136_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_142_lotresult import (
    parse_bt196_bt142_unpublished_justification,
    merge_bt196_bt142_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_144_lotresult import (
    parse_bt196_bt144_unpublished_justification,
    merge_bt196_bt144_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_160_tender import (
    parse_bt196_bt160_unpublished_justification,
    merge_bt196_bt160_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_162_tender import (
    parse_bt196_bt162_unpublished_justification,
    merge_bt196_bt162_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_163_tender import (
    parse_bt196_bt163_unpublished_justification,
    merge_bt196_bt163_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_171_tender import (
    parse_bt196_bt171_unpublished_justification,
    merge_bt196_bt171_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_191_tender import (
    parse_bt196_bt191_unpublished_justification,
    merge_bt196_bt191_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_193_tender import (
    parse_bt196_bt193_unpublished_justification,
    merge_bt196_bt193_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_539_lot import (
    parse_bt196_bt539_unpublished_justification,
    merge_bt196_bt539_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_539_lotsgroup import (
    parse_bt196_bt539_lotsgroup_unpublished_justification,
    merge_bt196_bt539_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_540_lot import (
    parse_bt196_bt540_lot_unpublished_justification,
    merge_bt196_bt540_lot_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_540_lotsgroup import (
    parse_bt196_bt540_lotsgroup_unpublished_justification,
    merge_bt196_bt540_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lot_fixed import (
    parse_bt196_bt541_lot_fixed_unpublished_justification,
    merge_bt196_bt541_lot_fixed_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lot_threshold import (
    parse_bt196_bt541_lot_threshold_unpublished_justification,
    merge_bt196_bt541_lot_threshold_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lot_weight import (
    parse_bt196_bt541_lot_weight_unpublished_justification,
    merge_bt196_bt541_lot_weight_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lotsgroup_fixed import (
    parse_bt196_bt541_lotsgroup_fixed_unpublished_justification,
    merge_bt196_bt541_lotsgroup_fixed_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lotsgroup_threshold import (
    parse_bt196_bt541_lotsgroup_threshold_unpublished_justification,
    merge_bt196_bt541_lotsgroup_threshold_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_541_lotsgroup_weight import (
    parse_bt196_bt541_lotsgroup_weight,
    merge_bt196_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5421_lot import (
    parse_bt196_bt5421_lot,
    merge_bt196_bt5421_lot,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5421_lotsgroup import (
    parse_bt196_bt5421_lotsgroup,
    merge_bt196_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_5422_lot import (
    parse_bt196_bt5422_lot,
    merge_bt196_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_5422_lotsgroup import (
    parse_bt196_bt5422_lotsgroup,
    merge_bt196_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_5423_lot import (
    parse_bt196_bt5423_lot,
    merge_bt196_bt5423_lot,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_5423_lotsgroup import (
    parse_bt196_bt5423_lotsgroup,
    merge_bt196_bt5423_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_543_lot import (
    parse_bt196_bt543_lot,
    merge_bt196_bt543_lot,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_543_lotsgroup import (
    parse_bt196_bt543_lotsgroup,
    merge_bt196_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_553_tender import (
    parse_bt196_bt553_tender,
    merge_bt196_bt553_tender,
)

from ted_and_doffin_to_ocds.converters.bt_196_bt_554_tender import (
    parse_bt196_bt554_unpublished_justification,
    merge_bt196_bt554_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_555_tender import (
    parse_bt196_bt555_unpublished_justification,
    merge_bt196_bt555_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_635_lotresult import (
    parse_bt196_bt635_unpublished_justification,
    merge_bt196_bt635_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_636_lotresult import (
    parse_bt196_bt636_unpublished_justification,
    merge_bt196_bt636_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_660_lotresult import (
    parse_bt196_bt660_unpublished_justification,
    merge_bt196_bt660_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_709_lotresult import (
    parse_bt196_bt709_unpublished_justification,
    merge_bt196_bt709_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_710_lotresult import (
    parse_bt196_bt710_unpublished_justification,
    merge_bt196_bt710_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_711_lotresult import (
    parse_bt196_bt711_unpublished_justification,
    merge_bt196_bt711_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_712_lotresult import (
    parse_bt196_bt712_unpublished_justification,
    merge_bt196_bt712_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_720_tender import (
    parse_bt196_bt720_unpublished_justification,
    merge_bt196_bt720_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_733_lot import (
    parse_bt196_bt733_unpublished_justification,
    merge_bt196_bt733_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_733_lotsgroup import (
    parse_bt196_bt733_lotsgroup_unpublished_justification,
    merge_bt196_bt733_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_734_lot import (
    parse_bt196_bt734_lot_unpublished_justification,
    merge_bt196_bt734_lot_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_734_lotsgroup import (
    parse_bt196_bt734_lotsgroup_unpublished_justification,
    merge_bt196_bt734_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_759_lotresult import (
    parse_bt196_bt759_lotresult_unpublished_justification,
    merge_bt196_bt759_lotresult_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_760_lotresult import (
    parse_bt196_bt760_lotresult_unpublished_justification,
    merge_bt196_bt760_lotresult_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_773_tender import (
    parse_bt196_bt773_tender_unpublished_justification,
    merge_bt196_bt773_tender_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.bt_196_bt_88_procedure import (
    parse_bt196_bt88_procedure_unpublished_justification,
    merge_bt196_bt88_procedure_unpublished_justification,
)

# #BT_197
from ted_and_doffin_to_ocds.converters.bt_197_bt_09_procedure import (
    bt_197_parse_unpublished_justification_code_bt_09_procedure,
    bt_197_merge_unpublished_justification_code_bt_09_procedure,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_105_procedure import (
    parse_bt197_bt105_unpublished_justification_code,
    merge_bt197_bt105_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_106_procedure import (
    parse_bt197_bt106_unpublished_justification_code,
    merge_bt197_bt106_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_1252_procedure import (
    parse_bt197_bt1252_unpublished_justification_code,
    merge_bt197_bt1252_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_135_procedure import (
    parse_bt197_bt135_unpublished_justification_code,
    merge_bt197_bt135_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_1351_procedure import (
    parse_bt197_bt1351_unpublished_justification_code,
    merge_bt197_bt1351_unpublished_justification_code,
)


from ted_and_doffin_to_ocds.converters.bt_197_bt_136_procedure import (
    parse_bt197_bt136_unpublished_justification_code,
    merge_bt197_bt136_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_142_lotresult import (
    parse_bt197_bt142_unpublished_justification_code,
    merge_bt197_bt142_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_144_lotresult import (
    parse_bt197_bt144_unpublished_justification_code,
    merge_bt197_bt144_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_160_tender import (
    parse_bt197_bt160_unpublished_justification_code,
    merge_bt197_bt160_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_162_tender import (
    parse_bt197_bt162_unpublished_justification_code,
    merge_bt197_bt162_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_163_tender import (
    parse_bt197_bt163_unpublished_justification_code,
    merge_bt197_bt163_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_171_tender import (
    parse_bt197_bt171_unpublished_justification_code,
    merge_bt197_bt171_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_191_tender import (
    parse_bt197_bt191_unpublished_justification_code,
    merge_bt197_bt191_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_193_tender import (
    parse_bt197_bt193_unpublished_justification_code,
    merge_bt197_bt193_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_539_lot import (
    parse_bt197_bt539_unpublished_justification_code,
    merge_bt197_bt539_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_539_lotsgroup import (
    parse_bt197_bt539_lotsgroup_unpublished_justification_code,
    merge_bt197_bt539_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_540_lot import (
    parse_bt197_bt540_lot_unpublished_justification_code,
    merge_bt197_bt540_lot_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_540_lotsgroup import (
    parse_bt197_bt540_lotsgroup_unpublished_justification_code,
    merge_bt197_bt540_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lot_fixed import (
    parse_bt197_bt541_lot_fixed_unpublished_justification_code,
    merge_bt197_bt541_lot_fixed_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lot_threshold import (
    parse_bt197_bt541_lot_threshold_unpublished_justification_code,
    merge_bt197_bt541_lot_threshold_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lot_weight import (
    parse_bt197_bt541_lot_weight_unpublished_justification_code,
    merge_bt197_bt541_lot_weight_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lotsgroup_fixed import (
    parse_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
    merge_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lotsgroup import (
    parse_bt197_bt541_lotsgroup_threshold,
    merge_bt197_bt541_lotsgroup_threshold,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_541_lotsgroup_weight import (
    parse_bt197_bt541_lotsgroup_weight,
    merge_bt197_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5421_lot import (
    parse_bt197_bt5421_lot,
    merge_bt197_bt5421_lot,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_5421_lotsgroup import (
    parse_bt197_bt5421_lotsgroup,
    merge_bt197_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_5422_lot import (
    parse_bt197_bt5422_lot,
    merge_bt197_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5422_lotsgroup import (
    parse_bt197_bt5422_lotsgroup,
    merge_bt197_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_197_bt_5423_lot import (
    parse_bt197_bt5423_lot,
    merge_bt197_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_5423_lotsgroup import (
    parse_bt197_bt5423_lotsgroup,
    merge_bt197_bt5423_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_543_lot import (
    parse_bt197_bt543_lot,
    merge_bt197_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_543_lotsgroup import (
    parse_bt197_bt543_lotsgroup,
    merge_bt197_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_553_tender import (
    parse_bt197_bt553_tender,
    merge_bt197_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_554_tender import (
    parse_bt197_bt554_unpublished_justification_code,
    merge_bt197_bt554_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_555_tender import (
    parse_bt197_bt555_unpublished_justification_code,
    merge_bt197_bt555_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_635_lotresult import (
    parse_bt197_bt635_unpublished_justification_code,
    merge_bt197_bt635_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_636_lotresult import (
    parse_bt197_bt636_unpublished_justification_code,
    merge_bt197_bt636_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_660_lotresult import (
    parse_bt197_bt660_unpublished_justification_code,
    merge_bt197_bt660_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_709_lotresult import (
    parse_bt197_bt709_unpublished_justification_code,
    merge_bt197_bt709_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_710_lotresult import (
    parse_bt197_bt710_unpublished_justification_code,
    merge_bt197_bt710_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_711_lotresult import (
    parse_bt197_bt711_unpublished_justification_code,
    merge_bt197_bt711_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_712_lotresult import (
    parse_bt197_bt712_unpublished_justification_code,
    merge_bt197_bt712_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_720_tender import (
    parse_bt197_bt720_unpublished_justification_code,
    merge_bt197_bt720_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_733_lot import (
    parse_bt197_bt733_unpublished_justification_code,
    merge_bt197_bt733_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_733_lotsgroup import (
    parse_bt197_bt733_lotsgroup_unpublished_justification_code,
    merge_bt197_bt733_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_734_lot import (
    parse_bt197_bt734_lot_unpublished_justification_code,
    merge_bt197_bt734_lot_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_734_lotsgroup import (
    parse_bt197_bt734_lotsgroup_unpublished_justification_code,
    merge_bt197_bt734_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_759_lotresult import (
    parse_bt197_bt759_lotresult_unpublished_justification_code,
    merge_bt197_bt759_lotresult_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_760_lotresult import (
    parse_bt197_bt760_lotresult_unpublished_justification_code,
    merge_bt197_bt760_lotresult_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_773_tender import (
    parse_bt197_bt773_tender_unpublished_justification_code,
    merge_bt197_bt773_tender_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.bt_197_bt_88_procedure import (
    parse_bt197_bt88_procedure_unpublished_justification_code,
    merge_bt197_bt88_procedure_unpublished_justification_code,
)

#
# #BT_198
from ted_and_doffin_to_ocds.converters.bt_198_bt_09_procedure import (
    bt_198_parse_unpublished_access_date_bt_09_procedure,
    bt_198_merge_unpublished_access_date_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_105_procedure import (
    parse_bt198_bt105_unpublished_access_date,
    merge_bt198_bt105_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_106_procedure import (
    parse_bt198_bt106_unpublished_access_date,
    merge_bt198_bt106_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_1252_procedure import (
    parse_bt198_bt1252_unpublished_access_date,
    merge_bt198_bt1252_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_135_procedure import (
    parse_bt198_bt135_unpublished_access_date,
    merge_bt198_bt135_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_1351_procedure import (
    parse_bt198_bt1351_unpublished_access_date,
    merge_bt198_bt1351_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_136_procedure import (
    parse_bt198_bt136_unpublished_access_date,
    merge_bt198_bt136_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_142_lotresult import (
    parse_bt198_bt142_unpublished_access_date,
    merge_bt198_bt142_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_144_lotresult import (
    parse_bt198_bt144_unpublished_access_date,
    merge_bt198_bt144_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_160_tender import (
    parse_bt198_bt160_unpublished_access_date,
    merge_bt198_bt160_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_162_tender import (
    parse_bt198_bt162_unpublished_access_date,
    merge_bt198_bt162_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_163_tender import (
    parse_bt198_bt163_unpublished_access_date,
    merge_bt198_bt163_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_171_tender import (
    parse_bt198_bt171_unpublished_access_date,
    merge_bt198_bt171_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_191_tender import (
    parse_bt198_bt191_unpublished_access_date,
    merge_bt198_bt191_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_193_tender import (
    parse_bt198_bt193_unpublished_access_date,
    merge_bt198_bt193_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_539_lot import (
    parse_bt198_bt539_unpublished_access_date,
    merge_bt198_bt539_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_539_lotsgroup import (
    parse_bt198_bt539_lotsgroup_unpublished_access_date,
    merge_bt198_bt539_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_540_lot import (
    parse_bt198_bt540_lot_unpublished_access_date,
    merge_bt198_bt540_lot_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_540_lotsgroup import (
    parse_bt198_bt540_lotsgroup_unpublished_access_date,
    merge_bt198_bt540_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lot_fixed import (
    parse_bt198_bt541_lot_fixed_unpublished_access_date,
    merge_bt198_bt541_lot_fixed_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lot_threshold import (
    parse_bt198_bt541_lot_threshold_unpublished_access_date,
    merge_bt198_bt541_lot_threshold_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lot_weight import (
    parse_bt198_bt541_lot_weight_unpublished_access_date,
    merge_bt198_bt541_lot_weight_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lotsgroup_fixed import (
    parse_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
    merge_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lotsgroup import (
    parse_bt198_bt541_lotsgroup_threshold,
    merge_bt198_bt541_lotsgroup_threshold,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_541_lotsgroup_weight import (
    parse_bt198_bt541_lotsgroup_weight,
    merge_bt198_bt541_lotsgroup_weight,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_5421_lot import (
    parse_bt198_bt5421_lot,
    merge_bt198_bt5421_lot,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_5421_lotsgroup import (
    parse_bt198_bt5421_lotsgroup,
    merge_bt198_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_5422_lot import (
    parse_bt198_bt5422_lot,
    merge_bt198_bt5422_lot,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_5422_lotsgroup import (
    parse_bt198_bt5422_lotsgroup,
    merge_bt198_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.bt_198_bt_5423_lot import (
    parse_bt198_bt5423_lot,
    merge_bt198_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_5423_lotsgroup import (
    parse_bt198_bt5423_lotsgroup,
    merge_bt198_bt5423_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_543_lot import (
    parse_bt198_bt543_lot,
    merge_bt198_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_543_lotsgroup import (
    parse_bt198_bt543_lotsgroup,
    merge_bt198_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_553_tender import (
    parse_bt198_bt553_tender,
    merge_bt198_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_554_tender import (
    parse_bt198_bt554_unpublished_access_date,
    merge_bt198_bt554_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_555_tender import (
    parse_bt198_bt555_unpublished_access_date,
    merge_bt198_bt555_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_635_lotresult import (
    parse_bt198_bt635_unpublished_access_date,
    merge_bt198_bt635_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_636_lotresult import (
    parse_bt198_bt636_unpublished_access_date,
    merge_bt198_bt636_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_660_lotresult import (
    parse_bt198_bt660_unpublished_access_date,
    merge_bt198_bt660_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_709_lotresult import (
    parse_bt198_bt709_unpublished_access_date,
    merge_bt198_bt709_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_710_lotresult import (
    parse_bt198_bt710_unpublished_access_date,
    merge_bt198_bt710_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_711_lotresult import (
    parse_bt198_bt711_unpublished_access_date,
    merge_bt198_bt711_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_712_lotresult import (
    parse_bt198_bt712_unpublished_access_date,
    merge_bt198_bt712_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_720_tender import (
    parse_bt198_bt720_unpublished_access_date,
    merge_bt198_bt720_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_733_lot import (
    parse_bt198_bt733_unpublished_access_date,
    merge_bt198_bt733_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_733_lotsgroup import (
    parse_bt198_bt733_lotsgroup_unpublished_access_date,
    merge_bt198_bt733_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_734_lot import (
    parse_bt198_bt734_lot_unpublished_access_date,
    merge_bt198_bt734_lot_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_734_lotsgroup import (
    parse_bt198_bt734_lotsgroup_unpublished_access_date,
    merge_bt198_bt734_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_759_lotresult import (
    parse_bt198_bt759_lotresult_unpublished_access_date,
    merge_bt198_bt759_lotresult_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_760_lotresult import (
    parse_bt198_bt760_lotresult_unpublished_access_date,
    merge_bt198_bt760_lotresult_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_773_tender import (
    parse_bt198_bt773_tender_unpublished_access_date,
    merge_bt198_bt773_tender_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.bt_198_bt_88_procedure import (
    parse_bt198_bt88_procedure_unpublished_access_date,
    merge_bt198_bt88_procedure_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.bt_200_contract import (
    parse_contract_modification_reason,
    merge_contract_modification_reason,
)
from ted_and_doffin_to_ocds.converters.bt_201_contract import (
    parse_contract_modification_description,
    merge_contract_modification_description,
)
from ted_and_doffin_to_ocds.converters.bt_202_contract import (
    parse_contract_modification_summary,
    merge_contract_modification_summary,
)
from ted_and_doffin_to_ocds.converters.bt_21_lot import parse_lot_title, merge_lot_title
from ted_and_doffin_to_ocds.converters.bt_21_lotsgroup import (
    parse_lots_group_title,
    merge_lots_group_title,
)
from ted_and_doffin_to_ocds.converters.bt_21_part import (
    parse_part_title,
    merge_part_title,
)
from ted_and_doffin_to_ocds.converters.bt_21_procedure import (
    parse_procedure_title,
    merge_procedure_title,
)
from ted_and_doffin_to_ocds.converters.bt_22_lot import (
    parse_lot_internal_identifier,
    merge_lot_internal_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_23_lot import (
    parse_main_nature,
    merge_main_nature,
)
from ted_and_doffin_to_ocds.converters.bt_23_part import (
    parse_main_nature_part,
    merge_main_nature_part,
)
from ted_and_doffin_to_ocds.converters.bt_23_procedure import (
    parse_main_nature_procedure,
    merge_main_nature_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_24_lot import (
    parse_lot_description,
    merge_lot_description,
)
from ted_and_doffin_to_ocds.converters.bt_24_lotsgroup import (
    parse_lots_group_description,
    merge_lots_group_description,
)
from ted_and_doffin_to_ocds.converters.bt_24_part import (
    parse_part_description,
    merge_part_description,
)
from ted_and_doffin_to_ocds.converters.bt_24_procedure import (
    parse_procedure_description,
    merge_procedure_description,
)
from ted_and_doffin_to_ocds.converters.bt_25_lot import (
    parse_lot_quantity,
    merge_lot_quantity,
)
from ted_and_doffin_to_ocds.converters.bt_26a_lot import (
    parse_classification_type,
    merge_classification_type,
)
from ted_and_doffin_to_ocds.converters.bt_26a_part import (
    parse_classification_type_part,
    merge_classification_type_part,
)
from ted_and_doffin_to_ocds.converters.bt_26a_procedure import (
    parse_classification_type_procedure,
    merge_classification_type_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_26m_lot import (
    parse_main_classification_type_lot,
    merge_main_classification_type_lot,
)
from ted_and_doffin_to_ocds.converters.bt_26m_part import (
    parse_main_classification_type_part,
    merge_main_classification_type_part,
)
from ted_and_doffin_to_ocds.converters.bt_26m_procedure import (
    parse_main_classification_type_procedure,
    merge_main_classification_type_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_262_lot import (
    parse_main_classification_code_lot,
    merge_main_classification_code_lot,
)
from ted_and_doffin_to_ocds.converters.bt_262_part import (
    parse_main_classification_code_part,
    merge_main_classification_code_part,
)
from ted_and_doffin_to_ocds.converters.bt_262_procedure import (
    parse_main_classification_code_procedure,
    merge_main_classification_code_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_263_lot import (
    parse_additional_classification_code_lot,
    merge_additional_classification_code_lot,
)
from ted_and_doffin_to_ocds.converters.bt_263_part import (
    parse_additional_classification_code_part,
    merge_additional_classification_code_part,
)
from ted_and_doffin_to_ocds.converters.bt_263_procedure import (
    parse_additional_classification_code_procedure,
    merge_additional_classification_code_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_27_lot import (
    parse_lot_estimated_value,
    merge_lot_estimated_value,
)
from ted_and_doffin_to_ocds.converters.bt_27_lotsgroup import (
    parse_bt_27_lots_group,
    merge_bt_27_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_27_part import (
    parse_bt_27_part,
    merge_bt_27_part,
)
from ted_and_doffin_to_ocds.converters.bt_27_procedure import (
    parse_bt_27_procedure,
    merge_bt_27_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_271_lot import (
    parse_bt_271_lot,
    merge_bt_271_lot,
)
from ted_and_doffin_to_ocds.converters.bt_271_lotsgroup import (
    parse_bt_271_lots_group,
    merge_bt_271_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_271_procedure import (
    parse_bt_271_procedure,
    merge_bt_271_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_300_lot import (
    parse_lot_additional_info,
    merge_lot_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_300_lotsgroup import (
    parse_lotsgroup_additional_info,
    merge_lotsgroup_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_300_part import (
    parse_part_additional_info,
    merge_part_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_300_procedure import (
    parse_procedure_additional_info,
    merge_procedure_additional_info,
)
from ted_and_doffin_to_ocds.converters.bt_31_procedure import (
    parse_max_lots_allowed,
    merge_max_lots_allowed,
)
from ted_and_doffin_to_ocds.converters.bt_3201_tender import (
    parse_tender_identifier,
    merge_tender_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_3202_contract import (
    parse_contract_tender_id,
    merge_contract_tender_id,
)
from ted_and_doffin_to_ocds.converters.bt_33_procedure import (
    parse_max_lots_awarded,
    merge_max_lots_awarded,
)
from ted_and_doffin_to_ocds.converters.bt_330_procedure import (
    parse_group_identifier,
    merge_group_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_36_lot import (
    parse_lot_duration,
    merge_lot_duration,
)
from ted_and_doffin_to_ocds.converters.bt_36_part import (
    parse_part_duration,
    merge_part_duration,
)
from ted_and_doffin_to_ocds.converters.bt_40_lot import (
    parse_lot_selection_criteria_second_stage,
    merge_lot_selection_criteria_second_stage,
)
from ted_and_doffin_to_ocds.converters.bt_41_lot import (
    parse_lot_following_contract,
    merge_lot_following_contract,
)
from ted_and_doffin_to_ocds.converters.bt_42_lot import (
    parse_lot_jury_decision_binding,
    merge_lot_jury_decision_binding,
)
from ted_and_doffin_to_ocds.converters.bt_44_lot import (
    parse_prize_rank,
    merge_prize_rank,
)
from ted_and_doffin_to_ocds.converters.bt_45_lot import (
    parse_lot_rewards_other,
    merge_lot_rewards_other,
)
from ted_and_doffin_to_ocds.converters.bt_46_lot import (
    parse_jury_member_name,
    merge_jury_member_name,
)
from ted_and_doffin_to_ocds.converters.bt_47_lot import (
    parse_participant_name,
    merge_participant_name,
)
from ted_and_doffin_to_ocds.converters.bt_50_lot import (
    parse_minimum_candidates,
    merge_minimum_candidates,
)
from ted_and_doffin_to_ocds.converters.bt_500_organization_company import (
    parse_organization_name,
    merge_organization_name,
)
from ted_and_doffin_to_ocds.converters.bt_500_organization_touchpoint import (
    parse_touchpoint_name,
    merge_touchpoint_name,
)
from ted_and_doffin_to_ocds.converters.bt_500_ubo import parse_ubo_name, merge_ubo_name
from ted_and_doffin_to_ocds.converters.bt_501_organization_company import (
    parse_organization_identifier,
    merge_organization_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_5010_lot import (
    parse_eu_funds_financing_identifier,
    merge_eu_funds_financing_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_5011_contract import (
    parse_contract_eu_funds_financing_identifier,
    merge_contract_eu_funds_financing_identifier,
)
from ted_and_doffin_to_ocds.converters.bt_502_organization_company import (
    parse_organization_contact_point,
    merge_organization_contact_point,
)
from ted_and_doffin_to_ocds.converters.bt_502_organization_touchpoint import (
    parse_touchpoint_contact_point,
    merge_touchpoint_contact_point,
)
from ted_and_doffin_to_ocds.converters.bt_503_organization_company import (
    parse_organization_contact_telephone,
    merge_organization_contact_telephone,
)
from ted_and_doffin_to_ocds.converters.bt_503_organization_touchpoint import (
    parse_touchpoint_contact_telephone,
    merge_touchpoint_contact_telephone,
)
from ted_and_doffin_to_ocds.converters.bt_503_ubo import (
    parse_ubo_telephone,
    merge_ubo_telephone,
)
from ted_and_doffin_to_ocds.converters.bt_505_organization_company import (
    parse_organization_website,
    merge_organization_website,
)
from ted_and_doffin_to_ocds.converters.bt_505_organization_touchpoint import (
    parse_touchpoint_website,
    merge_touchpoint_website,
)
from ted_and_doffin_to_ocds.converters.bt_506_organization_company import (
    parse_organization_contact_email,
    merge_organization_contact_email,
)
from ted_and_doffin_to_ocds.converters.bt_506_organization_touchpoint import (
    parse_touchpoint_contact_email,
    merge_touchpoint_contact_email,
)
from ted_and_doffin_to_ocds.converters.bt_506_ubo import (
    parse_ubo_email,
    merge_ubo_email,
)
from ted_and_doffin_to_ocds.converters.bt_507_organization_company import (
    parse_organization_country_subdivision,
    merge_organization_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_507_organization_touchpoint import (
    parse_touchpoint_country_subdivision,
    merge_touchpoint_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_507_ubo import (
    parse_ubo_country_subdivision,
    merge_ubo_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_5071_lot import (
    parse_place_performance_country_subdivision,
    merge_place_performance_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_5071_part import (
    parse_part_place_performance_country_subdivision,
    merge_part_place_performance_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_5071_procedure import (
    parse_procedure_place_performance_country_subdivision,
    merge_procedure_place_performance_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.bt_508_procedure_buyer import (
    parse_buyer_profile_url,
    merge_buyer_profile_url,
)
from ted_and_doffin_to_ocds.converters.bt_509_organization_company import (
    parse_organization_edelivery_gateway,
    merge_organization_edelivery_gateway,
)
from ted_and_doffin_to_ocds.converters.bt_509_organization_touchpoint import (
    parse_touchpoint_edelivery_gateway,
    merge_touchpoint_edelivery_gateway,
)
from ted_and_doffin_to_ocds.converters.bt_51_lot import (
    parse_lot_maximum_candidates,
    merge_lot_maximum_candidates,
)
from ted_and_doffin_to_ocds.converters.bt_510a_organization_company import (
    parse_organization_street,
    merge_organization_street,
)
from ted_and_doffin_to_ocds.converters.bt_510a_organization_touchpoint import (
    parse_touchpoint_street,
    merge_touchpoint_street,
)
from ted_and_doffin_to_ocds.converters.bt_510a_ubo import (
    parse_ubo_street,
    merge_ubo_street,
)
from ted_and_doffin_to_ocds.converters.bt_510b_organization_company import (
    parse_organization_streetline1,
    merge_organization_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_510b_organization_touchpoint import (
    parse_touchpoint_streetline1,
    merge_touchpoint_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_510b_ubo import (
    parse_ubo_streetline1,
    merge_ubo_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_510c_organization_company import (
    parse_organization_streetline2,
    merge_organization_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_510c_organization_touchpoint import (
    parse_touchpoint_streetline2,
    merge_touchpoint_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_510c_ubo import (
    parse_ubo_streetline2,
    merge_ubo_streetline2,
)

from ted_and_doffin_to_ocds.converters.bt_5101_lot import (
    parse_place_performance_street_lot,
    merge_place_performance_street_lot,
)
from ted_and_doffin_to_ocds.converters.bt_5101a_part import (
    parse_part_place_performance_street,
    merge_part_place_performance_street,
)
from ted_and_doffin_to_ocds.converters.bt_5101a_procedure import (
    parse_procedure_place_performance_street,
    merge_procedure_place_performance_street,
)

from ted_and_doffin_to_ocds.converters.bt_5101b_part import (
    parse_part_place_performance_streetline1,
    merge_part_place_performance_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_5101b_procedure import (
    parse_procedure_place_performance_streetline1,
    merge_procedure_place_performance_streetline1,
)
from ted_and_doffin_to_ocds.converters.bt_5101c_part import (
    parse_part_place_performance_streetline2,
    merge_part_place_performance_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_5101c_procedure import (
    parse_procedure_place_performance_streetline2,
    merge_procedure_place_performance_streetline2,
)
from ted_and_doffin_to_ocds.converters.bt_512_organization_company import (
    parse_organization_postcode,
    merge_organization_postcode,
)
from ted_and_doffin_to_ocds.converters.bt_512_organization_touchpoint import (
    parse_touchpoint_postcode,
    merge_touchpoint_postcode,
)
from ted_and_doffin_to_ocds.converters.bt_512_ubo import (
    parse_ubo_postcode,
    merge_ubo_postcode,
)
from ted_and_doffin_to_ocds.converters.bt_5121_lot import (
    parse_place_performance_post_code,
    merge_place_performance_post_code,
)
from ted_and_doffin_to_ocds.converters.bt_5121_part import (
    parse_place_performance_post_code_part,
    merge_place_performance_post_code_part,
)
from ted_and_doffin_to_ocds.converters.bt_5121_procedure import (
    parse_place_performance_post_code_procedure,
    merge_place_performance_post_code_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_513_organization_company import (
    parse_organization_city,
    merge_organization_city,
)
from ted_and_doffin_to_ocds.converters.bt_513_organization_touchpoint import (
    parse_touchpoint_city,
    merge_touchpoint_city,
)
from ted_and_doffin_to_ocds.converters.bt_513_ubo import parse_ubo_city, merge_ubo_city
from ted_and_doffin_to_ocds.converters.bt_5131_lot import (
    parse_place_performance_city,
    merge_place_performance_city,
)
from ted_and_doffin_to_ocds.converters.bt_5131_part import (
    parse_place_performance_city_part,
    merge_place_performance_city_part,
)
from ted_and_doffin_to_ocds.converters.bt_5131_procedure import (
    parse_place_performance_city_procedure,
    merge_place_performance_city_procedure,
)
from ted_and_doffin_to_ocds.converters.bt_514_organization_company import (
    parse_organization_country,
    merge_organization_country,
)
from ted_and_doffin_to_ocds.converters.bt_514_organization_touchpoint import (
    parse_touchpoint_country,
    merge_touchpoint_country,
)
from ted_and_doffin_to_ocds.converters.bt_514_ubo import (
    parse_ubo_country,
    merge_ubo_country,
)
from ted_and_doffin_to_ocds.converters.bt_5141_lot import (
    parse_lot_country,
    merge_lot_country,
)
from ted_and_doffin_to_ocds.converters.bt_5141_part import (
    parse_part_country,
    merge_part_country,
)
from ted_and_doffin_to_ocds.converters.bt_5141_procedure import (
    parse_procedure_country,
    merge_procedure_country,
)
from ted_and_doffin_to_ocds.converters.bt_52_lot import (
    parse_successive_reduction_indicator,
    merge_successive_reduction_indicator,
)
from ted_and_doffin_to_ocds.converters.bt_531_lot import (
    parse_lot_additional_nature,
    merge_lot_additional_nature,
)
from ted_and_doffin_to_ocds.converters.bt_531_part import (
    parse_part_additional_nature,
    merge_part_additional_nature,
)
from ted_and_doffin_to_ocds.converters.bt_531_procedure import (
    parse_procedure_additional_nature,
    merge_procedure_additional_nature,
)
from ted_and_doffin_to_ocds.converters.bt_536_lot import (
    parse_lot_start_date,
    merge_lot_start_date,
)
from ted_and_doffin_to_ocds.converters.bt_536_part import (
    parse_part_contract_start_date,
    merge_part_contract_start_date,
)
from ted_and_doffin_to_ocds.converters.bt_537_lot import (
    parse_lot_duration_end_date,
    merge_lot_duration_end_date,
)
from ted_and_doffin_to_ocds.converters.bt_537_part import (
    parse_part_duration_end_date,
    merge_part_duration_end_date,
)
from ted_and_doffin_to_ocds.converters.bt_538_lot import (
    parse_lot_duration_other,
    merge_lot_duration_other,
)
from ted_and_doffin_to_ocds.converters.bt_538_part import (
    parse_part_duration_other,
    merge_part_duration_other,
)
from ted_and_doffin_to_ocds.converters.bt_539_lot import (
    parse_award_criterion_type,
    merge_award_criterion_type,
)
from ted_and_doffin_to_ocds.converters.bt_54_lot import (
    parse_options_description,
    merge_options_description,
)
from ted_and_doffin_to_ocds.converters.bt_540_lot import (
    parse_award_criterion_description,
    merge_award_criterion_description,
)
from ted_and_doffin_to_ocds.converters.bt_540_lotsgroup import (
    parse_award_criterion_description_lots_group,
    merge_award_criterion_description_lots_group,
)
from ted_and_doffin_to_ocds.converters.bt_541_lot_fixednumber import (
    parse_award_criterion_fixed_number,
    merge_award_criterion_fixed_number,
)

from ted_and_doffin_to_ocds.converters.bt_5423_lot import (
    parse_award_criterion_number_threshold,
    merge_award_criterion_number_threshold,
)
from ted_and_doffin_to_ocds.converters.bt_5423_lotsgroup import (
    parse_award_criterion_number_threshold_lotsgroup,
    merge_award_criterion_number_threshold_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_543_lot import (
    parse_award_criteria_complicated,
    merge_award_criteria_complicated,
)
from ted_and_doffin_to_ocds.converters.bt_543_lotsgroup import (
    parse_award_criteria_complicated_lotsgroup,
    merge_award_criteria_complicated_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_553_tender import (
    parse_subcontracting_value,
    merge_subcontracting_value,
)
from ted_and_doffin_to_ocds.converters.bt_554_tender import (
    parse_subcontracting_description,
    merge_subcontracting_description,
)
from ted_and_doffin_to_ocds.converters.bt_555_tender import (
    parse_subcontracting_percentage,
    merge_subcontracting_percentage,
)
from ted_and_doffin_to_ocds.converters.bt_57_lot import (
    parse_renewal_description,
    merge_renewal_description,
)
from ted_and_doffin_to_ocds.converters.bt_58_lot import (
    parse_renewal_maximum,
    merge_renewal_maximum,
)
from ted_and_doffin_to_ocds.converters.bt_60_lot import parse_eu_funds, merge_eu_funds
from ted_and_doffin_to_ocds.converters.bt_610_procedure_buyer import (
    parse_activity_entity,
    merge_activity_entity,
)
from ted_and_doffin_to_ocds.converters.bt_6110_contract import (
    parse_contract_eu_funds_details,
    merge_contract_eu_funds_details,
)
from ted_and_doffin_to_ocds.converters.bt_6140_lot import (
    parse_lot_eu_funds_details,
    merge_lot_eu_funds_details,
)
from ted_and_doffin_to_ocds.converters.bt_615_lot import (
    parse_documents_restricted_url,
    merge_documents_restricted_url,
)
from ted_and_doffin_to_ocds.converters.bt_615_part import (
    parse_documents_restricted_url_part,
    merge_documents_restricted_url_part,
)
from ted_and_doffin_to_ocds.converters.bt_625_lot import parse_unit, merge_unit
from ted_and_doffin_to_ocds.converters.bt_63_lot import parse_variants, merge_variants
from ted_and_doffin_to_ocds.converters.bt_630_lot import (
    parse_deadline_receipt_expressions,
    merge_deadline_receipt_expressions,
)
from ted_and_doffin_to_ocds.converters.bt_631_lot import (
    parse_dispatch_invitation_interest,
    merge_dispatch_invitation_interest,
)
from ted_and_doffin_to_ocds.converters.bt_632_lot import (
    parse_tool_name,
    merge_tool_name,
)
from ted_and_doffin_to_ocds.converters.bt_632_part import (
    parse_tool_name_part,
    merge_tool_name_part,
)
from ted_and_doffin_to_ocds.converters.bt_633_organization import (
    parse_organization_natural_person,
    merge_organization_natural_person,
)
from ted_and_doffin_to_ocds.converters.bt_635_lotresult import (
    parse_buyer_review_requests_count,
    merge_buyer_review_requests_count,
)
from ted_and_doffin_to_ocds.converters.bt_636_lotresult import (
    parse_irregularity_type,
    merge_irregularity_type,
)
from ted_and_doffin_to_ocds.converters.bt_64_lot import (
    parse_subcontracting_obligation_minimum,
    merge_subcontracting_obligation_minimum,
)
from ted_and_doffin_to_ocds.converters.bt_644_lot_prize_value import (
    parse_lot_prize_value,
    merge_lot_prize_value,
)
from ted_and_doffin_to_ocds.converters.bt_65_lot_subcontracting_obligation import (
    parse_subcontracting_obligation,
    merge_subcontracting_obligation,
)
from ted_and_doffin_to_ocds.converters.bt_651_lot_subcontracting_tender_indication import (
    parse_subcontracting_tender_indication,
    merge_subcontracting_tender_indication,
)
from ted_and_doffin_to_ocds.converters.bt_660_lotresult import (
    parse_framework_reestimated_value,
    merge_framework_reestimated_value,
)
from ted_and_doffin_to_ocds.converters.bt_67_exclusion_grounds import (
    parse_exclusion_grounds,
    merge_exclusion_grounds,
)
from ted_and_doffin_to_ocds.converters.bt_70_lot import (
    parse_lot_performance_terms,
    merge_lot_performance_terms,
)
from ted_and_doffin_to_ocds.converters.bt_702a_notice import (
    parse_notice_language,
    merge_notice_language,
)
from ted_and_doffin_to_ocds.converters.bt_706_ubo import (
    parse_ubo_nationality,
    merge_ubo_nationality,
)
from ted_and_doffin_to_ocds.converters.bt_707_lot import (
    parse_lot_documents_restricted_justification,
    merge_lot_documents_restricted_justification,
)
from ted_and_doffin_to_ocds.converters.bt_707_part import (
    parse_part_documents_restricted_justification,
    merge_part_documents_restricted_justification,
)
from ted_and_doffin_to_ocds.converters.bt_708_lot import (
    parse_lot_documents_official_language,
    merge_lot_documents_official_language,
)
from ted_and_doffin_to_ocds.converters.bt_708_part import (
    parse_part_documents_official_language,
    merge_part_documents_official_language,
)
from ted_and_doffin_to_ocds.converters.bt_709_lotresult import (
    parse_framework_maximum_value,
    merge_framework_maximum_value,
)
from ted_and_doffin_to_ocds.converters.bt_71_lot import (
    parse_reserved_participation,
    merge_reserved_participation,
)
from ted_and_doffin_to_ocds.converters.bt_71_part import (
    parse_reserved_participation_part,
    merge_reserved_participation_part,
)
from ted_and_doffin_to_ocds.converters.bt_710_lotresult import (
    parse_tender_value_lowest,
    merge_tender_value_lowest,
)
from ted_and_doffin_to_ocds.converters.bt_711_lotresult import (
    parse_tender_value_highest,
    merge_tender_value_highest,
)
from ted_and_doffin_to_ocds.converters.bt_712a_lotresult import (
    parse_buyer_review_complainants,
    merge_buyer_review_complainants,
)
from ted_and_doffin_to_ocds.converters.bt_712b_lotresult import (
    parse_buyer_review_complainants_bt_712b,
    merge_buyer_review_complainants_bt_712b,
)
from ted_and_doffin_to_ocds.converters.bt_717_lot import (
    parse_clean_vehicles_directive,
    merge_clean_vehicles_directive,
)
from ted_and_doffin_to_ocds.converters.bt_719_notice import (
    parse_procurement_documents_change_date,
    merge_procurement_documents_change_date,
)
from ted_and_doffin_to_ocds.converters.bt_720_tender import (
    parse_tender_value,
    merge_tender_value,
)
from ted_and_doffin_to_ocds.converters.bt_721_contract_title import (
    parse_contract_title,
    merge_contract_title,
)
from ted_and_doffin_to_ocds.converters.bt_722_contract import (
    parse_contract_eu_funds,
    merge_contract_eu_funds,
)
from ted_and_doffin_to_ocds.converters.bt_7220_lot import (
    parse_lot_eu_funds,
    merge_lot_eu_funds,
)
from ted_and_doffin_to_ocds.converters.bt_723_lotresult import (
    parse_vehicle_category,
    merge_vehicle_category,
)
from ted_and_doffin_to_ocds.converters.bt_726_lot import (
    parse_lot_sme_suitability,
    merge_lot_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.bt_726_lotsgroup import (
    parse_lots_group_sme_suitability,
    merge_lots_group_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.bt_726_part import (
    parse_part_sme_suitability,
    merge_part_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.bt_727_lot import (
    parse_lot_place_performance,
    merge_lot_place_performance,
)
from ted_and_doffin_to_ocds.converters.bt_727_part import (
    parse_part_place_performance,
    merge_part_place_performance,
)
from ted_and_doffin_to_ocds.converters.bt_727_procedure import (
    parse_procedure_place_performance,
    merge_procedure_place_performance,
)
from ted_and_doffin_to_ocds.converters.bt_728_lot import (
    parse_lot_place_performance_additional,
    merge_lot_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.bt_728_part import (
    parse_part_place_performance_additional,
    merge_part_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.bt_728_procedure import (
    parse_procedure_place_performance_additional,
    merge_procedure_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.bt_729_lot import (
    parse_lot_subcontracting_obligation_maximum,
    merge_lot_subcontracting_obligation_maximum,
)
from ted_and_doffin_to_ocds.converters.bt_732_lot import (
    parse_lot_security_clearance_description,
    merge_lot_security_clearance_description,
)
from ted_and_doffin_to_ocds.converters.bt_733_lot import (
    parse_lot_award_criteria_order_justification,
    merge_lot_award_criteria_order_justification,
)
from ted_and_doffin_to_ocds.converters.bt_733_lotsgroup import (
    parse_lots_group_award_criteria_order_justification,
    merge_lots_group_award_criteria_order_justification,
)
from ted_and_doffin_to_ocds.converters.bt_734_lot import (
    parse_award_criterion_name,
    merge_award_criterion_name,
)
from ted_and_doffin_to_ocds.converters.bt_734_lotsgroup import (
    parse_award_criterion_name_lotsgroup,
    merge_award_criterion_name_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.bt_735_lot import (
    parse_cvd_contract_type,
    merge_cvd_contract_type,
)
from ted_and_doffin_to_ocds.converters.bt_735_lotresult import (
    parse_cvd_contract_type_lotresult,
    merge_cvd_contract_type_lotresult,
)
from ted_and_doffin_to_ocds.converters.bt_736_lot import (
    parse_reserved_execution,
    merge_reserved_execution,
)
from ted_and_doffin_to_ocds.converters.bt_736_part import (
    parse_reserved_execution_part,
    merge_reserved_execution_part,
)
from ted_and_doffin_to_ocds.converters.bt_737_lot import (
    parse_documents_unofficial_language,
    merge_documents_unofficial_language,
)
from ted_and_doffin_to_ocds.converters.bt_737_part import (
    parse_documents_unofficial_language_part,
    merge_documents_unofficial_language_part,
)
from ted_and_doffin_to_ocds.converters.bt_738_notice import (
    parse_notice_preferred_publication_date,
    merge_notice_preferred_publication_date,
)
from ted_and_doffin_to_ocds.converters.bt_739_organization_company import (
    parse_organization_contact_fax,
    merge_organization_contact_fax,
)
from ted_and_doffin_to_ocds.converters.bt_739_organization_touchpoint import (
    parse_touchpoint_contact_fax,
    merge_touchpoint_contact_fax,
)
from ted_and_doffin_to_ocds.converters.bt_739_ubo import parse_ubo_fax, merge_ubo_fax
from ted_and_doffin_to_ocds.converters.bt_740_procedure_buyer import (
    parse_buyer_contracting_entity,
    merge_buyer_contracting_entity,
)
from ted_and_doffin_to_ocds.converters.bt_743_lot import (
    parse_electronic_invoicing,
    merge_electronic_invoicing,
)
from ted_and_doffin_to_ocds.converters.bt_744_lot import (
    parse_submission_electronic_signature,
    merge_submission_electronic_signature,
)
from ted_and_doffin_to_ocds.converters.bt_745_lot import (
    parse_submission_nonelectronic_description,
    merge_submission_nonelectronic_description,
)
from ted_and_doffin_to_ocds.converters.bt_746_organization import (
    parse_winner_listed,
    merge_winner_listed,
)
from ted_and_doffin_to_ocds.converters.bt_747_lot import (
    parse_selection_criteria_type,
    merge_selection_criteria_type,
)

# from ted_and_doffin_to_ocds.converters.bt_749_lot import parse_selection_criteria_name, merge_selection_criteria_name
from ted_and_doffin_to_ocds.converters.bt_75_lot import (
    parse_guarantee_required_description,
    merge_guarantee_required_description,
)
from ted_and_doffin_to_ocds.converters.bt_750_lot import (
    parse_selection_criteria,
    merge_selection_criteria,
)
from ted_and_doffin_to_ocds.converters.bt_752_lot_thresholdnumber import (
    parse_selection_criteria_threshold_number,
    merge_selection_criteria_threshold_number,
)
from ted_and_doffin_to_ocds.converters.bt_752_lot_weightnumber import (
    parse_selection_criteria_weight_number,
    merge_selection_criteria_weight_number,
)
from ted_and_doffin_to_ocds.converters.bt_7531_lot import (
    parse_selection_criteria_number_weight,
    merge_selection_criteria_number_weight,
)
from ted_and_doffin_to_ocds.converters.bt_7532_lot import (
    parse_selection_criteria_number_threshold,
    merge_selection_criteria_number_threshold,
)
from ted_and_doffin_to_ocds.converters.bt_754_lot import (
    parse_accessibility_criteria,
    merge_accessibility_criteria,
)
from ted_and_doffin_to_ocds.converters.bt_755_lot import (
    parse_accessibility_justification,
    merge_accessibility_justification,
)
from ted_and_doffin_to_ocds.converters.bt_756_procedure import (
    parse_pin_competition_termination,
    merge_pin_competition_termination,
)
from ted_and_doffin_to_ocds.converters.bt_759_lotresult import (
    parse_received_submissions_count,
    merge_received_submissions_count,
)
from ted_and_doffin_to_ocds.converters.bt_76_lot import (
    parse_tenderer_legal_form,
    merge_tenderer_legal_form,
)
from ted_and_doffin_to_ocds.converters.bt_760_lotresult import (
    parse_received_submissions_type,
    merge_received_submissions_type,
)
from ted_and_doffin_to_ocds.converters.bt_762_changereasondescription import (
    parse_change_reason_description,
    merge_change_reason_description,
)
from ted_and_doffin_to_ocds.converters.bt_763_lotsallrequired import (
    parse_lots_all_required,
    merge_lots_all_required,
)
from ted_and_doffin_to_ocds.converters.bt_764_submissionelectroniccatalogue import (
    parse_submission_electronic_catalogue,
    merge_submission_electronic_catalogue,
)
from ted_and_doffin_to_ocds.converters.bt_765_frameworkagreement import (
    parse_framework_agreement,
    merge_framework_agreement,
)
from ted_and_doffin_to_ocds.converters.bt_765_partframeworkagreement import (
    parse_part_framework_agreement,
    merge_part_framework_agreement,
)
from ted_and_doffin_to_ocds.converters.bt_766_dynamicpurchasingsystem import (
    parse_dynamic_purchasing_system,
    merge_dynamic_purchasing_system,
)
from ted_and_doffin_to_ocds.converters.bt_766_partdynamicpurchasingsystem import (
    parse_part_dynamic_purchasing_system,
    merge_part_dynamic_purchasing_system,
)
from ted_and_doffin_to_ocds.converters.bt_767_lot import (
    parse_electronic_auction,
    merge_electronic_auction,
)
from ted_and_doffin_to_ocds.converters.bt_769_lot import (
    parse_multiple_tenders,
    merge_multiple_tenders,
)
from ted_and_doffin_to_ocds.converters.bt_77_lot import (
    parse_financial_terms,
    merge_financial_terms,
)
from ted_and_doffin_to_ocds.converters.bt_771_lot import (
    parse_late_tenderer_info,
    merge_late_tenderer_info,
)
from ted_and_doffin_to_ocds.converters.bt_772_lot import (
    parse_late_tenderer_info_description,
    merge_late_tenderer_info_description,
)
from ted_and_doffin_to_ocds.converters.bt_773_tender import (
    parse_subcontracting,
    merge_subcontracting,
)
from ted_and_doffin_to_ocds.converters.bt_774_lot import (
    parse_green_procurement,
    merge_green_procurement,
)
from ted_and_doffin_to_ocds.converters.bt_775_lot import (
    parse_social_procurement,
    merge_social_procurement,
)
from ted_and_doffin_to_ocds.converters.bt_776_lot import (
    parse_procurement_innovation,
    merge_procurement_innovation,
)
from ted_and_doffin_to_ocds.converters.bt_777_lot import (
    parse_strategic_procurement_description,
    merge_strategic_procurement_description,
)
from ted_and_doffin_to_ocds.converters.bt_78_lot import (
    parse_security_clearance_deadline,
    merge_security_clearance_deadline,
)
from ted_and_doffin_to_ocds.converters.bt_79_lot import (
    parse_performing_staff_qualification,
    merge_performing_staff_qualification,
)
from ted_and_doffin_to_ocds.converters.bt_801_lot import (
    parse_non_disclosure_agreement,
    merge_non_disclosure_agreement,
)
from ted_and_doffin_to_ocds.converters.bt_802_lot import (
    parse_non_disclosure_agreement_description,
    merge_non_disclosure_agreement_description,
)
from ted_and_doffin_to_ocds.converters.bt_805_lot import (
    parse_green_procurement_criteria,
    merge_green_procurement_criteria,
)
from ted_and_doffin_to_ocds.converters.bt_92_lot import (
    parse_electronic_ordering,
    merge_electronic_ordering,
)
from ted_and_doffin_to_ocds.converters.bt_93_lot import (
    parse_electronic_payment,
    merge_electronic_payment,
)
from ted_and_doffin_to_ocds.converters.bt_94_lot import (
    parse_recurrence,
    merge_recurrence,
)
from ted_and_doffin_to_ocds.converters.bt_95_lot import (
    parse_recurrence_description,
    merge_recurrence_description,
)
from ted_and_doffin_to_ocds.converters.bt_97_lot import (
    parse_submission_language,
    merge_submission_language,
)
from ted_and_doffin_to_ocds.converters.bt_98_lot import (
    parse_tender_validity_deadline,
    merge_tender_validity_deadline,
)
from ted_and_doffin_to_ocds.converters.bt_99_lot import (
    parse_review_deadline_description,
    merge_review_deadline_description,
)
from ted_and_doffin_to_ocds.converters.opp_020_contract import (
    map_extended_duration_indicator,
    merge_extended_duration_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_021_contract import (
    map_essential_assets,
    merge_essential_assets,
)
from ted_and_doffin_to_ocds.converters.opp_022_contract import (
    map_asset_significance,
    merge_asset_significance,
)
from ted_and_doffin_to_ocds.converters.opp_023_contract import (
    map_asset_predominance,
    merge_asset_predominance,
)
from ted_and_doffin_to_ocds.converters.opp_031_tender import (
    parse_contract_conditions,
    merge_contract_conditions,
)
from ted_and_doffin_to_ocds.converters.opp_032_tender import (
    parse_revenues_allocation,
    merge_revenues_allocation,
)
from ted_and_doffin_to_ocds.converters.opp_034_tender import (
    parse_penalties_and_rewards,
    merge_penalties_and_rewards,
)
from ted_and_doffin_to_ocds.converters.opp_040_procedure import (
    parse_main_nature_sub_type,
    merge_main_nature_sub_type,
)
from ted_and_doffin_to_ocds.converters.opp_050_organization import (
    parse_buyers_group_lead_indicator,
    merge_buyers_group_lead_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_051_organization import (
    parse_awarding_cpb_buyer_indicator,
    merge_awarding_cpb_buyer_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_052_organization import (
    parse_acquiring_cpb_buyer_indicator,
    merge_acquiring_cpb_buyer_indicator,
)
from ted_and_doffin_to_ocds.converters.opp_080_tender import (
    parse_kilometers_public_transport,
    merge_kilometers_public_transport,
)
from ted_and_doffin_to_ocds.converters.opp_090_procedure import (
    parse_previous_notice_identifier,
    merge_previous_notice_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_030_procedure_sprovider import (
    parse_provided_service_type,
    merge_provided_service_type,
)
from ted_and_doffin_to_ocds.converters.opp_071_lot import (
    parse_quality_target_code,
    merge_quality_target_code,
)
from ted_and_doffin_to_ocds.converters.opp_072_lot import (
    parse_quality_target_description,
    merge_quality_target_description,
)
from ted_and_doffin_to_ocds.converters.opp_100_contract import (
    parse_framework_notice_identifier,
    merge_framework_notice_identifier,
)
from ted_and_doffin_to_ocds.converters.opp_110_111_fiscallegis import (
    parse_fiscal_legislation,
    merge_fiscal_legislation,
)
from ted_and_doffin_to_ocds.converters.opp_112_120_environlegis import (
    parse_environmental_legislation,
    merge_environmental_legislation,
)
from ted_and_doffin_to_ocds.converters.opp_113_130_employlegis import (
    parse_employment_legislation,
    merge_employment_legislation,
)
from ted_and_doffin_to_ocds.converters.opp_140_procurementdocs import (
    parse_procurement_documents,
    merge_procurement_documents,
)
from ted_and_doffin_to_ocds.converters.opt_155_lotresult import (
    parse_vehicle_type,
    merge_vehicle_type,
)
from ted_and_doffin_to_ocds.converters.opt_156_lotresult import (
    parse_vehicle_numeric,
    merge_vehicle_numeric,
)
from ted_and_doffin_to_ocds.converters.opt_160_ubo import (
    parse_ubo_first_name,
    merge_ubo_first_name,
)
from ted_and_doffin_to_ocds.converters.opt_170_tenderer import (
    parse_tendering_party_leader,
    merge_tendering_party_leader,
)
from ted_and_doffin_to_ocds.converters.opt_200_organization_company import (
    parse_organization_technical_identifier,
    merge_organization_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_201_organization_touchpoint import (
    parse_touchpoint_technical_identifier,
    merge_touchpoint_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_202_ubo import (
    parse_ubo_identifier,
    merge_ubo_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_300_contract_signatory import (
    parse_contract_signatory,
    merge_contract_signatory,
)
from ted_and_doffin_to_ocds.converters.opt_300_procedure_sprovider import (
    parse_procedure_sprovider,
    merge_procedure_sprovider,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_addinfo import (
    parse_additional_info_provider_identifier,
    merge_additional_info_provider_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_docprovider import (
    parse_document_provider_identifier,
    merge_document_provider_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_employlegis import (
    parse_employment_legislation_document_reference,
    merge_employment_legislation_document_reference,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_environlegis import (
    parse_environmental_legislation_document_reference,
    merge_environmental_legislation_document_reference,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_revieworg import (
    parse_review_org_identifier,
    merge_review_org_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_mediator import (
    parse_mediator_identifier,
    merge_mediator_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_reviewinfo import (
    parse_review_info_identifier,
    merge_review_info_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_tendereval import (
    parse_tender_evaluator_identifier,
    merge_tender_evaluator_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lot_tenderreceipt import (
    parse_tender_recipient_identifier,
    merge_tender_recipient_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_301_lotresult_financing import (
    parse_lotresult_financing,
    merge_lotresult_financing,
)
from ted_and_doffin_to_ocds.converters.opt_301_lotresult_paying import (
    parse_lotresult_paying,
    merge_lotresult_paying,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_addinfo import (
    parse_part_addinfo,
    merge_part_addinfo,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_docprovider import (
    parse_part_docprovider,
    merge_part_docprovider,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_employlegis import (
    parse_part_employlegis,
    merge_part_employlegis,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_environlegis import (
    parse_part_environlegis,
    merge_part_environlegis,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_fiscallegis import (
    parse_part_fiscallegis,
    merge_part_fiscallegis,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_mediator import (
    parse_part_mediator,
    merge_part_mediator,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_reviewinfo import (
    parse_part_reviewinfo,
    merge_part_reviewinfo,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_revieworg import (
    parse_part_revieworg,
    merge_part_revieworg,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_tendereval import (
    parse_part_tendereval,
    merge_part_tendereval,
)
from ted_and_doffin_to_ocds.converters.opt_301_part_tenderreceipt import (
    parse_part_tenderreceipt,
    merge_part_tenderreceipt,
)
from ted_and_doffin_to_ocds.converters.opt_301_tenderer_maincont import (
    parse_tenderer_maincont,
    merge_tenderer_maincont,
)

# add more OPT 301 her

from ted_and_doffin_to_ocds.converters.opt_302_organization import (
    parse_beneficial_owner_reference,
    merge_beneficial_owner_reference,
)
from ted_and_doffin_to_ocds.converters.opt_310_tender import (
    parse_tendering_party_id_reference,
    merge_tendering_party_id_reference,
)
from ted_and_doffin_to_ocds.converters.opt_315_lotresult import (
    parse_contract_identifier_reference,
    merge_contract_identifier_reference,
)
from ted_and_doffin_to_ocds.converters.opt_316_contract import (
    parse_contract_technical_identifier,
    merge_contract_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.opt_320_lotresult import (
    parse_tender_identifier_reference,
    merge_tender_identifier_reference,
)


def configure_logging():
    """Configures logging to write to both console and a log file."""
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler and set level to debug
    # console_handler = logging.StreamHandler()
    # console_handler.setLevel(logging.DEBUG)
    # console_handler.setFormatter(formatter)

    # Create file handler and set level to info
    file_handler = logging.FileHandler("app.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    # logger.addHandler(console_handler)
    logger.addHandler(file_handler)


def remove_empty_elements(data):
    """
    Recursively remove empty lists, empty dicts, or None elements from a dictionary or list.
    Preserves False boolean values and zero numeric values.
    """
    if isinstance(data, dict):
        return {
            key: remove_empty_elements(value)
            for key, value in data.items()
            if value is not None and (value or isinstance(value, bool | int | float))
        }
    if isinstance(data, list):
        return [
            remove_empty_elements(item)
            for item in data
            if item is not None and (item or isinstance(item, bool | int | float))
        ]
    return data


# Additional step to remove keys with empty dictionaries
def remove_empty_dicts(data):
    if isinstance(data, dict):
        return {
            key: remove_empty_dicts(value)
            for key, value in data.items()
            if value or isinstance(value, bool | int | float)
        }
    if isinstance(data, list):
        return [
            remove_empty_dicts(item)
            for item in data
            if item or isinstance(item, bool | int | float)
        ]
    return data


def process_bt_section2(
    release_json,
    xml_content,
    parse_funcs,
    merge_func,
    section_name,
):
    """
    Processes a specific business term section by calling the provided parsing and merging functions.

    Args:
        release_json (dict): The OCDS release JSON to be updated.
        xml_content (bytes): The XML content to parse.
        parse_funcs (list): A list of parsing functions for the section.
        merge_func (function): The merging function for the section.
        section_name (str): The name of the section being processed.

    Returns:
        None: The function updates the release_json in-place.
    """
    logger = logging.getLogger(__name__)

    logger.info("Processing %s", section_name)
    try:
        for parse_func in parse_funcs:
            data = parse_func(xml_content)
            if data:
                merge_func(release_json, data)
            else:
                logger.info("No data found for %s", parse_func.__name__)
    except Exception:
        logger.exception("Error processing %s", section_name)


def process_bt_section(
    release_json,
    xml_content,
    parse_functions,
    merge_function,
    section_name,
):
    logger = logging.getLogger(__name__)
    try:
        logger.info("Starting %s processing", section_name)
        for parse_function in parse_functions:
            parsed_data = parse_function(xml_content)
            logger.info("Parsed data for %s: %s", section_name, parsed_data)
            if parsed_data:
                # logger.info("Calling merge function for %s", section_name)
                merge_function(release_json, parsed_data)
                logger.info("Successfully merged data for %s", section_name)
                return
        logger.warning("No data found for %s", section_name)
    except Exception:
        logger.exception("Error processing %s data", section_name)
        logger.exception("Exception details")
    # finally:
    #    logger.info("Release JSON after %s processing: %s", section_name, release_json)


def main(xml_path, ocid_prefix):
    """
    Main function to orchestrate the XML to OCDS JSON conversion process.

    Args:
        xml_path (str): Path to the input XML file.
        ocid_prefix (str): Prefix for the OCID.

    Returns:
        dict: The final OCDS release JSON.
    """
    # Read the XML content from the file
    with Path(xml_path).open("rb") as xml_file:
        xml_content = xml_file.read()

    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting XML to JSON conversion for file: %s", xml_path)

    # Initialize NoticeProcessor
    notice_processor = NoticeProcessor(ocid_prefix)

    # Create the initial OCDS release JSON structure
    release_json_str = notice_processor.create_release(xml_content)
    release_json = json.loads(release_json_str)

    # Parse and merge BT-01 procedure Legal Basis
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_legal_basis],
        merge_procedure_legal_basis,
        "procedure Legal Basis (BT-01)",
    )

    # Parse and merge BT-03 Form Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_form_type],
        merge_form_type,
        "Form Type (BT-03)",
    )

    # Parse and merge BT-04 procedure Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_identifier],
        merge_procedure_identifier,
        "procedure Identifier (BT-04)",
    )

    # Parse and merge BT-05-notice notice Dispatch Date and Time
    process_bt_section(
        release_json,
        xml_content,
        [parse_notice_dispatch_date_time],
        merge_notice_dispatch_date_time,
        "notice Dispatch Date and Time (BT-05)",
    )

    # Parse and merge BT-06-Lot Strategic Procurement
    process_bt_section(
        release_json,
        xml_content,
        [parse_strategic_procurement],
        merge_strategic_procurement,
        "Strategic Procurement (BT-06)",
    )

    # Parse and merge BT-09-procedure Cross Border Law
    process_bt_section(
        release_json,
        xml_content,
        [parse_cross_border_law],
        merge_cross_border_law,
        "Cross Border Law (BT-09)",
    )

    # Parse and merge BT-10-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_xml],
        merge_contract_info,
        "organization Main Activity (BT-10)",
    )

    # Parse and merge BT-105-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_type],
        merge_procedure_type,
        "procedure Type (BT-105)",
    )

    # Parse and merge BT-106-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_accelerated],
        merge_procedure_accelerated,
        "procedure Accelerated (BT-106)",
    )

    # Parse and merge BT-109-Lot Framework Duration Justification
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_duration_justification],
        merge_framework_duration_justification,
        "Framework Duration Justification (BT-109)",
    )

    # Parse and merge BT-11-procedure-buyer buyer Legal Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_legal_type],
        merge_buyer_legal_type,
        "buyer Legal Type (BT-11)",
    )

    # Parse and merge BT-111-Lot Framework buyer Categories
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_buyer_categories],
        merge_framework_buyer_categories,
        "Framework buyer Categories (BT-111)",
    )

    # Parse and merge BT-113-Lot Framework Maximum participants Number
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_max_participants],
        merge_framework_max_participants,
        "Framework Maximum participants Number (BT-113)",
    )

    # Parse and merge BT-115 GPA Coverage
    process_bt_section(
        release_json,
        xml_content,
        [parse_gpa_coverage],
        merge_gpa_coverage,
        "GPA Coverage (BT-115)",
    )

    # Parse and merge BT-119-LotResult DPS Termination
    process_bt_section(
        release_json,
        xml_content,
        [parse_dps_termination],
        merge_dps_termination,
        "DPS Termination (BT-119)",
    )

    # Parse and merge BT-120-Lot No Negotiation Necessary
    process_bt_section(
        release_json,
        xml_content,
        [parse_no_negotiation_necessary],
        merge_no_negotiation_necessary,
        "No Negotiation Necessary (BT-120)",
    )

    # Parse and merge BT-122-Lot Electronic Auction Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_electronic_auction_description],
        merge_electronic_auction_description,
        "Electronic Auction Description (BT-122)",
    )

    # Parse and merge BT-123-Lot Electronic Auction URL
    process_bt_section(
        release_json,
        xml_content,
        [parse_electronic_auction_url],
        merge_electronic_auction_url,
        "Electronic Auction URL (BT-123)",
    )

    # Parse and merge BT-124 Tool Atypical URL
    process_bt_section(
        release_json,
        xml_content,
        [parse_tool_atypical_url],
        merge_tool_atypical_url,
        "Tool Atypical URL (BT-124)",
    )

    # Parse and merge BT-125(i)-Lot Previous Planning Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_previous_planning_identifier_lot],
        merge_previous_planning_identifier_lot,
        "Previous Planning Identifier (Lot) (BT-125(i))",
    )

    # Parse and merge BT-125(i)-part and BT-1251-part Previous Planning Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_previous_planning_identifier_part],
        merge_previous_planning_identifier_part,
        "Previous Planning Identifier (part) (BT-125(i) and BT-1251)",
    )

    # Parse and merge BT-1252-procedure Direct Award Justification
    process_bt_section(
        release_json,
        xml_content,
        [parse_direct_award_justification],
        merge_direct_award_justification,
        "Direct Award Justification (BT-1252)",
    )

    # Parse and merge BT-127 Future notice Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_future_notice_date],
        merge_future_notice_date,
        "Future notice Date (BT-127)",
    )

    # Parse and merge BT-13 Additional Information Deadline
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_info_deadline],
        merge_additional_info_deadline,
        "Additional Information Deadline (BT-13)",
    )

    # Parse and merge BT-13 Additional Information Deadline (part)
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_info_deadline_part],
        merge_additional_info_deadline_part,
        "Additional Information Deadline (part) (BT-13)",
    )

    # Parse and merge BT-130-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_dispatch_invitation_tender],
        merge_dispatch_invitation_tender,
        "Dispatch Invitation Tender (BT-130)",
    )

    # Parse and merge BT-131-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_deadline_receipt_tenders],
        merge_deadline_receipt_tenders,
        "Deadline Receipt Tenders (BT-131)",
    )

    # Parse and merge BT-1311-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_deadline_receipt_requests],
        merge_deadline_receipt_requests,
        "Deadline Receipt Requests (BT-1311)",
    )

    # Parse and merge BT-132-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_public_opening_date],
        merge_lot_public_opening_date,
        "Lot Public Opening Date (BT-132)",
    )

    # Parse and merge BT-133-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_bid_opening_location],
        merge_lot_bid_opening_location,
        "Lot Bid Opening Location (BT-133)",
    )

    # Parse and merge BT-134-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_public_opening_description],
        merge_lot_public_opening_description,
        "Lot Public Opening Description (BT-134)",
    )

    # Parse and merge BT-135-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_direct_award_justification_rationale],
        merge_direct_award_justification_rationale,
        "Direct Award Justification Rationale (BT-135)",
    )

    # Parse and merge BT-1351-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_accelerated_procedure_justification],
        merge_accelerated_procedure_justification,
        "Accelerated procedure Justification (BT-1351)",
    )

    # Parse and merge BT-136-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_direct_award_justification_code],
        merge_direct_award_justification_code,
        "Direct Award Justification Code (BT-136)",
    )

    # Parse and merge BT-137-Lot Purpose Lot Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_purpose_lot_identifier],
        merge_purpose_lot_identifier,
        "Purpose Lot Identifier (BT-137-Lot)",
    )

    # Parse and merge BT-137-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_lots_group_identifier],
        merge_lots_group_identifier,
        "Lots Group Identifier (BT-137-LotsGroup)",
    )

    # Parse and merge BT-137-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_identifier],
        merge_part_identifier,
        "part Identifier (BT-137-part)",
    )

    # Parse and merge BT-13713-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_result_identifier],
        merge_lot_result_identifier,
        "Lot Result Identifier (BT-13713)",
    )

    # Parse and merge BT-13714-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_lot_identifier],
        merge_tender_lot_identifier,
        "Tender Lot Identifier (BT-13714)",
    )

    # Parse and merge BT-1375-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_group_lot_identifier],
        merge_group_lot_identifier,
        "Group Lot Identifier (BT-1375)",
    )

    # Parse and merge BT-14-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_documents_restricted],
        merge_lot_documents_restricted,
        "Lot Documents Restricted (BT-14-Lot)",
    )

    # Parse and merge BT-14-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_documents_restricted],
        merge_part_documents_restricted,
        "part Documents Restricted (BT-14-part)",
    )

    # Parse and merge BT-140-notice
    process_bt_section(
        release_json,
        xml_content,
        [parse_change_reason_code],
        merge_change_reason_code,
        "Change Reason Code (BT-140)",
    )

    # Parse and merge BT-142-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_winner_chosen],
        merge_winner_chosen,
        "Winner Chosen (BT-142)",
    )

    # Parse and merge BT-144-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_not_awarded_reason],
        merge_not_awarded_reason,
        "Not Awarded Reason (BT-144)",
    )

    # Parse and merge BT-145-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_conclusion_date],
        merge_contract_conclusion_date,
        "Contract Conclusion Date (BT-145)",
    )

    # Parse and merge BT-1451-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_winner_decision_date],
        merge_winner_decision_date,
        "Winner Decision Date (BT-1451)",
    )

    # Parse and merge BT-15-Lot-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_url],
        merge_documents_url,
        "Documents URL (BT-15)",
    )

    # Parse and merge BT-150-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_identifier],
        merge_contract_identifier,
        "Contract Identifier (BT-150)",
    )

    # Parse and merge BT-151-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_url],
        merge_contract_url,
        "Contract URL (BT-151)",
    )

    # Parse the organization info BT-500
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_name],
        merge_organization_name,
        "organization Name (BT-500)",
    )

    # Parse and merge BT-16-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_part_name],
        merge_organization_part_name,
        "organization part Name (BT-16-organization-company)",
    )

    # Parse and merge BT-16-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_touchpoint_part_name],
        merge_organization_touchpoint_part_name,
        "organization touchpoint part Name (BT-16-organization-touchpoint)",
    )

    # Parse the organization info BT_500_organization_touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_name],
        merge_touchpoint_name,
        "touchpoint Name (BT-500-organization-touchpoint)",
    )

    # Parse and merge BT-160-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_concession_revenue_buyer],
        merge_concession_revenue_buyer,
        "Concession Revenue buyer (BT-160)",
    )

    # Parse and merge BT-162-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_concession_revenue_user],
        merge_concession_revenue_user,
        "Concession Revenue User (BT-162)",
    )

    # Parse and merge BT-163-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_concession_value_description],
        merge_concession_value_description,
        "Concession Value Description (BT-163)",
    )

    # Parse and merge BT-165-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_winner_size],
        merge_winner_size,
        "Winner Size (BT-165)",
    )

    # Parse and merge BT-17-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_submission_electronic],
        merge_submission_electronic,
        "Submission Electronic (BT-17)",
    )

    # Parse and merge BT-171-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_rank],
        merge_tender_rank,
        "Tender Rank (BT-171)",
    )

    # Parse and merge BT-1711-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_ranked],
        merge_tender_ranked,
        "Tender Ranked (BT-1711)",
    )

    # Parse the Submission URL (BT-18)
    process_bt_section(
        release_json,
        xml_content,
        [parse_submission_url],
        merge_submission_url,
        "Submission URL (BT-18)",
    )

    # Parse and merge BT-19-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_submission_nonelectronic_justification],
        merge_submission_nonelectronic_justification,
        "Submission Nonelectronic Justification (BT-19)",
    )

    # Parse and merge BT-191-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_country_origin],
        merge_country_origin,
        "Country Origin (BT-191)",
    )

    # Parse the Tender Variant (BT-193)
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_variant],
        merge_tender_variant,
        "Tender Variant (BT-193)",
    )

    # Parse and merge BT-195(BT-09) Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [bt_195_parse_unpublished_identifier_bt_09_procedure],
        bt_195_merge_unpublished_identifier_bt_09_procedure,
        "Unpublished Identifier (BT-195, BT-09)",
    )

    # Parse and merge BT-195(BT-105)-procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt105_unpublished_identifier],
        merge_bt195_bt105_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-105)",
    )

    # Parse and merge BT-195(BT-106)-procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt106_unpublished_identifier],
        merge_bt195_bt106_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-106)",
    )

    # Parse and merge BT-195(BT-1252)-procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt1252_unpublished_identifier],
        merge_bt195_bt1252_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-1252)",
    )

    # Parse and merge BT-195(BT-135)-procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt135_unpublished_identifier],
        merge_bt195_bt135_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-135)",
    )

    # Parse and merge BT-195(BT-1351)-procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt1351_unpublished_identifier],
        merge_bt195_bt1351_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-1351)",
    )

    # Parse and merge BT-195(BT-136)-procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt136_unpublished_identifier],
        merge_bt195_bt136_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-136)",
    )

    # Parse and merge BT-195(BT-142)-LotResult Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt142_unpublished_identifier],
        merge_bt195_bt142_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-142)",
    )

    # Parse and merge BT-195(BT-144)-LotResult Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt144_unpublished_identifier],
        merge_bt195_bt144_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-144)",
    )

    # Parse and merge BT-195(BT-160)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt160_unpublished_identifier],
        merge_bt195_bt160_unpublished_identifier,
        "procedure BT-195(BT-160)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-162)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt162_unpublished_identifier],
        merge_bt195_bt162_unpublished_identifier,
        "procedure BT-195(BT-162)-Tender Unpublished Identifier",
    )
    # Parse and merge BT-195(BT-163)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt163_unpublished_identifier],
        merge_bt195_bt163_unpublished_identifier,
        "procedure BT-195(BT-163)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-171)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt171_unpublished_identifier],
        merge_bt195_bt171_unpublished_identifier,
        "procedure BT-195(BT-171)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-191)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt191_unpublished_identifier],
        merge_bt195_bt191_unpublished_identifier,
        "procedure BT-195(BT-191)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-193)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt193_unpublished_identifier],
        merge_bt195_bt193_unpublished_identifier,
        "procedure BT-195(BT-193)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-539)-Lot Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt539_unpublished_identifier],
        merge_bt195_bt539_unpublished_identifier,
        "procedure BT-195(BT-539)-Lot Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-539)-LotsGroup Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt539_lotsgroup_unpublished_identifier],
        merge_bt195_bt539_lotsgroup_unpublished_identifier,
        "procedure BT-195(BT-539)-LotsGroup Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-540)-Lot Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt540_lot_unpublished_identifier],
        merge_bt195_bt540_lot_unpublished_identifier,
        "procedure BT-195(BT-540)-Lot Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-540)-LotsGroup Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt540_lotsgroup_unpublished_identifier],
        merge_bt195_bt540_lotsgroup_unpublished_identifier,
        "procedure BT-195(BT-540)-LotsGroup Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-541)-Lot-Fixed Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt541_lot_fixed_unpublished_identifier],
        merge_bt195_bt541_lot_fixed_unpublished_identifier,
        "procedure BT-195(BT-541)-Lot-Fixed Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-541) Lot Threshold Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt541_lot_threshold_unpublished_identifier],
        merge_bt195_bt541_lot_threshold_unpublished_identifier,
        "Lot Threshold Unpublished Identifier (BT-195(BT-541))",
    )

    # Parse and merge BT-195(BT-541) Lot Weight Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt541_lot_weight_unpublished_identifier],
        merge_bt195_bt541_lot_weight_unpublished_identifier,
        "Lot Weight Unpublished Identifier (BT-195(BT-541))",
    )

    # Parse and merge BT-195(BT-541) LotsGroup Fixed Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier],
        merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
        "LotsGroup Fixed Unpublished Identifier (BT-195(BT-541))",
    )

    # Parse and merge BT-195(BT-541) LotsGroup Threshold Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt541_lotsgroup_threshold_unpublished_identifier],
        merge_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
        "LotsGroup Threshold Unpublished Identifier (BT-195(BT-541))",
    )
    # Parse and merge BT-195(BT-541)-LotsGroup-Weight
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt541_lotsgroup_weight],
        merge_bt195_bt541_lotsgroup_weight,
        "Unpublished Identifier for LotsGroup Weight (BT-195(BT-541))",
    )
    # Parse and merge BT-195(BT-5421)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt5421_lot],
        merge_bt195_bt5421_lot,
        "Unpublished Identifier for Lot (BT-195(BT-5421))",
    )
    # Parse and merge BT-195(BT-5421)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt5421_lotsgroup],
        merge_bt195_bt5421_lotsgroup,
        "Unpublished Identifier for LotsGroup (BT-195(BT-5421))",
    )
    # Parse and merge BT-195(BT-5422)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt5422_lot],
        merge_bt195_bt5422_lot,
        "Unpublished Identifier for Lot (BT-195(BT-5422))",
    )
    # Parse and merge BT-195(BT-5422)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt5422_lotsgroup],
        merge_bt195_bt5422_lotsgroup,
        "Unpublished Identifier for LotsGroup (BT-195(BT-5422))",
    )
    # Parse and merge BT-195(BT-5423)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt5423_lot],
        merge_bt195_bt5423_lot,
        "Unpublished Identifier for Lot (BT-195(BT-5423))",
    )
    # Parse and merge BT-195(BT-5423)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt5423_lotsgroup],
        merge_bt195_bt5423_lotsgroup,
        "Unpublished Identifier for LotsGroup (BT-195(BT-5423))",
    )
    # Parse and merge BT-195(BT-543)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt543_lot],
        merge_bt195_bt543_lot,
        "Unpublished Identifier for Lot (BT-195(BT-543))",
    )
    # Parse and merge BT-195(BT-543)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt543_lotsgroup],
        merge_bt195_bt543_lotsgroup,
        "Unpublished Identifier for LotsGroup (BT-195(BT-543))",
    )
    # Parse and merge BT-195(BT-553)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt553_tender],
        merge_bt195_bt553_tender,
        "Unpublished Identifier for Tender (BT-195(BT-553))",
    )
    # Parse and merge BT-195(BT-554)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt554_unpublished_identifier],
        merge_bt195_bt554_unpublished_identifier,
        "Unpublished Identifier for Tender Subcontracting Description (BT-195(BT-554))",
    )
    # Parse and merge BT-195(BT-555)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt555_unpublished_identifier],
        merge_bt195_bt555_unpublished_identifier,
        "Unpublished Identifier for Tender Subcontracting Percentage (BT-195(BT-555))",
    )
    # Parse and merge BT-195(BT-635)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt635_unpublished_identifier],
        merge_bt195_bt635_unpublished_identifier,
        "Unpublished Identifier for Lot Result buyer Review Request Count (BT-195(BT-635))",
    )
    # Parse and merge BT-195(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt636_unpublished_identifier],
        merge_bt195_bt636_unpublished_identifier,
        "Unpublished Identifier for Lot Result buyer Review Request Irregularity Type (BT-195(BT-636))",
    )
    # Parse and merge BT-195(BT-660)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt660_unpublished_identifier],
        merge_bt195_bt660_unpublished_identifier,
        "Unpublished Identifier for Lot Result Framework Re-estimated Value (BT-195(BT-660))",
    )
    # Parse and merge BT-195(BT-709)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt709_unpublished_identifier],
        merge_bt195_bt709_unpublished_identifier,
        "Unpublished Identifier for Lot Result Maximum Value (BT-195(BT-709))",
    )

    # Parse and merge BT-195(BT-710)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt710_unpublished_identifier],
        merge_bt195_bt710_unpublished_identifier,
        "Unpublished Identifier for Lot Result Tender Lowest Value (BT-195(BT-710))",
    )
    # Parse and merge BT-195(BT-711)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt711_unpublished_identifier],
        merge_bt195_bt711_unpublished_identifier,
        "Unpublished Identifier for Lot Result Tender Highest Value (BT-195(BT-711))",
    )
    # Parse and merge BT-195(BT-712)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt712_unpublished_identifier],
        merge_bt195_bt712_unpublished_identifier,
        "Unpublished Identifier for Lot Result buyer Review Complainants (BT-195(BT-712))",
    )
    # Parse and merge BT-195(BT-720)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt720_unpublished_identifier],
        merge_bt195_bt720_unpublished_identifier,
        "Unpublished Identifier for Winning Tender Value (BT-195(BT-720))",
    )
    # Parse and merge BT-195(BT-733)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt733_unpublished_identifier],
        merge_bt195_bt733_unpublished_identifier,
        "Unpublished Identifier for Award Criteria Order Justification (BT-195(BT-733))",
    )
    # Parse and merge BT-195(BT-733)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt733_lotsgroup_unpublished_identifier],
        merge_bt195_bt733_lotsgroup_unpublished_identifier,
        "Unpublished Identifier for Award Criteria Order Justification in LotsGroup (BT-195(BT-733))",
    )
    # Parse and merge BT-195(BT-734)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt734_lot_unpublished_identifier],
        merge_bt195_bt734_lot_unpublished_identifier,
        "Unpublished Identifier for Award Criterion Name in Lot (BT-195(BT-734))",
    )
    # Parse and merge BT-195(BT-734)-LotGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt734_lotsgroup_unpublished_identifier],
        merge_bt195_bt734_lotsgroup_unpublished_identifier,
        "Unpublished Identifier for Award Criterion Name in LotGroup (BT-195(BT-734))",
    )
    # Parse and merge BT-195(BT-759)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt759_lotresult_unpublished_identifier],
        merge_bt195_bt759_lotresult_unpublished_identifier,
        "Unpublished Identifier for Received Submissions Count in Lot Result (BT-195(BT-759))",
    )
    # Parse and merge BT-195(BT-760)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt760_lotresult_unpublished_identifier],
        merge_bt195_bt760_lotresult_unpublished_identifier,
        "Unpublished Identifier for Received Submissions Type in Lot Result (BT-195(BT-760))",
    )
    # Parse and merge BT-195(BT-773)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt773_tender_unpublished_identifier],
        merge_bt195_bt773_tender_unpublished_identifier,
        "Unpublished Identifier for Subcontracting in Tender (BT-195(BT-773))",
    )
    # Parse and merge BT-195(BT-88)-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt88_procedure_unpublished_identifier],
        merge_bt195_bt88_procedure_unpublished_identifier,
        "Unpublished Identifier for procedure Features (BT-195(BT-88))",
    )

    # BT-196
    # Parse and merge BT-196(BT-09) Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [bt_196_parse_unpublished_justification_bt_09_procedure],
        bt_196_merge_unpublished_justification_bt_09_procedure,
        "Unpublished Justification Description (BT-196, BT-09)",
    )

    # Parse and merge BT-196(BT-105)-procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt105_unpublished_justification],
        merge_bt196_bt105_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-105)",
    )

    # Parse and merge BT-196(BT-106)-procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt106_unpublished_justification],
        merge_bt196_bt106_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-106)",
    )

    # Parse and merge BT-196(BT-1252)-procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt1252_unpublished_justification],
        merge_bt196_bt1252_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-1252)",
    )

    # Parse and merge BT-196(BT-135)-procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt135_unpublished_justification],
        merge_bt196_bt135_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-135)",
    )

    # Parse and merge BT-196(BT-1351)-procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt1351_unpublished_justification],
        merge_bt196_bt1351_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-1351)",
    )

    # Parse and merge BT-196(BT-136)-procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt136_unpublished_justification],
        merge_bt196_bt136_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-136)",
    )

    # Parse and merge BT-196(BT-142)-LotResult Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt142_unpublished_justification],
        merge_bt196_bt142_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-142)",
    )

    # Parse and merge BT-196(BT-144)-LotResult Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt144_unpublished_justification],
        merge_bt196_bt144_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-144)",
    )

    # Parse and merge BT-196(BT-160)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt160_unpublished_justification],
        merge_bt196_bt160_unpublished_justification,
        "procedure BT-196(BT-160)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-162)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt162_unpublished_justification],
        merge_bt196_bt162_unpublished_justification,
        "procedure BT-196(BT-162)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-163)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt163_unpublished_justification],
        merge_bt196_bt163_unpublished_justification,
        "procedure BT-196(BT-163)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-171)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt171_unpublished_justification],
        merge_bt196_bt171_unpublished_justification,
        "procedure BT-196(BT-171)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-191)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt191_unpublished_justification],
        merge_bt196_bt191_unpublished_justification,
        "procedure BT-196(BT-191)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-193)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt193_unpublished_justification],
        merge_bt196_bt193_unpublished_justification,
        "procedure BT-196(BT-193)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-539)-Lot Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt539_unpublished_justification],
        merge_bt196_bt539_unpublished_justification,
        "procedure BT-196(BT-539)-Lot Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-539)-LotsGroup Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt539_lotsgroup_unpublished_justification],
        merge_bt196_bt539_lotsgroup_unpublished_justification,
        "procedure BT-196(BT-539)-LotsGroup Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-540)-Lot Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt540_lot_unpublished_justification],
        merge_bt196_bt540_lot_unpublished_justification,
        "procedure BT-196(BT-540)-Lot Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-540)-LotsGroup Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt540_lotsgroup_unpublished_justification],
        merge_bt196_bt540_lotsgroup_unpublished_justification,
        "procedure BT-196(BT-540)-LotsGroup Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-541)-Lot-Fixed Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt541_lot_fixed_unpublished_justification],
        merge_bt196_bt541_lot_fixed_unpublished_justification,
        "procedure BT-196(BT-541)-Lot-Fixed Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-541) Lot Threshold Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt541_lot_threshold_unpublished_justification],
        merge_bt196_bt541_lot_threshold_unpublished_justification,
        "Lot Threshold Unpublished Justification Description (BT-196(BT-541))",
    )

    # Parse and merge BT-196(BT-541) Lot Weight Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt541_lot_weight_unpublished_justification],
        merge_bt196_bt541_lot_weight_unpublished_justification,
        "Lot Weight Unpublished Justification Description (BT-196(BT-541))",
    )

    # Parse and merge BT-196(BT-541) LotsGroup Fixed Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt541_lotsgroup_fixed_unpublished_justification],
        merge_bt196_bt541_lotsgroup_fixed_unpublished_justification,
        "LotsGroup Fixed Unpublished Justification Description (BT-196(BT-541))",
    )

    # Parse and merge BT-196(BT-541) LotsGroup Threshold Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt541_lotsgroup_threshold_unpublished_justification],
        merge_bt196_bt541_lotsgroup_threshold_unpublished_justification,
        "LotsGroup Threshold Unpublished Justification Description (BT-196(BT-541))",
    )
    # Parse and merge BT-196(BT-541)-LotsGroup-Weight
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt541_lotsgroup_weight],
        merge_bt196_bt541_lotsgroup_weight,
        "Unpublished Justification Description for LotsGroup Weight (BT-196(BT-541))",
    )
    # Parse and merge BT-196(BT-5421)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt5421_lot],
        merge_bt196_bt5421_lot,
        "Unpublished Justification Description for Lot (BT-196(BT-5421))",
    )
    # Parse and merge BT-196(BT-5421)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt5421_lotsgroup],
        merge_bt196_bt5421_lotsgroup,
        "Unpublished Justification Description for LotsGroup (BT-196(BT-5421))",
    )
    # Parse and merge BT-196(BT-5422)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt5422_lot],
        merge_bt196_bt5422_lot,
        "Unpublished Justification Description for Lot (BT-196(BT-5422))",
    )
    # Parse and merge BT-196(BT-5422)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt5422_lotsgroup],
        merge_bt196_bt5422_lotsgroup,
        "Unpublished Justification Description for LotsGroup (BT-196(BT-5422))",
    )
    # Parse and merge BT-196(BT-5423)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt5423_lot],
        merge_bt196_bt5423_lot,
        "Unpublished Justification Description for Lot (BT-196(BT-5423))",
    )

    # Parse and merge BT-196(BT-5423)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt5423_lotsgroup],
        merge_bt196_bt5423_lotsgroup,
        "Unpublished Justification Description for LotsGroup (BT-196(BT-5423))",
    )
    # Parse and merge BT-196(BT-543)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt543_lot],
        merge_bt196_bt543_lot,
        "Unpublished Justification Description for Lot (BT-196(BT-543))",
    )
    # Parse and merge BT-196(BT-543)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt543_lotsgroup],
        merge_bt196_bt543_lotsgroup,
        "Unpublished Justification Description for LotsGroup (BT-196(BT-543))",
    )
    # Parse and merge BT-196(BT-553)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt553_tender],
        merge_bt196_bt553_tender,
        "Unpublished Justification Description for Tender (BT-196(BT-553))",
    )
    # Parse and merge BT-196(BT-554)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt554_unpublished_justification],
        merge_bt196_bt554_unpublished_justification,
        "Unpublished Justification Description for Tender Subcontracting Description (BT-196(BT-554))",
    )
    # Parse and merge BT-196(BT-555)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt555_unpublished_justification],
        merge_bt196_bt555_unpublished_justification,
        "Unpublished Justification Description for Tender Subcontracting Percentage (BT-196(BT-555))",
    )
    # Parse and merge BT-196(BT-635)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt635_unpublished_justification],
        merge_bt196_bt635_unpublished_justification,
        "Unpublished Justification Description for Lot Result buyer Review Request Count (BT-196(BT-635))",
    )
    # Parse and merge BT-196(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt636_unpublished_justification],
        merge_bt196_bt636_unpublished_justification,
        "Unpublished Justification Description for Lot Result buyer Review Request Irregularity Type (BT-196(BT-636))",
    )
    # Parse and merge BT-196(BT-660)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt660_unpublished_justification],
        merge_bt196_bt660_unpublished_justification,
        "Unpublished Justification Description for Lot Result Framework Re-estimated Value (BT-196(BT-660))",
    )
    # Parse and merge BT-196(BT-709)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt709_unpublished_justification],
        merge_bt196_bt709_unpublished_justification,
        "Unpublished Justification Description for Lot Result Maximum Value (BT-196(BT-709))",
    )
    # Parse and merge BT-196(BT-710)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt710_unpublished_justification],
        merge_bt196_bt710_unpublished_justification,
        "Unpublished Justification for Lot Result Tender Lowest Value (BT-196(BT-710))",
    )
    # Parse and merge BT-196(BT-711)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt711_unpublished_justification],
        merge_bt196_bt711_unpublished_justification,
        "Unpublished Justification for Lot Result Tender Highest Value (BT-196(BT-711))",
    )
    # Parse and merge BT-196(BT-712)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt712_unpublished_justification],
        merge_bt196_bt712_unpublished_justification,
        "Unpublished Justification for Lot Result buyer Review Complainants (BT-196(BT-712))",
    )
    # Parse and merge BT-196(BT-720)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt720_unpublished_justification],
        merge_bt196_bt720_unpublished_justification,
        "Unpublished Justification for Winning Tender Value (BT-196(BT-720))",
    )
    # Parse and merge BT-196(BT-733)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt733_unpublished_justification],
        merge_bt196_bt733_unpublished_justification,
        "Unpublished Justification for Award Criteria Order Justification (BT-196(BT-733))",
    )
    # Parse and merge BT-196(BT-733)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt733_lotsgroup_unpublished_justification],
        merge_bt196_bt733_lotsgroup_unpublished_justification,
        "Unpublished Justification for Award Criteria Order Justification in LotsGroup (BT-196(BT-733))",
    )
    # Parse and merge BT-196(BT-734)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt734_lot_unpublished_justification],
        merge_bt196_bt734_lot_unpublished_justification,
        "Unpublished Justification for Award Criterion Name in Lot (BT-196(BT-734))",
    )
    # Parse and merge BT-196(BT-734)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt734_lotsgroup_unpublished_justification],
        merge_bt196_bt734_lotsgroup_unpublished_justification,
        "Unpublished Justification for Award Criterion Name in Lots Group (BT-196(BT-734))",
    )
    # Parse and merge BT-196(BT-759)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt759_lotresult_unpublished_justification],
        merge_bt196_bt759_lotresult_unpublished_justification,
        "Unpublished Justification for Received Submissions Count in Lot Result (BT-196(BT-759))",
    )
    # Parse and merge BT-196(BT-760)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt760_lotresult_unpublished_justification],
        merge_bt196_bt760_lotresult_unpublished_justification,
        "Unpublished Justification for Received Submissions Type in Lot Result (BT-196(BT-760))",
    )
    # Parse and merge BT-196(BT-773)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt773_tender_unpublished_justification],
        merge_bt196_bt773_tender_unpublished_justification,
        "Unpublished Justification for Subcontracting in Tender (BT-196(BT-773))",
    )
    # Parse and merge BT-196(BT-88)-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt88_procedure_unpublished_justification],
        merge_bt196_bt88_procedure_unpublished_justification,
        "Unpublished Justification for procedure Features (BT-196(BT-88))",
    )

    # BT-197

    # Parse and merge BT-197(BT-09) Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [bt_197_parse_unpublished_justification_code_bt_09_procedure],
        bt_197_merge_unpublished_justification_code_bt_09_procedure,
        "Unpublished Justification Code (BT-197, BT-09)",
    )

    # Parse and merge BT-197(BT-105)-procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt105_unpublished_justification_code],
        merge_bt197_bt105_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-105)",
    )

    # Parse and merge BT-197(BT-106)-procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt106_unpublished_justification_code],
        merge_bt197_bt106_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-106)",
    )

    # Parse and merge BT-197(BT-1252)-procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt1252_unpublished_justification_code],
        merge_bt197_bt1252_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-1252)",
    )

    # Parse and merge BT-197(BT-135)-procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt135_unpublished_justification_code],
        merge_bt197_bt135_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-135)",
    )

    # Parse and merge BT-197(BT-1351)-procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt1351_unpublished_justification_code],
        merge_bt197_bt1351_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-1351)",
    )

    # Parse and merge BT-197(BT-136)-procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt136_unpublished_justification_code],
        merge_bt197_bt136_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-136)",
    )

    # Parse and merge BT-197(BT-142)-LotResult Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt142_unpublished_justification_code],
        merge_bt197_bt142_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-142)",
    )

    # Parse and merge BT-197(BT-144)-LotResult Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt144_unpublished_justification_code],
        merge_bt197_bt144_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-144)",
    )

    # Parse and merge BT-197(BT-160)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt160_unpublished_justification_code],
        merge_bt197_bt160_unpublished_justification_code,
        "procedure BT-197(BT-160)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-162)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt162_unpublished_justification_code],
        merge_bt197_bt162_unpublished_justification_code,
        "procedure BT-197(BT-162)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-163)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt163_unpublished_justification_code],
        merge_bt197_bt163_unpublished_justification_code,
        "procedure BT-197(BT-163)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-171)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt171_unpublished_justification_code],
        merge_bt197_bt171_unpublished_justification_code,
        "procedure BT-197(BT-171)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-191)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt191_unpublished_justification_code],
        merge_bt197_bt191_unpublished_justification_code,
        "procedure BT-197(BT-191)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-193)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt193_unpublished_justification_code],
        merge_bt197_bt193_unpublished_justification_code,
        "procedure BT-197(BT-193)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-539)-Lot Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt539_unpublished_justification_code],
        merge_bt197_bt539_unpublished_justification_code,
        "procedure BT-197(BT-539)-Lot Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-539)-LotsGroup Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt539_lotsgroup_unpublished_justification_code],
        merge_bt197_bt539_lotsgroup_unpublished_justification_code,
        "procedure BT-197(BT-539)-LotsGroup Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-540)-Lot Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt540_lot_unpublished_justification_code],
        merge_bt197_bt540_lot_unpublished_justification_code,
        "procedure BT-197(BT-540)-Lot Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-540)-LotsGroup Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt540_lotsgroup_unpublished_justification_code],
        merge_bt197_bt540_lotsgroup_unpublished_justification_code,
        "procedure BT-197(BT-540)-LotsGroup Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-541)-Lot-Fixed Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt541_lot_fixed_unpublished_justification_code],
        merge_bt197_bt541_lot_fixed_unpublished_justification_code,
        "procedure BT-197(BT-541)-Lot-Fixed Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-541) Lot Threshold Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt541_lot_threshold_unpublished_justification_code],
        merge_bt197_bt541_lot_threshold_unpublished_justification_code,
        "Lot Threshold Unpublished Justification Code (BT-197(BT-541))",
    )

    # Parse and merge BT-197(BT-541) Lot Weight Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt541_lot_weight_unpublished_justification_code],
        merge_bt197_bt541_lot_weight_unpublished_justification_code,
        "Lot Weight Unpublished Justification Code (BT-197(BT-541))",
    )

    # Parse and merge BT-197(BT-541) LotsGroup Fixed Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt541_lotsgroup_fixed_unpublished_justification_code],
        merge_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
        "LotsGroup Fixed Unpublished Justification Code (BT-197(BT-541))",
    )

    # Parse and merge BT-197(BT-541)-LotsGroup-Threshold
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt541_lotsgroup_threshold],
        merge_bt197_bt541_lotsgroup_threshold,
        "Unpublished Justification Code for LotsGroup Threshold (BT-197(BT-541))",
    )

    # Parse and merge BT-197(BT-541)-LotsGroup-Weight
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt541_lotsgroup_weight],
        merge_bt197_bt541_lotsgroup_weight,
        "Unpublished Justification Code for LotsGroup Weight (BT-197(BT-541))",
    )
    # Parse and merge BT-197(BT-5421)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt5421_lot],
        merge_bt197_bt5421_lot,
        "Unpublished Justification Code for Lot (BT-197(BT-5421))",
    )
    # Parse and merge BT-197(BT-5421)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt5421_lotsgroup],
        merge_bt197_bt5421_lotsgroup,
        "Unpublished Justification Code for LotsGroup (BT-197(BT-5421))",
    )
    # Parse and merge BT-197(BT-5422)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt5422_lot],
        merge_bt197_bt5422_lot,
        "Unpublished Justification Code for Lot (BT-197(BT-5422))",
    )

    # Parse and merge BT-197(BT-5422)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt5422_lotsgroup],
        merge_bt197_bt5422_lotsgroup,
        "Unpublished Justification Code for LotsGroup (BT-197(BT-5422))",
    )
    # Parse and merge BT-197(BT-5423)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt5423_lot],
        merge_bt197_bt5423_lot,
        "Unpublished Justification Code for Lot (BT-197(BT-5423))",
    )
    # Parse and merge BT-197(BT-5423)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt5423_lotsgroup],
        merge_bt197_bt5423_lotsgroup,
        "Unpublished Justification Code for LotsGroup (BT-197(BT-5423))",
    )
    # Parse and merge BT-197(BT-543)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt543_lot],
        merge_bt197_bt543_lot,
        "Unpublished Justification Code for Lot (BT-197(BT-543))",
    )
    # Parse and merge BT-197(BT-543)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt543_lotsgroup],
        merge_bt197_bt543_lotsgroup,
        "Unpublished Justification Code for LotsGroup (BT-197(BT-543))",
    )
    # Parse and merge BT-197(BT-553)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt553_tender],
        merge_bt197_bt553_tender,
        "Unpublished Justification Code for Tender (BT-197(BT-553))",
    )

    # Parse and merge BT-197(BT-554)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt554_unpublished_justification_code],
        merge_bt197_bt554_unpublished_justification_code,
        "Unpublished Justification Code for Tender Subcontracting Description (BT-197(BT-554))",
    )
    # Parse and merge BT-197(BT-555)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt555_unpublished_justification_code],
        merge_bt197_bt555_unpublished_justification_code,
        "Unpublished Justification Code for Tender Subcontracting Percentage (BT-197(BT-555))",
    )
    # Parse and merge BT-197(BT-635)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt635_unpublished_justification_code],
        merge_bt197_bt635_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result buyer Review Request Count (BT-197(BT-635))",
    )
    # Parse and merge BT-197(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt636_unpublished_justification_code],
        merge_bt197_bt636_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result buyer Review Request Irregularity Type (BT-197(BT-636))",
    )
    # Parse and merge BT-197(BT-660)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt660_unpublished_justification_code],
        merge_bt197_bt660_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result Framework Re-estimated Value (BT-197(BT-660))",
    )
    # Parse and merge BT-197(BT-709)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt709_unpublished_justification_code],
        merge_bt197_bt709_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result Maximum Value (BT-197(BT-709))",
    )
    # Parse and merge BT-197(BT-710)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt710_unpublished_justification_code],
        merge_bt197_bt710_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result Tender Lowest Value (BT-197(BT-710))",
    )
    # Parse and merge BT-197(BT-711)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt711_unpublished_justification_code],
        merge_bt197_bt711_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result Tender Highest Value (BT-197(BT-711))",
    )
    # Parse and merge BT-197(BT-712)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt712_unpublished_justification_code],
        merge_bt197_bt712_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result buyer Review Complainants (BT-197(BT-712))",
    )
    # Parse and merge BT-197(BT-720)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt720_unpublished_justification_code],
        merge_bt197_bt720_unpublished_justification_code,
        "Unpublished Justification Code for Winning Tender Value (BT-197(BT-720))",
    )
    # Parse and merge BT-197(BT-733)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt733_unpublished_justification_code],
        merge_bt197_bt733_unpublished_justification_code,
        "Unpublished Justification Code for Award Criteria Order Justification (BT-197(BT-733))",
    )
    # Parse and merge BT-197(BT-733)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt733_lotsgroup_unpublished_justification_code],
        merge_bt197_bt733_lotsgroup_unpublished_justification_code,
        "Unpublished Justification Code for Award Criteria Order Justification in LotsGroup (BT-197(BT-733))",
    )
    # Parse and merge BT-197(BT-734)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt734_lot_unpublished_justification_code],
        merge_bt197_bt734_lot_unpublished_justification_code,
        "Unpublished Justification Code for Award Criterion Name in Lot (BT-197(BT-734))",
    )
    # Parse and merge BT-197(BT-734)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt734_lotsgroup_unpublished_justification_code],
        merge_bt197_bt734_lotsgroup_unpublished_justification_code,
        "Unpublished Justification Code for Award Criterion Name in Lots Group (BT-197(BT-734))",
    )
    # Parse and merge BT-197(BT-759)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt759_lotresult_unpublished_justification_code],
        merge_bt197_bt759_lotresult_unpublished_justification_code,
        "Unpublished Justification Code for Received Submissions Count in Lot Result (BT-197(BT-759))",
    )
    # Parse and merge BT-197(BT-760)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt760_lotresult_unpublished_justification_code],
        merge_bt197_bt760_lotresult_unpublished_justification_code,
        "Unpublished Justification Code for Received Submissions Type in Lot Result (BT-197(BT-760))",
    )
    # Parse and merge BT-197(BT-773)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt773_tender_unpublished_justification_code],
        merge_bt197_bt773_tender_unpublished_justification_code,
        "Unpublished Justification Code for Subcontracting in Tender (BT-197(BT-773))",
    )
    # Parse and merge BT-197(BT-88)-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt88_procedure_unpublished_justification_code],
        merge_bt197_bt88_procedure_unpublished_justification_code,
        "Unpublished Justification Code for procedure Features (BT-197(BT-88))",
    )

    # BT-198
    # Parse and merge BT-198(BT-09) Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [bt_198_parse_unpublished_access_date_bt_09_procedure],
        bt_198_merge_unpublished_access_date_bt_09_procedure,
        "Unpublished Access Date (BT-198, BT-09)",
    )

    # Parse and merge BT-198(BT-106)-procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt106_unpublished_access_date],
        merge_bt198_bt106_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-106)",
    )

    # Parse and merge BT-198(BT-105)-procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt105_unpublished_access_date],
        merge_bt198_bt105_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-105)",
    )

    # Parse and merge BT-198(BT-1252)-procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt1252_unpublished_access_date],
        merge_bt198_bt1252_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-1252)",
    )

    # Parse and merge BT-198(BT-135)-procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt135_unpublished_access_date],
        merge_bt198_bt135_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-135)",
    )

    # Parse and merge BT-198(BT-1351)-procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt1351_unpublished_access_date],
        merge_bt198_bt1351_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-1351)",
    )

    # Parse and merge BT-198(BT-142)-LotResult Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt142_unpublished_access_date],
        merge_bt198_bt142_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-142)",
    )

    # Parse and merge BT-198(BT-144)-LotResult Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt144_unpublished_access_date],
        merge_bt198_bt144_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-144)",
    )

    # Parse and merge BT-198(BT-160)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt160_unpublished_access_date],
        merge_bt198_bt160_unpublished_access_date,
        "procedure BT-198(BT-160)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-162)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt162_unpublished_access_date],
        merge_bt198_bt162_unpublished_access_date,
        "procedure BT-198(BT-162)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-163)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt163_unpublished_access_date],
        merge_bt198_bt163_unpublished_access_date,
        "procedure BT-198(BT-163)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-171)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt171_unpublished_access_date],
        merge_bt198_bt171_unpublished_access_date,
        "procedure BT-198(BT-171)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-191)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt191_unpublished_access_date],
        merge_bt198_bt191_unpublished_access_date,
        "procedure BT-198(BT-191)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-193)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt193_unpublished_access_date],
        merge_bt198_bt193_unpublished_access_date,
        "procedure BT-198(BT-193)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-539)-Lot Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt539_unpublished_access_date],
        merge_bt198_bt539_unpublished_access_date,
        "procedure BT-198(BT-539)-Lot Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-539)-LotsGroup Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt539_lotsgroup_unpublished_access_date],
        merge_bt198_bt539_lotsgroup_unpublished_access_date,
        "procedure BT-198(BT-539)-LotsGroup Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-540)-Lot Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt540_lot_unpublished_access_date],
        merge_bt198_bt540_lot_unpublished_access_date,
        "procedure BT-198(BT-540)-Lot Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-540)-LotsGroup Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt540_lotsgroup_unpublished_access_date],
        merge_bt198_bt540_lotsgroup_unpublished_access_date,
        "procedure BT-198(BT-540)-LotsGroup Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-541)-Lot-Fixed Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt541_lot_fixed_unpublished_access_date],
        merge_bt198_bt541_lot_fixed_unpublished_access_date,
        "procedure BT-198(BT-541)-Lot-Fixed Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-541) Lot Threshold Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt541_lot_threshold_unpublished_access_date],
        merge_bt198_bt541_lot_threshold_unpublished_access_date,
        "Lot Threshold Unpublished Access Date (BT-198(BT-541))",
    )

    # Parse and merge BT-198(BT-541) Lot Weight Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt541_lot_weight_unpublished_access_date],
        merge_bt198_bt541_lot_weight_unpublished_access_date,
        "Lot Weight Unpublished Access Date (BT-198(BT-541))",
    )

    # Parse and merge BT-198(BT-541) LotsGroup Fixed Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt541_lotsgroup_fixed_unpublished_access_date],
        merge_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
        "LotsGroup Fixed Unpublished Access Date (BT-198(BT-541))",
    )
    # Parse and merge BT-198(BT-541)-LotsGroup-Threshold
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt541_lotsgroup_threshold],
        merge_bt198_bt541_lotsgroup_threshold,
        "Unpublished Access Date for LotsGroup Threshold (BT-198(BT-541))",
    )
    # Parse and merge BT-198(BT-541)-LotsGroup-Weight
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt541_lotsgroup_weight],
        merge_bt198_bt541_lotsgroup_weight,
        "Unpublished Access Date for LotsGroup Weight (BT-198(BT-541))",
    )
    # Parse and merge BT-198(BT-5421)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt5421_lot],
        merge_bt198_bt5421_lot,
        "Unpublished Access Date for Lot (BT-198(BT-5421))",
    )
    # Parse and merge BT-198(BT-5421)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt5421_lotsgroup],
        merge_bt198_bt5421_lotsgroup,
        "Unpublished Access Date for LotsGroup (BT-198(BT-5421))",
    )
    # Parse and merge BT-198(BT-5422)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt5422_lot],
        merge_bt198_bt5422_lot,
        "Unpublished Access Date for Lot (BT-198(BT-5422))",
    )
    # Parse and merge BT-198(BT-5422)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt5422_lotsgroup],
        merge_bt198_bt5422_lotsgroup,
        "Unpublished Access Date for LotsGroup (BT-198(BT-5422))",
    )
    # Parse and merge BT-198(BT-5423)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt5423_lot],
        merge_bt198_bt5423_lot,
        "Unpublished Access Date for Lot (BT-198(BT-5423))",
    )
    # Parse and merge BT-198(BT-5423)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt5423_lotsgroup],
        merge_bt198_bt5423_lotsgroup,
        "Unpublished Access Date for LotsGroup (BT-198(BT-5423))",
    )
    # Parse and merge BT-198(BT-543)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt543_lot],
        merge_bt198_bt543_lot,
        "Unpublished Access Date for Lot (BT-198(BT-543))",
    )
    # Parse and merge BT-198(BT-543)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt543_lotsgroup],
        merge_bt198_bt543_lotsgroup,
        "Unpublished Access Date for LotsGroup (BT-198(BT-543))",
    )
    # Parse and merge BT-198(BT-553)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt553_tender],
        merge_bt198_bt553_tender,
        "Unpublished Access Date for Tender (BT-198(BT-553))",
    )
    # Parse and merge BT-198(BT-554)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt554_unpublished_access_date],
        merge_bt198_bt554_unpublished_access_date,
        "Unpublished Access Date for Tender Subcontracting Description (BT-198(BT-554))",
    )
    # Parse and merge BT-198(BT-555)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt555_unpublished_access_date],
        merge_bt198_bt555_unpublished_access_date,
        "Unpublished Access Date for Tender Subcontracting Percentage (BT-198(BT-555))",
    )
    # Parse and merge BT-198(BT-635)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt635_unpublished_access_date],
        merge_bt198_bt635_unpublished_access_date,
        "Unpublished Access Date for Lot Result buyer Review Request Count (BT-198(BT-635))",
    )
    # Parse and merge BT-198(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt636_unpublished_access_date],
        merge_bt198_bt636_unpublished_access_date,
        "Unpublished Access Date for Lot Result buyer Review Request Irregularity Type (BT-198(BT-636))",
    )
    # Parse and merge BT-198(BT-660)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt660_unpublished_access_date],
        merge_bt198_bt660_unpublished_access_date,
        "Unpublished Access Date for Lot Result Framework Re-estimated Value (BT-198(BT-660))",
    )
    # Parse and merge BT-198(BT-709)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt709_unpublished_access_date],
        merge_bt198_bt709_unpublished_access_date,
        "Unpublished Access Date for Lot Result Maximum Value (BT-198(BT-709))",
    )
    # Parse and merge BT-198(BT-710)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt710_unpublished_access_date],
        merge_bt198_bt710_unpublished_access_date,
        "Unpublished Access Date for Lot Result Tender Lowest Value (BT-198(BT-710))",
    )
    # Parse and merge BT-198(BT-711)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt711_unpublished_access_date],
        merge_bt198_bt711_unpublished_access_date,
        "Unpublished Access Date for Lot Result Tender Highest Value (BT-198(BT-711))",
    )
    # Parse and merge BT-198(BT-712)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt712_unpublished_access_date],
        merge_bt198_bt712_unpublished_access_date,
        "Unpublished Access Date for Lot Result buyer Review Complainants (BT-198(BT-712))",
    )
    # Parse and merge BT-198(BT-720)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt720_unpublished_access_date],
        merge_bt198_bt720_unpublished_access_date,
        "Unpublished Access Date for Winning Tender Value (BT-198(BT-720))",
    )
    # Parse and merge BT-198(BT-733)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt733_unpublished_access_date],
        merge_bt198_bt733_unpublished_access_date,
        "Unpublished Access Date for Award Criteria Order Justification (BT-198(BT-733))",
    )
    # Parse and merge BT-198(BT-733)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt733_lotsgroup_unpublished_access_date],
        merge_bt198_bt733_lotsgroup_unpublished_access_date,
        "Unpublished Access Date for Award Criteria Order Justification in LotsGroup (BT-198(BT-733))",
    )
    # Parse and merge BT-198(BT-734)-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt734_lot_unpublished_access_date],
        merge_bt198_bt734_lot_unpublished_access_date,
        "Unpublished Access Date for Award Criterion Name in Lot (BT-198(BT-734))",
    )
    # Parse and merge BT-198(BT-734)-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt734_lotsgroup_unpublished_access_date],
        merge_bt198_bt734_lotsgroup_unpublished_access_date,
        "Unpublished Access Date for Award Criterion Name in Lots Group (BT-198(BT-734))",
    )
    # Parse and merge BT-198(BT-759)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt759_lotresult_unpublished_access_date],
        merge_bt198_bt759_lotresult_unpublished_access_date,
        "Unpublished Access Date for Received Submissions Count in Lot Result (BT-198(BT-759))",
    )
    # Parse and merge BT-198(BT-760)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt760_lotresult_unpublished_access_date],
        merge_bt198_bt760_lotresult_unpublished_access_date,
        "Unpublished Access Date for Received Submissions Type in Lot Result (BT-198(BT-760))",
    )
    # Parse and merge BT-198(BT-773)-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt773_tender_unpublished_access_date],
        merge_bt198_bt773_tender_unpublished_access_date,
        "Unpublished Access Date for Subcontracting in Tender (BT-198(BT-773))",
    )
    # Parse and merge BT-198(BT-88)-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt88_procedure_unpublished_access_date],
        merge_bt198_bt88_procedure_unpublished_access_date,
        "Unpublished Access Date for procedure Features (BT-198(BT-88))",
    )

    # Process BT-200-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_modification_reason],
        merge_contract_modification_reason,
        "BT-200-Contract (Contract Modification Reason)",
    )

    # Parse and merge BT-198(BT-136)-procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt136_unpublished_access_date],
        merge_bt198_bt136_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-136)",
    )

    # Process BT-201-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_modification_description],
        merge_contract_modification_description,
        "BT-201-Contract (Contract Modification Description)",
    )

    # Process BT-202-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_modification_summary],
        merge_contract_modification_summary,
        "BT-202-Contract (Contract Modification Summary)",
    )

    # Process BT-21-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_title],
        merge_lot_title,
        "BT-21-Lot (Lot Title)",
    )

    # Process BT-21-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_lots_group_title],
        merge_lots_group_title,
        "BT-21-LotsGroup (Lots Group Title)",
    )

    # Process BT-21-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_title],
        merge_part_title,
        "BT-21-part (part Title)",
    )

    # Process BT-21-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_title],
        merge_procedure_title,
        "BT-21-procedure (procedure Title)",
    )

    # Process BT-22-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_internal_identifier],
        merge_lot_internal_identifier,
        "BT-22-Lot (Lot Internal Identifier)",
    )

    # Process BT-23-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_nature],
        merge_main_nature,
        "BT-23-Lot (Main Nature)",
    )

    # Process BT-23-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_nature_part],
        merge_main_nature_part,
        "BT-23-part (Main Nature part)",
    )

    # Process BT-23-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_nature_procedure],
        merge_main_nature_procedure,
        "BT-23-procedure (Main Nature procedure)",
    )

    # Process BT-24-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_description],
        merge_lot_description,
        "BT-24-Lot (Lot Description)",
    )

    # Process BT-24-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_lots_group_description],
        merge_lots_group_description,
        "BT-24-LotsGroup (Lots Group Description)",
    )

    # Process BT-24-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_description],
        merge_part_description,
        "BT-24-part (part Description)",
    )

    # Process BT-24-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_description],
        merge_procedure_description,
        "BT-24-procedure (procedure Description)",
    )

    # Process BT-25-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_quantity],
        merge_lot_quantity,
        "BT-25-Lot (Lot Quantity)",
    )

    # Process BT-26-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_classification_type],
        merge_classification_type,
        "BT-26-Lot (Classification Type)",
    )

    # Process BT-26-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_classification_type_part],
        merge_classification_type_part,
        "BT-26-part (Classification Type part)",
    )

    # Process BT-26-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_classification_type_procedure],
        merge_classification_type_procedure,
        "BT-26-procedure (Classification Type procedure)",
    )

    # Process Main Classification Type for BT_26m_lot Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_type_lot],
        merge_main_classification_type_lot,
        "Main Classification Type for Lot (BT_26m_lot)",
    )

    # Process Main Classification Type for BT_26m_part
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_type_part],
        merge_main_classification_type_part,
        "Main Classification Type for part (BT_26m_part)",
    )

    # Process Main Classification Type for BT_26m_procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_type_procedure],
        merge_main_classification_type_procedure,
        "Main Classification Type for procedure (BT_26m_procedure)",
    )

    # Process Main Classification Code for Lot BT_262_lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_code_lot],
        merge_main_classification_code_lot,
        "Main Classification Code for Lot (BT_262_lot)",
    )

    # Process Main Classification Code for part BT_262_part
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_code_part],
        merge_main_classification_code_part,
        "Main Classification Code for part (BT_262_part)",
    )

    # Process Main Classification Code for procedure BT_262_procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_code_procedure],
        merge_main_classification_code_procedure,
        "Main Classification Code for procedure (BT_262_procedure)",
    )

    # Process Additional Classification Code for Lot BT_263_lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_classification_code_lot],
        merge_additional_classification_code_lot,
        "Additional Classification Code for Lot (BT_263_lot)",
    )

    # Process Additional Classification Code for part BT_263_part
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_classification_code_part],
        merge_additional_classification_code_part,
        "Additional Classification Code for part (BT_263_part)",
    )

    # Process Additional Classification Code for procedure BT_263_procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_classification_code_procedure],
        merge_additional_classification_code_procedure,
        "Additional Classification Code for procedure (BT_263_procedure)",
    )

    # Process BT-27-Lot (Lot Estimated Value)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_estimated_value],
        merge_lot_estimated_value,
        "Lot Estimated Value (BT-27-Lot)",
    )

    # Process BT-27-LotsGroup Estimated Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_27_lots_group],
        merge_bt_27_lots_group,
        "LotsGroup Estimated Value (BT-27-LotsGroup)",
    )

    # Process BT-27-part Estimated Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_27_part],
        merge_bt_27_part,
        "part Estimated Value (BT-27-part)",
    )

    # Process BT-27-procedure Estimated Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_27_procedure],
        merge_bt_27_procedure,
        "procedure Estimated Value (BT-27-procedure)",
    )

    # Process BT-271-Lot Framework Maximum Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_271_lot],
        merge_bt_271_lot,
        "Lot Framework Maximum Value (BT-271-Lot)",
    )

    # Process BT-271-LotsGroup Framework Maximum Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_271_lots_group],
        merge_bt_271_lots_group,
        "LotsGroup Framework Maximum Value (BT-271-LotsGroup)",
    )

    # Process BT-271-procedure Framework Maximum Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_271_procedure],
        merge_bt_271_procedure,
        "procedure Framework Maximum Value (BT-271-procedure)",
    )

    # Process BT-300-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_additional_info],
        merge_lot_additional_info,
        "BT-300-Lot (Lot Additional Information)",
    )

    # Process BT-300-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_lotsgroup_additional_info],
        merge_lotsgroup_additional_info,
        "BT-300-LotsGroup (Lots Group Additional Information)",
    )

    # Process BT-300-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_additional_info],
        merge_part_additional_info,
        "BT-300-part (part Additional Information)",
    )

    # Process BT-300-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_additional_info],
        merge_procedure_additional_info,
        "BT-300-procedure (procedure Additional Information)",
    )

    # Process BT-31-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_max_lots_allowed],
        merge_max_lots_allowed,
        "BT-31-procedure (Maximum Lots Allowed)",
    )

    # Process BT-3201-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_identifier],
        merge_tender_identifier,
        "BT-3201-Tender (Tender Identifier)",
    )

    # Process BT-3202-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_tender_id],
        merge_contract_tender_id,
        "BT-3202-Contract (Contract Tender ID)",
    )

    # Process BT-33 Maximum Lots Awarded
    process_bt_section(
        release_json,
        xml_content,
        [parse_max_lots_awarded],
        merge_max_lots_awarded,
        "BT-33 (Maximum Lots Awarded)",
    )

    # Process BT-330 Group Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_group_identifier],
        merge_group_identifier,
        "BT-330 (Group Identifier)",
    )

    # Process BT-36-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_duration],
        merge_lot_duration,
        "BT-36-Lot (Lot Duration)",
    )

    # Process BT-36-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_duration],
        merge_part_duration,
        "BT-36-part (part Duration)",
    )

    # Process BT-40-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_selection_criteria_second_stage],
        merge_lot_selection_criteria_second_stage,
        "BT-40-Lot (Lot Selection Criteria Second Stage)",
    )

    # Process BT-41-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_following_contract],
        merge_lot_following_contract,
        "BT-41-Lot (Lot Following Contract)",
    )

    # Process BT-42-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_jury_decision_binding],
        merge_lot_jury_decision_binding,
        "BT-42-Lot (Lot Jury Decision Binding)",
    )

    # Process BT-44-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_prize_rank],
        merge_prize_rank,
        "BT-44-Lot (Prize Rank)",
    )

    # Process BT-45-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_rewards_other],
        merge_lot_rewards_other,
        "BT-45-Lot (Lot Rewards Other)",
    )

    # Process BT-46-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_jury_member_name],
        merge_jury_member_name,
        "BT-46-Lot (Jury Member Name)",
    )

    # Process BT-47-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_participant_name],
        merge_participant_name,
        "BT-47-Lot (participant Name)",
    )

    # Process BT-50-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_minimum_candidates],
        merge_minimum_candidates,
        "BT-50-Lot (Minimum Candidates)",
    )

    # Process BT-500
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_name],
        merge_ubo_name,
        "BT-500 (ubo Name)",
    )

    # Process BT-501
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_identifier],
        merge_organization_identifier,
        "BT-501 (organization Identifier)",
    )

    # Process BT-5010-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_eu_funds_financing_identifier],
        merge_eu_funds_financing_identifier,
        "BT-5010-Lot (EU Funds Financing Identifier)",
    )

    # Process BT-5011-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_eu_funds_financing_identifier],
        merge_contract_eu_funds_financing_identifier,
        "BT-5011-Contract (Contract EU Funds Financing Identifier)",
    )

    # Process BT-502-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_point],
        merge_organization_contact_point,
        "BT-502-organization-company (organization Contact Point)",
    )

    # Process BT-502-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_point],
        merge_touchpoint_contact_point,
        "BT-502-organization-touchpoint (touchpoint Contact Point)",
    )

    # Process BT-503-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_telephone],
        merge_organization_contact_telephone,
        "BT-503-organization-company (organization Contact Telephone)",
    )

    # Process BT-503-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_telephone],
        merge_touchpoint_contact_telephone,
        "BT-503-organization-touchpoint (touchpoint Contact Telephone)",
    )

    # Process BT-503-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_telephone],
        merge_ubo_telephone,
        "BT-503-ubo (ubo Telephone)",
    )

    # Process BT-505-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_website],
        merge_organization_website,
        "BT-505-organization-company (organization Website)",
    )

    # Process BT-505-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_website],
        merge_touchpoint_website,
        "BT-505-organization-touchpoint (touchpoint Website)",
    )

    # Process BT-506-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_email],
        merge_organization_contact_email,
        "BT-506-organization-company (organization Contact Email)",
    )

    # Process BT-506-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_email],
        merge_touchpoint_contact_email,
        "BT-506-organization-touchpoint (touchpoint Contact Email)",
    )

    # Process BT-506-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_email],
        merge_ubo_email,
        "BT-506-ubo (ubo Email)",
    )

    # Process BT-507-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_country_subdivision],
        merge_organization_country_subdivision,
        "BT-507-organization-company (organization Country Subdivision)",
    )

    # Process BT-507-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_country_subdivision],
        merge_touchpoint_country_subdivision,
        "BT-507-organization-touchpoint (touchpoint Country Subdivision)",
    )

    # Process BT-507-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_country_subdivision],
        merge_ubo_country_subdivision,
        "BT-507-ubo (ubo Country Subdivision)",
    )

    # Process BT-5071-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_country_subdivision],
        merge_place_performance_country_subdivision,
        "BT-5071-Lot (Place Performance Country Subdivision)",
    )

    # Parse and merge BT-5071 Place Performance Country Subdivision for part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_country_subdivision],
        merge_part_place_performance_country_subdivision,
        "Place Performance Country Subdivision part (BT-5071)",
    )

    # Process BT-5071-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_country_subdivision],
        merge_procedure_place_performance_country_subdivision,
        "BT-5071-procedure (procedure Place Performance Country Subdivision)",
    )

    # Process BT-508-procedure-buyer
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_profile_url],
        merge_buyer_profile_url,
        "BT-508-procedure-buyer (buyer Profile URL)",
    )

    # Process BT-509-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_edelivery_gateway],
        merge_organization_edelivery_gateway,
        "BT-509-organization-company (organization eDelivery Gateway)",
    )

    # Process BT-509-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_edelivery_gateway],
        merge_touchpoint_edelivery_gateway,
        "BT-509-organization-touchpoint (touchpoint eDelivery Gateway)",
    )

    # Process BT-51-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_maximum_candidates],
        merge_lot_maximum_candidates,
        "BT-51-Lot (Lot Maximum Candidates Number)",
    )

    # Process BT-510(a)-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_street],
        merge_organization_street,
        "BT-510(a)-organization-company (organization Street)",
    )

    # Process BT-510(a)-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_street],
        merge_touchpoint_street,
        "BT-510(a)-organization-touchpoint (touchpoint Street)",
    )

    # Process BT-510(a)-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_street],
        merge_ubo_street,
        "BT-510(a)-ubo (ubo Street)",
    )

    # Process BT-510(b)-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_streetline1],
        merge_organization_streetline1,
        "BT-510(b)-organization-company (organization Streetline 1)",
    )

    # Process BT-510(b)-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_streetline1],
        merge_touchpoint_streetline1,
        "BT-510(b)-organization-touchpoint (touchpoint Streetline 1)",
    )

    # Process BT-510(b)-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_streetline1],
        merge_ubo_streetline1,
        "BT-510(b)-ubo (ubo Streetline 1)",
    )

    # Process BT-510(c)-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_streetline2],
        merge_organization_streetline2,
        "BT-510(c)-organization-company (organization Streetline 2)",
    )

    # Process BT-510(c)-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_streetline2],
        merge_touchpoint_streetline2,
        "BT-510(c)-organization-touchpoint (touchpoint Streetline 2)",
    )

    # Process BT-510(c)-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_streetline2],
        merge_ubo_streetline2,
        "BT-510(c)-ubo (ubo Streetline 2)",
    )

    # Parse and merge BT-5101 Place Performance Street for Lot (including both a and b parts)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_street_lot],
        merge_place_performance_street_lot,
        "Place Performance Street Lot (BT-5101)",
    )

    # Process BT-5101(a)-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_street],
        merge_part_place_performance_street,
        "BT-5101(a)-part (part Place Performance Street)",
    )

    # Process BT-5101(a)-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_street],
        merge_procedure_place_performance_street,
        "BT-5101(a)-procedure (procedure Place Performance Street)",
    )

    # Process BT-5101(b)-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_streetline1],
        merge_part_place_performance_streetline1,
        "BT-5101(b)-part (part Place Performance Streetline 1)",
    )

    # Process BT-5101(b)-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_streetline1],
        merge_procedure_place_performance_streetline1,
        "BT-5101(b)-procedure (procedure Place Performance Streetline 1)",
    )

    # Process BT-5101(c)-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_streetline2],
        merge_part_place_performance_streetline2,
        "BT-5101(c)-part (part Place Performance Streetline 2)",
    )

    # Process BT-5101(c)-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_streetline2],
        merge_procedure_place_performance_streetline2,
        "BT-5101(c)-procedure (procedure Place Performance Streetline 2)",
    )

    # Process BT-512-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_postcode],
        merge_organization_postcode,
        "BT-512-organization-company (organization Postcode)",
    )

    # Process BT-512-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_postcode],
        merge_touchpoint_postcode,
        "BT-512-organization-touchpoint (touchpoint Postcode)",
    )

    # Process BT-512-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_postcode],
        merge_ubo_postcode,
        "BT-512-ubo (ubo Postcode)",
    )

    # Process BT-5121-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_post_code],
        merge_place_performance_post_code,
        "BT-5121-Lot (Place Performance Post Code)",
    )

    # Process BT-5121-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_post_code_part],
        merge_place_performance_post_code_part,
        "BT-5121-part (Place Performance Post Code part)",
    )
    # Process BT-5121-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_post_code_procedure],
        merge_place_performance_post_code_procedure,
        "BT-5121-procedure (Place Performance Post Code)",
    )

    # Process BT-513-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_city],
        merge_organization_city,
        "BT-513-organization-company (organization City)",
    )

    # Process BT-513-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_city],
        merge_touchpoint_city,
        "BT-513-organization-touchpoint (touchpoint City)",
    )

    # Process BT-513-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_city],
        merge_ubo_city,
        "BT-513-ubo (ubo City)",
    )

    # Process BT-5131 (Place Performance City)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_city],
        merge_place_performance_city,
        "BT-5131 (Place Performance City)",
    )

    # Process BT-5131 part (Place Performance City part)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_city_part],
        merge_place_performance_city_part,
        "BT-5131 part (Place Performance City part)",
    )

    # Process BT-5131 procedure (Place Performance City procedure)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_city_procedure],
        merge_place_performance_city_procedure,
        "BT-5131 procedure (Place Performance City procedure)",
    )

    # Process BT-514-organization-company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_country],
        merge_organization_country,
        "BT-514-organization-company (organization Country)",
    )

    # Process BT-514-organization-touchpoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_country],
        merge_touchpoint_country,
        "BT-514-organization-touchpoint (touchpoint Country)",
    )

    # Process BT-514-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_country],
        merge_ubo_country,
        "BT-514-ubo (ubo Country)",
    )

    # Process BT-5141-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_country],
        merge_lot_country,
        "BT-5141-Lot (Lot Country)",
    )

    # Process BT-5141-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_country],
        merge_part_country,
        "BT-5141-part (part Country)",
    )

    # Process BT-5141-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_country],
        merge_procedure_country,
        "BT-5141-procedure (procedure Country)",
    )

    # Process BT-52-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_successive_reduction_indicator],
        merge_successive_reduction_indicator,
        "BT-52-Lot (Successive Reduction Indicator)",
    )

    # Process BT-531-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_additional_nature],
        merge_lot_additional_nature,
        "BT-531-Lot (Lot Additional Nature)",
    )

    # Process BT-531-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_additional_nature],
        merge_part_additional_nature,
        "BT-531-part (part Additional Nature)",
    )

    # Process BT-531-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_additional_nature],
        merge_procedure_additional_nature,
        "BT-531-procedure (procedure Additional Nature)",
    )

    # Process BT-536-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_start_date],
        merge_lot_start_date,
        "BT-536-Lot",
    )

    # Process BT-536-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_contract_start_date],
        merge_part_contract_start_date,
        "BT-536-part",
    )

    # Process BT-537-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_duration_end_date],
        merge_lot_duration_end_date,
        "BT-537-Lot",
    )

    # Process BT-537-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_duration_end_date],
        merge_part_duration_end_date,
        "BT-537-part",
    )

    # Process BT-538-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_duration_other],
        merge_lot_duration_other,
        "BT-538-Lot",
    )

    # Process BT-538-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_duration_other],
        merge_part_duration_other,
        "BT-538-part",
    )

    # Process BT-539-Lot (Award Criterion Type)
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_type],
        merge_award_criterion_type,
        "BT-539-Lot (Award Criterion Type)",
    )

    # Process BT-539-LotsGroup (Award Criterion Type for Lot Groups)
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_type_lots_group],
        merge_award_criterion_type_lots_group,
        "BT-539-LotsGroup (Award Criterion Type for Lot Groups)",
    )

    # Process BT-540-Lot (Award Criterion Description)
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_description],
        merge_award_criterion_description,
        "BT-540-Lot (Award Criterion Description)",
    )

    # Process BT-540-LotsGroup (Award Criterion Description for Lot Groups)
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_description_lots_group],
        merge_award_criterion_description_lots_group,
        "BT-540-LotsGroup (Award Criterion Description for Lot Groups)",
    )

    # Process BT-54-Lot (Options Description)
    process_bt_section(
        release_json,
        xml_content,
        [parse_options_description],
        merge_options_description,
        "BT-54-Lot (Options Description)",
    )

    # Process BT-541-Lot-FixedNumber (Award Criterion Fixed Number)
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_fixed_number],
        merge_award_criterion_fixed_number,
        "BT-541-Lot-FixedNumber (Award Criterion Fixed Number)",
    )

    # Process BT-5421-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_number_weight_lot],
        merge_award_criterion_number_weight_lot,
        "BT-5421-Lot",
    )

    # Process BT-5421-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_number_weight_lots_group],
        merge_award_criterion_number_weight_lots_group,
        "BT-5421-LotsGroup",
    )

    # Process BT-5422-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_number_fixed],
        merge_award_criterion_number_fixed,
        "BT-5422-Lot",
    )

    # Process BT-5422-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_number_fixed_lotsgroup],
        merge_award_criterion_number_fixed_lotsgroup,
        "BT-5422-LotsGroup",
    )

    # Process BT-5423-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_number_threshold],
        merge_award_criterion_number_threshold,
        "BT-5423-Lot",
    )

    # Process BT-5423-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_number_threshold_lotsgroup],
        merge_award_criterion_number_threshold_lotsgroup,
        "BT-5423-LotsGroup",
    )

    # Process BT-543-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criteria_complicated],
        merge_award_criteria_complicated,
        "BT-543-Lot",
    )

    # Process BT-543-LotsGroup (Award Criteria Complicated for Lot Groups)
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criteria_complicated_lotsgroup],
        merge_award_criteria_complicated_lotsgroup,
        "BT-543-LotsGroup",
    )

    # Process BT-553-Tender (Subcontracting Value)
    process_bt_section(
        release_json,
        xml_content,
        [parse_subcontracting_value],
        merge_subcontracting_value,
        "BT-553-Tender (Subcontracting Value)",
    )

    # Process BT-554-Tender (Subcontracting Description)
    process_bt_section(
        release_json,
        xml_content,
        [parse_subcontracting_description],
        merge_subcontracting_description,
        "BT-554-Tender (Subcontracting Description)",
    )

    # Process BT-555-Tender (Subcontracting Percentage)
    process_bt_section(
        release_json,
        xml_content,
        [parse_subcontracting_percentage],
        merge_subcontracting_percentage,
        "BT-555-Tender (Subcontracting Percentage)",
    )

    # Process BT-57-Lot (Renewal Description)
    process_bt_section(
        release_json,
        xml_content,
        [parse_renewal_description],
        merge_renewal_description,
        "BT-57-Lot (Renewal Description)",
    )

    # Process BT-58-Lot (Renewal Maximum)
    process_bt_section(
        release_json,
        xml_content,
        [parse_renewal_maximum],
        merge_renewal_maximum,
        "BT-58-Lot (Renewal Maximum)",
    )

    # Process BT-60-Lot (EU Funds)
    process_bt_section(
        release_json,
        xml_content,
        [parse_eu_funds],
        merge_eu_funds,
        "BT-60-Lot (EU Funds)",
    )

    # Process BT-610-procedure-buyer (Activity Entity)
    process_bt_section(
        release_json,
        xml_content,
        [parse_activity_entity],
        merge_activity_entity,
        "BT-610-procedure-buyer (Activity Entity)",
    )

    # Process BT-6110-Contract (Contract EU Funds Details)
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_eu_funds_details],
        merge_contract_eu_funds_details,
        "BT-6110-Contract (Contract EU Funds Details)",
    )

    # Process BT-6140-Lot (EU Funds Details)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_eu_funds_details],
        merge_lot_eu_funds_details,
        "BT-6140-Lot (EU Funds Details)",
    )

    # Process BT-615-Lot (Documents Restricted URL)
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_restricted_url],
        merge_documents_restricted_url,
        "BT-615-Lot (Documents Restricted URL)",
    )

    # Process BT-615-part (Documents Restricted URL for parts)
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_restricted_url_part],
        merge_documents_restricted_url_part,
        "BT-615-part (Documents Restricted URL for parts)",
    )

    # Process BT-625-Lot (Unit)
    process_bt_section(
        release_json,
        xml_content,
        [parse_unit],
        merge_unit,
        "BT-625-Lot (Unit)",
    )

    # Process BT-63-Lot (Variants)
    process_bt_section(
        release_json,
        xml_content,
        [parse_variants],
        merge_variants,
        "BT-63-Lot (Variants)",
    )

    # Process BT-630-Lot Deadline Receipt Expressions
    process_bt_section(
        release_json,
        xml_content,
        [parse_deadline_receipt_expressions],
        merge_deadline_receipt_expressions,
        "BT-630-Lot Deadline Receipt Expressions",
    )

    # Process BT-631-Lot (Dispatch Invitation Interest)
    process_bt_section(
        release_json,
        xml_content,
        [parse_dispatch_invitation_interest],
        merge_dispatch_invitation_interest,
        "BT-631-Lot (Dispatch Invitation Interest)",
    )

    # Process BT-632-Lot (Tool Name)
    process_bt_section(
        release_json,
        xml_content,
        [parse_tool_name],
        merge_tool_name,
        "BT-632-Lot (Tool Name)",
    )

    # Process BT-632-part (Tool Name)
    process_bt_section(
        release_json,
        xml_content,
        [parse_tool_name_part],
        merge_tool_name_part,
        "BT-632-part (Tool Name)",
    )

    # Process BT-633-organization (Organisation Natural Person)
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_natural_person],
        merge_organization_natural_person,
        "BT-633-organization (Organisation Natural Person)",
    )

    # Process BT-635-LotResult buyer Review Requests Count
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_review_requests_count],
        merge_buyer_review_requests_count,
        "BT-635-LotResult buyer Review Requests Count",
    )

    # Process BT-636-LotResult buyer Review Requests Irregularity Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_irregularity_type],
        merge_irregularity_type,
        "BT-636-LotResult buyer Review Requests Irregularity Type",
    )

    # Process BT-64-Lot (Subcontracting Obligation Minimum)
    process_bt_section(
        release_json,
        xml_content,
        [parse_subcontracting_obligation_minimum],
        merge_subcontracting_obligation_minimum,
        "BT-64-Lot (Subcontracting Obligation Minimum)",
    )

    # Process BT-644-Lot (Prize Value)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_prize_value],
        merge_lot_prize_value,
        "BT-644-Lot (Prize Value)",
    )

    # Process BT-65-Lot Subcontracting Obligation
    process_bt_section(
        release_json,
        xml_content,
        [parse_subcontracting_obligation],
        merge_subcontracting_obligation,
        "BT-65-Lot Subcontracting Obligation",
    )

    # Process BT-651-Lot Subcontracting Tender Indication
    process_bt_section(
        release_json,
        xml_content,
        [parse_subcontracting_tender_indication],
        merge_subcontracting_tender_indication,
        "BT-651-Lot Subcontracting Tender Indication",
    )

    # Process BT-660-LotResult (Framework Re-estimated Value)
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_reestimated_value],
        merge_framework_reestimated_value,
        "BT-660-LotResult (Framework Re-estimated Value)",
    )

    # Process BT-67 Exclusion Grounds
    process_bt_section(
        release_json,
        xml_content,
        [parse_exclusion_grounds],
        merge_exclusion_grounds,
        "BT-67 Exclusion Grounds",
    )

    # Process BT-70-Lot (Performance Terms)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_performance_terms],
        merge_lot_performance_terms,
        "BT-70-Lot (Performance Terms)",
    )

    # Process BT-702(a)-notice (notice Official Language)
    process_bt_section(
        release_json,
        xml_content,
        [parse_notice_language],
        merge_notice_language,
        "BT-702(a)-notice (notice Official Language)",
    )

    # Process BT-706-ubo Winner Owner Nationality
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_nationality],
        merge_ubo_nationality,
        "BT-706-ubo Winner Owner Nationality",
    )

    # Process BT-707-Lot (Documents Restricted Justification)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_documents_restricted_justification],
        merge_lot_documents_restricted_justification,
        "BT-707-Lot (Documents Restricted Justification)",
    )

    # Process BT-707-part (Documents Restricted Justification)
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_documents_restricted_justification],
        merge_part_documents_restricted_justification,
        "BT-707-part (Documents Restricted Justification)",
    )

    # Process BT-708-Lot (Documents Official Language)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_documents_official_language],
        merge_lot_documents_official_language,
        "BT-708-Lot (Documents Official Language)",
    )

    # Process BT-708-part (Documents Official Language)
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_documents_official_language],
        merge_part_documents_official_language,
        "BT-708-part (Documents Official Language)",
    )

    # Process BT-709-LotResult (Framework Maximum Value)
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_maximum_value],
        merge_framework_maximum_value,
        "BT-709-LotResult (Framework Maximum Value)",
    )

    # Process BT-71-Lot (Reserved participation)
    process_bt_section(
        release_json,
        xml_content,
        [parse_reserved_participation],
        merge_reserved_participation,
        "BT-71-Lot (Reserved participation)",
    )

    # Process BT-71-part (Reserved participation)
    process_bt_section(
        release_json,
        xml_content,
        [parse_reserved_participation_part],
        merge_reserved_participation_part,
        "BT-71-part (Reserved participation)",
    )

    # Process BT-710-LotResult Tender Value Lowest
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_value_lowest],
        merge_tender_value_lowest,
        "BT-710-LotResult Tender Value Lowest",
    )

    # Process BT-711-LotResult Tender Value Highest
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_value_highest],
        merge_tender_value_highest,
        "BT-711-LotResult Tender Value Highest",
    )

    # Process BT-712(a)-LotResult buyer Review Complainants
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_review_complainants],
        merge_buyer_review_complainants,
        "BT-712(a)-LotResult buyer Review Complainants",
    )

    # Process BT-712(b)-LotResult buyer Review Complainants (Number)
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_review_complainants_bt_712b],
        merge_buyer_review_complainants_bt_712b,
        "BT-712(b)-LotResult buyer Review Complainants (Number)",
    )

    # Process BT-717-Lot (Clean Vehicles Directive)
    process_bt_section(
        release_json,
        xml_content,
        [parse_clean_vehicles_directive],
        merge_clean_vehicles_directive,
        "Clean Vehicles Directive (BT-717-Lot)",
    )

    # Process BT-719-notice
    process_bt_section(
        release_json,
        xml_content,
        [parse_procurement_documents_change_date],
        merge_procurement_documents_change_date,
        "Procurement Documents Change Date (BT-719-notice)",
    )

    # Process BT-720-Tender (Tender Value)
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_value],
        merge_tender_value,
        "Tender Value (BT-720-Tender)",
    )

    # Process BT-721-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_title],
        merge_contract_title,
        "Contract Title (BT-721-Contract)",
    )

    # Process BT-722-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_eu_funds],
        merge_contract_eu_funds,
        "Contract EU Funds (BT-722-Contract)",
    )

    # Process BT-7220-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_eu_funds],
        merge_lot_eu_funds,
        "Lot EU Funds (BT-7220-Lot)",
    )

    # Process BT-723-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_vehicle_category],
        merge_vehicle_category,
        "Vehicle Category (BT-723-LotResult)",
    )

    # Process BT-726-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_sme_suitability],
        merge_lot_sme_suitability,
        "Lot SME Suitability (BT-726-Lot)",
    )

    # Process BT-726-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_lots_group_sme_suitability],
        merge_lots_group_sme_suitability,
        "Lots Group SME Suitability (BT-726-LotsGroup)",
    )

    # Process BT-726-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_sme_suitability],
        merge_part_sme_suitability,
        "part SME Suitability (BT-726-part)",
    )

    # Process BT-727-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_place_performance],
        merge_lot_place_performance,
        "Lot Place of Performance (BT-727-Lot)",
    )

    # Process BT-727-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance],
        merge_part_place_performance,
        "part Place of Performance (BT-727-part)",
    )

    # Process BT-727-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance],
        merge_procedure_place_performance,
        "procedure Place of Performance (BT-727-procedure)",
    )

    # Process BT-728-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_place_performance_additional],
        merge_lot_place_performance_additional,
        "Additional Lot Place of Performance (BT-728-Lot)",
    )

    # Process BT-728-part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_additional],
        merge_part_place_performance_additional,
        "Additional part Place of Performance (BT-728-part)",
    )

    # Process BT-728-procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_additional],
        merge_procedure_place_performance_additional,
        "Additional procedure Place of Performance (BT-728-procedure)",
    )

    # Process BT-729-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_subcontracting_obligation_maximum],
        merge_lot_subcontracting_obligation_maximum,
        "Lot Subcontracting Obligation Maximum Percentage (BT-729-Lot)",
    )

    # Process BT-732-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_security_clearance_description],
        merge_lot_security_clearance_description,
        "Lot Security Clearance Description (BT-732-Lot)",
    )

    # Process BT-733-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_award_criteria_order_justification],
        merge_lot_award_criteria_order_justification,
        "Lot Award Criteria Order Justification (BT-733-Lot)",
    )

    # Process BT-733-LotsGroup
    process_bt_section(
        release_json,
        xml_content,
        [parse_lots_group_award_criteria_order_justification],
        merge_lots_group_award_criteria_order_justification,
        "Lots Group Award Criteria Order Justification (BT-733-LotsGroup)",
    )

    # Process BT-734-Lot Award Criterion Name
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_name],
        merge_award_criterion_name,
        "Lot Award Criterion Name (BT-734-Lot)",
    )

    # Process BT-734-LotsGroup Award Criterion Name
    process_bt_section(
        release_json,
        xml_content,
        [parse_award_criterion_name_lotsgroup],
        merge_award_criterion_name_lotsgroup,
        "Lots Group Award Criterion Name (BT-734-LotsGroup)",
    )

    # Process BT-735-Lot CVD Contract Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_cvd_contract_type],
        merge_cvd_contract_type,
        "Lot CVD Contract Type (BT-735-Lot)",
    )

    # Process BT-735-LotResult CVD Contract Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_cvd_contract_type_lotresult],
        merge_cvd_contract_type_lotresult,
        "LotResult CVD Contract Type (BT-735-LotResult)",
    )

    # Process BT-736-Lot Reserved Execution
    process_bt_section(
        release_json,
        xml_content,
        [parse_reserved_execution],
        merge_reserved_execution,
        "Lot Reserved Execution (BT-736-Lot)",
    )

    # Process BT-736-part Reserved Execution
    process_bt_section(
        release_json,
        xml_content,
        [parse_reserved_execution_part],
        merge_reserved_execution_part,
        "part Reserved Execution (BT-736-part)",
    )

    # Process BT-737-Lot Documents Unofficial Language
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_unofficial_language],
        merge_documents_unofficial_language,
        "Lot Documents Unofficial Language (BT-737-Lot)",
    )

    # Process BT-737-part Documents Unofficial Language
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_unofficial_language_part],
        merge_documents_unofficial_language_part,
        "part Documents Unofficial Language (BT-737-part)",
    )

    # Process BT-738-notice notice Preferred Publication Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_notice_preferred_publication_date],
        merge_notice_preferred_publication_date,
        "notice Preferred Publication Date (BT-738-notice)",
    )

    # Process BT-739-organization-company Organisation Contact Fax
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_fax],
        merge_organization_contact_fax,
        "Organisation Contact Fax (BT-739-organization-company)",
    )

    # Process BT-739-organization-touchpoint Contact Fax
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_fax],
        merge_touchpoint_contact_fax,
        "touchpoint Contact Fax (BT-739-organization-touchpoint)",
    )

    # Process BT-739-ubo ubo Contact Fax
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_fax],
        merge_ubo_fax,
        "ubo Contact Fax (BT-739-ubo)",
    )

    # Process BT-740-procedure-buyer buyer Contracting Entity
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_contracting_entity],
        merge_buyer_contracting_entity,
        "buyer Contracting Entity (BT-740-procedure-buyer)",
    )

    # Process BT-743-Lot Electronic Invoicing
    process_bt_section(
        release_json,
        xml_content,
        [parse_electronic_invoicing],
        merge_electronic_invoicing,
        "Lot Electronic Invoicing (BT-743-Lot)",
    )

    # Process BT-744-Lot Submission Electronic Signature
    process_bt_section(
        release_json,
        xml_content,
        [parse_submission_electronic_signature],
        merge_submission_electronic_signature,
        "Lot Submission Electronic Signature (BT-744-Lot)",
    )

    # Process BT-745-Lot Submission Nonelectronic Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_submission_nonelectronic_description],
        merge_submission_nonelectronic_description,
        "Lot Submission Nonelectronic Description (BT-745-Lot)",
    )

    # Process BT-746-organization Winner Listed
    process_bt_section(
        release_json,
        xml_content,
        [parse_winner_listed],
        merge_winner_listed,
        "organization Winner Listed (BT-746-organization)",
    )

    # Process BT-747-Lot Selection Criteria Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_selection_criteria_type],
        merge_selection_criteria_type,
        "Lot Selection Criteria Type (BT-747-Lot)",
    )

    # Process BT-75-Lot Guarantee Required Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_guarantee_required_description],
        merge_guarantee_required_description,
        "Lot Guarantee Required Description (BT-75-Lot)",
    )

    # Process BT-749 and BT-750 Selection Criteria
    process_bt_section(
        release_json,
        xml_content,
        [parse_selection_criteria],
        merge_selection_criteria,
        "Selection Criteria (BT-749 and BT-750)",
    )

    # Process BT-752-Lot-ThresholdNumber Selection Criteria Second Stage Invite Threshold Number
    process_bt_section(
        release_json,
        xml_content,
        [parse_selection_criteria_threshold_number],
        merge_selection_criteria_threshold_number,
        "Selection Criteria Second Stage Invite Threshold Number (BT-752-Lot-ThresholdNumber)",
    )

    # Process BT-752-Lot-WeightNumber Selection Criteria Second Stage Invite Weight Number
    process_bt_section(
        release_json,
        xml_content,
        [parse_selection_criteria_weight_number],
        merge_selection_criteria_weight_number,
        "Selection Criteria Second Stage Invite Weight Number (BT-752-Lot-WeightNumber)",
    )

    # Process BT-7531-Lot Selection Criteria Second Stage Invite Number Weight
    process_bt_section(
        release_json,
        xml_content,
        [parse_selection_criteria_number_weight],
        merge_selection_criteria_number_weight,
        "Selection Criteria Second Stage Invite Number Weight (BT-7531-Lot)",
    )

    # Process BT-7532-Lot Selection Criteria Second Stage Invite Number Threshold
    process_bt_section(
        release_json,
        xml_content,
        [parse_selection_criteria_number_threshold],
        merge_selection_criteria_number_threshold,
        "Selection Criteria Second Stage Invite Number Threshold (BT-7532-Lot)",
    )

    # Process BT-754-Lot Accessibility Criteria
    process_bt_section(
        release_json,
        xml_content,
        [parse_accessibility_criteria],
        merge_accessibility_criteria,
        "Lot Accessibility Criteria (BT-754-Lot)",
    )

    # Process BT-755-Lot Accessibility Justification
    process_bt_section(
        release_json,
        xml_content,
        [parse_accessibility_justification],
        merge_accessibility_justification,
        "Lot Accessibility Justification (BT-755-Lot)",
    )

    # Process BT-756-procedure PIN Competition Termination
    process_bt_section(
        release_json,
        xml_content,
        [parse_pin_competition_termination],
        merge_pin_competition_termination,
        "PIN Competition Termination (BT-756-procedure)",
    )

    # Process BT-759-LotResult Received Submissions Count
    process_bt_section(
        release_json,
        xml_content,
        [parse_received_submissions_count],
        merge_received_submissions_count,
        "BT-759-LotResult Received Submissions Count",
    )

    # Process BT-76-Lot Tenderer Legal Form Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_tenderer_legal_form],
        merge_tenderer_legal_form,
        "Lot Tenderer Legal Form Description (BT-76-Lot)",
    )

    # Process BT-760-LotResult Received Submissions Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_received_submissions_type],
        merge_received_submissions_type,
        "BT-760-LotResult Received Submissions Type",
    )

    # Process BT-762-notice Change Reason Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_change_reason_description],
        merge_change_reason_description,
        "Change Reason Description (BT-762-notice)",
    )

    # Process BT-763-procedure Lots All Required
    process_bt_section(
        release_json,
        xml_content,
        [parse_lots_all_required],
        merge_lots_all_required,
        "Lots All Required (BT-763-procedure)",
    )

    # Process BT-764-Lot Submission Electronic Catalogue
    process_bt_section(
        release_json,
        xml_content,
        [parse_submission_electronic_catalogue],
        merge_submission_electronic_catalogue,
        "Submission Electronic Catalogue (BT-764-Lot)",
    )

    # Process BT-765-Lot Framework Agreement
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_agreement],
        merge_framework_agreement,
        "Framework Agreement (BT-765-Lot)",
    )

    # Process BT-765-part Framework Agreement
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_framework_agreement],
        merge_part_framework_agreement,
        "part Framework Agreement (BT-765-part)",
    )

    # Process BT-766-Lot Dynamic Purchasing System
    process_bt_section(
        release_json,
        xml_content,
        [parse_dynamic_purchasing_system],
        merge_dynamic_purchasing_system,
        "Dynamic Purchasing System (BT-766-Lot)",
    )

    # Process BT-766-part Dynamic Purchasing System
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_dynamic_purchasing_system],
        merge_part_dynamic_purchasing_system,
        "part Dynamic Purchasing System (BT-766-part)",
    )

    # Process BT-767-Lot Electronic Auction
    process_bt_section(
        release_json,
        xml_content,
        [parse_electronic_auction],
        merge_electronic_auction,
        "Electronic Auction (BT-767-Lot)",
    )

    # Process BT-769-Lot Multiple Tenders
    process_bt_section(
        release_json,
        xml_content,
        [parse_multiple_tenders],
        merge_multiple_tenders,
        "Multiple Tenders (BT-769-Lot)",
    )

    # Process BT-77-Lot Financial Terms
    process_bt_section(
        release_json,
        xml_content,
        [parse_financial_terms],
        merge_financial_terms,
        "Financial Terms (BT-77-Lot)",
    )

    # Process BT-771-Lot Late Tenderer Information
    process_bt_section(
        release_json,
        xml_content,
        [parse_late_tenderer_info],
        merge_late_tenderer_info,
        "Late Tenderer Information (BT-771-Lot)",
    )

    # Process BT-772-Lot Late Tenderer Information Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_late_tenderer_info_description],
        merge_late_tenderer_info_description,
        "Late Tenderer Information Description (BT-772-Lot)",
    )

    # Process BT-773-Tender Subcontracting
    process_bt_section(
        release_json,
        xml_content,
        [parse_subcontracting],
        merge_subcontracting,
        "Subcontracting (BT-773-Tender)",
    )

    # Process BT-774-Lot Green Procurement
    process_bt_section(
        release_json,
        xml_content,
        [parse_green_procurement],
        merge_green_procurement,
        "Green Procurement (BT-774-Lot)",
    )

    # Process BT-775-Lot Social Procurement
    process_bt_section(
        release_json,
        xml_content,
        [parse_social_procurement],
        merge_social_procurement,
        "Social Procurement (BT-775-Lot)",
    )

    # Process BT-776-Lot Procurement of Innovation
    process_bt_section(
        release_json,
        xml_content,
        [parse_procurement_innovation],
        merge_procurement_innovation,
        "Procurement of Innovation (BT-776-Lot)",
    )

    # Process BT-777-Lot Strategic Procurement Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_strategic_procurement_description],
        merge_strategic_procurement_description,
        "Strategic Procurement Description (BT-777-Lot)",
    )

    # Process BT-78-Lot Security Clearance Deadline
    process_bt_section(
        release_json,
        xml_content,
        [parse_security_clearance_deadline],
        merge_security_clearance_deadline,
        "Security Clearance Deadline (BT-78-Lot)",
    )

    # Process BT-79-Lot Performing Staff Qualification
    process_bt_section(
        release_json,
        xml_content,
        [parse_performing_staff_qualification],
        merge_performing_staff_qualification,
        "Performing Staff Qualification (BT-79-Lot)",
    )

    # Process BT-801-Lot Non Disclosure Agreement
    process_bt_section(
        release_json,
        xml_content,
        [parse_non_disclosure_agreement],
        merge_non_disclosure_agreement,
        "Non Disclosure Agreement (BT-801-Lot)",
    )

    # Process BT-802-Lot Non Disclosure Agreement Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_non_disclosure_agreement_description],
        merge_non_disclosure_agreement_description,
        "Non Disclosure Agreement Description (BT-802-Lot)",
    )

    # Process BT-805-Lot Green Procurement Criteria
    process_bt_section(
        release_json,
        xml_content,
        [parse_green_procurement_criteria],
        merge_green_procurement_criteria,
        "Green Procurement Criteria (BT-805-Lot)",
    )

    # Process BT-88-procedure procedure Features
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_features],
        merge_procedure_features,
        "procedure Features (BT-88-procedure)",
    )

    # Process BT-92-Lot Electronic Ordering
    process_bt_section(
        release_json,
        xml_content,
        [parse_electronic_ordering],
        merge_electronic_ordering,
        "Electronic Ordering (BT-92-Lot)",
    )

    # Process BT-93-Lot Electronic Payment
    process_bt_section(
        release_json,
        xml_content,
        [parse_electronic_payment],
        merge_electronic_payment,
        "Electronic Payment (BT-93-Lot)",
    )

    # Process BT-94-Lot Recurrence
    process_bt_section(
        release_json,
        xml_content,
        [parse_recurrence],
        merge_recurrence,
        "Recurrence (BT-94-Lot)",
    )

    # Process BT-95-Lot Recurrence Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_recurrence_description],
        merge_recurrence_description,
        "Recurrence Description (BT-95-Lot)",
    )

    # Process BT-97-Lot Submission Language
    process_bt_section(
        release_json,
        xml_content,
        [parse_submission_language],
        merge_submission_language,
        "Submission Language (BT-97-Lot)",
    )

    # Process BT-98-Lot Tender Validity Deadline
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_validity_deadline],
        merge_tender_validity_deadline,
        "Tender Validity Deadline (BT-98-Lot)",
    )

    # Process BT-99-Lot Review Deadline Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_review_deadline_description],
        merge_review_deadline_description,
        "Review Deadline Description (BT-99-Lot)",
    )

    ################################################################OPP
    ##########################################################################

    # Process OPP-020 ExtendedDurationIndicator
    process_bt_section(
        release_json,
        xml_content,
        [map_extended_duration_indicator],
        merge_extended_duration_indicator,
        "ExtendedDurationIndicator (OPP-020)",
    )

    # Process OPP-021_Contract Essential Assets
    process_bt_section(
        release_json,
        xml_content,
        [map_essential_assets],
        merge_essential_assets,
        "Essential Assets (OPP-021_Contract)",
    )

    # Process OPP_022_Contract Asset Significance
    process_bt_section(
        release_json,
        xml_content,
        [map_asset_significance],
        merge_asset_significance,
        "Asset Significance (OPP_022_Contract)",
    )

    # Process OPP_023_Contract Asset Predominance
    process_bt_section(
        release_json,
        xml_content,
        [map_asset_predominance],
        merge_asset_predominance,
        "Asset Predominance (OPP_023_Contract)",
    )

    # Process OPP-031-Tender Contract Conditions
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_conditions],
        merge_contract_conditions,
        "Contract Conditions (OPP-031-Tender)",
    )

    # Process OPP-032-Tender Revenues Allocation
    process_bt_section(
        release_json,
        xml_content,
        [parse_revenues_allocation],
        merge_revenues_allocation,
        "Revenues Allocation (OPP-032-Tender)",
    )

    # Process OPP-034-Tender Penalties and Rewards
    process_bt_section(
        release_json,
        xml_content,
        [parse_penalties_and_rewards],
        merge_penalties_and_rewards,
        "Penalties and Rewards (OPP-034-Tender)",
    )

    # Process OPP-040-procedure Main Nature - Sub Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_nature_sub_type],
        merge_main_nature_sub_type,
        "Main Nature - Sub Type (OPP-040-procedure)",
    )

    # Process OPP-050-organization buyers Group Lead Indicator
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyers_group_lead_indicator],
        merge_buyers_group_lead_indicator,
        "buyers Group Lead Indicator (OPP-050-organization)",
    )

    # Process OPP-051-organization Awarding CPB buyer Indicator
    process_bt_section(
        release_json,
        xml_content,
        [parse_awarding_cpb_buyer_indicator],
        merge_awarding_cpb_buyer_indicator,
        "Awarding CPB buyer Indicator (OPP-051-organization)",
    )

    # Process OPP-052-organization Acquiring CPB buyer Indicator
    process_bt_section(
        release_json,
        xml_content,
        [parse_acquiring_cpb_buyer_indicator],
        merge_acquiring_cpb_buyer_indicator,
        "Acquiring CPB buyer Indicator (OPP-052-organization)",
    )

    # Process OPP-080-Tender Kilometers Public Transport
    process_bt_section(
        release_json,
        xml_content,
        [parse_kilometers_public_transport],
        merge_kilometers_public_transport,
        "Kilometers Public Transport (OPP-080-Tender)",
    )

    # Process OPP-090-procedure Previous notice Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_previous_notice_identifier],
        merge_previous_notice_identifier,
        "Previous notice Identifier (OPP-090-procedure)",
    )

    # Process OPT-030-procedure-sprovider Provided Service Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_provided_service_type],
        merge_provided_service_type,
        "Provided Service Type (OPT-030-procedure-sprovider)",
    )

    # Process OPP-071-Lot Quality Target Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_quality_target_code],
        merge_quality_target_code,
        "Quality Target Code (OPP-071-Lot)",
    )

    # Process OPP-072-Lot Quality Target Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_quality_target_description],
        merge_quality_target_description,
        "Quality Target Description (OPP-072-Lot)",
    )

    # Process OPP-100-Contract Framework notice Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_notice_identifier],
        merge_framework_notice_identifier,
        "Framework notice Identifier (OPP-100-Contract)",
    )

    # Process OPP-110 and OPP-111 Fiscal Legislation
    process_bt_section(
        release_json,
        xml_content,
        [parse_fiscal_legislation],
        merge_fiscal_legislation,
        "Fiscal Legislation (OPP-110 and OPP-111)",
    )

    # Process OPP-112 and OPP-120 Environmental Legislation
    process_bt_section(
        release_json,
        xml_content,
        [parse_environmental_legislation],
        merge_environmental_legislation,
        "Environmental Legislation (OPP-112 and OPP-120)",
    )

    # Process OPP-113 and OPP-130 Employment Legislation
    process_bt_section(
        release_json,
        xml_content,
        [parse_employment_legislation],
        merge_employment_legislation,
        "Employment Legislation (OPP-113 and OPP-130)",
    )

    # Process OPP-140 Procurement Documents
    process_bt_section(
        release_json,
        xml_content,
        [parse_procurement_documents],
        merge_procurement_documents,
        "Procurement Documents (OPP-140)",
    )

    ################################################################OPT
    ##########################################################################

    # Process OPT-155-LotResult Vehicle Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_vehicle_type],
        merge_vehicle_type,
        "Vehicle Type (OPT-155-LotResult)",
    )

    # Process OPT-156-LotResult Vehicle Numeric
    process_bt_section(
        release_json,
        xml_content,
        [parse_vehicle_numeric],
        merge_vehicle_numeric,
        "Vehicle Numeric (OPT-156-LotResult)",
    )

    # Process OPT-160-ubo First Name
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_first_name],
        merge_ubo_first_name,
        "ubo First Name (OPT-160-ubo)",
    )

    # Process OPT-170-Tenderer Tendering party Leader
    process_bt_section(
        release_json,
        xml_content,
        [parse_tendering_party_leader],
        merge_tendering_party_leader,
        "Tendering party Leader (OPT-170-Tenderer)",
    )

    # Process OPT-200-organization-company organization Technical Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_technical_identifier],
        merge_organization_technical_identifier,
        "organization Technical Identifier (OPT-200-organization-company)",
    )

    # Process OPT-201-organization-touchpoint touchpoint Technical Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_technical_identifier],
        merge_touchpoint_technical_identifier,
        "touchpoint Technical Identifier (OPT-201-organization-touchpoint)",
    )

    # Process OPT-202-ubo
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_identifier],
        merge_ubo_identifier,
        "ubo Identifier (OPT-202-ubo)",
    )

    # Process OPT-300 Contract Signatory
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_signatory],
        merge_contract_signatory,
        "Contract Signatory (OPT-300)",
    )

    # Process OPT-300 sprovider
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_sprovider],
        merge_procedure_sprovider,
        "procedure Service Provider (OPT-300)",
    )

    # Process OPT-301-Lot-AddInfo Additional Info Provider Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_info_provider_identifier],
        merge_additional_info_provider_identifier,
        "Additional Info Provider Technical Identifier Reference (OPT-301-Lot-AddInfo)",
    )

    # Process OPT-301-Lot-DocProvider Document Provider Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_document_provider_identifier],
        merge_document_provider_identifier,
        "Document Provider Technical Identifier Reference (OPT-301-Lot-DocProvider)",
    )

    # Process OPT-301-Lot-EmployLegis Employment Legislation organization Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_employment_legislation_document_reference],
        merge_employment_legislation_document_reference,
        "Employment Legislation organization Technical Identifier Reference (OPT-301-Lot-EmployLegis)",
    )

    # Process OPT-301-Lot-EnvironLegis Environmental Legislation organization Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_environmental_legislation_document_reference],
        merge_environmental_legislation_document_reference,
        "Environmental Legislation organization Technical Identifier Reference (OPT-301-Lot-EnvironLegis)",
    )

    # Process OPT-301-Lot-ReviewOrg Review organization Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_review_org_identifier],
        merge_review_org_identifier,
        "Review organization Technical Identifier Reference (OPT-301-Lot-ReviewOrg)",
    )

    # Process OPT-301-Lot-Mediator Mediator Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_mediator_identifier],
        merge_mediator_identifier,
        "Mediator Technical Identifier Reference (OPT-301-Lot-Mediator)",
    )

    # Process OPT-301-Lot-ReviewInfo Review Info Provider Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_review_info_identifier],
        merge_review_info_identifier,
        "Review Info Provider Technical Identifier Reference (OPT-301-Lot-ReviewInfo)",
    )

    # Process OPT_301_Lot_TenderEval
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_evaluator_identifier],
        merge_tender_evaluator_identifier,
        "Tender Evaluator Identifier (OPT_301_Lot_TenderEval)",
    )

    # Process OPT-301-Lot-TenderReceipt Tender Recipient Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_recipient_identifier],
        merge_tender_recipient_identifier,
        "Tender Recipient Technical Identifier Reference (OPT-301-Lot-TenderReceipt)",
    )

    # Process OPT-301 LotResult_Financing
    process_bt_section(
        release_json,
        xml_content,
        [parse_lotresult_financing],
        merge_lotresult_financing,
        "LotResult Financing (OPT-301)",
    )

    # Process OPT-301 LotResult_Paying
    process_bt_section(
        release_json,
        xml_content,
        [parse_lotresult_paying],
        merge_lotresult_paying,
        "LotResult Paying (OPT-301)",
    )

    # Process OPT-301 part_AddInfo
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_addinfo],
        merge_part_addinfo,
        "part Additional Info (OPT-301)",
    )

    # Process OPT_301_part_DocProvider
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_docprovider],
        merge_part_docprovider,
        "part Document Provider (OPT_301)",
    )

    # Process OPT_301_part_EmployLegis
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_employlegis],
        merge_part_employlegis,
        "part Employment Legislation (OPT_301)",
    )

    # Process OPT_301_part_EnvironLegis
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_environlegis],
        merge_part_environlegis,
        "part Environmental Legislation (OPT_301)",
    )

    # Process OPT_301_part_FiscalLegis
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_fiscallegis],
        merge_part_fiscallegis,
        "part Fiscal Legislation (OPT_301)",
    )

    # Process OPT_301_part_Mediator
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_mediator],
        merge_part_mediator,
        "part Mediator (OPT_301)",
    )

    # Process OPT_301_part_ReviewInfo
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_reviewinfo],
        merge_part_reviewinfo,
        "part Review Info (OPT_301)",
    )

    # Process OPT_301_part_ReviewOrg
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_revieworg],
        merge_part_revieworg,
        "part Review organization (OPT_301)",
    )

    # Process OPT_301_part_TenderEval
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_tendereval],
        merge_part_tendereval,
        "part Tender Evaluator (OPT_301)",
    )

    # Process OPT_301_part_TenderReceipt
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_tenderreceipt],
        merge_part_tenderreceipt,
        "part Tender Recipient (OPT_301)",
    )

    # Process OPT_301_Tenderer_MainCont
    process_bt_section(
        release_json,
        xml_content,
        [parse_tenderer_maincont],
        merge_tenderer_maincont,
        "Tenderer Main Contractor (OPT_301)",
    )
    # add more OPT-301 her

    # Process OPT-302-organization Beneficial Owner Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_beneficial_owner_reference],
        merge_beneficial_owner_reference,
        "Beneficial Owner Reference (OPT-302-organization)",
    )

    # Process OPT-310-Tender Tendering party ID Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_tendering_party_id_reference],
        merge_tendering_party_id_reference,
        "Tendering party ID Reference (OPT-310-Tender)",
    )

    # Process OPT-315-LotResult Contract Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_identifier_reference],
        merge_contract_identifier_reference,
        "Contract Identifier Reference (OPT-315-LotResult)",
    )

    # Process OPT-316-Contract Contract Technical Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_technical_identifier],
        merge_contract_technical_identifier,
        "Contract Technical Identifier (OPT-316-Contract)",
    )

    # Process OPT-320-LotResult Tender Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_tender_identifier_reference],
        merge_tender_identifier_reference,
        "Tender Identifier Reference (OPT-320-LotResult)",
    )

    # Before applying remove_empty_elements and remove_empty_dicts
    # logger.info(f"Release JSON before removing empty elements: {json.dumps(release_json, indent=2)}")

    release_json = remove_empty_elements(release_json)
    # logger.info(f"Release JSON after removing empty elements: {json.dumps(release_json, indent=2)}")

    release_json = remove_empty_dicts(release_json)
    # logger.info(f"Release JSON after removing empty dicts: {json.dumps(release_json, indent=2)}")

    # Before writing to output.json
    # logger.info(f"Final release JSON: {json.dumps(release_json, indent=2)}")

    # Write the JSON output to a file
    output_file = Path("output.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(release_json, f, ensure_ascii=False)

    logger.info("XML to JSON conversion completed")

    # Print the JSON string to console
    # json_string = json.dumps(release_json, ensure_ascii=False)

    return release_json


if __name__ == "__main__":
    # Path to the XML file
    # xml_path = "xmlfile/2022-319091.xml"
    xml_path = "bt_198-106.xml"
    # Prefix for OCID
    ocid_prefix = "ocid_prefix_value"

    main(xml_path, ocid_prefix)
