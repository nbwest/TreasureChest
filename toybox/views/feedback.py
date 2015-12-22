from django.shortcuts import render
from shared import *
from django.forms import ModelForm

def feedback(request):
    context={}

    form=FeedbackForm()
    context.update({"feedback_form":form})


    if (request.method == "POST"):
        form = FeedbackForm(request.POST)

        if form.is_valid():
            Feedback.objects.create(**form.cleaned_data)
            form=FeedbackForm()

        context.update({"feedback_form":form})
        #TODO export to CSV?
        # https://docs.djangoproject.com/en/1.9/howto/outputting-csv/


    return render(request, 'toybox/feedback.html', context)



class FeedbackForm(forms.Form):
    # date_time = forms.DateField(required=False)
    volunteer_reporting = forms.ModelChoiceField(queryset=Member.objects.filter(volunteer=True))
    page = forms.ChoiceField(choices=Feedback.PAGE_CHOICES)
    comment=forms.CharField(widget=forms.Textarea, max_length=Feedback._meta.get_field('comment').max_length)

