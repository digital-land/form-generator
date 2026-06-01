# Builder

Build Python classes from the [planning application data schema](https://github.com/digital-land/planning-application-data-specification).


## Overview

Representing the markdown/yaml schema as Python classes is intended to make the code more readable and discoverable by integrated development environments (IDEs) and other developer tooling.

For example, [component/time-range.md](https://github.com/digital-land/planning-application-data-specification/blob/main/specification/component/time-range.md) -


```yaml
---
component: time-range
name: Time range
description: Time range structure for opening and closing times
entry-date: 2025-07-16
end-date: ''
notes: ''
fields:
  - field: open-time
    required: true
  - field: close-time
    required: true
---
```

References two field files ([open time](https://github.com/digital-land/planning-application-data-specification/blob/main/specification/field/open-time.md) and [close tim](https://github.com/digital-land/planning-application-data-specification/blob/main/specification/field/close-time.md)


The three files are represented by a single Python class-


```python
class TimeRanges(SchemaNode):
    open_time = StringField(display="Open time", description="Opening time", max_length=None)
    close_time = StringField(display="Close time", description="Closing time", max_length=None)

    _ref = "time-ranges"
    _display = "Time range"
    _description = "Time range structure for opening and closing times"
```


Storing these Python classes in a Python module file comes with the cost of having to run the schema build tool (see below) when the upstream schema changes.


## Re-generating the schema

For convenience, this repo includes the current build of the schema in [schema/planning_applications.py](schema/planning_applications.py). It is built using [black](https://github.com/psf/black), the python formatter. This is primarily to keep the output consistent. If you used the instructions at the top level of this repo black will be included in your python virtual environment.


```python
python builder/build_schema.py|black - > schema/planning_applications.py
```

When re-generating the schema there is the opportunity to see a simple summary by viewing the code diff. e.g. for git repos `git diff`.
