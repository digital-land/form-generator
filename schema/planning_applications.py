from schema.schema_tree import (
    BooleanField,
    EnumField,
    EnumOption,
    schema_node_root_classes,
    SchemaNode,
    SchemaNodeField,
    StringField,
)


class PhoneNumbers(SchemaNode):
    _ref = "phone-numbers"
    _display = "Phone number"
    _description = "A substructure for recording a phone number "

    number = StringField(display="Phone number", description="A phone number", max_length=None)
    contact_priority = EnumField(
        display="Contact priority",
        description="The priority of a number",
        select_options=[
            EnumOption(key="primary", label="Primary", description="The preferred item to use"),
            EnumOption(
                key="secondary",
                label="Secondary",
                description="The option to use if primary is not working",
            ),
        ],
    )


class ContactDetails(SchemaNode):
    _ref = "contact-details"
    _display = "Contact details"
    _description = "A substructure for recording contact details "

    email = StringField(
        display="Email",
        description="The email address that can be used for electronic correspondence with the individual",
        max_length=None,
    )

    phone_numbers = SchemaNodeField(
        display="Phone number",
        description="A substructure for recording a phone number ",
        schema_node_cls=PhoneNumbers,
    )


class AgentContact(SchemaNode):
    _ref = "agent-contact"
    _display = "Agent contact details"
    _description = "Name and contact information if an agent is being used."

    agent_reference = StringField(
        display="Agent reference", description="A reference to an agent object", max_length=None
    )

    contact_details = SchemaNodeField(
        display="Contact details",
        description="A substructure for recording contact details ",
        schema_node_cls=ContactDetails,
    )


class Person(SchemaNode):
    _ref = "person"
    _display = "Person obj"
    _description = "Details of an individual "

    title = StringField(display="Title", description="The title of the individual", max_length=None)
    first_name = StringField(
        display="First Name", description="The first name of the individual", max_length=None
    )
    last_name = StringField(
        display="Last Name", description="The last name of the individual", max_length=None
    )
    address_text = StringField(
        display="Address Text",
        description="Flexible field for capturing addresses",
        max_length=None,
    )
    postcode = StringField(display="Postcode", description="The postal code", max_length=None)


class Agent(SchemaNode):
    _ref = "agent"
    _display = "Agent obj"
    _description = "Details of the agent acting on behalf of the applicant, including name and organisation if applicable "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    company = StringField(
        display="Company",
        description="The name of a company (that the agent works for)",
        max_length=None,
    )
    user_role = EnumField(
        display="User role",
        description="The role of the named individual. Agent or proxy",
        select_options=[
            EnumOption(
                key="agent",
                label="Agent",
                description="A professional agent working for the applicant",
            ),
            EnumOption(
                key="proxy",
                label="Proxy",
                description="An individual working on behalf of the applicant but not in a professional capacity",
            ),
        ],
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )


class AgentDetails(SchemaNode):
    _ref = "agent-details"
    _display = "Agent details"
    _description = "Name and contact information if an agent is being used."

    agent = SchemaNodeField(
        display="Agent obj",
        description="Details of the agent acting on behalf of the applicant, including name and organisation if applicable ",
        schema_node_cls=Agent,
    )


class ApplicantContact(SchemaNode):
    _ref = "applicant-contact"
    _display = "Applicant contact details"
    _description = "Telephone number and email address of the applicant."

    applicant_reference = StringField(
        display="Applicant reference",
        description="Reference to match contact details to a named individual from the applicant details component",
        max_length=None,
    )

    contact_details = SchemaNodeField(
        display="Contact details",
        description="A substructure for recording contact details ",
        schema_node_cls=ContactDetails,
    )


class Applicants(SchemaNode):
    _ref = "applicants"
    _display = "Applicant"
    _description = "Details of an individual applicant for the planning application, including their personal information and contact details "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )


class ApplicantDetails(SchemaNode):
    _ref = "applicant-details"
    _display = "Applicant details"
    _description = "Name and contact information for the parties making the application."

    applicants = SchemaNodeField(
        display="Applicant",
        description="Details of an individual applicant for the planning application, including their personal information and contact details ",
        schema_node_cls=Applicants,
    )


class BngConditionExemptionReasons(SchemaNode):
    _ref = "bng-condition-exemption-reasons"
    _display = "BNG exemption reason"
    _description = "Reason why Biodiversity Net Gain does not apply, referencing specific exemptions or transitional arrangements "

    exemption_type = EnumField(
        display="Exemption type",
        description="The type of biodiversity gain exemption from the bng-exemption-type enum",
        select_options=[
            EnumOption(
                key="pre-commencement",
                label="Submitted before BNG commencement",
                description="Planning applications submitted before the Biodiversity Net Gain rules took effect (need to add the effective date)",
            ),
            EnumOption(
                key="small-sites",
                label="Small sites exemption",
                description="Temporary exemption for non-major developments.",
            ),
            EnumOption(
                key="de-minimis",
                label="De minimis exemption",
                description="Development below the minimum threshold for BNG requirements.",
            ),
            EnumOption(
                key="self-build",
                label="Self-build and custom build",
                description="Self-build or custom build development projects.",
            ),
            EnumOption(
                key="gain-site",
                label="Biodiversity gain site",
                description="Development of a registered biodiversity gain site.",
            ),
            EnumOption(
                key="retrospective",
                label="Retrospective planning permission",
                description="Applications for retrospective planning permission.",
            ),
            EnumOption(
                key="hs2",
                label="High Speed Railway development",
                description="Development related to the High Speed Railway (HS2).",
            ),
        ],
    )
    reason = StringField(display="Reason", description="A textual reason", max_length=None)


class HabitatLossDetails(SchemaNode):
    _ref = "habitat-loss-details"
    _display = "Habitat loss details"
    _description = (
        "Details about habitat loss or degradation events that occurred after January 30, 2020 "
    )

    loss_date = StringField(
        display="Loss date",
        description="Date the activity causing habitat loss or degradation occurred",
        max_length=None,
    )
    pre_loss_biodiversity_value = StringField(
        display="Pre loss biodiversity value",
        description="Biodiversity value immediately before habitat loss or degradation occurred, measured in Habitat Biodiversity Units",
        max_length=None,
    )
    supporting_evidence = StringField(
        display="Supporting evidence",
        description="Description or reference to supporting documents for habitat loss or degradation evidence",
        max_length=None,
    )


class SupportingDocuments(SchemaNode):
    _ref = "supporting-documents"
    _display = "Supporting document"
    _description = "Reference to a supporting document already listed in application.documents "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    details = StringField(
        display="Details",
        description="Additional details or information about an item",
        max_length=None,
    )


class BngDetails(SchemaNode):
    _ref = "bng-details"
    _display = "Biodiversity net gain details"
    _description = "Details about the biodiversity net gain assessment including pre-development value, habitat loss information, and required supporting documents "

    pre_development_date = StringField(
        display="Pre development date",
        description="Date of pre-development biodiversity value calculation, must align with application or justified earlier date",
        max_length=None,
    )
    pre_development_biodiversity_value = StringField(
        display="Pre development biodiversity value",
        description="Calculated biodiversity value in Habitat Biodiversity Units",
        max_length=None,
    )
    earlier_date_reason = StringField(
        display="Earlier date reason",
        description="Reason for using a pre-development date that is earlier than the application submission",
        max_length=None,
    )
    habitat_loss_after_2020 = BooleanField(
        display="Habitat loss after 2020",
        description="Indicates whether there has been degradation of onsite habitat(s) after 30 Jan 2020",
    )
    metric_publication_date = StringField(
        display="Metric publication date",
        description="Publication date of the biodiversity metric tool used for calculations",
        max_length=None,
    )
    irreplaceable_habitats = BooleanField(
        display="Irreplaceable habitats",
        description="Indicates whether the site contains any irreplaceable habitats",
    )
    irreplaceable_habitats_details = StringField(
        display="Irreplaceable habitats details",
        description="Description and references for any irreplaceable habitats identified on the site",
        max_length=None,
    )

    habitat_loss_details = SchemaNodeField(
        display="Habitat loss details",
        description="Details about habitat loss or degradation events that occurred after January 30, 2020 ",
        schema_node_cls=HabitatLossDetails,
    )
    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class Bng(SchemaNode):
    _ref = "bng"
    _display = "Biodiversity net gain"
    _description = (
        "How any natural habitats on the development site will be improved by the proposed works."
    )

    bng_exempt = BooleanField(
        display="Biodiversity gain exemption",
        description="Statement whether the biodiversity gain condition will apply if permission is granted. Householder applicants need to confirm the biodiversity gain condition does not apply.",
    )
    bng_condition_applies = BooleanField(
        display="Biodiversity gain condition applies",
        description="Does the applicant believe the Biodiversity Gain Condition applies to this application",
    )

    bng_condition_exemption_reasons = SchemaNodeField(
        display="BNG exemption reason",
        description="Reason why Biodiversity Net Gain does not apply, referencing specific exemptions or transitional arrangements ",
        schema_node_cls=BngConditionExemptionReasons,
    )
    bng_details = SchemaNodeField(
        display="Biodiversity net gain details",
        description="Details about the biodiversity net gain assessment including pre-development value, habitat loss information, and required supporting documents ",
        schema_node_cls=BngDetails,
    )


class Checklist(SchemaNode):
    _ref = "checklist"
    _display = "Checklist"
    _description = "Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation."

    national_req_types = StringField(
        display="National requirement types",
        description="List of the document types required for the given application type",
        max_length=None,
    )


class ConflictOfInterest(SchemaNode):
    _ref = "conflict-of-interest"
    _display = "Conflict of interest"
    _description = "Details of any conflict of interest that may exist between the applicant and planning authority."

    conflict_to_declare = BooleanField(
        display="Conflict to declare",
        description="Indicates whether any named applicant or agent has a relationship to the planning authority that must be declared",
    )
    person_reference = StringField(
        display="Person reference",
        description="A reference to an applicant, agent or named individual",
        max_length=None,
    )
    conflict_details = StringField(
        display="Conflict details",
        description="Details of the conflict of interest including name, role and how the individual is related to the planning authority",
        max_length=None,
    )


class Declaration(SchemaNode):
    _ref = "declaration"
    _display = "Declaration"
    _description = "Signed and dated verification of the application's accuracy."

    person_reference = StringField(
        display="Person reference",
        description="A reference to an applicant, agent or named individual",
        max_length=None,
    )
    declaration_confirmed = BooleanField(
        display="Declaration confirmed",
        description="Confirms the applicant or agent has reviewed and validated the information provided in the application",
    )
    declaration_date = StringField(
        display="Declaration date", description="The date the declaration was made", max_length=None
    )


class ExistingEmployees(SchemaNode):
    _ref = "existing-employees"
    _display = "Employees"
    _description = "Employee count information including full-time, part-time, and total full-time equivalent (FTE) calculations "

    full_time = StringField(
        display="Full-time", description="Number of full-time employees", max_length=None
    )
    part_time = StringField(
        display="Part-time", description="Number of part-time employees", max_length=None
    )
    total_fte = StringField(
        display="Total FTE", description="Total full-time equivalent (FTE)", max_length=None
    )


class ProposedEmployees(SchemaNode):
    _ref = "proposed-employees"
    _display = "Employees"
    _description = "Employee count information including full-time, part-time, and total full-time equivalent (FTE) calculations "

    full_time = StringField(
        display="Full-time", description="Number of full-time employees", max_length=None
    )
    part_time = StringField(
        display="Part-time", description="Number of part-time employees", max_length=None
    )
    total_fte = StringField(
        display="Total FTE", description="Total full-time equivalent (FTE)", max_length=None
    )


class Employment(SchemaNode):
    _ref = "employment"
    _display = "Employment"
    _description = "How the proposed development will impact existing and proposed employee numbers"

    existing_employees = SchemaNodeField(
        display="Employees",
        description="Employee count information including full-time, part-time, and total full-time equivalent (FTE) calculations ",
        schema_node_cls=ExistingEmployees,
    )
    proposed_employees = SchemaNodeField(
        display="Employees",
        description="Employee count information including full-time, part-time, and total full-time equivalent (FTE) calculations ",
        schema_node_cls=ProposedEmployees,
    )


class ExistingUseDetails(SchemaNode):
    _ref = "existing-use-details"
    _display = "Existing use detail"
    _description = "Information about a specific existing use on the site, including use class, additional details, and which part of the land it relates to "

    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    use_details = StringField(
        display="Use details", description="Further detail of the use", max_length=None
    )
    land_part = StringField(
        display="Land part",
        description="Which part of the land the use relates to",
        max_length=None,
    )


class ExistingUse(SchemaNode):
    _ref = "existing-use"
    _display = "Existing use"
    _description = "How the site is currently being used."

    site_vacant = BooleanField(display="Site vacant", description="Is the site currently vacant")
    last_use_details = StringField(
        display="Last use details",
        description="Description of the last use of the site",
        max_length=None,
    )
    last_use_end_date = StringField(
        display="Last use end date",
        description="Date the last use ended (YYYY-MM-DD format)",
        max_length=None,
    )
    is_contaminated_land = BooleanField(
        display="Is contaminated land", description="Is the site known to be contaminated?"
    )
    is_suspected_contaminated_land = BooleanField(
        display="Is suspected contaminated land",
        description="Is the site suspected of contamination?",
    )
    proposed_use_contamination_risk = BooleanField(
        display="Proposed use contamination risk",
        description="Is the proposed use vulnerable to the presence of contamination?",
    )
    contamination_assessment = StringField(
        display="Contamination assessment",
        description="Reference to contamination assessment document",
        max_length=None,
    )

    existing_use_details = SchemaNodeField(
        display="Existing use detail",
        description="Information about a specific existing use on the site, including use class, additional details, and which part of the land it relates to ",
        schema_node_cls=ExistingUseDetails,
    )


class FloodRiskAssessment(SchemaNode):
    _ref = "flood-risk-assessment"
    _display = "Flood risk assessment"
    _description = "Results of any flood risk assessments made for the development site"

    flood_risk_area = BooleanField(
        display="Flood risk area", description="Is the site within an area at risk of flooding?"
    )
    data_provided_by = EnumField(
        display="Data provided by",
        description="Who provided the data: Applicant or System/Service?",
        select_options=[
            EnumOption(
                key="applicant",
                label="Applicant",
                description="Information provided by the applicant",
            ),
            EnumOption(
                key="system",
                label="System/Service",
                description="Information calculated or determined by the system or external service",
            ),
        ],
    )
    flood_risk_assessment = StringField(
        display="Flood risk assessment",
        description="Reference of the flood risk assessment document",
        max_length=None,
    )
    within_20m_watercourse = BooleanField(
        display="Within 20m watercourse",
        description="Whether the development is within 20 metres of a watercourse",
    )
    increases_flood_risk = BooleanField(
        display="Increases flood risk", description="Whether the development increases flood risk"
    )
    surface_water_disposal = EnumField(
        display="Surface water disposal",
        description="Method for disposing of surface water",
        select_options=[
            EnumOption(
                key="sustainable-drainage",
                label="Sustainable drainage system",
                description="System designed to manage surface water sustainably.",
            ),
            EnumOption(
                key="soakaway",
                label="Soakaway",
                description="Underground pit allowing water to drain naturally.",
            ),
            EnumOption(
                key="main-sewer",
                label="Main sewer",
                description="Surface water directed into the main sewer system.",
            ),
            EnumOption(
                key="existing-watercourse",
                label="Existing watercourse",
                description="Water discharged into an existing river, stream, or canal.",
            ),
            EnumOption(
                key="pond-lake",
                label="Pond/lake",
                description="Surface water discharged into a pond or lake.",
            ),
        ],
    )


class TimeRanges(SchemaNode):
    _ref = "time-ranges"
    _display = "Time range"
    _description = "Time range structure for opening and closing times"

    open_time = StringField(display="Open time", description="Opening time", max_length=None)
    close_time = StringField(display="Close time", description="Closing time", max_length=None)


class OperationalTimes(SchemaNode):
    _ref = "operational-times"
    _display = "Operational times"
    _description = "Opening times structure for operational hours by day"

    schedule_days = EnumField(
        display="Schedule days",
        description="List of days or day categories that a schedule entry applies to",
        select_options=[
            EnumOption(key="monday", label="Monday", description=""),
            EnumOption(key="tuesday", label="Tuesday", description=""),
            EnumOption(key="wednesday", label="Wednesday", description=""),
            EnumOption(key="thursday", label="Thursday", description=""),
            EnumOption(key="friday", label="Friday", description=""),
            EnumOption(key="saturday", label="Saturday", description=""),
            EnumOption(key="sunday", label="Sunday", description=""),
            EnumOption(key="bank-holiday", label="Bank holiday", description=""),
        ],
    )
    closed = BooleanField(
        display="Closed", description="True or False - explicitly state when closed"
    )

    time_ranges = SchemaNodeField(
        display="Time range",
        description="Time range structure for opening and closing times",
        schema_node_cls=TimeRanges,
    )


class HoursOfOperation(SchemaNode):
    _ref = "hours-of-operation"
    _display = "Hours of operation"
    _description = "Hours of operation structure for non-residential use"

    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    use_other = StringField(
        display="Use other", description='Specify use if use is "other"', max_length=None
    )
    hours_not_known = BooleanField(
        display="Hours not known",
        description="Applicant states they do not know the hours of operation",
    )

    operational_times = SchemaNodeField(
        display="Operational times",
        description="Opening times structure for operational hours by day",
        schema_node_cls=OperationalTimes,
    )


class HrsOperation(SchemaNode):
    _ref = "hrs-operation"
    _display = "Hours of operation"
    _description = (
        "Proposed operating hours if the proposed development is intended for non-residential use."
    )

    additional_information = StringField(
        display="Additional information",
        description="Any additional information (such as hours of use of other machinery within the site-generators, pumps, etc)",
        max_length=None,
    )

    hours_of_operation = SchemaNodeField(
        display="Hours of operation",
        description="Hours of operation structure for non-residential use",
        schema_node_cls=HoursOfOperation,
    )


class FloorspaceDetails(SchemaNode):
    _ref = "floorspace-details"
    _display = "Floorspace details"
    _description = "Details of non-residential floorspace changes by use class including existing, lost, and proposed amounts"

    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    specified_use = StringField(
        display="Specified use",
        description="A specified use if no applicable use class is available",
        max_length=None,
    )
    existing_gross_floorspace = StringField(
        display="Existing gross floorspace",
        description="Existing gross internal floorspace, in sqm",
        max_length=None,
    )
    floorspace_lost = StringField(
        display="Floorspace lost",
        description="Gross floorspace to be lost by change of use, in sqm",
        max_length=None,
    )
    total_gross_proposed = StringField(
        display="Total gross proposed",
        description="Total gross internal floorspace proposed, in sqm",
        max_length=None,
    )
    net_additional_floorspace = StringField(
        display="Net additional floorspace",
        description="Net additional gross internal floorspace, in sqm",
        max_length=None,
    )


class FloorspaceDetailsOutline(SchemaNode):
    _ref = "floorspace-details-outline"
    _display = "Floorspace details"
    _description = "Details of non-residential floorspace changes by use class including existing, lost, and proposed amounts. Specifically for outline applications"

    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    specified_use = StringField(
        display="Specified use",
        description="A specified use if no applicable use class is available",
        max_length=None,
    )
    existing_gross_floorspace = StringField(
        display="Existing gross floorspace",
        description="Existing gross internal floorspace, in sqm",
        max_length=None,
    )
    is_floorspace_lost_known = BooleanField(
        display="Is floorspace lost known",
        description="Whether the amount of floorspace to be lost is known",
    )
    floorspace_lost = StringField(
        display="Floorspace lost",
        description="Gross floorspace to be lost by change of use, in sqm",
        max_length=None,
    )
    is_total_gross_proposed_known = BooleanField(
        display="Is total gross proposed known",
        description="Whether the total gross proposed floorspace is known",
    )
    total_gross_proposed = StringField(
        display="Total gross proposed",
        description="Total gross internal floorspace proposed, in sqm",
        max_length=None,
    )
    net_additional_floorspace = StringField(
        display="Net additional floorspace",
        description="Net additional gross internal floorspace, in sqm",
        max_length=None,
    )


class RoomDetails(SchemaNode):
    _ref = "room-details"
    _display = "Room details"
    _description = "Details of room changes for hotels, residential institutions and hostels (C1, C2, C2A use classes)"

    use_class_accommodation = EnumField(
        display="Use class for accommodation",
        description="Type of non-residential use class referring to accommodation uses",
        select_options=[
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    use_other = StringField(
        display="Use other", description='Specify use if use is "other"', max_length=None
    )
    existing_rooms_lost = StringField(
        display="Existing rooms lost",
        description="Existing rooms to be lost by change of use",
        max_length=None,
    )
    total_rooms_proposed = StringField(
        display="Total rooms proposed",
        description="Total rooms proposed (including change of use)",
        max_length=None,
    )
    net_additional_rooms = StringField(
        display="Net additional rooms",
        description="Net additional rooms following development",
        max_length=None,
    )


class RoomDetailsOutline(SchemaNode):
    _ref = "room-details-outline"
    _display = "Room details"
    _description = "Details of room changes for hotels, residential institutions and hostels (C1, C2, C2A use classes)"

    use_class_accommodation = EnumField(
        display="Use class for accommodation",
        description="Type of non-residential use class referring to accommodation uses",
        select_options=[
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    use_other = StringField(
        display="Use other", description='Specify use if use is "other"', max_length=None
    )
    is_existing_rooms_lost_known = BooleanField(
        display="Is existing rooms lost known",
        description="Whether the total existing rooms that will be lost is known",
    )
    existing_rooms_lost = StringField(
        display="Existing rooms lost",
        description="Existing rooms to be lost by change of use",
        max_length=None,
    )
    is_total_rooms_proposed_known = BooleanField(
        display="Is total rooms proposed known",
        description="Whether the total rooms proposed is known",
    )
    total_rooms_proposed = StringField(
        display="Total rooms proposed",
        description="Total rooms proposed (including change of use)",
        max_length=None,
    )
    net_additional_rooms = StringField(
        display="Net additional rooms",
        description="Net additional rooms following development",
        max_length=None,
    )


class NonResFloorspace(SchemaNode):
    _ref = "non-res-floorspace"
    _display = "Non residential floorspace"
    _description = "Details of changes to non-residential floorspace in the proposed development."

    non_residential_change = BooleanField(
        display="Non residential change",
        description="Does the proposal involve the loss, gain, or change of non-residential floorspace?",
    )
    non_residential_change_outline = EnumField(
        display="Non residential change",
        description="Does the proposal involve the loss, gain, or change of non-residential floorspace?",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response  "),
            EnumOption(
                key="unknown",
                label="Unknown",
                description="Status is not known or cannot be determined",
            ),
        ],
    )

    floorspace_details = SchemaNodeField(
        display="Floorspace details",
        description="Details of non-residential floorspace changes by use class including existing, lost, and proposed amounts",
        schema_node_cls=FloorspaceDetails,
    )
    floorspace_details_outline = SchemaNodeField(
        display="Floorspace details",
        description="Details of non-residential floorspace changes by use class including existing, lost, and proposed amounts. Specifically for outline applications",
        schema_node_cls=FloorspaceDetailsOutline,
    )
    room_details = SchemaNodeField(
        display="Room details",
        description="Details of room changes for hotels, residential institutions and hostels (C1, C2, C2A use classes)",
        schema_node_cls=RoomDetails,
    )
    room_details_outline = SchemaNodeField(
        display="Room details",
        description="Details of room changes for hotels, residential institutions and hostels (C1, C2, C2A use classes)",
        schema_node_cls=RoomDetailsOutline,
    )


class OwnersAndTenants(SchemaNode):
    _ref = "owners-and-tenants"
    _display = "Notified person"
    _description = "Details of a person that has been notified (often owners and agricultural tenants of the land)"

    notice_date = StringField(
        display="Notice date",
        description="Date when notice was served to an owner or tenant",
        max_length=None,
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )


class LbcOwners(SchemaNode):
    _ref = "lbc-owners"
    _display = "Notified person"
    _description = "Details of a person that has been notified (often owners and agricultural tenants of the land)"

    notice_date = StringField(
        display="Notice date",
        description="Date when notice was served to an owner or tenant",
        max_length=None,
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )


class NewspaperNotices(SchemaNode):
    _ref = "newspaper-notices"
    _display = "Newspaper notice"
    _description = "Details of the newspaper notice published for unknown owners/tenants"

    newspaper_name = StringField(
        display="Newspaper name",
        description="Name of the newspaper where the ownership notice was published",
        max_length=None,
    )
    publication_date = StringField(
        display="Publication date",
        description="Date when the ownership notice was published in the newspaper",
        max_length=None,
    )


class OwnershipCerts(SchemaNode):
    _ref = "ownership-certs"
    _display = "Ownership certificates and agricultural land declaration"
    _description = "Who will be affected by the proposal and whether they have been notified, such as agricultural tenants"

    sole_owner = BooleanField(
        display="Sole owner", description="Is the applicant the sole owner of the land?"
    )
    agricultural_tenants = BooleanField(
        display="Agricultural tenants",
        description="Are there any agricultural tenants on the land?",
    )
    steps_taken = StringField(
        display="Steps taken",
        description="Description of steps taken to identify unknown owners or tenants",
        max_length=None,
    )
    ownership_cert_option = EnumField(
        display="Ownership certificate type",
        description="The type of ownership certificate based on ownership and tenancy status",
        select_options=[
            EnumOption(
                key="certificate-a",
                label="Certificate A",
                description="Applicant is the sole owner of the land and there are no agricultural tenants.",
            ),
            EnumOption(
                key="certificate-b",
                label="Certificate B",
                description="Applicant knows all other owners or agricultural tenants and has notified them.",
            ),
            EnumOption(
                key="certificate-c",
                label="Certificate C",
                description="Applicant knows some of the other owners or agricultural tenants and has notified those they know.",
            ),
            EnumOption(
                key="certificate-d",
                label="Certificate D",
                description="Applicant does not know any of the other owners or agricultural tenants.",
            ),
        ],
    )
    person_reference = StringField(
        display="Person reference",
        description="A reference to an applicant, agent or named individual",
        max_length=None,
    )
    declaration_confirmed = BooleanField(
        display="Declaration confirmed",
        description="Confirms the applicant or agent has reviewed and validated the information provided in the application",
    )
    declaration_date = StringField(
        display="Declaration date", description="The date the declaration was made", max_length=None
    )

    owners_and_tenants = SchemaNodeField(
        display="Notified person",
        description="Details of a person that has been notified (often owners and agricultural tenants of the land)",
        schema_node_cls=OwnersAndTenants,
    )
    lbc_owners = SchemaNodeField(
        display="Notified person",
        description="Details of a person that has been notified (often owners and agricultural tenants of the land)",
        schema_node_cls=LbcOwners,
    )
    newspaper_notices = SchemaNodeField(
        display="Newspaper notice",
        description="Details of the newspaper notice published for unknown owners/tenants",
        schema_node_cls=NewspaperNotices,
    )


class PreAppAdvice(SchemaNode):
    _ref = "pre-app-advice"
    _display = "Pre-application advice"
    _description = (
        "Details of pre-application advice previously received from the planning authority"
    )

    advice_sought = BooleanField(
        display="Pre-application advice sought",
        description="Whether pre-application advice has been sought from the planning authority",
    )
    officer_name = StringField(
        display="Officer name",
        description="Name of the planning officer who provided the pre-application advice",
        max_length=None,
    )
    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    advice_date = StringField(
        display="Advice date",
        description="Date when pre-application advice was received, in YYYY-MM-DD format",
        max_length=None,
    )
    advice_summary = StringField(
        display="Advice summary",
        description="Summary of the pre-application advice received from the planning authority",
        max_length=None,
    )


class WasteManagement(SchemaNode):
    _ref = "waste-management"
    _display = "Waste management"
    _description = "Details of applicable waste management facilities including type, capacity, and throughput information. "

    waste_management_facility_type = EnumField(
        display="Waste management facility type",
        description="Type of waste management facility being described in this entry",
        select_options=[
            EnumOption(
                key="inert-landfill",
                label="Inert Landfill",
                description="Disposal site for inert waste materials.",
            ),
            EnumOption(
                key="non-hazardous-landfill",
                label="Non-Hazardous Landfill",
                description="Landfill for non-hazardous waste.",
            ),
            EnumOption(
                key="hazardous-landfill",
                label="Hazardous Landfill",
                description="Landfill site for hazardous waste.",
            ),
            EnumOption(
                key="energy-waste-incineration",
                label="Energy from Waste Incineration",
                description="Incineration facility generating energy from waste.",
            ),
            EnumOption(
                key="other-incineration",
                label="Other Incineration",
                description="Non-energy-producing incineration sites.",
            ),
            EnumOption(
                key="landfill-gas-plant",
                label="Landfill Gas Generation Plant",
                description="Plant generating energy from landfill gas.",
            ),
            EnumOption(
                key="pyrolysis-gasification",
                label="Pyrolysis/Gasification",
                description="Facilities using pyrolysis or gasification processes.",
            ),
            EnumOption(
                key="metal-recycling",
                label="Metal Recycling Site",
                description="Site for recycling metals.",
            ),
            EnumOption(
                key="transfer-stations",
                label="Transfer Stations",
                description="Facilities for sorting and transferring waste.",
            ),
            EnumOption(
                key="mrf",
                label="Material Recovery Facility (MRF)",
                description="Facility for sorting recyclable materials.",
            ),
            EnumOption(
                key="household-amenity-site",
                label="Household Civic Amenity Sites",
                description="Public waste disposal sites for households.",
            ),
            EnumOption(
                key="open-windrow-composting",
                label="Open Windrow Composting",
                description="Outdoor composting of biodegradable waste.",
            ),
            EnumOption(
                key="in-vessel-composting",
                label="In-Vessel Composting",
                description="Enclosed composting for controlled conditions.",
            ),
            EnumOption(
                key="anaerobic-digestion",
                label="Anaerobic Digestion",
                description="Plant for organic waste decomposition without oxygen.",
            ),
            EnumOption(
                key="mbt",
                label="Mechanical, Biological, or Thermal (MBT)",
                description="Combined waste treatment facility.",
            ),
            EnumOption(
                key="sewage-treatment",
                label="Sewage Treatment Works",
                description="Plant for treating wastewater.",
            ),
            EnumOption(
                key="other-treatment",
                label="Other Treatment",
                description="Any other waste treatment not listed.",
            ),
            EnumOption(
                key="construction-recycling",
                label="Recycling Facilities for Construction Waste",
                description="Sites recycling construction and demolition waste.",
            ),
            EnumOption(
                key="waste-storage",
                label="Storage of Waste",
                description="Facilities for storing waste before processing.",
            ),
            EnumOption(
                key="other-waste-management",
                label="Other Waste Management",
                description="Any other waste management facility not listed.",
            ),
            EnumOption(
                key="other-developments",
                label="Other Developments",
                description="Any other related developments.",
            ),
        ],
    )
    total_capacity = StringField(
        display="Total capacity",
        description="Total capacity of void in cubic metres (or tonnes/litres)",
        max_length=None,
    )
    unit_type = EnumField(
        display="Unit type",
        description="Unit for capacity/throughput (e.g. cubic metres, tonnes, litres)",
        select_options=[
            EnumOption(
                key="cubic-metres",
                label="Cubic metres",
                description="Measured by volume in cubic metres",
            ),
            EnumOption(key="tonnes", label="Tonnes", description="Measured by mass in tonnes"),
            EnumOption(key="litres", label="Litres", description="Measured by volume in litres"),
        ],
    )
    annual_throughput = StringField(
        display="Annual throughput",
        description="Maximum annual operational throughput in tonnes/litres",
        max_length=None,
    )
    unit_type = EnumField(
        display="Unit type",
        description="Unit for capacity/throughput (e.g. cubic metres, tonnes, litres)",
        select_options=[
            EnumOption(
                key="cubic-metres",
                label="Cubic metres",
                description="Measured by volume in cubic metres",
            ),
            EnumOption(key="tonnes", label="Tonnes", description="Measured by mass in tonnes"),
            EnumOption(key="litres", label="Litres", description="Measured by volume in litres"),
        ],
    )


class WasteStreams(SchemaNode):
    _ref = "waste-streams"
    _display = "Waste streams"
    _description = "Annual throughput for different types of waste streams "

    municipal = StringField(
        display="Municipal",
        description="Maximum throughput for municipal waste (annual throughput in tonnes/litres)",
        max_length=None,
    )
    construction_demolition = StringField(
        display="Construction demolition",
        description="Maximum throughput for construction and demolition waste (annual throughput in tonnes/litres)",
        max_length=None,
    )
    commercial_industrial = StringField(
        display="Commercial industrial",
        description="Maximum throughput for commercial and industrial waste (annual throughput in tonnes/litres)",
        max_length=None,
    )
    hazardous = StringField(
        display="Hazardous",
        description="Maximum throughput for hazardous waste (annual throughput in tonnes/litres)",
        max_length=None,
    )


class ProcessesMachineryWaste(SchemaNode):
    _ref = "processes-machinery-waste"
    _display = "Processes machinery waste"
    _description = "How waste will be managed on the site "

    site_activity_details = StringField(
        display="Site activity details",
        description="Description of activities, processes, and end products including site operations, plant, ventilation, and machinery",
        max_length=None,
    )
    proposal_waste_management = BooleanField(
        display="Proposal waste management",
        description="Whether the proposal involves any waste management facility that is relevant to the proposal",
    )

    waste_management = SchemaNodeField(
        display="Waste management",
        description="Details of applicable waste management facilities including type, capacity, and throughput information. ",
        schema_node_cls=WasteManagement,
    )
    waste_streams = SchemaNodeField(
        display="Waste streams",
        description="Annual throughput for different types of waste streams ",
        schema_node_cls=WasteStreams,
    )


class RelatedApplication(SchemaNode):
    _ref = "related-application"
    _display = "Related application details"
    _description = "Details about a related application including its reference, description and decision date "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    decision_date = StringField(
        display="Decision date",
        description="The date when the decision was made, in YYYY-MM-DD format",
        max_length=None,
    )


class ProposalDetails(SchemaNode):
    _ref = "proposal-details"
    _display = "Description of the proposal"
    _description = "What development, works or change of use is proposed"

    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    reserved_matters = EnumField(
        display="Reserved matters",
        description="Identifies which reserved matters are being submitted for approval as part of this application",
        select_options=[
            EnumOption(key="access", label="Access", description=""),
            EnumOption(key="appearance", label="Appearance", description=""),
            EnumOption(key="landscaping", label="Landscaping", description=""),
            EnumOption(key="layout", label="Layout", description=""),
            EnumOption(key="scale", label="Scale", description=""),
        ],
    )
    proposal_started = BooleanField(
        display="Proposal started", description="Has any work on the proposal already been started"
    )
    proposal_started_date = StringField(
        display="Proposal start date",
        description="The date when work on the proposal started, in YYYY-MM-DD format",
        max_length=None,
    )
    proposal_completed = BooleanField(
        display="Proposal completed",
        description="Has any work on the proposal already been completed",
    )
    proposal_completed_date = StringField(
        display="Proposal completion date",
        description="The date when work on the proposal was completed, in YYYY-MM-DD format",
        max_length=None,
    )
    pip_reference = StringField(
        display="PIP reference",
        description="Reference number for the Planning in Principle (PIP) application this relates to",
        max_length=None,
    )
    is_psi = BooleanField(
        display="Is public service infrastructure",
        description="For applications made on or after 1 August 2021, is the proposal for public service infrastructure development",
    )

    related_application = SchemaNodeField(
        display="Related application details",
        description="Details about a related application including its reference, description and decision date ",
        schema_node_cls=RelatedApplication,
    )


class UnitsPerBedroomNo(SchemaNode):
    _ref = "units-per-bedroom-no"
    _display = "Bedroom count"
    _description = (
        "Structure for counting units by bedroom number, allowing for unknown bedroom counts "
    )

    no_bedrooms_unknown = BooleanField(
        display="No bedrooms unknown",
        description="Set to true when counting units where bedroom number is unknown",
    )
    no_of_bedrooms = StringField(
        display="Number of bedrooms", description="The number of bedrooms in unit", max_length=None
    )
    units = StringField(
        display="Units", description="The number of units of that bedroom count", max_length=None
    )


class ExistingUnitBreakdown(SchemaNode):
    _ref = "existing-unit-breakdown"
    _display = "Unit quantities"
    _description = "Structure for defining quantities of units, either as unknown or broken down by bedroom count "

    units_unknown = BooleanField(
        display="Units unknown", description="Whether the number of units is unknown"
    )
    total_units = StringField(
        display="Total units", description="Total number of units", max_length=None
    )

    units_per_bedroom_no = SchemaNodeField(
        display="Bedroom count",
        description="Structure for counting units by bedroom number, allowing for unknown bedroom counts ",
        schema_node_cls=UnitsPerBedroomNo,
    )


class ProposedUnitBreakdown(SchemaNode):
    _ref = "proposed-unit-breakdown"
    _display = "Unit quantities"
    _description = "Structure for defining quantities of units, either as unknown or broken down by bedroom count "

    units_unknown = BooleanField(
        display="Units unknown", description="Whether the number of units is unknown"
    )
    total_units = StringField(
        display="Total units", description="Total number of units", max_length=None
    )

    units_per_bedroom_no = SchemaNodeField(
        display="Bedroom count",
        description="Structure for counting units by bedroom number, allowing for unknown bedroom counts ",
        schema_node_cls=UnitsPerBedroomNo,
    )


class ResidentialUnitSummary(SchemaNode):
    _ref = "residential-unit-summary"
    _display = "Residential unit summary"
    _description = "Breakdown of residential unit counts by tenure and housing type, with optional unit breakdowns "

    tenure_type = EnumField(
        display="Tenure type",
        description="Category of housing tenure",
        select_options=[
            EnumOption(
                key="market-housing",
                label="Market Housing",
                description="Private housing for sale or rent.",
            ),
            EnumOption(
                key="social-rented",
                label="Social Rented Housing",
                description="Public/social housing at below-market rents.",
            ),
            EnumOption(
                key="intermediate-housing",
                label="Intermediate Housing",
                description="Housing with rents or ownership costs between social housing and market housing.",
            ),
            EnumOption(
                key="key-worker-housing",
                label="Key Worker Housing",
                description="Housing for essential workers (e.g. teachers, NHS staff).",
            ),
            EnumOption(
                key="affordable-rent",
                label="Social, Affordable, or Intermediate Rent",
                description="Housing for below-market rent.",
            ),
            EnumOption(
                key="home-ownership",
                label="Affordable Home Ownership",
                description="Shared ownership or similar schemes.",
            ),
            EnumOption(
                key="starter-homes",
                label="Starter Homes",
                description="Discounted homes for first-time buyers.",
            ),
            EnumOption(
                key="custom-build",
                label="Self-Build and Custom Build",
                description="Homes built or commissioned by individuals.",
            ),
            EnumOption(
                key="market-for-sale",
                label="Market for sale",
                description="Market housing for sale.",
            ),
            EnumOption(
                key="market-for-rent",
                label="Market for rent",
                description="Market housing for rent.",
            ),
            EnumOption(
                key="shared-equity",
                label="Shared Equity",
                description="Shared equity affordable home ownership product.",
            ),
            EnumOption(
                key="affordable-rent-not-lar-bm",
                label="Affordable Rent (not at LAR benchmark rents)",
                description="Affordable rent product not set at London Affordable Rent benchmark rents.",
            ),
            EnumOption(
                key="discount-market-sale",
                label="Discount Market Sale",
                description="Discounted market sale product.",
            ),
            EnumOption(
                key="discount-market-rent",
                label="Discount Market Rent",
                description="Discounted market rent product.",
            ),
            EnumOption(key="social-rent", label="Social Rent", description="Social rent product."),
            EnumOption(
                key="intermediate-other",
                label="Intermediate Other",
                description="Other intermediate housing product.",
            ),
            EnumOption(
                key="discount-market-llr",
                label="Discount Market Rent (charged at London Living Rents)",
                description="Discount market rent product charged at London Living Rent levels.",
            ),
            EnumOption(
                key="london-living-rent",
                label="London Living Rent",
                description="London Living Rent product.",
            ),
            EnumOption(
                key="london-shared-ownership",
                label="London Shared Ownership",
                description="London shared ownership product.",
            ),
            EnumOption(
                key="london-affordable-rent",
                label="London Affordable Rent",
                description="London Affordable Rent product.",
            ),
        ],
    )
    housing_type = EnumField(
        display="Housing type",
        description="Type of housing",
        select_options=[
            EnumOption(
                key="houses",
                label="Houses",
                description="Detached, semi-detached, or terraced houses.",
            ),
            EnumOption(
                key="flats-maisonettes",
                label="Flats/Maisonettes",
                description="Self-contained apartments or maisonettes.",
            ),
            EnumOption(
                key="sheltered-housing",
                label="Sheltered Housing",
                description="Housing with support for older or disabled people.",
            ),
            EnumOption(
                key="bedsit-studio", label="Bedsit/Studio", description="Single-room living spaces."
            ),
            EnumOption(
                key="cluster-flats",
                label="Cluster Flats",
                description="Flats with shared communal areas.",
            ),
            EnumOption(
                key="other", label="Other", description="Any other housing type not listed."
            ),
            EnumOption(
                key="live-work-units",
                label="Live-Work Units",
                description="Properties combining residential and workspace.",
            ),
            EnumOption(
                key="unknown", label="Unknown", description="When the type of housing is uncertain."
            ),
            EnumOption(
                key="terraced-home", label="Terraced Home", description="Terraced house type."
            ),
            EnumOption(
                key="house-or-bungalow",
                label="House or Bungalow",
                description="House or bungalow type.",
            ),
            EnumOption(
                key="semi-detached-home",
                label="Semi Detached Home",
                description="Semi-detached house type.",
            ),
            EnumOption(
                key="flat-apartment-maisonette",
                label="Flat Apartment Maisonette",
                description="Flat apartment or maisonette type.",
            ),
            EnumOption(key="co-living-unit", label="Co Living Unit", description="Co-living unit."),
            EnumOption(key="hmo", label="HMO", description="House in multiple occupation."),
            EnumOption(
                key="student-accommodation",
                label="Student Accommodation",
                description="Student accommodation.",
            ),
            EnumOption(
                key="communal-space",
                label="Communal Space",
                description="Communal space associated with residential use.",
            ),
        ],
    )

    existing_unit_breakdown = SchemaNodeField(
        display="Unit quantities",
        description="Structure for defining quantities of units, either as unknown or broken down by bedroom count ",
        schema_node_cls=ExistingUnitBreakdown,
    )
    proposed_unit_breakdown = SchemaNodeField(
        display="Unit quantities",
        description="Structure for defining quantities of units, either as unknown or broken down by bedroom count ",
        schema_node_cls=ProposedUnitBreakdown,
    )


class ResUnits(SchemaNode):
    _ref = "res-units"
    _display = "Residential units"
    _description = (
        "Details of the residential units that make up both the current and proposed development."
    )

    will_residential_units_change = BooleanField(
        display="Residential unit change",
        description="Proposal includes the gain, loss or change of use of residential units",
    )
    total_existing_units = StringField(
        display="Total existing units",
        description="The total number of existing units",
        max_length=None,
    )
    total_proposed_units = StringField(
        display="Total proposed units",
        description="The total number of proposed units",
        max_length=None,
    )
    net_change = StringField(
        display="Net change", description="Calculated net change in units", max_length=None
    )

    residential_unit_summary = SchemaNodeField(
        display="Residential unit summary",
        description="Breakdown of residential unit counts by tenure and housing type, with optional unit breakdowns ",
        schema_node_cls=ResidentialUnitSummary,
    )


class SiteArea(SchemaNode):
    _ref = "site-area"
    _display = "Site area"
    _description = "How big the site is including relevant measurements"

    site_area_in_hectares = StringField(
        display="Site area in hectares",
        description="The size of the site in hectares",
        max_length=None,
    )
    site_area_provided_by = EnumField(
        display="Site area provided by",
        description="Who provided the site area value",
        select_options=[
            EnumOption(
                key="applicant",
                label="Applicant",
                description="Information provided by the applicant",
            ),
            EnumOption(
                key="system",
                label="System/Service",
                description="Information calculated or determined by the system or external service",
            ),
        ],
    )


class SiteLocations(SchemaNode):
    _ref = "site-locations"
    _display = "Site location"
    _description = "Details about the location of a development site, including its boundary, address, and/or coordinates "

    site_boundary = StringField(
        display="Site boundary",
        description="Geometry of the site of the development, typically in GeoJSON format",
        max_length=None,
    )
    address_text = StringField(
        display="Address Text",
        description="Flexible field for capturing addresses",
        max_length=None,
    )
    postcode = StringField(display="Postcode", description="The postal code", max_length=None)
    easting = StringField(
        display="Easting",
        description="Easting coordinate in British National Grid (EPSG:27700)",
        max_length=None,
    )
    northing = StringField(
        display="Northing",
        description="Northing coordinate in British National Grid (EPSG:27700)",
        max_length=None,
    )
    latitude = StringField(
        display="Latitude", description="Latitude coordinate in WGS84 (EPSG:4326)", max_length=None
    )
    longitude = StringField(
        display="Longitude",
        description="Longitude coordinate in WGS84 (EPSG:4326)",
        max_length=None,
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    uprns = StringField(
        display="UPRNs",
        description="Unique Property Reference Numbers (UPRNs) for properties within the site boundary",
        max_length=None,
    )


class SiteDetails(SchemaNode):
    _ref = "site-details"
    _display = "Site details"
    _description = "Where the proposed development will be built."

    site_locations = SchemaNodeField(
        display="Site location",
        description="Details about the location of a development site, including its boundary, address, and/or coordinates ",
        schema_node_cls=SiteLocations,
    )


class OtherContact(SchemaNode):
    _ref = "other-contact"
    _display = "Other contact"
    _description = (
        "Details of another contact person for site visits when not using the applicant or agent "
    )

    fullname = StringField(
        display="Full name", description="The complete name of a person", max_length=None
    )
    number = StringField(display="Phone number", description="A phone number", max_length=None)
    email = StringField(
        display="Email",
        description="The email address that can be used for electronic correspondence with the individual",
        max_length=None,
    )


class SiteVisit(SchemaNode):
    _ref = "site-visit"
    _display = "Site Visit Details"
    _description = "Information to help the planning authority arrange a site visit"

    can_be_seen_from = BooleanField(
        display="Site seen from public area",
        description="Can site be seen from a public road, public footpath, bridleway or other public land",
    )
    contact_type = EnumField(
        display="Site visit contact type",
        description="Indicates who the authority should contact to arrange a site visit",
        select_options=[
            EnumOption(
                key="applicant", label="Applicant", description="The applicant of the application"
            ),
            EnumOption(key="agent", label="Agent", description="The agent who completed the form"),
        ],
    )
    contact_reference = StringField(
        display="Contact reference",
        description="The reference of the applicant or agent who should be contacted for site visits",
        max_length=None,
    )

    other_contact = SchemaNodeField(
        display="Other contact",
        description="Details of another contact person for site visits when not using the applicant or agent ",
        schema_node_cls=OtherContact,
    )


class OutlineAll(SchemaNode):
    _ref = "outline-all"
    _display = "Outline Planning Permission with All Matters Reserved"
    _description = "Outline planning permission with all matters reserved"

    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    bng = SchemaNodeField(
        display="Biodiversity net gain",
        description="How any natural habitats on the development site will be improved by the proposed works.",
        schema_node_cls=Bng,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    employment = SchemaNodeField(
        display="Employment",
        description="How the proposed development will impact existing and proposed employee numbers",
        schema_node_cls=Employment,
    )
    existing_use = SchemaNodeField(
        display="Existing use",
        description="How the site is currently being used.",
        schema_node_cls=ExistingUse,
    )
    flood_risk_assessment = SchemaNodeField(
        display="Flood risk assessment",
        description="Results of any flood risk assessments made for the development site",
        schema_node_cls=FloodRiskAssessment,
    )
    hrs_operation = SchemaNodeField(
        display="Hours of operation",
        description="Proposed operating hours if the proposed development is intended for non-residential use.",
        schema_node_cls=HrsOperation,
    )
    non_res_floorspace = SchemaNodeField(
        display="Non residential floorspace",
        description="Details of changes to non-residential floorspace in the proposed development.",
        schema_node_cls=NonResFloorspace,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    processes_machinery_waste = SchemaNodeField(
        display="Processes machinery waste",
        description="How waste will be managed on the site ",
        schema_node_cls=ProcessesMachineryWaste,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    res_units = SchemaNodeField(
        display="Residential units",
        description="Details of the residential units that make up both the current and proposed development.",
        schema_node_cls=ResUnits,
    )
    site_area = SchemaNodeField(
        display="Site area",
        description="How big the site is including relevant measurements",
        schema_node_cls=SiteArea,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class File(SchemaNode):
    _ref = "file"
    _display = "File"
    _description = "Structure for digital files to be included in the submission of an application "

    base64_content = StringField(
        display="Base64",
        description="Base64-encoded content of the file for inline file uploads",
        max_length=None,
    )
    filename = StringField(
        display="Filename",
        description="Name of the file being uploaded useful for identifying and preserving the file",
        max_length=None,
    )
    mime_type = StringField(
        display="MIME type",
        description="The file's MIME type such as application/pdf or image/jpeg",
        max_length=None,
    )
    file_size = StringField(
        display="File size",
        description="Size of the file in bytes that can be used to enforce limits",
        max_length=None,
    )


class Documents(SchemaNode):
    _ref = "documents"
    _display = "Document"
    _description = (
        "Structure for submitted documents including reference, metadata, and file information "
    )

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    name = StringField(display="Name", description="A name of a person", max_length=None)
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    document_types = StringField(
        display="Document types",
        description="List of codelist references that the document covers",
        max_length=None,
    )
    uploaded_date = StringField(
        display="Uploaded date",
        description="The date the document was uploaded to the application",
        max_length=None,
    )

    file = SchemaNodeField(
        display="File",
        description="Structure for digital files to be included in the submission of an application ",
        schema_node_cls=File,
    )


class Fee(SchemaNode):
    _ref = "fee"
    _display = "Fee"
    _description = "Structure for application fees including amounts due, amounts paid, and transaction references "

    amount = StringField(
        display="Amount",
        description="The total amount due for the application fee",
        max_length=None,
    )
    amount_paid = StringField(
        display="Amount paid",
        description="The amount paid towards the application fee",
        max_length=None,
    )
    transactions = StringField(
        display="Transactions",
        description="References to payments or financial transactions related to this application",
        max_length=None,
    )


class SubmissionDetails(SchemaNode):
    _ref = "submission-details"
    _display = "Submission details"
    _description = "Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees "

    submission_reference = StringField(
        display="Submission reference",
        description="A unique reference for the submission",
        max_length=None,
    )
    application_types = StringField(
        display="Application types",
        description="A list of planning application types that define the nature of the planning application",
        max_length=None,
    )
    specification_profile = EnumField(
        display="Specification profile",
        description="The specification profile used to determine context-specific allowed codelist values for the application",
        select_options=[
            EnumOption(
                key="mhclg-core",
                label="MHCLG core",
                description="The core national specification profile used by MHCLG.",
            ),
            EnumOption(
                key="gla",
                label="GLA",
                description="The Greater London Authority profile used where GLA-specific requirements apply.",
            ),
        ],
    )
    planning_authority = EnumField(
        display="Planning authority",
        description="A reference of the planning authority the application has been submitted to, e.g. local-authority:CMD for London borough of Camden",
        select_options=[
            EnumOption(key="local-authority:ADU", label="Adur District Council", description=None),
            EnumOption(
                key="local-authority:ALL", label="Allerdale Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:AMB", label="Amber Valley Borough Council", description=None
            ),
            EnumOption(key="local-authority:ARU", label="Arun District Council", description=None),
            EnumOption(
                key="local-authority:ASF", label="Ashford Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:ASH", label="Ashfield District Council", description=None
            ),
            EnumOption(
                key="local-authority:AYL", label="Aylesbury Vale District Council", description=None
            ),
            EnumOption(
                key="local-authority:BAB", label="Babergh District Council", description=None
            ),
            EnumOption(
                key="local-authority:BAE", label="Bassetlaw District Council", description=None
            ),
            EnumOption(
                key="local-authority:BAI", label="Basildon Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BAN",
                label="Basingstoke and Deane Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BAR",
                label="Barrow-in-Furness Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BAS",
                label="Bath and North East Somerset Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BBD",
                label="Blackburn with Darwen Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BDF", label="Bedford Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BDG",
                label="London Borough of Barking and Dagenham",
                description=None,
            ),
            EnumOption(
                key="local-authority:BEN", label="London Borough of Brent", description=None
            ),
            EnumOption(
                key="local-authority:BEX", label="London Borough of Bexley", description=None
            ),
            EnumOption(
                key="local-authority:BIR", label="Birmingham City Council", description=None
            ),
            EnumOption(
                key="local-authority:BKM", label="Buckinghamshire County Council", description=None
            ),
            EnumOption(key="local-authority:BLA", label="Blaby District Council", description=None),
            EnumOption(
                key="local-authority:BMH", label="Bournemouth Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BNE", label="London Borough of Barnet", description=None
            ),
            EnumOption(
                key="local-authority:BNH", label="Brighton and Hove City Council", description=None
            ),
            EnumOption(
                key="local-authority:BNS",
                label="Barnsley Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BOL",
                label="Bolton Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BOS", label="Bolsover District Council", description=None
            ),
            EnumOption(key="local-authority:BOT", label="Boston Borough Council", description=None),
            EnumOption(
                key="local-authority:BPC",
                label="Bournemouth, Christchurch and Poole Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BPL", label="Blackpool Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BRA", label="Braintree District Council", description=None
            ),
            EnumOption(
                key="local-authority:BRC", label="Bracknell Forest Council", description=None
            ),
            EnumOption(
                key="local-authority:BRD",
                label="City of Bradford Metropolitan District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:BRE", label="Breckland District Council", description=None
            ),
            EnumOption(
                key="local-authority:BRM", label="Bromsgrove District Council", description=None
            ),
            EnumOption(
                key="local-authority:BRO", label="Broadland District Council", description=None
            ),
            EnumOption(
                key="local-authority:BRT", label="Broxtowe Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BRW", label="Brentwood Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BRX", label="Broxbourne Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BRY", label="London Borough of Bromley", description=None
            ),
            EnumOption(key="local-authority:BST", label="Bristol City Council", description=None),
            EnumOption(
                key="local-authority:BUC", label="Buckinghamshire Council", description=None
            ),
            EnumOption(
                key="local-authority:BUN", label="Burnley Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:BUR",
                label="Bury Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(key="local-authority:CAB", label="Cambridge City Council", description=None),
            EnumOption(
                key="local-authority:CAM", label="Cambridgeshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:CAN", label="Cannock Chase District Council", description=None
            ),
            EnumOption(key="local-authority:CAR", label="Carlisle City Council", description=None),
            EnumOption(
                key="local-authority:CAS", label="Castle Point Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:CAT", label="Canterbury City Council", description=None
            ),
            EnumOption(
                key="local-authority:CBF", label="Central Bedfordshire Council", description=None
            ),
            EnumOption(
                key="local-authority:CHA", label="Charnwood Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:CHC", label="Christchurch Borough Council", description=None
            ),
            EnumOption(key="local-authority:CHE", label="Cheshire East Council", description=None),
            EnumOption(
                key="local-authority:CHI", label="Chichester District Council", description=None
            ),
            EnumOption(
                key="local-authority:CHL", label="Chelmsford City Council", description=None
            ),
            EnumOption(
                key="local-authority:CHN", label="Chiltern District Council", description=None
            ),
            EnumOption(
                key="local-authority:CHO", label="Chorley Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:CHR", label="Cherwell District Council", description=None
            ),
            EnumOption(
                key="local-authority:CHS", label="Chesterfield Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:CHT", label="Cheltenham Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:CHW",
                label="Cheshire West and Chester Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:CLD",
                label="Calderdale Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(key="local-authority:CMA", label="Cumbria County Council", description=None),
            EnumOption(
                key="local-authority:CMD", label="London Borough of Camden", description=None
            ),
            EnumOption(
                key="local-authority:COL", label="Colchester City Council", description=None
            ),
            EnumOption(key="local-authority:CON", label="Cornwall Council", description=None),
            EnumOption(
                key="local-authority:COP", label="Copeland Borough Council", description=None
            ),
            EnumOption(key="local-authority:COR", label="Corby Borough Council", description=None),
            EnumOption(
                key="local-authority:COT", label="Cotswold District Council", description=None
            ),
            EnumOption(key="local-authority:COV", label="Coventry City Council", description=None),
            EnumOption(
                key="local-authority:CPCA",
                label="Cambridgeshire and Peterborough Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:CRA", label="Craven District Council", description=None
            ),
            EnumOption(
                key="local-authority:CRW", label="Crawley Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:CRY", label="London Borough of Croydon", description=None
            ),
            EnumOption(
                key="local-authority:DAC", label="Dacorum Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:DAL", label="Darlington Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:DAR", label="Dartford Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:DAV", label="Daventry District Council", description=None
            ),
            EnumOption(
                key="local-authority:DBY", label="Derbyshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:DEB",
                label="Derbyshire Dales District Council",
                description=None,
            ),
            EnumOption(key="local-authority:DER", label="Derby City Council", description=None),
            EnumOption(key="local-authority:DEV", label="Devon County Council", description=None),
            EnumOption(
                key="local-authority:DNC",
                label="Doncaster Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(key="local-authority:DOR", label="Dorset County Council", description=None),
            EnumOption(key="local-authority:DOV", label="Dover District Council", description=None),
            EnumOption(key="local-authority:DST", label="Dorset Council", description=None),
            EnumOption(
                key="local-authority:DUD",
                label="Dudley Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(key="local-authority:DUR", label="Durham County Council", description=None),
            EnumOption(
                key="local-authority:EAL", label="London Borough of Ealing", description=None
            ),
            EnumOption(
                key="local-authority:EAS", label="Eastbourne Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:EAT", label="Eastleigh Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:ECA",
                label="East Cambridgeshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:EDE", label="East Devon District Council", description=None
            ),
            EnumOption(key="local-authority:EDN", label="Eden District Council", description=None),
            EnumOption(
                key="local-authority:EDO", label="East Dorset District Council", description=None
            ),
            EnumOption(
                key="local-authority:EHA", label="East Hampshire District Council", description=None
            ),
            EnumOption(
                key="local-authority:EHE",
                label="East Hertfordshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:ELI", label="East Lindsey District Council", description=None
            ),
            EnumOption(
                key="local-authority:ELM", label="Elmbridge Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:ENF", label="London Borough of Enfield", description=None
            ),
            EnumOption(
                key="local-authority:ENO", label="East Northamptonshire Council", description=None
            ),
            EnumOption(
                key="local-authority:EPP", label="Epping Forest District Council", description=None
            ),
            EnumOption(
                key="local-authority:EPS", label="Epsom and Ewell Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:ERE", label="Erewash Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:ERY",
                label="East Riding of Yorkshire Council",
                description=None,
            ),
            EnumOption(key="local-authority:ESK", label="East Suffolk Council", description=None),
            EnumOption(key="local-authority:ESS", label="Essex County Council", description=None),
            EnumOption(
                key="local-authority:EST",
                label="East Staffordshire Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:ESX", label="East Sussex County Council", description=None
            ),
            EnumOption(key="local-authority:EXE", label="Exeter City Council", description=None),
            EnumOption(
                key="local-authority:FAR", label="Fareham Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:FEN", label="Fenland District Council", description=None
            ),
            EnumOption(
                key="local-authority:FOE", label="Forest of Dean District Council", description=None
            ),
            EnumOption(
                key="local-authority:FOR", label="Forest Heath District Council", description=None
            ),
            EnumOption(key="local-authority:FYL", label="Fylde Borough Council", description=None),
            EnumOption(
                key="local-authority:GAT",
                label="Gateshead Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:GED", label="Gedling Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:GLA", label="Greater London Authority", description=None
            ),
            EnumOption(
                key="local-authority:GLO", label="Gloucester City Council", description=None
            ),
            EnumOption(
                key="local-authority:GLS", label="Gloucestershire County Council", description=None
            ),
            EnumOption(
                key="local-authority:GMCA",
                label="Greater Manchester Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:GOS", label="Gosport Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:GRA", label="Gravesham Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:GRE", label="Royal Borough of Greenwich", description=None
            ),
            EnumOption(
                key="local-authority:GRT", label="Guildford Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:GRY", label="Great Yarmouth Borough Council", description=None
            ),
            EnumOption(key="local-authority:HAA", label="Havant Borough Council", description=None),
            EnumOption(
                key="local-authority:HAE", label="Hambleton District Council", description=None
            ),
            EnumOption(
                key="local-authority:HAG", label="Harrogate Borough Council", description=None
            ),
            EnumOption(key="local-authority:HAL", label="Halton Borough Council", description=None),
            EnumOption(
                key="local-authority:HAM", label="Hampshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:HAO", label="Harborough District Council", description=None
            ),
            EnumOption(
                key="local-authority:HAR", label="Harlow District Council", description=None
            ),
            EnumOption(
                key="local-authority:HAS", label="Hastings Borough Council", description=None
            ),
            EnumOption(key="local-authority:HAT", label="Hart District Council", description=None),
            EnumOption(
                key="local-authority:HAV", label="London Borough of Havering", description=None
            ),
            EnumOption(
                key="local-authority:HCK", label="London Borough of Hackney", description=None
            ),
            EnumOption(key="local-authority:HEF", label="Herefordshire Council", description=None),
            EnumOption(
                key="local-authority:HER", label="Hertsmere Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:HIG", label="High Peak Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:HIL", label="London Borough of Hillingdon", description=None
            ),
            EnumOption(
                key="local-authority:HIN",
                label="Hinckley and Bosworth Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:HMF",
                label="London Borough of Hammersmith & Fulham",
                description=None,
            ),
            EnumOption(
                key="local-authority:HNS", label="London Borough of Hounslow", description=None
            ),
            EnumOption(
                key="local-authority:HOR", label="Horsham District Council", description=None
            ),
            EnumOption(
                key="local-authority:HPL", label="Hartlepool Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:HRT", label="Hertfordshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:HRW", label="London Borough of Harrow", description=None
            ),
            EnumOption(
                key="local-authority:HRY", label="London Borough of Haringey", description=None
            ),
            EnumOption(
                key="local-authority:HUN",
                label="Huntingdonshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:HYN", label="Hyndburn Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:IOS", label="Council of the Isles of Scilly", description=None
            ),
            EnumOption(key="local-authority:IOW", label="Isle of Wight Council", description=None),
            EnumOption(
                key="local-authority:IPS", label="Ipswich Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:ISL", label="London Borough of Islington", description=None
            ),
            EnumOption(
                key="local-authority:KEC",
                label="Royal Borough of Kensington and Chelsea",
                description=None,
            ),
            EnumOption(key="local-authority:KEN", label="Kent County Council", description=None),
            EnumOption(
                key="local-authority:KET", label="Kettering Borough Council", description=None
            ),
            EnumOption(key="local-authority:KHL", label="Hull City Council", description=None),
            EnumOption(
                key="local-authority:KIN",
                label="Borough Council of King's Lynn and West Norfolk",
                description=None,
            ),
            EnumOption(key="local-authority:KIR", label="Kirklees Council", description=None),
            EnumOption(
                key="local-authority:KTT",
                label="Royal Borough of Kingston upon Thames",
                description=None,
            ),
            EnumOption(
                key="local-authority:KWL",
                label="Knowsley Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(key="local-authority:LAC", label="Lancaster City Council", description=None),
            EnumOption(
                key="local-authority:LAN", label="Lancashire County Council", description=None
            ),
            EnumOption(
                key="local-authority:LBH", label="London Borough of Lambeth", description=None
            ),
            EnumOption(key="local-authority:LCE", label="Leicester City Council", description=None),
            EnumOption(key="local-authority:LCR", label="Liverpool City Region", description=None),
            EnumOption(key="local-authority:LDS", label="Leeds City Council", description=None),
            EnumOption(
                key="local-authority:LEC", label="Leicestershire County Council", description=None
            ),
            EnumOption(key="local-authority:LEE", label="Lewes District Council", description=None),
            EnumOption(
                key="local-authority:LEW", label="London Borough of Lewisham", description=None
            ),
            EnumOption(
                key="local-authority:LIC", label="City of Lincoln Council", description=None
            ),
            EnumOption(
                key="local-authority:LIF", label="Lichfield District Council", description=None
            ),
            EnumOption(
                key="local-authority:LIN", label="Lincolnshire County Council", description=None
            ),
            EnumOption(key="local-authority:LIV", label="Liverpool City Council", description=None),
            EnumOption(
                key="local-authority:LND", label="City of London Corporation", description=None
            ),
            EnumOption(key="local-authority:LUT", label="Luton Borough Council", description=None),
            EnumOption(
                key="local-authority:MAI", label="Maidstone Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:MAL", label="Maldon District Council", description=None
            ),
            EnumOption(
                key="local-authority:MAN", label="Manchester City Council", description=None
            ),
            EnumOption(
                key="local-authority:MAS", label="Mansfield District Council", description=None
            ),
            EnumOption(
                key="local-authority:MAV", label="Malvern Hills District Council", description=None
            ),
            EnumOption(
                key="local-authority:MDB", label="Middlesbrough Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:MDE", label="Mid Devon District Council", description=None
            ),
            EnumOption(key="local-authority:MDW", label="Medway Council", description=None),
            EnumOption(key="local-authority:MEL", label="Melton Borough Council", description=None),
            EnumOption(
                key="local-authority:MEN", label="Mendip District Council", description=None
            ),
            EnumOption(
                key="local-authority:MIK", label="Milton Keynes City Council", description=None
            ),
            EnumOption(
                key="local-authority:MOL", label="Mole Valley District Council", description=None
            ),
            EnumOption(
                key="local-authority:MRT", label="London Borough of Merton", description=None
            ),
            EnumOption(
                key="local-authority:MSS", label="Mid Sussex District Council", description=None
            ),
            EnumOption(
                key="local-authority:MSU", label="Mid Suffolk District Council", description=None
            ),
            EnumOption(
                key="local-authority:NBL", label="Northumberland County Council", description=None
            ),
            EnumOption(
                key="local-authority:NDE", label="North Devon District Council", description=None
            ),
            EnumOption(
                key="local-authority:NDO", label="North Dorset District Council", description=None
            ),
            EnumOption(
                key="local-authority:NEA",
                label="Newark and Sherwood District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:NEC",
                label="Newcastle-under-Lyme Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:NECA", label="North East Combined Authority", description=None
            ),
            EnumOption(
                key="local-authority:NED",
                label="North East Derbyshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:NEL", label="North East Lincolnshire Council", description=None
            ),
            EnumOption(key="local-authority:NET", label="Newcastle City Council", description=None),
            EnumOption(
                key="local-authority:NEW", label="New Forest District Council", description=None
            ),
            EnumOption(key="local-authority:NFK", label="Norfolk County Council", description=None),
            EnumOption(
                key="local-authority:NGM", label="Nottingham City Council", description=None
            ),
            EnumOption(
                key="local-authority:NHE",
                label="North Hertfordshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:NKE", label="North Kesteven District Council", description=None
            ),
            EnumOption(
                key="local-authority:NLN", label="North Lincolnshire Council", description=None
            ),
            EnumOption(
                key="local-authority:NNO", label="North Norfolk District Council", description=None
            ),
            EnumOption(
                key="local-authority:NOR", label="Northampton Borough Council", description=None
            ),
            EnumOption(key="local-authority:NOW", label="Norwich City Council", description=None),
            EnumOption(key="local-authority:NSM", label="North Somerset Council", description=None),
            EnumOption(
                key="local-authority:NTCA",
                label="North of Tyne Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:NTH", label="Northamptonshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:NTT", label="Nottinghamshire County Council", description=None
            ),
            EnumOption(key="local-authority:NTY", label="North Tyneside Council", description=None),
            EnumOption(
                key="local-authority:NUN",
                label="Nuneaton and Bedworth Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:NWA",
                label="North Warwickshire Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:NWL",
                label="North West Leicestershire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:NWM", label="London Borough of Newham", description=None
            ),
            EnumOption(
                key="local-authority:NYK", label="North Yorkshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:OAD",
                label="Oadby and Wigston Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:OLD",
                label="Oldham Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:OXF", label="Oxfordshire County Council", description=None
            ),
            EnumOption(key="local-authority:OXO", label="Oxford City Council", description=None),
            EnumOption(key="local-authority:PEN", label="Pendle Borough Council", description=None),
            EnumOption(key="local-authority:PLY", label="Plymouth City Council", description=None),
            EnumOption(key="local-authority:POL", label="Borough of Poole", description=None),
            EnumOption(
                key="local-authority:POR", label="Portsmouth City Council", description=None
            ),
            EnumOption(key="local-authority:PRE", label="Preston City Council", description=None),
            EnumOption(
                key="local-authority:PTE", label="Peterborough City Council", description=None
            ),
            EnumOption(
                key="local-authority:PUR", label="Purbeck District Council", description=None
            ),
            EnumOption(
                key="local-authority:RCC",
                label="Redcar and Cleveland Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:RCH",
                label="Rochdale Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:RDB", label="London Borough of Redbridge", description=None
            ),
            EnumOption(
                key="local-authority:RDG", label="Reading Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:RED", label="Redditch Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:REI",
                label="Reigate and Banstead Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:RIB", label="Ribble Valley Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:RIC",
                label="London Borough of Richmond upon Thames",
                description=None,
            ),
            EnumOption(
                key="local-authority:RIH", label="Richmondshire District Council", description=None
            ),
            EnumOption(
                key="local-authority:ROC", label="Rochford District Council", description=None
            ),
            EnumOption(
                key="local-authority:ROH", label="Rother District Council", description=None
            ),
            EnumOption(
                key="local-authority:ROS", label="Rossendale Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:ROT",
                label="Rotherham Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(key="local-authority:RUG", label="Rugby Borough Council", description=None),
            EnumOption(
                key="local-authority:RUH", label="Rushmoor Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:RUN", label="Runnymede Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:RUS", label="Rushcliffe Borough Council", description=None
            ),
            EnumOption(key="local-authority:RUT", label="Rutland County Council", description=None),
            EnumOption(
                key="local-authority:RYE", label="Ryedale District Council", description=None
            ),
            EnumOption(
                key="local-authority:SAL",
                label="St Albans City and District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SAW",
                label="Sandwell Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SBU", label="South Bucks District Council", description=None
            ),
            EnumOption(
                key="local-authority:SCA",
                label="South Cambridgeshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SCE", label="Scarborough Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:SYMCA",
                label="South Yorkshire Mayoral Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:SDE",
                label="South Derbyshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SED", label="St Edmundsbury Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:SEG", label="Sedgemoor District Council", description=None
            ),
            EnumOption(key="local-authority:SEL", label="Selby District Council", description=None),
            EnumOption(
                key="local-authority:SEV", label="Sevenoaks District Council", description=None
            ),
            EnumOption(key="local-authority:SFK", label="Suffolk County Council", description=None),
            EnumOption(
                key="local-authority:SFT",
                label="Sefton Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SGC", label="South Gloucestershire Council", description=None
            ),
            EnumOption(
                key="local-authority:SHA", label="South Hams District Council", description=None
            ),
            EnumOption(
                key="local-authority:SHE", label="Folkestone and Hythe Council", description=None
            ),
            EnumOption(key="local-authority:SHF", label="Sheffield City Council", description=None),
            EnumOption(key="local-authority:SHN", label="St Helens Council", description=None),
            EnumOption(
                key="local-authority:SHO", label="South Holland District Council", description=None
            ),
            EnumOption(key="local-authority:SHR", label="Shropshire Council", description=None),
            EnumOption(
                key="local-authority:SKE", label="South Kesteven District Council", description=None
            ),
            EnumOption(
                key="local-authority:SKP",
                label="Stockport Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SLA", label="South Lakeland District Council", description=None
            ),
            EnumOption(key="local-authority:SLF", label="Salford City Council", description=None),
            EnumOption(key="local-authority:SLG", label="Slough Borough Council", description=None),
            EnumOption(
                key="local-authority:SND", label="Sunderland City Council", description=None
            ),
            EnumOption(
                key="local-authority:SNO", label="South Norfolk District Council", description=None
            ),
            EnumOption(
                key="local-authority:SNR", label="South Northamptonshire Council", description=None
            ),
            EnumOption(
                key="local-authority:SOL",
                label="Solihull Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SOM", label="Somerset County Council", description=None
            ),
            EnumOption(
                key="local-authority:SOS", label="Southend-on-Sea Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:SOX",
                label="South Oxfordshire District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SPE", label="Spelthorne Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:SRI", label="South Ribble Borough Council", description=None
            ),
            EnumOption(key="local-authority:SRY", label="Surrey County Council", description=None),
            EnumOption(
                key="local-authority:SSO", label="South Somerset District Council", description=None
            ),
            EnumOption(
                key="local-authority:SST", label="South Staffordshire Council", description=None
            ),
            EnumOption(
                key="local-authority:STA", label="Stafford Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:STE", label="Stoke-on-Trent City Council", description=None
            ),
            EnumOption(
                key="local-authority:STF",
                label="Staffordshire Moorlands District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:STH", label="Southampton City Council", description=None
            ),
            EnumOption(
                key="local-authority:STN", label="London Borough of Sutton", description=None
            ),
            EnumOption(
                key="local-authority:STO", label="Stroud District Council", description=None
            ),
            EnumOption(
                key="local-authority:STR",
                label="Stratford-on-Avon District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:STS", label="Staffordshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:STT",
                label="Stockton-on-Tees Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:STV", label="Stevenage Borough Council", description=None
            ),
            EnumOption(key="local-authority:STY", label="South Tyneside Council", description=None),
            EnumOption(
                key="local-authority:SUF",
                label="Suffolk Coastal District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:SUR", label="Surrey Heath Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:SWD", label="Swindon Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:SWK", label="London Borough of Southwark", description=None
            ),
            EnumOption(key="local-authority:SWL", label="Swale Borough Council", description=None),
            EnumOption(
                key="local-authority:SWT",
                label="Somerset West and Taunton Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:TAM",
                label="Tameside Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:TAN", label="Tandridge District Council", description=None
            ),
            EnumOption(
                key="local-authority:TAU", label="Taunton Deane Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:TAW", label="Tamworth Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:TEI", label="Teignbridge District Council", description=None
            ),
            EnumOption(
                key="local-authority:TEN", label="Tendring District Council", description=None
            ),
            EnumOption(
                key="local-authority:TES", label="Test Valley Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:TEW", label="Tewkesbury Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:TFW", label="Telford & Wrekin Council", description=None
            ),
            EnumOption(
                key="local-authority:THA", label="Thanet District Council", description=None
            ),
            EnumOption(
                key="local-authority:THE", label="Three Rivers District Council", description=None
            ),
            EnumOption(key="local-authority:THR", label="Thurrock Council", description=None),
            EnumOption(key="local-authority:TOB", label="Torbay Council", description=None),
            EnumOption(
                key="local-authority:TON",
                label="Tonbridge and Malling Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:TOR", label="Torridge District Council", description=None
            ),
            EnumOption(
                key="local-authority:TRF",
                label="Trafford Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:TUN", label="Tunbridge Wells Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:TVCA", label="Tees Valley Combined Authority", description=None
            ),
            EnumOption(
                key="local-authority:TWH", label="London Borough of Tower Hamlets", description=None
            ),
            EnumOption(
                key="local-authority:UTT", label="Uttlesford District Council", description=None
            ),
            EnumOption(
                key="local-authority:VAL",
                label="Vale of White Horse District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:WAE", label="Waverley Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WAR", label="Warwickshire County Council", description=None
            ),
            EnumOption(
                key="local-authority:WAT", label="Watford Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WAV", label="Waveney District Council", description=None
            ),
            EnumOption(
                key="local-authority:WAW", label="Warwick District Council", description=None
            ),
            EnumOption(key="local-authority:WBK", label="West Berkshire Council", description=None),
            EnumOption(
                key="local-authority:WDE", label="West Devon Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WDO", label="West Dorset District Council", description=None
            ),
            EnumOption(
                key="local-authority:WEA", label="Wealden District Council", description=None
            ),
            EnumOption(
                key="local-authority:WECA",
                label="West of England Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:WEL", label="Wellingborough Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WEW", label="Welwyn Hatfield Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WEY",
                label="Weymouth and Portland Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:WFT",
                label="London Borough of Waltham Forest",
                description=None,
            ),
            EnumOption(
                key="local-authority:WGN",
                label="Wigan Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(key="local-authority:WIL", label="Wiltshire Council", description=None),
            EnumOption(
                key="local-authority:WIN", label="Winchester City Council", description=None
            ),
            EnumOption(
                key="local-authority:WKF",
                label="Wakefield Metropolitan District Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:WLA", label="West Lancashire Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WLI", label="West Lindsey District Council", description=None
            ),
            EnumOption(
                key="local-authority:WLL",
                label="Walsall Metropolitan Borough Council",
                description=None,
            ),
            EnumOption(
                key="local-authority:WLV", label="City of Wolverhampton Council", description=None
            ),
            EnumOption(
                key="local-authority:WMCA",
                label="West Midlands Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:WND", label="London Borough of Wandsworth", description=None
            ),
            EnumOption(
                key="local-authority:WNM",
                label="Royal Borough of Windsor and Maidenhead",
                description=None,
            ),
            EnumOption(key="local-authority:WOC", label="Worcester City Council", description=None),
            EnumOption(key="local-authority:WOI", label="Woking Borough Council", description=None),
            EnumOption(
                key="local-authority:WOK", label="Wokingham Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WOR", label="Worcestershire County Council", description=None
            ),
            EnumOption(
                key="local-authority:WOT", label="Worthing Borough Council", description=None
            ),
            EnumOption(
                key="local-authority:WOX",
                label="West Oxfordshire District Council",
                description=None,
            ),
            EnumOption(key="local-authority:WRL", label="Wirral Borough Council", description=None),
            EnumOption(
                key="local-authority:WRT", label="Warrington Borough Council", description=None
            ),
            EnumOption(key="local-authority:WSK", label="West Suffolk Council", description=None),
            EnumOption(key="local-authority:WSM", label="City of Westminster", description=None),
            EnumOption(
                key="local-authority:WSO", label="West Somerset District Council", description=None
            ),
            EnumOption(
                key="local-authority:WSX", label="West Sussex County Council", description=None
            ),
            EnumOption(
                key="local-authority:WYC", label="Wychavon District Council", description=None
            ),
            EnumOption(
                key="local-authority:WYCA",
                label="West Yorkshire Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:WYE", label="Wyre Forest District Council", description=None
            ),
            EnumOption(
                key="local-authority:WYO", label="Wycombe District Council", description=None
            ),
            EnumOption(key="local-authority:WYR", label="Wyre Borough Council", description=None),
            EnumOption(key="local-authority:YOR", label="City of York Council", description=None),
            EnumOption(key="local-authority:CUA", label="Cumberland Council", description=None),
            EnumOption(
                key="local-authority:WFUA",
                label="Westmorland and Furness Council",
                description=None,
            ),
            EnumOption(key="local-authority:SUA", label="Somerset Council", description=None),
            EnumOption(
                key="local-authority:NYUA", label="North Yorkshire Council", description=None
            ),
            EnumOption(
                key="local-authority:YNYCA",
                label="York and North Yorkshire Combined Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:NNECA", label="North East Combined Authority", description=None
            ),
            EnumOption(
                key="local-authority:EMCCA",
                label="East Midlands Combined County Authority",
                description=None,
            ),
            EnumOption(
                key="local-authority:NNUA", label="North Northamptonshire Council", description=None
            ),
            EnumOption(
                key="local-authority:WNUA", label="West Northamptonshire Council", description=None
            ),
            EnumOption(
                key="national-park-authority:Q20198711",
                label="South Downs National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q27159704",
                label="Lake District National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q27178932",
                label="Yorkshire Dales National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q4972284", label="Broads Authority", description=None
            ),
            EnumOption(
                key="national-park-authority:Q5225646",
                label="Dartmoor National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q72617158",
                label="New Forest National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q72617669",
                label="North York Moors National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q72617784",
                label="Exmoor National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q72617890",
                label="Northumberland National Park Authority",
                description=None,
            ),
            EnumOption(
                key="national-park-authority:Q72617988",
                label="Peak District National Park Authority",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q20648596",
                label="Old Oak and Park Royal Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q4916714",
                label="Birmingham Heartlands Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q6670544",
                label="London Legacy Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q6670837",
                label="London Thames Gateway Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q72456968",
                label="South Tees Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q72463795",
                label="Ebbsfleet Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q7799380",
                label="Thurrock Thames Gateway Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q7860503",
                label="Tyne and Wear Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q7986087",
                label="West Northamptonshire Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q105544651",
                label="Aycliffe and Peterlee Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q105544654",
                label="Basildon Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q5061392",
                label="Central Manchester Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q3258953",
                label="London Docklands Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q105544669",
                label="Telford Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q7694573",
                label="Teesside Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q117149370",
                label="Middlesbrough Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q124604981",
                label="Hartlepool Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q6515953",
                label="Leeds Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q4968888",
                label="Bristol Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q5182976",
                label="Crawley Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q115585981",
                label="Stockport Town Centre West Mayoral Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q3920908",
                label="Merseyside Development Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q6861239",
                label="Milton Keynes Development Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q7177999",
                label="Peterborough Development Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q7205796",
                label="Plymouth Development Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q7832579",
                label="Trafford Park Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:stockport-town-centre-MDC",
                label="Stockport Town Centre Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:northern-gateway-MDC",
                label="Northern Gateway Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:old-trafford-MDC",
                label="Old Trafford Development Corporation",
                description=None,
            ),
            EnumOption(
                key="development-corporation:Q137717415",
                label="Oxford Street Development Corporation",
                description=None,
            ),
        ],
    )
    submitted_at = StringField(
        display="Submitted at",
        description="The date and time the application was submitted",
        max_length=None,
    )
    created_at = StringField(
        display="Created at",
        description="The date and time the submission payload was created",
        max_length=None,
    )

    documents = SchemaNodeField(
        display="Document",
        description="Structure for submitted documents including reference, metadata, and file information ",
        schema_node_cls=Documents,
    )
    fee = SchemaNodeField(
        display="Fee",
        description="Structure for application fees including amounts due, amounts paid, and transaction references ",
        schema_node_cls=Fee,
    )


class AccessRightsOfWay(SchemaNode):
    _ref = "access-rights-of-way"
    _display = "Access and rights of way"
    _description = "Details of any changes the proposed development would make to existing access arrangements or public rights of way"

    new_altered_vehicle = EnumField(
        display="New or altered vehicle access",
        description="Is a new or altered vehicle access proposed to/from the public highway",
        select_options=[
            EnumOption(key="true", label="True", description="The statement is true"),
            EnumOption(key="false", label="False", description="The statement is false"),
            EnumOption(key="unknown", label="Unknown", description="The answer is unknown"),
        ],
    )
    new_altered_pedestrian = EnumField(
        display="New or altered pedestrian access",
        description="Is a new or altered pedestrian access proposed to/from the public highway",
        select_options=[
            EnumOption(key="true", label="True", description="The statement is true"),
            EnumOption(key="false", label="False", description="The statement is false"),
            EnumOption(key="unknown", label="Unknown", description="The answer is unknown"),
        ],
    )
    change_right_of_way = EnumField(
        display="Change to right of way",
        description="Will the proposal change public rights of way (diversion/extinguishment/creation)",
        select_options=[
            EnumOption(key="true", label="True", description="The statement is true"),
            EnumOption(key="false", label="False", description="The statement is false"),
            EnumOption(key="unknown", label="Unknown", description="The answer is unknown"),
        ],
    )
    new_right_of_way = EnumField(
        display="New right of way",
        description="Will new public rights of way be provided within or adjacent to the site",
        select_options=[
            EnumOption(key="true", label="True", description="The statement is true"),
            EnumOption(key="false", label="False", description="The statement is false"),
            EnumOption(key="unknown", label="Unknown", description="The answer is unknown"),
        ],
    )
    new_public_road = EnumField(
        display="New public road",
        description="Will new public roads be provided within the site",
        select_options=[
            EnumOption(key="true", label="True", description="The statement is true"),
            EnumOption(key="false", label="False", description="The statement is false"),
            EnumOption(key="unknown", label="Unknown", description="The answer is unknown"),
        ],
    )
    temp_right_of_way = EnumField(
        display="Temporary right of way changes",
        description="Are temporary changes to rights of way needed while the site is worked",
        select_options=[
            EnumOption(key="true", label="True", description="The statement is true"),
            EnumOption(key="false", label="False", description="The statement is false"),
            EnumOption(key="unknown", label="Unknown", description="The answer is unknown"),
        ],
    )
    future_new_right_of_way = EnumField(
        display="Future new right of way",
        description="Will new public rights of way be provided after extraction?",
        select_options=[
            EnumOption(key="true", label="True", description="The statement is true"),
            EnumOption(key="false", label="False", description="The statement is false"),
            EnumOption(key="unknown", label="Unknown", description="The answer is unknown"),
        ],
    )

    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class BioGeoArchCon(SchemaNode):
    _ref = "bio-geo-arch-con"
    _display = "Biodiversity, geological and archaeological conservation"
    _description = "Details of potential impacts to the biodiversity of the site, or any noteable archaeological or geological features."

    protected_species_impact = EnumField(
        display="Protected species impact",
        description="Where is there a likelihood of protected and priority species being affected?",
        select_options=[
            EnumOption(key="on-development-site", label="On development site", description=""),
            EnumOption(key="adjacent-to-site", label="On adjacent site", description=""),
        ],
    )
    biodiversity_features_impact = EnumField(
        display="Biodiversity features impact",
        description="Where is there a likelihood of important habitats or biodiversity features being affected?",
        select_options=[
            EnumOption(key="on-development-site", label="On development site", description=""),
            EnumOption(key="adjacent-to-site", label="On adjacent site", description=""),
        ],
    )
    geological_features_impact = EnumField(
        display="Geological features impact",
        description="Where is there a likelihood of features of geological conservation importance being affected?",
        select_options=[
            EnumOption(key="on-development-site", label="On development site", description=""),
            EnumOption(key="adjacent-to-site", label="On adjacent site", description=""),
        ],
    )
    archaeological_features_impact = EnumField(
        display="Archaeological features impact",
        description="Where is there a likelihood of features of archaeological conservation importance being affected?",
        select_options=[
            EnumOption(key="on-development-site", label="On development site", description=""),
            EnumOption(key="adjacent-to-site", label="On adjacent site", description=""),
        ],
    )


class FoulSewage(SchemaNode):
    _ref = "foul-sewage"
    _display = "Foul sewage disposal"
    _description = "How waste water will leave the property as part of the proposed development"

    has_new_disposal_arrangements = BooleanField(
        display="Has new disposal arrangements",
        description="Does the proposal include any new foul sewage disposal arrangments",
    )
    foul_sewage_disposal_types = EnumField(
        display="Foul sewage disposal types",
        description="List of ways foul sewage will be disposed of",
        select_options=[
            EnumOption(key="mains-sewer", label="Mains sewer", description=""),
            EnumOption(key="cess-pit", label="Cess pit", description=""),
            EnumOption(key="septic-tank", label="Septic tank", description=""),
            EnumOption(key="package-treatment", label="Package treatment plant", description=""),
            EnumOption(key="other", label="Other", description=""),
        ],
    )
    produce_foul_sewage = BooleanField(
        display="Produce foul sewage",
        description="Whether the proposed development will produce any foul sewage",
    )
    connect_to_drainage_system = BooleanField(
        display="Connect to drainage system",
        description="Whether the proposal needs to connect to the existing drainage system",
    )
    connect_to_drainage_system_oil_gas = EnumField(
        display="Connect to drainage system (oil and gas)",
        description="Whether the proposal needs to connect to the existing drainage system (oil and gas applications)",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response  "),
            EnumOption(
                key="unknown",
                label="Unknown",
                description="Status is not known or cannot be determined",
            ),
        ],
    )

    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class SubstanceTypes(SchemaNode):
    _ref = "substance-types"
    _display = "Hazardous substance"
    _description = "Information about a specific hazardous substance including its type, name (if other), and quantity in tonnes "

    hazardous_substance_type = EnumField(
        display="Hazardous substance type",
        description="Reference of hazardous substance type from predefined list",
        select_options=[
            EnumOption(key="acrylonitrile", label="Acrylonitrile", description=""),
            EnumOption(key="ammonia", label="Ammonia", description=""),
            EnumOption(key="bromine", label="Bromine", description=""),
            EnumOption(key="chlorine", label="Chlorine", description=""),
            EnumOption(key="ethylene-oxide", label="Ethylene oxide", description=""),
            EnumOption(key="flour", label="Flour", description=""),
            EnumOption(key="hydrogen-cyanide", label="Hydrogen cyanide", description=""),
            EnumOption(key="liquid-oxygen", label="Liquid oxygen", description=""),
            EnumOption(key="liquid-petroleum-gas", label="Liquid petroleum gas", description=""),
            EnumOption(key="phosgene", label="Phosgene", description=""),
            EnumOption(key="refined-white-sugar", label="Refined white sugar", description=""),
            EnumOption(key="sulphur-dioxide", label="Sulphur dioxide", description=""),
        ],
    )
    hazardous_substance_other = StringField(
        display="Hazardous substance other",
        description="The specific name of the hazardous substance if other is selected",
        max_length=None,
    )
    amount = StringField(
        display="Amount",
        description="The total amount due for the application fee",
        max_length=None,
    )


class HazSubstances(SchemaNode):
    _ref = "haz-substances"
    _display = "Hazardous substances"
    _description = (
        "Details of hazardous substances requiring consent used as part of the development"
    )

    involves_hazardous_substances = EnumField(
        display="Involves hazardous substances",
        description="Indicates if hazardous substances are involved in the proposal",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response"),
            EnumOption(
                key="not-applicable",
                label="Not Applicable",
                description="Response not applicable or not provided",
            ),
        ],
    )
    hazardous_sub_consent_req = BooleanField(
        display="Hazardous substance consent required",
        description="Does the proposal involve the use or storage of any substances requiring hazardous substances consent",
    )
    hazardous_sub_consent_details = StringField(
        display="Hazardous substance consent details",
        description="Details of hazardous substance consent requirements",
        max_length=None,
    )

    substance_types = SchemaNodeField(
        display="Hazardous substance",
        description="Information about a specific hazardous substance including its type, name (if other), and quantity in tonnes ",
        schema_node_cls=SubstanceTypes,
    )


class BuildingElements(SchemaNode):
    _ref = "building-elements"
    _display = "Building element"
    _description = "Describes the materials used for a specific part of a building, such as walls, roof, windows or doors "

    building_element_type = EnumField(
        display="Building element type",
        description="The part of building the materials relate to, such as walls, roofs, windows, or doors",
        select_options=[
            EnumOption(
                key="walls",
                label="Walls",
                description="A vertical construction that bounds or subdivides spaces",
            ),
            EnumOption(
                key="roof",
                label="Roof",
                description="A covering of the top part of a building, it protects the building against the effects of weather",
            ),
            EnumOption(key="windows", label="Windows", description=""),
            EnumOption(key="doors", label="Doors", description=""),
            EnumOption(key="boundary-treatments", label="Boundary treatments", description=""),
            EnumOption(
                key="vehicle-access-hard-standings",
                label="Vehicle access and hard-standings",
                description="",
            ),
            EnumOption(key="lighting", label="Lighting", description=""),
            EnumOption(key="external-walls", label="External walls", description=""),
            EnumOption(key="roof-covering", label="Roof covering", description=""),
            EnumOption(key="chimney", label="Chimney", description=""),
            EnumOption(key="external-doors", label="External doors", description=""),
            EnumOption(key="ceilings", label="Ceilings", description=""),
            EnumOption(key="internal-walls", label="Internal walls", description=""),
            EnumOption(key="floors", label="Floors", description=""),
            EnumOption(key="internal-doors", label="Internal doors", description=""),
            EnumOption(key="rainwater-goods", label="Rainwater goods", description=""),
            EnumOption(key="other", label="Other", description=""),
        ],
    )
    existing_materials = StringField(
        display="Existing materials",
        description="Description of the materials currently used for this building element",
        max_length=None,
    )
    proposed_materials = StringField(
        display="Proposed materials",
        description="Description of the materials proposed for this building element as part of the development",
        max_length=None,
    )
    materials_not_known = BooleanField(
        display="Materials not known",
        description="Indicates the materials for this building element are not yet known",
    )


class Materials(SchemaNode):
    _ref = "materials"
    _display = "Materials"
    _description = "What materials are being used for the proposed development"

    proposal_material_details = BooleanField(
        display="Proposal material details",
        description="Whether the proposal involves material details that need to be provided",
    )
    providing_additional_material_information = BooleanField(
        display="Providing additional material information",
        description="Is the applicant providing additional materials information on submitted plan(s)/drawing(s)/design and access statement?",
    )

    building_elements = SchemaNodeField(
        display="Building element",
        description="Describes the materials used for a specific part of a building, such as walls, roof, windows or doors ",
        schema_node_cls=BuildingElements,
    )
    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class TradeEffluent(SchemaNode):
    _ref = "trade-effluent"
    _display = "Trade effluent"
    _description = "Details of any liquid waste produced by industial processes on the proposed site, and how it will be diposed of."

    is_disposal_required = BooleanField(
        display="Disposal required",
        description="Does the proposal involve the disposal of trade effluents or waste (true/false)",
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )


class FallingTreesDocument(SchemaNode):
    _ref = "falling-trees-document"
    _display = "Supporting document"
    _description = "Reference to a supporting document already listed in application.documents "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    details = StringField(
        display="Details",
        description="Additional details or information about an item",
        max_length=None,
    )


class TreeRemovalPlan(SchemaNode):
    _ref = "tree-removal-plan"
    _display = "Supporting document"
    _description = "Reference to a supporting document already listed in application.documents "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    details = StringField(
        display="Details",
        description="Additional details or information about an item",
        max_length=None,
    )


class TreesHedges(SchemaNode):
    _ref = "trees-hedges"
    _display = "Trees and hedges information"
    _description = (
        "Details of trees and/or hedges that will be affected by the proposed development"
    )

    trees_on_site = BooleanField(
        display="Trees on site",
        description="Whether trees or hedges are present on the proposed development site",
    )
    trees_on_adj_land = BooleanField(
        display="Trees on adjacent land",
        description="Whether trees or hedges on land adjacent to the proposed development site could influence the development or might be important as part of the local landscape character",
    )
    has_falling_trees_risk = BooleanField(
        display="Falling trees risk",
        description="Whether there are falling trees on-premises or adjacent premises that are a risk to the development",
    )
    tree_removal = BooleanField(
        display="Tree removal", description="Whether trees or hedges need to be pruned or removed"
    )

    falling_trees_document = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=FallingTreesDocument,
    )
    tree_removal_plan = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=TreeRemovalPlan,
    )


class ParkingSpaces(SchemaNode):
    _ref = "parking-spaces"
    _display = "Parking space"
    _description = "Information about parking spaces by vehicle type, including existing and proposed counts with net change calculations "

    parking_space_type = EnumField(
        display="Parking space type",
        description="Type of parking space or vehicle type",
        select_options=[
            EnumOption(
                key="car-space",
                label="Cars",
                description="Standard on-site parking spaces for cars.",
            ),
            EnumOption(
                key="light-goods-vehicle-space",
                label="Light Goods/Public Carrier Vehicles",
                description="Vans, delivery vehicles, and public carriers.",
            ),
            EnumOption(
                key="motorcycle-space",
                label="Motorcycles",
                description="Spaces designated for motorbikes.",
            ),
            EnumOption(
                key="disability-space",
                label="Disability Space",
                description="Accessible parking spaces.",
            ),
            EnumOption(
                key="cycle-space",
                label="Cycle Space",
                description="Bicycle parking, including racks or shelters.",
            ),
            EnumOption(
                key="blue-badge-space",
                label="Blue Badge Spaces",
                description="Parking spaces reserved for blue badge holders.",
            ),
            EnumOption(key="bus", label="Bus", description="Parking bays or laybys for buses."),
            EnumOption(
                key="car-club",
                label="Car Club",
                description="Parking spaces allocated for car club vehicles.",
            ),
            EnumOption(
                key="resi-off-street",
                label="Resi Only Off Street Parking",
                description="Private off-street parking for residents only.",
            ),
            EnumOption(
                key="other",
                label="Other",
                description="Other parking types not covered by the defined categories.",
            ),
        ],
    )
    vehicle_type_other = StringField(
        display="Vehicle type other",
        description="Vehicle type when parking space type is 'other'",
        max_length=None,
    )
    total_existing = StringField(
        display="Total existing",
        description="Total number of existing parking spaces",
        max_length=None,
    )
    total_proposed = StringField(
        display="Total proposed",
        description="Total number of proposed parking spaces",
        max_length=None,
    )
    unknown_proposed = BooleanField(
        display="Unknown proposed", description="If proposed parking spaces is unknown"
    )
    difference_in_spaces = StringField(
        display="Difference in spaces",
        description="Net change in parking spaces (proposed minus existing)",
        max_length=None,
    )


class VehicleParking(SchemaNode):
    _ref = "vehicle-parking"
    _display = "Vehicle parking"
    _description = "Details of current parking facilities at the site and any changes that would be made by the proposed development."

    parking_spaces = SchemaNodeField(
        display="Parking space",
        description="Information about parking spaces by vehicle type, including existing and proposed counts with net change calculations ",
        schema_node_cls=ParkingSpaces,
    )


class WasteStorageCollection(SchemaNode):
    _ref = "waste-storage-collection"
    _display = "Waste storage and collection"
    _description = (
        "Any waste storage or recycling arrangements are in place, such as waste storage areas"
    )

    needs_waste_storage_area = BooleanField(
        display="Needs waste storage area",
        description="Does the proposal require a waste storage area",
    )
    needs_waste_storage_area_outline = EnumField(
        display="Needs waste storage area",
        description="Does the proposal require a waste storage area?",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response  "),
            EnumOption(
                key="unknown",
                label="Unknown",
                description="Status is not known or cannot be determined",
            ),
        ],
    )
    waste_storage_area_details = StringField(
        display="Waste storage area details",
        description="Details of the waste storage area including location, size, design and access arrangements",
        max_length=None,
    )
    separate_recycling_arrangements = BooleanField(
        display="Separate recycling arrangements",
        description="Does the proposal include separate recycling arrangements",
    )
    separate_recycling_arrangements_outline = EnumField(
        display="Separate recycling arrangements (outline)",
        description="Does the proposal include separate recycling arrangements?",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response  "),
            EnumOption(
                key="unknown",
                label="Unknown",
                description="Status is not known or cannot be determined",
            ),
        ],
    )
    separate_recycling_arrangements_details = StringField(
        display="Separate recycling arrangements details",
        description="Details of the recycling arrangements including types of materials, collection methods and storage facilities",
        max_length=None,
    )


class TechnicalDetailsConsent(SchemaNode):
    _ref = "technical-details-consent"
    _display = "Technical details consent"
    _description = "Technical Details Consent (TDC) is the second stage of the 'Permission in Principle' (PiP) process in planning, primarily for housing-led development. It follows the initial 'Permission in Principle' stage, which establishes whether a site is suitable in principle for development. TDC assesses the detailed design, layout, and other technical aspects of the proposed development. "

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    access_rights_of_way = SchemaNodeField(
        display="Access and rights of way",
        description="Details of any changes the proposed development would make to existing access arrangements or public rights of way",
        schema_node_cls=AccessRightsOfWay,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    bio_geo_arch_con = SchemaNodeField(
        display="Biodiversity, geological and archaeological conservation",
        description="Details of potential impacts to the biodiversity of the site, or any noteable archaeological or geological features.",
        schema_node_cls=BioGeoArchCon,
    )
    bng = SchemaNodeField(
        display="Biodiversity net gain",
        description="How any natural habitats on the development site will be improved by the proposed works.",
        schema_node_cls=Bng,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    employment = SchemaNodeField(
        display="Employment",
        description="How the proposed development will impact existing and proposed employee numbers",
        schema_node_cls=Employment,
    )
    existing_use = SchemaNodeField(
        display="Existing use",
        description="How the site is currently being used.",
        schema_node_cls=ExistingUse,
    )
    flood_risk_assessment = SchemaNodeField(
        display="Flood risk assessment",
        description="Results of any flood risk assessments made for the development site",
        schema_node_cls=FloodRiskAssessment,
    )
    foul_sewage = SchemaNodeField(
        display="Foul sewage disposal",
        description="How waste water will leave the property as part of the proposed development",
        schema_node_cls=FoulSewage,
    )
    haz_substances = SchemaNodeField(
        display="Hazardous substances",
        description="Details of hazardous substances requiring consent used as part of the development",
        schema_node_cls=HazSubstances,
    )
    hrs_operation = SchemaNodeField(
        display="Hours of operation",
        description="Proposed operating hours if the proposed development is intended for non-residential use.",
        schema_node_cls=HrsOperation,
    )
    materials = SchemaNodeField(
        display="Materials",
        description="What materials are being used for the proposed development",
        schema_node_cls=Materials,
    )
    non_res_floorspace = SchemaNodeField(
        display="Non residential floorspace",
        description="Details of changes to non-residential floorspace in the proposed development.",
        schema_node_cls=NonResFloorspace,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    processes_machinery_waste = SchemaNodeField(
        display="Processes machinery waste",
        description="How waste will be managed on the site ",
        schema_node_cls=ProcessesMachineryWaste,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    res_units = SchemaNodeField(
        display="Residential units",
        description="Details of the residential units that make up both the current and proposed development.",
        schema_node_cls=ResUnits,
    )
    site_area = SchemaNodeField(
        display="Site area",
        description="How big the site is including relevant measurements",
        schema_node_cls=SiteArea,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )
    trade_effluent = SchemaNodeField(
        display="Trade effluent",
        description="Details of any liquid waste produced by industial processes on the proposed site, and how it will be diposed of.",
        schema_node_cls=TradeEffluent,
    )
    trees_hedges = SchemaNodeField(
        display="Trees and hedges information",
        description="Details of trees and/or hedges that will be affected by the proposed development",
        schema_node_cls=TreesHedges,
    )
    vehicle_parking = SchemaNodeField(
        display="Vehicle parking",
        description="Details of current parking facilities at the site and any changes that would be made by the proposed development.",
        schema_node_cls=VehicleParking,
    )
    waste_storage_collection = SchemaNodeField(
        display="Waste storage and collection",
        description="Any waste storage or recycling arrangements are in place, such as waste storage areas",
        schema_node_cls=WasteStorageCollection,
    )


class CommunityConsultation(SchemaNode):
    _ref = "community-consultation"
    _display = "Community consultation"
    _description = (
        "What community consultation activities have taken place as part of the application"
    )

    have_consulted = BooleanField(
        display="Have consulted", description="Whether community consultation has been carried out"
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )


class Demolition(SchemaNode):
    _ref = "demolition"
    _display = "Demolition"
    _description = (
        "Details of any demolition that needs to take place as part of the development proposal."
    )

    is_proposing_demolition = BooleanField(
        display="Is propsing demolition",
        description="The proposal includes partial or total demolition of a listed building?",
    )
    is_total_demolition = BooleanField(
        display="Is total demolition",
        description="Indicating whether the proposal involves total demolition of a listed building",
    )
    is_demolishing_building_in_curtilage = BooleanField(
        display="Demolition building in curtilage",
        description="True or False indicating whether the proposal involves demolition of a building in the curtilage of a listed building",
    )
    is_partial_demolition = BooleanField(
        display="Demolition part",
        description="True or False indicating whether the proposal involves partial demolition of a listed building",
    )
    listed_building_volume = StringField(
        display="Listed building volume",
        description="Volume of listed building in cubic metres",
        max_length=None,
    )
    demolition_volume = StringField(
        display="Demolition volume",
        description="Volume of part to be demolished in cubic metres",
        max_length=None,
    )
    part_built_date = StringField(
        display="Part built date",
        description="The approximate date the part to be removed was built, in YYYY-MM format.",
        max_length=None,
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    reason = StringField(display="Reason", description="A textual reason", max_length=None)


class ImmunityFromListing(SchemaNode):
    _ref = "immunity-from-listing"
    _display = "Immunity from listing"
    _description = "Whether the applicant has obtained a Certificate of Immunity (COI) meaning the building in question cannot be listed"

    cert_of_immunity_sought = EnumField(
        display="Certificate of immunity sought",
        description="Has a certificate of immunity been sought",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response  "),
            EnumOption(
                key="unknown",
                label="Unknown",
                description="Status is not known or cannot be determined",
            ),
        ],
    )
    application_result = StringField(
        display="Application result",
        description="Provide the result of the application for a certificate of immunity",
        max_length=None,
    )


class DocumentReference(SchemaNode):
    _ref = "document-reference"
    _display = "Supporting document"
    _description = "Reference to a supporting document already listed in application.documents "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    details = StringField(
        display="Details",
        description="Additional details or information about an item",
        max_length=None,
    )


class LbAlter(SchemaNode):
    _ref = "lb-alter"
    _display = "Listed building alterations"
    _description = (
        "Details of any changes being made to a listed building as part of development works"
    )

    proposal_alter_lb = BooleanField(
        display="Proposal alter listed building",
        description="True or False if proposal includes alterations to a listed building",
    )
    proposal_alter_lb_types = EnumField(
        display="Proposal alteration types",
        description="Select from a list of listed building alteration types, select all that apply",
        select_options=[
            EnumOption(
                key="interior",
                label="Interior of building",
                description="Works to the interior of the building",
            ),
            EnumOption(
                key="exterior",
                label="Exterior of building",
                description="Works to the exterior of the building",
            ),
            EnumOption(
                key="fixed",
                label="Fixed structure or object",
                description="Works to any structure or object fixed to the property (or buildings with the curtilage) internally or externally",
            ),
            EnumOption(
                key="stripping",
                label="Stripping out",
                description="Stripping out of any internal wall, ceiling or floor finishes",
            ),
        ],
    )

    document_reference = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=DocumentReference,
    )


class LbGrade(SchemaNode):
    _ref = "lb-grade"
    _display = "Listed building grade"
    _description = "The grade of any listed building affected by the proposed development."

    listed_building_grade = StringField(
        display="Listed building grade",
        description='The grade of the listed building, selected from the listed-building-grade codelist or "don\'t know"',
        max_length=None,
    )
    listed_building = StringField(
        display="Listed building",
        description="Listed building reference for cross-referencing with listed building records",
        max_length=None,
    )
    provided_by = EnumField(
        display="Provided by",
        description="Whether the information was provided by the applicant or calculated by the system",
        select_options=[
            EnumOption(
                key="applicant",
                label="Applicant",
                description="Information provided by the applicant",
            ),
            EnumOption(
                key="system",
                label="System/Service",
                description="Information calculated or determined by the system or external service",
            ),
        ],
    )


class RelatedApplications(SchemaNode):
    _ref = "related-applications"
    _display = "Related application details"
    _description = "Details about a related application including its reference, description and decision date "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    decision_date = StringField(
        display="Decision date",
        description="The date when the decision was made, in YYYY-MM-DD format",
        max_length=None,
    )


class RelatedApplicationsmoduleresolved(SchemaNode):
    _ref = "related-applications"
    _display = "Related applications"
    _description = "Details of any other development proposals made for the site"

    has_related_applications = BooleanField(
        display="Has related applications",
        description="Are there any related applications, previous proposals or demolitions for the site",
    )

    related_applications = SchemaNodeField(
        display="Related application details",
        description="Details about a related application including its reference, description and decision date ",
        schema_node_cls=RelatedApplications,
    )


class Lbc(SchemaNode):
    _ref = "lbc"
    _display = "Listed building consent"
    _description = "An application for works for the demolition of a listed building or for its alteration or extension in any manner which would affect its character as a building of special architectural or historic interest"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    community_consultation = SchemaNodeField(
        display="Community consultation",
        description="What community consultation activities have taken place as part of the application",
        schema_node_cls=CommunityConsultation,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    demolition = SchemaNodeField(
        display="Demolition",
        description="Details of any demolition that needs to take place as part of the development proposal.",
        schema_node_cls=Demolition,
    )
    immunity_from_listing = SchemaNodeField(
        display="Immunity from listing",
        description="Whether the applicant has obtained a Certificate of Immunity (COI) meaning the building in question cannot be listed",
        schema_node_cls=ImmunityFromListing,
    )
    lb_alter = SchemaNodeField(
        display="Listed building alterations",
        description="Details of any changes being made to a listed building as part of development works",
        schema_node_cls=LbAlter,
    )
    lb_grade = SchemaNodeField(
        display="Listed building grade",
        description="The grade of any listed building affected by the proposed development.",
        schema_node_cls=LbGrade,
    )
    materials = SchemaNodeField(
        display="Materials",
        description="What materials are being used for the proposed development",
        schema_node_cls=Materials,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    related_applications = SchemaNodeField(
        display="Related applications",
        description="Details of any other development proposals made for the site",
        schema_node_cls=RelatedApplicationsmoduleresolved,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class DescProposedWorksLbLdc(SchemaNode):
    _ref = "desc-proposed-works-lb-ldc"
    _display = "Description of proposed works for listed building lawful development certificate"
    _description = "Details of development plans for the work to the listed building an applicant is seeking a lawful development certificate for"

    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )


class GroundsForApplication(SchemaNode):
    _ref = "grounds-for-application"
    _display = "Grounds for application"
    _description = "Why a Certificate of Lawfulness of Propose Works is being requested."

    grounds_for_application = StringField(
        display="Grounds for application",
        description="Reason(s) why Certificate of Lawfulness of Proposed Works should be granted, including explanation of why listed building consent is not required ",
        max_length=None,
    )

    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class OwnerDetails(SchemaNode):
    _ref = "owner-details"
    _display = "LDC Owner Details"
    _description = "Details of property owners for Listed Building Consent applications including their personal information and whether they have been informed of the application "

    informed_of_application = BooleanField(
        display="Informed of application",
        description="Whether the person has been informed of the application",
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )


class InterestedPersons(SchemaNode):
    _ref = "interested-persons"
    _display = "LDC Interested Person"
    _description = "Details of persons with an interest in the property for Listed Building Consent applications including their personal information, nature of interest, and notification status "

    nature_of_interest = StringField(
        display="Nature of interest",
        description="Description of the nature of a person's interest in the property",
        max_length=None,
    )
    informed_of_application = BooleanField(
        display="Informed of application",
        description="Whether the person has been informed of the application",
    )
    reason_not_informed = StringField(
        display="Reason not informed",
        description="Reason why a person was not informed of the application",
        max_length=None,
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )


class InterestDetails(SchemaNode):
    _ref = "interest-details"
    _display = "Interest details"
    _description = (
        "Names and contact details for all parties with an interest in the proposed develpoment."
    )

    applicant_interest = StringField(
        display="Applicant interest",
        description="Description of the applicant's interest in the land",
        max_length=None,
    )

    owner_details = SchemaNodeField(
        display="LDC Owner Details",
        description="Details of property owners for Listed Building Consent applications including their personal information and whether they have been informed of the application ",
        schema_node_cls=OwnerDetails,
    )
    interested_persons = SchemaNodeField(
        display="LDC Interested Person",
        description="Details of persons with an interest in the property for Listed Building Consent applications including their personal information, nature of interest, and notification status ",
        schema_node_cls=InterestedPersons,
    )


class LdcProposedWorkLb(SchemaNode):
    _ref = "ldc-proposed-work-lb"
    _display = "LDC Proposed Work to a Listed Building"
    _description = "An application for a certificate confirming whether proposed works to a listed building would be lawful because they do not require listed building consent"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    desc_proposed_works_lb_ldc = SchemaNodeField(
        display="Description of proposed works for listed building lawful development certificate",
        description="Details of development plans for the work to the listed building an applicant is seeking a lawful development certificate for",
        schema_node_cls=DescProposedWorksLbLdc,
    )
    grounds_for_application = SchemaNodeField(
        display="Grounds for application",
        description="Why a Certificate of Lawfulness of Propose Works is being requested.",
        schema_node_cls=GroundsForApplication,
    )
    interest_details = SchemaNodeField(
        display="Interest details",
        description="Names and contact details for all parties with an interest in the proposed develpoment.",
        schema_node_cls=InterestDetails,
    )
    lb_grade = SchemaNodeField(
        display="Listed building grade",
        description="The grade of any listed building affected by the proposed development.",
        schema_node_cls=LbGrade,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class HedgerowRemoval(SchemaNode):
    _ref = "hedgerow-removal"
    _display = "Hedgerow removal notice"
    _description = "Details of any hedgerows being removed as part of the development"

    reason = StringField(display="Reason", description="A textual reason", max_length=None)
    hedgerow_length = StringField(
        display="Hedgerow length",
        description="Total length, in metres, of hedgerow proposed for removal",
        max_length=None,
    )
    hedgerow_less_than_30_years = BooleanField(
        display="Hedgerow less than 30 years", description="Is the hedgerow less than 30 years old?"
    )
    planting_evidence_attached = BooleanField(
        display="Planting evidence attached",
        description="Is evidence of the date of planting attached?",
    )
    interest_declaration = EnumField(
        display="Interest declaration",
        description="The applicant's interest or ownership in the hedgerow",
        select_options=[
            EnumOption(
                key="owner",
                label="Owner",
                description="The applicant is the freehold owner of the land concerned",
            ),
            EnumOption(
                key="agricultural-tenant",
                label="Agricultural tenant",
                description="The applicant is the tenant of the agricultural holding concerned",
            ),
            EnumOption(
                key="farm-business-tenant",
                label="Farm business tenant",
                description="The applicant is the tenant under the farm business tenancy concerned",
            ),
            EnumOption(
                key="utility-operator",
                label="Utility operator",
                description="The applicant is acting for the utility operator concerned",
            ),
        ],
    )

    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class HedgerowRemovalapplicationresolved(SchemaNode):
    _ref = "hedgerow-removal"
    _display = "Hedgerow removal notice"
    _description = "An application for anyone proposing to remove a hedgerow, or part of a hedgerow"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    hedgerow_removal = SchemaNodeField(
        display="Hedgerow removal notice",
        description="Details of any hedgerows being removed as part of the development",
        schema_node_cls=HedgerowRemoval,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class PriorApproval(SchemaNode):
    _ref = "prior-approval"
    _display = "Prior approval"
    _description = "This applies to developments with permitted development rights (where developments are granted planning permission by national legislation without the need to submit a planning application)"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )


class ProposalDetailsLdc(SchemaNode):
    _ref = "proposal-details-ldc"
    _display = "Proposal details LDC"
    _description = "Details of why a Lawful Development Certificate is required."

    proposal_incl_building_operations = BooleanField(
        display="Proposal incl building operations",
        description="Does the proposal include building operations?",
    )
    proposal_building_operations_description = StringField(
        display="Proposal building operations description",
        description="Description of the building operations included in the proposal",
        max_length=None,
    )
    proposal_incl_change_of_use = BooleanField(
        display="Proposal incl change of use",
        description="Does the proposal include a change of use?",
    )
    proposal_change_of_use_description = StringField(
        display="Proposal change of use description",
        description="Description of the change of use included in the proposal",
        max_length=None,
    )
    proposal_existing_use_description = StringField(
        display="Proposal existing use description",
        description="Description of the existing use before the proposed change of use",
        max_length=None,
    )
    proposal_existing_use_stop_date = StringField(
        display="Proposal existing use stop date",
        description="Date when the existing use stopped or will stop",
        max_length=None,
    )
    proposal_started = BooleanField(
        display="Proposal started", description="Has any work on the proposal already been started"
    )


class GroundsExistingUse(SchemaNode):
    _ref = "grounds-existing-use"
    _display = "Grounds for application (information about the existing use(s))"
    _description = "Supporting inforation for a Lawful Development Certificate application relating to how the site has most recently been used."

    reason = StringField(display="Reason", description="A textual reason", max_length=None)
    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    specified_use = StringField(
        display="Specified use",
        description="A specified use if no applicable use class is available",
        max_length=None,
    )

    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class GroundsProposedUse(SchemaNode):
    _ref = "grounds-proposed-use"
    _display = "Grounds for proposed use"
    _description = "What the new site will be used for"

    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    specified_use = StringField(
        display="Specified use",
        description="A specified use if no applicable use class is available",
        max_length=None,
    )
    operation_type = EnumField(
        display="Operation type",
        description="Whether the proposed use is temporary or permanent",
        select_options=[
            EnumOption(key="permanent", label="Permanent", description=""),
            EnumOption(key="temporary", label="Temporary", description=""),
        ],
    )
    temporary_details = StringField(
        display="Temporary details",
        description="Details of temporary use including duration and specific arrangements",
        max_length=None,
    )
    reason = StringField(display="Reason", description="A textual reason", max_length=None)


class LdcProspectiveUse(SchemaNode):
    _ref = "ldc-prospective-use"
    _display = "LDC Proposed Use"
    _description = "Prospective use of the site"

    proposal_details_ldc = SchemaNodeField(
        display="Proposal details LDC",
        description="Details of why a Lawful Development Certificate is required.",
        schema_node_cls=ProposalDetailsLdc,
    )
    grounds_existing_use = SchemaNodeField(
        display="Grounds for application (information about the existing use(s))",
        description="Supporting inforation for a Lawful Development Certificate application relating to how the site has most recently been used.",
        schema_node_cls=GroundsExistingUse,
    )
    grounds_proposed_use = SchemaNodeField(
        display="Grounds for proposed use",
        description="What the new site will be used for",
        schema_node_cls=GroundsProposedUse,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    interest_details = SchemaNodeField(
        display="Interest details",
        description="Names and contact details for all parties with an interest in the proposed develpoment.",
        schema_node_cls=InterestDetails,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class ReplacementDrawings(SchemaNode):
    _ref = "replacement-drawings"
    _display = "Replacement drawing"
    _description = "Details of an approved drawing being replaced by a new drawing, including references to both old and new drawings "

    old_drawing_reference = StringField(
        display="Old drawing reference",
        description="Reference of the old drawing being replaced",
        max_length=None,
    )
    new_drawing_reference = StringField(
        display="New drawing reference",
        description="Reference for the new drawing that replaces the old drawing",
        max_length=None,
    )
    reason = StringField(display="Reason", description="A textual reason", max_length=None)


class SupportingInfo(SchemaNode):
    _ref = "supporting-info"
    _display = "Supporting information"
    _description = "Any additional information which will help with the planning application"

    replacement_drawings = SchemaNodeField(
        display="Replacement drawing",
        description="Details of an approved drawing being replaced by a new drawing, including references to both old and new drawings ",
        schema_node_cls=ReplacementDrawings,
    )


class ReservedMatters(SchemaNode):
    _ref = "reserved-matters"
    _display = "Reserved matters"
    _description = "This application is only required when the applicant has already been granted outline planning permission. Reserved matters can include appearance, means of access, landscaping, layout and scale"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )
    supporting_info = SchemaNodeField(
        display="Supporting information",
        description="Any additional information which will help with the planning application",
        schema_node_cls=SupportingInfo,
    )


class DemolitionReason(SchemaNode):
    _ref = "demolition-reason"
    _display = "Demolition reason"
    _description = "Why demolition is necessary at the development site"

    reason = StringField(display="Reason", description="A textual reason", max_length=None)


class DemolitionConArea(SchemaNode):
    _ref = "demolition-con-area"
    _display = "Planning permission for relevant demolition in a conservation area"
    _description = "An application for planning permission involving the demolition of any unlisted building or structure in a conservation area if permission is required"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    bng = SchemaNodeField(
        display="Biodiversity net gain",
        description="How any natural habitats on the development site will be improved by the proposed works.",
        schema_node_cls=Bng,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    community_consultation = SchemaNodeField(
        display="Community consultation",
        description="What community consultation activities have taken place as part of the application",
        schema_node_cls=CommunityConsultation,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    demolition_reason = SchemaNodeField(
        display="Demolition reason",
        description="Why demolition is necessary at the development site",
        schema_node_cls=DemolitionReason,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    related_applications = SchemaNodeField(
        display="Related applications",
        description="Details of any other development proposals made for the site",
        schema_node_cls=RelatedApplicationsmoduleresolved,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class Tpo(SchemaNode):
    _ref = "tpo"
    _display = "Tree preservation order details"
    _description = "Details of any Tree Preservation Orders (TPO) affecting the development site"

    tpo_reference = StringField(
        display="TPO reference",
        description="Reference for a Tree Preservation Order covering affected trees",
        max_length=None,
    )
    tpo_provided_by = EnumField(
        display="TPO provided by",
        description="How was the list of TPO references generated - by the applicant or system/service",
        select_options=[
            EnumOption(
                key="applicant",
                label="Applicant",
                description="Information provided by the applicant",
            ),
            EnumOption(
                key="system",
                label="System/Service",
                description="Information calculated or determined by the system or external service",
            ),
        ],
    )


class TreeDetails(SchemaNode):
    _ref = "tree-details"
    _display = "Tree details"
    _description = "Detailed information about an individual tree including identification, species and proposed works "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    species = StringField(display="Species", description="The species of the tree", max_length=None)
    description_of_works = StringField(
        display="Description of works",
        description="Description of the nature of the work to be carried out on this tree",
        max_length=None,
    )
    reason = StringField(display="Reason", description="A textual reason", max_length=None)
    replanting_description = StringField(
        display="Replanting description",
        description="Details of replanting arrangements if applicable",
        max_length=None,
    )


class TreeWorkDetails(SchemaNode):
    _ref = "tree-work-details"
    _display = "Identification of tree(s) and description of works"
    _description = (
        "Details of trees affected by the proposed development and what work is being done to them."
    )

    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )

    tree_details = SchemaNodeField(
        display="Tree details",
        description="Detailed information about an individual tree including identification, species and proposed works ",
        schema_node_cls=TreeDetails,
    )


class TreesAdditional(SchemaNode):
    _ref = "trees-additional"
    _display = "Trees additional information"
    _description = "Further details of any issues relating to trees on the site"

    advice_from_authority = StringField(
        display="Advice from authority",
        description="Any advice provided on-site by a Local Planning Authority (LPA) officer",
        max_length=None,
    )
    condition_concerns = BooleanField(
        display="Condition concerns",
        description="Whether there are concerns the tree(s) are diseased or might break or fall",
    )
    causing_subsidence = BooleanField(
        display="Causing subsidence",
        description="Whether subsidence damage is being caused by the tree(s)",
    )
    causing_structural_damage = BooleanField(
        display="Causing structural damage",
        description="Whether structural damage is being caused by the tree(s)",
    )

    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class Owner(SchemaNode):
    _ref = "owner"
    _display = "Tree owner"
    _description = (
        "Details of a tree owner including their personal information and contact details "
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )
    contact_details = SchemaNodeField(
        display="Contact details",
        description="A substructure for recording contact details ",
        schema_node_cls=ContactDetails,
    )


class TreesOwnership(SchemaNode):
    _ref = "trees-ownership"
    _display = "Trees ownership"
    _description = "Who owns any trees affected by the proposed development."

    is_applicant_owner = BooleanField(
        display="Is applicant owner",
        description="Whether the applicant owns the trees affected by the proposed works",
    )

    owner = SchemaNodeField(
        display="Tree owner",
        description="Details of a tree owner including their personal information and contact details ",
        schema_node_cls=Owner,
    )


class ConsentUnderTpo(SchemaNode):
    _ref = "consent-under-tpo"
    _display = "Consent under TPO"
    _description = "An application that will affect a protected tree including those covered by a Tree Preservation Order (TPO) or those which grow in a conservation area"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    tpo = SchemaNodeField(
        display="Tree preservation order details",
        description="Details of any Tree Preservation Orders (TPO) affecting the development site",
        schema_node_cls=Tpo,
    )
    tree_work_details = SchemaNodeField(
        display="Identification of tree(s) and description of works",
        description="Details of trees affected by the proposed development and what work is being done to them.",
        schema_node_cls=TreeWorkDetails,
    )
    trees_additional = SchemaNodeField(
        display="Trees additional information",
        description="Further details of any issues relating to trees on the site",
        schema_node_cls=TreesAdditional,
    )
    trees_ownership = SchemaNodeField(
        display="Trees ownership",
        description="Who owns any trees affected by the proposed development.",
        schema_node_cls=TreesOwnership,
    )


class OutlineSome(SchemaNode):
    _ref = "outline-some"
    _display = "Outline Planning Permission with Some Matters Reserved"
    _description = "Outline planning permission with some matters reserved"

    access_rights_of_way = SchemaNodeField(
        display="Access and rights of way",
        description="Details of any changes the proposed development would make to existing access arrangements or public rights of way",
        schema_node_cls=AccessRightsOfWay,
    )
    bio_geo_arch_con = SchemaNodeField(
        display="Biodiversity, geological and archaeological conservation",
        description="Details of potential impacts to the biodiversity of the site, or any noteable archaeological or geological features.",
        schema_node_cls=BioGeoArchCon,
    )
    foul_sewage = SchemaNodeField(
        display="Foul sewage disposal",
        description="How waste water will leave the property as part of the proposed development",
        schema_node_cls=FoulSewage,
    )
    haz_substances = SchemaNodeField(
        display="Hazardous substances",
        description="Details of hazardous substances requiring consent used as part of the development",
        schema_node_cls=HazSubstances,
    )
    materials = SchemaNodeField(
        display="Materials",
        description="What materials are being used for the proposed development",
        schema_node_cls=Materials,
    )
    trade_effluent = SchemaNodeField(
        display="Trade effluent",
        description="Details of any liquid waste produced by industial processes on the proposed site, and how it will be diposed of.",
        schema_node_cls=TradeEffluent,
    )
    trees_hedges = SchemaNodeField(
        display="Trees and hedges information",
        description="Details of trees and/or hedges that will be affected by the proposed development",
        schema_node_cls=TreesHedges,
    )
    vehicle_parking = SchemaNodeField(
        display="Vehicle parking",
        description="Details of current parking facilities at the site and any changes that would be made by the proposed development.",
        schema_node_cls=VehicleParking,
    )
    waste_storage_collection = SchemaNodeField(
        display="Waste storage and collection",
        description="Any waste storage or recycling arrangements are in place, such as waste storage areas",
        schema_node_cls=WasteStorageCollection,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    bng = SchemaNodeField(
        display="Biodiversity net gain",
        description="How any natural habitats on the development site will be improved by the proposed works.",
        schema_node_cls=Bng,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    employment = SchemaNodeField(
        display="Employment",
        description="How the proposed development will impact existing and proposed employee numbers",
        schema_node_cls=Employment,
    )
    existing_use = SchemaNodeField(
        display="Existing use",
        description="How the site is currently being used.",
        schema_node_cls=ExistingUse,
    )
    flood_risk_assessment = SchemaNodeField(
        display="Flood risk assessment",
        description="Results of any flood risk assessments made for the development site",
        schema_node_cls=FloodRiskAssessment,
    )
    hrs_operation = SchemaNodeField(
        display="Hours of operation",
        description="Proposed operating hours if the proposed development is intended for non-residential use.",
        schema_node_cls=HrsOperation,
    )
    non_res_floorspace = SchemaNodeField(
        display="Non residential floorspace",
        description="Details of changes to non-residential floorspace in the proposed development.",
        schema_node_cls=NonResFloorspace,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    processes_machinery_waste = SchemaNodeField(
        display="Processes machinery waste",
        description="How waste will be managed on the site ",
        schema_node_cls=ProcessesMachineryWaste,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    res_units = SchemaNodeField(
        display="Residential units",
        description="Details of the residential units that make up both the current and proposed development.",
        schema_node_cls=ResUnits,
    )
    site_area = SchemaNodeField(
        display="Site area",
        description="How big the site is including relevant measurements",
        schema_node_cls=SiteArea,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class DescWorkImpactsRisks(SchemaNode):
    _ref = "desc-work-impacts-risks"
    _display = "Description of work impacts and risks"
    _description = "How the proposed development may affect nearby amenities, air traffic, defence assets or protected views."

    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    dwellinghouse_height = StringField(
        display="Dwellinghouse height",
        description="Height from ground to highest point of roof in metres",
        max_length=None,
    )
    proposed_height = StringField(
        display="Proposed height",
        description="Height once the additional storeys have been added in metres",
        max_length=None,
    )
    impact_on_amenity = StringField(
        display="Impact on amenity",
        description="Details of the impacts on the amenity of any adjoining premises including overlooking, privacy and the loss of light including how these will be mitigated",
        max_length=None,
    )
    air_traffic_defence_impacts = StringField(
        display="Air traffic defence impacts",
        description="Details of any air traffic and defence asset impacts, including how these will be mitigated",
        max_length=None,
    )
    protected_view_impact = StringField(
        display="Protected view impact",
        description="Details of the impact on any protected view where relevant",
        max_length=None,
    )


class EligibilityRelatedWorks(SchemaNode):
    _ref = "eligibility-related-works"
    _display = "Eligibility related works"
    _description = "Whether any related works such as scaffolding required will affect the eligibility of the planning proposal"

    external_support_required = BooleanField(
        display="External support required",
        description="Will the proposed engineering works include external support structures or extend beyond the curtilage for wall or foundation strengthening",
    )


class EligibilityCurrentBuilding(SchemaNode):
    _ref = "eligibility-current-building"
    _display = "Eligibility current building"
    _description = "How the current building meets eligibity criteria"

    was_constructed_btw_1948_2018 = BooleanField(
        display="Was constructed between 1948 and 2018",
        description="Was the current building constructed between 1 July 1948 and 28 October 2018? If False, application cannot proceed.",
    )
    has_additional_storeys = BooleanField(
        display="Additional storeys added",
        description="Have additional storeys already been added to the original building? If True, application cannot proceed.",
    )
    was_use_granted_by_pdr = BooleanField(
        display="Use granted by permitted development right",
        description="Was the current use of the building granted by permitted development rights? If True, application cannot proceed.",
    )
    is_site_in_restricted_area = BooleanField(
        display="Site in restricted area",
        description="Is any part of the land or site located in a restricted area? If True, application cannot proceed.",
    )


class EligibilityProposal(SchemaNode):
    _ref = "eligibility-proposal"
    _display = "Eligibility proposal"
    _description = "How the proposed development meets eligibility criteria"

    principal_part_only = BooleanField(
        display="Principal part only",
        description="Will the additional storeys be constructed only on the principal part of the building",
    )
    ceiling_height_exceeds_3m = BooleanField(
        display="Ceiling height exceeds 3m",
        description="Will the internal floor-to-ceiling height of any additional storey exceed 3 metres",
    )
    existing_ceiling_height_exceeds_3m = BooleanField(
        display="Existing ceiling height exceeds 3m",
        description="Will the internal floor-to-ceiling height of any existing storey exceed 3 metres",
    )
    building_height_exceeds_18m = BooleanField(
        display="Building height exceeds 18m",
        description="Will the height of the extended building exceed 18 metres",
    )
    roof_height_exceeds_3_5m = BooleanField(
        display="Roof height exceeds 3.5m",
        description="Will the roof exceed 3.5 metres above the highest part of the existing roof",
    )
    roof_height_exceeds_7m = BooleanField(
        display="Roof height exceeds 7m",
        description="Will the roof exceed 7 metres above the highest part of the existing roof",
    )
    is_dwelling_detached = BooleanField(
        display="Dwelling detached", description="Is the dwelling detached"
    )
    extension_on_attached_dwelling = BooleanField(
        display="Extension on attached dwelling",
        description="Will the extension result in the highest part exceeding 3.5 metres above the attached roof",
    )
    extension_below_terrace_roof = BooleanField(
        display="Extension below terrace roof",
        description="Will the extension result in the highest part exceeding 3.5 metres above any roof in the terrace",
    )
    roof_pitch_matching = BooleanField(
        display="Roof pitch matching",
        description="Will the roof pitch of the extended dwelling match the existing roof pitch",
    )
    window_on_side_elevation = BooleanField(
        display="Window on side elevation",
        description="Will the development include a side elevation window or roof slope window",
    )
    materials_similar_exterior = BooleanField(
        display="Materials similar exterior",
        description="Will exterior materials be similar to those of the existing dwelling",
    )
    dwellinghouse_use = BooleanField(
        display="Dwellinghouse use",
        description="Will the extended dwelling remain as a Class C3 dwellinghouse or ancillary use",
    )


class PaStorey(SchemaNode):
    _ref = "pa-storey"
    _display = "Additional storeys"
    _description = "Enlargement of a dwellinghouse by construction of additional storeys"

    desc_work_impacts_risks = SchemaNodeField(
        display="Description of work impacts and risks",
        description="How the proposed development may affect nearby amenities, air traffic, defence assets or protected views.",
        schema_node_cls=DescWorkImpactsRisks,
    )
    eligibility_related_works = SchemaNodeField(
        display="Eligibility related works",
        description="Whether any related works such as scaffolding required will affect the eligibility of the planning proposal",
        schema_node_cls=EligibilityRelatedWorks,
    )
    eligibility_current_building = SchemaNodeField(
        display="Eligibility current building",
        description="How the current building meets eligibity criteria",
        schema_node_cls=EligibilityCurrentBuilding,
    )
    eligibility_proposal = SchemaNodeField(
        display="Eligibility proposal",
        description="How the proposed development meets eligibility criteria",
        schema_node_cls=EligibilityProposal,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )


class NonResidentialUse(SchemaNode):
    _ref = "non-residential-use"
    _display = "Non-residential use"
    _description = "Structure for defining non-residential use amounts, which can be expressed as floorspace or site area with exact values or ranges "

    non_residential_measurement_type = EnumField(
        display="Non-residential measurement type",
        description="The type of value being provided for non-residential use - either floorspace or site-area",
        select_options=[
            EnumOption(
                key="floorspace",
                label="Floorspace",
                description="The total floor area of the building",
            ),
            EnumOption(
                key="site-area", label="Site area", description="The total area of the site"
            ),
        ],
    )
    exact_value = StringField(
        display="Exact value",
        description="Exact figure of non-residential use, measured in square metres for floorspace or hectares for site area",
        max_length=None,
    )
    min = StringField(
        display="Minimum value",
        description="Lower bound of non-residential use, measured in square metres for floorspace or hectares for site area",
        max_length=None,
    )
    max = StringField(
        display="Maximum value",
        description="Upper bound of non-residential use, measured in square metres for floorspace or hectares for site area",
        max_length=None,
    )


class ProposalDetailsIncNonResidential(SchemaNode):
    _ref = "proposal-details-inc-non-residential"
    _display = "Description of the proposed development including any non-residential development"
    _description = (
        "Details of the residential and non-residential parts of the proposed development."
    )

    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    net_dwellings_min = StringField(
        display="Net dwellings minimum",
        description="The minimum number of net additional dwellings proposed as part of the development, accounting for any existing dwellings lost and new dwellings created",
        max_length=None,
    )
    net_dwellings_max = StringField(
        display="Net dwellings maximum",
        description="The maximum number of net additional dwellings proposed as part of the development, allowing for flexibility in the final housing numbers",
        max_length=None,
    )

    non_residential_use = SchemaNodeField(
        display="Non-residential use",
        description="Structure for defining non-residential use amounts, which can be expressed as floorspace or site area with exact values or ranges ",
        schema_node_cls=NonResidentialUse,
    )


class SiteAreacomponentresolved(SchemaNode):
    _ref = "site-area"
    _display = "Site area"
    _description = "Information about the total area of a development site, including the measured value, unit, and source of the measurement "

    value = StringField(
        display="Value",
        description="Numeric value representing a measurement or quantity",
        max_length=None,
    )
    unit = StringField(
        display="Unit", description="Unit of measurement for a value", max_length=None
    )
    provided_by = EnumField(
        display="Provided by",
        description="Whether the information was provided by the applicant or calculated by the system",
        select_options=[
            EnumOption(
                key="applicant",
                label="Applicant",
                description="Information provided by the applicant",
            ),
            EnumOption(
                key="system",
                label="System/Service",
                description="Information calculated or determined by the system or external service",
            ),
        ],
    )


class Uses(SchemaNode):
    _ref = "uses"
    _display = "Use"
    _description = "A specific use class or type of use for a site or building "

    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    specified_use = StringField(
        display="Specified use",
        description="A specified use if no applicable use class is available",
        max_length=None,
    )


class ExistingUsecomponentresolved(SchemaNode):
    _ref = "existing-use"
    _display = "Existing use"
    _description = "Information about the current use of a site, including the use classes and associated floorspace "

    floorspace = StringField(
        display="Floorspace",
        description="Total floorspace for a use in square metres",
        max_length=None,
    )

    uses = SchemaNodeField(
        display="Use",
        description="A specific use class or type of use for a site or building ",
        schema_node_cls=Uses,
    )


class SiteInfo(SchemaNode):
    _ref = "site-info"
    _display = "Site information"
    _description = "Any additional relevant information about the development site."

    known_constraints = EnumField(
        display="Known constraints",
        description="A list of the known constraints affecting the site",
        select_options=[
            EnumOption(key="conservation-area", label="Conservation Area", description=""),
            EnumOption(
                key="aona-beauty", label="Area of Outstanding Natural Beauty", description=""
            ),
            EnumOption(
                key="secretary-specified-area",
                label="Secretary of State Protected Area",
                description="",
            ),
            EnumOption(key="the-broads", label="The Broads", description=""),
            EnumOption(key="national-park", label="National Park", description=""),
            EnumOption(key="world-heritage-site", label="World Heritage Site", description=""),
            EnumOption(
                key="site-of-special-interest",
                label="Site of Special Scientific Interest",
                description="",
            ),
        ],
    )

    site_area = SchemaNodeField(
        display="Site area",
        description="Information about the total area of a development site, including the measured value, unit, and source of the measurement ",
        schema_node_cls=SiteAreacomponentresolved,
    )
    existing_use = SchemaNodeField(
        display="Existing use",
        description="Information about the current use of a site, including the use classes and associated floorspace ",
        schema_node_cls=ExistingUsecomponentresolved,
    )
    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class Pip(SchemaNode):
    _ref = "pip"
    _display = "Permission in principle"
    _description = "An alternative way of getting planning permission for housing-led development which separates the consideration of matters of principle from the technical detail of the development"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    proposal_details_inc_non_residential = SchemaNodeField(
        display="Description of the proposed development including any non-residential development",
        description="Details of the residential and non-residential parts of the proposed development.",
        schema_node_cls=ProposalDetailsIncNonResidential,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_info = SchemaNodeField(
        display="Site information",
        description="Any additional relevant information about the development site.",
        schema_node_cls=SiteInfo,
    )


class ConRemoveVary(SchemaNode):
    _ref = "con-remove-vary"
    _display = "Condition removal or variation"
    _description = "Why the applicant is asking for planning conditions to be removed or changed."

    reason = StringField(display="Reason", description="A textual reason", max_length=None)
    condition_change = StringField(
        display="Condition change",
        description="State how the condition should vary",
        max_length=None,
    )


class DescYourProposal(SchemaNode):
    _ref = "desc-your-proposal"
    _display = "Description of your proposal"
    _description = (
        "Written description of the proposed development including any additional relevant details."
    )

    condition_numbers = StringField(
        display="Condition numbers",
        description="List of condition numbers related to this application",
        max_length=None,
    )
    original_application_type = StringField(
        display="Original application type",
        description="Type of original planning application",
        max_length=None,
    )
    is_householder_development = BooleanField(
        display="Is householder development",
        description="Is the development to an existing dwelling-house or development within its curtilage (true/false)",
    )
    has_development_started = BooleanField(
        display="Has development started", description="Whether the development has already started"
    )
    development_start_date = StringField(
        display="Development start date",
        description="Date when development started",
        max_length=None,
    )
    has_development_completed = BooleanField(
        display="Has development completed",
        description="Whether the development has been completed",
    )
    development_completed_date = StringField(
        display="Development completed date",
        description="Date when development was completed",
        max_length=None,
    )

    related_application = SchemaNodeField(
        display="Related application details",
        description="Details about a related application including its reference, description and decision date ",
        schema_node_cls=RelatedApplication,
    )


class S73(SchemaNode):
    _ref = "s73"
    _display = "Removal or variation of a condition following grant of planning permission"
    _description = "Applications for a removal or variation of a condition after planning permission has been granted"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    con_remove_vary = SchemaNodeField(
        display="Condition removal or variation",
        description="Why the applicant is asking for planning conditions to be removed or changed.",
        schema_node_cls=ConRemoveVary,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    desc_your_proposal = SchemaNodeField(
        display="Description of your proposal",
        description="Written description of the proposed development including any additional relevant details.",
        schema_node_cls=DescYourProposal,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class Parking(SchemaNode):
    _ref = "parking"
    _display = "Parking arrangements"
    _description = (
        "Details of any changes the proposed development would make to parking facilities."
    )

    is_existing_parking_affected = BooleanField(
        display="Existing parking affected",
        description="Will the proposed works affect existing car parking arrangements",
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )


class Hh(SchemaNode):
    _ref = "hh"
    _display = "Householder planning application"
    _description = "A simplified process for applications to alter or enlarge a single house (but not a flat), including works within the boundary/garden"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    access_rights_of_way = SchemaNodeField(
        display="Access and rights of way",
        description="Details of any changes the proposed development would make to existing access arrangements or public rights of way",
        schema_node_cls=AccessRightsOfWay,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    bng = SchemaNodeField(
        display="Biodiversity net gain",
        description="How any natural habitats on the development site will be improved by the proposed works.",
        schema_node_cls=Bng,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    materials = SchemaNodeField(
        display="Materials",
        description="What materials are being used for the proposed development",
        schema_node_cls=Materials,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    parking = SchemaNodeField(
        display="Parking arrangements",
        description="Details of any changes the proposed development would make to parking facilities.",
        schema_node_cls=Parking,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )
    trees_hedges = SchemaNodeField(
        display="Trees and hedges information",
        description="Details of trees and/or hedges that will be affected by the proposed development",
        schema_node_cls=TreesHedges,
    )


class Outline(SchemaNode):
    _ref = "outline"
    _display = "Outline planning"
    _description = "Applications that are used to understand whether the basic nature of a development is viable"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    bng = SchemaNodeField(
        display="Biodiversity net gain",
        description="How any natural habitats on the development site will be improved by the proposed works.",
        schema_node_cls=Bng,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    employment = SchemaNodeField(
        display="Employment",
        description="How the proposed development will impact existing and proposed employee numbers",
        schema_node_cls=Employment,
    )
    existing_use = SchemaNodeField(
        display="Existing use",
        description="How the site is currently being used.",
        schema_node_cls=ExistingUse,
    )
    flood_risk_assessment = SchemaNodeField(
        display="Flood risk assessment",
        description="Results of any flood risk assessments made for the development site",
        schema_node_cls=FloodRiskAssessment,
    )
    hrs_operation = SchemaNodeField(
        display="Hours of operation",
        description="Proposed operating hours if the proposed development is intended for non-residential use.",
        schema_node_cls=HrsOperation,
    )
    non_res_floorspace = SchemaNodeField(
        display="Non residential floorspace",
        description="Details of changes to non-residential floorspace in the proposed development.",
        schema_node_cls=NonResFloorspace,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    processes_machinery_waste = SchemaNodeField(
        display="Processes machinery waste",
        description="How waste will be managed on the site ",
        schema_node_cls=ProcessesMachineryWaste,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    res_units = SchemaNodeField(
        display="Residential units",
        description="Details of the residential units that make up both the current and proposed development.",
        schema_node_cls=ResUnits,
    )
    site_area = SchemaNodeField(
        display="Site area",
        description="How big the site is including relevant measurements",
        schema_node_cls=SiteArea,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class DesignatedAreas(SchemaNode):
    _ref = "designated-areas"
    _display = "Designated areas"
    _description = "Details of any 'designated area' the develpoment site is on, such as a Conservation Area or National Park."

    designations = EnumField(
        display="Designations",
        description="List of designated areas that apply to the site",
        select_options=[
            EnumOption(
                key="world-heritage-site",
                label="World Heritage Site",
                description="Site of global cultural or natural importance",
            ),
            EnumOption(
                key="national-park",
                label="National Park",
                description="Protected area for natural beauty and recreation",
            ),
            EnumOption(
                key="area-outstanding-natural-beauty",
                label="Area of Outstanding Natural Beauty (AONB)",
                description="Designated for distinctive landscape value",
            ),
            EnumOption(
                key="site-special-scientific-interest",
                label="Site of Special Scientific Interest (SSSI)",
                description="Protected for wildlife, geology, or landform",
            ),
            EnumOption(
                key="national-nature-reserve",
                label="National Nature Reserve",
                description="Important area for wildlife and conservation",
            ),
            EnumOption(
                key="conservation-area",
                label="Conservation Area",
                description="Area designated for historical or architectural significance",
            ),
            EnumOption(
                key="special-area-conservation",
                label="Special Area of Conservation",
                description="Designated under the EU Habitats Directive",
            ),
            EnumOption(
                key="special-protection-area",
                label="Special Protection Area/Ramsar site",
                description="Protected for bird species under the EU Birds Directive",
            ),
            EnumOption(
                key="green-belt",
                label="Green Belt",
                description="Area designated to prevent urban sprawl",
            ),
            EnumOption(
                key="secretary-specified-area",
                label="Secretary of State Protected Area",
                description="",
            ),
            EnumOption(key="the-broads", label="The Broads", description=""),
        ],
    )


class EquipMethod(SchemaNode):
    _ref = "equip-method"
    _display = "Equipment and method"
    _description = "How oil and gas will be extracted as part of the proposed development."

    equipment_plan = StringField(
        display="Equipment plan",
        description="Details of equipment to be used as part of the application including the maximum height and type of drilling rig to be used",
        max_length=None,
    )


class PlansDrawingsSupportingMaterials(SchemaNode):
    _ref = "plans-drawings-supporting-materials"
    _display = "Plans, drawings and supporting materials"
    _description = (
        "Additional materials and specifications that form part of the planning application"
    )

    inspection_address = StringField(
        display="Inspection address",
        description="Full postal address where supporting material can be inspected",
        max_length=None,
    )

    supporting_documents = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=SupportingDocuments,
    )


class SiteOwner(SchemaNode):
    _ref = "site-owner"
    _display = "Site owner"
    _description = "Details of the owner of the development site including name and address "

    fullname = StringField(
        display="Full name", description="The complete name of a person", max_length=None
    )
    address_text = StringField(
        display="Address Text",
        description="Flexible field for capturing addresses",
        max_length=None,
    )


class SiteOwnership(SchemaNode):
    _ref = "site-ownership"
    _display = "Site ownership"
    _description = (
        "For oil and gas extraction developments, who owns or has an interest in the site."
    )

    applicant_interest = StringField(
        display="Applicant interest",
        description="Description of the applicant's interest in the land",
        max_length=None,
    )
    applicant_interest_adjoining_land = StringField(
        display="Applicant interest adjoining land",
        description="Description of the applicant's interest in the adjacent land",
        max_length=None,
    )

    site_owner = SchemaNodeField(
        display="Site owner",
        description="Details of the owner of the development site including name and address ",
        schema_node_cls=SiteOwner,
    )


class StorageFacilities(SchemaNode):
    _ref = "storage-facilities"
    _display = "Storage facilities"
    _description = "For oil and gas extraction developments, how chemicals will be stored"

    storage_facilities_description = StringField(
        display="Storage facilities description",
        description="Details and proposed facilities for the storage of oil, fuel and chemicals and the proposed means of their protection",
        max_length=None,
    )


class RelatedPermissions(SchemaNode):
    _ref = "related-permissions"
    _display = "Related permission-details"
    _description = "Details about a related permission including the reference of the original application, type and decision date, and an option condition number/reference if varying "

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    oilgas_permission_type = EnumField(
        display="Oil and gas permission type",
        description="An oil and gas related permission type",
        select_options=[
            EnumOption(
                key="oil-gas-full-permission",
                label="Full planning permission for oil and gas working",
                description="",
            ),
            EnumOption(
                key="waste-full-permission",
                label="Full planning permission for controlled waste",
                description="",
            ),
            EnumOption(
                key="renewal-unimplemented",
                label="Renewal of unimplemented permission",
                description="",
            ),
            EnumOption(
                key="renewal-temporary", label="Renewal of temporary permission", description=""
            ),
            EnumOption(
                key="extension-existing-site", label="Extension to an existing site", description=""
            ),
            EnumOption(
                key="variation-condition", label="Variation of condition(s)", description=""
            ),
            EnumOption(
                key="romp-review",
                label="Review of conditions for Mineral Permissions (ROMPs)",
                description="",
            ),
            EnumOption(
                key="minerals-development",
                label="Previous permissions for minerals development on the site",
                description="",
            ),
        ],
    )
    decision_date = StringField(
        display="Decision date",
        description="The date when the decision was made, in YYYY-MM-DD format",
        max_length=None,
    )
    condition_number = StringField(
        display="Condition number",
        description="Number of any condition being breached",
        max_length=None,
    )


class RelatedProposals(SchemaNode):
    _ref = "related-proposals"
    _display = "Related proposal"
    _description = (
        "Details about a related proposal including its reference, type and decision date "
    )

    reference = StringField(
        display="Reference", description="A unique reference for the data item", max_length=None
    )
    application_type = StringField(
        display="Application type", description="The type of planning application", max_length=None
    )
    decision_date = StringField(
        display="Decision date",
        description="The date when the decision was made, in YYYY-MM-DD format",
        max_length=None,
    )


class OilgasPermissionType(SchemaNode):
    _ref = "oilgas-permission-type"
    _display = "Oil and gas permission types"
    _description = "Module for details about types of onshore oil and gas extraction permissions already received and applying for "

    oilgas_permission_types = EnumField(
        display="Oil and gas permission types",
        description="List of permission types being applied for",
        select_options=[
            EnumOption(
                key="oil-gas-full-permission",
                label="Full planning permission for oil and gas working",
                description="",
            ),
            EnumOption(
                key="waste-full-permission",
                label="Full planning permission for controlled waste",
                description="",
            ),
            EnumOption(
                key="renewal-unimplemented",
                label="Renewal of unimplemented permission",
                description="",
            ),
            EnumOption(
                key="renewal-temporary", label="Renewal of temporary permission", description=""
            ),
            EnumOption(
                key="extension-existing-site", label="Extension to an existing site", description=""
            ),
            EnumOption(
                key="variation-condition", label="Variation of condition(s)", description=""
            ),
            EnumOption(
                key="romp-review",
                label="Review of conditions for Mineral Permissions (ROMPs)",
                description="",
            ),
            EnumOption(
                key="minerals-development",
                label="Previous permissions for minerals development on the site",
                description="",
            ),
        ],
    )
    other_details = StringField(
        display="Other details",
        description="Explanation if other ground is selected",
        max_length=None,
    )
    will_consolidate_permissions = BooleanField(
        display="Will consolidate permissions",
        description="Is the applicant looking to consolidate permissions?",
    )
    details = StringField(
        display="Details",
        description="Additional details or information about an item",
        max_length=None,
    )

    related_permissions = SchemaNodeField(
        display="Related permission-details",
        description="Details about a related permission including the reference of the original application, type and decision date, and an option condition number/reference if varying ",
        schema_node_cls=RelatedPermissions,
    )
    related_proposals = SchemaNodeField(
        display="Related proposal",
        description="Details about a related proposal including its reference, type and decision date ",
        schema_node_cls=RelatedProposals,
    )


class DevType(SchemaNode):
    _ref = "dev-type"
    _display = "Development type"
    _description = (
        "Supporting information for developments used for oil and gas exploration or mining "
    )

    development_phase = EnumField(
        display="Development phase",
        description="Phases of oil and gas development the application covers",
        select_options=[
            EnumOption(
                key="exploratory",
                label="Exploratory Phase",
                description="Initial drilling and testing for hydrocarbons.",
            ),
            EnumOption(
                key="appraisal",
                label="Appraisal Phase",
                description="Further testing to determine viability.",
            ),
            EnumOption(
                key="production",
                label="Production Phase",
                description="Full-scale extraction and production operations.",
            ),
        ],
    )
    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    quantity_cubic_metres = StringField(
        display="Quantity cubic metres",
        description="Quantity of oil or gas involved in cubic metres",
        max_length=None,
    )
    permission_period_years = StringField(
        display="Permission period years",
        description="Period of permission sought in years",
        max_length=None,
    )
    hydrocarbon_licence_block = StringField(
        display="Hydrocarbon licence block",
        description="Hydrocarbon licence block where the development is located",
        max_length=None,
    )
    surface_site_area_hectares = StringField(
        display="Surface site area hectares",
        description="Surface site area in hectares",
        max_length=None,
    )
    site_hectares_provided_by = EnumField(
        display="Site hectares provided by",
        description="Who provided the site hectares value (applicant or system)",
        select_options=[
            EnumOption(
                key="applicant",
                label="Applicant",
                description="Information provided by the applicant",
            ),
            EnumOption(
                key="system",
                label="System/Service",
                description="Information calculated or determined by the system or external service",
            ),
        ],
    )
    environmental_statement = BooleanField(
        display="Environmental statement",
        description="Is an Environmental Statement attached to the application",
    )
    environmental_statement_reference = StringField(
        display="Environmental statement reference",
        description="Reference of the environmental statement document supplied with application",
        max_length=None,
    )


class VolAgreement(SchemaNode):
    _ref = "vol-agreement"
    _display = "Voluntary agreement"
    _description = (
        "Details of any voluntary agreements made as part of an oil and gas extraction application."
    )

    draft_agreement_included = BooleanField(
        display="Draft agreement included",
        description="Has an outline or draft agreement been included? (True / False)",
    )
    agreement_summary = StringField(
        display="Agreement summary", description="Summary of the agreement", max_length=None
    )


class ExtractionOilGas(SchemaNode):
    _ref = "extraction-oil-gas"
    _display = "Development relating to the onshore extraction of oil and gas"
    _description = "Development relating to the onshore extraction of oil and gas (including exploratory, appraisal and production phases) and the associated plans, documents and validation information required to support an application. "

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    flood_risk_assessment = SchemaNodeField(
        display="Flood risk assessment",
        description="Results of any flood risk assessments made for the development site",
        schema_node_cls=FloodRiskAssessment,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    bio_geo_arch_con = SchemaNodeField(
        display="Biodiversity, geological and archaeological conservation",
        description="Details of potential impacts to the biodiversity of the site, or any noteable archaeological or geological features.",
        schema_node_cls=BioGeoArchCon,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    designated_areas = SchemaNodeField(
        display="Designated areas",
        description="Details of any 'designated area' the develpoment site is on, such as a Conservation Area or National Park.",
        schema_node_cls=DesignatedAreas,
    )
    employment = SchemaNodeField(
        display="Employment",
        description="How the proposed development will impact existing and proposed employee numbers",
        schema_node_cls=Employment,
    )
    equip_method = SchemaNodeField(
        display="Equipment and method",
        description="How oil and gas will be extracted as part of the proposed development.",
        schema_node_cls=EquipMethod,
    )
    existing_use = SchemaNodeField(
        display="Existing use",
        description="How the site is currently being used.",
        schema_node_cls=ExistingUse,
    )
    foul_sewage = SchemaNodeField(
        display="Foul sewage disposal",
        description="How waste water will leave the property as part of the proposed development",
        schema_node_cls=FoulSewage,
    )
    haz_substances = SchemaNodeField(
        display="Hazardous substances",
        description="Details of hazardous substances requiring consent used as part of the development",
        schema_node_cls=HazSubstances,
    )
    hrs_operation = SchemaNodeField(
        display="Hours of operation",
        description="Proposed operating hours if the proposed development is intended for non-residential use.",
        schema_node_cls=HrsOperation,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    access_rights_of_way = SchemaNodeField(
        display="Access and rights of way",
        description="Details of any changes the proposed development would make to existing access arrangements or public rights of way",
        schema_node_cls=AccessRightsOfWay,
    )
    plans_drawings_supporting_materials = SchemaNodeField(
        display="Plans, drawings and supporting materials",
        description="Additional materials and specifications that form part of the planning application",
        schema_node_cls=PlansDrawingsSupportingMaterials,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_ownership = SchemaNodeField(
        display="Site ownership",
        description="For oil and gas extraction developments, who owns or has an interest in the site.",
        schema_node_cls=SiteOwnership,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )
    storage_facilities = SchemaNodeField(
        display="Storage facilities",
        description="For oil and gas extraction developments, how chemicals will be stored",
        schema_node_cls=StorageFacilities,
    )
    trade_effluent = SchemaNodeField(
        display="Trade effluent",
        description="Details of any liquid waste produced by industial processes on the proposed site, and how it will be diposed of.",
        schema_node_cls=TradeEffluent,
    )
    trees_hedges = SchemaNodeField(
        display="Trees and hedges information",
        description="Details of trees and/or hedges that will be affected by the proposed development",
        schema_node_cls=TreesHedges,
    )
    oilgas_permission_type = SchemaNodeField(
        display="Oil and gas permission types",
        description="Module for details about types of onshore oil and gas extraction permissions already received and applying for ",
        schema_node_cls=OilgasPermissionType,
    )
    dev_type = SchemaNodeField(
        display="Development type",
        description="Supporting information for developments used for oil and gas exploration or mining ",
        schema_node_cls=DevType,
    )
    vol_agreement = SchemaNodeField(
        display="Voluntary agreement",
        description="Details of any voluntary agreements made as part of an oil and gas extraction application.",
        schema_node_cls=VolAgreement,
    )


class NotifiedPersons(SchemaNode):
    _ref = "notified-persons"
    _display = "Notified person"
    _description = "Details of a person that has been notified (often owners and agricultural tenants of the land)"

    notice_date = StringField(
        display="Notice date",
        description="Date when notice was served to an owner or tenant",
        max_length=None,
    )

    person = SchemaNodeField(
        display="Person obj", description="Details of an individual ", schema_node_cls=Person
    )


class Eligibility(SchemaNode):
    _ref = "eligibility"
    _display = "Eligibility"
    _description = "Whether certain eligibility criteria has been met and the right people notified"

    applicant_land_interest = BooleanField(
        display="Applicant land interest",
        description="Does the applicant have an interest in the land",
    )
    ownership_notification = EnumField(
        display="Ownership notification",
        description="If not the sole owner, has notification been given under Article 10",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response"),
            EnumOption(
                key="not-applicable",
                label="Not Applicable",
                description="Response not applicable or not provided",
            ),
        ],
    )

    notified_persons = SchemaNodeField(
        display="Notified person",
        description="Details of a person that has been notified (often owners and agricultural tenants of the land)",
        schema_node_cls=NotifiedPersons,
    )


class ReplacementDocuments(SchemaNode):
    _ref = "replacement-documents"
    _display = "Replacement document"
    _description = "Structure for documents being replaced in non-material amendments, mapping old document references to new document references held in application.documents "

    old_document = StringField(
        display="Old document",
        description="Reference of the old document being replaced in the amendment",
        max_length=None,
    )
    new_document = StringField(
        display="New document",
        description="Reference for the new document replacing the old document in the amendment",
        max_length=None,
    )


class NmAmendmentDetails(SchemaNode):
    _ref = "nm-amendment-details"
    _display = "Non-material amendment details"
    _description = (
        "Details of changes being requested to plans after permission has already been granted."
    )

    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )
    is_substituting_document = BooleanField(
        display="Substituting document",
        description="True or False indicating whether the amendment involves substituting documents",
    )
    reason = StringField(display="Reason", description="A textual reason", max_length=None)

    replacement_documents = SchemaNodeField(
        display="Replacement document",
        description="Structure for documents being replaced in non-material amendments, mapping old document references to new document references held in application.documents ",
        schema_node_cls=ReplacementDocuments,
    )


class NonMaterialAmendment(SchemaNode):
    _ref = "non-material-amendment"
    _display = "Non-material amendment (S96a)"
    _description = (
        "An application for any minor changes to proposals that have already been approved"
    )

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    desc_your_proposal = SchemaNodeField(
        display="Description of your proposal",
        description="Written description of the proposed development including any additional relevant details.",
        schema_node_cls=DescYourProposal,
    )
    eligibility = SchemaNodeField(
        display="Eligibility",
        description="Whether certain eligibility criteria has been met and the right people notified",
        schema_node_cls=Eligibility,
    )
    nm_amendment_details = SchemaNodeField(
        display="Non-material amendment details",
        description="Details of changes being requested to plans after permission has already been granted.",
        schema_node_cls=NmAmendmentDetails,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class AdvertLocation(SchemaNode):
    _ref = "advert-location"
    _display = "Advertisement location"
    _description = "Where the advertisement being applied to be built will be located"

    is_advert_in_place = BooleanField(
        display="Is advert in place", description="Whether the advertisement is already in place"
    )
    advert_placed_date = StringField(
        display="Advert placed date",
        description="Date when the advertisement was placed (YYYY-MM-DD format)",
        max_length=None,
    )
    is_replacement_advert = BooleanField(
        display="Is replacement advert", description="Whether this is a replacement advertisement"
    )
    is_advert_overhanging = BooleanField(
        display="Is advert overhanging",
        description="Whether the advertisement will project over a footpath or other public highway",
    )

    document_reference = SchemaNodeField(
        display="Supporting document",
        description="Reference to a supporting document already listed in application.documents ",
        schema_node_cls=DocumentReference,
    )


class AdvertPeriod(SchemaNode):
    _ref = "advert-period"
    _display = "Advert period"
    _description = "How long the proposed advertisement will be shown."

    advert_start_date = StringField(
        display="Advert start date",
        description="The start of the time period that consent to advertisement is sought",
        max_length=None,
    )
    advert_end_date = StringField(
        display="Advert end date",
        description="The end of the time period that consent to advertisement is sought",
        max_length=None,
    )


class AdvertisementProposalType(SchemaNode):
    _ref = "advertisement-proposal-type"
    _display = "Advertisement proposal type"
    _description = "Information about a specific type of advertisement including type, count, and additional description if 'other' type is selected "

    advertisement_type = EnumField(
        display="Advertisement type",
        description="One of the advertisement-types or other",
        select_options=[
            EnumOption(key="fascia", label="Fascia", description=""),
            EnumOption(
                key="projecting-hanging", label="Projecting or hanging sign", description=""
            ),
            EnumOption(key="hoarding", label="Hoarding", description=""),
            EnumOption(key="other", label="Other", description=""),
        ],
    )
    advertisement_count = StringField(
        display="Advertisement count",
        description="Number of this type of advertisement",
        max_length=None,
    )
    advertisement_other_description = StringField(
        display="Advertisement other description",
        description="Details required if other advertisement type is selected",
        max_length=None,
    )


class AdvertisementTypes(SchemaNode):
    _ref = "advertisement-types"
    _display = "Advertisement types"
    _description = "What type of advertisements are proposed and how many there will be."

    description = StringField(
        display="Description",
        description="A text description providing details about the subject.",
        max_length=None,
    )

    advertisement_proposal_type = SchemaNodeField(
        display="Advertisement proposal type",
        description="Information about a specific type of advertisement including type, count, and additional description if 'other' type is selected ",
        schema_node_cls=AdvertisementProposalType,
    )


class InterestInLand(SchemaNode):
    _ref = "interest-in-land"
    _display = "Interest in land"
    _description = "Whether the applicant owns or has permission to use the land where the proposed advertisement will be placed"

    applicant_owns_land = BooleanField(
        display="Applicant owns land",
        description="True or False indicating whether the applicant owns the land where the advertisement will be displayed",
    )
    permission_obtained = BooleanField(
        display="Permission obtained",
        description="True or False indicating whether permission of the owner for the display of an advertisement has been obtained",
    )
    permission_not_obtained_details = StringField(
        display="Permission not obtained details",
        description="Details explaining why permission from the land owner has not been obtained for the advertisement display",
        max_length=None,
    )


class Advertisements(SchemaNode):
    _ref = "advertisements"
    _display = "Advertisement"
    _description = (
        "Details of a proposed advertisement including dimensions, materials, and illumination"
    )

    height_from_ground = StringField(
        display="Height from ground",
        description="Height, in metres, from ground to the base of the advertisement",
        max_length=None,
    )
    height = StringField(
        display="Height",
        description="Height, in metres, of dimensions of advertisement",
        max_length=None,
    )
    width = StringField(
        display="Width", description="Width of dimensions of advertisement", max_length=None
    )
    depth = StringField(
        display="Depth",
        description="Depth, in metres, of dimensions of advertisement",
        max_length=None,
    )
    symbol_height_max = StringField(
        display="Symbol height max",
        description="Maximum height, in metres, of any individual letters or symbols",
        max_length=None,
    )
    colour = StringField(display="Colour", description="Colour of proposed sign", max_length=None)
    materials = StringField(
        display="Materials", description="Materials of proposed sign", max_length=None
    )
    max_projection = StringField(
        display="Max projection",
        description="Maximum projection, in metres, of the advertisement from the face of the building",
        max_length=None,
    )
    illuminated = BooleanField(
        display="Illuminated", description="Will the sign(s) be illuminated?"
    )
    illumination_method = EnumField(
        display="Illumination method",
        description="Method of illumination for the advertisement",
        select_options=[
            EnumOption(
                key="internally",
                label="Internally",
                description="Illumination provided from within the advertisement structure.",
            ),
            EnumOption(
                key="externally",
                label="Externally",
                description="Illumination provided by external light sources.",
            ),
        ],
    )
    illuminance_level = StringField(
        display="Illuminance level",
        description="Level of illuminance for the advertisement",
        max_length=None,
    )
    illumination_type = EnumField(
        display="Illumination type",
        description="Type of illumination (static or intermittent)",
        select_options=[
            EnumOption(
                key="static",
                label="Static",
                description="Illumination is constant and does not change or flash.",
            ),
            EnumOption(
                key="intermittent",
                label="Intermittent",
                description="Illumination switches on and off or flashes at intervals.",
            ),
        ],
    )


class ProposedAdvertDetails(SchemaNode):
    _ref = "proposed-advert-details"
    _display = "Proposed advert details"
    _description = "Details of the proposed advertisements such as their size and how they are made"

    advertisements = SchemaNodeField(
        display="Advertisement",
        description="Details of a proposed advertisement including dimensions, materials, and illumination",
        schema_node_cls=Advertisements,
    )


class Advertising(SchemaNode):
    _ref = "advertising"
    _display = "Advertising"
    _description = "An application for all types of advertisements and signs"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    advert_location = SchemaNodeField(
        display="Advertisement location",
        description="Where the advertisement being applied to be built will be located",
        schema_node_cls=AdvertLocation,
    )
    advert_period = SchemaNodeField(
        display="Advert period",
        description="How long the proposed advertisement will be shown.",
        schema_node_cls=AdvertPeriod,
    )
    advertisement_types = SchemaNodeField(
        display="Advertisement types",
        description="What type of advertisements are proposed and how many there will be.",
        schema_node_cls=AdvertisementTypes,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    community_consultation = SchemaNodeField(
        display="Community consultation",
        description="What community consultation activities have taken place as part of the application",
        schema_node_cls=CommunityConsultation,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    interest_in_land = SchemaNodeField(
        display="Interest in land",
        description="Whether the applicant owns or has permission to use the land where the proposed advertisement will be placed",
        schema_node_cls=InterestInLand,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    proposed_advert_details = SchemaNodeField(
        display="Proposed advert details",
        description="Details of the proposed advertisements such as their size and how they are made",
        schema_node_cls=ProposedAdvertDetails,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class Ldc(SchemaNode):
    _ref = "ldc"
    _display = "Lawful development certificate"
    _description = "A legal document stating the lawfulness of past, present or future building use, operation or other matters, signifying that enforcement action cannot be carried out against the development"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    interest_details = SchemaNodeField(
        display="Interest details",
        description="Names and contact details for all parties with an interest in the proposed develpoment.",
        schema_node_cls=InterestDetails,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class Full(SchemaNode):
    _ref = "full"
    _display = "Full planning permission"
    _description = "This application is needed when making detailed proposals for developments which are not covered by a householder application or permitted development rights"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    access_rights_of_way = SchemaNodeField(
        display="Access and rights of way",
        description="Details of any changes the proposed development would make to existing access arrangements or public rights of way",
        schema_node_cls=AccessRightsOfWay,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    bio_geo_arch_con = SchemaNodeField(
        display="Biodiversity, geological and archaeological conservation",
        description="Details of potential impacts to the biodiversity of the site, or any noteable archaeological or geological features.",
        schema_node_cls=BioGeoArchCon,
    )
    bng = SchemaNodeField(
        display="Biodiversity net gain",
        description="How any natural habitats on the development site will be improved by the proposed works.",
        schema_node_cls=Bng,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    employment = SchemaNodeField(
        display="Employment",
        description="How the proposed development will impact existing and proposed employee numbers",
        schema_node_cls=Employment,
    )
    existing_use = SchemaNodeField(
        display="Existing use",
        description="How the site is currently being used.",
        schema_node_cls=ExistingUse,
    )
    flood_risk_assessment = SchemaNodeField(
        display="Flood risk assessment",
        description="Results of any flood risk assessments made for the development site",
        schema_node_cls=FloodRiskAssessment,
    )
    foul_sewage = SchemaNodeField(
        display="Foul sewage disposal",
        description="How waste water will leave the property as part of the proposed development",
        schema_node_cls=FoulSewage,
    )
    haz_substances = SchemaNodeField(
        display="Hazardous substances",
        description="Details of hazardous substances requiring consent used as part of the development",
        schema_node_cls=HazSubstances,
    )
    hrs_operation = SchemaNodeField(
        display="Hours of operation",
        description="Proposed operating hours if the proposed development is intended for non-residential use.",
        schema_node_cls=HrsOperation,
    )
    materials = SchemaNodeField(
        display="Materials",
        description="What materials are being used for the proposed development",
        schema_node_cls=Materials,
    )
    non_res_floorspace = SchemaNodeField(
        display="Non residential floorspace",
        description="Details of changes to non-residential floorspace in the proposed development.",
        schema_node_cls=NonResFloorspace,
    )
    ownership_certs = SchemaNodeField(
        display="Ownership certificates and agricultural land declaration",
        description="Who will be affected by the proposal and whether they have been notified, such as agricultural tenants",
        schema_node_cls=OwnershipCerts,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    processes_machinery_waste = SchemaNodeField(
        display="Processes machinery waste",
        description="How waste will be managed on the site ",
        schema_node_cls=ProcessesMachineryWaste,
    )
    proposal_details = SchemaNodeField(
        display="Description of the proposal",
        description="What development, works or change of use is proposed",
        schema_node_cls=ProposalDetails,
    )
    res_units = SchemaNodeField(
        display="Residential units",
        description="Details of the residential units that make up both the current and proposed development.",
        schema_node_cls=ResUnits,
    )
    site_area = SchemaNodeField(
        display="Site area",
        description="How big the site is including relevant measurements",
        schema_node_cls=SiteArea,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )
    trade_effluent = SchemaNodeField(
        display="Trade effluent",
        description="Details of any liquid waste produced by industial processes on the proposed site, and how it will be diposed of.",
        schema_node_cls=TradeEffluent,
    )
    trees_hedges = SchemaNodeField(
        display="Trees and hedges information",
        description="Details of trees and/or hedges that will be affected by the proposed development",
        schema_node_cls=TreesHedges,
    )
    vehicle_parking = SchemaNodeField(
        display="Vehicle parking",
        description="Details of current parking facilities at the site and any changes that would be made by the proposed development.",
        schema_node_cls=VehicleParking,
    )
    waste_storage_collection = SchemaNodeField(
        display="Waste storage and collection",
        description="Any waste storage or recycling arrangements are in place, such as waste storage areas",
        schema_node_cls=WasteStorageCollection,
    )


class Addresses(SchemaNode):
    _ref = "addresses"
    _display = "Address"
    _description = "Address information including text representation, postcode, and UPRN "

    address_text = StringField(
        display="Address Text",
        description="Flexible field for capturing addresses",
        max_length=None,
    )
    postcode = StringField(display="Postcode", description="The postal code", max_length=None)
    uprn = StringField(
        display="UPRN", description="Unique Property Reference Number", max_length=None
    )


class AdjPremises(SchemaNode):
    _ref = "adj-premises"
    _display = "Adjacent premises"
    _description = "Details of properties next to the development site"

    addresses = SchemaNodeField(
        display="Address",
        description="Address information including text representation, postcode, and UPRN ",
        schema_node_cls=Addresses,
    )


class DescProposedWorks(SchemaNode):
    _ref = "desc-proposed-works"
    _display = "Description of proposed works"
    _description = (
        "Details of development plans such as extensions measurements or work specifications"
    )

    proposed_works_details = StringField(
        display="Proposed works details",
        description="Description of the proposed works including detailed explanation of the work",
        max_length=None,
    )
    extension_depth = StringField(
        display="Extension depth",
        description="How far the extension extends beyond the rear wall, measured externally in metres",
        max_length=None,
    )
    max_extension_height = StringField(
        display="Maximum extension height",
        description="Maximum height of the extension, measured externally from natural ground level in metres",
        max_length=None,
    )
    eaves_height = StringField(
        display="Eaves height",
        description="Height at the eaves of the extension, measured externally from natural ground level in metres",
        max_length=None,
    )


class EligibilityExtension(SchemaNode):
    _ref = "eligibility-extension"
    _display = "Eligibility extension"
    _description = "How a proposal to build an extension meets relevant criteria."

    is_single_storey_extension = BooleanField(
        display="Single storey extension", description="Will the extension be a single storey"
    )
    is_extension_height_over_4m = BooleanField(
        display="Extension height over 4m",
        description="Will the extension exceed 4 metres in height",
    )
    is_dwelling_detached = BooleanField(
        display="Dwelling detached", description="Is the dwelling detached"
    )
    is_extension_beyond_rear_wall = BooleanField(
        display="Extension beyond rear wall",
        description="Will the extension extend beyond the rear wall of the original dwelling",
    )
    extension_length = StringField(
        display="Extension length",
        description="Length of rear extension in metres",
        max_length=None,
    )
    is_within_site_constraints = BooleanField(
        display="Within site constraints",
        description="Is the dwellinghouse within any restricted area",
    )
    site_constraints = EnumField(
        display="Site constraints",
        description="List of specific site constraints that restrict development",
        select_options=[
            EnumOption(
                key="world-heritage-site",
                label="World Heritage Site",
                description="Site of global cultural or natural importance",
            ),
            EnumOption(
                key="national-park",
                label="National Park",
                description="Protected area for natural beauty and recreation",
            ),
            EnumOption(
                key="area-outstanding-natural-beauty",
                label="Area of Outstanding Natural Beauty (AONB)",
                description="Designated for distinctive landscape value",
            ),
            EnumOption(
                key="site-special-scientific-interest",
                label="Site of Special Scientific Interest (SSSI)",
                description="Protected for wildlife, geology, or landform",
            ),
            EnumOption(
                key="national-nature-reserve",
                label="National Nature Reserve",
                description="Important area for wildlife and conservation",
            ),
            EnumOption(
                key="conservation-area",
                label="Conservation Area",
                description="Area designated for historical or architectural significance",
            ),
            EnumOption(
                key="special-area-conservation",
                label="Special Area of Conservation",
                description="Designated under the EU Habitats Directive",
            ),
            EnumOption(
                key="special-protection-area",
                label="Special Protection Area/Ramsar site",
                description="Protected for bird species under the EU Birds Directive",
            ),
            EnumOption(
                key="green-belt",
                label="Green Belt",
                description="Area designated to prevent urban sprawl",
            ),
            EnumOption(
                key="secretary-specified-area",
                label="Secretary of State Protected Area",
                description="",
            ),
            EnumOption(key="the-broads", label="The Broads", description=""),
        ],
    )


class PaExtension(SchemaNode):
    _ref = "pa-extension"
    _display = "Larger Home Extension"
    _description = "Planning application for extension"

    adj_premises = SchemaNodeField(
        display="Adjacent premises",
        description="Details of properties next to the development site",
        schema_node_cls=AdjPremises,
    )
    desc_proposed_works = SchemaNodeField(
        display="Description of proposed works",
        description="Details of development plans such as extensions measurements or work specifications",
        schema_node_cls=DescProposedWorks,
    )
    eligibility_extension = SchemaNodeField(
        display="Eligibility extension",
        description="How a proposal to build an extension meets relevant criteria.",
        schema_node_cls=EligibilityExtension,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )


class DischargeCon(SchemaNode):
    _ref = "discharge-con"
    _display = "Discharge condition"
    _description = (
        "How any conditions imposed as part of being given planning permission will be met"
    )

    description_list = StringField(
        display="Description list",
        description="Description or list of materials/details that are being submitted for approval",
        max_length=None,
    )


class PartDischarge(SchemaNode):
    _ref = "part-discharge"
    _display = "Part discharge"
    _description = "Details of how the applicant is meeting a specific part of a set of conditions made by the planning authority."

    is_discharging_part = BooleanField(
        display="Is discharging part",
        description="Is applicant trying to discharge part of condition?",
    )
    discharging_part_details = StringField(
        display="Discharging part details",
        description="Indicate which part of the condition the application relates to",
        max_length=None,
    )


class ApprovalCondition(SchemaNode):
    _ref = "approval-condition"
    _display = "Approval of details reserved by condition"
    _description = "An application to have conditions approved which have been applied at the time of granting a planning permission to limit and control the way in which the planning permission has been implemented"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    desc_your_proposal = SchemaNodeField(
        display="Description of your proposal",
        description="Written description of the proposed development including any additional relevant details.",
        schema_node_cls=DescYourProposal,
    )
    discharge_con = SchemaNodeField(
        display="Discharge condition",
        description="How any conditions imposed as part of being given planning permission will be met",
        schema_node_cls=DischargeCon,
    )
    part_discharge = SchemaNodeField(
        display="Part discharge",
        description="Details of how the applicant is meeting a specific part of a set of conditions made by the planning authority.",
        schema_node_cls=PartDischarge,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class TreesLocation(SchemaNode):
    _ref = "trees-location"
    _display = "Trees location"
    _description = "Where trees affected by the proposed development are located."

    is_site_different = BooleanField(
        display="Is site different",
        description="Whether the site where trees are located is different from the applicant's address",
    )

    site_locations = SchemaNodeField(
        display="Site location",
        description="Details about the location of a development site, including its boundary, address, and/or coordinates ",
        schema_node_cls=SiteLocations,
    )


class NoticeTreesInConArea(SchemaNode):
    _ref = "notice-trees-in-con-area"
    _display = "Notification of proposed works to trees in a conservation area"
    _description = "Notification, 6 weeks prior to works being carried out, of proposed works to a tree in a conservation area that is not subject to a Tree Preservation order"

    submission_details = SchemaNodeField(
        display="Submission details",
        description="Details about the submitted payload, including reference information, application types, specification profile, destination, documents, and fees ",
        schema_node_cls=SubmissionDetails,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    trees_additional = SchemaNodeField(
        display="Trees additional information",
        description="Further details of any issues relating to trees on the site",
        schema_node_cls=TreesAdditional,
    )
    trees_location = SchemaNodeField(
        display="Trees location",
        description="Where trees affected by the proposed development are located.",
        schema_node_cls=TreesLocation,
    )
    trees_ownership = SchemaNodeField(
        display="Trees ownership",
        description="Who owns any trees affected by the proposed development.",
        schema_node_cls=TreesOwnership,
    )
    tree_work_details = SchemaNodeField(
        display="Identification of tree(s) and description of works",
        description="Details of trees affected by the proposed development and what work is being done to them.",
        schema_node_cls=TreeWorkDetails,
    )


class DescExistingUse(SchemaNode):
    _ref = "desc-existing-use"
    _display = "Description of existing use"
    _description = "How the development site is used, including use class information"

    existing_use_details = SchemaNodeField(
        display="Existing use detail",
        description="Information about a specific existing use on the site, including use class, additional details, and which part of the land it relates to ",
        schema_node_cls=ExistingUseDetails,
    )


class UseWorksActivity(SchemaNode):
    _ref = "use-works-activity"
    _display = "Use works activity"
    _description = "Why a Lawful Development Certificate is required regarding how the development site is being used, or specific works taking place on the site."

    ldc_need = EnumField(
        display="LDC need",
        description="What is the lawful development certificate needed for?",
        select_options=[
            EnumOption(key="existing-use", label="Existing use", description=""),
            EnumOption(
                key="existing-building-work", label="Existing building work", description=""
            ),
            EnumOption(
                key="breach-con-existing-use",
                label="Existing use in breach of condition",
                description="",
            ),
            EnumOption(
                key="breach-con-building-work",
                label="Building work in breach of condition",
                description="",
            ),
            EnumOption(
                key="breach-con-activity", label="Activity in breach of condition", description=""
            ),
        ],
    )
    use = EnumField(
        display="Use",
        description="A use class or type of use",
        select_options=[
            EnumOption(
                key="b2",
                label="B2 – General Industrial",
                description="Industrial uses not falling within Class E.",
            ),
            EnumOption(
                key="b8",
                label="B8 – Storage and Distribution",
                description="Warehousing and storage.",
            ),
            EnumOption(
                key="c1",
                label="C1 – Hotels",
                description="Includes hotels, boarding houses, and guest houses.",
            ),
            EnumOption(
                key="c2",
                label="C2 – Residential Institutions",
                description="Care homes, hospitals, and boarding schools.",
            ),
            EnumOption(
                key="c2a",
                label="C2A – Secure Residential Institutions",
                description="Prisons, young offender institutions.",
            ),
            EnumOption(
                key="c3",
                label="C3 – Dwellinghouses",
                description="Sole or main residence used by people forming a single household.",
            ),
            EnumOption(
                key="c4",
                label="C4 – Houses in multiple occupation",
                description="Defined in the Housing Act 2004 (with the exclusion of converted block of flats).",
            ),
            EnumOption(
                key="e-a",
                label="E(a) – Retail (other than hot food)",
                description="Shops and other retail services.",
            ),
            EnumOption(
                key="e-b",
                label="E(b) – Food and Drink",
                description="Premises mostly for on-site consumption.",
            ),
            EnumOption(
                key="e-c-i",
                label="E(c)(i) – Financial Services",
                description="Banks, building societies, and credit unions.",
            ),
            EnumOption(
                key="e-c-ii",
                label="E(c)(ii) – Professional Services",
                description="Non-health/medical services (e.g., accountants, solicitors).",
            ),
            EnumOption(
                key="e-c-iii",
                label="E(c)(iii) – Any Other Service",
                description="Non-retail services to the public.",
            ),
            EnumOption(
                key="e-d",
                label="E(d) – Indoor Sports and Recreation",
                description="Excludes motorised or firearms activities.",
            ),
            EnumOption(
                key="e-e",
                label="E(e) – Medical or Health Services",
                description="Clinics and health centres.",
            ),
            EnumOption(
                key="e-f",
                label="E(f) – Creche, Day Nursery",
                description="Facilities for childcare.",
            ),
            EnumOption(
                key="e-g-i",
                label="E(g)(i) – Office",
                description="For operational or administrative functions.",
            ),
            EnumOption(
                key="e-g-ii",
                label="E(g)(ii) – Research and Development",
                description="Development of products or processes.",
            ),
            EnumOption(
                key="e-g-iii",
                label="E(g)(iii) – Industrial Process",
                description="Processes that can operate within a residential area.",
            ),
            EnumOption(
                key="f1-a",
                label="F1(a) – Education",
                description="Schools, colleges, and training centres.",
            ),
            EnumOption(
                key="f1-b",
                label="F1(b) – Display of Works of Art",
                description="Galleries (excluding commercial galleries).",
            ),
            EnumOption(key="f1-c", label="F1(c) – Museum", description="Non-commercial museums."),
            EnumOption(
                key="f1-d",
                label="F1(d) – Public Library",
                description="Libraries open to the public.",
            ),
            EnumOption(
                key="f1-e",
                label="F1(e) – Public Hall/Exhibition Hall",
                description="Community spaces for events.",
            ),
            EnumOption(
                key="f1-f",
                label="F1(f) – Public Worship/Religious Instruction",
                description="Churches, mosques, synagogues.",
            ),
            EnumOption(key="f1-g", label="F1(g) – Law Court", description="Court facilities."),
            EnumOption(
                key="f2-a",
                label="F2(a) – Local Community Shop",
                description="Shop under 280 sqm with no similar facility nearby.",
            ),
            EnumOption(
                key="f2-b",
                label="F2(b) – Community Hall",
                description="Halls for local community use.",
            ),
            EnumOption(
                key="f2-c",
                label="F2(c) – Outdoor Sport/Recreation",
                description="Excludes motorised sports.",
            ),
            EnumOption(
                key="f2-d",
                label="F2(d) – Indoor/Outdoor Swimming Pool",
                description="Includes skating rinks.",
            ),
            EnumOption(
                key="sui",
                label="Sui generis",
                description="Uses that do not fall within any defined use class and are considered unique. For example, theatres, nightclubs, scrap yards and mineral extraction",
            ),
            EnumOption(
                key="other",
                label="Other (Please Specify)",
                description="Free text required if selected.",
            ),
        ],
    )
    specified_use = StringField(
        display="Specified use",
        description="A specified use if no applicable use class is available",
        max_length=None,
    )


class SupportingApplications(SchemaNode):
    _ref = "supporting-applications"
    _display = "Supporting applications"
    _description = "Planning permissions, certificates, or notices affecting the application site "

    reference_number = StringField(
        display="Reference number",
        description="Reference number of the planning permission",
        max_length=None,
    )
    condition_number = StringField(
        display="Condition number",
        description="Number of any condition being breached",
        max_length=None,
    )
    decision_date = StringField(
        display="Decision date",
        description="The date when the decision was made, in YYYY-MM-DD format",
        max_length=None,
    )


class GroundsLdc(SchemaNode):
    _ref = "grounds-ldc"
    _display = "Grounds for lawful development certificate"
    _description = (
        "Evidence and explanations relating to a Lawful Development Certificate (LDC) application"
    )

    grounds_pre_2024 = EnumField(
        display="Grounds pre 2024",
        description="List of grounds pre 2024-04-25 under which the certificate is sought",
        select_options=[
            EnumOption(
                key="use-10y",
                label="Use over 10 years ago",
                description="The use began more than 10 years before the date of this application.",
            ),
            EnumOption(
                key="breach-10y",
                label="Breach of condition over 10 years ago",
                description="The use, building works or activity in breach of condition began more than 10 years before the date of this application.",
            ),
            EnumOption(
                key="lawful-change-no-pp",
                label="Lawful change of use within 10 years",
                description="The use began within the last 10 years, as a result of a change of use not requiring planning permission, and there has not been a change of use requiring planning permission in the last 10 years.",
            ),
            EnumOption(
                key="works-complete-4y",
                label="Building works completed over 4 years ago",
                description="The building works (for instance, building or engineering works) were substantially completed more than four years before the date of this application.",
            ),
            EnumOption(
                key="dwelling-change-4y",
                label="Dwelling change of use over 4 years ago",
                description="The change of use to use as a single dwelling house began more than four years before the date of this application.",
            ),
            EnumOption(
                key="other",
                label="Other",
                description="Other – please specify (this might include claims that the change of use or building work was not development, or that it benefited from planning permission granted under the Act or by the General Permitted Development Order).",
            ),
        ],
    )
    grounds_post_2024 = EnumField(
        display="Grounds post 2024",
        description="List of grounds post 2024-04-25 under which the certificate is sought",
        select_options=[
            EnumOption(
                key="use-10y",
                label="Use over 10 years ago",
                description="The use, building works or activity began more than 10 years before the date of this application.",
            ),
            EnumOption(
                key="lawful-change-no-pp",
                label="Lawful change of use within 10 years",
                description="The use began within the last 10 years, as a result of a change of use not requiring planning permission, and there has not been a change of use requiring planning permission in the last 10 years.",
            ),
            EnumOption(
                key="other",
                label="Other",
                description="Other – please specify (this might include claims that the change of use or building work was not development, or that it benefited from planning permission granted under the Act or by the General Permitted Development Order).",
            ),
        ],
    )
    other_details = StringField(
        display="Other details",
        description="Explanation if other ground is selected",
        max_length=None,
    )
    reason = StringField(display="Reason", description="A textual reason", max_length=None)

    supporting_applications = SchemaNodeField(
        display="Supporting applications",
        description="Planning permissions, certificates, or notices affecting the application site ",
        schema_node_cls=SupportingApplications,
    )


class InfoSupportLdc(SchemaNode):
    _ref = "info-support-ldc"
    _display = "Information to support LDC"
    _description = (
        "Supporting information required to make a Lawful Development Certificate application"
    )

    existing_use_start_date = StringField(
        display="Existing use start date",
        description="Date when the existing use of the land or building commenced, in YYYY-MM-DD format",
        max_length=None,
    )
    has_existing_use_interrupted = BooleanField(
        display="Existing use interrupted",
        description="Indicating whether the existing use has been interrupted since it commenced",
    )
    interruption_details = StringField(
        display="Interruption details",
        description="Details of any interruption to the existing use including dates and circumstances",
        max_length=None,
    )
    has_existing_use_changed = BooleanField(
        display="Existing use change",
        description="Indicate whether there has been any change in the existing use since it commenced",
    )
    existing_use_change_details = StringField(
        display="Existing use change details",
        description="Details of any changes to the existing use including nature of changes and dates",
        max_length=None,
    )


class LdcExistingUse(SchemaNode):
    _ref = "ldc-existing-use"
    _display = "LDC Existing Use"
    _description = "Existing use of the site"

    desc_existing_use = SchemaNodeField(
        display="Description of existing use",
        description="How the development site is used, including use class information",
        schema_node_cls=DescExistingUse,
    )
    use_works_activity = SchemaNodeField(
        display="Use works activity",
        description="Why a Lawful Development Certificate is required regarding how the development site is being used, or specific works taking place on the site.",
        schema_node_cls=UseWorksActivity,
    )
    grounds_ldc = SchemaNodeField(
        display="Grounds for lawful development certificate",
        description="Evidence and explanations relating to a Lawful Development Certificate (LDC) application",
        schema_node_cls=GroundsLdc,
    )
    info_support_ldc = SchemaNodeField(
        display="Information to support LDC",
        description="Supporting information required to make a Lawful Development Certificate application",
        schema_node_cls=InfoSupportLdc,
    )
    res_units = SchemaNodeField(
        display="Residential units",
        description="Details of the residential units that make up both the current and proposed development.",
        schema_node_cls=ResUnits,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    interest_details = SchemaNodeField(
        display="Interest details",
        description="Names and contact details for all parties with an interest in the proposed develpoment.",
        schema_node_cls=InterestDetails,
    )
    pre_app_advice = SchemaNodeField(
        display="Pre-application advice",
        description="Details of pre-application advice previously received from the planning authority",
        schema_node_cls=PreAppAdvice,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )
    site_visit = SchemaNodeField(
        display="Site Visit Details",
        description="Information to help the planning authority arrange a site visit",
        schema_node_cls=SiteVisit,
    )


class AgriForestDevElig(SchemaNode):
    _ref = "agri-forest-dev-elig"
    _display = "Agricultural and forestry development eligibility"
    _description = "Information needed to assess agricultural unit, land parcel, agricultural purpose and wider site constraints "

    agri_unit_area = StringField(
        display="Agricultural unit area",
        description="Total area of the entire agricultural unit",
        max_length=None,
    )
    land_parcel_area = EnumField(
        display="Land parcel area",
        description="The size category for a given land parcel",
        select_options=[
            EnumOption(key="1-hec-or-more", label="1 hectare or more", description=""),
            EnumOption(
                key="less-1-more-point4-hec",
                label="Less than 1 hectare but at least 0.4 hectare",
                description="",
            ),
            EnumOption(key="less-point4.hec", label="Less that 0.4 hectare", description=""),
        ],
    )
    agri_start_date = StringField(
        display="Agricultural use start date",
        description="The month and year when the land started being used for agriculture",
        max_length=None,
    )
    is_necessary_for_agri = BooleanField(
        display="Is necessary for agriculture",
        description="Is the proposed development reasonably necessary for the purposes of agriculture?",
    )
    details = StringField(
        display="Details",
        description="Additional details or information about an item",
        max_length=None,
    )
    is_designed_agri = BooleanField(
        display="Is designed for agricultural purposes",
        description="Is the proposed development designed for the purposes of agriculture?",
    )
    design_details = StringField(
        display="Design details",
        description="Additional details or information about design",
        max_length=None,
    )
    dwelling_alteration = BooleanField(
        display="Dwelling alteration",
        description="Whether the proposed development involves any alteration to a dwelling.",
    )
    away_from_road = BooleanField(
        display="Is over 25 metres from road",
        description="Whether the proposed development is more than 25 metres from a metalled part of a trunk or classified road",
    )
    close_to_aerodrome = BooleanField(
        display="Within 3km of aerodrome",
        description="Whether the proposed development is within 3 kilometres of an aerodrome",
    )
    proposed_height = StringField(
        display="Proposed height",
        description="Height once the additional storeys have been added in metres",
        max_length=None,
    )
    affects_heritage = BooleanField(
        display="Affects heritage or nature conservation",
        description="Whether the proposed development would affect local hertiage or nature considerations",
    )
    heritage_nature_impact_details = StringField(
        display="Heritage and nature impact details",
        description="Details of how the proposed development would affect an ancient monument, archaeological site or listed building, or relate to a Site of Special Scientific Interest or local nature reserve.",
        max_length=None,
    )


class ProposedBuildingDetails(SchemaNode):
    _ref = "proposed-building-details"
    _display = "Building details"
    _description = "Details of the building being proposed, extended or altered "

    details = StringField(
        display="Details",
        description="Additional details or information about an item",
        max_length=None,
    )
    building_length = StringField(
        display="Building length",
        description="Length of the building (in metres).",
        max_length=None,
    )
    eaves_height = StringField(
        display="Eaves height",
        description="Height at the eaves of the extension, measured externally from natural ground level in metres",
        max_length=None,
    )
    building_breadth = StringField(
        display="Building breadth",
        description="Breadth of the building (in metres).",
        max_length=None,
    )
    building_ridge_height = StringField(
        display="Building ridge height",
        description="Height to the ridge of the building (in metres).",
        max_length=None,
    )


class ProposedBuilding(SchemaNode):
    _ref = "proposed-building"
    _display = "Agricultural or forestry building details"
    _description = "Details of the proposed agricultural or forestry building, including operation type, dimensions, materials "

    development_operation_types = EnumField(
        display="Development operation types",
        description="The types of building operation included in the agricultural or forestry proposal.",
        select_options=[
            EnumOption(key="new-build", label="A new building", description=""),
            EnumOption(key="extension", label="An extension", description=""),
            EnumOption(key="alteration", label="An alteration", description=""),
        ],
    )
    building_wall_materials = StringField(
        display="Wall materials", description="Details of the wall materials", max_length=None
    )
    building_wall_colour = StringField(
        display="Wall colour", description="Colour of the wall", max_length=None
    )
    building_roof_materials = StringField(
        display="Roof materials", description="Details of the roof materials", max_length=None
    )
    building_roof_colour = StringField(
        display="Roof colour", description="Colour of the roof", max_length=None
    )
    has_agri_building_2_yrs = BooleanField(
        display="Agricultural building built within 2 years",
        description="Whether an agricultural building has been constructed on the agricultural unit within the last two years",
    )
    agri_building_area = StringField(
        display="Agricultural building ground area",
        description="Overall ground area of the agricultural building constructed within the last two years, in square metres",
        max_length=None,
    )
    agri_building_distance = StringField(
        display="Agricultural building distance",
        description="Distance from the recent agricultural building to the proposed new building (in metres)",
        max_length=None,
    )
    house_livestock = BooleanField(
        display="Houses livestock, slurry or sewage sludge",
        description="Whether the proposed building would be used to house livestock, slurry or sewage sludge ",
    )
    livestock_building_400m = BooleanField(
        display="Livestock building distance from homes",
        description="Whether livestock building more than 400 metres from the nearest house, excluding the farmhouse",
    )
    exceeds_threshold = BooleanField(
        display="Exceeds threhold",
        description="Whether the ground area covered by the proposed building exceeds the relevant Part 6 threshold",
    )
    related_work_distance = BooleanField(
        display="Related work distance",
        description="Whether specified related works have been erected within 90 metres of the proposed development within the last two years",
    )
    engineering_operations_threshold = EnumField(
        display="Engineering operations threshold",
        description="Whether engineering operations exceed 1,000 square metres where the agricultural unit is 5 hectares or more",
        select_options=[
            EnumOption(key="yes", label="Yes", description="Affirmative response"),
            EnumOption(key="no", label="No", description="Negative response"),
            EnumOption(
                key="not-applicable",
                label="Not Applicable",
                description="Response not applicable or not provided",
            ),
        ],
    )
    within_scheduled_monument = BooleanField(
        display="Within Scheduled Momument",
        description="Would the erection, extension, or alteration be carried out on land or a building that is, or is within the curtilage of, a scheduled monument",
    )

    proposed_building_details = SchemaNodeField(
        display="Building details",
        description="Details of the building being proposed, extended or altered ",
        schema_node_cls=ProposedBuildingDetails,
    )


class PaBuildAgriForest(SchemaNode):
    _ref = "pa-build-agri-forest"
    _display = "Prior approval: Agricultural or forestry building development"
    _description = (
        "Prior apporval for building development related to agricultural and forestry buildings"
    )

    agri_forest_dev_elig = SchemaNodeField(
        display="Agricultural and forestry development eligibility",
        description="Information needed to assess agricultural unit, land parcel, agricultural purpose and wider site constraints ",
        schema_node_cls=AgriForestDevElig,
    )
    proposed_building = SchemaNodeField(
        display="Agricultural or forestry building details",
        description="Details of the proposed agricultural or forestry building, including operation type, dimensions, materials ",
        schema_node_cls=ProposedBuilding,
    )
    agent_contact = SchemaNodeField(
        display="Agent contact details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentContact,
    )
    agent_details = SchemaNodeField(
        display="Agent details",
        description="Name and contact information if an agent is being used.",
        schema_node_cls=AgentDetails,
    )
    applicant_contact = SchemaNodeField(
        display="Applicant contact details",
        description="Telephone number and email address of the applicant.",
        schema_node_cls=ApplicantContact,
    )
    applicant_details = SchemaNodeField(
        display="Applicant details",
        description="Name and contact information for the parties making the application.",
        schema_node_cls=ApplicantDetails,
    )
    conflict_of_interest = SchemaNodeField(
        display="Conflict of interest",
        description="Details of any conflict of interest that may exist between the applicant and planning authority.",
        schema_node_cls=ConflictOfInterest,
    )
    checklist = SchemaNodeField(
        display="Checklist",
        description="Checking whether all the requirements of the form have been met, such as proof of payment or supporting documentation.",
        schema_node_cls=Checklist,
    )
    declaration = SchemaNodeField(
        display="Declaration",
        description="Signed and dated verification of the application's accuracy.",
        schema_node_cls=Declaration,
    )
    site_details = SchemaNodeField(
        display="Site details",
        description="Where the proposed development will be built.",
        schema_node_cls=SiteDetails,
    )


# list of roots are loaded here so all the processing is done on startup not for each request.
# roots are expected to be planning application nodes
schema_node_roots = schema_node_root_classes()

# convenience ref -> schema map
schema_node_root_mapping = {schema_node._ref: schema_node for schema_node in schema_node_roots}
