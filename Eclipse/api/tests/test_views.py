from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from EclipseUser.models.user import EclipseUser
from EclipseRoom.models.room import Room
from EclipseRoom.models.roomuser import RoomUser
from EclipseRoom.models.roommessage import RoomMessage
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

# ... (other classes) ...

class RoomUpdateViewTest(APITestCase):
    def setUp(self):
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.moderator = EclipseUser.objects.create_user(username='moderator', password='password')
        self.user = EclipseUser.objects.create_user(username='user', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.creator_room_user = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.moderator_room_user = RoomUser.objects.create(user=self.moderator, room=self.room, role=RoomUser.ROLE_MODERATOR)
        self.user_room_user = RoomUser.objects.create(user=self.user, room=self.room, role=RoomUser.ROLE_USER)

    def test_creator_can_update_room(self):
        self.client.login(username='creator', password='password')
        url = reverse('api:roomupdate', kwargs={'room_pk': self.room.pk})
        data = {'description': 'New description'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertEqual(self.room.description, 'New description')

    def test_moderator_can_update_room(self):
        self.client.login(username='moderator', password='password')
        url = reverse('api:roomupdate', kwargs={'room_pk': self.room.pk})
        data = {'description': 'New description'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_update_room(self):
        self.client.login(username='user', password='password')
        url = reverse('api:roomupdate', kwargs={'room_pk': self.room.pk})
        data = {'description': 'New description'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_room_avatar(self):
        self.client.login(username='creator', password='password')
        url = reverse('api:roomupdate', kwargs={'room_pk': self.room.pk})

        # Create a dummy image
        image_file = io.BytesIO()
        Image.new('RGB', (100, 100), color = 'red').save(image_file, format='JPEG')
        image_file.seek(0)
        image = SimpleUploadedFile("room_avatar.jpg", image_file.read(), content_type="image/jpeg")

        data = {'avatar': image}
        response = self.client.patch(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room.refresh_from_db()
        self.assertIn('room_avatar', self.room.avatar.name)

class RoomDeleteViewTest(APITestCase):
    def setUp(self):
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.user = EclipseUser.objects.create_user(username='user', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.creator_room_user = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.user_room_user = RoomUser.objects.create(user=self.user, room=self.room, role=RoomUser.ROLE_USER)

    def test_creator_can_delete_room(self):
        self.client.login(username='creator', password='password')
        url = reverse('api:roomdelete', kwargs={'room_pk': self.room.pk})
        data = {'passphrase': 'delete Test Room'}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())

    def test_user_cannot_delete_room(self):
        self.client.login(username='user', password='password')
        url = reverse('api:roomdelete', kwargs={'room_pk': self.room.pk})
        data = {'passphrase': 'delete Test Room'}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_room_with_incorrect_passphrase(self):
        self.client.login(username='creator', password='password')
        url = reverse('api:roomdelete', kwargs={'room_pk': self.room.pk})
        data = {'passphrase': 'wrong passphrase'}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_nonexistent_room(self):
        self.client.login(username='creator', password='password')
        url = reverse('api:roomdelete', kwargs={'room_pk': 999})
        data = {'passphrase': 'delete Nonexistent Room'}
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class RoomMessageDeleteViewTest(APITestCase):
    def setUp(self):
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_user = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.message = RoomMessage.objects.create(room=self.room, room_user=self.room_user, text='Hello')
        self.client.login(username='creator', password='password')

    def test_delete_room_message(self):
        url = reverse('api:messagedelete', kwargs={'room_pk': self.room.pk, 'message_pk': self.message.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RoomMessage.objects.filter(pk=self.message.pk).exists())

    def test_delete_nonexistent_room_message(self):
        url = reverse('api:messagedelete', kwargs={'room_pk': self.room.pk, 'message_pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class RoomUserAPITest(APITestCase):
    def setUp(self):
        self.user = EclipseUser.objects.create_user(username='testuser', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_user = RoomUser.objects.create(user=self.user, room=self.room)
        self.client.login(username='testuser', password='password')

    def test_get_room_user(self):
        url = reverse('api:roomuser', kwargs={'room_pk': self.room.pk, 'roomuser_pk': self.room_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.pk)

    def test_get_nonexistent_room_user(self):
        url = reverse('api:roomuser', kwargs={'room_pk': self.room.pk, 'roomuser_pk': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class RoomUserDeleteViewTest(APITestCase):
    def setUp(self):
        self.moderator = EclipseUser.objects.create_user(username='moderator', password='password')
        self.user_to_delete = EclipseUser.objects.create_user(username='usertodelete', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_moderator = RoomUser.objects.create(user=self.moderator, room=self.room, role=RoomUser.ROLE_MODERATOR)
        self.room_user_to_delete = RoomUser.objects.create(user=self.user_to_delete, room=self.room, role=RoomUser.ROLE_USER)
        self.client.login(username='moderator', password='password')

    def test_moderator_can_delete_room_user(self):
        url = reverse('api:roomuserdelete', kwargs={'room_pk': self.room.pk, 'roomuser_pk': self.room_user_to_delete.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RoomUser.objects.filter(pk=self.room_user_to_delete.pk).exists())

    def test_moderator_cannot_delete_nonexistent_room_user(self):
        url = reverse('api:roomuserdelete', kwargs={'room_pk': self.room.pk, 'roomuser_pk': 999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class RoomUserRoleUpdateViewTest(APITestCase):
    def setUp(self):
        self.creator = EclipseUser.objects.create_user(username='creator', password='password')
        self.moderator = EclipseUser.objects.create_user(username='moderator', password='password')
        self.user_to_change = EclipseUser.objects.create_user(username='usertochange', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_creator = RoomUser.objects.create(user=self.creator, room=self.room, role=RoomUser.ROLE_CREATOR)
        self.room_moderator = RoomUser.objects.create(user=self.moderator, room=self.room, role=RoomUser.ROLE_MODERATOR)
        self.room_user_to_change = RoomUser.objects.create(user=self.user_to_change, room=self.room, role=RoomUser.ROLE_USER)
        self.client.login(username='creator', password='password')

    def test_creator_can_promote_user(self):
        url = reverse('api:roomuserrole', kwargs={'room_pk': self.room.pk, 'roomuser_pk': self.room_user_to_change.pk})
        data = {'role': 'moderator'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room_user_to_change.refresh_from_db()
        self.assertEqual(self.room_user_to_change.role, RoomUser.ROLE_MODERATOR)

    def test_creator_can_demote_moderator(self):
        self.room_user_to_change.role = RoomUser.ROLE_MODERATOR
        self.room_user_to_change.save()
        url = reverse('api:roomuserrole', kwargs={'room_pk': self.room.pk, 'roomuser_pk': self.room_user_to_change.pk})
        data = {'role': 'user'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.room_user_to_change.refresh_from_db()
        self.assertEqual(self.room_user_to_change.role, RoomUser.ROLE_USER)

    def test_invalid_role_update(self):
        url = reverse('api:roomuserrole', kwargs={'room_pk': self.room.pk, 'roomuser_pk': self.room_user_to_change.pk})
        data = {'role': 'invalid_role'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Роль должна быть: moderator или user', response.data['error'])

    def test_cannot_demote_creator(self):
        url = reverse('api:roomuserrole', kwargs={'room_pk': self.room.pk, 'roomuser_pk': self.room_creator.pk})
        data = {'role': 'user'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Нельзя понизить роль создателю', response.data['error'])

class RoomBulkUsersAPITest(APITestCase):
    def setUp(self):
        self.user1 = EclipseUser.objects.create_user(username='user1', password='password')
        self.user2 = EclipseUser.objects.create_user(username='user2', password='password')
        self.room = Room.objects.create(name='Test Room')
        self.room_user1 = RoomUser.objects.create(user=self.user1, room=self.room, role=RoomUser.ROLE_USER)
        self.room_user2 = RoomUser.objects.create(user=self.user2, room=self.room, role=RoomUser.ROLE_USER)
        self.client.login(username='user1', password='password')

    def test_get_bulk_users(self):
        url = reverse('api:roomuserbulk', kwargs={'room_pk': self.room.pk}) + f'?user_ids={self.room_user1.pk},{self.room_user2.pk}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_bulk_users_no_user_ids(self):
        url = reverse('api:roomuserbulk', kwargs={'room_pk': self.room.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Параметр 'user_ids' обязателен (например: ?user_ids=1,2,3)", response.data['error'])

    def test_get_bulk_users_invalid_user_ids_format(self):
        url = reverse('api:roomuserbulk', kwargs={'room_pk': self.room.pk}) + '?user_ids=1,abc,3'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Некорректный формат user_ids", response.data['error'])

    def test_get_bulk_users_empty_user_ids(self):
        url = reverse('api:roomuserbulk', kwargs={'room_pk': self.room.pk}) + '?user_ids='
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Параметр 'user_ids' обязателен (например: ?user_ids=1,2,3)", response.data['error'])