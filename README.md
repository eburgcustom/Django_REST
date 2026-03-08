# Django REST API

Проект для управления курсами и уроками с системой прав доступа.

## Структура

- **users** - управление пользователями с email-авторизацией
- **materials** - управление курсами, уроками и подписками.

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
- Владелец (связь с User)

### Lesson
- Название
- Описание
- Превью (картинка)
- Ссылка на видео (только YouTube)
- Связь с Course
- Владелец (связь с User)
- Цена

### Subscription
- Пользователь (связь с User)
- Курс (связь с Course)
- Дата подписки

### Payment
- Пользователь (связь с User)
- Оплаченный курс (связь с Course)
- Оплаченный урок (связь с Lesson)
- Сумма оплаты
- Способ оплаты (наличные/перевод)
- ID сессии Stripe
- Ссылка на оплату Stripe
## Права доступа

### Модераторы
- ✅ Просмотр всех курсов и уроков
- ✅ Редактирование любых курсов и уроков
- ❌ Создание курсов и уроков
- ❌ Удаление курсов и уроков

### Обычные пользователи
- ✅ Просмотр только своих курсов и уроков
- ✅ Создание курсов и уроков (автоматически привязываются к пользователю)
- ✅ Редактирование и удаление только своих объектов
- ✅ Подписка на любые курсы
- ❌ Доступ к чужим объектам запрещен

## API Эндпоинты

### Пользователи
- `POST /api/register/` - регистрация (доступно всем)
- `POST /api/login/` - вход (доступно всем)
- `POST /api/token/refresh/` - обновление токена
- `GET /api/users/` - список пользователей
- `GET /api/users/{id}/` - получение пользователя
- `PUT/PATCH /api/users/{id}/` - обновление пользователя
- `DELETE /api/users/{id}/` - удаление пользователя

### Курсы (ViewSet)

**Пагинация курсов:**
- По умолчанию: 5 элементов на странице
- Параметр: `?page_size=10`
- Максимум: 20 элементов

- `GET /api/courses/` - список курсов (своих для пользователей, всех для модераторов)
- `POST /api/courses/` - создание курса (только для пользователей)
- `GET /api/courses/{id}/` - получение курса (владелец или модератор)
- `PUT/PATCH /api/courses/{id}/` - обновление курса (владелец или модератор)
- `DELETE /api/courses/{id}/` - удаление курса (владелец или модератор)

### Подписки
- `POST /api/materials/subscription/` - подписка/отписка от курса

**Тело запроса:**
```json
{
  "course_id": 1
}
```
**Ответ:**
```json
{
  "message": "подписка добавлена"  // или "подписка удалена"
}
```

### Платежи (Stripe)
- `POST /api/materials/payment/create/` - создание платежа и получение ссылки на оплату
- `GET /api/materials/payment/{payment_id}/status/` - проверка статуса платежа

**Создание платежа:**
```json
{
  "course_id": 1
}
```
**Ответ:**
```json
{
  "payment_id": 1,
  "payment_url": "https://checkout.stripe.com/pay/...",
  "amount": 100.00
}
```

**Проверка статуса:**
```json
{
  "payment_id": 1,
  "status": "paid",
  "is_paid": true,
  "amount": 100.00
}
```

### Уроки (Generic-классы)
**Пагинация уроков:**
- По умолчанию: 10 элементов на странице
- Параметр: `?page_size=20`
- Максимум: 50 элементов
- `GET /api/lessons/` - список уроков (своих для пользователей, всех для модераторов)
- `POST /api/lessons/` - создание урока (только для пользователей)
- `GET /api/lessons/{id}/` - получение урока (владелец или модератор)
- `PUT/PATCH /api/lessons/{id}/` - обновление урока (владелец или модератор)
- `DELETE /api/lessons/{id}/` - удаление урока (владелец или модератор)

### Платежи (с фильтрацией)
- `GET /api/payments/` - список платежей

**Фильтрация платежей:**
- `?paid_course=1` - по курсу
- `?paid_lesson=1` - по уроку
- `?payment_method=cash` - по способу оплаты

**Сортировка платежей:**
- `?ordering=payment_date` - по возрастанию даты
- `?ordering=-payment_date` - по убыванию даты (по умолчанию)

## Установка

1. Клонировать репозиторий
2. Установить зависимости: `poetry install --no-root`
3. Создать `.env` файл на основе `.env_example`
4. Добавить Stripe ключи в `.env`:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_test_... (получить на https://dashboard.stripe.com/apikeys)
   STRIPE_SECRET_KEY=sk_test_... (получить на https://dashboard.stripe.com/apikeys)
   ```
5. Выполнить миграции: `python manage.py migrate`
6. Создать группу модераторов: `python manage.py loaddata users/fixtures/groups.json`
7. Запустить сервер: `python manage.py runserver`

## Аутентификация

Проект использует JWT-токены для аутентификации:

1. **Регистрация:** `POST /api/register/`
   ```json
   {
     "email": "user@example.com",
     "password": "password123",
     "password_confirm": "password123",
     "first_name": "John",
     "last_name": "Snow"
   }
   ```

2. **Вход:** `POST /api/login/`
   ```json
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```

3. **Использование токена:** Добавить в заголовки запросов:
   ```
   Authorization: Bearer <access_token>
   ```

## Валидация

### YouTube ссылки
Разрешены только ссылки на YouTube следующих форматов:
- `youtube.com/watch?v=ID`
- `youtu.be/ID`
- `m.youtube.com/watch?v=ID`

При попытке сохранить другую ссылку будет возвращена ошибка валидации.

## Особенности

### Признак подписки
При получении данных курса в ответе включается поле `is_subscribed`:
```json
{
  "id": 1,
  "title": "Курс",
  "is_subscribed": true,
  "lessons_count": 5,
  "lessons": [...]
}
```

## Пагинация
Все списочные эндпоинты поддерживают пагинацию:

```json
{
  "count": 25,
  "next": "http://localhost:8000/api/courses/?page=3",
  "previous": "http://localhost:8000/api/courses/?page=1",
  "results": [...]
}
```

## Тестирование
Запуск всех тестов:

```bash
python python manage.py test materials.tests
````
Запуск тестов уроков:

```bash
python manage.py test materials.tests.LessonCRUDTestCase
````
Запуск тестов подписок:

```bash
python manage.py test materials.tests.SubscriptionTestCase
````
Тесты проверяют:

- CRUD операции для уроков
- Права доступа (владельцы, модераторы, обычные пользователи)
- Функционал подписок
- Валидацию YouTube ссылок
- Пагинацию

## Создание тестовых данных

**Через кастомную команду:**
```bash
python manage.py create_payments
```

## Установка

1. Клонировать репозиторий
2. Установить зависимости: `poetry install`
3. Создать `.env` файл на основе `.env_example`
4. Выполнить миграции: `python manage.py migrate`
5. Создать группу модераторов: `python manage.py loaddata users/fixtures/groups.json`
6. Запустить сервер: `python manage.py runserver`

## Назначение прав

1. Создайте пользователей через API или админку
2. Назначьте группу `moderator` через админку Django
3. Пользователи с группой `moderator` получают соответствующие права доступа
