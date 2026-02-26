from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Проверяет, является ли пользователь модератором.
    """
    
    def has_permission(self, request, view):
        # Проверяем, что пользователь авторизован и состоит в группе moderator
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='moderator').exists()
        )


class IsModeratorOrReadOnly(permissions.BasePermission):
    """
    Позволяет модераторам редактировать, а всем остальным - только чтение.
    """
    
    def has_permission(self, request, view):
        # Разрешаем безопасные методы (GET, HEAD, OPTIONS) всем авторизованным
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Для небезопасных методов требуем права модератора
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='moderator').exists()
        )


class IsOwner(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем объекта.
    """
    
    def has_object_permission(self, request, view, obj):
        # Проверяем, что пользователь является владельцем объекта
        return obj.owner == request.user


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Позволяет доступ владельцу или модератору.
    """
    
    def has_object_permission(self, request, view, obj):
        # Владелец может делать что угодно со своими объектами
        if obj.owner == request.user:
            return True
        
        # Модератор может просматривать и редактировать любые объекты
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.groups.filter(name='moderator').exists()
        )
