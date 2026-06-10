---
component: application
name: Planning application
description: |
  Core planning application structure containing reference information,
  application types, submission details, modules, documents, and fees
fields:
  - field: reference
    required: true
  - field: tenure-type
    required: true
validation:
  - rule: "reference must be a valid UUID format"
  - rule: "application-types must reference valid application type codelist values"
  - rule: "planning-authority must be a valid organisation reference"
  - rule: "modules must reference existing module definitions"
  - rule: "document references must be unique within the application"
  - rule: "file must contain base64-content"
  - rule: "document-types must reference valid planning requirement codelist values"
entry-date: 2025-06-20
end-date: ''
---
