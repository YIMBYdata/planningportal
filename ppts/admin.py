from django.contrib import admin

from ppts.models import DwellingType
from ppts.models import LandUse
from ppts.models import Location
from ppts.models import Planner
from ppts.models import ProjectFeature
from ppts.models import ProjectDescription
from ppts.models import Record
from ppts.models import RecordType

admin.site.register(DwellingType)
admin.site.register(LandUse)
admin.site.register(Location)
admin.site.register(Planner)
admin.site.register(ProjectFeature)
admin.site.register(ProjectDescription)
admin.site.register(Record)
admin.site.register(RecordType)