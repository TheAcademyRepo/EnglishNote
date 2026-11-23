from django.urls import path

from .views import (
    SearchContentView,
    TrendingContentView,
    DiscoveryFiltersView,
)


urlpatterns = [

    path(
        "search/",
        SearchContentView.as_view(),
        name="content-search"
    ),

    path(
        "trending/",
        TrendingContentView.as_view(),
        name="trending-content"
    ),

    path(
        "filters/",
        DiscoveryFiltersView.as_view(),
        name="discovery-filters"
    ),

]