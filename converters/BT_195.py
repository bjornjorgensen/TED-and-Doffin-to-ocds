"""
Missing
BT-195(BT-555)-Tender 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-per']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotTender/cbc:ID].

Set its .field to "sub-per".

Set its .name to "Subcontracting Percentage".

<efac:NoticeResult>
  <efac:LotTender>
    <cbc:ID schemeName="result">TEN-0001</cbc:ID>
    <efac:SubcontractingTerm>
      <efac:FieldsPrivacy>
        <efbc:FieldIdentifierCode listName="non-publication-identifier">sub-per</efbc:FieldIdentifierCode>
      </efac:FieldsPrivacy>
    </efac:SubcontractingTerm>
  </efac:LotTender>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "sub-per",
      "id": "sub-per-TEN-0001",
      "name": "Subcontracting Percentage"
    }
  ]
}
BT-195(BT-556)-NoticeResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:GroupFramework/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='gro-max-ide']/efbc:FieldIdentifierCode	
Discard.

<efac:FieldsPrivacy>
  <efbc:FieldIdentifierCode listName="non-publication-identifier">gro-max-ide</efbc:FieldIdentifierCode>
</efac:FieldsPrivacy>
BT-195(BT-635)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='buy-rev-cou']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "buy-rev-cou".

Set its .name to "Buyer Review Request Count".

<efac:NoticeResult>
  <efac:LotResult>
    <efac:AppealRequestsStatistics>
      <efac:FieldsPrivacy>
        <efbc:FieldIdentifierCode listName="non-publication-identifier">buy-rev-cou</efbc:FieldIdentifierCode>
      </efac:FieldsPrivacy>
    </efac:AppealRequestsStatistics>
    <cbc:ID schemeName="result">RES-0001</cbc:ID>
  </efac:LotResult>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "buy-rev-cou",
      "id": "buy-rev-cou-RES-0001",
      "name": "Buyer Review Request Count"
    }
  ]
}
BT-195(BT-636)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='irregularity-type']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='buy-rev-typ']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "buy-rev-typ".

Set its .name to "Buyer Review Requests Irregularity Type".

<efac:NoticeResult>
  <efac:LotResult>
    <efac:AppealRequestsStatistics>
      <efac:FieldsPrivacy>
        <efbc:FieldIdentifierCode listName="non-publication-identifier">buy-rev-typ</efbc:FieldIdentifierCode>
      </efac:FieldsPrivacy>
    </efac:AppealRequestsStatistics>
    <cbc:ID schemeName="result">RES-0001</cbc:ID>
  </efac:LotResult>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "buy-rev-typ",
      "id": "buy-rev-typ-RES-0001",
      "name": "Buyer Review Request Irregularity Type"
    }
  ]
}
BT-195(BT-660)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FrameworkAgreementValues/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='ree-val']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "ree-val".

Set its .name to "Framework Re-estimated Value".

<efac:NoticeResult>
  <efac:LotResult>
    <efac:FrameworkAgreementValues>
      <efac:FieldsPrivacy>
        <efbc:FieldIdentifierCode listName="non-publication-identifier">ree-val</efbc:FieldIdentifierCode>
      </efac:FieldsPrivacy>
    </efac:FrameworkAgreementValues>
    <cbc:ID schemeName="result">RES-0001</cbc:ID>
  </efac:LotResult>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "ree-val",
      "id": "ree-val-RES-0001",
      "name": "Framework Re-estimated Value"
    }
  ]
}
BT-195(BT-709)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FrameworkAgreementValues/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='max-val']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "max-val".

Set its .name to "Maximum Value".

<efac:NoticeResult>
  <efac:LotResult>
    <efac:FrameworkAgreementValues>
      <efac:FieldsPrivacy>
        <efbc:FieldIdentifierCode listName="non-publication-identifier">max-val</efbc:FieldIdentifierCode>
      </efac:FieldsPrivacy>
    </efac:FrameworkAgreementValues>
    <cbc:ID schemeName="result">RES-0001</cbc:ID>
  </efac:LotResult>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "max-val",
      "id": "max-val-RES-0001",
      "name": "Maximum Value"
    }
  ]
}
BT-195(BT-710)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='ten-val-low']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "ten-val-low".

Set its .name to "Tender Lowest Value".

<efac:NoticeResult>
  <efac:LotResult>
    <efac:FieldsPrivacy>
      <efbc:FieldIdentifierCode listName="non-publication-identifier">ten-val-low</efbc:FieldIdentifierCode>
    </efac:FieldsPrivacy>
    <cbc:ID schemeName="result">RES-0001</cbc:ID>
  </efac:LotResult>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "ten-val-low",
      "id": "ten-val-low-RES-0001",
      "name": "Tender Lowest Value"
    }
  ]
}
BT-195(BT-711)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='ten-val-hig']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "ten-val-hig".

Set its .name to "Tender Highest Value".

<efac:NoticeResult>
  <efac:LotResult>
    <efac:FieldsPrivacy>
      <efbc:FieldIdentifierCode listName="non-publication-identifier">ten-val-hig</efbc:FieldIdentifierCode>
    </efac:FieldsPrivacy>
    <cbc:ID schemeName="result">RES-0001</cbc:ID>
  </efac:LotResult>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "ten-val-hig",
      "id": "ten-val-hig-RES-0001",
      "name": "Tender Highest Value"
    }
  ]
}
BT-195(BT-712)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:AppealRequestsStatistics[efbc:StatisticsCode/@listName='review-type']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='rev-req']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "rev-req".

Set its .name to "Buyer Review Complainants".

<efac:NoticeResult>
  <efac:LotResult>
    <efac:AppealRequestsStatistics>
      <efac:FieldsPrivacy>
        <efbc:FieldIdentifierCode listName="non-publication-identifier">rev-rec</efbc:FieldIdentifierCode>
      </efac:FieldsPrivacy>
    </efac:AppealRequestsStatistics>
    <cbc:ID schemeName="result">RES-0001</cbc:ID>
  </efac:LotResult>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "rev-req",
      "id": "rev-req-RES-0001",
      "name": "Buyer Review Complainants"
    }
  ]
}
BT-195(BT-720)-Tender 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-ten-val']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotTender/cbc:ID].

Set its .field to "win-ten-val".

Set its .name to "Winning Tender Value".

<efac:NoticeResult>
  <efac:LotTender>
    <cbc:ID schemeName="result">TEN-0001</cbc:ID>
    <efac:FieldsPrivacy>
      <efbc:FieldIdentifierCode listName="non-publication-identifier">win-ten-val</efbc:FieldIdentifierCode>
    </efac:FieldsPrivacy>
  </efac:LotTender>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "win-ten-val",
      "id": "win-ten-val-TEN-0001",
      "name": "Winning Tender Value"
    }
  ]
}
BT-195(BT-730)-Tender 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-val-kno']/efbc:FieldIdentifierCode	
Discard. BT-730 is discarded as it is implied by BT-553.

<efac:FieldsPrivacy>
  <efbc:FieldIdentifierCode listName="non-publication-identifier">sub-val-kno</efbc:FieldIdentifierCode>
</efac:FieldsPrivacy>
BT-195(BT-731)-Tender 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-per-kno']/efbc:FieldIdentifierCode	
Discard. BT-731 is discarded as it is implied by BT-555.

<efac:FieldsPrivacy>
  <efbc:FieldIdentifierCode listName="non-publication-identifier">sub-per-kno</efbc:FieldIdentifierCode>
</efac:FieldsPrivacy>
BT-195(BT-733)-Lot 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-ord']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::cac:ProcurementProjectLot/cbc:ID schemeName="Lot"].

Set its .field to "awa-cri-ord".

Set its .name to "Award Criteria Order Justification".

<cac:ProcurementProjectLot>
  <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
  <cac:TenderingTerms>
    <cac:AwardingTerms>
      <cac:AwardingCriterion>
        <cac:SubordinateAwardingCriterion>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode listName="non-publication-identifier">awa-cri-ord</efbc:FieldIdentifierCode>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:SubordinateAwardingCriterion>
      </cac:AwardingCriterion>
    </cac:AwardingTerms>
  </cac:TenderingTerms>
</cac:ProcurementProjectLot>
{
  "withheldInformation": [
    {
      "field": "awa-cri-ord",
      "id": "awa-cri-ord-LOT-0001",
      "name": "Award Criteria Order Justification"
    }
  ]
}
BT-195(BT-733)-LotsGroup 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-ord']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::cac:ProcurementProjectLot/cbc:ID schemeName="LotsGroup"].

Set its .field to "awa-cri-ord".

Set its .name to "Award Criteria Order Justification".

<cac:ProcurementProjectLot>
  <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
  <cac:TenderingTerms>
    <cac:AwardingTerms>
      <cac:AwardingCriterion>
        <cac:SubordinateAwardingCriterion>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode listName="non-publication-identifier">awa-cri-ord</efbc:FieldIdentifierCode>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:SubordinateAwardingCriterion>
      </cac:AwardingCriterion>
    </cac:AwardingTerms>
  </cac:TenderingTerms>
</cac:ProcurementProjectLot>
{
  "withheldInformation": [
    {
      "field": "awa-cri-ord",
      "id": "awa-cri-ord-GLO-0001",
      "name": "Award Criteria Order Justification"
    }
  ]
}
BT-195(BT-734)-Lot 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-nam']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::cac:ProcurementProjectLot/cbc:ID schemeName="Lot"].

Set its .field to "awa-cri-nam".

Set its .name to "Award Criterion Name".

<cac:ProcurementProjectLot>
  <cbc:ID schemeName="Lot">LOT-0001</cbc:ID>
  <cac:TenderingTerms>
    <cac:AwardingTerms>
      <cac:AwardingCriterion>
        <cac:SubordinateAwardingCriterion>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode listName="non-publication-identifier">awa-cri-ord</efbc:FieldIdentifierCode>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:SubordinateAwardingCriterion>
      </cac:AwardingCriterion>
    </cac:AwardingTerms>
  </cac:TenderingTerms>
</cac:ProcurementProjectLot>
{
  "withheldInformation": [
    {
      "field": "awa-cri-nam",
      "id": "awa-cri-nam-LOT-0001",
      "name": "Award Criterion Name"
    }
  ]
}
BT-195(BT-734)-LotsGroup 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-nam']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::cac:ProcurementProjectLot/cbc:ID schemeName="LotsGroup"].

Set its .field to "awa-cri-nam".

Set its .name to "Award Criterion Name".

<cac:ProcurementProjectLot>
  <cbc:ID schemeName="LotsGroup">GLO-0001</cbc:ID>
  <cac:TenderingTerms>
    <cac:AwardingTerms>
      <cac:AwardingCriterion>
        <cac:SubordinateAwardingCriterion>
          <ext:UBLExtensions>
            <ext:UBLExtension>
              <ext:ExtensionContent>
                <efext:EformsExtension>
                  <efac:FieldsPrivacy>
                    <efbc:FieldIdentifierCode listName="non-publication-identifier">awa-cri-ord</efbc:FieldIdentifierCode>
                  </efac:FieldsPrivacy>
                </efext:EformsExtension>
              </ext:ExtensionContent>
            </ext:UBLExtension>
          </ext:UBLExtensions>
        </cac:SubordinateAwardingCriterion>
      </cac:AwardingCriterion>
    </cac:AwardingTerms>
  </cac:TenderingTerms>
</cac:ProcurementProjectLot>
{
  "withheldInformation": [
    {
      "field": "awa-cri-nam",
      "id": "awa-cri-nam-GLO-0001",
      "name": "Award Criterion Name"
    }
  ]
}
BT-195(BT-759)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:ReceivedSubmissionsStatistics/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='rec-sub-cou']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "rec-sub-cou".

Set its .name to "Received Submissions Count".

<efac:FieldsPrivacy>
  <efbc:FieldIdentifierCode listName="non-publication-identifier">rec-sub-cou</efbc:FieldIdentifierCode>
</efac:FieldsPrivacy>
{
  "withheldInformation": [
    {
      "field": "rec-sub-cou",
      "id": "rec-sub-cou-RES-0001",
      "name": "Received Submissions Count"
    }
  ]
}
BT-195(BT-760)-LotResult 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotResult/efac:ReceivedSubmissionsStatistics/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='rec-sub-typ']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotResult/cbc:ID].

Set its .field to "rec-sub-typ".

Set its .name to "Received Submissions Type".

<efac:FieldsPrivacy>
  <efbc:FieldIdentifierCode listName="non-publication-identifier">rec-sub-typ</efbc:FieldIdentifierCode>
</efac:FieldsPrivacy>
{
  "withheldInformation": [
    {
      "field": "rec-sub-typ",
      "id": "rec-sub-typ-RES-0001",
      "name": "Received Submissions Type"
    }
  ]
}
BT-195(BT-773)-Tender 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-con']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[ancestor::efac:LotTender/cbc:ID].

Set its .field to "sub-con".

Set its .name to "Subcontracting".

<efac:NoticeResult>
  <efac:LotTender>
    <cbc:ID schemeName="result">TEN-0001</cbc:ID>
    <efac:SubcontractingTerm>
      <efac:FieldsPrivacy>
        <efbc:FieldIdentifierCode listName="non-publication-identifier">sub-con</efbc:FieldIdentifierCode>
      </efac:FieldsPrivacy>
    </efac:SubcontractingTerm>
  </efac:LotTender>
</efac:NoticeResult>
{
  "withheldInformation": [
    {
      "field": "sub-con",
      "id": "sub-con-TEN-0001",
      "name": "Subcontracting"
    }
  ]
}
BT-195(BT-88)-Procedure 
Unpublished Identifier

BT-195: Identifier of the field that shall not be immediately published. Only fields concerning the Result value and groups of fields concerning the Tender and Procedure Lot Result can be unpublished. In the case of the European Parliament and Council Directive 2014/25/EU, the award criteria, the procurement procedure, certain dates and in certain cases information about the nature and quantity of a service can be unpublished as well.

/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-fea']/efbc:FieldIdentifierCode	
Add a withheldInformationItem to the withheldInformation array, and:

Set its .id to [efbc:FieldIdentifierCode]-[/*/cbc:ContractFolderID].

Set its .field to "pro-fea".

Set its .name to "Procedure Features".

<cbc:ContractFolderID>18d27a53-0109-4f93-9231-6659d931bce0</cbc:ContractFolderID>
<cac:TenderingProcess>
  <ext:UBLExtensions>
    <ext:UBLExtension>
      <ext:ExtensionContent>
        <efext:EformsExtension>
          <efac:FieldsPrivacy>
            <efbc:FieldIdentifierCode listName="non-publication-identifier">pro-fea</efbc:FieldIdentifierCode>
          </efac:FieldsPrivacy>
        </efext:EformsExtension>
      </ext:ExtensionContent>
    </ext:UBLExtension>
  </ext:UBLExtensions>
</cac:TenderingProcess>
{
  "withheldInformation": [
    {
      "field": "pro-fea",
      "id": "pro-fea-18d27a53-0109-4f93-9231-6659d931bce0",
      "name": "Procedure Features"
    }
  ]
}

"""








from lxml import etree

def parse_unpublished_identifier(xml_content):
    if isinstance(xml_content, str):
        xml_content = xml_content.encode('utf-8')
    root = etree.fromstring(xml_content)
    namespaces = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac': 'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1',
    'efext': 'http://data.europa.eu/p27/eforms-ubl-extensions/1',
    'efbc': 'http://data.europa.eu/p27/eforms-ubl-extension-basic-components/1'
}

    result = {"withheldInformation": []}
    contract_folder_id = root.xpath("//cbc:ContractFolderID/text()", namespaces=namespaces)[0]

    # Define a list of XPath expressions and their corresponding field names
    fields_to_parse = [
        ("/*/cac:TenderingTerms/cac:ProcurementLegislationDocumentReference[cbc:ID/text()='CrossBorderLaw']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cro-bor-law']/efbc:FieldIdentifierCode", "Cross Border Law"),
        ("/*/cac:TenderingProcess/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-typ']/efbc:FieldIdentifierCode", "Procedure Type"),
        ("/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc']/efbc:FieldIdentifierCode", "Procedure Accelerated"),
        ("/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='dir-awa-pre']/efbc:FieldIdentifierCode", "Direct Award Justification Previous Procedure Identifier"),
        ("/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='dir-awa-tex']/efbc:FieldIdentifierCode", "Direct Award Justification"),
        ("/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='accelerated-procedure']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='pro-acc-jus']/efbc:FieldIdentifierCode", "Procedure Accelerated Justification"),
        ("/*/cac:TenderingProcess/cac:ProcessJustification[cbc:ProcessReasonCode/@listName='direct-award-justification']/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='dir-awa-jus']/efbc:FieldIdentifierCode", "Direct Award Justification")
    ]

    for xpath, name in fields_to_parse:
        field_identifiers = root.xpath(xpath, namespaces=namespaces)
        for field_identifier in field_identifiers:
            result["withheldInformation"].append({
                "id": f"{field_identifier}-{contract_folder_id}",
                "field": field_identifier,
                "name": name
            })

    # Parse lot-specific fields
    lot_fields = [
        ("//efac:NoticeResult/efac:LotResult/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-cho']/efbc:FieldIdentifierCode", "Winner Chosen"),
        ("//efac:NoticeResult/efac:LotResult/efac:DecisionReason/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='no-awa-rea']/efbc:FieldIdentifierCode", "Not Awarded Reason"),
        ("//efac:NoticeResult/efac:LotTender/efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='con-rev-buy']/efbc:FieldIdentifierCode", "Concession Revenue Buyer"),
        ("//efac:NoticeResult/efac:LotTender/efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='con-rev-use']/efbc:FieldIdentifierCode", "Concession Revenue User"),
        ("//efac:NoticeResult/efac:LotTender/efac:ConcessionRevenue/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='val-con-des']/efbc:FieldIdentifierCode", "Concession Value Description"),
        ("//efac:NoticeResult/efac:LotTender/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='ten-ran']/efbc:FieldIdentifierCode", "Tender Rank"),
        ("//efac:NoticeResult/efac:LotTender/efac:Origin/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='cou-ori']/efbc:FieldIdentifierCode", "Country Origin"),
        ("//efac:NoticeResult/efac:LotTender/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='win-ten-var']/efbc:FieldIdentifierCode", "Winning Tender Variant")
    ]

    for xpath, name in lot_fields:
        field_identifiers = root.xpath(xpath, namespaces=namespaces)
        for field_identifier in field_identifiers:
            lot_id = field_identifier.xpath("ancestor::efac:LotTender/cbc:ID/text() | ancestor::efac:LotResult/cbc:ID/text()", namespaces=namespaces)[0]
            result["withheldInformation"].append({
                "id": f"{field_identifier}-{lot_id}",
                "field": field_identifier,
                "name": name
            })

    # Parse award criterion fields
    award_criterion_fields = [
        ("//cac:ProcurementProjectLot[@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-typ']/efbc:FieldIdentifierCode", "Award Criterion Type"),
        ("//cac:ProcurementProjectLot[@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-des']/efbc:FieldIdentifierCode", "Award Criterion Description")
    ]

    for xpath, name in award_criterion_fields:
        field_identifiers = root.xpath(xpath, namespaces=namespaces)
        for field_identifier in field_identifiers:
            lot_id = field_identifier.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID/text()", namespaces=namespaces)[0]
            result["withheldInformation"].append({
                "id": f"{field_identifier}-{lot_id}",
                "field": field_identifier,
                "name": name
            })

    # New parsing logic for award criteria related unpublished identifiers
    award_criteria_fields = [
        ("//cac:ProcurementProjectLot[@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-num']/efbc:FieldIdentifierCode", "Award Criterion Number Weight", "awa-cri-num-weight"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-wei']/efbc:FieldIdentifierCode", "Award Criterion Number Weight", "awa-cri-wei"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-weight']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-wei']/efbc:FieldIdentifierCode", "Award Criterion Number Weight", "awa-cri-wei"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-fix']/efbc:FieldIdentifierCode", "Award Criterion Number Fixed", "awa-cri-fix"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-fixed']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-fix']/efbc:FieldIdentifierCode", "Award Criterion Number Fixed", "awa-cri-fix"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-thr']/efbc:FieldIdentifierCode", "Award Criterion Number Threshold", "awa-cri-thr"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/cac:SubordinateAwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:AwardCriterionParameter[efbc:ParameterCode/@listName='number-threshold']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-thr']/efbc:FieldIdentifierCode", "Award Criterion Number Threshold", "awa-cri-thr"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='Lot']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-com']/efbc:FieldIdentifierCode", "Award Criteria Complicated", "awa-cri-com"),
        ("//cac:ProcurementProjectLot[cbc:ID/@schemeName='LotsGroup']/cac:TenderingTerms/cac:AwardingTerms/cac:AwardingCriterion/ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent/efext:EformsExtension/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='awa-cri-com']/efbc:FieldIdentifierCode", "Award Criteria Complicated", "awa-cri-com")
    ]

    for xpath, name, field in award_criteria_fields:
        field_identifiers = root.xpath(xpath, namespaces=namespaces)
        for field_identifier in field_identifiers:
            lot_id = field_identifier.xpath("ancestor::cac:ProcurementProjectLot/cbc:ID/text()", namespaces=namespaces)[0]
            result["withheldInformation"].append({
                "id": f"{field}-{lot_id}",
                "field": field,
                "name": name
            })


    # New parsing logic for subcontracting terms related unpublished identifiers
    subcontracting_fields = [
        ("//efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-val']/efbc:FieldIdentifierCode", "Subcontracting Value", "sub-val"),
        ("//efac:NoticeResult/efac:LotTender/efac:SubcontractingTerm[efbc:TermCode/@listName='applicability']/efac:FieldsPrivacy[efbc:FieldIdentifierCode/text()='sub-des']/efbc:FieldIdentifierCode", "Subcontracting Description", "sub-des")
    ]

    for xpath, name, field in subcontracting_fields:
        field_identifiers = root.xpath(xpath, namespaces=namespaces)
        for field_identifier in field_identifiers:
            tender_id = field_identifier.xpath("ancestor::efac:LotTender/cbc:ID/text()", namespaces=namespaces)[0]
            result["withheldInformation"].append({
                "id": f"{field}-{tender_id}",
                "field": field,
                "name": name
            })

    return result if result["withheldInformation"] else None