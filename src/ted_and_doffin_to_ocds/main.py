# main.py
import json
import logging
from ted_and_doffin_to_ocds.converters.Common_operations import NoticeProcessor
from ted_and_doffin_to_ocds.converters.BT_01_Procedure import (
    parse_procedure_legal_basis,
    merge_procedure_legal_basis,
)
from ted_and_doffin_to_ocds.converters.BT_03 import parse_form_type, merge_form_type
from ted_and_doffin_to_ocds.converters.BT_04_Procedure import (
    parse_procedure_identifier,
    merge_procedure_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_05_notice import (
    parse_notice_dispatch_date_time,
    merge_notice_dispatch_date_time,
)
from ted_and_doffin_to_ocds.converters.BT_06_Lot import (
    parse_strategic_procurement,
    merge_strategic_procurement,
)
from ted_and_doffin_to_ocds.converters.BT_09_Procedure import (
    parse_cross_border_law,
    merge_cross_border_law,
)
from ted_and_doffin_to_ocds.converters.BT_10 import (
    parse_contract_xml,
    merge_contract_info,
)
from ted_and_doffin_to_ocds.converters.BT_11_Procedure_Buyer import (
    parse_buyer_legal_type,
    merge_buyer_legal_type,
)
from ted_and_doffin_to_ocds.converters.BT_88_Procedure import (
    parse_procedure_features,
    merge_procedure_features,
)
from ted_and_doffin_to_ocds.converters.BT_105_Procedure import (
    parse_procedure_type,
    merge_procedure_type,
)
from ted_and_doffin_to_ocds.converters.BT_106_Procedure import (
    parse_procedure_accelerated,
    merge_procedure_accelerated,
)
from ted_and_doffin_to_ocds.converters.BT_109_Lot import (
    parse_framework_duration_justification,
    merge_framework_duration_justification,
)
from ted_and_doffin_to_ocds.converters.BT_111_Lot import (
    parse_framework_buyer_categories,
    merge_framework_buyer_categories,
)
from ted_and_doffin_to_ocds.converters.BT_113_Lot import (
    parse_framework_max_participants,
    merge_framework_max_participants,
)
from ted_and_doffin_to_ocds.converters.BT_115_GPA_Coverage import (
    parse_gpa_coverage,
    merge_gpa_coverage,
)
from ted_and_doffin_to_ocds.converters.BT_13713_LotResult import (
    parse_lot_result_identifier,
    merge_lot_result_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_13714_Tender import (
    parse_tender_lot_identifier,
    merge_tender_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_1375_Procedure import (
    parse_group_lot_identifier,
    merge_group_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_119_LotResult import (
    parse_dps_termination,
    merge_dps_termination,
)
from ted_and_doffin_to_ocds.converters.BT_120_Lot import (
    parse_no_negotiation_necessary,
    merge_no_negotiation_necessary,
)
from ted_and_doffin_to_ocds.converters.BT_122_Lot import (
    parse_electronic_auction_description,
    merge_electronic_auction_description,
)
from ted_and_doffin_to_ocds.converters.BT_123_Lot import (
    parse_electronic_auction_url,
    merge_electronic_auction_url,
)
from ted_and_doffin_to_ocds.converters.BT_124_Tool_Atypical_URL import (
    parse_tool_atypical_url,
    merge_tool_atypical_url,
)
from ted_and_doffin_to_ocds.converters.BT_125_Lot import (
    parse_previous_planning_identifier_lot,
    merge_previous_planning_identifier_lot,
)
from ted_and_doffin_to_ocds.converters.BT_125_Part import (
    parse_previous_planning_identifier_part,
    merge_previous_planning_identifier_part,
)
from ted_and_doffin_to_ocds.converters.BT_1252_Procedure import (
    parse_direct_award_justification,
    merge_direct_award_justification,
)
from ted_and_doffin_to_ocds.converters.BT_127_notice import (
    parse_future_notice_date,
    merge_future_notice_date,
)
from ted_and_doffin_to_ocds.converters.BT_13_Lot import (
    parse_additional_info_deadline,
    merge_additional_info_deadline,
)
from ted_and_doffin_to_ocds.converters.BT_13_Part import (
    parse_additional_info_deadline_part,
    merge_additional_info_deadline_part,
)
from ted_and_doffin_to_ocds.converters.BT_130_Lot import (
    parse_dispatch_invitation_tender,
    merge_dispatch_invitation_tender,
)
from ted_and_doffin_to_ocds.converters.BT_131_Lot import (
    parse_deadline_receipt_tenders,
    merge_deadline_receipt_tenders,
)
from ted_and_doffin_to_ocds.converters.BT_1311_Lot import (
    parse_deadline_receipt_requests,
    merge_deadline_receipt_requests,
)
from ted_and_doffin_to_ocds.converters.BT_132_Lot import (
    parse_lot_public_opening_date,
    merge_lot_public_opening_date,
)
from ted_and_doffin_to_ocds.converters.BT_133_Lot import (
    parse_lot_bid_opening_location,
    merge_lot_bid_opening_location,
)
from ted_and_doffin_to_ocds.converters.BT_134_Lot import (
    parse_lot_public_opening_description,
    merge_lot_public_opening_description,
)
from ted_and_doffin_to_ocds.converters.BT_135_Procedure import (
    parse_direct_award_justification_rationale,
    merge_direct_award_justification_rationale,
)
from ted_and_doffin_to_ocds.converters.BT_1351_Procedure import (
    parse_accelerated_procedure_justification,
    merge_accelerated_procedure_justification,
)
from ted_and_doffin_to_ocds.converters.BT_136_Procedure import (
    parse_direct_award_justification_code,
    merge_direct_award_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_137_Lot import (
    parse_purpose_lot_identifier,
    merge_purpose_lot_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_137_LotsGroup import (
    parse_lots_group_identifier,
    merge_lots_group_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_137_Part import (
    parse_part_identifier,
    merge_part_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_14_Lot import (
    parse_lot_documents_restricted,
    merge_lot_documents_restricted,
)
from ted_and_doffin_to_ocds.converters.BT_14_Part import (
    parse_part_documents_restricted,
    merge_part_documents_restricted,
)
from ted_and_doffin_to_ocds.converters.BT_140_notice import (
    parse_change_reason_code,
    merge_change_reason_code,
)
from ted_and_doffin_to_ocds.converters.BT_142_LotResult import (
    parse_winner_chosen,
    merge_winner_chosen,
)
from ted_and_doffin_to_ocds.converters.BT_144_LotResult import (
    parse_not_awarded_reason,
    merge_not_awarded_reason,
)
from ted_and_doffin_to_ocds.converters.BT_145_Contract import (
    parse_contract_conclusion_date,
    merge_contract_conclusion_date,
)
from ted_and_doffin_to_ocds.converters.BT_1451_Contract import (
    parse_winner_decision_date,
    merge_winner_decision_date,
)
from ted_and_doffin_to_ocds.converters.BT_15_Lot_Part import (
    parse_documents_url,
    merge_documents_url,
)
from ted_and_doffin_to_ocds.converters.BT_150_Contract import (
    parse_contract_identifier,
    merge_contract_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_151_Contract import (
    parse_contract_url,
    merge_contract_url,
)
from ted_and_doffin_to_ocds.converters.BT_16_Organization_Company import (
    parse_organization_part_name,
    merge_organization_part_name,
)
from ted_and_doffin_to_ocds.converters.BT_16_Organization_TouchPoint import (
    parse_organization_touchpoint_part_name,
    merge_organization_touchpoint_part_name,
)
from ted_and_doffin_to_ocds.converters.BT_160_Tender import (
    parse_concession_revenue_buyer,
    merge_concession_revenue_buyer,
)
from ted_and_doffin_to_ocds.converters.BT_162_Tender import (
    parse_concession_revenue_user,
    merge_concession_revenue_user,
)
from ted_and_doffin_to_ocds.converters.BT_163_Tender import (
    parse_concession_value_description,
    merge_concession_value_description,
)
from ted_and_doffin_to_ocds.converters.BT_165_Organization_Company import (
    parse_winner_size,
    merge_winner_size,
)
from ted_and_doffin_to_ocds.converters.BT_17_Lot import (
    parse_submission_electronic,
    merge_submission_electronic,
)
from ted_and_doffin_to_ocds.converters.BT_171_Tender import (
    parse_tender_rank,
    merge_tender_rank,
)
from ted_and_doffin_to_ocds.converters.BT_1711_Tender import (
    parse_tender_ranked,
    merge_tender_ranked,
)
from ted_and_doffin_to_ocds.converters.BT_18_Lot import (
    parse_submission_url,
    merge_submission_url,
)
from ted_and_doffin_to_ocds.converters.BT_19_Lot import (
    parse_submission_nonelectronic_justification,
    merge_submission_nonelectronic_justification,
)
from ted_and_doffin_to_ocds.converters.BT_191_Tender import (
    parse_country_origin,
    merge_country_origin,
)
from ted_and_doffin_to_ocds.converters.BT_193_Tender import (
    parse_tender_variant,
    merge_tender_variant,
)
from ted_and_doffin_to_ocds.converters.BT_539_LotsGroup import (
    parse_award_criterion_type_lots_group,
    merge_award_criterion_type_lots_group,
)
from ted_and_doffin_to_ocds.converters.BT_5421_Lot import (
    parse_award_criterion_number_weight_lot,
    merge_award_criterion_number_weight_lot,
)
from ted_and_doffin_to_ocds.converters.BT_5421_LotsGroup import (
    parse_award_criterion_number_weight_lots_group,
    merge_award_criterion_number_weight_lots_group,
)
from ted_and_doffin_to_ocds.converters.BT_5422_Lot import (
    parse_award_criterion_number_fixed,
    merge_award_criterion_number_fixed,
)
from ted_and_doffin_to_ocds.converters.BT_5422_LotsGroup import (
    parse_award_criterion_number_fixed_lotsgroup,
    merge_award_criterion_number_fixed_lotsgroup,
)


# BT_195
from ted_and_doffin_to_ocds.converters.BT_195_BT_09_Procedure import (
    bt_195_parse_unpublished_identifier_bt_09_procedure,
    bt_195_merge_unpublished_identifier_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_105_Procedure import (
    parse_bt195_bt105_unpublished_identifier,
    merge_bt195_bt105_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_106_Procedure import (
    parse_bt195_bt106_unpublished_identifier,
    merge_bt195_bt106_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_1252_Procedure import (
    parse_bt195_bt1252_unpublished_identifier,
    merge_bt195_bt1252_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_135_Procedure import (
    parse_bt195_bt135_unpublished_identifier,
    merge_bt195_bt135_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_1351_Procedure import (
    parse_bt195_bt1351_unpublished_identifier,
    merge_bt195_bt1351_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_136_Procedure import (
    parse_bt195_bt136_unpublished_identifier,
    merge_bt195_bt136_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_142_LotResult import (
    parse_bt195_bt142_unpublished_identifier,
    merge_bt195_bt142_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_144_LotResult import (
    parse_bt195_bt144_unpublished_identifier,
    merge_bt195_bt144_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_160_Tender import (
    parse_bt195_bt160_unpublished_identifier,
    merge_bt195_bt160_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_162_Tender import (
    parse_bt195_bt162_unpublished_identifier,
    merge_bt195_bt162_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_163_Tender import (
    parse_bt195_bt163_unpublished_identifier,
    merge_bt195_bt163_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_171_Tender import (
    parse_bt195_bt171_unpublished_identifier,
    merge_bt195_bt171_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_191_Tender import (
    parse_bt195_bt191_unpublished_identifier,
    merge_bt195_bt191_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_193_Tender import (
    parse_bt195_bt193_unpublished_identifier,
    merge_bt195_bt193_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_539_Lot import (
    parse_bt195_bt539_unpublished_identifier,
    merge_bt195_bt539_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_539_LotsGroup import (
    parse_bt195_bt539_lotsgroup_unpublished_identifier,
    merge_bt195_bt539_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_540_Lot import (
    parse_bt195_bt540_lot_unpublished_identifier,
    merge_bt195_bt540_lot_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_540_LotsGroup import (
    parse_bt195_bt540_lotsgroup_unpublished_identifier,
    merge_bt195_bt540_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_541_Lot_Fixed import (
    parse_bt195_bt541_lot_fixed_unpublished_identifier,
    merge_bt195_bt541_lot_fixed_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_541_Lot_Threshold import (
    parse_bt195_bt541_lot_threshold_unpublished_identifier,
    merge_bt195_bt541_lot_threshold_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_541_Lot_Weight import (
    parse_bt195_bt541_lot_weight_unpublished_identifier,
    merge_bt195_bt541_lot_weight_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_541_LotsGroup_Fixed import (
    parse_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
    merge_bt195_bt541_lotsgroup_fixed_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_541_LotsGroup_Threshold import (
    parse_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
    merge_bt195_bt541_lotsgroup_threshold_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_541_LotsGroup_Weight import (
    parse_bt195_bt541_lotsgroup_weight,
    merge_bt195_bt541_lotsgroup_weight,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_5421_Lot import (
    parse_bt195_bt5421_lot,
    merge_bt195_bt5421_lot,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_5421_LotsGroup import (
    parse_bt195_bt5421_lotsgroup,
    merge_bt195_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_5422_Lot import (
    parse_bt195_bt5422_lot,
    merge_bt195_bt5422_lot,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_5422_LotsGroup import (
    parse_bt195_bt5422_lotsgroup,
    merge_bt195_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_5423_Lot import (
    parse_bt195_bt5423_lot,
    merge_bt195_bt5423_lot,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_5423_LotsGroup import (
    parse_bt195_bt5423_lotsgroup,
    merge_bt195_bt5423_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_543_Lot import (
    parse_bt195_bt543_lot,
    merge_bt195_bt543_lot,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_543_LotsGroup import (
    parse_bt195_bt543_lotsgroup,
    merge_bt195_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_553_Tender import (
    parse_bt195_bt553_tender,
    merge_bt195_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_554_Tender import (
    parse_bt195_bt554_unpublished_identifier,
    merge_bt195_bt554_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_555_Tender import (
    parse_bt195_bt555_unpublished_identifier,
    merge_bt195_bt555_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_635_LotResult import (
    parse_bt195_bt635_unpublished_identifier,
    merge_bt195_bt635_unpublished_identifier,
)

from ted_and_doffin_to_ocds.converters.BT_195_BT_636_LotResult import (
    parse_bt195_bt636_unpublished_identifier,
    merge_bt195_bt636_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_660_LotResult import (
    parse_bt195_bt660_unpublished_identifier,
    merge_bt195_bt660_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_709_LotResult import (
    parse_bt195_bt709_unpublished_identifier,
    merge_bt195_bt709_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_710_LotResult import (
    parse_bt195_bt710_unpublished_identifier,
    merge_bt195_bt710_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_711_LotResult import (
    parse_bt195_bt711_unpublished_identifier,
    merge_bt195_bt711_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_712_LotResult import (
    parse_bt195_bt712_unpublished_identifier,
    merge_bt195_bt712_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_720_Tender import (
    parse_bt195_bt720_unpublished_identifier,
    merge_bt195_bt720_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_733_Lot import (
    parse_bt195_bt733_unpublished_identifier,
    merge_bt195_bt733_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_733_LotsGroup import (
    parse_bt195_bt733_lotsgroup_unpublished_identifier,
    merge_bt195_bt733_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_734_Lot import (
    parse_bt195_bt734_lot_unpublished_identifier,
    merge_bt195_bt734_lot_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_734_LotsGroup import (
    parse_bt195_bt734_lotsgroup_unpublished_identifier,
    merge_bt195_bt734_lotsgroup_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_759_LotResult import (
    parse_bt195_bt759_lotresult_unpublished_identifier,
    merge_bt195_bt759_lotresult_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_760_LotResult import (
    parse_bt195_bt760_lotresult_unpublished_identifier,
    merge_bt195_bt760_lotresult_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_773_Tender import (
    parse_bt195_bt773_tender_unpublished_identifier,
    merge_bt195_bt773_tender_unpublished_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_195_BT_88_Procedure import (
    parse_bt195_bt88_procedure_unpublished_identifier,
    merge_bt195_bt88_procedure_unpublished_identifier,
)

# BT_196
from ted_and_doffin_to_ocds.converters.BT_196_BT_09_Procedure import (
    bt_196_parse_unpublished_justification_bt_09_procedure,
    bt_196_merge_unpublished_justification_bt_09_procedure,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_105_Procedure import (
    parse_bt196_bt105_unpublished_justification,
    merge_bt196_bt105_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_106_Procedure import (
    parse_bt196_bt106_unpublished_justification,
    merge_bt196_bt106_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_1252_Procedure import (
    parse_bt196_bt1252_unpublished_justification,
    merge_bt196_bt1252_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_135_Procedure import (
    parse_bt196_bt135_unpublished_justification,
    merge_bt196_bt135_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_1351_Procedure import (
    parse_bt196_bt1351_unpublished_justification,
    merge_bt196_bt1351_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_136_Procedure import (
    parse_bt196_bt136_unpublished_justification,
    merge_bt196_bt136_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_142_LotResult import (
    parse_bt196_bt142_unpublished_justification,
    merge_bt196_bt142_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_144_LotResult import (
    parse_bt196_bt144_unpublished_justification,
    merge_bt196_bt144_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_160_Tender import (
    parse_bt196_bt160_unpublished_justification,
    merge_bt196_bt160_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_162_Tender import (
    parse_bt196_bt162_unpublished_justification,
    merge_bt196_bt162_unpublished_justification,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_163_Tender import (
    parse_bt196_bt163_unpublished_justification,
    merge_bt196_bt163_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_171_Tender import (
    parse_bt196_bt171_unpublished_justification,
    merge_bt196_bt171_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_191_Tender import (
    parse_bt196_bt191_unpublished_justification,
    merge_bt196_bt191_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_193_Tender import (
    parse_bt196_bt193_unpublished_justification,
    merge_bt196_bt193_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_539_Lot import (
    parse_bt196_bt539_unpublished_justification,
    merge_bt196_bt539_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_539_LotsGroup import (
    parse_bt196_bt539_lotsgroup_unpublished_justification,
    merge_bt196_bt539_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_540_Lot import (
    parse_bt196_bt540_lot_unpublished_justification,
    merge_bt196_bt540_lot_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_540_LotsGroup import (
    parse_bt196_bt540_lotsgroup_unpublished_justification,
    merge_bt196_bt540_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_541_Lot_Fixed import (
    parse_bt196_bt541_lot_fixed_unpublished_justification,
    merge_bt196_bt541_lot_fixed_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_541_Lot_Threshold import (
    parse_bt196_bt541_lot_threshold_unpublished_justification,
    merge_bt196_bt541_lot_threshold_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_541_Lot_Weight import (
    parse_bt196_bt541_lot_weight_unpublished_justification,
    merge_bt196_bt541_lot_weight_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_541_LotsGroup_Fixed import (
    parse_bt196_bt541_lotsgroup_fixed_unpublished_justification,
    merge_bt196_bt541_lotsgroup_fixed_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_541_LotsGroup_Threshold import (
    parse_bt196_bt541_lotsgroup_threshold_unpublished_justification,
    merge_bt196_bt541_lotsgroup_threshold_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_541_LotsGroup_Weight import (
    parse_bt196_bt541_lotsgroup_weight,
    merge_bt196_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_5421_Lot import (
    parse_bt196_bt5421_lot,
    merge_bt196_bt5421_lot,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_5421_LotsGroup import (
    parse_bt196_bt5421_lotsgroup,
    merge_bt196_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_5422_Lot import (
    parse_bt196_bt5422_lot,
    merge_bt196_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_5422_LotsGroup import (
    parse_bt196_bt5422_lotsgroup,
    merge_bt196_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_5423_Lot import (
    parse_bt196_bt5423_lot,
    merge_bt196_bt5423_lot,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_5423_LotsGroup import (
    parse_bt196_bt5423_lotsgroup,
    merge_bt196_bt5423_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_543_Lot import (
    parse_bt196_bt543_lot,
    merge_bt196_bt543_lot,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_543_LotsGroup import (
    parse_bt196_bt543_lotsgroup,
    merge_bt196_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_553_Tender import (
    parse_bt196_bt553_tender,
    merge_bt196_bt553_tender,
)

from ted_and_doffin_to_ocds.converters.BT_196_BT_554_Tender import (
    parse_bt196_bt554_unpublished_justification,
    merge_bt196_bt554_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_555_Tender import (
    parse_bt196_bt555_unpublished_justification,
    merge_bt196_bt555_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_635_LotResult import (
    parse_bt196_bt635_unpublished_justification,
    merge_bt196_bt635_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_636_LotResult import (
    parse_bt196_bt636_unpublished_justification,
    merge_bt196_bt636_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_660_LotResult import (
    parse_bt196_bt660_unpublished_justification,
    merge_bt196_bt660_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_709_LotResult import (
    parse_bt196_bt709_unpublished_justification,
    merge_bt196_bt709_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_710_LotResult import (
    parse_bt196_bt710_unpublished_justification,
    merge_bt196_bt710_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_711_LotResult import (
    parse_bt196_bt711_unpublished_justification,
    merge_bt196_bt711_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_712_LotResult import (
    parse_bt196_bt712_unpublished_justification,
    merge_bt196_bt712_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_720_Tender import (
    parse_bt196_bt720_unpublished_justification,
    merge_bt196_bt720_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_733_Lot import (
    parse_bt196_bt733_unpublished_justification,
    merge_bt196_bt733_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_733_LotsGroup import (
    parse_bt196_bt733_lotsgroup_unpublished_justification,
    merge_bt196_bt733_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_734_Lot import (
    parse_bt196_bt734_lot_unpublished_justification,
    merge_bt196_bt734_lot_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_734_LotsGroup import (
    parse_bt196_bt734_lotsgroup_unpublished_justification,
    merge_bt196_bt734_lotsgroup_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_759_LotResult import (
    parse_bt196_bt759_lotresult_unpublished_justification,
    merge_bt196_bt759_lotresult_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_760_LotResult import (
    parse_bt196_bt760_lotresult_unpublished_justification,
    merge_bt196_bt760_lotresult_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_773_Tender import (
    parse_bt196_bt773_tender_unpublished_justification,
    merge_bt196_bt773_tender_unpublished_justification,
)
from ted_and_doffin_to_ocds.converters.BT_196_BT_88_Procedure import (
    parse_bt196_bt88_procedure_unpublished_justification,
    merge_bt196_bt88_procedure_unpublished_justification,
)

# #BT_197
from ted_and_doffin_to_ocds.converters.BT_197_BT_09_Procedure import (
    bt_197_parse_unpublished_justification_code_bt_09_procedure,
    bt_197_merge_unpublished_justification_code_bt_09_procedure,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_105_Procedure import (
    parse_bt197_bt105_unpublished_justification_code,
    merge_bt197_bt105_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_106_Procedure import (
    parse_bt197_bt106_unpublished_justification_code,
    merge_bt197_bt106_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_1252_Procedure import (
    parse_bt197_bt1252_unpublished_justification_code,
    merge_bt197_bt1252_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_135_Procedure import (
    parse_bt197_bt135_unpublished_justification_code,
    merge_bt197_bt135_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_1351_Procedure import (
    parse_bt197_bt1351_unpublished_justification_code,
    merge_bt197_bt1351_unpublished_justification_code,
)


from ted_and_doffin_to_ocds.converters.BT_197_BT_136_Procedure import (
    parse_bt197_bt136_unpublished_justification_code,
    merge_bt197_bt136_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_142_LotResult import (
    parse_bt197_bt142_unpublished_justification_code,
    merge_bt197_bt142_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_144_LotResult import (
    parse_bt197_bt144_unpublished_justification_code,
    merge_bt197_bt144_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_160_Tender import (
    parse_bt197_bt160_unpublished_justification_code,
    merge_bt197_bt160_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_162_Tender import (
    parse_bt197_bt162_unpublished_justification_code,
    merge_bt197_bt162_unpublished_justification_code,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_163_Tender import (
    parse_bt197_bt163_unpublished_justification_code,
    merge_bt197_bt163_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_171_Tender import (
    parse_bt197_bt171_unpublished_justification_code,
    merge_bt197_bt171_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_191_Tender import (
    parse_bt197_bt191_unpublished_justification_code,
    merge_bt197_bt191_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_193_Tender import (
    parse_bt197_bt193_unpublished_justification_code,
    merge_bt197_bt193_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_539_Lot import (
    parse_bt197_bt539_unpublished_justification_code,
    merge_bt197_bt539_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_539_LotsGroup import (
    parse_bt197_bt539_lotsgroup_unpublished_justification_code,
    merge_bt197_bt539_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_540_Lot import (
    parse_bt197_bt540_lot_unpublished_justification_code,
    merge_bt197_bt540_lot_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_540_LotsGroup import (
    parse_bt197_bt540_lotsgroup_unpublished_justification_code,
    merge_bt197_bt540_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_541_Lot_Fixed import (
    parse_bt197_bt541_lot_fixed_unpublished_justification_code,
    merge_bt197_bt541_lot_fixed_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_541_Lot_Threshold import (
    parse_bt197_bt541_lot_threshold_unpublished_justification_code,
    merge_bt197_bt541_lot_threshold_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_541_Lot_Weight import (
    parse_bt197_bt541_lot_weight_unpublished_justification_code,
    merge_bt197_bt541_lot_weight_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_541_LotsGroup_Fixed import (
    parse_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
    merge_bt197_bt541_lotsgroup_fixed_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_541_LotsGroup import (
    parse_bt197_bt541_lotsgroup_threshold,
    merge_bt197_bt541_lotsgroup_threshold,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_541_LotsGroup_Weight import (
    parse_bt197_bt541_lotsgroup_weight,
    merge_bt197_bt541_lotsgroup_weight,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_5421_Lot import (
    parse_bt197_bt5421_lot,
    merge_bt197_bt5421_lot,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_5421_LotsGroup import (
    parse_bt197_bt5421_lotsgroup,
    merge_bt197_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_5422_Lot import (
    parse_bt197_bt5422_lot,
    merge_bt197_bt5422_lot,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_5422_LotsGroup import (
    parse_bt197_bt5422_lotsgroup,
    merge_bt197_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_197_BT_5423_Lot import (
    parse_bt197_bt5423_lot,
    merge_bt197_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_5423_LotsGroup import (
    parse_bt197_bt5423_lotsgroup,
    merge_bt197_bt5423_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_543_Lot import (
    parse_bt197_bt543_lot,
    merge_bt197_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_543_LotsGroup import (
    parse_bt197_bt543_lotsgroup,
    merge_bt197_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_553_Tender import (
    parse_bt197_bt553_tender,
    merge_bt197_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_554_Tender import (
    parse_bt197_bt554_unpublished_justification_code,
    merge_bt197_bt554_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_555_Tender import (
    parse_bt197_bt555_unpublished_justification_code,
    merge_bt197_bt555_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_635_LotResult import (
    parse_bt197_bt635_unpublished_justification_code,
    merge_bt197_bt635_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_636_LotResult import (
    parse_bt197_bt636_unpublished_justification_code,
    merge_bt197_bt636_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_660_LotResult import (
    parse_bt197_bt660_unpublished_justification_code,
    merge_bt197_bt660_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_709_LotResult import (
    parse_bt197_bt709_unpublished_justification_code,
    merge_bt197_bt709_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_710_LotResult import (
    parse_bt197_bt710_unpublished_justification_code,
    merge_bt197_bt710_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_711_LotResult import (
    parse_bt197_bt711_unpublished_justification_code,
    merge_bt197_bt711_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_712_LotResult import (
    parse_bt197_bt712_unpublished_justification_code,
    merge_bt197_bt712_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_720_Tender import (
    parse_bt197_bt720_unpublished_justification_code,
    merge_bt197_bt720_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_733_Lot import (
    parse_bt197_bt733_unpublished_justification_code,
    merge_bt197_bt733_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_733_LotsGroup import (
    parse_bt197_bt733_lotsgroup_unpublished_justification_code,
    merge_bt197_bt733_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_734_Lot import (
    parse_bt197_bt734_lot_unpublished_justification_code,
    merge_bt197_bt734_lot_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_734_LotsGroup import (
    parse_bt197_bt734_lotsgroup_unpublished_justification_code,
    merge_bt197_bt734_lotsgroup_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_759_LotResult import (
    parse_bt197_bt759_lotresult_unpublished_justification_code,
    merge_bt197_bt759_lotresult_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_760_LotResult import (
    parse_bt197_bt760_lotresult_unpublished_justification_code,
    merge_bt197_bt760_lotresult_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_773_Tender import (
    parse_bt197_bt773_tender_unpublished_justification_code,
    merge_bt197_bt773_tender_unpublished_justification_code,
)
from ted_and_doffin_to_ocds.converters.BT_197_BT_88_Procedure import (
    parse_bt197_bt88_procedure_unpublished_justification_code,
    merge_bt197_bt88_procedure_unpublished_justification_code,
)

#
# #BT_198
from ted_and_doffin_to_ocds.converters.BT_198_BT_09_Procedure import (
    bt_198_parse_unpublished_access_date_bt_09_procedure,
    bt_198_merge_unpublished_access_date_bt_09_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_105_Procedure import (
    parse_bt198_bt105_unpublished_access_date,
    merge_bt198_bt105_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_106_Procedure import (
    parse_bt198_bt106_unpublished_access_date,
    merge_bt198_bt106_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_1252_Procedure import (
    parse_bt198_bt1252_unpublished_access_date,
    merge_bt198_bt1252_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_135_Procedure import (
    parse_bt198_bt135_unpublished_access_date,
    merge_bt198_bt135_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_1351_Procedure import (
    parse_bt198_bt1351_unpublished_access_date,
    merge_bt198_bt1351_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_136_Procedure import (
    parse_bt198_bt136_unpublished_access_date,
    merge_bt198_bt136_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_142_LotResult import (
    parse_bt198_bt142_unpublished_access_date,
    merge_bt198_bt142_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_144_LotResult import (
    parse_bt198_bt144_unpublished_access_date,
    merge_bt198_bt144_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_160_Tender import (
    parse_bt198_bt160_unpublished_access_date,
    merge_bt198_bt160_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_162_Tender import (
    parse_bt198_bt162_unpublished_access_date,
    merge_bt198_bt162_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_163_Tender import (
    parse_bt198_bt163_unpublished_access_date,
    merge_bt198_bt163_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_171_Tender import (
    parse_bt198_bt171_unpublished_access_date,
    merge_bt198_bt171_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_191_Tender import (
    parse_bt198_bt191_unpublished_access_date,
    merge_bt198_bt191_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_193_Tender import (
    parse_bt198_bt193_unpublished_access_date,
    merge_bt198_bt193_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_539_Lot import (
    parse_bt198_bt539_unpublished_access_date,
    merge_bt198_bt539_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_539_LotsGroup import (
    parse_bt198_bt539_lotsgroup_unpublished_access_date,
    merge_bt198_bt539_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_540_Lot import (
    parse_bt198_bt540_lot_unpublished_access_date,
    merge_bt198_bt540_lot_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_540_LotsGroup import (
    parse_bt198_bt540_lotsgroup_unpublished_access_date,
    merge_bt198_bt540_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_541_Lot_Fixed import (
    parse_bt198_bt541_lot_fixed_unpublished_access_date,
    merge_bt198_bt541_lot_fixed_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_541_Lot_Threshold import (
    parse_bt198_bt541_lot_threshold_unpublished_access_date,
    merge_bt198_bt541_lot_threshold_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_541_Lot_Weight import (
    parse_bt198_bt541_lot_weight_unpublished_access_date,
    merge_bt198_bt541_lot_weight_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_541_LotsGroup_Fixed import (
    parse_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
    merge_bt198_bt541_lotsgroup_fixed_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_541_LotsGroup import (
    parse_bt198_bt541_lotsgroup_threshold,
    merge_bt198_bt541_lotsgroup_threshold,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_541_LotsGroup_Weight import (
    parse_bt198_bt541_lotsgroup_weight,
    merge_bt198_bt541_lotsgroup_weight,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_5421_Lot import (
    parse_bt198_bt5421_lot,
    merge_bt198_bt5421_lot,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_5421_LotsGroup import (
    parse_bt198_bt5421_lotsgroup,
    merge_bt198_bt5421_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_5422_Lot import (
    parse_bt198_bt5422_lot,
    merge_bt198_bt5422_lot,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_5422_LotsGroup import (
    parse_bt198_bt5422_lotsgroup,
    merge_bt198_bt5422_lotsgroup,
)

from ted_and_doffin_to_ocds.converters.BT_198_BT_5423_Lot import (
    parse_bt198_bt5423_lot,
    merge_bt198_bt5423_lot,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_5423_LotsGroup import (
    parse_bt198_bt5423_lotsgroup,
    merge_bt198_bt5423_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_543_Lot import (
    parse_bt198_bt543_lot,
    merge_bt198_bt543_lot,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_543_LotsGroup import (
    parse_bt198_bt543_lotsgroup,
    merge_bt198_bt543_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_553_Tender import (
    parse_bt198_bt553_tender,
    merge_bt198_bt553_tender,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_554_Tender import (
    parse_bt198_bt554_unpublished_access_date,
    merge_bt198_bt554_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_555_Tender import (
    parse_bt198_bt555_unpublished_access_date,
    merge_bt198_bt555_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_635_LotResult import (
    parse_bt198_bt635_unpublished_access_date,
    merge_bt198_bt635_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_636_LotResult import (
    parse_bt198_bt636_unpublished_access_date,
    merge_bt198_bt636_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_660_LotResult import (
    parse_bt198_bt660_unpublished_access_date,
    merge_bt198_bt660_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_709_LotResult import (
    parse_bt198_bt709_unpublished_access_date,
    merge_bt198_bt709_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_710_LotResult import (
    parse_bt198_bt710_unpublished_access_date,
    merge_bt198_bt710_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_711_LotResult import (
    parse_bt198_bt711_unpublished_access_date,
    merge_bt198_bt711_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_712_LotResult import (
    parse_bt198_bt712_unpublished_access_date,
    merge_bt198_bt712_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_720_Tender import (
    parse_bt198_bt720_unpublished_access_date,
    merge_bt198_bt720_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_733_Lot import (
    parse_bt198_bt733_unpublished_access_date,
    merge_bt198_bt733_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_733_LotsGroup import (
    parse_bt198_bt733_lotsgroup_unpublished_access_date,
    merge_bt198_bt733_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_734_Lot import (
    parse_bt198_bt734_lot_unpublished_access_date,
    merge_bt198_bt734_lot_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_734_LotsGroup import (
    parse_bt198_bt734_lotsgroup_unpublished_access_date,
    merge_bt198_bt734_lotsgroup_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_759_LotResult import (
    parse_bt198_bt759_lotresult_unpublished_access_date,
    merge_bt198_bt759_lotresult_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_760_LotResult import (
    parse_bt198_bt760_lotresult_unpublished_access_date,
    merge_bt198_bt760_lotresult_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_773_Tender import (
    parse_bt198_bt773_tender_unpublished_access_date,
    merge_bt198_bt773_tender_unpublished_access_date,
)
from ted_and_doffin_to_ocds.converters.BT_198_BT_88_Procedure import (
    parse_bt198_bt88_procedure_unpublished_access_date,
    merge_bt198_bt88_procedure_unpublished_access_date,
)

from ted_and_doffin_to_ocds.converters.BT_200_Contract import (
    parse_contract_modification_reason,
    merge_contract_modification_reason,
)
from ted_and_doffin_to_ocds.converters.BT_201_Contract import (
    parse_contract_modification_description,
    merge_contract_modification_description,
)
from ted_and_doffin_to_ocds.converters.BT_202_Contract import (
    parse_contract_modification_summary,
    merge_contract_modification_summary,
)
from ted_and_doffin_to_ocds.converters.BT_21_Lot import parse_lot_title, merge_lot_title
from ted_and_doffin_to_ocds.converters.BT_21_LotsGroup import (
    parse_lots_group_title,
    merge_lots_group_title,
)
from ted_and_doffin_to_ocds.converters.BT_21_Part import (
    parse_part_title,
    merge_part_title,
)
from ted_and_doffin_to_ocds.converters.BT_21_Procedure import (
    parse_procedure_title,
    merge_procedure_title,
)
from ted_and_doffin_to_ocds.converters.BT_22_Lot import (
    parse_lot_internal_identifier,
    merge_lot_internal_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_23_Lot import (
    parse_main_nature,
    merge_main_nature,
)
from ted_and_doffin_to_ocds.converters.BT_23_Part import (
    parse_main_nature_part,
    merge_main_nature_part,
)
from ted_and_doffin_to_ocds.converters.BT_23_Procedure import (
    parse_main_nature_procedure,
    merge_main_nature_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_24_Lot import (
    parse_lot_description,
    merge_lot_description,
)
from ted_and_doffin_to_ocds.converters.BT_24_LotsGroup import (
    parse_lots_group_description,
    merge_lots_group_description,
)
from ted_and_doffin_to_ocds.converters.BT_24_Part import (
    parse_part_description,
    merge_part_description,
)
from ted_and_doffin_to_ocds.converters.BT_24_Procedure import (
    parse_procedure_description,
    merge_procedure_description,
)
from ted_and_doffin_to_ocds.converters.BT_25_Lot import (
    parse_lot_quantity,
    merge_lot_quantity,
)
from ted_and_doffin_to_ocds.converters.BT_26a_lot import (
    parse_classification_type,
    merge_classification_type,
)
from ted_and_doffin_to_ocds.converters.BT_26a_part import (
    parse_classification_type_part,
    merge_classification_type_part,
)
from ted_and_doffin_to_ocds.converters.BT_26a_procedure import (
    parse_classification_type_procedure,
    merge_classification_type_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_26m_lot import (
    parse_main_classification_type_lot,
    merge_main_classification_type_lot,
)
from ted_and_doffin_to_ocds.converters.BT_26m_part import (
    parse_main_classification_type_part,
    merge_main_classification_type_part,
)
from ted_and_doffin_to_ocds.converters.BT_26m_procedure import (
    parse_main_classification_type_procedure,
    merge_main_classification_type_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_262_lot import (
    parse_main_classification_code_lot,
    merge_main_classification_code_lot,
)
from ted_and_doffin_to_ocds.converters.BT_262_part import (
    parse_main_classification_code_part,
    merge_main_classification_code_part,
)
from ted_and_doffin_to_ocds.converters.BT_262_procedure import (
    parse_main_classification_code_procedure,
    merge_main_classification_code_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_263_lot import (
    parse_additional_classification_code_lot,
    merge_additional_classification_code_lot,
)
from ted_and_doffin_to_ocds.converters.BT_263_part import (
    parse_additional_classification_code_part,
    merge_additional_classification_code_part,
)
from ted_and_doffin_to_ocds.converters.BT_263_procedure import (
    parse_additional_classification_code_procedure,
    merge_additional_classification_code_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_27_Lot import (
    parse_lot_estimated_value,
    merge_lot_estimated_value,
)
from ted_and_doffin_to_ocds.converters.BT_27_LotsGroup import (
    parse_bt_27_lots_group,
    merge_bt_27_lots_group,
)
from ted_and_doffin_to_ocds.converters.BT_27_Part import (
    parse_bt_27_part,
    merge_bt_27_part,
)
from ted_and_doffin_to_ocds.converters.BT_27_Procedure import (
    parse_bt_27_procedure,
    merge_bt_27_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_271_Lot import (
    parse_bt_271_lot,
    merge_bt_271_lot,
)
from ted_and_doffin_to_ocds.converters.BT_271_LotsGroup import (
    parse_bt_271_lots_group,
    merge_bt_271_lots_group,
)
from ted_and_doffin_to_ocds.converters.BT_271_Procedure import (
    parse_bt_271_procedure,
    merge_bt_271_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_300_Lot import (
    parse_lot_additional_info,
    merge_lot_additional_info,
)
from ted_and_doffin_to_ocds.converters.BT_300_LotsGroup import (
    parse_lotsgroup_additional_info,
    merge_lotsgroup_additional_info,
)
from ted_and_doffin_to_ocds.converters.BT_300_Part import (
    parse_part_additional_info,
    merge_part_additional_info,
)
from ted_and_doffin_to_ocds.converters.BT_300_Procedure import (
    parse_procedure_additional_info,
    merge_procedure_additional_info,
)
from ted_and_doffin_to_ocds.converters.BT_31_Procedure import (
    parse_max_lots_allowed,
    merge_max_lots_allowed,
)
from ted_and_doffin_to_ocds.converters.BT_3201_Tender import (
    parse_tender_identifier,
    merge_tender_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_3202_Contract import (
    parse_contract_tender_id,
    merge_contract_tender_id,
)
from ted_and_doffin_to_ocds.converters.BT_33_Procedure import (
    parse_max_lots_awarded,
    merge_max_lots_awarded,
)
from ted_and_doffin_to_ocds.converters.BT_330_Procedure import (
    parse_group_identifier,
    merge_group_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_36_Lot import (
    parse_lot_duration,
    merge_lot_duration,
)
from ted_and_doffin_to_ocds.converters.BT_36_Part import (
    parse_part_duration,
    merge_part_duration,
)
from ted_and_doffin_to_ocds.converters.BT_40_Lot import (
    parse_lot_selection_criteria_second_stage,
    merge_lot_selection_criteria_second_stage,
)
from ted_and_doffin_to_ocds.converters.BT_41_Lot import (
    parse_lot_following_contract,
    merge_lot_following_contract,
)
from ted_and_doffin_to_ocds.converters.BT_42_Lot import (
    parse_lot_jury_decision_binding,
    merge_lot_jury_decision_binding,
)
from ted_and_doffin_to_ocds.converters.BT_44_Lot import (
    parse_prize_rank,
    merge_prize_rank,
)
from ted_and_doffin_to_ocds.converters.BT_45_Lot import (
    parse_lot_rewards_other,
    merge_lot_rewards_other,
)
from ted_and_doffin_to_ocds.converters.BT_46_Lot import (
    parse_jury_member_name,
    merge_jury_member_name,
)
from ted_and_doffin_to_ocds.converters.BT_47_Lot import (
    parse_participant_name,
    merge_participant_name,
)
from ted_and_doffin_to_ocds.converters.BT_50_Lot import (
    parse_minimum_candidates,
    merge_minimum_candidates,
)
from ted_and_doffin_to_ocds.converters.BT_500_Organization_Company import (
    parse_organization_name,
    merge_organization_name,
)
from ted_and_doffin_to_ocds.converters.BT_500_Organization_TouchPoint import (
    parse_touchpoint_name,
    merge_touchpoint_name,
)
from ted_and_doffin_to_ocds.converters.BT_500_UBO import parse_ubo_name, merge_ubo_name
from ted_and_doffin_to_ocds.converters.BT_501_Organization_Company import (
    parse_organization_identifier,
    merge_organization_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_5010_Lot import (
    parse_eu_funds_financing_identifier,
    merge_eu_funds_financing_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_5011_Contract import (
    parse_contract_eu_funds_financing_identifier,
    merge_contract_eu_funds_financing_identifier,
)
from ted_and_doffin_to_ocds.converters.BT_502_Organization_Company import (
    parse_organization_contact_point,
    merge_organization_contact_point,
)
from ted_and_doffin_to_ocds.converters.BT_502_Organization_TouchPoint import (
    parse_touchpoint_contact_point,
    merge_touchpoint_contact_point,
)
from ted_and_doffin_to_ocds.converters.BT_503_Organization_Company import (
    parse_organization_contact_telephone,
    merge_organization_contact_telephone,
)
from ted_and_doffin_to_ocds.converters.BT_503_Organization_TouchPoint import (
    parse_touchpoint_contact_telephone,
    merge_touchpoint_contact_telephone,
)
from ted_and_doffin_to_ocds.converters.BT_503_UBO import (
    parse_ubo_telephone,
    merge_ubo_telephone,
)
from ted_and_doffin_to_ocds.converters.BT_505_Organization_Company import (
    parse_organization_website,
    merge_organization_website,
)
from ted_and_doffin_to_ocds.converters.BT_505_Organization_TouchPoint import (
    parse_touchpoint_website,
    merge_touchpoint_website,
)
from ted_and_doffin_to_ocds.converters.BT_506_Organization_Company import (
    parse_organization_contact_email,
    merge_organization_contact_email,
)
from ted_and_doffin_to_ocds.converters.BT_506_Organization_TouchPoint import (
    parse_touchpoint_contact_email,
    merge_touchpoint_contact_email,
)
from ted_and_doffin_to_ocds.converters.BT_506_UBO import (
    parse_ubo_email,
    merge_ubo_email,
)
from ted_and_doffin_to_ocds.converters.BT_507_Organization_Company import (
    parse_organization_country_subdivision,
    merge_organization_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.BT_507_Organization_TouchPoint import (
    parse_touchpoint_country_subdivision,
    merge_touchpoint_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.BT_507_UBO import (
    parse_ubo_country_subdivision,
    merge_ubo_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.BT_5071_Lot import (
    parse_place_performance_country_subdivision,
    merge_place_performance_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.BT_5071_Part import (
    parse_part_place_performance_country_subdivision,
    merge_part_place_performance_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.BT_5071_Procedure import (
    parse_procedure_place_performance_country_subdivision,
    merge_procedure_place_performance_country_subdivision,
)
from ted_and_doffin_to_ocds.converters.BT_508_Procedure_Buyer import (
    parse_buyer_profile_url,
    merge_buyer_profile_url,
)
from ted_and_doffin_to_ocds.converters.BT_509_Organization_Company import (
    parse_organization_edelivery_gateway,
    merge_organization_edelivery_gateway,
)
from ted_and_doffin_to_ocds.converters.BT_509_Organization_TouchPoint import (
    parse_touchpoint_edelivery_gateway,
    merge_touchpoint_edelivery_gateway,
)
from ted_and_doffin_to_ocds.converters.BT_51_Lot import (
    parse_lot_maximum_candidates,
    merge_lot_maximum_candidates,
)
from ted_and_doffin_to_ocds.converters.BT_510a_Organization_Company import (
    parse_organization_street,
    merge_organization_street,
)
from ted_and_doffin_to_ocds.converters.BT_510a_Organization_TouchPoint import (
    parse_touchpoint_street,
    merge_touchpoint_street,
)
from ted_and_doffin_to_ocds.converters.BT_510a_UBO import (
    parse_ubo_street,
    merge_ubo_street,
)
from ted_and_doffin_to_ocds.converters.BT_510b_Organization_Company import (
    parse_organization_streetline1,
    merge_organization_streetline1,
)
from ted_and_doffin_to_ocds.converters.BT_510b_Organization_TouchPoint import (
    parse_touchpoint_streetline1,
    merge_touchpoint_streetline1,
)
from ted_and_doffin_to_ocds.converters.BT_510b_UBO import (
    parse_ubo_streetline1,
    merge_ubo_streetline1,
)
from ted_and_doffin_to_ocds.converters.BT_510c_Organization_Company import (
    parse_organization_streetline2,
    merge_organization_streetline2,
)
from ted_and_doffin_to_ocds.converters.BT_510c_Organization_TouchPoint import (
    parse_touchpoint_streetline2,
    merge_touchpoint_streetline2,
)
from ted_and_doffin_to_ocds.converters.BT_510c_UBO import (
    parse_ubo_streetline2,
    merge_ubo_streetline2,
)

from ted_and_doffin_to_ocds.converters.BT_5101_Lot import (
    parse_place_performance_street_lot,
    merge_place_performance_street_lot,
)
from ted_and_doffin_to_ocds.converters.BT_5101a_Part import (
    parse_part_place_performance_street,
    merge_part_place_performance_street,
)
from ted_and_doffin_to_ocds.converters.BT_5101a_Procedure import (
    parse_procedure_place_performance_street,
    merge_procedure_place_performance_street,
)

from ted_and_doffin_to_ocds.converters.BT_5101b_Part import (
    parse_part_place_performance_streetline1,
    merge_part_place_performance_streetline1,
)
from ted_and_doffin_to_ocds.converters.BT_5101b_Procedure import (
    parse_procedure_place_performance_streetline1,
    merge_procedure_place_performance_streetline1,
)
from ted_and_doffin_to_ocds.converters.BT_5101c_Part import (
    parse_part_place_performance_streetline2,
    merge_part_place_performance_streetline2,
)
from ted_and_doffin_to_ocds.converters.BT_5101c_Procedure import (
    parse_procedure_place_performance_streetline2,
    merge_procedure_place_performance_streetline2,
)
from ted_and_doffin_to_ocds.converters.BT_512_Organization_Company import (
    parse_organization_postcode,
    merge_organization_postcode,
)
from ted_and_doffin_to_ocds.converters.BT_512_Organization_TouchPoint import (
    parse_touchpoint_postcode,
    merge_touchpoint_postcode,
)
from ted_and_doffin_to_ocds.converters.BT_512_UBO import (
    parse_ubo_postcode,
    merge_ubo_postcode,
)
from ted_and_doffin_to_ocds.converters.BT_5121_Lot import (
    parse_place_performance_post_code,
    merge_place_performance_post_code,
)
from ted_and_doffin_to_ocds.converters.BT_5121_Part import (
    parse_place_performance_post_code_part,
    merge_place_performance_post_code_part,
)
from ted_and_doffin_to_ocds.converters.BT_5121_Procedure import (
    parse_place_performance_post_code_procedure,
    merge_place_performance_post_code_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_513_Organization_Company import (
    parse_organization_city,
    merge_organization_city,
)
from ted_and_doffin_to_ocds.converters.BT_513_Organization_TouchPoint import (
    parse_touchpoint_city,
    merge_touchpoint_city,
)
from ted_and_doffin_to_ocds.converters.BT_513_UBO import parse_ubo_city, merge_ubo_city
from ted_and_doffin_to_ocds.converters.BT_5131_Lot import (
    parse_place_performance_city,
    merge_place_performance_city,
)
from ted_and_doffin_to_ocds.converters.BT_5131_Part import (
    parse_place_performance_city_part,
    merge_place_performance_city_part,
)
from ted_and_doffin_to_ocds.converters.BT_5131_Procedure import (
    parse_place_performance_city_procedure,
    merge_place_performance_city_procedure,
)
from ted_and_doffin_to_ocds.converters.BT_514_Organization_Company import (
    parse_organization_country,
    merge_organization_country,
)
from ted_and_doffin_to_ocds.converters.BT_514_Organization_TouchPoint import (
    parse_touchpoint_country,
    merge_touchpoint_country,
)
from ted_and_doffin_to_ocds.converters.BT_514_UBO import (
    parse_ubo_country,
    merge_ubo_country,
)
from ted_and_doffin_to_ocds.converters.BT_5141_Lot import (
    parse_lot_country,
    merge_lot_country,
)
from ted_and_doffin_to_ocds.converters.BT_5141_Part import (
    parse_part_country,
    merge_part_country,
)
from ted_and_doffin_to_ocds.converters.BT_5141_Procedure import (
    parse_procedure_country,
    merge_procedure_country,
)
from ted_and_doffin_to_ocds.converters.BT_52_Lot import (
    parse_successive_reduction_indicator,
    merge_successive_reduction_indicator,
)
from ted_and_doffin_to_ocds.converters.BT_531_Lot import (
    parse_lot_additional_nature,
    merge_lot_additional_nature,
)
from ted_and_doffin_to_ocds.converters.BT_531_Part import (
    parse_part_additional_nature,
    merge_part_additional_nature,
)
from ted_and_doffin_to_ocds.converters.BT_531_Procedure import (
    parse_procedure_additional_nature,
    merge_procedure_additional_nature,
)
from ted_and_doffin_to_ocds.converters.BT_536_Lot import (
    parse_lot_start_date,
    merge_lot_start_date,
)
from ted_and_doffin_to_ocds.converters.BT_536_Part import (
    parse_part_contract_start_date,
    merge_part_contract_start_date,
)
from ted_and_doffin_to_ocds.converters.BT_537_Lot import (
    parse_lot_duration_end_date,
    merge_lot_duration_end_date,
)
from ted_and_doffin_to_ocds.converters.BT_537_Part import (
    parse_part_duration_end_date,
    merge_part_duration_end_date,
)
from ted_and_doffin_to_ocds.converters.BT_538_Lot import (
    parse_lot_duration_other,
    merge_lot_duration_other,
)
from ted_and_doffin_to_ocds.converters.BT_538_Part import (
    parse_part_duration_other,
    merge_part_duration_other,
)
from ted_and_doffin_to_ocds.converters.BT_539_Lot import (
    parse_award_criterion_type,
    merge_award_criterion_type,
)
from ted_and_doffin_to_ocds.converters.BT_54_Lot import (
    parse_options_description,
    merge_options_description,
)
from ted_and_doffin_to_ocds.converters.BT_540_Lot import (
    parse_award_criterion_description,
    merge_award_criterion_description,
)
from ted_and_doffin_to_ocds.converters.BT_540_LotsGroup import (
    parse_award_criterion_description_lots_group,
    merge_award_criterion_description_lots_group,
)
from ted_and_doffin_to_ocds.converters.BT_541_Lot_FixedNumber import (
    parse_award_criterion_fixed_number,
    merge_award_criterion_fixed_number,
)

from ted_and_doffin_to_ocds.converters.BT_5423_Lot import (
    parse_award_criterion_number_threshold,
    merge_award_criterion_number_threshold,
)
from ted_and_doffin_to_ocds.converters.BT_5423_LotsGroup import (
    parse_award_criterion_number_threshold_lotsgroup,
    merge_award_criterion_number_threshold_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_543_Lot import (
    parse_award_criteria_complicated,
    merge_award_criteria_complicated,
)
from ted_and_doffin_to_ocds.converters.BT_543_LotsGroup import (
    parse_award_criteria_complicated_lotsgroup,
    merge_award_criteria_complicated_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_553_Tender import (
    parse_subcontracting_value,
    merge_subcontracting_value,
)
from ted_and_doffin_to_ocds.converters.BT_554_Tender import (
    parse_subcontracting_description,
    merge_subcontracting_description,
)
from ted_and_doffin_to_ocds.converters.BT_555_Tender import (
    parse_subcontracting_percentage,
    merge_subcontracting_percentage,
)
from ted_and_doffin_to_ocds.converters.BT_57_Lot import (
    parse_renewal_description,
    merge_renewal_description,
)
from ted_and_doffin_to_ocds.converters.BT_58_Lot import (
    parse_renewal_maximum,
    merge_renewal_maximum,
)
from ted_and_doffin_to_ocds.converters.BT_60_Lot import parse_eu_funds, merge_eu_funds
from ted_and_doffin_to_ocds.converters.BT_610_Procedure_Buyer import (
    parse_activity_entity,
    merge_activity_entity,
)
from ted_and_doffin_to_ocds.converters.BT_6110_Contract import (
    parse_contract_eu_funds_details,
    merge_contract_eu_funds_details,
)
from ted_and_doffin_to_ocds.converters.BT_6140_Lot import (
    parse_lot_eu_funds_details,
    merge_lot_eu_funds_details,
)
from ted_and_doffin_to_ocds.converters.BT_615_Lot import (
    parse_documents_restricted_url,
    merge_documents_restricted_url,
)
from ted_and_doffin_to_ocds.converters.BT_615_Part import (
    parse_documents_restricted_url_part,
    merge_documents_restricted_url_part,
)
from ted_and_doffin_to_ocds.converters.BT_625_Lot import parse_unit, merge_unit
from ted_and_doffin_to_ocds.converters.BT_63_Lot import parse_variants, merge_variants
from ted_and_doffin_to_ocds.converters.BT_630_Lot import (
    parse_deadline_receipt_expressions,
    merge_deadline_receipt_expressions,
)
from ted_and_doffin_to_ocds.converters.BT_631_Lot import (
    parse_dispatch_invitation_interest,
    merge_dispatch_invitation_interest,
)
from ted_and_doffin_to_ocds.converters.BT_632_Lot import (
    parse_tool_name,
    merge_tool_name,
)
from ted_and_doffin_to_ocds.converters.BT_632_Part import (
    parse_tool_name_part,
    merge_tool_name_part,
)
from ted_and_doffin_to_ocds.converters.BT_633_Organization import (
    parse_organization_natural_person,
    merge_organization_natural_person,
)
from ted_and_doffin_to_ocds.converters.BT_635_LotResult import (
    parse_buyer_review_requests_count,
    merge_buyer_review_requests_count,
)
from ted_and_doffin_to_ocds.converters.BT_636_LotResult import (
    parse_irregularity_type,
    merge_irregularity_type,
)
from ted_and_doffin_to_ocds.converters.BT_64_Lot import (
    parse_subcontracting_obligation_minimum,
    merge_subcontracting_obligation_minimum,
)
from ted_and_doffin_to_ocds.converters.BT_644_Lot_Prize_Value import (
    parse_lot_prize_value,
    merge_lot_prize_value,
)
from ted_and_doffin_to_ocds.converters.BT_65_Lot_Subcontracting_Obligation import (
    parse_subcontracting_obligation,
    merge_subcontracting_obligation,
)
from ted_and_doffin_to_ocds.converters.BT_651_Lot_Subcontracting_Tender_Indication import (
    parse_subcontracting_tender_indication,
    merge_subcontracting_tender_indication,
)
from ted_and_doffin_to_ocds.converters.BT_660_LotResult import (
    parse_framework_reestimated_value,
    merge_framework_reestimated_value,
)
from ted_and_doffin_to_ocds.converters.BT_67_Exclusion_Grounds import (
    parse_exclusion_grounds,
    merge_exclusion_grounds,
)
from ted_and_doffin_to_ocds.converters.BT_70_Lot import (
    parse_lot_performance_terms,
    merge_lot_performance_terms,
)
from ted_and_doffin_to_ocds.converters.BT_702a_Notice import (
    parse_notice_language,
    merge_notice_language,
)
from ted_and_doffin_to_ocds.converters.BT_706_UBO import (
    parse_ubo_nationality,
    merge_ubo_nationality,
)
from ted_and_doffin_to_ocds.converters.BT_707_Lot import (
    parse_lot_documents_restricted_justification,
    merge_lot_documents_restricted_justification,
)
from ted_and_doffin_to_ocds.converters.BT_707_Part import (
    parse_part_documents_restricted_justification,
    merge_part_documents_restricted_justification,
)
from ted_and_doffin_to_ocds.converters.BT_708_Lot import (
    parse_lot_documents_official_language,
    merge_lot_documents_official_language,
)
from ted_and_doffin_to_ocds.converters.BT_708_Part import (
    parse_part_documents_official_language,
    merge_part_documents_official_language,
)
from ted_and_doffin_to_ocds.converters.BT_709_LotResult import (
    parse_framework_maximum_value,
    merge_framework_maximum_value,
)
from ted_and_doffin_to_ocds.converters.BT_71_Lot import (
    parse_reserved_participation,
    merge_reserved_participation,
)
from ted_and_doffin_to_ocds.converters.BT_71_Part import (
    parse_reserved_participation_part,
    merge_reserved_participation_part,
)
from ted_and_doffin_to_ocds.converters.BT_710_LotResult import (
    parse_tender_value_lowest,
    merge_tender_value_lowest,
)
from ted_and_doffin_to_ocds.converters.BT_711_LotResult import (
    parse_tender_value_highest,
    merge_tender_value_highest,
)
from ted_and_doffin_to_ocds.converters.BT_712a_LotResult import (
    parse_buyer_review_complainants,
    merge_buyer_review_complainants,
)
from ted_and_doffin_to_ocds.converters.BT_712b_LotResult import (
    parse_buyer_review_complainants_bt_712b,
    merge_buyer_review_complainants_bt_712b,
)
from ted_and_doffin_to_ocds.converters.BT_717_Lot import (
    parse_clean_vehicles_directive,
    merge_clean_vehicles_directive,
)
from ted_and_doffin_to_ocds.converters.BT_719_notice import (
    parse_procurement_documents_change_date,
    merge_procurement_documents_change_date,
)
from ted_and_doffin_to_ocds.converters.BT_720_Tender import (
    parse_tender_value,
    merge_tender_value,
)
from ted_and_doffin_to_ocds.converters.BT_721_Contract_Title import (
    parse_contract_title,
    merge_contract_title,
)
from ted_and_doffin_to_ocds.converters.BT_722_Contract import (
    parse_contract_eu_funds,
    merge_contract_eu_funds,
)
from ted_and_doffin_to_ocds.converters.BT_7220_Lot import (
    parse_lot_eu_funds,
    merge_lot_eu_funds,
)
from ted_and_doffin_to_ocds.converters.BT_723_LotResult import (
    parse_vehicle_category,
    merge_vehicle_category,
)
from ted_and_doffin_to_ocds.converters.BT_726_Lot import (
    parse_lot_sme_suitability,
    merge_lot_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.BT_726_LotsGroup import (
    parse_lots_group_sme_suitability,
    merge_lots_group_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.BT_726_Part import (
    parse_part_sme_suitability,
    merge_part_sme_suitability,
)
from ted_and_doffin_to_ocds.converters.BT_727_Lot import (
    parse_lot_place_performance,
    merge_lot_place_performance,
)
from ted_and_doffin_to_ocds.converters.BT_727_Part import (
    parse_part_place_performance,
    merge_part_place_performance,
)
from ted_and_doffin_to_ocds.converters.BT_727_Procedure import (
    parse_procedure_place_performance,
    merge_procedure_place_performance,
)
from ted_and_doffin_to_ocds.converters.BT_728_Lot import (
    parse_lot_place_performance_additional,
    merge_lot_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.BT_728_Part import (
    parse_part_place_performance_additional,
    merge_part_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.BT_728_Procedure import (
    parse_procedure_place_performance_additional,
    merge_procedure_place_performance_additional,
)
from ted_and_doffin_to_ocds.converters.BT_729_Lot import (
    parse_lot_subcontracting_obligation_maximum,
    merge_lot_subcontracting_obligation_maximum,
)
from ted_and_doffin_to_ocds.converters.BT_732_Lot import (
    parse_lot_security_clearance_description,
    merge_lot_security_clearance_description,
)
from ted_and_doffin_to_ocds.converters.BT_733_Lot import (
    parse_lot_award_criteria_order_justification,
    merge_lot_award_criteria_order_justification,
)
from ted_and_doffin_to_ocds.converters.BT_733_LotsGroup import (
    parse_lots_group_award_criteria_order_justification,
    merge_lots_group_award_criteria_order_justification,
)
from ted_and_doffin_to_ocds.converters.BT_734_Lot import (
    parse_award_criterion_name,
    merge_award_criterion_name,
)
from ted_and_doffin_to_ocds.converters.BT_734_LotsGroup import (
    parse_award_criterion_name_lotsgroup,
    merge_award_criterion_name_lotsgroup,
)
from ted_and_doffin_to_ocds.converters.BT_735_Lot import (
    parse_cvd_contract_type,
    merge_cvd_contract_type,
)
from ted_and_doffin_to_ocds.converters.BT_735_LotResult import (
    parse_cvd_contract_type_lotresult,
    merge_cvd_contract_type_lotresult,
)
from ted_and_doffin_to_ocds.converters.BT_736_Lot import (
    parse_reserved_execution,
    merge_reserved_execution,
)
from ted_and_doffin_to_ocds.converters.BT_736_Part import (
    parse_reserved_execution_part,
    merge_reserved_execution_part,
)
from ted_and_doffin_to_ocds.converters.BT_737_Lot import (
    parse_documents_unofficial_language,
    merge_documents_unofficial_language,
)
from ted_and_doffin_to_ocds.converters.BT_737_Part import (
    parse_documents_unofficial_language_part,
    merge_documents_unofficial_language_part,
)
from ted_and_doffin_to_ocds.converters.BT_738_notice import (
    parse_notice_preferred_publication_date,
    merge_notice_preferred_publication_date,
)
from ted_and_doffin_to_ocds.converters.BT_739_Organization_Company import (
    parse_organization_contact_fax,
    merge_organization_contact_fax,
)
from ted_and_doffin_to_ocds.converters.BT_739_Organization_TouchPoint import (
    parse_touchpoint_contact_fax,
    merge_touchpoint_contact_fax,
)
from ted_and_doffin_to_ocds.converters.BT_739_UBO import parse_ubo_fax, merge_ubo_fax
from ted_and_doffin_to_ocds.converters.BT_740_Procedure_Buyer import (
    parse_buyer_contracting_entity,
    merge_buyer_contracting_entity,
)
from ted_and_doffin_to_ocds.converters.BT_743_Lot import (
    parse_electronic_invoicing,
    merge_electronic_invoicing,
)
from ted_and_doffin_to_ocds.converters.BT_744_Lot import (
    parse_submission_electronic_signature,
    merge_submission_electronic_signature,
)
from ted_and_doffin_to_ocds.converters.BT_745_Lot import (
    parse_submission_nonelectronic_description,
    merge_submission_nonelectronic_description,
)
from ted_and_doffin_to_ocds.converters.BT_746_Organization import (
    parse_winner_listed,
    merge_winner_listed,
)
from ted_and_doffin_to_ocds.converters.BT_747_Lot import (
    parse_selection_criteria_type,
    merge_selection_criteria_type,
)

# from ted_and_doffin_to_ocds.converters.BT_749_Lot import parse_selection_criteria_name, merge_selection_criteria_name
from ted_and_doffin_to_ocds.converters.BT_75_Lot import (
    parse_guarantee_required_description,
    merge_guarantee_required_description,
)
from ted_and_doffin_to_ocds.converters.BT_750_Lot import (
    parse_selection_criteria,
    merge_selection_criteria,
)
from ted_and_doffin_to_ocds.converters.BT_752_Lot_ThresholdNumber import (
    parse_selection_criteria_threshold_number,
    merge_selection_criteria_threshold_number,
)
from ted_and_doffin_to_ocds.converters.BT_752_Lot_WeightNumber import (
    parse_selection_criteria_weight_number,
    merge_selection_criteria_weight_number,
)
from ted_and_doffin_to_ocds.converters.BT_7531_Lot import (
    parse_selection_criteria_number_weight,
    merge_selection_criteria_number_weight,
)
from ted_and_doffin_to_ocds.converters.BT_7532_Lot import (
    parse_selection_criteria_number_threshold,
    merge_selection_criteria_number_threshold,
)
from ted_and_doffin_to_ocds.converters.BT_754_Lot import (
    parse_accessibility_criteria,
    merge_accessibility_criteria,
)
from ted_and_doffin_to_ocds.converters.BT_755_Lot import (
    parse_accessibility_justification,
    merge_accessibility_justification,
)
from ted_and_doffin_to_ocds.converters.BT_756_Procedure import (
    parse_pin_competition_termination,
    merge_pin_competition_termination,
)
from ted_and_doffin_to_ocds.converters.BT_759_LotResult import (
    parse_received_submissions_count,
    merge_received_submissions_count,
)
from ted_and_doffin_to_ocds.converters.BT_76_Lot import (
    parse_tenderer_legal_form,
    merge_tenderer_legal_form,
)
from ted_and_doffin_to_ocds.converters.BT_760_LotResult import (
    parse_received_submissions_type,
    merge_received_submissions_type,
)
from ted_and_doffin_to_ocds.converters.BT_762_ChangeReasonDescription import (
    parse_change_reason_description,
    merge_change_reason_description,
)
from ted_and_doffin_to_ocds.converters.BT_763_LotsAllRequired import (
    parse_lots_all_required,
    merge_lots_all_required,
)
from ted_and_doffin_to_ocds.converters.BT_764_SubmissionElectronicCatalogue import (
    parse_submission_electronic_catalogue,
    merge_submission_electronic_catalogue,
)
from ted_and_doffin_to_ocds.converters.BT_765_FrameworkAgreement import (
    parse_framework_agreement,
    merge_framework_agreement,
)
from ted_and_doffin_to_ocds.converters.BT_765_PartFrameworkAgreement import (
    parse_part_framework_agreement,
    merge_part_framework_agreement,
)
from ted_and_doffin_to_ocds.converters.BT_766_DynamicPurchasingSystem import (
    parse_dynamic_purchasing_system,
    merge_dynamic_purchasing_system,
)
from ted_and_doffin_to_ocds.converters.BT_766_PartDynamicPurchasingSystem import (
    parse_part_dynamic_purchasing_system,
    merge_part_dynamic_purchasing_system,
)
from ted_and_doffin_to_ocds.converters.BT_767_Lot import (
    parse_electronic_auction,
    merge_electronic_auction,
)
from ted_and_doffin_to_ocds.converters.BT_769_Lot import (
    parse_multiple_tenders,
    merge_multiple_tenders,
)
from ted_and_doffin_to_ocds.converters.BT_77_Lot import (
    parse_financial_terms,
    merge_financial_terms,
)
from ted_and_doffin_to_ocds.converters.BT_771_Lot import (
    parse_late_tenderer_info,
    merge_late_tenderer_info,
)
from ted_and_doffin_to_ocds.converters.BT_772_Lot import (
    parse_late_tenderer_info_description,
    merge_late_tenderer_info_description,
)
from ted_and_doffin_to_ocds.converters.BT_773_Tender import (
    parse_subcontracting,
    merge_subcontracting,
)
from ted_and_doffin_to_ocds.converters.BT_774_Lot import (
    parse_green_procurement,
    merge_green_procurement,
)
from ted_and_doffin_to_ocds.converters.BT_775_Lot import (
    parse_social_procurement,
    merge_social_procurement,
)
from ted_and_doffin_to_ocds.converters.BT_776_Lot import (
    parse_procurement_innovation,
    merge_procurement_innovation,
)
from ted_and_doffin_to_ocds.converters.BT_777_Lot import (
    parse_strategic_procurement_description,
    merge_strategic_procurement_description,
)
from ted_and_doffin_to_ocds.converters.BT_78_Lot import (
    parse_security_clearance_deadline,
    merge_security_clearance_deadline,
)
from ted_and_doffin_to_ocds.converters.BT_79_Lot import (
    parse_performing_staff_qualification,
    merge_performing_staff_qualification,
)
from ted_and_doffin_to_ocds.converters.BT_801_Lot import (
    parse_non_disclosure_agreement,
    merge_non_disclosure_agreement,
)
from ted_and_doffin_to_ocds.converters.BT_802_Lot import (
    parse_non_disclosure_agreement_description,
    merge_non_disclosure_agreement_description,
)
from ted_and_doffin_to_ocds.converters.BT_805_Lot import (
    parse_green_procurement_criteria,
    merge_green_procurement_criteria,
)
from ted_and_doffin_to_ocds.converters.BT_92_Lot import (
    parse_electronic_ordering,
    merge_electronic_ordering,
)
from ted_and_doffin_to_ocds.converters.BT_93_Lot import (
    parse_electronic_payment,
    merge_electronic_payment,
)
from ted_and_doffin_to_ocds.converters.BT_94_Lot import (
    parse_recurrence,
    merge_recurrence,
)
from ted_and_doffin_to_ocds.converters.BT_95_Lot import (
    parse_recurrence_description,
    merge_recurrence_description,
)
from ted_and_doffin_to_ocds.converters.BT_97_Lot import (
    parse_submission_language,
    merge_submission_language,
)
from ted_and_doffin_to_ocds.converters.BT_98_Lot import (
    parse_tender_validity_deadline,
    merge_tender_validity_deadline,
)
from ted_and_doffin_to_ocds.converters.BT_99_Lot import (
    parse_review_deadline_description,
    merge_review_deadline_description,
)
from ted_and_doffin_to_ocds.converters.OPP_020_Contract import (
    map_extended_duration_indicator,
    merge_extended_duration_indicator,
)
from ted_and_doffin_to_ocds.converters.OPP_021_Contract import (
    map_essential_assets,
    merge_essential_assets,
)
from ted_and_doffin_to_ocds.converters.OPP_022_Contract import (
    map_asset_significance,
    merge_asset_significance,
)
from ted_and_doffin_to_ocds.converters.OPP_023_Contract import (
    map_asset_predominance,
    merge_asset_predominance,
)
from ted_and_doffin_to_ocds.converters.OPP_031_Tender import (
    parse_contract_conditions,
    merge_contract_conditions,
)
from ted_and_doffin_to_ocds.converters.OPP_032_Tender import (
    parse_revenues_allocation,
    merge_revenues_allocation,
)
from ted_and_doffin_to_ocds.converters.OPP_034_Tender import (
    parse_penalties_and_rewards,
    merge_penalties_and_rewards,
)
from ted_and_doffin_to_ocds.converters.OPP_040_Procedure import (
    parse_main_nature_sub_type,
    merge_main_nature_sub_type,
)
from ted_and_doffin_to_ocds.converters.OPP_050_Organization import (
    parse_buyers_group_lead_indicator,
    merge_buyers_group_lead_indicator,
)
from ted_and_doffin_to_ocds.converters.OPP_051_Organization import (
    parse_awarding_cpb_buyer_indicator,
    merge_awarding_cpb_buyer_indicator,
)
from ted_and_doffin_to_ocds.converters.OPP_052_Organization import (
    parse_acquiring_cpb_buyer_indicator,
    merge_acquiring_cpb_buyer_indicator,
)
from ted_and_doffin_to_ocds.converters.OPP_080_Tender import (
    parse_kilometers_public_transport,
    merge_kilometers_public_transport,
)
from ted_and_doffin_to_ocds.converters.OPP_090_Procedure import (
    parse_previous_notice_identifier,
    merge_previous_notice_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_030_Procedure_SProvider import (
    parse_provided_service_type,
    merge_provided_service_type,
)
from ted_and_doffin_to_ocds.converters.OPP_071_Lot import (
    parse_quality_target_code,
    merge_quality_target_code,
)
from ted_and_doffin_to_ocds.converters.OPP_072_Lot import (
    parse_quality_target_description,
    merge_quality_target_description,
)
from ted_and_doffin_to_ocds.converters.OPP_100_Contract import (
    parse_framework_notice_identifier,
    merge_framework_notice_identifier,
)
from ted_and_doffin_to_ocds.converters.OPP_110_111_FiscalLegis import (
    parse_fiscal_legislation,
    merge_fiscal_legislation,
)
from ted_and_doffin_to_ocds.converters.OPP_112_120_EnvironLegis import (
    parse_environmental_legislation,
    merge_environmental_legislation,
)
from ted_and_doffin_to_ocds.converters.OPP_113_130_EmployLegis import (
    parse_employment_legislation,
    merge_employment_legislation,
)
from ted_and_doffin_to_ocds.converters.OPP_140_ProcurementDocs import (
    parse_procurement_documents,
    merge_procurement_documents,
)
from ted_and_doffin_to_ocds.converters.OPT_155_LotResult import (
    parse_vehicle_type,
    merge_vehicle_type,
)
from ted_and_doffin_to_ocds.converters.OPT_156_LotResult import (
    parse_vehicle_numeric,
    merge_vehicle_numeric,
)
from ted_and_doffin_to_ocds.converters.OPT_160_UBO import (
    parse_ubo_first_name,
    merge_ubo_first_name,
)
from ted_and_doffin_to_ocds.converters.OPT_170_Tenderer import (
    parse_tendering_party_leader,
    merge_tendering_party_leader,
)
from ted_and_doffin_to_ocds.converters.OPT_200_Organization_Company import (
    parse_organization_technical_identifier,
    merge_organization_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_201_Organization_TouchPoint import (
    parse_touchpoint_technical_identifier,
    merge_touchpoint_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_202_UBO import (
    parse_ubo_identifier,
    merge_ubo_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_300_Contract_Signatory import (
    parse_contract_signatory,
    merge_contract_signatory,
)
from ted_and_doffin_to_ocds.converters.OPT_300_Procedure_SProvider import (
    parse_procedure_sprovider,
    merge_procedure_sprovider,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_AddInfo import (
    parse_additional_info_provider_identifier,
    merge_additional_info_provider_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_DocProvider import (
    parse_document_provider_identifier,
    merge_document_provider_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_EmployLegis import (
    parse_employment_legislation_document_reference,
    merge_employment_legislation_document_reference,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_EnvironLegis import (
    parse_environmental_legislation_document_reference,
    merge_environmental_legislation_document_reference,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_ReviewOrg import (
    parse_review_org_identifier,
    merge_review_org_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_Mediator import (
    parse_mediator_identifier,
    merge_mediator_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_ReviewInfo import (
    parse_review_info_identifier,
    merge_review_info_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_TenderEval import (
    parse_tender_evaluator_identifier,
    merge_tender_evaluator_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Lot_TenderReceipt import (
    parse_tender_recipient_identifier,
    merge_tender_recipient_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_301_LotResult_Financing import (
    parse_lotresult_financing,
    merge_lotresult_financing,
)
from ted_and_doffin_to_ocds.converters.OPT_301_LotResult_Paying import (
    parse_lotresult_paying,
    merge_lotresult_paying,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_AddInfo import (
    parse_part_addinfo,
    merge_part_addinfo,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_DocProvider import (
    parse_part_docprovider,
    merge_part_docprovider,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_EmployLegis import (
    parse_part_employlegis,
    merge_part_employlegis,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_EnvironLegis import (
    parse_part_environlegis,
    merge_part_environlegis,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_FiscalLegis import (
    parse_part_fiscallegis,
    merge_part_fiscallegis,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_Mediator import (
    parse_part_mediator,
    merge_part_mediator,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_ReviewInfo import (
    parse_part_reviewinfo,
    merge_part_reviewinfo,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_ReviewOrg import (
    parse_part_revieworg,
    merge_part_revieworg,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_TenderEval import (
    parse_part_tendereval,
    merge_part_tendereval,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Part_TenderReceipt import (
    parse_part_tenderreceipt,
    merge_part_tenderreceipt,
)
from ted_and_doffin_to_ocds.converters.OPT_301_Tenderer_MainCont import (
    parse_tenderer_maincont,
    merge_tenderer_maincont,
)

# add more OPT 301 her

from ted_and_doffin_to_ocds.converters.OPT_302_Organization import (
    parse_beneficial_owner_reference,
    merge_beneficial_owner_reference,
)
from ted_and_doffin_to_ocds.converters.OPT_310_Tender import (
    parse_tendering_party_id_reference,
    merge_tendering_party_id_reference,
)
from ted_and_doffin_to_ocds.converters.OPT_315_LotResult import (
    parse_contract_identifier_reference,
    merge_contract_identifier_reference,
)
from ted_and_doffin_to_ocds.converters.OPT_316_Contract import (
    parse_contract_technical_identifier,
    merge_contract_technical_identifier,
)
from ted_and_doffin_to_ocds.converters.OPT_320_LotResult import (
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

    logger.info(f"Processing {section_name}")
    try:
        for parse_func in parse_funcs:
            data = parse_func(xml_content)
            if data:
                merge_func(release_json, data)
            else:
                logger.info(f"No data found for {parse_func.__name__}")
    except Exception as e:
        logger.error(f"Error processing {section_name}: {str(e)}")


def process_bt_section(
    release_json,
    xml_content,
    parse_functions,
    merge_function,
    section_name,
):
    logger = logging.getLogger(__name__)
    try:
        logger.info(f"Starting {section_name} processing")
        for parse_function in parse_functions:
            parsed_data = parse_function(xml_content)
            logger.info(f"Parsed data for {section_name}: {parsed_data}")
            if parsed_data:
                # logger.info(f"Calling merge function for {section_name}")
                merge_function(release_json, parsed_data)
                logger.info(f"Successfully merged data for {section_name}")
                return
        logger.warning(f"No data found for {section_name}")
    except Exception as e:
        logger.error(f"Error processing {section_name} data: {str(e)}")
        logger.exception("Exception details:")
    # finally:
    #    logger.info(f"Release JSON after {section_name} processing: {release_json}")


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
    with open(xml_path, "rb") as xml_file:
        xml_content = xml_file.read()

    configure_logging()
    logger = logging.getLogger(__name__)
    logger.info(f"Starting XML to JSON conversion for file: {xml_path}")

    # Initialize NoticeProcessor
    notice_processor = NoticeProcessor(ocid_prefix)

    # Create the initial OCDS release JSON structure
    release_json_str = notice_processor.create_release(xml_content)
    release_json = json.loads(release_json_str)

    # Parse and merge BT-01 Procedure Legal Basis
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_legal_basis],
        merge_procedure_legal_basis,
        "Procedure Legal Basis (BT-01)",
    )

    # Parse and merge BT-03 Form Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_form_type],
        merge_form_type,
        "Form Type (BT-03)",
    )

    # Parse and merge BT-04 Procedure Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_identifier],
        merge_procedure_identifier,
        "Procedure Identifier (BT-04)",
    )

    # Parse and merge BT-05-notice Notice Dispatch Date and Time
    process_bt_section(
        release_json,
        xml_content,
        [parse_notice_dispatch_date_time],
        merge_notice_dispatch_date_time,
        "Notice Dispatch Date and Time (BT-05)",
    )

    # Parse and merge BT-06-Lot Strategic Procurement
    process_bt_section(
        release_json,
        xml_content,
        [parse_strategic_procurement],
        merge_strategic_procurement,
        "Strategic Procurement (BT-06)",
    )

    # Parse and merge BT-09-Procedure Cross Border Law
    process_bt_section(
        release_json,
        xml_content,
        [parse_cross_border_law],
        merge_cross_border_law,
        "Cross Border Law (BT-09)",
    )

    # Parse and merge BT-10-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_xml],
        merge_contract_info,
        "Organization Main Activity (BT-10)",
    )

    # Parse and merge BT-105-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_type],
        merge_procedure_type,
        "Procedure Type (BT-105)",
    )

    # Parse and merge BT-106-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_accelerated],
        merge_procedure_accelerated,
        "Procedure Accelerated (BT-106)",
    )

    # Parse and merge BT-109-Lot Framework Duration Justification
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_duration_justification],
        merge_framework_duration_justification,
        "Framework Duration Justification (BT-109)",
    )

    # Parse and merge BT-11-Procedure-Buyer Buyer Legal Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_legal_type],
        merge_buyer_legal_type,
        "Buyer Legal Type (BT-11)",
    )

    # Parse and merge BT-111-Lot Framework Buyer Categories
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_buyer_categories],
        merge_framework_buyer_categories,
        "Framework Buyer Categories (BT-111)",
    )

    # Parse and merge BT-113-Lot Framework Maximum Participants Number
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_max_participants],
        merge_framework_max_participants,
        "Framework Maximum Participants Number (BT-113)",
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

    # Parse and merge BT-125(i)-Part and BT-1251-Part Previous Planning Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_previous_planning_identifier_part],
        merge_previous_planning_identifier_part,
        "Previous Planning Identifier (Part) (BT-125(i) and BT-1251)",
    )

    # Parse and merge BT-1252-Procedure Direct Award Justification
    process_bt_section(
        release_json,
        xml_content,
        [parse_direct_award_justification],
        merge_direct_award_justification,
        "Direct Award Justification (BT-1252)",
    )

    # Parse and merge BT-127 Future Notice Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_future_notice_date],
        merge_future_notice_date,
        "Future Notice Date (BT-127)",
    )

    # Parse and merge BT-13 Additional Information Deadline
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_info_deadline],
        merge_additional_info_deadline,
        "Additional Information Deadline (BT-13)",
    )

    # Parse and merge BT-13 Additional Information Deadline (Part)
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_info_deadline_part],
        merge_additional_info_deadline_part,
        "Additional Information Deadline (Part) (BT-13)",
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

    # Parse and merge BT-135-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_direct_award_justification_rationale],
        merge_direct_award_justification_rationale,
        "Direct Award Justification Rationale (BT-135)",
    )

    # Parse and merge BT-1351-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_accelerated_procedure_justification],
        merge_accelerated_procedure_justification,
        "Accelerated Procedure Justification (BT-1351)",
    )

    # Parse and merge BT-136-Procedure
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

    # Parse and merge BT-137-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_identifier],
        merge_part_identifier,
        "Part Identifier (BT-137-Part)",
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

    # Parse and merge BT-1375-Procedure
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

    # Parse and merge BT-14-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_documents_restricted],
        merge_part_documents_restricted,
        "Part Documents Restricted (BT-14-Part)",
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

    # Parse and merge BT-15-Lot-Part
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
        "Organization Name (BT-500)",
    )

    # Parse and merge BT-16-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_part_name],
        merge_organization_part_name,
        "Organization Part Name (BT-16-Organization-Company)",
    )

    # Parse and merge BT-16-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_touchpoint_part_name],
        merge_organization_touchpoint_part_name,
        "Organization TouchPoint Part Name (BT-16-Organization-TouchPoint)",
    )

    # Parse the organization info BT_500_Organization_TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_name],
        merge_touchpoint_name,
        "TouchPoint Name (BT-500-Organization-TouchPoint)",
    )

    # Parse and merge BT-160-Tender
    process_bt_section(
        release_json,
        xml_content,
        [parse_concession_revenue_buyer],
        merge_concession_revenue_buyer,
        "Concession Revenue Buyer (BT-160)",
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

    # Parse and merge BT-165-Organization-Company
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

    # Parse and merge BT-195(BT-105)-Procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt105_unpublished_identifier],
        merge_bt195_bt105_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-105)",
    )

    # Parse and merge BT-195(BT-106)-Procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt106_unpublished_identifier],
        merge_bt195_bt106_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-106)",
    )

    # Parse and merge BT-195(BT-1252)-Procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt1252_unpublished_identifier],
        merge_bt195_bt1252_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-1252)",
    )

    # Parse and merge BT-195(BT-135)-Procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt135_unpublished_identifier],
        merge_bt195_bt135_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-135)",
    )

    # Parse and merge BT-195(BT-1351)-Procedure Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt1351_unpublished_identifier],
        merge_bt195_bt1351_unpublished_identifier,
        "Unpublished Identifier (BT-195, BT-1351)",
    )

    # Parse and merge BT-195(BT-136)-Procedure Unpublished Identifier
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
        "Procedure BT-195(BT-160)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-162)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt162_unpublished_identifier],
        merge_bt195_bt162_unpublished_identifier,
        "Procedure BT-195(BT-162)-Tender Unpublished Identifier",
    )
    # Parse and merge BT-195(BT-163)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt163_unpublished_identifier],
        merge_bt195_bt163_unpublished_identifier,
        "Procedure BT-195(BT-163)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-171)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt171_unpublished_identifier],
        merge_bt195_bt171_unpublished_identifier,
        "Procedure BT-195(BT-171)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-191)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt191_unpublished_identifier],
        merge_bt195_bt191_unpublished_identifier,
        "Procedure BT-195(BT-191)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-193)-Tender Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt193_unpublished_identifier],
        merge_bt195_bt193_unpublished_identifier,
        "Procedure BT-195(BT-193)-Tender Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-539)-Lot Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt539_unpublished_identifier],
        merge_bt195_bt539_unpublished_identifier,
        "Procedure BT-195(BT-539)-Lot Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-539)-LotsGroup Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt539_lotsgroup_unpublished_identifier],
        merge_bt195_bt539_lotsgroup_unpublished_identifier,
        "Procedure BT-195(BT-539)-LotsGroup Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-540)-Lot Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt540_lot_unpublished_identifier],
        merge_bt195_bt540_lot_unpublished_identifier,
        "Procedure BT-195(BT-540)-Lot Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-540)-LotsGroup Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt540_lotsgroup_unpublished_identifier],
        merge_bt195_bt540_lotsgroup_unpublished_identifier,
        "Procedure BT-195(BT-540)-LotsGroup Unpublished Identifier",
    )

    # Parse and merge BT-195(BT-541)-Lot-Fixed Unpublished Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt541_lot_fixed_unpublished_identifier],
        merge_bt195_bt541_lot_fixed_unpublished_identifier,
        "Procedure BT-195(BT-541)-Lot-Fixed Unpublished Identifier",
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
        "Unpublished Identifier for Lot Result Buyer Review Request Count (BT-195(BT-635))",
    )
    # Parse and merge BT-195(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt636_unpublished_identifier],
        merge_bt195_bt636_unpublished_identifier,
        "Unpublished Identifier for Lot Result Buyer Review Request Irregularity Type (BT-195(BT-636))",
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
        "Unpublished Identifier for Lot Result Buyer Review Complainants (BT-195(BT-712))",
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
    # Parse and merge BT-195(BT-88)-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt195_bt88_procedure_unpublished_identifier],
        merge_bt195_bt88_procedure_unpublished_identifier,
        "Unpublished Identifier for Procedure Features (BT-195(BT-88))",
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

    # Parse and merge BT-196(BT-105)-Procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt105_unpublished_justification],
        merge_bt196_bt105_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-105)",
    )

    # Parse and merge BT-196(BT-106)-Procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt106_unpublished_justification],
        merge_bt196_bt106_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-106)",
    )

    # Parse and merge BT-196(BT-1252)-Procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt1252_unpublished_justification],
        merge_bt196_bt1252_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-1252)",
    )

    # Parse and merge BT-196(BT-135)-Procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt135_unpublished_justification],
        merge_bt196_bt135_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-135)",
    )

    # Parse and merge BT-196(BT-1351)-Procedure Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt1351_unpublished_justification],
        merge_bt196_bt1351_unpublished_justification,
        "Unpublished Justification Description (BT-196, BT-1351)",
    )

    # Parse and merge BT-196(BT-136)-Procedure Unpublished Justification Description
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
        "Procedure BT-196(BT-160)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-162)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt162_unpublished_justification],
        merge_bt196_bt162_unpublished_justification,
        "Procedure BT-196(BT-162)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-163)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt163_unpublished_justification],
        merge_bt196_bt163_unpublished_justification,
        "Procedure BT-196(BT-163)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-171)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt171_unpublished_justification],
        merge_bt196_bt171_unpublished_justification,
        "Procedure BT-196(BT-171)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-191)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt191_unpublished_justification],
        merge_bt196_bt191_unpublished_justification,
        "Procedure BT-196(BT-191)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-193)-Tender Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt193_unpublished_justification],
        merge_bt196_bt193_unpublished_justification,
        "Procedure BT-196(BT-193)-Tender Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-539)-Lot Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt539_unpublished_justification],
        merge_bt196_bt539_unpublished_justification,
        "Procedure BT-196(BT-539)-Lot Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-539)-LotsGroup Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt539_lotsgroup_unpublished_justification],
        merge_bt196_bt539_lotsgroup_unpublished_justification,
        "Procedure BT-196(BT-539)-LotsGroup Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-540)-Lot Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt540_lot_unpublished_justification],
        merge_bt196_bt540_lot_unpublished_justification,
        "Procedure BT-196(BT-540)-Lot Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-540)-LotsGroup Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt540_lotsgroup_unpublished_justification],
        merge_bt196_bt540_lotsgroup_unpublished_justification,
        "Procedure BT-196(BT-540)-LotsGroup Unpublished Justification Description",
    )

    # Parse and merge BT-196(BT-541)-Lot-Fixed Unpublished Justification Description
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt541_lot_fixed_unpublished_justification],
        merge_bt196_bt541_lot_fixed_unpublished_justification,
        "Procedure BT-196(BT-541)-Lot-Fixed Unpublished Justification Description",
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
        "Unpublished Justification Description for Lot Result Buyer Review Request Count (BT-196(BT-635))",
    )
    # Parse and merge BT-196(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt636_unpublished_justification],
        merge_bt196_bt636_unpublished_justification,
        "Unpublished Justification Description for Lot Result Buyer Review Request Irregularity Type (BT-196(BT-636))",
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
        "Unpublished Justification for Lot Result Buyer Review Complainants (BT-196(BT-712))",
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
    # Parse and merge BT-196(BT-88)-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt196_bt88_procedure_unpublished_justification],
        merge_bt196_bt88_procedure_unpublished_justification,
        "Unpublished Justification for Procedure Features (BT-196(BT-88))",
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

    # Parse and merge BT-197(BT-105)-Procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt105_unpublished_justification_code],
        merge_bt197_bt105_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-105)",
    )

    # Parse and merge BT-197(BT-106)-Procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt106_unpublished_justification_code],
        merge_bt197_bt106_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-106)",
    )

    # Parse and merge BT-197(BT-1252)-Procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt1252_unpublished_justification_code],
        merge_bt197_bt1252_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-1252)",
    )

    # Parse and merge BT-197(BT-135)-Procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt135_unpublished_justification_code],
        merge_bt197_bt135_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-135)",
    )

    # Parse and merge BT-197(BT-1351)-Procedure Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt1351_unpublished_justification_code],
        merge_bt197_bt1351_unpublished_justification_code,
        "Unpublished Justification Code (BT-197, BT-1351)",
    )

    # Parse and merge BT-197(BT-136)-Procedure Unpublished Justification Code
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
        "Procedure BT-197(BT-160)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-162)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt162_unpublished_justification_code],
        merge_bt197_bt162_unpublished_justification_code,
        "Procedure BT-197(BT-162)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-163)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt163_unpublished_justification_code],
        merge_bt197_bt163_unpublished_justification_code,
        "Procedure BT-197(BT-163)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-171)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt171_unpublished_justification_code],
        merge_bt197_bt171_unpublished_justification_code,
        "Procedure BT-197(BT-171)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-191)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt191_unpublished_justification_code],
        merge_bt197_bt191_unpublished_justification_code,
        "Procedure BT-197(BT-191)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-193)-Tender Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt193_unpublished_justification_code],
        merge_bt197_bt193_unpublished_justification_code,
        "Procedure BT-197(BT-193)-Tender Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-539)-Lot Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt539_unpublished_justification_code],
        merge_bt197_bt539_unpublished_justification_code,
        "Procedure BT-197(BT-539)-Lot Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-539)-LotsGroup Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt539_lotsgroup_unpublished_justification_code],
        merge_bt197_bt539_lotsgroup_unpublished_justification_code,
        "Procedure BT-197(BT-539)-LotsGroup Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-540)-Lot Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt540_lot_unpublished_justification_code],
        merge_bt197_bt540_lot_unpublished_justification_code,
        "Procedure BT-197(BT-540)-Lot Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-540)-LotsGroup Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt540_lotsgroup_unpublished_justification_code],
        merge_bt197_bt540_lotsgroup_unpublished_justification_code,
        "Procedure BT-197(BT-540)-LotsGroup Unpublished Justification Code",
    )

    # Parse and merge BT-197(BT-541)-Lot-Fixed Unpublished Justification Code
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt541_lot_fixed_unpublished_justification_code],
        merge_bt197_bt541_lot_fixed_unpublished_justification_code,
        "Procedure BT-197(BT-541)-Lot-Fixed Unpublished Justification Code",
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
        "Unpublished Justification Code for Lot Result Buyer Review Request Count (BT-197(BT-635))",
    )
    # Parse and merge BT-197(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt636_unpublished_justification_code],
        merge_bt197_bt636_unpublished_justification_code,
        "Unpublished Justification Code for Lot Result Buyer Review Request Irregularity Type (BT-197(BT-636))",
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
        "Unpublished Justification Code for Lot Result Buyer Review Complainants (BT-197(BT-712))",
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
    # Parse and merge BT-197(BT-88)-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt197_bt88_procedure_unpublished_justification_code],
        merge_bt197_bt88_procedure_unpublished_justification_code,
        "Unpublished Justification Code for Procedure Features (BT-197(BT-88))",
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

    # Parse and merge BT-198(BT-106)-Procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt106_unpublished_access_date],
        merge_bt198_bt106_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-106)",
    )

    # Parse and merge BT-198(BT-105)-Procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt105_unpublished_access_date],
        merge_bt198_bt105_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-105)",
    )

    # Parse and merge BT-198(BT-1252)-Procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt1252_unpublished_access_date],
        merge_bt198_bt1252_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-1252)",
    )

    # Parse and merge BT-198(BT-135)-Procedure Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt135_unpublished_access_date],
        merge_bt198_bt135_unpublished_access_date,
        "Unpublished Access Date (BT-198, BT-135)",
    )

    # Parse and merge BT-198(BT-1351)-Procedure Unpublished Access Date
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
        "Procedure BT-198(BT-160)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-162)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt162_unpublished_access_date],
        merge_bt198_bt162_unpublished_access_date,
        "Procedure BT-198(BT-162)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-163)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt163_unpublished_access_date],
        merge_bt198_bt163_unpublished_access_date,
        "Procedure BT-198(BT-163)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-171)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt171_unpublished_access_date],
        merge_bt198_bt171_unpublished_access_date,
        "Procedure BT-198(BT-171)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-191)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt191_unpublished_access_date],
        merge_bt198_bt191_unpublished_access_date,
        "Procedure BT-198(BT-191)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-193)-Tender Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt193_unpublished_access_date],
        merge_bt198_bt193_unpublished_access_date,
        "Procedure BT-198(BT-193)-Tender Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-539)-Lot Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt539_unpublished_access_date],
        merge_bt198_bt539_unpublished_access_date,
        "Procedure BT-198(BT-539)-Lot Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-539)-LotsGroup Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt539_lotsgroup_unpublished_access_date],
        merge_bt198_bt539_lotsgroup_unpublished_access_date,
        "Procedure BT-198(BT-539)-LotsGroup Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-540)-Lot Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt540_lot_unpublished_access_date],
        merge_bt198_bt540_lot_unpublished_access_date,
        "Procedure BT-198(BT-540)-Lot Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-540)-LotsGroup Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt540_lotsgroup_unpublished_access_date],
        merge_bt198_bt540_lotsgroup_unpublished_access_date,
        "Procedure BT-198(BT-540)-LotsGroup Unpublished Access Date",
    )

    # Parse and merge BT-198(BT-541)-Lot-Fixed Unpublished Access Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt541_lot_fixed_unpublished_access_date],
        merge_bt198_bt541_lot_fixed_unpublished_access_date,
        "Procedure BT-198(BT-541)-Lot-Fixed Unpublished Access Date",
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
        "Unpublished Access Date for Lot Result Buyer Review Request Count (BT-198(BT-635))",
    )
    # Parse and merge BT-198(BT-636)-LotResult
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt636_unpublished_access_date],
        merge_bt198_bt636_unpublished_access_date,
        "Unpublished Access Date for Lot Result Buyer Review Request Irregularity Type (BT-198(BT-636))",
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
        "Unpublished Access Date for Lot Result Buyer Review Complainants (BT-198(BT-712))",
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
    # Parse and merge BT-198(BT-88)-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt198_bt88_procedure_unpublished_access_date],
        merge_bt198_bt88_procedure_unpublished_access_date,
        "Unpublished Access Date for Procedure Features (BT-198(BT-88))",
    )

    # Process BT-200-Contract
    process_bt_section(
        release_json,
        xml_content,
        [parse_contract_modification_reason],
        merge_contract_modification_reason,
        "BT-200-Contract (Contract Modification Reason)",
    )

    # Parse and merge BT-198(BT-136)-Procedure Unpublished Access Date
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

    # Process BT-21-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_title],
        merge_part_title,
        "BT-21-Part (Part Title)",
    )

    # Process BT-21-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_title],
        merge_procedure_title,
        "BT-21-Procedure (Procedure Title)",
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

    # Process BT-23-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_nature_part],
        merge_main_nature_part,
        "BT-23-Part (Main Nature Part)",
    )

    # Process BT-23-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_nature_procedure],
        merge_main_nature_procedure,
        "BT-23-Procedure (Main Nature Procedure)",
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

    # Process BT-24-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_description],
        merge_part_description,
        "BT-24-Part (Part Description)",
    )

    # Process BT-24-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_description],
        merge_procedure_description,
        "BT-24-Procedure (Procedure Description)",
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

    # Process BT-26-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_classification_type_part],
        merge_classification_type_part,
        "BT-26-Part (Classification Type Part)",
    )

    # Process BT-26-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_classification_type_procedure],
        merge_classification_type_procedure,
        "BT-26-Procedure (Classification Type Procedure)",
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
        "Main Classification Type for Part (BT_26m_part)",
    )

    # Process Main Classification Type for BT_26m_procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_type_procedure],
        merge_main_classification_type_procedure,
        "Main Classification Type for Procedure (BT_26m_procedure)",
    )

    # Process Main Classification Code for Lot BT_262_lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_code_lot],
        merge_main_classification_code_lot,
        "Main Classification Code for Lot (BT_262_lot)",
    )

    # Process Main Classification Code for Part BT_262_part
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_code_part],
        merge_main_classification_code_part,
        "Main Classification Code for Part (BT_262_part)",
    )

    # Process Main Classification Code for Procedure BT_262_procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_classification_code_procedure],
        merge_main_classification_code_procedure,
        "Main Classification Code for Procedure (BT_262_procedure)",
    )

    # Process Additional Classification Code for Lot BT_263_lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_classification_code_lot],
        merge_additional_classification_code_lot,
        "Additional Classification Code for Lot (BT_263_lot)",
    )

    # Process Additional Classification Code for Part BT_263_part
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_classification_code_part],
        merge_additional_classification_code_part,
        "Additional Classification Code for Part (BT_263_part)",
    )

    # Process Additional Classification Code for Procedure BT_263_procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_additional_classification_code_procedure],
        merge_additional_classification_code_procedure,
        "Additional Classification Code for Procedure (BT_263_procedure)",
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

    # Process BT-27-Part Estimated Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_27_part],
        merge_bt_27_part,
        "Part Estimated Value (BT-27-Part)",
    )

    # Process BT-27-Procedure Estimated Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_27_procedure],
        merge_bt_27_procedure,
        "Procedure Estimated Value (BT-27-Procedure)",
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

    # Process BT-271-Procedure Framework Maximum Value
    process_bt_section(
        release_json,
        xml_content,
        [parse_bt_271_procedure],
        merge_bt_271_procedure,
        "Procedure Framework Maximum Value (BT-271-Procedure)",
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

    # Process BT-300-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_additional_info],
        merge_part_additional_info,
        "BT-300-Part (Part Additional Information)",
    )

    # Process BT-300-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_additional_info],
        merge_procedure_additional_info,
        "BT-300-Procedure (Procedure Additional Information)",
    )

    # Process BT-31-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_max_lots_allowed],
        merge_max_lots_allowed,
        "BT-31-Procedure (Maximum Lots Allowed)",
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

    # Process BT-36-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_duration],
        merge_part_duration,
        "BT-36-Part (Part Duration)",
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
        "BT-47-Lot (Participant Name)",
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
        "BT-500 (UBO Name)",
    )

    # Process BT-501
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_identifier],
        merge_organization_identifier,
        "BT-501 (Organization Identifier)",
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

    # Process BT-502-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_point],
        merge_organization_contact_point,
        "BT-502-Organization-Company (Organization Contact Point)",
    )

    # Process BT-502-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_point],
        merge_touchpoint_contact_point,
        "BT-502-Organization-TouchPoint (TouchPoint Contact Point)",
    )

    # Process BT-503-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_telephone],
        merge_organization_contact_telephone,
        "BT-503-Organization-Company (Organization Contact Telephone)",
    )

    # Process BT-503-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_telephone],
        merge_touchpoint_contact_telephone,
        "BT-503-Organization-TouchPoint (TouchPoint Contact Telephone)",
    )

    # Process BT-503-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_telephone],
        merge_ubo_telephone,
        "BT-503-UBO (UBO Telephone)",
    )

    # Process BT-505-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_website],
        merge_organization_website,
        "BT-505-Organization-Company (Organization Website)",
    )

    # Process BT-505-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_website],
        merge_touchpoint_website,
        "BT-505-Organization-TouchPoint (TouchPoint Website)",
    )

    # Process BT-506-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_email],
        merge_organization_contact_email,
        "BT-506-Organization-Company (Organization Contact Email)",
    )

    # Process BT-506-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_email],
        merge_touchpoint_contact_email,
        "BT-506-Organization-TouchPoint (TouchPoint Contact Email)",
    )

    # Process BT-506-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_email],
        merge_ubo_email,
        "BT-506-UBO (UBO Email)",
    )

    # Process BT-507-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_country_subdivision],
        merge_organization_country_subdivision,
        "BT-507-Organization-Company (Organization Country Subdivision)",
    )

    # Process BT-507-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_country_subdivision],
        merge_touchpoint_country_subdivision,
        "BT-507-Organization-TouchPoint (TouchPoint Country Subdivision)",
    )

    # Process BT-507-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_country_subdivision],
        merge_ubo_country_subdivision,
        "BT-507-UBO (UBO Country Subdivision)",
    )

    # Process BT-5071-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_country_subdivision],
        merge_place_performance_country_subdivision,
        "BT-5071-Lot (Place Performance Country Subdivision)",
    )

    # Parse and merge BT-5071 Place Performance Country Subdivision for Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_country_subdivision],
        merge_part_place_performance_country_subdivision,
        "Place Performance Country Subdivision Part (BT-5071)",
    )

    # Process BT-5071-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_country_subdivision],
        merge_procedure_place_performance_country_subdivision,
        "BT-5071-Procedure (Procedure Place Performance Country Subdivision)",
    )

    # Process BT-508-Procedure-Buyer
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_profile_url],
        merge_buyer_profile_url,
        "BT-508-Procedure-Buyer (Buyer Profile URL)",
    )

    # Process BT-509-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_edelivery_gateway],
        merge_organization_edelivery_gateway,
        "BT-509-Organization-Company (Organization eDelivery Gateway)",
    )

    # Process BT-509-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_edelivery_gateway],
        merge_touchpoint_edelivery_gateway,
        "BT-509-Organization-TouchPoint (TouchPoint eDelivery Gateway)",
    )

    # Process BT-51-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_maximum_candidates],
        merge_lot_maximum_candidates,
        "BT-51-Lot (Lot Maximum Candidates Number)",
    )

    # Process BT-510(a)-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_street],
        merge_organization_street,
        "BT-510(a)-Organization-Company (Organization Street)",
    )

    # Process BT-510(a)-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_street],
        merge_touchpoint_street,
        "BT-510(a)-Organization-TouchPoint (TouchPoint Street)",
    )

    # Process BT-510(a)-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_street],
        merge_ubo_street,
        "BT-510(a)-UBO (UBO Street)",
    )

    # Process BT-510(b)-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_streetline1],
        merge_organization_streetline1,
        "BT-510(b)-Organization-Company (Organization Streetline 1)",
    )

    # Process BT-510(b)-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_streetline1],
        merge_touchpoint_streetline1,
        "BT-510(b)-Organization-TouchPoint (TouchPoint Streetline 1)",
    )

    # Process BT-510(b)-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_streetline1],
        merge_ubo_streetline1,
        "BT-510(b)-UBO (UBO Streetline 1)",
    )

    # Process BT-510(c)-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_streetline2],
        merge_organization_streetline2,
        "BT-510(c)-Organization-Company (Organization Streetline 2)",
    )

    # Process BT-510(c)-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_streetline2],
        merge_touchpoint_streetline2,
        "BT-510(c)-Organization-TouchPoint (TouchPoint Streetline 2)",
    )

    # Process BT-510(c)-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_streetline2],
        merge_ubo_streetline2,
        "BT-510(c)-UBO (UBO Streetline 2)",
    )

    # Parse and merge BT-5101 Place Performance Street for Lot (including both a and b parts)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_street_lot],
        merge_place_performance_street_lot,
        "Place Performance Street Lot (BT-5101)",
    )

    # Process BT-5101(a)-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_street],
        merge_part_place_performance_street,
        "BT-5101(a)-Part (Part Place Performance Street)",
    )

    # Process BT-5101(a)-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_street],
        merge_procedure_place_performance_street,
        "BT-5101(a)-Procedure (Procedure Place Performance Street)",
    )

    # Process BT-5101(b)-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_streetline1],
        merge_part_place_performance_streetline1,
        "BT-5101(b)-Part (Part Place Performance Streetline 1)",
    )

    # Process BT-5101(b)-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_streetline1],
        merge_procedure_place_performance_streetline1,
        "BT-5101(b)-Procedure (Procedure Place Performance Streetline 1)",
    )

    # Process BT-5101(c)-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_streetline2],
        merge_part_place_performance_streetline2,
        "BT-5101(c)-Part (Part Place Performance Streetline 2)",
    )

    # Process BT-5101(c)-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_streetline2],
        merge_procedure_place_performance_streetline2,
        "BT-5101(c)-Procedure (Procedure Place Performance Streetline 2)",
    )

    # Process BT-512-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_postcode],
        merge_organization_postcode,
        "BT-512-Organization-Company (Organization Postcode)",
    )

    # Process BT-512-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_postcode],
        merge_touchpoint_postcode,
        "BT-512-Organization-TouchPoint (TouchPoint Postcode)",
    )

    # Process BT-512-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_postcode],
        merge_ubo_postcode,
        "BT-512-UBO (UBO Postcode)",
    )

    # Process BT-5121-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_post_code],
        merge_place_performance_post_code,
        "BT-5121-Lot (Place Performance Post Code)",
    )

    # Process BT-5121-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_post_code_part],
        merge_place_performance_post_code_part,
        "BT-5121-Part (Place Performance Post Code Part)",
    )
    # Process BT-5121-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_post_code_procedure],
        merge_place_performance_post_code_procedure,
        "BT-5121-Procedure (Place Performance Post Code)",
    )

    # Process BT-513-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_city],
        merge_organization_city,
        "BT-513-Organization-Company (Organization City)",
    )

    # Process BT-513-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_city],
        merge_touchpoint_city,
        "BT-513-Organization-TouchPoint (TouchPoint City)",
    )

    # Process BT-513-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_city],
        merge_ubo_city,
        "BT-513-UBO (UBO City)",
    )

    # Process BT-5131 (Place Performance City)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_city],
        merge_place_performance_city,
        "BT-5131 (Place Performance City)",
    )

    # Process BT-5131 Part (Place Performance City Part)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_city_part],
        merge_place_performance_city_part,
        "BT-5131 Part (Place Performance City Part)",
    )

    # Process BT-5131 Procedure (Place Performance City Procedure)
    process_bt_section(
        release_json,
        xml_content,
        [parse_place_performance_city_procedure],
        merge_place_performance_city_procedure,
        "BT-5131 Procedure (Place Performance City Procedure)",
    )

    # Process BT-514-Organization-Company
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_country],
        merge_organization_country,
        "BT-514-Organization-Company (Organization Country)",
    )

    # Process BT-514-Organization-TouchPoint
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_country],
        merge_touchpoint_country,
        "BT-514-Organization-TouchPoint (TouchPoint Country)",
    )

    # Process BT-514-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_country],
        merge_ubo_country,
        "BT-514-UBO (UBO Country)",
    )

    # Process BT-5141-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_country],
        merge_lot_country,
        "BT-5141-Lot (Lot Country)",
    )

    # Process BT-5141-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_country],
        merge_part_country,
        "BT-5141-Part (Part Country)",
    )

    # Process BT-5141-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_country],
        merge_procedure_country,
        "BT-5141-Procedure (Procedure Country)",
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

    # Process BT-531-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_additional_nature],
        merge_part_additional_nature,
        "BT-531-Part (Part Additional Nature)",
    )

    # Process BT-531-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_additional_nature],
        merge_procedure_additional_nature,
        "BT-531-Procedure (Procedure Additional Nature)",
    )

    # Process BT-536-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_start_date],
        merge_lot_start_date,
        "BT-536-Lot",
    )

    # Process BT-536-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_contract_start_date],
        merge_part_contract_start_date,
        "BT-536-Part",
    )

    # Process BT-537-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_duration_end_date],
        merge_lot_duration_end_date,
        "BT-537-Lot",
    )

    # Process BT-537-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_duration_end_date],
        merge_part_duration_end_date,
        "BT-537-Part",
    )

    # Process BT-538-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_duration_other],
        merge_lot_duration_other,
        "BT-538-Lot",
    )

    # Process BT-538-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_duration_other],
        merge_part_duration_other,
        "BT-538-Part",
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

    # Process BT-610-Procedure-Buyer (Activity Entity)
    process_bt_section(
        release_json,
        xml_content,
        [parse_activity_entity],
        merge_activity_entity,
        "BT-610-Procedure-Buyer (Activity Entity)",
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

    # Process BT-615-Part (Documents Restricted URL for Parts)
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_restricted_url_part],
        merge_documents_restricted_url_part,
        "BT-615-Part (Documents Restricted URL for Parts)",
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

    # Process BT-632-Part (Tool Name)
    process_bt_section(
        release_json,
        xml_content,
        [parse_tool_name_part],
        merge_tool_name_part,
        "BT-632-Part (Tool Name)",
    )

    # Process BT-633-Organization (Organisation Natural Person)
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_natural_person],
        merge_organization_natural_person,
        "BT-633-Organization (Organisation Natural Person)",
    )

    # Process BT-635-LotResult Buyer Review Requests Count
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_review_requests_count],
        merge_buyer_review_requests_count,
        "BT-635-LotResult Buyer Review Requests Count",
    )

    # Process BT-636-LotResult Buyer Review Requests Irregularity Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_irregularity_type],
        merge_irregularity_type,
        "BT-636-LotResult Buyer Review Requests Irregularity Type",
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

    # Process BT-702(a)-notice (Notice Official Language)
    process_bt_section(
        release_json,
        xml_content,
        [parse_notice_language],
        merge_notice_language,
        "BT-702(a)-notice (Notice Official Language)",
    )

    # Process BT-706-UBO Winner Owner Nationality
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_nationality],
        merge_ubo_nationality,
        "BT-706-UBO Winner Owner Nationality",
    )

    # Process BT-707-Lot (Documents Restricted Justification)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_documents_restricted_justification],
        merge_lot_documents_restricted_justification,
        "BT-707-Lot (Documents Restricted Justification)",
    )

    # Process BT-707-Part (Documents Restricted Justification)
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_documents_restricted_justification],
        merge_part_documents_restricted_justification,
        "BT-707-Part (Documents Restricted Justification)",
    )

    # Process BT-708-Lot (Documents Official Language)
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_documents_official_language],
        merge_lot_documents_official_language,
        "BT-708-Lot (Documents Official Language)",
    )

    # Process BT-708-Part (Documents Official Language)
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_documents_official_language],
        merge_part_documents_official_language,
        "BT-708-Part (Documents Official Language)",
    )

    # Process BT-709-LotResult (Framework Maximum Value)
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_maximum_value],
        merge_framework_maximum_value,
        "BT-709-LotResult (Framework Maximum Value)",
    )

    # Process BT-71-Lot (Reserved Participation)
    process_bt_section(
        release_json,
        xml_content,
        [parse_reserved_participation],
        merge_reserved_participation,
        "BT-71-Lot (Reserved Participation)",
    )

    # Process BT-71-Part (Reserved Participation)
    process_bt_section(
        release_json,
        xml_content,
        [parse_reserved_participation_part],
        merge_reserved_participation_part,
        "BT-71-Part (Reserved Participation)",
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

    # Process BT-712(a)-LotResult Buyer Review Complainants
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_review_complainants],
        merge_buyer_review_complainants,
        "BT-712(a)-LotResult Buyer Review Complainants",
    )

    # Process BT-712(b)-LotResult Buyer Review Complainants (Number)
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_review_complainants_bt_712b],
        merge_buyer_review_complainants_bt_712b,
        "BT-712(b)-LotResult Buyer Review Complainants (Number)",
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

    # Process BT-726-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_sme_suitability],
        merge_part_sme_suitability,
        "Part SME Suitability (BT-726-Part)",
    )

    # Process BT-727-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_place_performance],
        merge_lot_place_performance,
        "Lot Place of Performance (BT-727-Lot)",
    )

    # Process BT-727-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance],
        merge_part_place_performance,
        "Part Place of Performance (BT-727-Part)",
    )

    # Process BT-727-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance],
        merge_procedure_place_performance,
        "Procedure Place of Performance (BT-727-Procedure)",
    )

    # Process BT-728-Lot
    process_bt_section(
        release_json,
        xml_content,
        [parse_lot_place_performance_additional],
        merge_lot_place_performance_additional,
        "Additional Lot Place of Performance (BT-728-Lot)",
    )

    # Process BT-728-Part
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_place_performance_additional],
        merge_part_place_performance_additional,
        "Additional Part Place of Performance (BT-728-Part)",
    )

    # Process BT-728-Procedure
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_place_performance_additional],
        merge_procedure_place_performance_additional,
        "Additional Procedure Place of Performance (BT-728-Procedure)",
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

    # Process BT-736-Part Reserved Execution
    process_bt_section(
        release_json,
        xml_content,
        [parse_reserved_execution_part],
        merge_reserved_execution_part,
        "Part Reserved Execution (BT-736-Part)",
    )

    # Process BT-737-Lot Documents Unofficial Language
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_unofficial_language],
        merge_documents_unofficial_language,
        "Lot Documents Unofficial Language (BT-737-Lot)",
    )

    # Process BT-737-Part Documents Unofficial Language
    process_bt_section(
        release_json,
        xml_content,
        [parse_documents_unofficial_language_part],
        merge_documents_unofficial_language_part,
        "Part Documents Unofficial Language (BT-737-Part)",
    )

    # Process BT-738-notice Notice Preferred Publication Date
    process_bt_section(
        release_json,
        xml_content,
        [parse_notice_preferred_publication_date],
        merge_notice_preferred_publication_date,
        "Notice Preferred Publication Date (BT-738-notice)",
    )

    # Process BT-739-Organization-Company Organisation Contact Fax
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_contact_fax],
        merge_organization_contact_fax,
        "Organisation Contact Fax (BT-739-Organization-Company)",
    )

    # Process BT-739-Organization-TouchPoint Contact Fax
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_contact_fax],
        merge_touchpoint_contact_fax,
        "TouchPoint Contact Fax (BT-739-Organization-TouchPoint)",
    )

    # Process BT-739-UBO UBO Contact Fax
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_fax],
        merge_ubo_fax,
        "UBO Contact Fax (BT-739-UBO)",
    )

    # Process BT-740-Procedure-Buyer Buyer Contracting Entity
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyer_contracting_entity],
        merge_buyer_contracting_entity,
        "Buyer Contracting Entity (BT-740-Procedure-Buyer)",
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

    # Process BT-746-Organization Winner Listed
    process_bt_section(
        release_json,
        xml_content,
        [parse_winner_listed],
        merge_winner_listed,
        "Organization Winner Listed (BT-746-Organization)",
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

    # Process BT-756-Procedure PIN Competition Termination
    process_bt_section(
        release_json,
        xml_content,
        [parse_pin_competition_termination],
        merge_pin_competition_termination,
        "PIN Competition Termination (BT-756-Procedure)",
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

    # Process BT-763-Procedure Lots All Required
    process_bt_section(
        release_json,
        xml_content,
        [parse_lots_all_required],
        merge_lots_all_required,
        "Lots All Required (BT-763-Procedure)",
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

    # Process BT-765-Part Framework Agreement
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_framework_agreement],
        merge_part_framework_agreement,
        "Part Framework Agreement (BT-765-Part)",
    )

    # Process BT-766-Lot Dynamic Purchasing System
    process_bt_section(
        release_json,
        xml_content,
        [parse_dynamic_purchasing_system],
        merge_dynamic_purchasing_system,
        "Dynamic Purchasing System (BT-766-Lot)",
    )

    # Process BT-766-Part Dynamic Purchasing System
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_dynamic_purchasing_system],
        merge_part_dynamic_purchasing_system,
        "Part Dynamic Purchasing System (BT-766-Part)",
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

    # Process BT-88-Procedure Procedure Features
    process_bt_section(
        release_json,
        xml_content,
        [parse_procedure_features],
        merge_procedure_features,
        "Procedure Features (BT-88-Procedure)",
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

    # Process OPP-040-Procedure Main Nature - Sub Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_main_nature_sub_type],
        merge_main_nature_sub_type,
        "Main Nature - Sub Type (OPP-040-Procedure)",
    )

    # Process OPP-050-Organization Buyers Group Lead Indicator
    process_bt_section(
        release_json,
        xml_content,
        [parse_buyers_group_lead_indicator],
        merge_buyers_group_lead_indicator,
        "Buyers Group Lead Indicator (OPP-050-Organization)",
    )

    # Process OPP-051-Organization Awarding CPB Buyer Indicator
    process_bt_section(
        release_json,
        xml_content,
        [parse_awarding_cpb_buyer_indicator],
        merge_awarding_cpb_buyer_indicator,
        "Awarding CPB Buyer Indicator (OPP-051-Organization)",
    )

    # Process OPP-052-Organization Acquiring CPB Buyer Indicator
    process_bt_section(
        release_json,
        xml_content,
        [parse_acquiring_cpb_buyer_indicator],
        merge_acquiring_cpb_buyer_indicator,
        "Acquiring CPB Buyer Indicator (OPP-052-Organization)",
    )

    # Process OPP-080-Tender Kilometers Public Transport
    process_bt_section(
        release_json,
        xml_content,
        [parse_kilometers_public_transport],
        merge_kilometers_public_transport,
        "Kilometers Public Transport (OPP-080-Tender)",
    )

    # Process OPP-090-Procedure Previous Notice Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_previous_notice_identifier],
        merge_previous_notice_identifier,
        "Previous Notice Identifier (OPP-090-Procedure)",
    )

    # Process OPT-030-Procedure-SProvider Provided Service Type
    process_bt_section(
        release_json,
        xml_content,
        [parse_provided_service_type],
        merge_provided_service_type,
        "Provided Service Type (OPT-030-Procedure-SProvider)",
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

    # Process OPP-100-Contract Framework Notice Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_framework_notice_identifier],
        merge_framework_notice_identifier,
        "Framework Notice Identifier (OPP-100-Contract)",
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

    # Process OPT-160-UBO First Name
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_first_name],
        merge_ubo_first_name,
        "UBO First Name (OPT-160-UBO)",
    )

    # Process OPT-170-Tenderer Tendering Party Leader
    process_bt_section(
        release_json,
        xml_content,
        [parse_tendering_party_leader],
        merge_tendering_party_leader,
        "Tendering Party Leader (OPT-170-Tenderer)",
    )

    # Process OPT-200-Organization-Company Organization Technical Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_organization_technical_identifier],
        merge_organization_technical_identifier,
        "Organization Technical Identifier (OPT-200-Organization-Company)",
    )

    # Process OPT-201-Organization-TouchPoint TouchPoint Technical Identifier
    process_bt_section(
        release_json,
        xml_content,
        [parse_touchpoint_technical_identifier],
        merge_touchpoint_technical_identifier,
        "TouchPoint Technical Identifier (OPT-201-Organization-TouchPoint)",
    )

    # Process OPT-202-UBO
    process_bt_section(
        release_json,
        xml_content,
        [parse_ubo_identifier],
        merge_ubo_identifier,
        "UBO Identifier (OPT-202-UBO)",
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
        "Procedure Service Provider (OPT-300)",
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

    # Process OPT-301-Lot-EmployLegis Employment Legislation Organization Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_employment_legislation_document_reference],
        merge_employment_legislation_document_reference,
        "Employment Legislation Organization Technical Identifier Reference (OPT-301-Lot-EmployLegis)",
    )

    # Process OPT-301-Lot-EnvironLegis Environmental Legislation Organization Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_environmental_legislation_document_reference],
        merge_environmental_legislation_document_reference,
        "Environmental Legislation Organization Technical Identifier Reference (OPT-301-Lot-EnvironLegis)",
    )

    # Process OPT-301-Lot-ReviewOrg Review Organization Technical Identifier Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_review_org_identifier],
        merge_review_org_identifier,
        "Review Organization Technical Identifier Reference (OPT-301-Lot-ReviewOrg)",
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

    # Process OPT-301 Part_AddInfo
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_addinfo],
        merge_part_addinfo,
        "Part Additional Info (OPT-301)",
    )

    # Process OPT_301_Part_DocProvider
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_docprovider],
        merge_part_docprovider,
        "Part Document Provider (OPT_301)",
    )

    # Process OPT_301_Part_EmployLegis
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_employlegis],
        merge_part_employlegis,
        "Part Employment Legislation (OPT_301)",
    )

    # Process OPT_301_Part_EnvironLegis
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_environlegis],
        merge_part_environlegis,
        "Part Environmental Legislation (OPT_301)",
    )

    # Process OPT_301_Part_FiscalLegis
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_fiscallegis],
        merge_part_fiscallegis,
        "Part Fiscal Legislation (OPT_301)",
    )

    # Process OPT_301_Part_Mediator
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_mediator],
        merge_part_mediator,
        "Part Mediator (OPT_301)",
    )

    # Process OPT_301_Part_ReviewInfo
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_reviewinfo],
        merge_part_reviewinfo,
        "Part Review Info (OPT_301)",
    )

    # Process OPT_301_Part_ReviewOrg
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_revieworg],
        merge_part_revieworg,
        "Part Review Organization (OPT_301)",
    )

    # Process OPT_301_Part_TenderEval
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_tendereval],
        merge_part_tendereval,
        "Part Tender Evaluator (OPT_301)",
    )

    # Process OPT_301_Part_TenderReceipt
    process_bt_section(
        release_json,
        xml_content,
        [parse_part_tenderreceipt],
        merge_part_tenderreceipt,
        "Part Tender Recipient (OPT_301)",
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

    # Process OPT-302-Organization Beneficial Owner Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_beneficial_owner_reference],
        merge_beneficial_owner_reference,
        "Beneficial Owner Reference (OPT-302-Organization)",
    )

    # Process OPT-310-Tender Tendering Party ID Reference
    process_bt_section(
        release_json,
        xml_content,
        [parse_tendering_party_id_reference],
        merge_tendering_party_id_reference,
        "Tendering Party ID Reference (OPT-310-Tender)",
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
    with open("output.json", "w", encoding="utf-8") as f:
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
