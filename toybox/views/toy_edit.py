
from toybox.models import *
from django import forms
from django.shortcuts import get_object_or_404
from shared import get_config
from django.template.loader import render_to_string
from django.shortcuts import HttpResponse
from django.template import RequestContext

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
        context.update({"toy_edit_form_ok": False})
        if form.is_valid():
            toy_id=request.POST.get('toy_edit_id',None)
            if form.save(toy_id):
                context.update({"toy_edit_form_ok": True})
        else:
            context.update({'toy_edit_form': form})








    return context



class ToyEditForm(forms.Form):
    code = forms.CharField(label="ID Code", max_length=Toy._meta.get_field('code').max_length)
    name = forms.CharField(max_length=Toy._meta.get_field('name').max_length)
    # needs record in history logic
    state=forms.ChoiceField(choices=Toy.TOY_STATE_CHOICES)
    comment = forms.CharField(required=False, max_length=Toy._meta.get_field('comment').max_length,widget=forms.Textarea(attrs={"rows": "1"}))
    issue_type = forms.ChoiceField(required=False, choices=Toy.ISSUE_TYPE_CHOICES)
    issue_comment = forms.CharField(required=False, max_length=Toy._meta.get_field('issue_comment').max_length,widget=forms.Textarea(attrs={"rows":"1"}))
    member_loaned = forms.ModelChoiceField(required=False,queryset=Member.objects.all())
    borrow_date = forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))
    due_date = forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))
    borrow_counter = forms.IntegerField(required=False)
    loan_cost = forms.DecimalField(min_value=0, decimal_places=2)
    loan_bond = forms.DecimalField(required=False,min_value=0, decimal_places=2)
    last_check = forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))
    last_stock_take = forms.DateField(required=False, input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))


    image = forms.ModelChoiceField(queryset=Image.objects.all(), widget=forms.Select(attrs={"col2":"true"}))
    category = forms.ModelChoiceField(queryset=ToyCategory.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    min_age = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={"col2":"true"}))
    purchase_date = forms.DateField(required=False, input_formats=['%d/%m/%Y'], widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True","col2":"true"}))
    purchase_cost = forms.DecimalField(required=False,min_value=0, decimal_places=2,widget=forms.NumberInput(attrs={"col2":"true"}))
    num_pieces = forms.IntegerField(required=False,widget=forms.NumberInput(attrs={"col2":"true"}))
    parts_list = forms.CharField(required=False, max_length=Toy._meta.get_field('parts_list').max_length,widget=forms.Textarea(attrs={"rows":"1","col2":"true"}))
    storage_location = forms.CharField(required=False,max_length=Toy._meta.get_field('storage_location').max_length,widget=forms.TextInput(attrs={"col2":"true"}))

    brand = forms.ModelChoiceField(required=False,queryset=ToyBrand.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    purchased_from = forms.ModelChoiceField(required=False,queryset=ToyVendor.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    image_receipt = forms.ModelChoiceField(required=False,queryset=Image.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    image_instructions = forms.ModelChoiceField(required=False,queryset=Image.objects.all(),widget=forms.Select(attrs={"col2":"true"}))
    packaging = forms.ModelChoiceField(required=False,queryset=ToyPackaging.objects.all(),widget=forms.Select(attrs={"col2":"true"}))

    def save(self,toy_id):
       if not toy_id:
            return None

       if toy_id=="add":
           toy_id=None

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