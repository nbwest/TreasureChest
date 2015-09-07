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




    context.update({"issue_list":IssueChoiceType.ISSUE_TYPE_CHOICES[:IssueChoiceType.RETURNED_MISSING_PIECE]})

    if (member_id):
        context.update(handle_member_summary(request, member_id))
        #TODO add fee multiplier by weeks late
        context.update(handle_borrowed_toy_list(request, member_id))

    # display toy in toy summary
    context.update(handle_toy_summary(request))

    context.update(handle_member_search(request))


    # returns_table_form = formset_factory(ReturnsTableForm, extra=context["toy_list"].count())
    # context.update({"returns_form":returns_table_form})
    #
    # returns_fee_due_form=ReturnsFeeDueForm(request.POST)
    # context.update({"fee_due_form":returns_fee_due_form})

    return render(request, 'toybox/returns.html', context)

class ReturnsTableForm(forms.Form):
    returned = forms.BooleanField()
    comment = forms.CharField(max_length=Issue._meta.get_field('comment').max_length)
    issue_type=forms.ChoiceField(choices=IssueChoiceType.ISSUE_TYPE_CHOICES[:IssueChoiceType.RETURNED_MISSING_PIECE])


class ReturnsFeeDueForm(forms.Form):
    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')
    fee_due = forms.CharField(label="Fee Due", max_length=20, validators=[numeric])



