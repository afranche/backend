from rest_framework.pagination import PageNumberPagination

# Define the number of items per page
ITEMS_PER_PAGE = 16

class CategoryPagination(PageNumberPagination):
    page_size = ITEMS_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ListingPagination(PageNumberPagination):
    page_size = ITEMS_PER_PAGE
    page_size_query_param = 'page_size'
    max_page_size = 1000