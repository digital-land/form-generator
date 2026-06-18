---
component: person
name: Person obj
description: |
  Details of an individual
fields:
  - field: first-name
    required: true
  - field: fullname
    required-if:
      - field: first-name
        operator: empty
entry-date: 2025-05-28
end-date: ''
---
