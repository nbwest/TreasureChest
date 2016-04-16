from django.contrib import admin

from .models import *


class MemberTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'fee', 'membership_period')


class FeedbackAdmin(admin.ModelAdmin):
    list_display=('id','date','name','page','comment')
    readonly_fields=('id',)


# Admin space lists
admin.site.register(MemberType, MemberTypeAdmin)
admin.site.register(ToyBrand)
admin.site.register(ToyCategory)
admin.site.register(ToyPackaging)
admin.site.register(ToyVendor)
admin.site.register(RecycledToyId)
admin.site.register(TempBorrowList)
admin.site.register(Config)
admin.site.register(Feedback,FeedbackAdmin)

class ToyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'admin_image')
    search_fields = ('code','name' )
    # list_filter = ('code', )
    #readonly_fields = ('member_loaned','due_date','borrow_date','state')

class ToyHistoryAdmin(admin.ModelAdmin):
    list_display=('date_time','toy','event_type','member')

class ChildAdmin(admin.ModelAdmin):
    list_display=('parent','date_of_birth')

class ImageAdmin(admin.ModelAdmin):
    list_display=('file','type','admin_image')

# User space lists
admin.site.register(Member)
admin.site.register(Child,ChildAdmin)
admin.site.register(Toy, ToyAdmin)
admin.site.register(Image, ImageAdmin)

# Issues added when returning or from toy list (stocktake)
# used for toy history
admin.site.register(ToyHistory,ToyHistoryAdmin)

# Added when any transaction occurred, never changed via list
# used for toy or member history via member list display
admin.site.register(Transaction)
