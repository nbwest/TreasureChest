from django.contrib import admin

from .models import *

admin.site.register(MemberType)
admin.site.register(ToyBrand)
admin.site.register(Location)

admin.site.register(Toy)
admin.site.register(Member)
