from django.core.management.base import BaseCommand
# from django.core.management.base import CommandError

import time
import pandas as pd

from ppts.models import DwellingType
from ppts.models import LandUse
from ppts.models import Location
from ppts.models import Planner
from ppts.models import ProjectFeature
from ppts.models import HearingDate
from ppts.models import ProjectDescription
from ppts.models import MCDReferral
from ppts.models import EnvironmentalReview
from ppts.models import Record
from ppts.models import RecordType


class Command(BaseCommand):
    help = 'Imports the PPTS data into the database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.record_types = dict()
        self._planners = dict()
        self._project_descriptions = dict()
        self._mcd_referrals = dict()
        self._environmental_reviews = dict()

    def add_arguments(self, parser):
        parser.add_argument('filename')

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
            if checked and not pd.isnull(checked):
                if (isinstance(checked, str) and
                        checked.lower() == "unchecked" and
                        checked.lower() == "no"):
                    continue
                if col in self._project_descriptions:
                    pds.append(self._project_descriptions[col])
                else:
                    _pd = ProjectDescription(type=col)
                    # print("Creating project decsription %s" % _pd.__dict__)
                    _pd.save()
                    self._project_descriptions[col] = _pd
                    pds.append(_pd)
        return pds

    def mcd(self, row):
        mcd = None
        val = getattr(row, MCDReferral._COL_NAME, "")
        if val and not pd.isnull(val):
            if val in self._mcd_referrals:
                mcd = self._mcd_referrals[val]
            else:
                mcd = MCDReferral(type=val)
                # print("Creating mcd: %s" % mcd.__dict__)
                mcd.save()
                self._mcd_referrals[val] = mcd
        return mcd

    def env(self, row):
        env = None
        val = getattr(row, EnvironmentalReview._COL_NAME, "")
        if val and not pd.isnull(val):
            if val in self._environmental_reviews:
                env = self._environmental_reviews[val]
            else:
                env = EnvironmentalReview(type=val)
                print("Creating env %s" % env.__dict__)
                env.save()
                self._environmental_reviews[val] = env
        return env

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

    def hearing_date(self, row, record):
        hds = []
        for (col, _ignore) in HearingDate.CHOICES:
            val = getattr(row, col, None)  # This should be a date
            if val:
                hds.append(HearingDate(
                    record=record,
                    type=col,
                    date=val))
        return hds

    def pd_date(self, d):
        if pd.isnull(d) or isinstance(d, str):
            return None
        return d

    def handle(self, *args, **options):
        comp_timer = Timer()
        # import ipdb
        # ipdb.set_trace()
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
        hearing_dates = []
        i = -1
        project_description_map = dict()
        for row in data.itertuples():
            i += 1
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
                mcd_referral=self.mcd(row),
                environmental_review=self.env(row),
            )
            project_description_map[i] = self.project_descriptions(row)
            records.append(record)
            dwelling_types.extend(self.dwelling_type(row, record))
            project_features.extend(self.project_feature(row, record))
            land_uses.extend(self.land_use(row, record))
            hearing_dates.extend(self.hearing_date(row, record))
            if len(records) > 100:
                Record.objects.bulk_create(records)
                rpis = []
                for (rid, pds) in project_description_map.items():
                    for pdi in pds:
                        rpis.append(Record.project_description.through(
                            projectdescription_id=pdi.pk,
                            record_id=rid))
                Record.project_description.through.objects.bulk_create(rpis)
                DwellingType.objects.bulk_create(dwelling_types)
                ProjectFeature.objects.bulk_create(project_features)
                LandUse.objects.bulk_create(land_uses)
                HearingDate.objects.bulk_create(hearing_dates)
                records = []
                dwelling_types = []
                project_features = []
                land_uses = []
                hearing_dates = []

        Record.objects.bulk_create(records)
        rpis = []
        for (rid, pds) in project_description_map.items():
            for pdi in pds:
                rpis.append(Record.project_description.through(
                    projectdescription_id=pdi.pk,
                    record_id=rid))
        Record.project_description.through.objects.bulk_create(rpis)
        DwellingType.objects.bulk_create(dwelling_types)
        ProjectFeature.objects.bulk_create(project_features)
        LandUse.objects.bulk_create(land_uses)
        HearingDate.objects.bulk_create(hearing_dates)
        records = []
        dwelling_types = []
        project_features = []
        land_uses = []
        hearing_dates = []

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