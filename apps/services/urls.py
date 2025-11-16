"""
Service URLs
"""
from django.urls import path
from services import views

app_name = 'services'

urlpatterns = [
    # Categories
    path('categories/', views.ServiceCategoryListView.as_view(), name='category_list'),
    
    # Services
    path('', views.ServiceListView.as_view(), name='service_list'),
    path('create/', views.ServiceCreateView.as_view(), name='service_create'),
    path('my-services/', views.MyServicesView.as_view(), name='my_services'),
    path('featured/', views.FeaturedServicesView.as_view(), name='featured_services'),
    path('popular/', views.PopularServicesView.as_view(), name='popular_services'),
    path('<slug:slug>/', views.ServiceDetailView.as_view(), name='service_detail'),
    path('<slug:slug>/update/', views.ServiceUpdateView.as_view(), name='service_update'),
    path('<slug:slug>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
    
    # Availability & Areas
    path('availability/', views.ServiceAvailabilityView.as_view(), name='availability'),
    path('areas/', views.ServiceAreaView.as_view(), name='service_areas'),
]