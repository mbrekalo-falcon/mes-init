from core.cluster.tests.__init__ import *

MACHINE_DEVICES_URL = reverse('clusters:machine-devices')


class PublicClusterMachineDevicesAPITest(TestCase):
    """Test the publicly available cluster machine devices API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving cluster machine devices"""
        response = self.client.get(MACHINE_DEVICES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClusterMachineDevicesPermissionsAPITests(TestCase):
    """Test the authorized cluster user module permissions roles API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_cluster_machines_devices_list(self):
        """Test retrieving cluster machines devices"""
        create_cluster_machine_device()
        create_cluster_machine_device()

        response = self.client.get(MACHINE_DEVICES_URL)

        cluster_machine_device = ClusterMachineDevice.custom_manager.get_queryset()
        serializer = ClusterMachineDeviceSerializer(cluster_machine_device, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_cluster_machine_device(self):
        """Test  creating a new cluster machine device"""
        cluster = create_cluster()
        machine = create_machine()
        device = create_device()
        printer = create_printer()

        payload = {
            "machine": machine.id,
            "cluster": cluster.id,
            "device": device.id,
            "printer": printer.id
        }

        response = self.client.post(MACHINE_DEVICES_URL, payload)
        cluster_machine_device = ClusterMachineDevice.custom_manager.get(id=response.data['data']['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cluster_machine_device.cluster, cluster)
        self.assertEqual(cluster_machine_device.machine, machine)
        self.assertEqual(cluster_machine_device.device, device)
        self.assertEqual(cluster_machine_device.printer, printer)

    def test_create_cluster_machine_device_invalid(self):
        """Test creating a new cluster machine device invalid"""
        payload = {'machine': ''}
        response = self.client.post(MACHINE_DEVICES_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cluster_machine_device_filter_queryset_search_machine_name(self):
        """Test filter queryset cluster user module permissions by machine_name"""
        cluster_machine_device = create_cluster_machine_device()
        machine = create_machine(name="machine")
        ClusterMachineDevice.custom_manager.create(
            cluster=cluster_machine_device.cluster,
            machine=machine,
            device=cluster_machine_device.device,
            printer=cluster_machine_device.printer
        )

        url_machine_name = f'{MACHINE_DEVICES_URL}?search_machine_name={machine.name}'

        response_machine_name = self.client.get(url_machine_name)
        results_machine_name = response_machine_name.data['data']['results']

        self.assertEqual(response_machine_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_machine_name), 2)
    
    def test_cluster_machine_device_filter_queryset_search_cluster_name(self):
        """Test filter queryset cluster user module permissions by cluster_name"""
        cluster_machine_device = create_cluster_machine_device()
        cluster = create_cluster(name="cluster1")
        ClusterMachineDevice.custom_manager.create(
            cluster=cluster,
            machine=cluster_machine_device.machine,
            device=cluster_machine_device.device,
            printer=cluster_machine_device.printer
        )

        url_cluster_name = f'{MACHINE_DEVICES_URL}?search_cluster_name={cluster.name}'

        response_cluster_name = self.client.get(url_cluster_name)
        results_cluster_name = response_cluster_name.data['data']['results']

        self.assertEqual(response_cluster_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_cluster_name), 2)

    def test_cluster_machine_device_filter_queryset_search_device_name(self):
        """Test filter queryset cluster user module permissions by cluster_name"""
        cluster_machine_device = create_cluster_machine_device()
        device = create_device(name="device")
        ClusterMachineDevice.custom_manager.create(
            cluster=cluster_machine_device.cluster,
            machine=cluster_machine_device.machine,
            device=device,
            printer=cluster_machine_device.printer
        )

        url_device_name = f'{MACHINE_DEVICES_URL}?search_device_name={device.name}'

        response_device_name = self.client.get(url_device_name)
        results_device_name = response_device_name.data['data']['results']

        self.assertEqual(response_device_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_device_name), 2)

    def test_cluster_machine_device_filter_queryset_search_printer_name(self):
        """Test filter queryset cluster user module permissions by printer_name"""
        cluster_machine_device = create_cluster_machine_device()
        printer = create_printer(name="Pr1nt3r")
        ClusterMachineDevice.custom_manager.create(
            cluster=cluster_machine_device.cluster,
            machine=cluster_machine_device.machine,
            device=cluster_machine_device.device,
            printer=printer
        )

        url_printer_name = f'{MACHINE_DEVICES_URL}?search_printer_name={printer.name}'

        response_printer_name = self.client.get(url_printer_name)
        results_printer_name = response_printer_name.data['data']['results']

        self.assertEqual(response_printer_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_printer_name), 1)
    
    def test_cluster_machine_devices_filter_queryset_search_machine_name_invalid(self):
        """Test filter queryset cluster machine devices by invalid search_machine_name input"""
        create_cluster_user_role()
        url_machine_name = f'{MACHINE_DEVICES_URL}?search_machine_name=invalid1'

        response_name = self.client.get(url_machine_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cluster_machine_devices_filter_queryset_search_cluster_name_invalid(self):
        """Test filter queryset cluster machine devices by invalid search_cluster_name input"""
        create_cluster_user_role()
        url_cluster_name = f'{MACHINE_DEVICES_URL}?search_machine_name=invalid1'

        response_name = self.client.get(url_cluster_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_cluster_machine_devices_filter_queryset_search_device_name_invalid(self):
        """Test filter queryset cluster machine devices by invalid search_device_name input"""
        create_cluster_user_role()
        url_device_name = f'{MACHINE_DEVICES_URL}?search_device_name=invalid1'

        response_name = self.client.get(url_device_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_cluster_machine_devices_filter_queryset_search_printer_name_invalid(self):
        """Test filter queryset cluster machine devices by invalid search_printer_name input"""
        create_cluster_user_role()
        url_printer_name = f'{MACHINE_DEVICES_URL}?search_printer_name=invalid1'

        response_name = self.client.get(url_printer_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_cluster_machine_device_filter_queryset_instance_id(self):
        """Test filter queryset cluster machine devices by instance_id"""
        cluster_machine_device1 = create_cluster_machine_device()
        cluster = create_cluster(name='cluster2')
        machine = create_machine(name='machine2')
        device = create_device(name='device2')
        printer = create_printer(name='printer2')

        cluster_machine_device2 = ClusterMachineDevice.custom_manager.create(
            cluster=cluster,
            machine=machine,
            device=device,
            printer=printer
        )

        url_id_1 = f'{MACHINE_DEVICES_URL}?instance_id={cluster_machine_device1.id}'
        url_id_2 = f'{MACHINE_DEVICES_URL}?instance_id={cluster_machine_device2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_cluster_machine_device_filter_queryset_instance_id_invalid(self):
        """Test filter queryset cluster machine device by invalid instance_id"""
        create_cluster_machine_device()

        url = f'{MACHINE_DEVICES_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_cluster_machine_device(self):
        """Test updating a cluster machine device with put"""
        cluster_machine_device = create_cluster_machine_device()
        cluster = create_cluster(name='cluster2')
        machine = create_machine(name='machine2')
        device = create_device(name='device2')
        printer = create_printer(name='printer2')

        payload = {
            "cluster": cluster.id,
            "machine": machine.id,
            'device': device.id,
            'printer': printer.id
        }
        cluster_machine_device_url = f'{MACHINE_DEVICES_URL}?instance_id={cluster_machine_device.id}'

        self.client.put(cluster_machine_device_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(cluster_machine_device.cluster, cluster)

        cluster_machine_device.refresh_from_db()

        self.assertEqual(cluster_machine_device.cluster, cluster)
        self.assertEqual(cluster_machine_device.machine, machine)
        self.assertEqual(cluster_machine_device.device, device)
        self.assertEqual(cluster_machine_device.printer, printer)

    def test_full_update_cluster_machine_device_invalid(self):
        """Test updating cluster machine device with invalid put"""
        cluster_machine_device = create_cluster_machine_device()
        payload = {
            "cluster": "",
            "machine": "",
            'device': "",
            'printer': ''
        }
        cluster_machine_device_url = f'{MACHINE_DEVICES_URL}?instance_id={cluster_machine_device.id}'
        response = self.client.put(cluster_machine_device_url, json.dumps(payload), content_type="application/json")

        cluster_error = (response.data['cluster'][0])
        machine_error = (response.data['machine'][0])
        device_error = (response.data['device'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cluster_error, machine_error, device_error)
        self.assertEqual(device_error, message)

    def test_partial_update_cluster_machine_device(self):
        """Test updating a cluster machine device with patch"""
        cluster_machine_device = create_cluster_machine_device()
        cluster = create_cluster(name='cluster2')
        device = create_device(name='device2')
        printer = create_printer(name='printer2')

        payload = {
            "cluster": cluster.id,
            "machine": cluster_machine_device.machine.id,
            'device': device.id,
            'printer': printer.id
        }
        cluster_machine_device_url = f'{MACHINE_DEVICES_URL}?instance_id={cluster_machine_device.id}'
        self.client.patch(cluster_machine_device_url, json.dumps(payload), content_type="application/json")

        cluster_machine_device.refresh_from_db()
        self.assertEqual(cluster_machine_device.cluster.name, cluster.name)
        self.assertEqual(cluster_machine_device.device.name, device.name)
        self.assertEqual(cluster_machine_device.machine.id, payload['machine'])
        self.assertEqual(cluster_machine_device.printer.name, printer.name)

    def test_partial_update_cluster_machine_device_invalid(self):
        """Test updating a cluster machine device with invalid patch"""
        cluster_machine_device = create_cluster_machine_device()
        payload = {
            "cluster": "",
            "machine": "",
            'device': ""
        }
        cluster_machine_device_url = f'{MACHINE_DEVICES_URL}?instance_id={cluster_machine_device.id}'
        response = self.client.patch(cluster_machine_device_url, json.dumps(payload), content_type="application/json")

        cluster_error = (response.data['cluster'][0])
        machine_error = (response.data['machine'][0])
        device_error = (response.data['device'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cluster_error, machine_error, device_error)
        self.assertEqual(device_error, message)

    def test_update_cluster_machine_device_without_instance_id(self):
        """Test updating cluster machine device when instance_id not provided"""
        cluster_machine_device = create_cluster_machine_device()
        cluster = create_cluster(name='cluster2')

        payload = {
            "cluster": cluster.id,
            "machine": cluster_machine_device.machine.id,
            'device': cluster_machine_device.device.id,
            'printer': cluster_machine_device.printer.id
        }

        url = MACHINE_DEVICES_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_machine_device(self):
        """Test delete cluster machine device"""
        cluster_machine_device = create_cluster_machine_device()

        cluster_machine_device_url = f'{MACHINE_DEVICES_URL}?instance_id={cluster_machine_device.id}'
        response = self.client.delete(cluster_machine_device_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_machine_device_without_instance_id(self):
        """Test delete cluster machine device when instance_id not provided"""
        url = MACHINE_DEVICES_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
