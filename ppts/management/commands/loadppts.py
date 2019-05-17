from django.core.management.base import BaseCommand
# from django.core.management.base import CommandError

import time
import pandas as pd

from ppts.models import DwellingType
from ppts.models import LandUse
from ppts.models import Location
from ppts.models import Planner
from ppts.models import ProjectFeature
from ppts.models import ProjectDescription
from ppts.models import Record
from ppts.models import RecordType


class Command(BaseCommand):
    help = """Imports the PPTS data into the database.

Run like: rm db.sqlite3 && \
    python manage.py migrate && \
    python manage.py loadppts /path/to/ppts.csv
"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.record_types = dict()
        self._planners = dict()
        self._project_descriptions = dict()

    def add_arguments(self, parser):
        parser.add_argument('filename')

    def pd_date(self, d):
        #TODO: replace this when I remove pandas
        if pd.isnull(d) or isinstance(d, str):
            return None
        return d

    def make_enum(self, obj):
        d = dict()
        for (col, _ignore) in obj.CHOICES:
            d[col] = obj.objects.create(type=col)
        return d

    def record_type(self, row):
        # TODO: clean the data, as in Tristan's script
        if row.record_type_category in self.record_types:
            rt = self.record_types[row.record_type_category]
        else:
            rt = RecordType(
                category=row.record_type_category,
                name=row.record_type,
                subtype=row.record_type_subtype,
                type=row.record_type_type,
                group=row.record_type_group,
                module=row.module)
            # print("Creating %s" % rt.__dict__)
            rt.save()
            self.record_types[row.record_type_category] = rt
        return rt

    def planner(self, row):
        if row.planner_id in self._planners:
            planner = self._planners[row.planner_id]
        else:
            planner = Planner.objects.create(
                planner_id=row.planner_id,
                name=row.planner_name,
                email=row.planner_email,
                phone=row.planner_phone)
            self._planners[row.planner_id] = planner
        return planner

    def location(self, row):
        #TODO: make this into a proper one-to-many relationship, similar to planner
        return Location(
            the_geom=row.the_geom,
            shape_length=row.Shape_Length,
            shape_area=row.Shape_Area,
            address=row.address)

    def project_descriptions(self, row):
        # The choices on ProjectDescription are the column names in the
        # original data
        pds = []
        for (col, _ignore) in ProjectDescription.CHOICES:
            checked = getattr(row, col, False)
            #TODO: replace this when I remove pandas
            if checked and not pd.isnull(checked):
                if (isinstance(checked, str) and
                        checked.lower() == "unchecked" and
                        checked.lower() == "no"):
                    continue
                pds.append(self._project_descriptions[col])
        return pds

    def dwelling_type(self, row, record):
        prefix = "RESIDENTIAL"
        dts = []
        for (infix, _ignore) in DwellingType.CHOICES:
            exist = getattr(row, "_".join([prefix, infix, "EXIST"]), 0)
            prop = getattr(row, "_".join([prefix, infix, "PROP"]), 0)
            net = getattr(row, "_".join([prefix, infix, "NET"]), 0)
            area = getattr(row, "_".join([prefix, infix, "AREA"]), 0)
            if any([exist, prop, net, area]):
                dts.append(DwellingType(
                    record=record,
                    type=infix,
                    exist=exist,
                    proposed=prop,
                    net=net,
                    area=area))
        return dts

    def project_feature(self, row, record):
        prefix = "PRJ_FEATURE"
        pfs = []
        for (infix, _ignore) in ProjectFeature.CHOICES:
            other_name = ""
            if infix == ProjectFeature.OTHER:
                other_name = getattr(row, "_".join([prefix, infix]), "")
            exist = getattr(row, "_".join([prefix, infix, "EXIST"]), 0)
            prop = getattr(row, "_".join([prefix, infix, "PROP"]), 0)
            net = getattr(row, "_".join([prefix, infix, "NET"]), 0)
            # TODO: cleanup related to the empty PROP columns
            if any([exist, prop, net, other_name]):
                pfs.append(ProjectFeature(
                    record=record,
                    type=infix,
                    other_name=other_name,
                    exist=exist,
                    proposed=prop,
                    net=net))
        return pfs

    def land_use(self, row, record):
        prefix = "LAND_USE"
        lus = []
        for (infix, _ignore) in LandUse.CHOICES:
            exist = getattr(row, "_".join([prefix, infix, "EXIST"]), 0)
            prop = getattr(row, "_".join([prefix, infix, "PROP"]), 0)
            net = getattr(row, "_".join([prefix, infix, "NET"]), 0)
            if any([exist, prop, net]):
                lus.append(LandUse(
                    record=record,
                    type=infix,
                    exist=exist,
                    proposed=prop,
                    net=net))
        return lus

    def handle(self, *args, **options):
        comp_timer = Timer()
        # import ipdb
        # ipdb.set_trace()
        self._project_descriptions = self.make_enum(ProjectDescription)
        #TODO: remove use of pandas, and read files line by line
        data = pd.read_csv(
            options['filename'],
            parse_dates=[
                "date_opened",
                "date_closed",
                "BOS_1ST_READ",
                "BOS_2ND_READ",
                "COM_HEARING",
                "MAYORAL_SIGN",
                "TRANSMIT_DATE_BOS",
                "COM_HEARING_DATE_BOS",
            ],
            infer_datetime_format=True)
        records = []
        dwelling_types = []
        project_features = []
        land_uses = []
        i = -1
        project_description_map = dict()
        print("Creating %d rows" % len(data))
        for row in data.itertuples():
            i += 1
            if i % 1000 == 0:
                print(i)
            record = Record(
                id=i,
                planner=self.planner(row),
                location=self.location(row),
                record_type=self.record_type(row),
                record_id=row.record_id,
                # TODO: parent=
                object_id=row.OBJECTID,
                template_id=row.templateid,
                name=row.record_name,
                description=row.description,
                status=row.record_status,
                construct_cost=row.constructcost,
                related_building_permit=row.RELATED_BUILDING_PERMIT,
                acalink=row.acalink,
                aalink=row.aalink,
                date_opened=self.pd_date(row.date_opened),
                date_closed=self.pd_date(row.date_closed),
                bos_1st_read=self.pd_date(row.BOS_1ST_READ),
                bos_2nd_read=self.pd_date(row.BOS_2ND_READ),
                com_hearing=self.pd_date(row.COM_HEARING),
                mayoral_sign=self.pd_date(row.MAYORAL_SIGN),
                transmit_date_bos=self.pd_date(row.TRANSMIT_DATE_BOS),
                com_hearing_date_bos=self.pd_date(row.COM_HEARING_DATE_BOS),
                mcd_referral=row.MCD_REFERRAL,
                environmental_review=row.ENVIRONMENTAL_REVIEW_TYPE,
            )
            project_description_map[i] = self.project_descriptions(row)
            records.append(record)
            dwelling_types.extend(self.dwelling_type(row, record))
            project_features.extend(self.project_feature(row, record))
            land_uses.extend(self.land_use(row, record))
            if len(records) > 10000:
                Record.objects.bulk_create(records)
                rpis = []
                for (rid, pds) in project_description_map.items():
                    for pdi in pds:
                        rpis.append(Record.project_description.through(
                            projectdescription_id=pdi.pk,
                            record_id=rid))
                Record.project_description.through.objects.bulk_create(rpis)
                project_description_map = dict()
                DwellingType.objects.bulk_create(dwelling_types)
                ProjectFeature.objects.bulk_create(project_features)
                LandUse.objects.bulk_create(land_uses)
                records = []
                dwelling_types = []
                project_features = []
                land_uses = []
            #early abort for testing purposes
            #if len(records) > 1000:
            #    break
        
        #TODO: Fix the bulk create because I don't think it's working right now.
        Record.objects.bulk_create(records)
        rpis = []
        for (rid, pds) in project_description_map.items():
            for pdi in pds:
                rpis.append(Record.project_description.through(
                    projectdescription_id=pdi.pk,
                    record_id=rid))
        Record.project_description.through.objects.bulk_create(rpis)
        project_description_map = dict()
        DwellingType.objects.bulk_create(dwelling_types)
        ProjectFeature.objects.bulk_create(project_features)
        LandUse.objects.bulk_create(land_uses)
        records = []
        dwelling_types = []
        project_features = []
        land_uses = []

        comp_timer.printreport()


# quick timer class for debugging computation time
class Timer():
    def __init__(self, start=True):
        self.paused = True
        self.runtime = 0
        if start:
            self.start()

    def pause(self):
        if(not self.paused):
            self.runtime += (time.time() - self.checkpoint)/60
            self.paused = True

    def start(self):
        if(self.paused):
            self.checkpoint = time.time()
            self.paused = False

    def report(self):
        self.pause()
        return self.runtime

    def printreport(self):
        print('Time passed: %.2f min' % self.report())

    def restart(self):
        self.pause()
        self.runtime = 0
        self.start()
