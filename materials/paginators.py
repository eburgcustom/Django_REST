from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """
    Единый пагинатор для курсов и уроков.
    """

    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = "page_size"  # Параметр для изменения размера страницы
    max_page_size = 15  # Максимальное количество элементов на странице

    def get_page_size(self, request):
        """
        Переопределяем метод для установки минимального размера страницы.
        """
        page_size = super().get_page_size(request)
        # Устанавливаем минимальный размер страницы 5
        if page_size < 5:
            return 5
        return page_size
