# converters/Common_operations.py
import json
import uuid
from datetime import datetime
from lxml import etree

class NoticeProcessor:
    def __init__(self, ocid_prefix):
        self.ocid_prefix = ocid_prefix
        self.item_id_counter = 1

    def create_release(self, xml_string):
        tree = etree.fromstring(xml_string)

        # Extract notice identifier
        notice_id = tree.xpath('string(/*/cbc:ID)',
                               namespaces={'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})

        # Create an empty JSON object
        release = {}
        release['id'] = notice_id
        release['initiationType'] = 'tender'

        # Determine if this is the first publication or a follow-up notice
        is_first_publication = self.is_first_publication(tree)
        is_can_for_framework = self.is_can_for_framework(tree)
        is_pin_only = self.is_pin_only(tree)

        if is_first_publication or is_can_for_framework or is_pin_only:
            release['ocid'] = f"{self.ocid_prefix}-{uuid.uuid4()}"
        else:
            previous_ocid = self.get_previous_ocid(tree)
            release['ocid'] = previous_ocid

        if is_pin_only and len(tree.xpath('/*/cac:ProcurementProjectLot[cbc:ID/@schemeName="Part"]', namespaces={
                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})) > 1:
            self.add_related_processes(tree, release)

        # Format dates to ISO format
        self.format_dates_to_iso(tree, release)

        # Add documents and participation fees
        self.add_documents_and_fees(tree, release)

        # Add parties
        self.add_parties(tree, release)

        # Add lots, lot groups, items, bids, awards, and contracts
        self.add_lots_and_items(tree, release)
        self.add_bids(tree, release)
        self.add_awards(tree, release)
        self.add_contracts(tree, release)
        self.cleanup_empty_fields(release)

        return json.dumps(release, indent=4)

    def cleanup_empty_fields(self, obj):
        if isinstance(obj, dict):
            keys_to_remove = []
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    self.cleanup_empty_fields(v)
                if v in [None, {}, [], ""]:
                    keys_to_remove.append(k)
            for k in keys_to_remove:
                del obj[k]
        elif isinstance(obj, list):
            obj[:] = [v for v in obj if v not in [None, {}, [], ""]]
            for item in obj:
                self.cleanup_empty_fields(item)

    def is_first_publication(self, tree):
        # Implement logic to determine if this is the first publication
        return True

    def is_can_for_framework(self, tree):
        # Implement logic to determine if this is a CAN for framework
        return False

    def is_pin_only(self, tree):
        # Implement logic to determine if the previous publication was PIN only
        return False

    def get_previous_ocid(self, tree):
        # Implement logic to retrieve the previous ocid
        return "previous-ocid"

    def add_related_processes(self, tree, release):
        related_processes = []
        parts = tree.xpath('/*/cac:ProcurementProjectLot[cbc:ID/@schemeName="Part"]', namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})

        for part in parts:
            related_process = {}
            related_process['id'] = '1'
            related_process['relationship'] = ['planning']
            related_process['scheme'] = 'eu-oj'  # You can modify this if necessary
            related_process['identifier'] = part.xpath('string(cbc:ID)',
                                                       namespaces={
                                                           'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            related_processes.append(related_process)

        release['relatedProcesses'] = related_processes

    def format_dates_to_iso(self, tree, release):
        date_fields = tree.xpath('//*[contains(name(), "Date") or contains(name(), "date")]', namespaces={
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})

        for field in date_fields:
            date_text = field.text
            if date_text:
                formatted_date = self.to_iso_format(date_text)
                field.text = formatted_date

    def to_iso_format(self, date_text):
        try:
            date_obj = datetime.strptime(date_text, '%Y-%m-%dT%H:%M:%S%z')
        except ValueError:
            try:
                date_obj = datetime.strptime(date_text, '%Y-%m-%d')
                # Check if the date is an end date or not
                if 'end' in date_text.lower():
                    date_obj = date_obj.replace(hour=23, minute=59, second=59)
                else:
                    date_obj = date_obj.replace(hour=0, minute=0, second=0)
                date_text = date_obj.isoformat() + 'Z'
            except ValueError:
                date_text = 'Invalid date format'

        return date_text

    def add_documents_and_fees(self, tree, release):
        tender = release.setdefault('tender', {})
        tender.setdefault('documents', [])
        tender.setdefault('participationFees', [])
        tender.setdefault('lots', [])

        documents = tender['documents']
        participation_fees = tender['participationFees']
        lots = tender['lots']

        # Add documents
        document_references = tree.xpath('//cac:DocumentReference', namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for doc_ref in document_references:
            doc_id = doc_ref.xpath('string(cbc:ID)',
                                   namespaces={
                                       'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            document = next((doc for doc in documents if doc['id'] == doc_id), None)
            if not document:
                documents.append({'id': doc_id})

        # Add participation fees
        project_lots = tree.xpath('//cac:ProcurementProjectLot', namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for lot in project_lots:
            lot_id = lot.xpath('string(cbc:ID)',
                               namespaces={
                                   'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            scheme_name = lot.xpath('string(cbc:ID/@schemeName)',
                                    namespaces={
                                        'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            call_for_tenders_doc_id = lot.xpath('string(cac:CallForTendersDocumentReference/cbc:ID)',
                                                namespaces={
                                                    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                                                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})

            if scheme_name == 'Part':
                participation_fee = next((fee for fee in participation_fees if fee['id'] == call_for_tenders_doc_id),
                                         None)
                if not participation_fee and call_for_tenders_doc_id:
                    participation_fees.append({'id': call_for_tenders_doc_id})
            elif scheme_name == 'Lot':
                lot_obj = next((lot for lot in lots if lot['id'] == lot_id), None)
                if not lot_obj:
                    lot_obj = {'id': lot_id, 'participationFees': []}
                    lots.append(lot_obj)
                participation_fee = next((fee for fee in lot_obj['participationFees'] if fee['id'] == call_for_tenders_doc_id), None)
                if not participation_fee and call_for_tenders_doc_id:
                    lot_obj['participationFees'].append({'id': call_for_tenders_doc_id})

    def add_parties(self, tree, release):
        parties = release.setdefault('parties', [])

        def get_or_add_organization(party_id, party_details=None, roles=None):
            organization = next((party for party in parties if party['id'] == party_id), None)
            if not organization:
                organization = {'id': party_id}
                if party_details:
                    organization.update(party_details)
                if roles:
                    organization['roles'] = roles
                parties.append(organization)
            elif roles:
                organization.setdefault('roles', []).extend(roles)
                organization['roles'] = list(set(organization['roles']))  # Remove duplicates
            return organization

        # Process company organizations
        company_refs = tree.xpath('//efac:Organization/efac:Company', namespaces={
            'efac': 'http://example.com/efac',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for company_ref in company_refs:
            party_id = company_ref.xpath('string(cac:PartyIdentification/cbc:ID)',
                                         namespaces={
                                             'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                                             'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_organization(party_id)

        # Process touchpoints
        touchpoint_refs = tree.xpath('//efac:TouchPoint', namespaces={
            'efac': 'http://example.com/efac',
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for touchpoint_ref in touchpoint_refs:
            party_id = touchpoint_ref.xpath('string(cac:PartyIdentification/cbc:ID)',
                                            namespaces={
                                                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                                                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            organization_details = {
                'identifier': {
                    'id': touchpoint_ref.xpath('string(ancestor::efac:Organization/efac:Company/cac:PartyLegalEntity/cbc:CompanyID)',
                                               namespaces={
                                                   'efac': 'http://example.com/efac',
                                                   'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                                                   'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}),
                    'scheme': 'example-scheme'  # Replace with appropriate scheme
                }
            }
            get_or_add_organization(party_id, organization_details)

        # Process buyers
        buyer_refs = tree.xpath('//cac:ContractingParty/cac:Party', namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for buyer_ref in buyer_refs:
            party_id = buyer_ref.xpath('string(cac:PartyIdentification/cbc:ID)',
                                       namespaces={
                                           'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                                           'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_organization(party_id, roles=['buyer'])

        # Process tenderers
        tenderer_refs = tree.xpath('//efac:TenderingParty/efac:Tenderer', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for tenderer_ref in tenderer_refs:
            party_id = tenderer_ref.xpath('string(cbc:ID)',
                                          namespaces={
                                              'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_organization(party_id, roles=['tenderer'])

        # Process ultimate beneficial owners
        ubo_refs = tree.xpath('//efac:UltimateBeneficialOwner', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for ubo_ref in ubo_refs:
            organization_id = ubo_ref.xpath('string(ancestor::efac:Organization/efac:Company/cac:PartyIdentification/cbc:ID)',
                                            namespaces={
                                                'efac': 'http://example.com/efac',
                                                'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
                                                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            organization = get_or_add_organization(organization_id)
            person_id = ubo_ref.xpath('string(cbc:ID)',
                                      namespaces={
                                          'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            beneficial_owners = organization.setdefault('beneficialOwners', [])
            person = next((person for person in beneficial_owners if person['id'] == person_id), None)
            if not person:
                beneficial_owners.append({'id': person_id})

        # Process organization technical identifier references
        org_tech_id_refs = tree.xpath('//cbc:ID', namespaces={
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for org_tech_id_ref in org_tech_id_refs:
            party_id = org_tech_id_ref.text
            get_or_add_organization(party_id)

    def add_lots_and_items(self, tree, release):
        tender = release.setdefault('tender', {})
        tender.setdefault('lots', [])
        tender.setdefault('lotGroups', [])
        tender.setdefault('items', [])

        lots = tender['lots']
        lot_groups = tender['lotGroups']
        items = tender['items']

        def get_or_add_lot(lot_id):
            lot = next((lot for lot in lots if lot['id'] == lot_id), None)
            if not lot:
                lot = {'id': lot_id}
                lots.append(lot)
            return lot

        def get_or_add_lot_group(lot_group_id):
            lot_group = next((lot_group for lot_group in lot_groups if lot_group['id'] == lot_group_id), None)
            if not lot_group:
                lot_group = {'id': lot_group_id}
                lot_groups.append(lot_group)
            return lot_group

        def get_or_add_item(related_lot_id):
            item = next((item for item in items if item['relatedLot'] == related_lot_id), None)
            if not item:
                item = {'id': str(self.item_id_counter), 'relatedLot': related_lot_id}
                self.item_id_counter += 1
                items.append(item)
            return item

        # Get the lot for a ProcurementProjectLot
        project_lots = tree.xpath('//cac:ProcurementProjectLot', namespaces={
            'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for lot in project_lots:
            lot_id = lot.xpath('string(cbc:ID)', namespaces={
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_lot(lot_id)

        # Get the lot group for a ProcurementProjectLot
        for lot in project_lots:
            lot_group_id = lot.xpath('string(cbc:ID)', namespaces={
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_lot_group(lot_group_id)

        # Get the item for a ProcurementProjectLot
        for lot in project_lots:
            related_lot_id = lot.xpath('string(cbc:ID)', namespaces={
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_item(related_lot_id)

        # Get the lot for a LotResult
        lot_results = tree.xpath('//efac:LotResult', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for lot_result in lot_results:
            lot_id = lot_result.xpath('string(efac:TenderLot/cbc:ID)', namespaces={
                'efac': 'http://example.com/efac',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_lot(lot_id)

        # Get the lots for a SettledContract
        settled_contracts = tree.xpath('//efac:SettledContract', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for settled_contract in settled_contracts:
            settled_contract_id = settled_contract.xpath('string(cbc:ID)', namespaces={
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            lot_results = tree.xpath(f'//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID="{settled_contract_id}"]', namespaces={
                'efac': 'http://example.com/efac',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            for lot_result in lot_results:
                lot_id = lot_result.xpath('string(efac:TenderLot/cbc:ID)', namespaces={
                    'efac': 'http://example.com/efac',
                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
                get_or_add_lot(lot_id)

        # Get the lot for a LotTender
        lot_tenders = tree.xpath('//efac:LotTender', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for lot_tender in lot_tenders:
            lot_id = lot_tender.xpath('string(efac:TenderLot/cbc:ID)', namespaces={
                'efac': 'http://example.com/efac',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            get_or_add_lot(lot_id)

    def add_bids(self, tree, release):
        bids = release.setdefault('bids', {}).setdefault('details', [])

        def get_or_add_bid(bid_id):
            bid = next((bid for bid in bids if bid['id'] == bid_id), None)
            if not bid:
                bid = {'id': bid_id, 'relatedLots': []}
                bids.append(bid)
            return bid

        # Get the bid for a LotTender
        lot_tenders = tree.xpath('//efac:LotTender', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for lot_tender in lot_tenders:
            bid_id = lot_tender.xpath('string(cbc:ID)', namespaces={
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            related_lot_id = lot_tender.xpath('string(efac:TenderLot/cbc:ID)', namespaces={
                'efac': 'http://example.com/efac',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            bid = get_or_add_bid(bid_id)
            if related_lot_id not in bid['relatedLots']:
                bid['relatedLots'].append(related_lot_id)

    def add_awards(self, tree, release):
        awards = release.setdefault('awards', [])

        def get_or_add_award(award_id):
            award = next((award for award in awards if award['id'] == award_id), None)
            if not award:
                award = {'id': award_id, 'relatedLots': []}
                awards.append(award)
            return award

        # Get the award for a LotResult
        lot_results = tree.xpath('//efac:LotResult', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for lot_result in lot_results:
            award_id = lot_result.xpath('string(cbc:ID)', namespaces={
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            related_lot_id = lot_result.xpath('string(efac:TenderLot/cbc:ID)', namespaces={
                'efac': 'http://example.com/efac',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            award = get_or_add_award(award_id)
            if related_lot_id not in award['relatedLots']:
                award['relatedLots'].append(related_lot_id)

    def add_contracts(self, tree, release):
        contracts = release.setdefault('contracts', [])

        def get_or_add_contract(contract_id):
            contract = next((contract for contract in contracts if contract['id'] == contract_id), None)
            if not contract:
                contract = {'id': contract_id, 'awardID': [], 'awardIDs': []}
                contracts.append(contract)
            return contract

        # Get the contract for a SettledContract
        settled_contracts = tree.xpath('//efac:SettledContract', namespaces={
            'efac': 'http://example.com/efac',
            'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
        for settled_contract in settled_contracts:
            contract_id = settled_contract.xpath('string(cbc:ID)', namespaces={
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            contract = get_or_add_contract(contract_id)
            lot_results = tree.xpath(f'//efac:NoticeResult/efac:LotResult[efac:SettledContract/cbc:ID="{contract_id}"]', namespaces={
                'efac': 'http://example.com/efac',
                'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            if len(lot_results) == 1:
                contract['awardID'] = lot_results[0].xpath('string(cbc:ID)', namespaces={
                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'})
            else:
                contract['awardIDs'] = [lot_result.xpath('string(cbc:ID)', namespaces={
                    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'}) for lot_result in lot_results]
