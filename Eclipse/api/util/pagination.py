from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    page_size = 15  # Default number of messages per page
    page_size_query_param = 'page_size' # Allows client to set page size e.g. ?page_size=100
    max_page_size = 100 # Maximum page size client can request
