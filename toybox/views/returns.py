from django.shortcuts import render
from shared import *
from django.core.validators import *
from django.forms.formsets import formset_factory

def handle_returns(request,member_id):
    context={}

    context.update(handle_member_search(request))

    if (request.method == "GET"):
        if (member_id):
            context.update(handle_member_summary(request, member_id))

    return context


def returns(request, member_id=None):

    context= handle_returns(request,member_id)

    # TODO get this from authentication and transaction register
    #base page context
    context.update({"daily_balance":23.20,"login_name":"Jess Benning"})

    if (request.method == "POST"):
        for key, value in request.POST.iteritems():
            if key.startswith("returned_checkbox_"):
                toy = get_object_or_404(Toy, code=value)
                toy.return_toy()




    context.update({"issue_list":Toy.ISSUE_TYPE_CHOICES})#[:IssueChoiceType.RETURNED_MISSING_PIECE]})

    #TODO take into account of half week overdue - leeway for half week
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        #TODO add fee multiplier by weeks late
        context.update(handle_borrowed_toy_list(request, member_id))

    # display toy in toy summary
    # context.update(handle_toy_summary(request))


    context.update(handle_member_search(request))


    # returns_table_form = formset_factory(ReturnsTableForm, extra=context["toy_list"].count())
    # context.update({"returns_form":returns_table_form})state
    #
    # initial_toys={}
    # for toy in context['toy_list']:
    #      initial_toys.update({'issue_comment_%s' % toy.code:toy.issue_comment})
    #      initial_toys.update({'issue_type_%s' % toy.code:toy.issue_type})
    # #, initial={'issue_comment':[o.issue_comment for o in context["toy_list"]]}
    #
    # initial_toys.update({'late_fee':234})

    toyList=None
    if "toy_list" in context:
        toyList=context["toy_list"]


    returns_form = ReturnsForm(toyList, initial={'issue_fee':12})#,initial=initial_toys)



    context.update({"returns_form":returns_form})

    return render(request, 'toybox/returns.html', context)

# class ReturnsTableForm(forms.Form):
#     returned = forms.BooleanField()
#
#
#     def __init__(self, field_qty, *args, **kwargs):
#         super(ReturnsTableForm, self).__init__(*args, **kwargs)
#         for if not user.is_authenticated():
#             self.fields['captcha'] = CaptchaField()

#             comment = forms.CharField(max_length=ToyHistory._meta.get_field('comment').max_length)
#             issue_type=forms.ChoiceField(choices=Toy.ISSUE_TYPE_CHOICES)#[:IssueChoiceType.RETURNED_MISSING_PIECE])


class ReturnsForm(forms.Form):

#INITIAL DATA NOT WORKING AT ALL

    def __init__(self,toyList, *args, **kwargs):
        #toyList=kwargs.pop("toyList", 0)
        super(ReturnsForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:

                self.fields['issue_comment_%s' % toy.code] = forms.CharField(initial=toy.issue_comment, max_length=ToyHistory._meta.get_field('comment').max_length)
                self.fields['issue_type_%s' % toy.code] = forms.ChoiceField(initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES)

    # issue_comment = forms.CharField(widget=forms.MultipleHiddenInput(), max_length=ToyHistory._meta.get_field('comment').max_length)
    # issue_type=forms.ChoiceField(widget=forms.MultipleHiddenInput(),choices=Toy.ISSUE_TYPE_CHOICES)#[:IssueChoiceType.RETURNED_MISSING_PIECE])

    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')

    late_fee = forms.CharField(required=False,label="Late Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'visible':'True','readonly':'readonly', 'adjust_button':'True'}))
    issue_fee = forms.CharField( required=False,label="Issue Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'visible':'True','readonly':'readonly','adjust_button':'True'}))
    total = forms.CharField(required=False,label="Total", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True','visible':'True','readonly':'readonly', 'done_button':'True'}))




