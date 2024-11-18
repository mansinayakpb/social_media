from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .factories import CategoryFactory


class CategoryViewTests(APITestCase):
    def setUp(self):
        User = get_user_model()

        # Create an admin user
        self.superuser = User.objects.create_superuser(
            email="superuser@example.com",
            password="password123",
        )

        # Generate JWT token for the superuser
        refresh = RefreshToken.for_user(self.superuser)
        self.token = str(refresh.access_token)

        # Create a category instance using the factory
        self.category = CategoryFactory.create()

        # Define the URL endpoints for the category list and category detail
        self.url_list = reverse("category_list_create")
        self.url_detail = reverse(
            "category_detail_update_delete", kwargs={"pk": self.category.id}
        )

    def test_get_category_list(self):
        """Test that the category list is retrieved correctly."""
        response = self.client.get(
            self.url_list, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]["category_name"], self.category.category_name
        )

    def test_get_category_detail(self):
        """Test that the details of a single category are retrieved correctly."""
        response = self.client.get(
            self.url_detail, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["category_name"], self.category.category_name
        )

    def test_post_create_category(self):
        """Test that an admin can create a new category."""
        data = {
            "category_name": "Technology",
            "description": "Tech-related items",
        }
        response = self.client.post(
            self.url_list,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["category_name"], data["category_name"])

    def test_post_create_category_invalid_name(self):
        """Test that category name validation works."""
        data = {
            "category_name": "Tech@123",
            "description": "Invalid category name",
        }
        response = self.client.post(
            self.url_list,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("category_name", response.data)
        self.assertEqual(
            response.data["category_name"][0],
            "Category name should only contain letters and spaces.",
        )

    def test_put_update_category(self):
        """Test that an admin can update an existing category."""
        updated_data = {"category_name": "Updated Category"}
        response = self.client.put(
            self.url_detail,
            updated_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["category_name"], updated_data["category_name"]
        )

    def test_patch_update_category(self):
        """Test that an admin can partially update a category."""
        updated_data = {"category_name": "Partially Updated Category"}
        response = self.client.patch(
            self.url_detail,
            updated_data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["category_name"], updated_data["category_name"]
        )

    def test_delete_category(self):
        """Test that an admin can delete a category."""
        response = self.client.delete(
            self.url_detail, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the category is deleted and no longer accessible
        response = self.client.get(
            self.url_detail, HTTP_AUTHORIZATION=f"Bearer {self.token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)