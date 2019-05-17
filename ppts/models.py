from django.db import models


class Location(models.Model):
    id = models.IntegerField(help_text="Primary Key", primary_key=True)
    the_geom = models.TextField(
        help_text="Polygon defining the parcel.")  # TODO: GIS support
    shape_length = models.DecimalField(
        max_digits=15,
        decimal_places=8,
        help_text="Perimeter of polygon",
        null=True)
    shape_area = models.DecimalField(
        max_digits=15,
        decimal_places=15,
        help_text="Area of polygon",
        null=True)
    address = models.CharField(
        max_length=250,
        help_text=("An address for this location. The format of these is "
                   "extremely inconsistent, and sometimes a single parcel "
                   "actually has two addresses."))


class Planner(models.Model):
    planner_id = models.CharField(
        max_length=100,
        help_text=("ID of planner as provided in original data. "
                   "Looks like a user login id"))
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)


class RecordType(models.Model):
    category = models.CharField(
        max_length=100,
        help_text=("3-letter acronym for the record type (e.g. PRJ, PRL, "
                   "ENV).  There are 63 types."),
        primary_key=True)
    name = models.CharField(
        max_length=100,
        help_text=("Expansion of the 3-letter acronym (e.g. PRJ, PRL, ENV). "
                   "There are 63 types."))
    subtype = models.CharField(
        max_length=100,
        help_text=("One of 17 subcategories of records (e.g. Environmental, "
                   "Referrals, Legislation)"))
    type = models.CharField(
        max_length=100,
        help_text=("One of 5 categories of records (e.g. Applications, "
                   "Projects)"))
    group = models.CharField(
        max_length=100,
        help_text=("In this data, always \"planning\", but hypothetically we "
                   "could add data from other departments to the database"))
    module = models.CharField(
        max_length=100,
        help_text=("City department that owns the record. In this data, "
                   "always \"planning\"."))


class ProjectDescription(models.Model):
    """Project Description

    Note that MCD_REFERRAL and ENVIRONMENTAL_REVIEW_TYPE are not boolean
    fields, they are categorical and get their own special case extra info.

    For people new to Django, this looks weird. But it's how you make a
    multiple-choice ENUM field.
    See https://docs.djangoproject.com/en/2.2/ref/models/fields/#choices
    """
    ADDITIONS = "ADDITIONS"
    ADU = "ADU"
    AFFORDABLE_UNITS = "AFFORDABLE_UNITS"
    CHANGE_OF_USE = "CHANGE_OF_USE"
    DEMOLITION = "DEMOLITION"
    #ENVIRONMENTAL_REVIEW_TYPE = "ENVIRONMENTAL_REVIEW_TYPE"
    FACADE_ALT = "FACADE_ALT"
    FINANCIAL = "FINANCIAL"
    FORMULA_RETAIL = "FORMULA_RETAIL"
    INCLUSIONARY = "INCLUSIONARY"
    LEG_ZONE_CHANGE = "LEG_ZONE_CHANGE"
    LOT_LINE_ADJUST = "LOT_LINE_ADJUST"
    MASSAGE = "MASSAGE"
    MCD = "MCD"
    #MCD_REFERRAL = "MCD_REFERRAL"
    NEW_CONSTRUCTION = "NEW_CONSTRUCTION"
    OTHER_NON_RES = "OTHER_NON_RES"
    OTHER_PRJ_DESC = "OTHER_PRJ_DESC"
    ROW_IMPROVE = "ROW_IMPROVE"
    SENIOR = "SENIOR"
    SPECIAL_NEEDS = "SPECIAL_NEEDS"
    STATE_DENSITY_BONUS = "STATE_DENSITY_BONUS"
    STUDENT = "STUDENT"
    TOBACCO = "TOBACCO"

    CHOICES = (
        (ADDITIONS, 'Additions'),
        (ADU, 'Accessory Dwelling Unit'),
        (AFFORDABLE_UNITS, '100% Affordable Housing'),
        (CHANGE_OF_USE, 'Change of Use'),
        (DEMOLITION, 'Demolition'),
        #(ENVIRONMENTAL_REVIEW_TYPE, 'Environmental Review'),
        (FACADE_ALT, 'Facade Alterations'),
        (FINANCIAL, 'Financial Services'),
        (FORMULA_RETAIL, 'Formula Retail'),
        (INCLUSIONARY, 'Inclusionary Housing Required'),
        (LEG_ZONE_CHANGE, 'Legislative/Zoning Change'),
        (LOT_LINE_ADJUST, 'Lot Line Adjustment-Subdivision'),
        (MASSAGE, 'Massage Establishment'),
        (MCD, 'Medical Cannabis Dispensary'),
        #(MCD_REFERRAL, 'Public Health Review - MCD'),
        (NEW_CONSTRUCTION, 'New Construction'),
        (OTHER_NON_RES, 'Non-Residential Use Type - Other'),
        (OTHER_PRJ_DESC, 'Other'),
        (ROW_IMPROVE, 'ROW Improvements'),
        (SENIOR, 'Senior Housing'),
        (SPECIAL_NEEDS, 'Special Needs Housing'),
        (STATE_DENSITY_BONUS, 'State Density Bonus'),
        (STUDENT, 'Student Housing'),
        (TOBACCO, 'Tobacco Paraphernalia Est'),
    )

    type = models.CharField(
        max_length=50,
        choices=CHOICES,
        primary_key=True)


class Record(models.Model):
    id = models.IntegerField(help_text="Primary Key", primary_key=True)
    planner = models.ForeignKey(Planner, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True)
    record_type = models.ForeignKey(
        RecordType, on_delete=models.SET_NULL, null=True)
    record_id = models.CharField(
        max_length=100,
        help_text="Planning Department unique identifier for the record")
    
    parent = models.ManyToManyField(
        "self",
        related_name="child",
        help_text="The parent/child relationship for related records.")

    object_id = models.IntegerField(
        help_text="Esri ArcGIS system ID",
        null=True)
    template_id = models.CharField(
        max_length=100, help_text="Unique system identifier for the record")
    name = models.CharField(
        max_length=100,
        help_text="Title of record as provided haphazardly by applicant")
    description = models.TextField(
        help_text=("Long description of record as provided haphazardly by "
                   "applicant"))
    status = models.CharField(
        max_length=100,
        help_text="Current status (e.g. open, closed, accepted, rejected)")
    construct_cost = models.FloatField(
        help_text="Estimated construction cost in dollars of the project",
        null=True)
    related_building_permit = models.CharField(
        max_length=100,
        help_text="Related Building Permit Number")
    acalink = models.TextField(
        help_text="Link to this record in Accela Citizen Access")
    aalink = models.TextField(
        help_text="Link to this record in Accela Automation")
    date_opened = models.DateField("Date record was opened", null=True)
    date_closed = models.DateField("Date record was closed", null=True)

    project_description = models.ManyToManyField(
        ProjectDescription,
        help_text="Checkboxes describing type of project")
    mcd_referral = models.CharField(
        max_length=150,
        help_text="Medical Cannabis Dispensary referral",
        blank=True,
        null=True)
    environmental_review = models.CharField(
        max_length=150,
        help_text="Environmental Review type",
        blank=True,
        null=True)
    # I think some other relations are missing still
    
    bos_1st_read = models.DateField(
        help_text="Full Board Hearing Date, First",
        null=True)
    bos_2nd_read = models.DateField(
        help_text="Full Board Hearing Date, Second",
        null=True)
    com_hearing = models.DateField(
        help_text="Committee Hearing Date",
        null=True)
    mayoral_sign = models.DateField(
        help_text="Mayoral Action - Ordinance Signed Date",
        null=True)
    transmit_date_bos = models.DateField(
        help_text="Materials Hearing to BOS Clerk Date",
        null=True)
    com_hearing_date_bos = models.DateField(
        help_text="Committee Hearing Date - BOS Review",
        null=True)


class LandUse(models.Model):
    RC = "RC"
    RESIDENTIAL = "RESIDENTIAL"
    CIE = "CIE"
    PDR = "PDR"
    OFFICE = "OFFICE"
    MEDICAL = "MEDICAL"
    VISITOR = "VISITOR"
    PARKING_SPACES = "PARKING_SPACES"

    CHOICES = (
        (RC, 'Retail/Commercial (sq ft)'),
        (RESIDENTIAL, 'Residential (sq ft)'),
        (CIE, 'CIE (Cultural, Institutional, Educational)'),
        (PDR, 'Industrial-PDR (sq ft)'),
        (OFFICE, 'Office (sq ft)'),
        (MEDICAL, 'Medical (sq ft)'),
        (VISITOR, 'Visitor (sq ft)'),
        (PARKING_SPACES, 'Parking Spaces (sq ft)'),
    )
    record = models.ForeignKey(Record, on_delete=models.SET_NULL, null=True)
    type = models.CharField(max_length=20, choices=CHOICES)
    exist = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Existing amount",
        null=True)
    proposed = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Proposed amount",
        null=True)
    net = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Net change",
        null=True)


class ProjectFeature(models.Model):
    AFFORDABLE = "AFFORDABLE"
    HOTEL_ROOMS = "HOTEL_ROOMS"
    MARKET_RATE = "MARKET_RATE"
    BUILD = "BUILD"
    STORIES = "STORIES"
    PARKING = "PARKING"
    LOADING = "LOADING"
    BIKE = "BIKE"
    CAR_SHARE = "CAR_SHARE"
    USABLE = "USABLE"
    PUBLIC = "PUBLIC"
    ART = "ART"
    ROOF = "ROOF"
    SOLAR = "SOLAR"
    LIVING = "LIVING"
    OTHER = "OTHER"
    CHOICES = (
        (AFFORDABLE, 'Dwelling Units-Affordable, Units'),
        (HOTEL_ROOMS, 'Hotel Rooms'),
        (MARKET_RATE, 'Dwelling Units-Market Rate, Units'),
        (BUILD, 'Building Number'),
        (STORIES, 'Stories Number'),
        (PARKING, 'Parking Spaces'),
        (LOADING, 'Loading Spaces'),
        (BIKE, 'Bicycle Spaces'),
        (CAR_SHARE, 'Car Share Spaces'),
        (USABLE, 'Usable Open Spaces'),
        (PUBLIC, 'Public Open Space'),
        (ART, 'Public Art'),
        (ROOF, 'Better Roof - Total Roof Area'),
        (SOLAR, 'Better Roof - Solar Area'),
        (LIVING, 'Better Roof - Living Roof Area'),
        (OTHER, 'Other Project Feature'),
    )
    record = models.ForeignKey(Record, on_delete=models.SET_NULL, null=True)
    type = models.CharField(
        max_length=50,
        choices=CHOICES)
    other_name = models.CharField(
        max_length=250,
        blank=True,
        help_text="The \"other\" project type has a manually-input name.")
    exist = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Existing amount",
        null=True)
    proposed = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Proposed amount",
        null=True)
    net = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Net change",
        null=True)


class DwellingType(models.Model):
    ADU_1BR = "ADU_1BR"
    ADU_2BR = "ADU_2BR"
    ADU_3BR = "ADU_3BR"
    ADU_STUDIO = "ADU_STUDIO"
    BR_1 = "BR_1"
    BR_2 = "BR_2"
    BR_3 = "BR_3"
    GH_BEDS = "GH_BEDS"
    GH_ROOMS = "GH_ROOMS"
    MICRO = "MICRO"
    SRO = "SRO"
    STUDIO = "STUDIO"

    CHOICES = (
        (ADU_1BR, 'Accessory Dwelling Unit 1 Bedroom, Units'),
        (ADU_2BR, 'Accessory Dwelling Unit 2 Bedroom, Units'),
        (ADU_3BR, 'Accessory Dwelling Unit 3+ Bedroom, Units'),
        (ADU_STUDIO, 'Accessory Dwelling Unit Studio, Units'),
        (BR_1, '1 Bedroom, Units'),
        (BR_2, '2 Bedroom, Units'),
        (BR_3, '3+ Bedroom, Units'),
        (GH_BEDS, 'Group Housing, Beds'),
        (GH_ROOMS, 'Group Housing, Rooms'),
        (MICRO, 'Micro, Units'),
        (SRO, 'SRO, Units'),
        (STUDIO, 'Studios, Units'),
    )
    record = models.ForeignKey(Record, on_delete=models.SET_NULL, null=True)
    type = models.CharField(
        max_length=50,
        choices=CHOICES)
    exist = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Existing amount",
        null=True)
    proposed = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Proposed amount",
        null=True)
    net = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Net change",
        null=True)
    area = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Area (optional)",
        blank=True,
        null=True)
