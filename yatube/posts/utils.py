from django.core.paginator import Paginator
from django.conf import settings


def get_page_context(queryset, request):
    paginator = Paginator(queryset, settings.NUMBER_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
