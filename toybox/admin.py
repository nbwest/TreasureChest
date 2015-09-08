from django.contrib import admin

from .models import *


class MemberTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'fee', 'membership_period')


class LoanTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'loan_cost', 'loan_deposit')

# Admin space lists
admin.site.register(MemberType, MemberTypeAdmin)
admin.site.register(ToyBrand)
admin.site.register(ToyCategory)
admin.site.register(ToyPackaging)
admin.site.register(LoanType, LoanTypeAdmin)
admin.site.register(TempBorrowList)
admin.site.register(Config)

class ToyAdmin(admin.ModelAdmin):
    list_display = ('code', 'description', 'admin_image')
    #readonly_fields = ('member_loaned','due_date','borrow_date','state')

# User space lists
admin.site.register(Member)
admin.site.register(Child)
admin.site.register(Toy, ToyAdmin)

# Issues added when returning or from toy list (stocktake)
# used for toy history
admin.site.register(Issue)

# Added when any transaction occurred, never changed via list
# used for toy or member history via member list display
admin.site.register(Transaction)
