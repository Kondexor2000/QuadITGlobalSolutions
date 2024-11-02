from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from blogserviceapp.models import Category
import logging

logger = logging.getLogger(__name__)

def check_template_exists(template_name, request):
    try:
        get_template(template_name)
        logger.info(f"Template '{template_name}' found for user {request.user}.")
        return True
    except TemplateDoesNotExist:
        logger.error(f"Template '{template_name}' does not exist for user {request.user}.")
        return False

def category_view(request):
    logger.info(f"User {request.user} accessed the category view.")
    template_name = 'read_categories.html'
    
    if not check_template_exists(template_name, request):
        logger.warning(f"User {request.user} received a 404 because the template '{template_name}' was not found.")
        return HttpResponseNotFound("Template not found.")
    
    try:
        categories = Category.objects.all()
        logger.info(f"Categories retrieved successfully for user {request.user}.")
    except Exception as e:
        logger.error(f"Error retrieving categories for user {request.user}: {e}")
        return HttpResponse("An error occurred while retrieving categories.", status=500)
    
    return render(request, template_name, {'categories': categories})