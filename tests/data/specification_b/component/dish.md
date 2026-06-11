---
component: dish
name: Dish
description: |
  Dish details
fields:
  - field: title
  - field: description
  - field: contains-cheese
    required: true
  - field: reason
    required-if:
      - field: contains-cheese
        value: false
entry-date: 2026-06-04
end-date: ''
---
