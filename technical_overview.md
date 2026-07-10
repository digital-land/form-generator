
# Technical Overview

This project is a prototype and example implmentation aimed at covering the following areas-

* HTML forms
* PDF 'paper' style forms
* Payload validation
* Readable code
* Usable code by 3rd parties

The approach used is opinionated and uses language features specific to Python. Other software architectures are available!


## Builder (The Complicated Bit)

The [planning application data schema](https://github.com/digital-land/planning-application-data-specification) contains around 760 files describing the data standard. These files are well structured YML wrapped in Markdown.

The first stage is to transform the spec files into a structure which is easier for humans, AI and dev. tools to work with.

Using a language to write code in the same language isn't a universally agreed approach but does have a few strong advantages-

* The two projects are decoupled
* Code in this project is much more readable
* Understanding the schema now requires reading Python which is more universally understood than the schema's markdown notation
* Less brittle if the upsteam schema change isn't supported. The build simply fails and code can be rolled to last working version.
* Pythonic approach for other parts of the project (i.e. HTML forms, PDFs and payload verification) 

[Code for the builder](./builder) is complex because the specification's schema has a lot of internal referencing.

Each markdown file (i.e. `*.md`) is loaded into a Python dataclass derived from `SchemaBase`. These are loaded by the `PlanningAppDataSpec` class and each dataclass stands alone without references to to other parts of the specification.

The `PlanningAppDataResolved` class inherits from `PlanningAppDataSpec` and has the role of linking all the references together. For example, a planning application uses `Modules` which are named. The process of resolving the modules is just looking these up and linking them into the data structure.

The `build_schema.py` module uses a Jinja2 template to write Python classes into a string. Python is able to `eval` and use these but it's more readable to write these into a file. Instructions for this are in the [build README](build/README.md).

 
## Schema

The Python classes build in the last step are an [ORM](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping) like view of the specification. The schema is arranged as a tree with leaves being scalar fields with the expectation that a user would enter values into these fields.

The `SchemaNode` classes use a Pythonic coding construct called a [descriptor](https://rszalski.github.io/magicmethods/#descriptor) to make class attributes also useable when data is loaded into the an instance of the class.

TLDR; The `SchemaNode` classes define what is allowed in the schema. An instance of these classes allow data to be evaluated against the schema to determine if it's valid.

The data schema (upstream specification project) defines Applications, Modules, Components and Fields. The `SchemaNode` classes are a simplification and just use `SchemaNode` and fields which are subclasses of `AbstractSchemaField`.


The `planning_application_ui.py` module demonstrates how details by the specification can be overridden without making changes to the file created by the `build_schema.py` process. This makes it possible to re-run `build_schema.py` without loosing local changes.

The `planning_application.py` module joins the `planning_application_specification.py` and `planning_application_ui.py` modules into one namespace. This namespace is the only place that should be used by the rest of the project.


## The rest of the project

PDFs, Web Forms and Validation are much simpler. They all use the unified `planning_application.py` classes.

Validation is performed by the `SchemaNode` instances. There is a web page for pasting a JSON payload for evaluation. Submitting a web form sends the user submitted values to validation.
