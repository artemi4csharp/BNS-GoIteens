from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import CategoryRequest

User = get_user_model()

class CategoryRequestTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass12345")
        self.client.login(username="testuser", password="pass12345")

    def test_create_category_request(self):
        url = reverse("categories:request_create")
        response = self.client.post(url, {"name": "Кухонні прилади"}, follow=True)

        # Перевіряємо що редіректнув назад на список
        self.assertEqual(response.status_code, 200)

        # Перевіряємо що запит створився
        self.assertTrue(CategoryRequest.objects.filter(name="Кухонні прилади").exists())
        req = CategoryRequest.objects.get(name="Кухонні прилади")
        self.assertEqual(req.status, CategoryRequest.STATUS_PENDING)
        self.assertEqual(req.user, self.user)
