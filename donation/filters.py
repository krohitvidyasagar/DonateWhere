from django_filters import rest_framework as filters


class DonationFilter(filters.FilterSet):
    item = filters.CharFilter(field_name='item', lookup_expr='icontains')
    category = filters.CharFilter(field_name='category', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    is_claimed = filters.BooleanFilter(field_name='is_claimed')


class EventFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    address = filters.CharFilter(field_name='address', lookup_expr='icontains')
    organization = filters.CharFilter(field_name='organization__first_name', lookup_expr='icontains')

    datetime_gte = filters.DateFilter(field_name='datetime', lookup_expr='gte')
    datetime_lte = filters.DateFilter(field_name='datetime', lookup_expr='lte')

