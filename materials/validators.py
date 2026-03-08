import re
from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_youtube_url(value):
    """
    Валидатор проверяет, что ссылка ведет только на YouTube.
    Разрешенные форматы:
    - youtube.com/watch?v=ID
    - youtu.be/ID
    - m.youtube.com/watch?v=ID
    """
    if not value:
        return value
    
    # Регулярные выражения для различных форматов YouTube
    youtube_patterns = [
        r'^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'^https?://(?:www\.)?youtu\.be/[\w-]+',
        r'^https?://(?:www\.)?m\.youtube\.com/watch\?v=[\w-]+',
    ]
    
    # Проверяем, что ссылка соответствует одному из форматов YouTube
    is_youtube = any(re.match(pattern, value, re.IGNORECASE) for pattern in youtube_patterns)
    
    if not is_youtube:
        raise ValidationError(
            'Разрешены только ссылки на YouTube. '
            'Форматы: youtube.com/watch?v=ID, youtu.be/ID, m.youtube.com/watch?v=ID'
        )
    
    return value


class YouTubeURLValidator:
    """
    Класс-валидатор для проверки YouTube ссылок.
    """
    def __init__(self, field):
        self.field = field
    
    def __call__(self, attrs):
        url = attrs.get(self.field)
        if url:
            validate_youtube_url(url)
