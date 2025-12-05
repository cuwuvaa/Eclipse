from django.test import TestCase, Client
from django.urls import reverse
from EclipseUser.models.user import EclipseUser
from EclipseUser.forms.auth import UserRegisterForm, UserLoginForm

class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_get(self):
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertIsInstance(response.context['form'], UserRegisterForm)

    def test_register_post_valid_data(self):
        initial_user_count = EclipseUser.objects.count()
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'password1': 'password',
            'password2': 'password'
        }, follow=True)
        self.assertEqual(response.status_code, 200) # Should be 200 after redirect
        self.assertEqual(EclipseUser.objects.count(), initial_user_count + 1)
        self.assertTrue(EclipseUser.objects.filter(username='newuser').exists())
        self.assertRedirects(response, reverse('rooms:main'))

    def test_register_post_invalid_data(self):
        initial_user_count = EclipseUser.objects.count()
        response = self.client.post(reverse('users:register'), {
            'username': 'newuser',
            'password1': 'password',
            'password2': 'wrongpassword'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertFormError(response.context['form'], 'password2', ['The two password fields didn’t match.'])
        self.assertEqual(EclipseUser.objects.count(), initial_user_count)

    def test_register_post_existing_username(self):
        EclipseUser.objects.create_user(username='existinguser', password='password')
        initial_user_count = EclipseUser.objects.count()
        response = self.client.post(reverse('users:register'), {
            'username': 'existinguser',
            'password': 'password',
            'password2': 'password'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')
        self.assertFormError(response.context['form'], 'username', ['Пользователь with this Username already exists.'])
        self.assertEqual(EclipseUser.objects.count(), initial_user_count)

    def test_register_authenticated_user_redirects(self):
        user = EclipseUser.objects.create_user(username='authuser', password='password')
        self.client.login(username='authuser', password='password')
        response = self.client.get(reverse('users:register'), follow=True)
        self.assertRedirects(response, reverse('rooms:main'))

class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')

    def test_login_get(self):
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')
        self.assertIsInstance(response.context['form'], UserLoginForm)

    def test_login_post_valid_data(self):
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'password'
        }, follow=True) # Added follow=True
        self.assertEqual(response.status_code, 200) # Should be 200 after redirect
        self.assertRedirects(response, reverse('rooms:main'))
        # self.assertTrue(self.user.is_authenticated) # This checks if the user object in the test is authenticated, not the session
        self.assertTrue('_auth_user_id' in self.client.session) # Check if user is logged in



class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_logout_get(self):
        response = self.client.get(reverse('users:logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/logout.html')
        self.assertFalse(self.client.session.get('_auth_user_id')) # User should be logged out
