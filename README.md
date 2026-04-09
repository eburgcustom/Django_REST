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

### Способ 1: Docker Compose (рекомендуется)

1. **Клонировать репозиторий**
2. **Создать `.env` файл на основе `.env_example`**
   ```bash
   cp .env_example .env
   ```
3. **Настроить переменные окружения в `.env`:**
   - `SECRET_KEY` - сгенерировать новый ключ
   - `DATABASE_USER`, `DATABASE_PASSWORD` - данные для PostgreSQL
   - `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - данные для почты
   - `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY` - ключи Stripe

4. **Запустить все сервисы:**
   ```bash
   docker-compose up --build
   ```

5. **Выполнить миграции и создать суперпользователя:**
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py csu
   ```

### Способ 2: Локальная установка

1. Клонировать репозиторий
2. Установить зависимости: `poetry install --no-root`
3. Создать `.env` файл на основе `.env_example`
4. Добавить Stripe ключи в `.env`
5. Выполнить миграции: `python manage.py migrate`
6. Создать суперпользователя: `python manage.py csu`
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

## Проверка работоспособности сервисов

### Docker Compose

После запуска `docker-compose up --build` проверьте каждый сервис:

1. **Django Backend:**
   ```bash
   # Проверить статус контейнера
   docker-compose ps backend
   
   # Посмотреть логи
   docker-compose logs backend
   
   # Проверить API
   curl http://localhost:8000/api/materials/courses/
   ```

2. **PostgreSQL:**
   ```bash
   # Проверить статус контейнера
   docker-compose ps db
   
   # Подключиться к базе
   
   
   # Проверить таблицы
   \dt
   ```

3. **Redis:**
   ```bash
   # Проверить статус
   docker-compose ps redis
   
   # Тестировать подключение
   docker-compose exec redis redis-cli ping
   ```

4. **Celery Worker:**
   ```bash
   # Проверить статус
   docker-compose ps celery-worker
   
   # Посмотреть логи
   docker-compose logs celery-worker
   ```

5. **Celery Beat:**
   ```bash
   # Проверить статус
   docker-compose ps celery-beat
   
   # Посмотреть логи
   docker-compose logs celery-beat
   ```

### Полезные команды

```bash
# Остановить все сервисы
docker-compose down

# Перезапустить с пересборкой
docker-compose up --build --force-recreate

# Выполнить команду в контейнере
docker-compose exec backend python manage.py shell

# Посмотреть логи всех сервисов
docker-compose logs -f

# Очистить volumes (удалит данные БД)
docker-compose down -v
```

## CI/CD и Автоматический Деплой

### GitHub Actions Workflow

Проект использует GitHub Actions для автоматического тестирования и деплоя:

**Что происходит при push:**
1. **Запускаются тесты** - автоматически с SQLite
2. **Собирается Docker образ** - если тесты пройдены
3. **Пушится в Docker Hub** - с тегом по SHA коммита
4. **Деплоится на сервер** - автоматически через SSH

### Настройка GitHub Secrets

Добавьте в репозитории GitHub → Settings → Secrets and variables → Actions:

```
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_token
PROD_HOST=your_server_ip
PROD_USER=ssh_user
PROD_SSH_KEY=-----BEGIN OPENSSH PRIVATE KEY-----
```

### Настройка удаленного сервера

**1. Установите Docker:**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

**2. Настройте SSH доступ:**
```bash
# Для личного сервера можно использовать существующего пользователя
# Добавьте пользователя в группу docker
sudo usermod -aG docker your_username

# Настройте SSH ключи (если еще не настроены)
mkdir -p ~/.ssh
# Добавьте ваш публичный ключ в ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**3. Создайте директорию проекта:**
```bash
sudo mkdir -p /opt/django-rest
sudo chown your_username:your_username /opt/django-rest
```

**4. Создайте .env файл с переменными окружения:**
```bash
nano /opt/django-rest/.env
```

Добавьте переменные из вашего локального .env файла:
```bash
SECRET_KEY=your_production_secret_key
DEBUG=False
DATABASE_NAME=django_rest_db
DATABASE_USER=django_user
DATABASE_PASSWORD=your_production_db_password
DATABASE_HOST=db
DATABASE_PORT=5432
PASSWORD_FOR_SUPER_USER=your_password
STRIPE_PUBLISHABLE_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
EMAIL_HOST_USER=your_email@yandex.ru
EMAIL_HOST_PASSWORD=your_email_password
DEFAULT_FROM_EMAIL=your_email@yandex.ru
SERVER_EMAIL=your_email@yandex.ru
```

**5. Установите правильные права доступа для .env:**
```bash
chmod 600 /opt/django-rest/.env
chown your_username:your_username /opt/django-rest/.env
```

### Запуск деплоя

**Автоматический:**
```bash
# Просто сделайте push в main ветку
git add .
git commit -m "Update and deploy"
git push origin main
```

**Ручной запуск в GitHub:**
1. Перейдите в Actions → CI/CD
2. Нажмите "Run workflow"

### Проверка деплоя

```bash
# На сервере проверьте контейнер
ssh deploy@your_server
docker ps
docker logs django-rest
```

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
