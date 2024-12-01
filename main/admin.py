from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.penumpang)
admin.site.register(models.pemesanan)
admin.site.register(models.detailpemesanan)
admin.site.register(models.bis)
admin.site.register(models.kelaslayanan)
admin.site.register(models.detailkelaslayanan)
admin.site.register(models.layanantambahan)