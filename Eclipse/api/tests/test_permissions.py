from django.test import TestCase
from rest_framework.test import APIRequestFactory
from EclipseUser.models.user import EclipseUser
from EclipseRoom.models.room import Room
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.roommessage import RoomMessage
from api.util.permissions import IsRoomAdminOrCreator, IsRoomCreator, IsModerator, RoleChange, IsRoomMember
from django.contrib.auth.models import AnonymousUser

class PermissionTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.moderator = EclipseUser.objects.create_user(username='moderator', password='password')
        self.user = EclipseUser.objects.create_user(username='user', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_creator = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.room_moderator = RoomUser.objects.create(user=self.moderator, room=self.room, role=RoomUser.ROLE_MODERATOR)
        self.room_user = RoomUser.objects.create(user=self.user, room=self.room, role=RoomUser.ROLE_USER)
        self.message = RoomMessage.objects.create(room=self.room, room_user=self.room_user, text='Hello')

    def test_is_room_admin_or_creator_for_room_message(self):
        # Creator of the room
        request = self.factory.get('/')
        request.user = self.creator
        permission = IsRoomAdminOrCreator()
        self.assertTrue(permission.has_object_permission(request, None, self.message))

        # Moderator of the room
        request = self.factory.get('/')
        request.user = self.moderator
        permission = IsRoomAdminOrCreator()
        self.assertTrue(permission.has_object_permission(request, None, self.message))

        # User who sent the message
        request = self.factory.get('/')
        request.user = self.user
        permission = IsRoomAdminOrCreator()
        self.assertTrue(permission.has_object_permission(request, None, self.message))

        # Other user
        other_user = EclipseUser.objects.create_user(username='other', password='password')
        request = self.factory.get('/')
        request.user = other_user
        permission = IsRoomAdminOrCreator()
        self.assertFalse(permission.has_object_permission(request, None, self.message))

    def test_is_room_admin_or_creator_for_room(self):
        # Creator of the room
        request = self.factory.get('/')
        request.user = self.creator
        permission = IsRoomAdminOrCreator()
        self.assertTrue(permission.has_object_permission(request, None, self.room))

        # Moderator of the room
        request = self.factory.get('/')
        request.user = self.moderator
        permission = IsRoomAdminOrCreator()
        self.assertTrue(permission.has_object_permission(request, None, self.room))

        # Regular member of the room
        request = self.factory.get('/')
        request.user = self.user
        permission = IsRoomAdminOrCreator()
        self.assertFalse(permission.has_object_permission(request, None, self.room))

        # Other user
        other_user = EclipseUser.objects.create_user(username='other', password='password')
        request = self.factory.get('/')
        request.user = other_user
        permission = IsRoomAdminOrCreator()
        self.assertFalse(permission.has_object_permission(request, None, self.room))

class IsRoomCreatorTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.user = EclipseUser.objects.create_user(username='user', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_creator = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.room_user = RoomUser.objects.create(user=self.user, room=self.room, role=RoomUser.ROLE_USER)

    def test_is_room_creator_permission(self):
        # Creator can delete
        request = self.factory.get('/')
        request.user = self.creator
        permission = IsRoomCreator()
        self.assertTrue(permission.has_object_permission(request, None, self.room))

        # Regular user cannot delete
        request = self.factory.get('/')
        request.user = self.user
        permission = IsRoomCreator()
        self.assertFalse(permission.has_object_permission(request, None, self.room))

        # Unauthorized user
        other_user = EclipseUser.objects.create_user(username='other', password='password')
        request = self.factory.get('/')
        request.user = other_user
        permission = IsRoomCreator()
        self.assertFalse(permission.has_object_permission(request, None, self.room))

class IsModeratorTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.moderator = EclipseUser.objects.create_user(username='moderator', password='password')
        self.user = EclipseUser.objects.create_user(username='user', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_creator = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.room_moderator = RoomUser.objects.create(user=self.moderator, room=self.room, role=RoomUser.ROLE_MODERATOR)
        self.room_user = RoomUser.objects.create(user=self.user, room=self.room, role=RoomUser.ROLE_USER)
        self.message = RoomMessage.objects.create(room=self.room, room_user=self.room_user, text='Hello')

    def test_is_moderator_permission(self):
        # Creator
        request = self.factory.get('/')
        request.user = self.creator
        permission = IsModerator()
        self.assertTrue(permission.has_object_permission(request, None, self.room_user))

        # Moderator
        request = self.factory.get('/')
        request.user = self.moderator
        permission = IsModerator()
        self.assertTrue(permission.has_object_permission(request, None, self.room_user))

        # Regular user
        request = self.factory.get('/')
        request.user = self.user
        permission = IsModerator()
        self.assertFalse(permission.has_object_permission(request, None, self.room_user))

        # Trying to change creator
        request = self.factory.get('/')
        request.user = self.moderator
        permission = IsModerator()
        self.assertFalse(permission.has_object_permission(request, None, self.room_creator))

class RoleChangeTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.moderator = EclipseUser.objects.create_user(username='moderator', password='password')
        self.user1 = EclipseUser.objects.create_user(username='user1', password='password')
        self.user2 = EclipseUser.objects.create_user(username='user2', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_creator = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.room_moderator = RoomUser.objects.create(user=self.moderator, room=self.room, role=RoomUser.ROLE_MODERATOR)
        self.room_user1 = RoomUser.objects.create(user=self.user1, room=self.room, role=RoomUser.ROLE_USER)
        self.room_user2 = RoomUser.objects.create(user=self.user2, room=self.room, role=RoomUser.ROLE_USER)

    def test_creator_can_change_role_of_user(self):
        request = self.factory.patch('/')
        request.user = self.creator
        permission = RoleChange()
        self.assertTrue(permission.has_object_permission(request, None, self.room_user1))

    def test_moderator_can_change_role_of_user(self):
        request = self.factory.patch('/')
        request.user = self.moderator
        permission = RoleChange()
        self.assertTrue(permission.has_object_permission(request, None, self.room_user1))

    def test_user_cannot_change_role_of_user(self):
        request = self.factory.patch('/')
        request.user = self.user1
        permission = RoleChange()
        self.assertFalse(permission.has_object_permission(request, None, self.room_user2))

    def test_cannot_change_role_of_creator(self):
        request = self.factory.patch('/')
        request.user = self.moderator
        permission = RoleChange()
        self.assertFalse(permission.has_object_permission(request, None, self.room_creator))
    
    def test_cannot_change_own_role(self):
        request = self.factory.patch('/')
        request.user = self.creator
        permission = RoleChange()
        self.assertFalse(permission.has_object_permission(request, None, self.room_creator))

class IsRoomMemberTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_user = RoomUser.objects.create(user=self.user, room=self.room, role=RoomUser.ROLE_USER)

    def test_is_room_member_has_permission(self):
        # Authenticated member
        request = self.factory.get('/')
        request.user = self.user
        permission = IsRoomMember()
        view_mock = type('ViewMock', (object,), {'kwargs': {'room_pk': self.room.pk}})()
        self.assertTrue(permission.has_permission(request, view_mock))

        # Unauthenticated user
        request = self.factory.get('/')
        request.user = AnonymousUser()
        self.assertFalse(permission.has_permission(request, view_mock))

        # Authenticated non-member
        other_user = EclipseUser.objects.create_user(username='other', password='password')
        request = self.factory.get('/')
        request.user = other_user
        self.assertFalse(permission.has_permission(request, view_mock))

        # No room_pk in kwargs
        request = self.factory.get('/')
        request.user = self.user
        view_mock_no_room_pk = type('ViewMock', (object,), {'kwargs': {}})()
        self.assertFalse(permission.has_permission(request, view_mock_no_room_pk))
