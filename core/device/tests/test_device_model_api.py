from core.device.tests.__init__ import *

DEVICE_MODELS_URL = reverse('devices:device-models')


class PublicDeviceModelAPITest(TestCase):
    """Test the publicly available device model API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving device models"""
        response = self.client.get(DEVICE_MODELS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeviceModelsAPITests(TestCase):
    """Test the authorized user device model API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_device_models_list(self):
        """Test retrieving device models"""
        create_device_model()
        create_device_model(
            name="new device",
            note='device from future',
        )

        response = self.client.get(DEVICE_MODELS_URL)

        device_models = DeviceModel.objects.get_queryset()
        serializer = DeviceModelSerializer(device_models, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_device_model(self):
        """Test  creating a new device model"""
        payload = {
            'name': 'Test device model',
            'note': 'device from future'
        }

        self.client.post(DEVICE_MODELS_URL, json.dumps(payload), content_type="application/json")

        exists = DeviceModel.objects.get_queryset().filter(
            name=payload['name'],
            note=payload['note']
        ).exists()
        self.assertTrue(exists)
    
    def test_create_device_model_invalid(self):
        """Test creating a new device model with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(DEVICE_MODELS_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_device_model_filter_queryset_search_name(self):
        """Test filter queryset device models by name"""
        device_model = create_device_model()
        create_device_model(
            name="fast model T-2000",
            note='device from future',
        )

        url_name = f'{DEVICE_MODELS_URL}?search_name={device_model.name}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_device_model_filter_queryset_search_name_invalid(self):
        """Test filter queryset device models by invalid search_name input"""
        create_device_model()
        url_name = f'{DEVICE_MODELS_URL}?search_name=invalid1'

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_device_model_filter_queryset_instance_id(self):
        """Test filter queryset DeviceModels by instance_id"""
        device_model1 = create_device_model()
        device_model2 = create_device_model(
            name="Dangerous device2",
            note='device from future',
        )
        url_id_1 = f'{DEVICE_MODELS_URL}?instance_id={device_model1.id}'
        url_id_2 = f'{DEVICE_MODELS_URL}?instance_id={device_model2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_device_model_filter_queryset_instance_id_invalid(self):
        """Test filter queryset device models by invalid instance_id"""
        create_device_model()

        url = f'{DEVICE_MODELS_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_device_model(self):
        """Test updating a device model with put"""
        device_model = create_device_model()
        payload = {
            "name": "Dangerous device2",
            "note": 'device from future',
        }
        device_model_url = f'{DEVICE_MODELS_URL}?instance_id={device_model.id}'

        self.client.put(device_model_url, json.dumps(payload), content_type="application/json")

        device_model.refresh_from_db()
        self.assertEqual(device_model.name, payload['name'])
        self.assertEqual(device_model.note, payload['note'])

    def test_full_update_device_model_invalid(self):
        """Test updating device model with invalid put"""
        device_model = create_device_model()
        payload = {
            "name": "",
            "note": "",
        }
        device_model_url = f'{DEVICE_MODELS_URL}?instance_id={device_model.id}'
        response = self.client.put(device_model_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message)

    def test_partial_update_device_model(self):
        """Test updating a device model with patch"""
        device_model = create_device_model()
        payload = {
            "name": "Dangerous Device2",
            "note": 'device from outer space',
        }
        device_model_url = f'{DEVICE_MODELS_URL}?instance_id={device_model.id}'
        self.client.patch(device_model_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device_model.name, payload['name'])

        device_model.refresh_from_db()
        self.assertEqual(device_model.name, payload['name'])
        self.assertEqual(device_model.note, payload['note'])

    def test_partial_update_device_model_invalid(self):
        """Test updating a device_model with patch invalid"""
        device_model = create_device_model()
        payload = {
            "name": "",
            "note": 'some note',
        }
        device_model_url = f'{DEVICE_MODELS_URL}?instance_id={device_model.id}'
        response = self.client.patch(device_model_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message)

    def test_update_device_model_without_instance_id(self):
        """Test updating device model when instance_id not provided"""
        payload = {
            "name": "Dangerous device2",
            "note": 'some note',
        }
        url = DEVICE_MODELS_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_model(self):
        """Test delete device model"""
        device_model = create_device_model()

        device_model_url = f'{DEVICE_MODELS_URL}?instance_id={device_model.id}'
        response = self.client.delete(device_model_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_model_without_instance_id(self):
        """Test delete device model when instance_id not provided"""
        url = DEVICE_MODELS_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
