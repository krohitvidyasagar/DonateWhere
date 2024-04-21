from django_filters import rest_framework as filters


class DonationFilter(filters.FilterSet):
    item = filters.CharFilter(field_name='item', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category', lookup_expr='icontains')
    is_claimed = filters.BooleanFilter(field_name='is_claimed')
