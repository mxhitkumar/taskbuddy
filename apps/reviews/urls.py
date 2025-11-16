"""
Review URLs
"""
from django.urls import path
from reviews import views

app_name = 'reviews'

urlpatterns = [
    # Review Management
    path('', views.ReviewListView.as_view(), name='review_list'),
    path('create/', views.ReviewCreateView.as_view(), name='review_create'),
    path('my-reviews/', views.MyReviewsView.as_view(), name='my_reviews'),
    path('stats/', views.ReviewStatsView.as_view(), name='review_stats'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='review_detail'),
    path('<int:pk>/update/', views.ReviewUpdateView.as_view(), name='review_update'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    path('<int:review_id>/respond/', views.ReviewResponseCreateView.as_view(), name='review_respond'),
    path('<int:review_id>/helpful/', views.ReviewHelpfulView.as_view(), name='review_helpful'),
    
    # Provider/Service Reviews
    path('provider/<int:provider_id>/', views.ProviderReviewsView.as_view(), name='provider_reviews'),
    path('service/<int:service_id>/', views.ServiceReviewsView.as_view(), name='service_reviews'),
]