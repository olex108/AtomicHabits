from rest_framework.pagination import PageNumberPagination


class HabitPaginator(PageNumberPagination):
    page_size = 5  # Количество элементов на страницу
    page_size_query_param = 'page_size' # Позволяет клиенту менять размер страницы (опционально)
    max_page_size = 50
