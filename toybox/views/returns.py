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

 #TODO take into account of half week overdue - leeway for half week
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        #TODO add fee multiplier by weeks late
        context.update(handle_borrowed_toy_list(request, member_id))



    toyList=None
    if "toy_list" in context:
        toyList=context["toy_list"]

    # TODO get this from authentication and transaction register
    #base page context
    context.update({"daily_balance":23.20,"login_name":"Jess Benning"})

    if (request.method == "POST"):
        returns_form = ReturnsForm(request.POST,toyList=toyList)

        if returns_form.is_valid():

            for toy in toyList:
                print(returns_form.cleaned_data['issue_type_'+toy.code])
                print(returns_form.cleaned_data['issue_comment_'+toy.code])
                print(returns_form.cleaned_data['returned_checkbox_'+toy.code])

                # toy.return_toy_with_issue()
                # toy.issue_type=returns_form.cleaned_data['issue_type_'+toy.code]
                # toy.issue_comment=returns_form.cleaned_data['issue_comment_'+toy.code]

                if returns_form.cleaned_data['returned_checkbox_'+toy.code]==True:
                    toy.return_toy(returns_form.cleaned_data['issue_type_'+toy.code],returns_form.cleaned_data['issue_comment_'+toy.code])
                    # toy.return_toy()
                context.pop("toy_list",None)
                context.pop("member",None)




    context.update({"issue_list":Toy.ISSUE_TYPE_CHOICES})#[:IssueChoiceType.RETURNED_MISSING_PIECE]})


    # display toy in toy summary
    # context.update(handle_toy_summary(request))


    context.update(handle_member_search(request))


    returns_form = ReturnsForm(toyList=toyList)



    context.update({"returns_form":returns_form})

    return render(request, 'toybox/returns.html', context)



class ReturnsForm(forms.Form):



    def __init__(self, *args, **kwargs):
        toyList=kwargs.pop("toyList", 0)
        super(ReturnsForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:
                self.fields['returned_checkbox_%s' % toy.code]=forms.BooleanField(required=False)
                self.fields['issue_comment_%s' % toy.code] = forms.CharField(required=False,initial=toy.issue_comment, max_length=ToyHistory._meta.get_field('comment').max_length)
                self.fields['issue_type_%s' % toy.code] = forms.ChoiceField(required=False,initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES)


    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')

    late_fee = forms.CharField(required=False,label="Late Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'visible':'True','readonly':'readonly', 'adjust_button':'True'}))
    issue_fee = forms.CharField( required=False,label="Issue Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'visible':'True','readonly':'readonly','adjust_button':'True'}))
    total = forms.CharField(required=False,label="Total", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True','visible':'True','readonly':'readonly', 'done_button':'True'}))




