from django.test import TestCase, Client
from django.urls import reverse
from EclipseUser.models.user import EclipseUser
from django.core.files.uploadedfile import SimpleUploadedFile

class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.other_user = EclipseUser.objects.create_user(username='otheruser', password='password')

    def test_profile_view_redirects_to_my_profile_if_same_user(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('users:profiles', kwargs={'username': 'testuser'}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:profile'))

    def test_profile_view_displays_other_user_profile(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get(reverse('users:profiles', kwargs={'username': 'otheruser'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        self.assertIn('USER', response.context)
        self.assertEqual(response.context['USER'], self.other_user)

class MyProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_my_profile_get(self):
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        self.assertIn('USER', response.context)
        self.assertEqual(response.context['USER'], self.user)

    def test_my_profile_post_update_displayname(self):
        response = self.client.post(reverse('users:profile'), {'displayname': 'New Displayname'})
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.displayname, 'New Displayname')
        self.assertRedirects(response, reverse('users:profile'))

    def test_my_profile_post_update_avatar(self):
        # Create a dummy image file
        image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('users:profile'), {'avatar': image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertIn('test_image', self.user.avatar.name)
        self.assertTemplateUsed(response, 'user/profile.html')

    def test_my_profile_post_update_displayname_and_avatar(self):
        image = SimpleUploadedFile("test_image2.jpg", b"file_content2", content_type="image/jpeg")
        response = self.client.post(reverse('users:profile'), {'displayname': 'Another Displayname', 'avatar': image}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.displayname, 'Another Displayname')
        self.assertIn('test_image2', self.user.avatar.name)
        self.assertTemplateUsed(response, 'user/profile.html')
