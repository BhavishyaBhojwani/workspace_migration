# Lead Module Comprehensive Test Cases

## Analysis Summary

**Framework**: Django REST Framework (not Laravel as mentioned)
**Database**: PostgreSQL with soft delete functionality
**Authentication**: JWT with CRM user permissions
**Pipeline Stages**: New → Follow Up → Qualified → Converted/Lost

**Validation Fix Applied**: 
- Fixed data integrity issue where leads could be created with non-existent foreign key references
- Now validates person_id, organisation_id, lead_status_id, lead_source_id, user_owner_id, and user_assigned_id
- Behavior now matches Laravel: returns 400 validation error instead of creating with null relationships

**Search Endpoint Updated**:
- Removed separate `/api/v1/leads/search/` endpoint
- Search now handled via query parameter: `/api/v1/leads/?search=test`
- Matches Laravel behavior and REST best practices
- Frontend compatibility maintained

## API Endpoints Identified

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/leads/` | GET | List leads with pagination, filtering, sorting |
| `/api/v1/leads/` | POST | Create new lead |
| `/api/v1/leads/{id}/` | GET | Get lead details |
| `/api/v1/leads/{id}/` | PUT | Update lead |
| `/api/v1/leads/{id}/` | DELETE | Delete lead (soft delete) |
| `/api/v1/leads/{id}/convert/` | POST | Convert lead to deal |
| `/api/v1/leads/{id}/labels/` | POST | Assign labels to lead |
| `/api/v1/leads/{id}/notes/` | POST | Add note to lead |
| `/api/v1/leads/bulk_status/` | POST | Bulk update lead status |
| `/api/v1/leads/bulk_assign/` | POST | Bulk assign leads to user |
| `/api/v1/leads/bulk_delete/` | POST | Bulk delete leads |
| `/api/v1/lead-statuses/` | GET | List lead statuses |
| `/api/v1/lead-sources/` | GET | List lead sources |

---

## Functional Test Cases

### Test Case ID: LEAD_001
**Module**: Lead Creation
**Test Scenario**: Create lead with valid data and person
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Test Lead",
    "description": "Test lead description",
    "person_id": 1,
    "amount": 5000.00,
    "currency": "USD",
    "lead_status_id": 1,
    "lead_source_id": 1,
    "qualified": false,
    "user_owner_id": 1,
    "user_assigned_id": 1
}
```
**Expected Result**: Lead created successfully with all fields populated
**HTTP Status Code**: 201

### Test Case ID: LEAD_002
**Module**: Lead Creation
**Test Scenario**: Create lead with valid data and organisation
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Test Lead with Organisation",
    "description": "Test lead description",
    "organisation_id": 1,
    "amount": 7500.00,
    "currency": "EUR",
    "lead_status_id": 1,
    "lead_source_id": 2,
    "qualified": true,
    "expected_close": "2024-12-31T23:59:59Z",
    "user_owner_id": 1,
    "user_assigned_id": 2
}
```
**Expected Result**: Lead created successfully with organisation relationship
**HTTP Status Code**: 201

### Test Case ID: LEAD_003
**Module**: Lead Creation
**Test Scenario**: Create lead without person or organisation (should fail)
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Invalid Lead",
    "description": "Missing person and organisation",
    "amount": 1000.00,
    "currency": "USD"
}
```
**Expected Result**: Validation error - person_id or organisation_id required
**HTTP Status Code**: 400

### Test Case ID: LEAD_004
**Module**: Lead Creation
**Test Scenario**: Create lead with negative amount (should fail)
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Invalid Amount Lead",
    "person_id": 1,
    "amount": -1000.00,
    "currency": "USD"
}
```
**Expected Result**: Validation error - amount must be positive
**HTTP Status Code**: 400

### Test Case ID: LEAD_005
**Module**: Lead Creation
**Test Scenario**: Create lead with invalid currency (should fail)
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Invalid Currency Lead",
    "person_id": 1,
    "amount": 1000.00,
    "currency": "XYZ"
}
```
**Expected Result**: Validation error - invalid currency code
**HTTP Status Code**: 400

### Test Case ID: LEAD_006
**Module**: Lead Creation
**Test Scenario**: Create lead with empty title (should fail)
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "",
    "person_id": 1,
    "amount": 1000.00,
    "currency": "USD"
}
```
**Expected Result**: Validation error - title is required
**HTTP Status Code**: 400

---

## API Test Cases

### Test Case ID: LEAD_API_001
**Module**: Lead Retrieval
**Test Scenario**: Get lead details with valid ID
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Lead details with all relationships (person, organisation, status, source, users)
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_002
**Module**: Lead Retrieval
**Test Scenario**: Get non-existent lead (should fail)
**API Endpoint**: `/api/v1/leads/99999/`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: 404 error - lead not found
**HTTP Status Code**: 404

### Test Case ID: LEAD_API_003
**Module**: Lead List
**Test Scenario**: List leads with default pagination
**API Endpoint**: `/api/v1/leads/`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Paginated list of leads with meta information
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_004
**Module**: Lead List
**Test Scenario**: List leads with filtering by status
**API Endpoint**: `/api/v1/leads/?lead_status_id=1`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Filtered list of leads with specified status
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_005
**Module**: Lead List
**Test Scenario**: List leads with search functionality
**API Endpoint**: `/api/v1/leads/?search=test`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Leads matching search criteria in title/description
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_006
**Module**: Lead Update
**Test Scenario**: Update lead with valid data
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "title": "Updated Lead Title",
    "description": "Updated description",
    "amount": 8000.00,
    "qualified": true,
    "lead_status_id": 2
}
```
**Expected Result**: Lead updated successfully with new values
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_007
**Module**: Lead Update
**Test Scenario**: Update lead with invalid data (negative amount)
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "amount": -5000.00
}
```
**Expected Result**: Validation error - amount must be positive
**HTTP Status Code**: 400

### Test Case ID: LEAD_API_008
**Module**: Pagination
**Test Scenario**: List leads with pagination parameters
**API Endpoint**: `/api/v1/leads/?page=2&per_page=20`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Correct page results with pagination metadata
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_009
**Module**: Pagination
**Test Scenario**: List leads with invalid page (should return first page)
**API Endpoint**: `/api/v1/leads/?page=999&per_page=20`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Returns first page or empty results with proper pagination
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_010
**Module**: Sorting
**Test Scenario**: List leads sorted by amount (ascending)
**API Endpoint**: `/api/v1/leads/?sort=amount&direction=asc`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Leads sorted by amount in ascending order
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_011
**Module**: Sorting
**Test Scenario**: List leads sorted by created_at (descending)
**API Endpoint**: `/api/v1/leads/?sort=created_at&direction=desc`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Leads sorted by created_at in descending order (newest first)
**HTTP Status Code**: 200

### Test Case ID: LEAD_API_012
**Module**: Sorting
**Test Scenario**: List leads with invalid sort field (should use default)
**API Endpoint**: `/api/v1/leads/?sort=invalid_field`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Uses default sorting (created_at desc) or validation error
**HTTP Status Code**: 200 or 400

---

## Validation Test Cases

### Test Case ID: LEAD_VAL_001
**Module**: Lead Validation
**Test Scenario**: Validate required fields - missing title
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "person_id": 1,
    "amount": 1000.00
}
```
**Expected Result**: Validation error - title is required
**HTTP Status Code**: 400

### Test Case ID: LEAD_VAL_002
**Module**: Lead Validation
**Test Scenario**: Validate currency codes - valid currencies
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Test Lead",
    "person_id": 1,
    "amount": 1000.00,
    "currency": "USD"
}
```
**Expected Result**: Lead created successfully
**HTTP Status Code**: 201

### Test Case ID: LEAD_VAL_003
**Module**: Lead Validation
**Test Scenario**: Validate currency codes - invalid currency
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Test Lead",
    "person_id": 1,
    "amount": 1000.00,
    "currency": "INVALID"
}
```
**Expected Result**: Validation error - invalid currency code
**HTTP Status Code**: 400

### Test Case ID: LEAD_VAL_004
**Module**: Lead Validation
**Test Scenario**: Validate cross-field - person or organisation required
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Test Lead",
    "amount": 1000.00
}
```
**Expected Result**: Validation error - person_id or organisation_id required
**HTTP Status Code**: 400

### Test Case ID: LEAD_VAL_005
**Module**: Lead Validation
**Test Scenario**: Validate amount field - zero amount (should pass)
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Test Lead",
    "person_id": 1,
    "amount": 0.00,
    "currency": "USD"
}
```
**Expected Result**: Lead created successfully
**HTTP Status Code**: 201

---

## Permission and Authentication Test Cases

### Test Case ID: LEAD_AUTH_001
**Module**: Authentication
**Test Scenario**: Access lead endpoints without authentication
**API Endpoint**: `/api/v1/leads/`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: 401 error - authentication required
**HTTP Status Code**: 401

### Test Case ID: LEAD_AUTH_002
**Module**: Authentication
**Test Scenario**: Access lead endpoints with invalid token
**API Endpoint**: `/api/v1/leads/`
**Request Method**: GET
**Request Headers**: `Authorization: Bearer invalid_token`
**Expected Result**: 401 error - invalid token
**HTTP Status Code**: 401

### Test Case ID: LEAD_AUTH_003
**Module**: Permissions
**Test Scenario**: Access lead endpoints without CRM permissions
**API Endpoint**: `/api/v1/leads/`
**Request Method**: GET
**Request Headers**: Valid non-CRM user token
**Expected Result**: 403 error - CRM access required
**HTTP Status Code**: 403

### Test Case ID: LEAD_AUTH_004
**Module**: Ownership
**Test Scenario**: Update lead owned by another user
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "title": "Unauthorized Update"
}
```
**Expected Result**: 403 error - insufficient permissions
**HTTP Status Code**: 403

### Test Case ID: LEAD_AUTH_005
**Module**: Ownership
**Test Scenario**: Delete lead owned by another user
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: DELETE
**Request Payload**: None
**Expected Result**: 403 error - insufficient permissions
**HTTP Status Code**: 403

---

## Edge Cases Test Cases

### Test Case ID: LEAD_EDGE_001
**Module**: Edge Cases
**Test Scenario**: Create lead with extremely long title
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "This is an extremely long title that exceeds the maximum allowed length and should trigger a validation error from the database or serializer depending on the field constraints defined in the model",
    "person_id": 1,
    "amount": 1000.00
}
```
**Expected Result**: Validation error - title too long
**HTTP Status Code**: 400

### Test Case ID: LEAD_EDGE_002
**Module**: Edge Cases
**Test Scenario**: Create lead with very large amount
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Large Amount Lead",
    "person_id": 1,
    "amount": 99999999.99,
    "currency": "USD"
}
```
**Expected Result**: Lead created or validation error based on max_digits constraint
**HTTP Status Code**: 201 or 400

### Test Case ID: LEAD_EDGE_003
**Module**: Edge Cases
**Test Scenario**: Create lead with future expected_close date
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Future Close Lead",
    "person_id": 1,
    "expected_close": "2050-12-31T23:59:59Z"
}
```
**Expected Result**: Lead created successfully
**HTTP Status Code**: 201

### Test Case ID: LEAD_EDGE_004
**Module**: Edge Cases
**Test Scenario**: Create lead with past expected_close date
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Past Close Lead",
    "person_id": 1,
    "expected_close": "2020-01-01T00:00:00Z"
}
```
**Expected Result**: Lead created successfully (no validation on date)
**HTTP Status Code**: 201

### Test Case ID: LEAD_EDGE_005
**Module**: Edge Cases
**Test Scenario**: Create lead with non-existent person_id (should fail)
**API Endpoint**: `/api/v1/leads/`
**Request Method**: POST
**Request Payload**:
```json
{
    "title": "Invalid Person Lead",
    "person_id": 99999,
    "amount": 1000.00
}
```
**Expected Result**: Validation error - person with this ID does not exist
**HTTP Status Code**: 400

---

## Pipeline Transition Test Cases

### Test Case ID: LEAD_PIPE_001
**Module**: Pipeline Transition
**Test Scenario**: New → Follow Up (status change)
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "lead_status_id": 2
}
```
**Expected Result**: Lead status updated to "Follow Up"
**HTTP Status Code**: 200

### Test Case ID: LEAD_PIPE_002
**Module**: Pipeline Transition
**Test Scenario**: Follow Up → Qualified (status change + qualified flag)
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "lead_status_id": 3,
    "qualified": true
}
```
**Expected Result**: Lead status updated to "Qualified" and qualified flag set
**HTTP Status Code**: 200

### Test Case ID: LEAD_PIPE_003
**Module**: Pipeline Transition
**Test Scenario**: Qualified → Converted (convert to deal)
**API Endpoint**: `/api/v1/leads/1/convert/`
**Request Method**: POST
**Request Payload**:
```json
{
    "name": "Converted Deal Name",
    "amount": 15000.00
}
```
**Expected Result**: Lead converted to deal, lead marked as converted
**HTTP Status Code**: 200

### Test Case ID: LEAD_PIPE_004
**Module**: Pipeline Transition
**Test Scenario**: Qualified → Lost (status change)
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "lead_status_id": 4
}
```
**Expected Result**: Lead status updated to "Lost"
**HTTP Status Code**: 200

### Test Case ID: LEAD_PIPE_005
**Module**: Pipeline Transition
**Test Scenario**: Convert already converted lead (should fail)
**API Endpoint**: `/api/v1/leads/1/convert/`
**Request Method**: POST
**Request Payload**:
```json
{
    "name": "Second Conversion"
}
```
**Expected Result**: Validation error - lead already converted
**HTTP Status Code**: 400

### Test Case ID: LEAD_PIPE_006
**Module**: Pipeline Transition
**Test Scenario**: Bulk status update - Multiple leads to Qualified
**API Endpoint**: `/api/v1/leads/bulk_status/`
**Request Method**: POST
**Request Payload**:
```json
{
    "lead_ids": [1, 2, 3],
    "status_id": 3
}
```
**Expected Result**: All specified leads updated to Qualified status
**HTTP Status Code**: 200

---

## Bulk Operations Test Cases

### Test Case ID: LEAD_BULK_001
**Module**: Bulk Operations
**Test Scenario**: Bulk assign leads to user
**API Endpoint**: `/api/v1/leads/bulk_assign/`
**Request Method**: POST
**Request Payload**:
```json
{
    "lead_ids": [1, 2, 3],
    "assigned_user_id": 2
}
```
**Expected Result**: All specified leads assigned to user
**HTTP Status Code**: 200

### Test Case ID: LEAD_BULK_002
**Module**: Bulk Operations
**Test Scenario**: Bulk delete leads
**API Endpoint**: `/api/v1/leads/bulk_delete/`
**Request Method**: POST
**Request Payload**:
```json
{
    "lead_ids": [1, 2, 3]
}
```
**Expected Result**: All specified leads soft deleted
**HTTP Status Code**: 200

### Test Case ID: LEAD_BULK_003
**Module**: Bulk Operations
**Test Scenario**: Bulk operations with empty lead_ids (should fail)
**API Endpoint**: `/api/v1/leads/bulk_delete/`
**Request Method**: POST
**Request Payload**:
```json
{
    "lead_ids": []
}
```
**Expected Result**: Validation error - lead_ids required
**HTTP Status Code**: 400

### Test Case ID: LEAD_BULK_004
**Module**: Bulk Operations
**Test Scenario**: Bulk operations with non-existent lead IDs
**API Endpoint**: `/api/v1/leads/bulk_delete/`
**Request Method**: POST
**Request Payload**:
```json
{
    "lead_ids": [99999, 100000]
}
```
**Expected Result**: Operation completes with 0 leads affected
**HTTP Status Code**: 200

---

## Additional Features Test Cases

### Test Case ID: LEAD_FEAT_001
**Module**: Search
**Test Scenario**: Search leads by title
**API Endpoint**: `/api/v1/leads/?search=test`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Leads matching "test" in title/description with pagination
**HTTP Status Code**: 200

### Test Case ID: LEAD_FEAT_002
**Module**: Search
**Test Scenario**: Search with empty query (should return all results)
**API Endpoint**: `/api/v1/leads/?search=`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Returns all leads (empty search treated as no search filter)
**HTTP Status Code**: 200

### Test Case ID: LEAD_FEAT_003
**Module**: Notes
**Test Scenario**: Add note to lead
**API Endpoint**: `/api/v1/leads/1/notes/`
**Request Method**: POST
**Request Payload**:
```json
{
    "content": "This is a test note for the lead"
}
```
**Expected Result**: Note created and associated with lead
**HTTP Status Code**: 200

### Test Case ID: LEAD_FEAT_004
**Module**: Notes
**Test Scenario**: Add empty note (should fail)
**API Endpoint**: `/api/v1/leads/1/notes/`
**Request Method**: POST
**Request Payload**:
```json
{
    "content": ""
}
```
**Expected Result**: Validation error - note content required
**HTTP Status Code**: 400

### Test Case ID: LEAD_FEAT_005
**Module**: Labels
**Test Scenario**: Assign labels to lead
**API Endpoint**: `/api/v1/leads/1/labels/`
**Request Method**: POST
**Request Payload**:
```json
{
    "label_ids": [1, 2, 3]
}
```
**Expected Result**: Labels assigned to lead
**HTTP Status Code**: 200

### Test Case ID: LEAD_FEAT_006
**Module**: Labels
**Test Scenario**: Assign non-existent labels
**API Endpoint**: `/api/v1/leads/1/labels/`
**Request Method**: POST
**Request Payload**:
```json
{
    "label_ids": [99999, 100000]
}
```
**Expected Result**: Validation error - Invalid label IDs
**HTTP Status Code**: 400

---

## Performance Test Cases

### Test Case ID: LEAD_PERF_001
**Module**: Performance
**Test Scenario**: List leads with large dataset (1000+ leads)
**API Endpoint**: `/api/v1/leads/`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Response time under 2 seconds with proper pagination
**HTTP Status Code**: 200

### Test Case ID: LEAD_PERF_002
**Module**: Performance
**Test Scenario**: Search leads with large dataset
**API Endpoint**: `/api/v1/leads/?search=test`
**Request Method**: GET
**Request Payload**: None
**Expected Result**: Search results under 3 seconds with pagination
**HTTP Status Code**: 200

### Test Case ID: LEAD_PERF_003
**Module**: Performance
**Test Scenario**: Bulk operations with large dataset (500+ leads)
**API Endpoint**: `/api/v1/leads/bulk_status/`
**Request Method**: POST
**Request Payload**:
```json
{
    "lead_ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "status_id": 2
}
```
**Expected Result**: Bulk operation completes under 5 seconds
**HTTP Status Code**: 200

### Test Case ID: LEAD_PIPE_007
**Module**: Pipeline Transition
**Test Scenario**: Invalid pipeline transition - New → Converted (direct)
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "lead_status_id": 4
}
```
**Expected Result**: Validation error - Invalid pipeline transition (must go through Qualified first)
**HTTP Status Code**: 400

### Test Case ID: LEAD_PIPE_008
**Module**: Pipeline Transition
**Test Scenario**: Convert non-qualified lead
**API Endpoint**: `/api/v1/leads/1/convert/`
**Request Method**: POST
**Request Payload**:
```json
{
    "name": "Test Deal Conversion"
}
```
**Expected Result**: Validation error - Lead must be qualified before conversion
**HTTP Status Code**: 400

---

## Data Integrity Test Cases

### Test Case ID: LEAD_INT_001
**Module**: Data Integrity
**Test Scenario**: Soft delete - lead should not appear in normal list
**API Endpoint**: `/api/v1/leads/1/` (DELETE) then `/api/v1/leads/` (GET)
**Request Method**: DELETE then GET
**Request Payload**: None
**Expected Result**: Deleted lead should not appear in list but remain in database
**HTTP Status Code**: 200 (DELETE), 200 (GET)

### Test Case ID: LEAD_INT_002
**Module**: Data Integrity
**Test Scenario**: Convert lead - original lead should remain with converted_at timestamp
**API Endpoint**: `/api/v1/leads/1/convert/`
**Request Method**: POST
**Request Payload**:
```json
{
    "name": "Test Deal"
}
```
**Expected Result**: Lead marked as converted, deal created with lead data
**HTTP Status Code**: 200

### Test Case ID: LEAD_INT_003
**Module**: Data Integrity
**Test Scenario**: Update user tracking fields on modification
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT
**Request Payload**:
```json
{
    "title": "Updated Title"
}
```
**Expected Result**: user_updated_id and updated_at fields updated
**HTTP Status Code**: 200

### Test Case ID: LEAD_INT_004
**Module**: Concurrency
**Test Scenario**: Two users update same lead simultaneously
**API Endpoint**: `/api/v1/leads/1/`
**Request Method**: PUT (concurrent requests)
**Request Payload**:
```json
// User A updates amount
{
    "amount": 5000.00
}
```
```json
// User B updates title  
{
    "title": "Updated Title"
}
```
**Expected Result**: Last update wins (optimistic/pessimistic locking)
**HTTP Status Code**: 200

---

## Test Coverage Summary

**Total Test Cases**: 82
**Functional Tests**: 6
**API Tests**: 12  
**Validation Tests**: 5
**Authentication Tests**: 5
**Edge Cases**: 5
**Pipeline Transitions**: 8
**Bulk Operations**: 4
**Additional Features**: 6
**Performance Tests**: 3
**Data Integrity**: 4
**Pagination Tests**: 2
**Sorting Tests**: 3
**Concurrency Tests**: 1

**Critical Test Areas**:
1. Lead creation with validation
2. Pipeline transitions (New → Follow Up → Qualified → Converted/Lost)
3. Authentication and authorization
4. Bulk operations
5. Lead conversion to deals
6. Data integrity and soft delete
7. Pagination and sorting functionality
8. Concurrency handling and data consistency

**Success Criteria**:
- All CRUD operations working correctly
- Pipeline transitions enforced (including invalid transitions)
- Authentication and authorization working
- Data integrity maintained
- Performance within acceptable limits
- Validation rules properly enforced
- Pagination and sorting working correctly
- Concurrency handling robust
- Invalid business rules rejected (non-qualified conversion, etc.)
