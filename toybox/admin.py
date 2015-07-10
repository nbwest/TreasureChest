from django.contrib import admin

from .models import *


class MemberTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'fee', 'membership_period')


class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'loan_period', 'loan_cost', 'loan_deposit', 'member_type')

# Admin space lists
admin.site.register(MemberType, MemberTypeAdmin)
admin.site.register(ToyBrand)
admin.site.register(ToyCategory)
admin.site.register(ToyPackaging)
admin.site.register(LoanType, LoanTypeAdmin)


class ToyAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'admin_image')

# User space lists
admin.site.register(Member)
admin.site.register(Child)
admin.site.register(Toy, ToyAdmin)  # Toy list available in user space

# Issues added when returning or from toy list (stocktake)
# used for toy history
admin.site.register(Issue)

# Added when any transaction occurred, never changed via list
# used for toy or member history via member list display
admin.site.register(Transaction)
