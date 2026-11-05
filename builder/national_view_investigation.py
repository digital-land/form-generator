"""
Project sample data into two representations - dataset and 'application document'.

Created on 22 Oct 2026

@author: si
"""

import copy
import csv
import json

import frontmatter
import ndjson

from builder.planning_app_data_spec import PlanningAppDataSpec

base_dir = "/Users/si/Documents/TPXimpact/"
planning_app_repo_path = base_dir + "Projects/planning-application-data-specification/"
public_view_schema_doc = f"{planning_app_repo_path}specification/national-public-view.schema.md"
example_docs_dir = base_dir + "Project Docs/Planning_Reform/Redbridge/"
example_apps = example_docs_dir + "Publication standard_with conditions.csv"


spec = PlanningAppDataSpec(planning_app_repo_path=planning_app_repo_path)

# for sample data
# 261,local-authority:RDB,London Borough of Redbridge,RDB,local-authority,local-authority,E60000217,2025-02-19,,
PLANNING_AUTHORITY_CODE = "local-authority:RDB"


# sample data to specification mapping
# sample_type -> specification
# these are Si's guess and not checked by someone who understands planning
app_type_map = {
    "Advertisement Consent": "advertising",
    "Listed Building Consent": "lbc",
    "Section 73 - Major": "s73",
    "Prior Approval Determination": "",
    "Householder (fasttrack)": "hh",
    "Householder": "hh",
    "Full Planning Permission": "full",
    "Works to TPO Tree(s)": "consent-under-tpo",
    "Section 73 - Minor": "s73",
}

decision_type_map = {
    "Granted/Approved - with conditions": "grant",
    "Prior Approval Required - Conditional Granted": "grant",
}


def show_schema():
    post = frontmatter.load(public_view_schema_doc)
    post_native = post.to_dict()

    for dataset in post_native["datasets"]:

        print(dataset["dataset"])

        r = {}
        for field in dataset["fields"]:

            field_name = field["field"]
            f = spec.fields[field_name]
            # print("\t", field_name, f.datatype, f.cardinality)
            # print("\t", field_name, spec.fields[field_name])
            r[field_name] = ""
        print(r)


def _is_outward_code(token):
    """First part of a UK postcode, e.g. 'SW1A', 'W1', 'EC1A', 'M1'."""
    letters = 0
    while letters < len(token) and token[letters].isalpha():
        letters += 1
    if letters == 0 or letters > 2:
        return False

    digits = letters
    while digits < len(token) and token[digits].isdigit():
        digits += 1
    if digits == letters:
        return False

    remainder = token[digits:]
    return remainder == "" or (len(remainder) == 1 and remainder.isalpha())


def _is_inward_code(token):
    """Second part of a UK postcode, e.g. '1AA'."""
    return len(token) == 3 and token[0].isdigit() and token[1:].isalpha()


def split_address_and_postcode(address_text):
    """
    Split a free-text address field into (address, postcode).

    Returns (address, None) when address_text doesn't end with
    something recognisable as a UK postcode.
    """
    if not address_text:
        return address_text, None

    tokens = address_text.split()
    if not tokens:
        return address_text, None

    last = tokens[-1].upper()

    # postcode given as two tokens, e.g. "... SW1A 1AA"
    if len(tokens) >= 2:
        second_last = tokens[-2].upper()
        if _is_inward_code(last) and _is_outward_code(second_last):
            postcode = f"{second_last} {last}"
            address = " ".join(tokens[:-2]).rstrip(" ,")
            return address, postcode

    # postcode given as one token, e.g. "... SW1A1AA"
    if 5 <= len(last) <= 7 and _is_inward_code(last[-3:]) and _is_outward_code(last[:-3]):
        postcode = f"{last[:-3]} {last[-3:]}"
        address = " ".join(tokens[:-1]).rstrip(" ,")
        return address, postcode

    return address_text, None


def reproject_sample_data():
    """
    Build two types of data layout from sample data.

    These are ideas on how
    to datasets view of national public view.

    @return (tuple) (datasets (dict), as_documents (list of dict))
    """
    f = open(example_apps)
    csv_reader = csv.DictReader(f)
    # xx = {fn: "" for fn in csv_reader.fieldnames}

    datasets = {
        "planning-application": [],
        "site": [],
        "decision-notice": [],
        "planning-condition": [],
        "decision-condition": [],
        # section-106 - can't do - no sample data
        # planning-application-document - can't do - no sample data
        "planning-permission-timeline": [],
    }

    # alternative view
    applications_as_documents = []
    application_doc_conditions = []

    # TODO
    planning_permission_timeline = {
        "reference": "",
        "planning-application": "",
        "permission-process-event": "",
        "event-date": "",
    }

    # CSV is cartesian product of application and conditions. This variable is used to unbundle them
    current_app_ref = None
    planning_application = None
    site = None
    decision_notice = None
    sub_row_index = 0
    for app_row in csv_reader:

        # print(app_row)

        if current_app_ref is None:
            current_app_ref = app_row["Application Number"]

        if app_row["Application Number"] != current_app_ref and planning_application:
            # next application has been reached

            # process application document view
            app_doc = copy.copy(planning_application)
            app_doc["site"] = site
            app_doc["decision_notice"] = copy.copy(decision_notice)
            app_doc["decision_notice"]["conditions"] = application_doc_conditions
            applications_as_documents.append(app_doc)

            # reset
            application_doc_conditions = []

            # process items for dataset views and reset items
            datasets["planning-application"].append(planning_application)
            datasets["site"].append(site)
            datasets["decision-notice"].append(decision_notice)
            planning_application = {}
            current_app_ref = app_row["Application Number"]
            sub_row_index = 0

        # commented out means not yet used
        # --------------------------------
        # app_row["Decision Date"] # one and the same with despatch date
        # app_row["Level of Decision"]
        # app_row["Prescription Type"]  # condition is type C - is implied in sample data
        # TODO "development-scale" - not complete set in specification - major, minor, other,
        # not required, prior cert
        # This is over simplified and wrong
        development_scale_simplified = None
        if "Minor" in app_row["PS_DEVELOPMENT_trans"]:
            development_scale_simplified = "minor"
        elif "Major" in app_row["PS_DEVELOPMENT_trans"]:
            development_scale_simplified = "major"

        # This is a boolean in the spec. but 'Unknown' in sample data. It's a MUST not sure how to
        # map between the two.
        # app_row["PP Agreement Exists"]

        # insufficient sample data to build S106
        # app_row["S106 Indicator"]
        # app_row["S106 Signed Date"]

        planning_application = {
            "reference": app_row["Application Number"],
            # "name": "", not in sample data and field is SHOULD
            "description": app_row["Full Description"],
            "application-types": app_type_map[app_row["Application Type"]],
            # single site with single reference for sample data
            "site": app_row["Application Number"],
            "received-date": app_row["Received Date"],
            "planning-authority": PLANNING_AUTHORITY_CODE,
            "development-scale": development_scale_simplified,
            "planning-performance-agreement": None,
            "withdrawn-date": None,
            "linked-applications": None,
            "document-url": None,
            "documentation-url": None,
            "notes": None,
        }

        address_text, postcode = split_address_and_postcode(app_row["Main Location"])

        site = {
            "reference": app_row["Application Number"],
            "name": None,
            "address-text": address_text,
            "postcode": postcode or None,
            "uprns": None,
            "usrns": None,  # TBC - if uprns are supplied should this?
            "geometry": None,
        }

        decision_notice = {
            "reference": app_row["Application Number"],
            "planning-application": app_row["Application Number"],
            "decision": decision_type_map[app_row["Decision"]],
            "decision-date": app_row["Despatch Date"],
            "organisation": None,  # TBC - is this the local authority or the upstream organisation?
            "decision-maker": None,
            "planning-officer-recommendation": app_row["Officer Recommendation"],
            "document-url": None,
            "documentation-url": None,
            "notes": None,
        }

        decision_condition = {
            "reference": app_row["Application Number"] + f"_{sub_row_index}",
            "decision-notice": app_row["Application Number"],
            "planning-condition": app_row["Application Number"] + f"_{sub_row_index}",
            "requested-by": None,
            "discharged-by": None,
        }

        planning_condition = {
            "reference": app_row["Application Number"] + f"_{sub_row_index}",
            "name": app_row["Short Description"],
            "description": app_row["Long Description"],
            "reason": None,
            "organisation": None,
        }

        datasets["decision-condition"].append(decision_condition)
        datasets["planning-condition"].append(copy.copy(planning_condition))

        # this reference is used when discharging a condition. It's being lost in the dataset view.
        # It's an ordered id - legal doc for the condition references this id
        planning_condition["reference"] = str(app_row["prnseqnum"])

        # version used in application-document view
        application_doc_conditions.append(planning_condition)

        sub_row_index += 1

    f.close()
    return datasets, applications_as_documents


if __name__ == "__main__":
    # show_schema()

    datasets, as_documents = reproject_sample_data()
    for ds_name, dataset_values in datasets.items():

        dataset_path = example_docs_dir + f"{ds_name}.ndjson"
        print(f"Writing {dataset_path}")
        with open(dataset_path, "wt", encoding="utf-8-sig") as f:
            ndjson_out = ndjson.writer(f)
            for s in datasets[ds_name]:
                ndjson_out.writerow(s)

        # As list of dict
        dataset_path = example_docs_dir + f"{ds_name}.json"
        print(f"Writing {dataset_path}")
        with open(dataset_path, "wt", encoding="utf-8-sig") as f:
            json.dump(datasets[ds_name], f)

    as_documents_path = example_docs_dir + f"application_documents.ndjson"
    print(f"Writing {as_documents_path}")
    with open(as_documents_path, "wt", encoding="utf-8-sig") as f:
        ndjson_out = ndjson.writer(f)
        for s in as_documents:
            ndjson_out.writerow(s)

    as_documents_path = example_docs_dir + f"application_documents.json"
    print(f"Writing {as_documents_path}")
    with open(as_documents_path, "wt", encoding="utf-8-sig") as f:
        json.dump(as_documents, f)

    print("All done!")
