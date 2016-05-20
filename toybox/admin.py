from django.contrib import admin

from .models import *
from django import forms

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
admin.site.register(TempBorrowList) #to hide
admin.site.register(Feedback,FeedbackAdmin)

class ToyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'admin_image')
    search_fields = ('code','name' )

    #readonly_fields = ('member_loaned','due_date','borrow_date','state')

class ToyHistoryAdmin(admin.ModelAdmin):
    list_display=('date_time','toy','event_type','member')

class ChildAdmin(admin.ModelAdmin):
    list_display=('parent','date_of_birth')

class ImageAdmin(admin.ModelAdmin):
    list_display=('file','type','admin_image')

class MemberAdmin(admin.ModelAdmin):
    readonly_fields = ('membership_end_date',)

# User space lists
admin.site.register(Member, MemberAdmin)
admin.site.register(Child,ChildAdmin)
admin.site.register(Toy, ToyAdmin)
admin.site.register(Image, ImageAdmin)

# Issues added when returning or from toy list (stocktake)
# used for toy history
admin.site.register(ToyHistory,ToyHistoryAdmin)

# Added when any transaction occurred, never changed via list
# used for toy or member history via member list display
admin.site.register(Transaction)



class ConfigForm(forms.ModelForm):


    def clean(self):

        false_set=set(["0","no","n","false"])
        true_set=set(["1","yes","y","true"])

        value=self.cleaned_data.get('value').lower()
        value_type=self.cleaned_data.get('value_type')

        if value_type == Config.NUMBER:
            try:
                Decimal(value)
            except:
                raise forms.ValidationError('Value "'+value+'" is not type "'+Config.CONFIG_TYPES[value_type][1]+'"')


        elif value_type == Config.BOOLEAN:
            if (value not in true_set) and (value not in false_set):
                raise forms.ValidationError('Value "'+value+'" is not type "'+Config.CONFIG_TYPES[value_type][1]+'"')


        elif value_type != Config.STRING:
            raise forms.ValidationError("Invalid type")


        return self.cleaned_data

    class Meta:
        fields = '__all__'
        model = Config

class ConfigAdmin(admin.ModelAdmin):
    form = ConfigForm
    list_display = ('key', 'value', 'value_type', 'help')

admin.site.register(Config, ConfigAdmin)