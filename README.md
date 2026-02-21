# Django REST API

Проект для управления курсами и уроками.

## Структура

- **users** - управление пользователями с email-авторизацией
- **materials** - управление курсами и уроками

## Модели

### User
- Email (уникальный)
- Телефон
- Город
- Аватар

### Course
- Название
- Превью (картинка)
- Описание

### Lesson
- Название
- Описание
- Превью (картинка)
- Ссылка на видео
- Связь с Course

## API Эндпоинты

### Курсы (ViewSet)
- `GET /api/courses/` - список курсов
- `POST /api/courses/` - создание курса
- `GET /api/courses/{id}/` - получение курса
- `PUT/PATCH /api/courses/{id}/` - обновление курса
- `DELETE /api/courses/{id}/` - удаление курса

### Уроки (Generic-классы)
- `GET /api/lessons/` - список уроков
- `POST /api/lessons/` - создание урока
- `GET /api/lessons/{id}/` - получение урока
- `PUT/PATCH /api/lessons/{id}/` - обновление урока
- `DELETE /api/lessons/{id}/` - удаление урока

## Установка

1. Клонировать репозиторий
2. Установить зависимости: `poetry install`
3. Создать `.env` файл на основе `.env_example`
4. Выполнить миграции: `python manage.py migrate`
5. Запустить сервер: `python manage.py runserver`