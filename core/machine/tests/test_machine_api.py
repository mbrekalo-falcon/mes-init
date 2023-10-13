from core.machine.tests.__init__ import *

MACHINE_URL = reverse('machines:machines-list')


class PublicMachineAPITest(TestCase):
    """Test the publicly available machines API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving machines list"""
        response = self.client.get(MACHINE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMachineAPITests(TestCase):
    """Test the authorized machines API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@thefalcontech.com',
            'password123',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_clusters_users_list(self):
        """Test retrieving machines"""
        create_machine()
        create_machine()
        response = self.client.get(MACHINE_URL)

        clusters = Machine.custom_manager.get_queryset()
        serializer = MachineSerializer(clusters, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_machine(self):
        """Test creating a new machine"""
        machine_model = create_machine_model()
        cluster = create_cluster()

        payload = {
            "name": "T-4000",
            "ip": "123.123.123.123",
            "note": "new one",
            "cluster": cluster.id,
            "machine_model": machine_model.id
        }

        response = self.client.post(MACHINE_URL, payload)
        machine = Machine.custom_manager.get(id=response.data['data']['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(machine.name, payload['name'])
        self.assertEqual(machine.ip, payload['ip'])
        self.assertEqual(machine.note, payload['note'])
        self.assertEqual(machine.machine_model, machine_model)

    def test_create_machine_invalid(self):
        """Test creating a new machine with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(MACHINE_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_machines_filter_queryset_search_name(self):
        """Test filter queryset machines by name or machine_model_name"""
        machine = create_machine()
        create_machine(name="new machine")

        url_name = f'{MACHINE_URL}?search_name={machine.name}'
        url_machine_model_name = f'{MACHINE_URL}?search_name={machine.machine_model.name}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        response_machine_model_name = self.client.get(url_machine_model_name)
        results_machine_model_name = response_machine_model_name.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(response_machine_model_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 1)
        self.assertEqual(len(results_machine_model_name), 2)
    
    def test_clusters_users_filter_queryset_search_name_invalid(self):
        """Test filter queryset machines by invalid search_name input"""
        create_machine()
        url_name = f'{MACHINE_URL}?search_name=invalid1'
        url_machine_model_name = f'{MACHINE_URL}?search_name=invalidModel1'

        response_name = self.client.get(url_name)
        response_machine_model_name = self.client.get(url_machine_model_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_machine_model_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_machines_filter_queryset_instance_id(self):
        """Test filter queryset machines by instance_id"""
        machine1 = create_machine()
        machine2 = create_machine(name="new machine")

        url_id_1 = f'{MACHINE_URL}?instance_id={machine1.id}'
        url_id_2 = f'{MACHINE_URL}?instance_id={machine2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_machines_filter_queryset_instance_id_invalid(self):
        """Test filter queryset machines by invalid instance_id"""
        create_machine()

        url = f'{MACHINE_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_machine(self):
        """Test updating a machine with put"""
        machine = create_machine()
        machine_model = create_machine_model(name="soft machine")
        cluster = create_cluster()

        payload = {
            "name": "T-4000",
            "ip": "123.123.123.123",
            "note": "simple note",
            "machine_model": machine_model.id,
            'cluster': cluster.id
        }
        machine_url = f'{MACHINE_URL}?instance_id={machine.id}'

        self.client.put(machine_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(machine.machine_model.name, machine_model.name)

        machine.refresh_from_db()

        self.assertEqual(machine.machine_model.name, machine_model.name)
        self.assertEqual(machine.cluster.id, cluster.id)
        self.assertEqual(machine.name, payload['name'])
        self.assertEqual(machine.ip, payload['ip'])
        self.assertEqual(machine.note, payload['note'])

    def test_full_update_machine_invalid(self):
        """Test updating machine with invalid put"""
        machine = create_machine()
        payload = {
            "name": "",
            "machine_model": "",
            'cluster': ''
        }
        machine_url = f'{MACHINE_URL}?instance_id={machine.id}'
        response = self.client.put(machine_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        machine_model_error = (response.data['machine_model'][0])
        message = 'This field may not be blank.'
        cluster_error = (response.data['cluster'][0])
        cluster_msg = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message, machine_model_error)
        self.assertEqual(cluster_error, cluster_msg)

    def test_partial_update_machine(self):
        """Test updating a machine with patch"""
        machine = create_machine()
        machine_model = create_machine_model(name="soft machine")
        cluster = create_cluster()
        payload = {
            "name": "T-4000",
            "machine_model": machine_model.id,
            'cluster': cluster.id
        }
        machine_url = f'{MACHINE_URL}?instance_id={machine.id}'
        self.client.patch(machine_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(machine.name, payload['name'])
        self.assertNotEqual(machine.cluster, payload['cluster'])

        machine.refresh_from_db()
        self.assertEqual(machine.machine_model.name, machine_model.name)
        self.assertEqual(machine.name, payload['name'])
        self.assertEqual(machine.cluster.id, payload['cluster'])

    def test_partial_update_machine_invalid(self):
        """Test updating a machine with invalid patch"""
        machine = create_machine()
        payload = {
            "name": "",
            "machine_model": "",
            'cluster': ''
        }
        machine_url = f'{MACHINE_URL}?instance_id={machine.id}'
        response = self.client.patch(machine_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        address_error = (response.data['machine_model'][0])
        message = 'This field may not be blank.'
        cluster_error = (response.data['cluster'][0])
        cluster_msg = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message, address_error)
        self.assertEqual(cluster_error, cluster_msg)

    def test_update_machine_without_instance_id(self):
        """Test updating machine when instance_id not provided"""
        create_machine()
        machine_model = create_machine_model(name="soft machine")
        cluster = create_cluster()
        payload = {
            "name": "T-4000",
            "machine_model": machine_model.id,
            'cluster': cluster.id
        }
        url = MACHINE_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_machine(self):
        """Test delete machine"""
        machine = create_machine()

        machine_url = f'{MACHINE_URL}?instance_id={machine.id}'
        response = self.client.delete(machine_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_machine_without_instance_id(self):
        """Test delete machine when instance_id not provided"""
        url = MACHINE_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)