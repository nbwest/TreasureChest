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
admin.site.register(LoanType,LoanTypeAdmin)


class ToyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'admin_image')

# User space lists
admin.site.register(Member)
admin.site.register(Children)
admin.site.register(Toy, ToyAdmin) # Toy list aviable in user space

# Issues added when returning or from toy list (stocktake)
# used for toy history
admin.site.register(IssuesResister)

# Added when any transaction occured, never changed via list
# used for toy or member history via member list display
admin.site.register(TransactionRegister)


