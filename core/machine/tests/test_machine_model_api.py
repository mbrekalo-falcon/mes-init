from core.machine.tests.__init__ import *

MACHINE_MODELS_URL = reverse('machines:machine-models')


class PublicMachineModelAPITest(TestCase):
    """Test the publicly available MachineModel API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving MachineModels"""
        response = self.client.get(MACHINE_MODELS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMachineModelsAPITests(TestCase):
    """Test the authorized user MachineModels API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_MachineModels_list(self):
        """Test retrieving MachineModels"""
        create_machine_model()
        create_machine_model(
            name="T-2020",
            note='machine from future',
        )

        response = self.client.get(MACHINE_MODELS_URL)

        machine_models = MachineModel.objects.get_queryset()
        serializer = MachineModelSerializer(machine_models, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_machine_model(self):
        """Test  creating a new MachineModel"""
        payload = {
            'name': 'Test MachineModel',
            'note': 'machine from future'
        }

        self.client.post(MACHINE_MODELS_URL, json.dumps(payload), content_type="application/json")

        exists = MachineModel.objects.get_queryset().filter(
            name=payload['name'],
            note=payload['note']
        ).exists()
        self.assertTrue(exists)
    
    def test_create_machine_model_invalid(self):
        """Test creating a new machine model with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(MACHINE_MODELS_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_machine_model_filter_queryset_search_name(self):
        """Test filter queryset MachineModels by name"""
        machine_model1 = create_machine_model()
        create_machine_model(
            name="Dangerous Machine2",
            note='machine from future',
        )

        url_name = f'{MACHINE_MODELS_URL}?search_name={machine_model1.name}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_machine_model_filter_queryset_search_name_invalid(self):
        """Test filter queryset machine models by invalid search_name input"""
        create_machine_model()
        url_name = f'{MACHINE_MODELS_URL}?search_name=invalid1'

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_machine_model_filter_queryset_instance_id(self):
        """Test filter queryset MachineModels by instance_id"""
        machine_model1 = create_machine_model()
        machine_model2 = create_machine_model(
            name="Dangerous Machine2",
            note='machine from future',
        )
        url_id_1 = f'{MACHINE_MODELS_URL}?instance_id={machine_model1.id}'
        url_id_2 = f'{MACHINE_MODELS_URL}?instance_id={machine_model2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_machine_model_filter_queryset_instance_id_invalid(self):
        """Test filter queryset machine models by invalid instance_id"""
        create_machine_model()

        url = f'{MACHINE_MODELS_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_machine_model(self):
        """Test updating a machine model with put"""
        machine_model = create_machine_model()
        payload = {
            "name": "Dangerous Machine2",
            "note": 'machine from future',
        }
        machine_model_url = f'{MACHINE_MODELS_URL}?instance_id={machine_model.id}'

        self.client.put(machine_model_url, json.dumps(payload), content_type="application/json")

        machine_model.refresh_from_db()
        self.assertEqual(machine_model.name, payload['name'])
        self.assertEqual(machine_model.note, payload['note'])

    def test_full_update_machine_model_invalid(self):
        """Test updating machine model with invalid put"""
        machine_model = create_machine_model()
        payload = {
            "name": "",
            "note": "",
        }
        machine_model_url = f'{MACHINE_MODELS_URL}?instance_id={machine_model.id}'
        response = self.client.put(machine_model_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message)

    def test_partial_update_machine_model(self):
        """Test updating a machine model with patch"""
        machine_model = create_machine_model()
        payload = {
            "name": "Dangerous Machine2",
            "note": '',
        }
        machine_model_url = f'{MACHINE_MODELS_URL}?instance_id={machine_model.id}'
        self.client.patch(machine_model_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(machine_model.name, payload['name'])

        machine_model.refresh_from_db()
        self.assertEqual(machine_model.name, payload['name'])
        self.assertEqual(machine_model.note, payload['note'])

    def test_partial_update_machine_model_invalid(self):
        """Test updating a machine_model with patch invalid"""
        machine_model = create_machine_model()
        payload = {
            "name": "",
            "note": 'some note',
        }
        machine_model_url = f'{MACHINE_MODELS_URL}?instance_id={machine_model.id}'
        response = self.client.patch(machine_model_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message)

    def test_update_machine_model_without_instance_id(self):
        """Test updating machine model when instance_id not provided"""
        payload = {
            "name": "Dangerous Machine2",
            "note": 'some note',
        }
        url = MACHINE_MODELS_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_machine_model(self):
        """Test delete machine model"""
        machine_model = create_machine_model()

        machine_model_url = f'{MACHINE_MODELS_URL}?instance_id={machine_model.id}'
        response = self.client.delete(machine_model_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_machine_model_without_instance_id(self):
        """Test delete machine model when instance_id not provided"""
        url = MACHINE_MODELS_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
