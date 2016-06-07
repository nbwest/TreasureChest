from django.shortcuts import render
from shared import *
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required

@login_required
def feedback(request):
    context = {"title":"Feedback"}

    context.update(base_data(request))

    form=FeedbackForm()
    context.update({"feedback_form":form})

    feedback_list=Feedback.objects.all()

    context.update({"feedback":feedback_list})


    if (request.method == "POST"):
        form = FeedbackForm(request.POST)

        if form.is_valid():
            feedback=Feedback.objects.create(**form.cleaned_data)

            if request.user.first_name:
                feedback.name=request.user.first_name+" "+request.user.last_name
            else:
                feedback.name=request.user.username

            feedback.save()
            form=FeedbackForm()

        context.update({"feedback_form":form})
        #TODO export to CSV?
        # https://docs.djangoproject.com/en/1.9/howto/outputting-csv/


    return render(request, 'toybox/feedback.html', context)



class FeedbackForm(forms.Form):

    page = forms.ChoiceField(choices=Feedback.PAGE_CHOICES)
    comment=forms.CharField(widget=forms.Textarea, max_length=Feedback._meta.get_field('comment').max_length)

