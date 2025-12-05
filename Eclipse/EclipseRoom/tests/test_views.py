from django.test import TestCase, Client
from django.urls import reverse
from EclipseUser.models.user import EclipseUser
from EclipseRoom.models.room import Room
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.forms.create import RoomCreationForm

class MainViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.room1 = Room.objects.create(name='Room 1', description='Description 1')
        self.room2 = Room.objects.create(name='Room 2', description='Description 2')

    def test_main_view_no_query(self):
        response = self.client.get(reverse('rooms:main'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/main.html')
        self.assertIn('rooms', response.context)
        self.assertEqual(len(response.context['rooms']), 2)

    def test_main_view_with_query(self):
        response = self.client.get(reverse('rooms:main') + '?q=Room 1')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/main.html')
        self.assertIn('rooms', response.context)
        self.assertEqual(len(response.context['rooms']), 1)
        self.assertEqual(response.context['rooms'][0], self.room1)

class RoomCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_room_create_get(self):
        response = self.client.get(reverse('rooms:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'room/create.html')
        self.assertIsInstance(response.context['form'], RoomCreationForm)

    def test_room_create_post_valid_data(self):
        initial_room_count = Room.objects.count()
        response = self.client.post(reverse('rooms:create'), {'name': 'New Room', 'description': 'New description'})
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertEqual(Room.objects.count(), initial_room_count + 1)
        new_room = Room.objects.get(name='New Room')
        self.assertRedirects(response, reverse('rooms:room', kwargs={'room_pk': new_room.pk}))
        self.assertTrue(RoomUser.objects.filter(user=self.user, room=new_room, role=RoomUser.ROLE_CREATOR).exists())

    def test_room_create_post_invalid_data(self):
        initial_room_count = Room.objects.count()
        response = self.client.post(reverse('rooms:create'), {'name': '', 'description': 'New description'})
        self.assertEqual(response.status_code, 200) # Form redisplayed
        self.assertTemplateUsed(response, 'room/create.html')
        self.assertFormError(response.context['form'], 'name', ['This field is required.'])
        self.assertEqual(Room.objects.count(), initial_room_count)

class RoomPageViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_user = RoomUser.objects.create(user=self.user, room=self.room)

    def test_room_page_is_participant(self):
        response = self.client.get(reverse('rooms:room', kwargs={'room_pk': self.room.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'room/room.html')
        self.assertIn('room', response.context)
        self.assertEqual(response.context['room'], self.room)
        self.assertTrue(response.context['is_participant'])

    def test_room_page_not_participant(self):
        user2 = EclipseUser.objects.create_user(username='testuser2', password='password2')
        self.client.login(username='testuser2', password='password2')
        response = self.client.get(reverse('rooms:room', kwargs={'room_pk': self.room.pk}))
        self.assertEqual(response.status_code, 302) # Redirect to join page
        self.assertRedirects(response, reverse('rooms:room_join', kwargs={'room_pk': self.room.pk}))

class RoomJoinViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.room = Room.objects.create(name='Test Room')

    def test_room_join_get(self):
        response = self.client.get(reverse('rooms:room_join', kwargs={'room_pk': self.room.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'room/enter.html')
        self.assertIn('room', response.context)
        self.assertEqual(response.context['room'], self.room)

    def test_room_join_post(self):
        initial_room_user_count = RoomUser.objects.count()
        response = self.client.post(reverse('rooms:room_join', kwargs={'room_pk': self.room.pk}))
        self.assertEqual(response.status_code, 302) # Redirect
        self.assertEqual(RoomUser.objects.count(), initial_room_user_count + 1)
        self.assertTrue(RoomUser.objects.filter(user=self.user, room=self.room).exists())
        self.assertRedirects(response, reverse('rooms:room', kwargs={'room_pk': self.room.pk}))

class MyRoomsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')
        self.room1 = Room.objects.create(name='Room 1')
        self.room2 = Room.objects.create(name='Room 2')
        RoomUser.objects.create(user=self.user, room=self.room1)
        RoomUser.objects.create(user=self.user, room=self.room2)

    def test_my_rooms_view(self):
        response = self.client.get(reverse('rooms:my_rooms'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'room/my_rooms.html')
        self.assertIn('rooms', response.context)
        self.assertEqual(len(response.context['rooms']), 2)
        self.assertIn(self.room1, response.context['rooms'])
        self.assertIn(self.room2, response.context['rooms'])