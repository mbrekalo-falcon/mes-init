from core.device.tests.__init__ import *

COMMAND_RESPONSE_URL = reverse('devices:device-command-responses')


class PublicDeviceCommandResponsePermissionsAPITest(TestCase):
    """Test the publicly available device command response permission API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving device command response permission"""
        response = self.client.get(COMMAND_RESPONSE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeviceCommandResponsePermissionsAPITests(TestCase):
    """Test the authorized device command response permissions roles API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_device_command_responses_list(self):
        """Test retrieving device command response permissions"""
        create_device_command_response()
        create_device_command_response()

        response = self.client.get(COMMAND_RESPONSE_URL)

        device_command_responses = DeviceCommandResponse.custom_manager.get_queryset()
        serializer = DeviceCommandResponseSerializer(device_command_responses, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_device_command_response(self):
        """Test creating a new device command response"""
        device_command_request=create_device_command_request()
        payload = {
            "response_at": "2021-07-28T08:25:41Z",
            "applied": True,
            "response_message": "this is device command response",
            "device_command_request": device_command_request.id
        }

        response = self.client.post(COMMAND_RESPONSE_URL, json.dumps(payload), content_type="application/json")
        device_command_response = DeviceCommandResponse.custom_manager.get(id=response.data['data']['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(device_command_response.device_command_request, device_command_request)
        date = parser.isoparse(payload['response_at'])
        self.assertEqual(device_command_response.response_at, date)
        self.assertEqual(device_command_response.applied, payload['applied'])
        self.assertEqual(device_command_response.response_message, payload['response_message'])
            
    def test_create_device_command_response_invalid(self):
        """Test creating a new device command response permission invalid"""
        payload = {'response_at': ''}
        response = self.client.post(COMMAND_RESPONSE_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_device_command_response_filter_queryset_search_name(self):
        """Test filter queryset device command response by device_name"""
        device_command_response = create_device_command_response()
        device = create_device(name='new device')
        device_command_request = DeviceCommandRequest.custom_manager.create(
                                 device=device, device_command=create_device_command())
        DeviceCommandResponse.custom_manager.create(
            device_command_request=device_command_request,
            response_at="2021-07-28T08:25:41Z"
        )

        url_name = f'{COMMAND_RESPONSE_URL}?search_name={device_command_response.device_command_request.device.name}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']
        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_device_command_response_filter_queryset_search_name_invalid(self):
        """Test filter queryset device command response by invalid search_name input"""
        create_device_command_response()
        url_name = f'{COMMAND_RESPONSE_URL}?search_name=invalid1'

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_device_command_responses_filter_queryset_instance_id(self):
        """Test filter queryset device command response by instance_id"""
        device_command_response1 = create_device_command_response()
        device_command_response2 = create_device_command_response()

        url_id_1 = f'{COMMAND_RESPONSE_URL}?instance_id={device_command_response1.id}'
        url_id_2 = f'{COMMAND_RESPONSE_URL}?instance_id={device_command_response2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_device_command_response_filter_queryset_instance_id_invalid(self):
        """Test filter queryset device command response by invalid instance_id"""
        create_device_command_response()

        url = f'{COMMAND_RESPONSE_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_device_command_response(self):
        """Test updating a device command response with put"""
        device_command_response = create_device_command_response()
        device_command_request=create_device_command_request()

        payload = {
            "response_at": "2021-07-28T08:25:41Z",
            "applied": True,
            "response_message": "this is device command response",
            "device_command_request": device_command_request.id
        }

        device_command_response_url = f'{COMMAND_RESPONSE_URL}?instance_id={device_command_response.id}'

        self.client.put(device_command_response_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device_command_response.device_command_request, device_command_request)

        device_command_response.refresh_from_db()

        self.assertEqual(device_command_response.device_command_request, device_command_request)
        date = parser.isoparse(payload['response_at'])
        self.assertEqual(device_command_response.response_at, date)
        self.assertEqual(device_command_response.applied, payload['applied'])
        self.assertEqual(device_command_response.response_message, payload['response_message'])

    def test_full_update_device_command_response_invalid(self):
        """Test updating device command response with invalid put"""
        device_command_response = create_device_command_response()
        payload = {
            "response_at": "",
            "device_command_request": "",
        }
        device_command_response_url = f'{COMMAND_RESPONSE_URL}?instance_id={device_command_response.id}'
        response = self.client.put(device_command_response_url, json.dumps(payload), content_type="application/json")

        response_at_error = (response.data['response_at'][0])
        device_command_request_error = (response.data['device_command_request'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Datetime has wrong format.', response_at_error)
        self.assertEqual(message, device_command_request_error)

    def test_partial_update_device_command_response(self):
        """Test updating a device command response with patch"""
        device_command_response = create_device_command_response()
        device = create_device(name='dev123', identifier='12')
        device_command_request = DeviceCommandRequest.custom_manager.create(
                                    device=device,
                                    device_command=create_device_command()
                                )
        payload = {
            "response_at": device_command_response.response_at,
            "applied": True,
            "response_message": device_command_response.response_message,
            "device_command_request": device_command_request.id
        }

        device_command_response_url = f'{COMMAND_RESPONSE_URL}?instance_id={device_command_response.id}'
        self.client.patch(device_command_response_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device_command_response.device_command_request, device_command_request)

        device_command_response.refresh_from_db()
        self.assertEqual(device_command_response.device_command_request, device_command_request)
        self.assertEqual(device_command_response.response_message, payload['response_message'])
        date = parser.isoparse(payload['response_at'])
        self.assertEqual(device_command_response.response_at, date)

    def test_partial_update_device_command_response_invalid(self):
        """Test updating a device command response with patch invalid"""
        device_command_response = create_device_command_response()

        payload = {
            "response_at": "",
            "device_command_request": ""
        }
        device_command_resp_url = f'{COMMAND_RESPONSE_URL}?instance_id={device_command_response.id}'
        response = self.client.patch(device_command_resp_url, json.dumps(payload), content_type="application/json")

        device_command_request_error = (response.data['device_command_request'][0])
        response_at_error = (response.data['response_at'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Datetime has wrong format.', response_at_error)
        self.assertEqual(device_command_request_error, message)

    def test_update_device_command_response_without_instance_id(self):
        """Test updating device command response when instance_id not provided"""
        device_command_response = create_device_command_response()
        device_command_request = create_device_command_request()

        payload = {
            "device_command_request": device_command_request.id,
        }

        url = COMMAND_RESPONSE_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_command_response(self):
        """Test delete device command response"""
        device_command_response = create_device_command_response()

        device_command_response_url = f'{COMMAND_RESPONSE_URL}?instance_id={device_command_response.id}'

        response = self.client.delete(device_command_response_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_device_command_response_without_instance_id(self):
        """Test delete device command response when instance_id not provided"""
        url = COMMAND_RESPONSE_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
