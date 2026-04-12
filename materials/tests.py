from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):
    """
    Тесты CRUD операций для уроков.
    """

    def setUp(self):
        """Создание тестовых данных."""
        # Создание пользователей
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password123"
        )
        self.moderator = User.objects.create_user(
            email="moderator@example.com", password="password123"
        )

        # Назначение группы модератора
        from django.contrib.auth.models import Group

        moderator_group, _ = Group.objects.get_or_create(name="moderator")
        self.moderator.groups.add(moderator_group)

        # Создание курсов
        self.course1 = Course.objects.create(
            title="Course 1", description="Description 1", owner=self.user1
        )
        self.course2 = Course.objects.create(
            title="Course 2", description="Description 2", owner=self.user2
        )

        # Создание уроков
        self.lesson1 = Lesson.objects.create(
            title="Lesson 1",
            description="Description 1",
            video_url="https://youtube.com/watch?v=123",
            course=self.course1,
            owner=self.user1,
        )
        self.lesson2 = Lesson.objects.create(
            title="Lesson 2",
            description="Description 2",
            video_url="https://youtube.com/watch?v=456",
            course=self.course2,
            owner=self.user2,
        )

    def test_lesson_list_as_owner(self):
        """Тест получения списка уроков владельцем."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get("/api/materials/lessons/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Lesson 1")

    def test_lesson_list_as_moderator(self):
        """Тест получения списка уроков модератором."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get("/api/materials/lessons/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_lesson_create_as_user(self):
        """Тест создания урока обычным пользователем."""
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "New Lesson",
            "description": "New Description",
            "video_url": "https://youtube.com/watch?v=789",
            "course": self.course1.id,
        }
        response = self.client.post("/api/materials/lessons/", data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)

        new_lesson = Lesson.objects.get(id=response.data["id"])
        self.assertEqual(new_lesson.owner, self.user1)

    def test_lesson_create_as_moderator_forbidden(self):
        """Тест создания урока модератором (запрещено)."""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "New Lesson",
            "description": "New Description",
            "video_url": "https://youtube.com/watch?v=789",
            "course": self.course1.id,
        }
        response = self.client.post("/api/materials/lessons/", data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_retrieve_as_owner(self):
        """Тест получения урока владельцем."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"/api/materials/lessons/{self.lesson1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Lesson 1")

    def test_lesson_retrieve_as_moderator(self):
        """Тест получения урока модератором."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(f"/api/materials/lessons/{self.lesson1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_retrieve_as_other_user_forbidden(self):
        """Тест получения урока другим пользователем (запрещено)."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(f"/api/materials/lessons/{self.lesson1.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_lesson_update_as_owner(self):
        """Тест обновления урока владельцем."""
        self.client.force_authenticate(user=self.user1)
        data = {"title": "Updated Lesson", "description": "Updated Description"}
        response = self.client.patch(f"/api/materials/lessons/{self.lesson1.id}/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.title, "Updated Lesson")

    def test_lesson_update_as_moderator(self):
        """Тест обновления урока модератором."""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Updated Lesson by Moderator",
            "description": "Updated Description",
        }
        response = self.client.patch(f"/api/materials/lessons/{self.lesson1.id}/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.title, "Updated Lesson by Moderator")

    def test_lesson_delete_as_owner(self):
        """Тест удаления урока владельцем."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(f"/api/materials/lessons/{self.lesson1.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_delete_as_moderator(self):
        """Тест удаления урока модератором."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f"/api/materials/lessons/{self.lesson1.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)

    def test_lesson_delete_as_other_user_forbidden(self):
        """Тест удаления урока другим пользователем (запрещено)."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/api/materials/lessons/{self.lesson1.id}/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SubscriptionTestCase(APITestCase):
    """
    Тесты функционала подписки на курсы.
    """

    def setUp(self):
        """Создание тестовых данных."""
        # Создание пользователей
        self.user1 = User.objects.create_user(
            email="user1@example.com", password="password123"
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com", password="password123"
        )

        # Создание курсов
        self.course1 = Course.objects.create(
            title="Course 1", description="Description 1", owner=self.user1
        )
        self.course2 = Course.objects.create(
            title="Course 2", description="Description 2", owner=self.user2
        )

    def test_subscribe_to_course(self):
        """Тест подписки на курс."""
        self.client.force_authenticate(user=self.user1)
        data = {"course_id": self.course2.id}
        response = self.client.post("/api/materials/subscription/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")

        # Проверяем, что подписка создана
        self.assertTrue(
            Subscription.objects.filter(user=self.user1, course=self.course2).exists()
        )

    def test_unsubscribe_from_course(self):
        """Тест отписки от курса."""
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user1, course=self.course2)

        self.client.force_authenticate(user=self.user1)
        data = {"course_id": self.course2.id}
        response = self.client.post("/api/materials/subscription/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")

        # Проверяем, что подписка удалена
        self.assertFalse(
            Subscription.objects.filter(user=self.user1, course=self.course2).exists()
        )

    def test_subscribe_to_own_course(self):
        """Тест подписки на собственный курс."""
        self.client.force_authenticate(user=self.user1)
        data = {"course_id": self.course1.id}
        response = self.client.post("/api/materials/subscription/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")

    def test_subscription_without_course_id(self):
        """Тест подписки без указания ID курса."""
        self.client.force_authenticate(user=self.user1)
        data = {}
        response = self.client.post("/api/materials/subscription/", data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Не указан ID курса")

    def test_subscription_nonexistent_course(self):
        """Тест подписки на несуществующий курс."""
        self.client.force_authenticate(user=self.user1)
        data = {"course_id": 999}
        response = self.client.post("/api/materials/subscription/", data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscription_unauthorized(self):
        """Тест подписки без авторизации."""
        data = {"course_id": self.course1.id}
        response = self.client.post("/api/materials/subscription/", data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_subscription_flag(self):
        """Тест признака подписки в данных курса."""
        # Создаем подписку
        Subscription.objects.create(user=self.user1, course=self.course2)

        # Создаем модератора для просмотра всех курсов
        moderator = User.objects.create_user(
            email="moderator@example.com", password="password123"
        )
        from django.contrib.auth.models import Group

        moderator_group, _ = Group.objects.get_or_create(name="moderator")
        moderator.groups.add(moderator_group)

        self.client.force_authenticate(user=moderator)
        response = self.client.get("/api/materials/courses/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Находим курсы в ответе (пагинация)
        courses = response.data["results"]
        course1_data = next((c for c in courses if c["id"] == self.course1.id), None)
        course2_data = next((c for c in courses if c["id"] == self.course2.id), None)

        # Проверяем, что курсы найдены
        self.assertIsNotNone(course1_data)
        self.assertIsNotNone(course2_data)

        # Для модератора проверяем подписки user1
        # Модератор не подписан на курсы, поэтому is_subscribed будет False
        # Проверим, что поле есть в ответе
        self.assertIn("is_subscribed", course1_data)
        self.assertIn("is_subscribed", course2_data)
