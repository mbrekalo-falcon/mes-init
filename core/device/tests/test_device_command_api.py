from core.device.tests.__init__ import *

DEVICE_COMMANDS_URL = reverse('devices:device-commands')


class PublicDeviceCommandAPITest(TestCase):
    """Test the publicly available device command API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving device commands"""
        response = self.client.get(DEVICE_COMMANDS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeviceCommandsAPITests(TestCase):
    """Test the authorized user device command API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_device_commands_list(self):
        """Test retrieving device commands"""
        create_device_command()
        create_device_command(
            name="new device command",
            note='device command from future',
            default_value="commandos"
        )

        response = self.client.get(DEVICE_COMMANDS_URL)

        device_commands = DeviceCommand.objects.get_queryset()
        serializer = DeviceCommandSerializer(device_commands, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_device_command(self):
        """Test  creating a new device command"""
        payload = {
            'name': 'Test device command',
            'note': 'device from future',
            'default_value': 'def value'
        }

        self.client.post(DEVICE_COMMANDS_URL, json.dumps(payload), content_type="application/json")

        exists = DeviceCommand.objects.get_queryset().filter(
            name=payload['name'],
            note=payload['note'],
            default_value=payload['default_value']
        ).exists()
        self.assertTrue(exists)
    
    def test_create_device_command_invalid(self):
        """Test creating a new device command with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(DEVICE_COMMANDS_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_device_command_filter_queryset_search_name(self):
        """Test filter queryset device commands by name"""
        device_command = create_device_command()
        create_device_command(
            name="new device command",
            note='device command from future',
            default_value="commandos"
        )

        url_name = f'{DEVICE_COMMANDS_URL}?search_name={device_command.name}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_device_command_filter_queryset_search_name_invalid(self):
        """Test filter queryset device commands by invalid search_name input"""
        create_device_command()
        url_name = f'{DEVICE_COMMANDS_URL}?search_name=invalid1'

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_device_command_filter_queryset_instance_id(self):
        """Test filter queryset DeviceCommands by instance_id"""
        device_command1 = create_device_command()
        device_command2 = create_device_command(
            name="Dangerous device2",
            note='device from future',
            default_value="commandos"
        )
        url_id_1 = f'{DEVICE_COMMANDS_URL}?instance_id={device_command1.id}'
        url_id_2 = f'{DEVICE_COMMANDS_URL}?instance_id={device_command2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_device_command_filter_queryset_instance_id_invalid(self):
        """Test filter queryset device commands by invalid instance_id"""
        create_device_command()

        url = f'{DEVICE_COMMANDS_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_device_command(self):
        """Test updating a device command with put"""
        device_command = create_device_command()
        payload = {
            'name': 'Test device command',
            'note': 'device from future',
            'default_value': 'def value'
        }
        device_command_url = f'{DEVICE_COMMANDS_URL}?instance_id={device_command.id}'

        self.client.put(device_command_url, json.dumps(payload), content_type="application/json")

        device_command.refresh_from_db()
        self.assertEqual(device_command.name, payload['name'])
        self.assertEqual(device_command.note, payload['note'])
        self.assertEqual(device_command.default_value, payload['default_value'])

    def test_full_update_device_command_invalid(self):
        """Test updating device command with invalid put"""
        device_command = create_device_command()
        payload = {
            "name": "",
            "note": "",
            "default_value": ""
        }
        device_command_url = f'{DEVICE_COMMANDS_URL}?instance_id={device_command.id}'
        response = self.client.put(device_command_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message)

    def test_partial_update_device_command(self):
        """Test updating a device command with patch"""
        device_command = create_device_command()
        payload = {
            'name': 'Test device command',
            'note': '',
            'default_value': 'def value'
        }
        device_command_url = f'{DEVICE_COMMANDS_URL}?instance_id={device_command.id}'
        self.client.patch(device_command_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device_command.name, payload['name'])

        device_command.refresh_from_db()
        self.assertEqual(device_command.name, payload['name'])
        self.assertEqual(device_command.note, payload['note'])
        self.assertEqual(device_command.default_value, payload['default_value'])

    def test_partial_update_device_command_invalid(self):
        """Test updating a device_command with patch invalid"""
        device_command = create_device_command()
        payload = {
            "name": "",
            "note": 'some note',
            'default_value': ''
        }
        device_command_url = f'{DEVICE_COMMANDS_URL}?instance_id={device_command.id}'
        response = self.client.patch(device_command_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message)

    def test_update_device_command_without_instance_id(self):
        """Test updating device command when instance_id not provided"""
        payload = {
            'name': 'Test device command',
            'note': 'device from future',
            'default_value': 'def value'
        }
        url = DEVICE_COMMANDS_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_command(self):
        """Test delete device command"""
        device_command = create_device_command()

        device_command_url = f'{DEVICE_COMMANDS_URL}?instance_id={device_command.id}'
        response = self.client.delete(device_command_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_command_without_instance_id(self):
        """Test delete device command when instance_id not provided"""
        url = DEVICE_COMMANDS_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
