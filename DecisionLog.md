

To fill in properly later

* Generating python code from a template

* making a class for each application/module/component instead of using one class that changes behaviour when it's instantiated.

* not using a data class for the SchemaNode

* creating new classes in schema.schema_tree

* PlanningAppDataSpec and PlanningAppDataResolved instead of /bin/loader.py from 'planning application data schema' project. Separation between mark down file values and code interpretation of schema. This decision increases readability by having less code and intentionally makes the process more brittle. e.g. If the developer assumes a field is mandatory and it's missing the problem is either an invalid spec. file or the code is wrong. The code raises an exception rather than filling in with a default value.
