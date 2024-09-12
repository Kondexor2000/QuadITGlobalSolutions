from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from blogserviceapp.models import Category

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        return True
    except TemplateDoesNotExist:
        return False

def category_view(request):
    template_name = 'read_categories.html'
    if not check_template_exists(template_name, request):
        return HttpResponse("Template not found.")
    
    categories = Category.objects.all()
    return render(request, template_name, {'categories': categories})