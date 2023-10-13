from core.device.tests.__init__ import *

COMMAND_REQUEST_URL = reverse('devices:device-command-requests')


class PublicDeviceCommandRequestPermissionsAPITest(TestCase):
    """Test the publicly available device command request permission API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving device command request permission"""
        response = self.client.get(COMMAND_REQUEST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeviceCommandRequestPermissionsAPITests(TestCase):
    """Test the authorized device command request permissions roles API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_device_command_requests_list(self):
        """Test retrieving device command request permissions"""
        create_device_command_request()
        create_device_command_request()

        response = self.client.get(COMMAND_REQUEST_URL)

        device_command_requests = DeviceCommandRequest.custom_manager.get_queryset()
        serializer = DeviceCommandRequestSerializer(device_command_requests, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_device_command_request(self):
        """Test creating a new device command request"""
        device = create_device()
        device_command = create_device_command()
        payload = {
            'device': device.id,
            'device_command': device_command.id,
            'device_command_updated': 'update this'
        }

        response = self.client.post(COMMAND_REQUEST_URL, payload)
        device_command_request = DeviceCommandRequest.custom_manager.get(id=response.data['data']['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(device_command_request.device, device)
        self.assertEqual(device_command_request.device_command, device_command)
        self.assertEqual(device_command_request.device_command_updated, payload['device_command_updated'])

    def test_create_device_command_request_invalid(self):
        """Test creating a new device command request invalid"""
        payload = {'device': ''}
        response = self.client.post(COMMAND_REQUEST_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_device_command_request_filter_queryset_search_name(self):
        """Test filter queryset device command request by device_name"""
        device_command_request = create_device_command_request()
        device = create_device(name='new device')
        device_command = create_device_command()
        DeviceCommandRequest.custom_manager.create(
            device=device,
            device_command=device_command
        )

        url_name = f'{COMMAND_REQUEST_URL}?search_name={device_command_request.device.name}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_device_command_request_filter_queryset_search_name_invalid(self):
        """Test filter queryset device command request by invalid search_name input"""
        create_device_command_request()
        url_name = f'{COMMAND_REQUEST_URL}?search_name=invalid1'

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_device_command_requests_filter_queryset_instance_id(self):
        """Test filter queryset device command request by instance_id"""
        device_command_request1 = create_device_command_request()
        device = create_device(name='new device')
        device_command = create_device_command()

        device_command_request2 = DeviceCommandRequest.custom_manager.create(
            device=device,
            device_command=device_command
        )

        url_id_1 = f'{COMMAND_REQUEST_URL}?instance_id={device_command_request1.id}'
        url_id_2 = f'{COMMAND_REQUEST_URL}?instance_id={device_command_request2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_device_command_request_filter_queryset_instance_id_invalid(self):
        """Test filter queryset device command request by invalid instance_id"""
        create_device_command_request()

        url = f'{COMMAND_REQUEST_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_device_command_request(self):
        """Test updating a device command request with put"""
        device_command_request = create_device_command_request()
        device = create_device(name='new device')
        device_command = create_device_command(name='new command')

        payload = {
            'device': device.id,
            'device_command': device_command.id,
            'device_command_updated': 'update this'
        }
        device_command_request_url = f'{COMMAND_REQUEST_URL}?instance_id={device_command_request.id}'

        self.client.put(device_command_request_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device_command_request.device, device)

        device_command_request.refresh_from_db()

        self.assertEqual(device_command_request.device, device)
        self.assertEqual(device_command_request.device_command, device_command)
        self.assertEqual(device_command_request.device_command_updated, payload['device_command_updated'])

    def test_full_update_device_command_request_invalid(self):
        """Test updating device command request with invalid put"""
        device_command_request = create_device_command_request()
        payload = {
            "device": "",
            "device_command": "",
        }
        device_command_request_url = f'{COMMAND_REQUEST_URL}?instance_id={device_command_request.id}'
        response = self.client.put(device_command_request_url, json.dumps(payload), content_type="application/json")

        device_error = (response.data['device'][0])
        device_command_error = (response.data['device_command'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(device_error, message, device_command_error)

    def test_partial_update_device_command_request(self):
        """Test updating a device command request with patch"""
        device_command_request = create_device_command_request()
        device_command = create_device_command(name='new command')

        payload = {
            "device": device_command_request.id,
            "device_command": device_command.id,
            'device_command_updated': 'update this'
        }
        device_command_request_url = f'{COMMAND_REQUEST_URL}?instance_id={device_command_request.id}'
        self.client.patch(device_command_request_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device_command_request.device_command, device_command)

        device_command_request.refresh_from_db()
        self.assertEqual(device_command_request.device_command, device_command)
        self.assertEqual(device_command_request.device_command_updated, payload['device_command_updated'])

    def test_partial_update_device_command_request_invalid(self):
        """Test updating a device command request with patch invalid"""
        device_command_request = create_device_command_request()

        payload = {
            "device": "",
            "device_command": ""
        }
        device_command_request_url = f'{COMMAND_REQUEST_URL}?instance_id={device_command_request.id}'
        response = self.client.patch(device_command_request_url, json.dumps(payload), content_type="application/json")

        device_error = (response.data['device'][0])
        device_command_error = (response.data['device_command'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(device_error, message, device_command_error)

    def test_update_device_command_request_without_instance_id(self):
        """Test updating device command request when instance_id not provided"""
        device_command_request = create_device_command_request()
        device_command = create_device_command(name='new command')

        payload = {
            "device": device_command_request.id,
            "device_command": device_command.id,
            'device_command_updated': 'update this'
        }

        url = COMMAND_REQUEST_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_command_request(self):
        """Test delete device command request"""
        device_command_request = create_device_command_request()

        device_command_request_url = f'{COMMAND_REQUEST_URL}?instance_id={device_command_request.id}'

        response = self.client.delete(device_command_request_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_device_command_request_without_instance_id(self):
        """Test delete device command request when instance_id not provided"""
        url = COMMAND_REQUEST_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
