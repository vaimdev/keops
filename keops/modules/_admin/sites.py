
from django.contrib.admin import sites

class AdminSite(sites.AdminSite):
    pass

site = AdminSite()
