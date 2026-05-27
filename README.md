# Forms Generator

Example implementation of the [planning application data schema](https://github.com/digital-land/planning-application-data-specification). 

This repo demonstrates how to go from [schema specification files](https://github.com/digital-land/planning-application-data-specification/tree/main/specification) writen in yaml+mark down to Python classes.

These Python classes aer used to builf a [Flask](https://flask.palletsprojects.com/en/stable/) app (using [WTForms](https://wtforms.readthedocs.io/en/3.2.x/), a schema validator and a PDF generator.


## Local setup

Python packages and a python virtual environment. Stay in the pipenv shell for the steps below.

```shell
cp env_example .env
pipenv shell
pipenv install
```


Check it works by running the unittests-

```shell
python -m unittest discover
```

To run ETLs or the web app start by creating a settings file which is used as the default when running code locally-

```shell
cd settings
cp local_config_template.py local_config_YOURNAME.py
ln -s local_config_YOURNAME.py local_config.py
```

Update the parameters in `local_config_YOURNAME.py`. Without a map key from Google you'll get an error message and see a greyed out map.

To run the web app-

```shell
python web_viewer/app.py
```

Point a web browser at [http://127.0.0.1:2121](http://127.0.0.1:2121) and you should see a list of 'Planning application types'.


# Licence

The software in this project is open source and covered by the [LICENSE](LICENSE) file.

Individual datasets copied into this repository may have specific copyright and licensing, otherwise all content and data in this repository is [© Crown copyright](http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/copyright-and-re-use/crown-copyright/) and available under the terms of the [Open Government 3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/) licence.
