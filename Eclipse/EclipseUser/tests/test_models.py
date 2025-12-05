from django.test import TestCase
from EclipseUser.models.user import EclipseUser

class EclipseUserModelTest(TestCase):
    def test_save_sets_displayname(self):
        user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.assertEqual(user.displayname, 'testuser')

    def test_save_assigns_default_avatar(self):
        user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.assertTrue(user.avatar.name.startswith('avatars/defaults/account'))

    def test_custom_user_manager(self):
        user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.assertEqual(user.username, 'testuser')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        admin_user = EclipseUser.objects.create_superuser(username='admin', password='password')
        self.assertEqual(admin_user.username, 'admin')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
