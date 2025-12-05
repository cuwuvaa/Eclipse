from django.test import TestCase
from EclipseRoom.models.room import Room
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.roommessage import RoomMessage
from EclipseUser.models.user import EclipseUser

class RoomModelTest(TestCase):
    def test_save_assigns_default_avatar(self):
        room = Room.objects.create(name='Test Room')
        print(room.avatar.name)
        self.assertTrue(room.avatar.name.startswith('rooms/defaults/room'))

class RoomUserModelTest(TestCase):
    def setUp(self):
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.room = Room.objects.create(name='Test Room')

    def test_room_user_creation(self):
        room_user = RoomUser.objects.create(user=self.user, room=self.room)
        self.assertEqual(room_user.user, self.user)
        self.assertEqual(room_user.room, self.room)
        self.assertEqual(room_user.role, RoomUser.ROLE_USER)

class RoomMessageModelTest(TestCase):
    def setUp(self):
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_user = RoomUser.objects.create(user=self.user, room=self.room)

    def test_room_message_creation(self):
        message = RoomMessage.objects.create(room=self.room, room_user=self.room_user, text='Hello')
        self.assertEqual(message.room, self.room)
        self.assertEqual(message.room_user, self.room_user)
        self.assertEqual(message.text, 'Hello')
