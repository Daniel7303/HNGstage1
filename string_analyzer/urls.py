from django.urls import path
from .views import (
    StringListCreateView,
    StringDetailView,
    NaturalLanguageFilterView,
    DeleteStringView
)

urlpatterns = [
    path('strings/', StringListCreateView.as_view(), name='string-list-create'),
    path('strings/<str:string_value>/', StringDetailView.as_view(), name='string-detail'),
    path('strings/filter-by-natural-language/', NaturalLanguageFilterView.as_view(), name='natural-language-filter'),
    path('strings/delete/<str:string_value>/', DeleteStringView.as_view(), name='delete-string'),
]
