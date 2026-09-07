# Forms Generator

Example implementation of the [planning application data schema](https://github.com/digital-land/planning-application-data-specification). 

This repo demonstrates how to go from [schema specification files](https://github.com/digital-land/planning-application-data-specification/tree/main/specification) writen in yaml+mark down to Python classes.

These Python classes are used with a [Flask](https://flask.palletsprojects.com/en/stable/) app to build HTML forms (using [WTForms](https://wtforms.readthedocs.io/en/3.2.x/)), a schema validator (to determine if a JSON documnet conforms with the schema) and a PDF generator for paper based forms.

This project is a prototype to demonstrate the structure of the planning application data schema. The forms produced have not had input from a content designer and the validate hasn't been through quality assurance.

This project is hosted publically at [https://form-generator.prototype.development.planning.data.gov.uk/](https://form-generator.prototype.development.planning.data.gov.uk/).


## Running Locally

Install Python packages and a Python virtual environment. Stay in this pipenv shell for the steps below.

```shell
cp env_example .env
pipenv shell
pipenv install --dev
```


Check it works by running the unittests-

```shell
python -m unittest discover
```

To run the [Builder](builder), web app or PDF generator, start by creating a local settings file. The `ln -s` symlink makes your settings file easily available as the default when running code locally-

```shell
cd settings
cp local_config_template.py local_config_YOURNAME.py
ln -s local_config_YOURNAME.py local_config.py
```

Update the parameters in `local_config_YOURNAME.py`. This only parameter likely to need an update is `PLANNING_APPLICATION_DATA_SPECIFICATION_REPO` and this is only needed if you are using the builder to update the Python classes derived from the specification.


To run the web app-

```shell
python web_viewer/app.py
```

Point a web browser at [http://127.0.0.1:2121](http://127.0.0.1:2121) and you should see a list of 'Planning application types'.


## Overview

The [builder](builder/README.md) package creates a simplified pythonic representation of the [planning application data schema](https://github.com/digital-land/planning-application-data-specification). The pythonic representation is a Python module of base schema classes which are intended to be intuative and simple. These classes are ready to be extended or used just like any other Python code in other parts of this project.

The [web app](web_client) is a Flask app for navigating planning applications. HTML forms are auto-built on demand from the *base schema classes* created by *builder*.

[PDFs](pdf_builder) are also built with the *base schema classes*. The web app has a link alongside each application type which dynamically builds a PDF.

The [technical overview](technical_overview.md) goes into greater depth.


## Deployment

A Dockerfile builds the web_viewer into deployable container.

The web_viewer uses the [schema/planning_application_specification.py](schema/planning_application_specification.py) included in this repo (i.e. it doesn't build from the external [schema specification github repo](https://github.com/digital-land/planning-application-data-specification/tree/main/specification).

The web_viewer does include dynamic building of PDFs. 

Build and run locally-

```shell
docker build -t forms-generator .
docker run -p 2121:2121 forms-generator
```


## Licence

The software in this project is open source and covered by the [LICENSE](LICENSE) file.

Individual datasets copied into this repository may have specific copyright and licensing, otherwise all content and data in this repository is [© Crown copyright](http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/copyright-and-re-use/crown-copyright/) and available under the terms of the [Open Government 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) licence.
