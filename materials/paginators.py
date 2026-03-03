from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """
    Пагинатор для курсов.
    """
    page_size = 5  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 20  # Максимальное количество элементов на странице


class LessonPagination(PageNumberPagination):
    """
    Пагинатор для уроков.
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения размера страницы
    max_page_size = 50  # Максимальное количество элементов на странице
