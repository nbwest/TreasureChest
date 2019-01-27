
from toybox.models import *
from django import forms
from django.shortcuts import get_object_or_404
from shared import get_config
from django.template.loader import render_to_string
from django.shortcuts import HttpResponse
from django.template import RequestContext
from django.core.validators import *

def handle_toy_edit(request, toy_id):
    context = {}

    if (request.method == "GET"):
        if (toy_id=="add"):
            form = ToyEditForm(label_suffix="")
        else:
            form = ToyEditForm(toy_id=toy_id, label_suffix="")
        context.update({'toy_edit_form': form})


    # add or update member details
    if (request.method == "POST"):
        form = ToyEditForm(request.POST)
        context.update({"toy_edit_form_error": ""})
        if form.is_valid():
            toy_id=request.POST.get('toy_edit_id',None)

            try:
                form.save(toy_id)
            except ValueError as err:
                context.update({"toy_edit_form_error": err.message})
                context.update({"toy_edit_id": toy_id})
        else:
            context.update({"toy_edit_form_error": "Missing required field(s)"})

        context.update({'toy_edit_form': form})


    return context



class ToyEditForm(forms.Form):
    numeric = RegexValidator(r'^[0-9.-]*$', 'Only numeric characters are allowed.')

    code = forms.CharField(label="ID Code", max_length=Toy._meta.get_field('code').max_length)
    name = forms.CharField(max_length=Toy._meta.get_field('name').max_length)
    # needs record in history logic
    state=forms.ChoiceField(choices=Toy.TOY_STATE_CHOICES)
    comment = forms.CharField(required=False, max_length=Toy._meta.get_field('comment').max_length,widget=forms.Textarea(attrs={"rows": "1"}))
    issue_type = forms.ChoiceField(required=False, choices=Toy.ISSUE_TYPE_CHOICES)
    issue_comment = forms.CharField(required=False, max_length=Toy._meta.get_field('issue_comment').max_length,widget=forms.Textarea(attrs={"rows":"1"}))
    member_loaned = forms.ModelChoiceField(required=False,queryset=Member.objects.all())
    borrow_date = forms.DateField(required=False, input_formats=['%d/%m/%Y','%d/%m/%y'],widget=forms.DateInput(format='%d/%m/%y', attrs={"datepicker": "True"}))
    due_date = forms.DateField(required=False, input_formats=['%d/%m/%Y','%d/%m/%y'],widget=forms.DateInput(format='%d/%m/%y', attrs={"datepicker": "True"}))
    borrow_counter = forms.IntegerField(required=False)
    rent_tally = forms.DecimalField(required=False, validators=[numeric], min_value=0, decimal_places=2)
    loan_cost = forms.DecimalField(min_value=0,validators=[numeric], decimal_places=2)
    loan_bond = forms.DecimalField(required=False,validators=[numeric],min_value=0, decimal_places=2)
    last_check = forms.DateField(required=False, input_formats=['%d/%m/%Y','%d/%m/%y'],widget=forms.DateInput(format='%d/%m/%y', attrs={"datepicker": "True"}))

    last_stock_take = forms.DateField(required=False, input_formats=['%d/%m/%Y','%d/%m/%y'],widget=forms.DateInput(format='%d/%m/%y', attrs={"datepicker": "True","col2":"true"}))
    image = forms.ModelChoiceField(queryset=Image.objects.all(), widget=forms.Select(attrs={"col2":"true"}))
    category = forms.ModelChoiceField(queryset=ToyCategory.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    min_age = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={"col2":"true"}))
    purchase_date = forms.DateField(required=False, input_formats=['%d/%m/%Y','%d/%m/%y'], widget=forms.DateInput(format='%d/%m/%y', attrs={"datepicker": "True","col2":"true"}))
    purchase_cost = forms.DecimalField(required=False,min_value=0,validators=[numeric], decimal_places=2,widget=forms.NumberInput(attrs={"col2":"true"}))
    num_pieces = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={"col2":"true"}))
    parts_list = forms.CharField(required=False, max_length=Toy._meta.get_field('parts_list').max_length,widget=forms.Textarea(attrs={"rows":"1","col2":"true"}))
    storage_location = forms.CharField(required=False,max_length=Toy._meta.get_field('storage_location').max_length,widget=forms.TextInput(attrs={"col2":"true"}))

    brand = forms.ModelChoiceField(required=False,queryset=ToyBrand.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    purchased_from = forms.ModelChoiceField(required=False,queryset=ToyVendor.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    image_receipt = forms.ModelChoiceField(required=False,queryset=Image.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    image_instructions = forms.ModelChoiceField(required=False,queryset=Image.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    packaging = forms.ModelChoiceField(required=False,queryset=ToyPackaging.objects.all(),widget=forms.Select(attrs={"col2":"true"}))

    def save(self,toy_id):

        #Store current issue type and toy state
        #check validity of toy state change to issues type - add function to define this
        #check validity of issue type change to toy state - issue_type_to_state()
        #


       if not toy_id:
          raise Exception("Toy ID missing")



       # current_toy_state = self.cleaned_data["state"]
       # current_issue_type = self.cleaned_data["issue_type"]
       #
       # new_toy_state = Toy.issue_type_to_state(current_issue_type)
       # if new_toy_state != None:
       #     self.cleaned_data["state"] = new_toy_state
       #
       # new_issue_type = Toy.toy_state_to_issue_type(current_toy_state)
       # if new_issue_type != None:
       #     self.cleaned_data["issue_type"] = new_issue_type

       if toy_id=="add":
           toy_id=None

           if Toy.objects.filter(code=self.cleaned_data["code"]).exclude(state=Toy.RETIRED).exists():
               raise ValueError(self.cleaned_data["code"]+" already exists. Retire existing toy before reassignment")

       result=Toy.objects.update_or_create(pk=toy_id, defaults=self.cleaned_data)

       return result



    def form_initial(self,toy_id):
    
        initial = get_object_or_404(Toy, pk=toy_id).__dict__
        
        for key, value in initial.iteritems():
            if key.endswith('_id'):
                initial.update({key[:-3]: value})
                initial.pop(key)

        return initial

    def __init__(self, *args, **kwargs):
        toy_id=kwargs.pop("toy_id", 0)
        if toy_id:
            kwargs.update({"initial":self.form_initial(toy_id)})
        super(ToyEditForm, self).__init__(*args, **kwargs)

def render_toy_edit(request, context={}):

     rendered=None




     if "toy_edit_id" in request.GET:
        toy_id=request.GET["toy_edit_id"]
        context={}
        context.update({"toy_edit_id":toy_id})
        context.update(handle_toy_edit(request,toy_id))
        context=RequestContext(request,context)
        rendered=render_to_string('toybox/toy_edit.html', context)


     return rendered


def render_ajax_request(request):
    rendered=None
    if request.is_ajax():
         if "toy_edit_id" in request.GET:
             rendered=render_toy_edit(request)

         if rendered:
            return HttpResponse(rendered)

    return None