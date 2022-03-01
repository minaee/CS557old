from django.shortcuts import render
from datetime import datetime

def uni_index(request):
    # queryset_list_srvices = Service_main_page.objects.order_by('title').exclude(services_intro=True)
    # queryset_list_products = Intro_products.objects.order_by('title').exclude(products_intro=True)

    # today = datetime.today()
    # datem = datetime(today.year, today.month, today.day)
    
    
    # queryset_list_news = News.objects.order_by('-date').filter(is_published=True)[:3]
    # queryset_list_events = Events.objects.order_by('start_date').filter(start_date__gte=datem, is_published=True)[:3]
    # queryset_list_main_page = Main_page.objects.order_by('title')
    

    context = {
        # 'srevices': queryset_list_srvices,
        # 'products': queryset_list_products,
        # 'events': queryset_list_events,
        # 'news': queryset_list_news,
        # 'main_items': queryset_list_main_page,
    }
    return render(request, 'university/uni_index.html', context)
