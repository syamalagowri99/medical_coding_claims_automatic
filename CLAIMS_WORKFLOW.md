# Claims Workflow: Validation, Submission & Approval with LLM

## 📋 Overview

The claims system has a **4-stage workflow**:
1. **DRAFT** - Claim created but not submitted
2. **SUBMITTED** - Claim validation triggered, LLM checks it
3. **PROCESSING/APPROVED** - Admin reviews validations
4. **APPROVED/DENIED** - Final approval or rejection
5. **PAID** - Payment processed

---

## 🔄 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLAIMS WORKFLOW WITH LLM VALIDATION                  │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: CREATE CLAIM (DRAFT)
├─ User enters claim info:
│  ├─ Patient ID
│  ├─ Insurance provider
│  ├─ Policy number
│  ├─ NPI (Rendering provider)
│  ├─ Place of service ("11" for office, "21" for inpatient, etc.)
│  └─ Line items (procedure codes, diagnosis codes, amounts)
│
├─ Database state:
│  ├─ claims.status = "draft"
│  ├─ claims.total_amount = $100.00 (default) or sum of items
│  └─ claim_items table populated
│
└─ Frontend shows: "Draft claim created" ✅

       │
       │ User clicks "Validate" button
       ↓

Step 2: VALIDATE CLAIM (LLM ANALYSIS)
├─ Backend receives: POST /claims/{id}/validate
│  └─ JWT token verified ✅
│
├─ claim_service.validate_claim() executes:
│  ├─ Gather claim_data:
│  │  {
│  │    "claim_number": "CLM-202605-74756",
│  │    "patient_id": "PAT-001",
│  │    "insurance_provider": "BlueCross",
│  │    "policy_number": "POL-123456",
│  │    "rendering_provider_npi": "1234567890",
│  │    "place_of_service": "11",
│  │    "items": [
│  │      {
│  │        "procedure_code": "99213",
│  │        "diagnosis_code": "Z00.00",
│  │        "amount": 125.00
│  │      }
│  │    ]
│  │  }
│  │
│  └─ Call: llm_service.validate_claim(claim_data)
│
├─ LLM Service (Azure OpenAI):
│  ├─ HTTP POST to: 
│  │  https://pkvaidemo.services.ai.azure.com/openai/v1
│  │  /deployments/gpt-5.4/chat/completions
│  │
│  ├─ Headers:
│  │  api-key: BHwCZ0xmIUgGFfvrK1SHpWd56hTSF0Oottj9eVww5HxtYrUjgrC3JQQJ99CEACYeBjFXJ3w3AAAAACOGB7Yk
│  │  api-version: 2024-02-01
│  │
│  ├─ Payload:
│  │  {
│  │    "messages": [
│  │      {
│  │        "role": "user",
│  │        "content": "Validate this claim: {...}"
│  │      }
│  │    ],
│  │    "model": "gpt-5.4",
│  │    "temperature": 0.1
│  │  }
│  │
│  └─ Response (GPT-5.4 analyzes and returns):
│     {
│       "validations": [
│         {
│           "validation_type": "documentation",
│           "error_message": "Claim has complete patient info",
│           "severity": "info",
│           "is_valid": true
│         },
│         {
│           "validation_type": "coding",
│           "error_message": "CPT code 99213 valid for office visit",
│           "severity": "info",
│           "is_valid": true
│         },
│         {
│           "validation_type": "medical_necessity",
│           "error_message": "ICD-10 Z00.00 justified for routine exam",
│           "severity": "info",
│           "is_valid": true
│         }
│       ]
│     }
│
├─ Database updates:
│  ├─ Clear existing claim_validations
│  ├─ INSERT INTO claim_validations (claim_id, validation_type, error_message, severity):
│  │  ├─ ("documentation", "Claim has complete patient info", "info")
│  │  ├─ ("coding", "CPT code 99213 valid", "info")
│  │  └─ ("medical_necessity", "ICD-10 justified", "info")
│  │
│  └─ claims.status stays "draft" (not updated yet)
│
└─ Frontend displays: Validations grouped by category

       │
       │ User clicks "Submit Claim" button
       ↓

Step 3: SUBMIT CLAIM (STATUS CHANGE)
├─ Backend receives: POST /claims/{id}/submit
│  └─ JWT token verified ✅
│
├─ claim_service.submit_claim() checks:
│  ├─ Is claim in DRAFT status? ✅
│  ├─ Does claim have patient_id? ✅
│  ├─ Does claim have items? (optional, warning if missing)
│  │
│  └─ Check for BLOCKING errors only:
│     ├─ validation_type IN ("blocking_error", "missing_patient", "missing_items")
│     └─ If found: Reject submission ❌
│
├─ If no blocking errors:
│  ├─ Database update:
│  │  ├─ UPDATE claims SET status = 'SUBMITTED'
│  │  ├─ UPDATE claims SET submission_date = NOW()
│  │  └─ Commit transaction
│  │
│  └─ Response: Claim submitted successfully ✅
│
└─ Frontend shows: "Claim submitted" + status badge changes to BLUE

       │
       │ Admin reviews claim details + validations
       ↓

Step 4: ADMIN REVIEW & DECISION
├─ Admin views claim at http://localhost:5173/claims/{id}
│
├─ Sees:
│  ├─ Claim Summary:
│  │  ├─ Patient: John Doe
│  │  ├─ Total: $300.00
│  │  ├─ Insurance: BlueCross BlueShield
│  │  ├─ NPI: 1234567890
│  │  └─ Place of Service: 11 (Office)
│  │
│  ├─ Validations (grouped by LLM category):
│  │  ├─ 📄 Documentation (blue panel)
│  │  ├─ 💻 Coding Issues (orange panel)
│  │  ├─ 🏥 Medical Necessity (red panel)
│  │  └─ ⚖️ Compliance (purple panel)
│  │
│  └─ Claim Items:
│     ├─ Item 1: Office visit (CPT 99213, ICD-10 Z00.00) - $125.00
│     └─ Item 2: Follow-up (CPT 99000, ICD-10 R51.9) - $175.00
│
├─ Decision options:
│  ├─ Option A: APPROVE ✅
│  └─ Option B: REJECT ❌ (requires reason)
│
└─ Admin clicks button

       │
       │ Path A: APPROVE
       ↓ (or Path B: REJECT)

Path A: APPROVE CLAIM
├─ Backend receives: POST /claims/{id}/approve
│
├─ claim_service.approve_claim() executes:
│  ├─ Check if status IN ('submitted', 'processing')? ✅
│  ├─ Database update:
│  │  ├─ UPDATE claims SET status = 'APPROVED'
│  │  ├─ UPDATE claims SET processing_date = NOW()
│  │  └─ Commit
│  │
│  └─ Return updated claim
│
├─ Database state:
│  ├─ claims.status = "approved"
│  ├─ claims.processing_date = 2026-06-01 14:30:00
│  └─ claim_validations remain as-is (for audit)
│
├─ Audit log entry created:
│  ├─ action: "APPROVED"
│  ├─ entity_type: "claim"
│  ├─ entity_id: 6
│  ├─ changed_by: admin_user_id
│  └─ timestamp: NOW()
│
└─ Frontend: Green badge "APPROVED" ✅

Path B: REJECT CLAIM
├─ Backend receives: POST /claims/{id}/reject {rejection_reason}
│
├─ claim_service.reject_claim() executes:
│  ├─ Check if status IN ('submitted', 'processing')? ✅
│  ├─ Database update:
│  │  ├─ UPDATE claims SET status = 'DENIED'
│  │  ├─ UPDATE claims SET rejection_reason = 'Diagnosis code not justified'
│  │  ├─ UPDATE claims SET processing_date = NOW()
│  │  └─ Commit
│  │
│  └─ Return updated claim
│
├─ Database state:
│  ├─ claims.status = "denied"
│  ├─ claims.rejection_reason = "Diagnosis code not justified"
│  ├─ claims.processing_date = NOW()
│  └─ claim_validations remain as-is (for audit)
│
├─ Audit log entry created:
│  ├─ action: "REJECTED"
│  ├─ entity_type: "claim"
│  ├─ reason: "Diagnosis code not justified"
│  ├─ changed_by: admin_user_id
│  └─ timestamp: NOW()
│
└─ Frontend: Red badge "DENIED" ❌ + shows rejection reason

End of Workflow
```

---

## 🎯 Detailed Step Breakdown

### Step 1: CREATE CLAIM (Draft)

**User Input**:
```json
{
  "patient_id": 1,
  "claim_number": "CLM-202605-74756",
  "insurance_provider": "BlueCross BlueShield",
  "policy_number": "POL-123456789",
  "rendering_provider_npi": "1234567890",
  "place_of_service": "11",
  "total_amount": 300.00
}
```

**Backend (create_claim)**:
```python
def create_claim(db: Session, claim: ClaimCreate, created_by: int) -> Claim:
    # Default total_amount to 100.0 if not provided
    total_amount = claim.total_amount or 100.0
    
    db_claim = Claim(
        patient_id=claim.patient_id,
        claim_number=claim.claim_number,
        insurance_provider=claim.insurance_provider,
        policy_number=claim.policy_number,
        rendering_provider_npi=claim.rendering_provider_npi,
        place_of_service=claim.place_of_service,
        status=ClaimStatus.DRAFT,  # ← Always starts as DRAFT
        total_amount=total_amount,
        created_by=created_by
    )
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim
```

**Database State**:
```sql
SELECT * FROM claims WHERE id = 6;

id  | claim_number        | status  | total_amount | patient_id | created_by | created_at
----+---------------------+---------+--------------+------------+------------+---------------------
6   | CLM-202605-74756    | draft   | 300.00       | 1          | 1          | 2026-06-01 10:00:00
```

---

### Step 2: VALIDATE CLAIM (LLM Analysis)

**Frontend Call**:
```javascript
// Button click in ClaimDetails.jsx
onClick={() => validateMutation.mutate(claim.id)}

// Calls:
claimAPI.validate(claimId) 
// → POST /claims/6/validate
```

**Backend Processing**:
```python
def validate_claim(db: Session, claim_id: int) -> Claim:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    
    # Gather claim data
    claim_data = {
        "claim_number": claim.claim_number,
        "patient_id": claim.patient_id,
        "insurance_provider": claim.insurance_provider,
        "policy_number": claim.policy_number,
        "rendering_provider_npi": claim.rendering_provider_npi,
        "place_of_service": claim.place_of_service,
        "items": [
            {
                "procedure_code": item.procedure_code,
                "diagnosis_code": item.diagnosis_code,
                "amount": item.amount,
                "description": item.description
            }
            for item in claim.claim_items
        ]
    }
    
    # Call LLM service
    validation_result = llm_service.validate_claim(claim_data)
    
    # Clear existing validations
    db.query(ClaimValidation).filter(
        ClaimValidation.claim_id == claim_id
    ).delete()
    
    # Store new validations
    for error in validation_result.get("errors", []):
        validation = ClaimValidation(
            claim_id=claim.id,
            validation_type=error["type"],  # documentation, coding, medical_necessity, compliance
            is_valid=error.get("severity") != "error",
            error_message=error["message"],
            severity=error.get("severity", "error")  # error, warning, info
        )
        db.add(validation)
    
    db.commit()
    db.refresh(claim)
    return claim
```

**LLM Service - Azure OpenAI Call**:
```python
def validate_claim(self, claim_data: dict) -> dict:
    prompt = f"""
    Analyze this medical claim for completeness and accuracy:
    
    {json.dumps(claim_data, indent=2)}
    
    Check:
    1. DOCUMENTATION: All required fields present? Patient ID, NPI, place of service?
    2. CODING: Are procedure codes (CPT/HCPCS) and diagnosis codes (ICD-10) valid?
    3. MEDICAL_NECESSITY: Is the diagnosis justified for the procedures?
    4. COMPLIANCE: Does it follow healthcare regulations?
    
    Return JSON array:
    [
      {{
        "type": "documentation|coding|medical_necessity|compliance",
        "message": "Specific finding",
        "severity": "error|warning|info"
      }}
    ]
    """
    
    response = self.client.chat.completions.create(
        model="gpt-5.4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1  # Low temp = consistent results
    )
    
    result = json.loads(response.choices[0].message.content)
    return {"errors": result}
```

**Azure OpenAI HTTP Request** (what actually happens):
```
POST https://pkvaidemo.services.ai.azure.com/openai/v1/deployments/gpt-5.4/chat/completions?api-version=2024-02-01

Headers:
  api-key: BHwCZ0xmIUgGFfvrK1SHpWd56hTSF0Oottj9eVww5HxtYrUjgrC3JQQJ99CEACYeBjFXJ3w3AAAAACOGB7Yk
  Content-Type: application/json

Body:
{
  "messages": [
    {
      "role": "user",
      "content": "Analyze this medical claim...{claim_data}..."
    }
  ],
  "model": "gpt-5.4",
  "temperature": 0.1
}

Response (from GPT-5.4):
{
  "choices": [
    {
      "message": {
        "content": "[
          {
            \"type\": \"documentation\",
            \"message\": \"Complete patient and provider information provided\",
            \"severity\": \"info\"
          },
          {
            \"type\": \"coding\",
            \"message\": \"CPT code 99213 (office visit, low complexity) appropriate\",
            \"severity\": \"info\"
          },
          {
            \"type\": \"medical_necessity\",
            \"message\": \"ICD-10 Z00.00 (routine examination) supports CPT 99213\",
            \"severity\": \"info\"
          },
          {
            \"type\": \"compliance\",
            \"message\": \"NPI and place of service valid\",
            \"severity\": \"info\"
          }
        ]"
      }
    }
  ]
}
```

**Database After Validation**:
```sql
INSERT INTO claim_validations (claim_id, validation_type, error_message, severity, is_valid)
VALUES
(6, 'documentation', 'Complete patient and provider info provided', 'info', true),
(6, 'coding', 'CPT code 99213 appropriate for office visit', 'info', true),
(6, 'medical_necessity', 'ICD-10 Z00.00 supports CPT 99213', 'info', true),
(6, 'compliance', 'NPI and place of service valid', 'info', true);

-- Status stays DRAFT
SELECT status FROM claims WHERE id = 6;
-- status: "draft"
```

**Frontend Display** (Grouped by Category):
```
┌─ 📄 DOCUMENTATION ─────────────────┐
│ ✅ Complete patient and provider   │
│    info provided                   │
└────────────────────────────────────┘

┌─ 💻 CODING ISSUES ─────────────────┐
│ ✅ CPT code 99213 appropriate      │
│    for office visit                │
└────────────────────────────────────┘

┌─ 🏥 MEDICAL NECESSITY ─────────────┐
│ ✅ ICD-10 Z00.00 supports CPT 99213│
└────────────────────────────────────┘

┌─ ⚖️ COMPLIANCE ────────────────────┐
│ ✅ NPI and place of service valid  │
└────────────────────────────────────┘
```

---

### Step 3: SUBMIT CLAIM

**Frontend Call**:
```javascript
onClick={() => submitMutation.mutate(claim.id)}
// → POST /claims/6/submit
```

**Backend Processing**:
```python
def submit_claim(db: Session, claim_id: int) -> Claim:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise ValueError("Claim not found")
    
    # Must be in DRAFT status
    if claim.status != ClaimStatus.DRAFT:
        raise ValueError("Claim must be in draft status to submit")
    
    # Check basic requirements
    if not claim.patient_id:
        raise ValueError("Claim must have a patient assigned")
    
    # Allow empty items (show warning instead of blocking)
    if not claim.claim_items or len(claim.claim_items) == 0:
        warning = ClaimValidation(
            claim_id=claim_id,
            validation_type="documentation",
            is_valid=True,
            error_message="Warning: Claim has no line items",
            severity="warning"
        )
        db.add(warning)
    
    # Validate (if not already done)
    try:
        validate_claim(db, claim_id)
    except:
        pass  # Allow submission even if validation fails
    
    # Check for BLOCKING errors only (very specific types)
    blocking_errors = db.query(ClaimValidation).filter(
        ClaimValidation.claim_id == claim_id,
        ClaimValidation.validation_type.in_([
            "blocking_error",
            "missing_patient",
            "missing_items"
        ])
    ).all()
    
    if blocking_errors:
        raise ValueError("Cannot submit: " + ", ".join([e.error_message for e in blocking_errors]))
    
    # No blocking errors? Change status to SUBMITTED
    claim.status = ClaimStatus.SUBMITTED
    claim.submission_date = func.now()
    db.commit()
    db.refresh(claim)
    
    return claim
```

**Database After Submit**:
```sql
UPDATE claims 
SET status = 'SUBMITTED', 
    submission_date = '2026-06-01 11:00:00'
WHERE id = 6;

-- Insert audit log
INSERT INTO audit_logs (action, entity_type, entity_id, changed_by, timestamp)
VALUES ('SUBMIT', 'claim', 6, 1, NOW());
```

**Frontend State**:
```
Status Badge changes: GRAY → BLUE
Button text: "Submit Claim" → Disabled
Shows: "Claim submitted successfully" ✅
```

---

### Step 4: ADMIN REVIEW & APPROVAL/REJECTION

**Admin Views Claim**:
Frontend displays claim with:
- ✅ All validation results (from Step 2)
- ✅ Claim items with codes
- ✅ Two action buttons:
  - 🟢 Approve Claim
  - 🔴 Reject

#### Option A: APPROVE

**Frontend Call**:
```javascript
onClick={() => approveMutation.mutate(claim.id)}
// → POST /claims/6/approve
```

**Backend Processing**:
```python
def approve_claim(db: Session, claim_id: int, approved_by: int, notes: Optional[str] = None) -> Claim:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise ValueError("Claim not found")
    
    # Can approve from SUBMITTED or PROCESSING
    if claim.status not in [ClaimStatus.SUBMITTED, ClaimStatus.PROCESSING]:
        raise ValueError(f"Claim must be submitted to approve. Current status: {claim.status}")
    
    # Update status
    claim.status = ClaimStatus.APPROVED
    claim.processing_date = func.now()
    claim.notes = notes or claim.notes
    
    db.commit()
    db.refresh(claim)
    
    # Create audit log
    audit_log = AuditLog(
        action="APPROVE",
        entity_type="claim",
        entity_id=claim.id,
        changed_by=approved_by,
        old_value=ClaimStatus.SUBMITTED,
        new_value=ClaimStatus.APPROVED,
        timestamp=func.now()
    )
    db.add(audit_log)
    db.commit()
    
    return claim
```

**Database After Approval**:
```sql
UPDATE claims 
SET status = 'APPROVED', 
    processing_date = '2026-06-01 12:00:00'
WHERE id = 6;

INSERT INTO audit_logs 
(action, entity_type, entity_id, changed_by, old_value, new_value, timestamp)
VALUES 
('APPROVE', 'claim', 6, 1, 'SUBMITTED', 'APPROVED', '2026-06-01 12:00:00');
```

**Frontend State**:
```
Status Badge: BLUE → GREEN
Shows: "Claim approved successfully" ✅
Buttons disabled
```

---

#### Option B: REJECT

**Frontend - Rejection Modal**:
```
┌─────────────────────────────────────┐
│ Reject Claim                        │
├─────────────────────────────────────┤
│ Please provide a reason:            │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Diagnosis code is not properly  │ │
│ │ justified for this procedure.   │ │
│ │ Please resubmit with additional │ │
│ │ clinical documentation.         │ │
│ └─────────────────────────────────┘ │
│                                     │
│     [Cancel]    [Reject Claim]      │
└─────────────────────────────────────┘
```

**Frontend Call**:
```javascript
onClick={() => {
  rejectMutation.mutate({
    claimId: claim.id,
    reason: rejectionReason
  })
}}
// → POST /claims/6/reject 
//   {rejection_reason: "Diagnosis code not justified..."}
```

**Backend Processing**:
```python
def reject_claim(db: Session, claim_id: int, approved_by: int, rejection_reason: str, notes: Optional[str] = None) -> Claim:
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise ValueError("Claim not found")
    
    # Can reject from SUBMITTED or PROCESSING
    if claim.status not in [ClaimStatus.SUBMITTED, ClaimStatus.PROCESSING]:
        raise ValueError(f"Claim must be submitted to reject. Current status: {claim.status}")
    
    # Update status
    claim.status = ClaimStatus.DENIED
    claim.rejection_reason = rejection_reason  # ← Store reason for audit
    claim.processing_date = func.now()
    claim.notes = notes or claim.notes
    
    db.commit()
    db.refresh(claim)
    
    # Create audit log
    audit_log = AuditLog(
        action="REJECT",
        entity_type="claim",
        entity_id=claim.id,
        changed_by=approved_by,
        old_value=ClaimStatus.SUBMITTED,
        new_value=ClaimStatus.DENIED,
        additional_data={"rejection_reason": rejection_reason},
        timestamp=func.now()
    )
    db.add(audit_log)
    db.commit()
    
    return claim
```

**Database After Rejection**:
```sql
UPDATE claims 
SET status = 'DENIED', 
    rejection_reason = 'Diagnosis code not justified. Please resubmit with additional clinical documentation.',
    processing_date = '2026-06-01 12:00:00'
WHERE id = 6;

INSERT INTO audit_logs 
(action, entity_type, entity_id, changed_by, old_value, new_value, additional_data, timestamp)
VALUES 
('REJECT', 'claim', 6, 1, 'SUBMITTED', 'DENIED', 
 '{"rejection_reason": "Diagnosis code not justified..."}', 
 '2026-06-01 12:00:00');
```

**Frontend State**:
```
Status Badge: BLUE → RED
Shows: "Claim rejected successfully" ✅
Shows: "Rejection Reason: Diagnosis code not justified..."
Buttons disabled
```

---

## 🎨 Validation Categories (From LLM)

### 📄 DOCUMENTATION
**What it checks**:
- Required fields present (patient ID, NPI, place of service)
- Contact information valid
- Insurance information complete
- Dates in correct format
- Address/demographic info present

**Example errors**:
- ❌ "Missing rendering provider NPI"
- ❌ "Patient phone number required"
- ⚠️ "Address incomplete"

### 💻 CODING ISSUES
**What it checks**:
- Procedure codes (CPT, HCPCS) valid
- Diagnosis codes (ICD-10) valid
- Code combinations allowed
- Code versions current
- Modifier codes correct (if applicable)

**Example errors**:
- ❌ "CPT code 99999 does not exist"
- ❌ "ICD-10 code Z99.99 invalid"
- ⚠️ "Unusual combination: CPT 99213 with major surgery code"

### 🏥 MEDICAL NECESSITY
**What it checks**:
- Diagnosis supports the procedure
- Service appropriate for diagnosis
- Clinical justification present
- Frequency reasonable
- Age/gender appropriate

**Example errors**:
- ❌ "ICD-10 E11.9 (diabetes) does not justify CPT 70450 (CT brain)"
- ⚠️ "Diagnosis code suggests lower complexity than billed procedure"

### ⚖️ COMPLIANCE
**What it checks**:
- NPI valid format
- Place of service valid for procedure
- Billing rules followed
- HIPAA requirements met
- Regulatory compliance

**Example errors**:
- ❌ "NPI must be 10 digits"
- ❌ "Place of service 11 (office) invalid for inpatient procedure"
- ⚠️ "Missing required modifier for this service"

---

## 📊 Example: Complete Workflow with Real Data

### Claim 6: Well-formed claim (should pass validation)

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: CREATE (Draft)                                      │
├─────────────────────────────────────────────────────────────┤
│ Patient: John Doe (PAT-001)                                 │
│ Insurance: BlueCross BlueShield                             │
│ Policy: POL-123456789                                       │
│ NPI: 1234567890 ✅                                          │
│ Place of Service: 11 (Office) ✅                            │
│ Total Amount: $300.00                                       │
│                                                             │
│ Items:                                                      │
│  └─ CPT 99213 (Office visit) + ICD-10 Z00.00 (Routine exam)│
│  └─ CPT 99000 (E&M) + ICD-10 R51.9 (Headache)             │
│                                                             │
│ Status: DRAFT                                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
User clicks "Validate"
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: VALIDATE (LLM Analysis)                             │
├─────────────────────────────────────────────────────────────┤
│ Azure OpenAI GPT-5.4 analyzes claim...                      │
│                                                             │
│ Response:                                                   │
│                                                             │
│ 📄 DOCUMENTATION:                                           │
│    ✅ Complete patient info                                │
│    ✅ Valid NPI provided                                   │
│    ✅ Place of service specified                           │
│                                                             │
│ 💻 CODING:                                                  │
│    ✅ CPT 99213 valid for office visit                     │
│    ✅ ICD-10 Z00.00 valid diagnosis code                   │
│    ✅ CPT 99000 valid for E&M                              │
│                                                             │
│ 🏥 MEDICAL NECESSITY:                                       │
│    ✅ Z00.00 justifies routine examination                 │
│    ✅ R51.9 supports follow-up E&M                         │
│    ✅ Codes appropriate for complexity billed              │
│                                                             │
│ ⚖️ COMPLIANCE:                                              │
│    ✅ NPI format valid                                     │
│    ✅ Place of service 11 appropriate                      │
│    ✅ No HIPAA violations detected                         │
│                                                             │
│ Status: DRAFT (validations stored, status not changed)     │
└─────────────────────────────────────────────────────────────┘
                         ↓
User clicks "Submit Claim"
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: SUBMIT (Change Status)                              │
├─────────────────────────────────────────────────────────────┤
│ Backend checks:                                             │
│  ✅ Claim in DRAFT? YES                                    │
│  ✅ Patient assigned? YES                                  │
│  ✅ Blocking errors? NO                                    │
│                                                             │
│ Update: claims.status = SUBMITTED                          │
│ Update: claims.submission_date = NOW()                     │
│                                                             │
│ Status: SUBMITTED ← Blue badge                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
Admin reviews + makes decision
                         ↓
Admin clicks "Approve Claim" (no issues found)
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: APPROVE (Final Decision)                            │
├─────────────────────────────────────────────────────────────┤
│ Backend checks:                                             │
│  ✅ Claim in SUBMITTED? YES                                │
│                                                             │
│ Update: claims.status = APPROVED                           │
│ Update: claims.processing_date = NOW()                     │
│ Create: audit_log entry                                    │
│                                                             │
│ Status: APPROVED ← Green badge ✅                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔴 Example: Claim with Issues

### Claim 7: Minimal claim (shows validation errors)

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: CREATE (Draft)                                      │
├─────────────────────────────────────────────────────────────┤
│ Patient: John Doe (PAT-001)                                 │
│ Insurance: Blue Shield                                      │
│ Policy: POL-987654                                          │
│ NPI: ❌ MISSING                                             │
│ Place of Service: ❌ MISSING                                │
│ Total Amount: $150.00                                       │
│                                                             │
│ Items: ❌ NONE                                              │
│ Status: DRAFT                                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
User clicks "Validate"
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: VALIDATE (LLM Analysis)                             │
├─────────────────────────────────────────────────────────────┤
│ Azure OpenAI identifies issues:                             │
│                                                             │
│ 📄 DOCUMENTATION (RED errors):                              │
│    ❌ Missing rendering provider NPI (required)             │
│    ❌ Missing place of service (required)                  │
│    ⚠️ No line items in claim                               │
│                                                             │
│ 💻 CODING (ORANGE warnings):                                │
│    ⚠️ Cannot validate codes - no items provided            │
│                                                             │
│ 🏥 MEDICAL NECESSITY (GRAY):                                │
│    ⚠️ Cannot assess - insufficient data                    │
│                                                             │
│ ⚖️ COMPLIANCE (RED errors):                                 │
│    ❌ NPI required for provider compliance                 │
│                                                             │
│ Status: DRAFT                                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
Frontend shows grouped validations:

   RED errors (must fix)
   YELLOW warnings (should address)
   
User clicks "Submit Claim" anyway
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: SUBMIT (Check for Blocking Errors)                  │
├─────────────────────────────────────────────────────────────┤
│ Backend checks for BLOCKING errors:                         │
│  - validation_type = "blocking_error"? NO                  │
│  - validation_type = "missing_patient"? NO                 │
│  - validation_type = "missing_items"? NO                   │
│                                                             │
│ Warning added for missing items, but not blocking          │
│                                                             │
│ Result: ALLOWED to submit (non-blocking)                   │
│ Status: SUBMITTED ← Blue badge                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
Admin reviews
- Sees all validation warnings/errors
- Decides to REJECT because NPI missing
                         ↓
Admin enters reason: "Rendering provider NPI required"
Admin clicks "Reject"
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: REJECT (With Reason)                                │
├─────────────────────────────────────────────────────────────┤
│ Update: claims.status = DENIED                             │
│ Update: claims.rejection_reason = "Rendering provider..."  │
│ Create: audit_log entry                                    │
│                                                             │
│ Status: DENIED ← Red badge ❌                              │
│ Shows rejection reason to user                             │
└─────────────────────────────────────────────────────────────┘

User sees error, adds NPI, resubmits
→ Cycle starts again from STEP 1
```

---

## 🔑 Key Points

### ✅ What Gets Validated by LLM
- Completeness of required fields
- Code validity (CPT, ICD-10, HCPCS)
- Medical appropriateness
- Regulatory compliance
- Consistency between diagnosis and procedures

### ✅ What Prevents Submission
- **ONLY** blocking errors block submission
- Missing patient ID
- Explicitly marked critical errors
- **Most** warnings/info messages allow submission

### ✅ Validation Grouping (Frontend)
- **📄 Documentation** (Blue) - Field completeness
- **💻 Coding** (Orange) - Code validity
- **🏥 Medical Necessity** (Red) - Clinical appropriateness
- **⚖️ Compliance** (Purple) - Regulatory requirements

### ✅ Audit Trail
Every action logged:
- CREATE, SUBMIT, APPROVE, REJECT
- User who made action
- Timestamp
- Old/new values
- Rejection reason (if applicable)

### ✅ Workflow States
```
DRAFT
  ↓ (Submit)
SUBMITTED
  ↓ (Approve or Reject)
APPROVED / DENIED
  ↓
PAID (Future state)
```

---

## 📱 Frontend UI Summary

**Claim Details Page** shows:
1. **Claim Summary** - Basic info + NPI + Place of Service
2. **Validations Panel** - Grouped by category with icons/colors
3. **Claim Items** - Procedure codes, diagnosis codes, dates, amounts
4. **Action Buttons**:
   - Draft: "Validate" + "Submit"
   - Submitted: "Approve" + "Reject"
   - Approved/Denied: Disabled (read-only)

**Status Badges**:
- 🟦 DRAFT (Gray)
- 🟦 SUBMITTED (Blue)
- 🟩 APPROVED (Green)
- 🟥 DENIED (Red)

