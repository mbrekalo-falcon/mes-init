from core.device.tests.__init__ import *

DEVICE_FIRMWARES_URL = reverse('devices:device-firmwares')


class PublicDeviceFirmwareAPITest(TestCase):
    """Test the publicly available device firmware API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving device firmwares"""
        response = self.client.get(DEVICE_FIRMWARES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeviceFirmwaresAPITests(TestCase):
    """Test the authorized user device firmware API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
    
    def test_retrieve_device_firmwares_list(self):
        """Test retrieving device firmwares"""
        create_device_firmware()
        create_device_firmware(
            firmware_version="new device firmware",
            firmware_note='device firmware from future'
        )

        response = self.client.get(DEVICE_FIRMWARES_URL, format='multipart')

        device_firmwares = DeviceFirmware.objects.get_queryset()
        serializer = DeviceFirmwareSerializer(device_firmwares, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']

        self.assertEqual(len(results), len(serializer.data))

    def test_create_device_firmware(self):
        """Test  creating a new device firmware"""
        device_model = create_device_model(name="test model")
        firmware = SimpleUploadedFile(name='firmware.txt', content=b"firmware file content")

        payload = {
            'firmware_version': 'Test device firmware',
            'firmware_note': 'device from future',
            'firmware': firmware,
            'device_model': device_model.id
        }

        self.client.post(DEVICE_FIRMWARES_URL, payload, format='multipart')
        
        exists = DeviceFirmware.objects.get_queryset().filter(
            firmware_version=payload['firmware_version'],
            firmware_note=payload['firmware_note'],
            device_model=payload['device_model']
        ).exists()
        self.assertTrue(exists)
    
    def test_create_device_firmware_invalid(self):
        """Test creating a new device firmware with invalid payload"""
        payload = {'firmware_version': ''}
        response = self.client.post(DEVICE_FIRMWARES_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_device_firmwares_filter_queryset_search_name(self):
        """Test filter queryset device firmwares by device_model_name or firmware_version"""
        device_firmware = create_device_firmware()
        create_device_firmware(
            firmware_version="version123",
            firmware_note='device firmware from future',
        )

        url_name = f'{DEVICE_FIRMWARES_URL}?search_name={device_firmware.firmware_version}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_device_firmware_filter_queryset_search_name_invalid(self):
        """Test filter queryset device firmwares by invalid search_name input"""
        create_device_firmware()
        url_name = f'{DEVICE_FIRMWARES_URL}?search_name=invalid1'

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_device_firmware_filter_queryset_instance_id(self):
        """Test filter queryset DeviceFirmwares by instance_id"""
        device_firmware1 = create_device_firmware()
        device_firmware2 = create_device_firmware(
            firmware_version="version123",
            firmware_note='device firmware from future'
        )
        url_id_1 = f'{DEVICE_FIRMWARES_URL}?instance_id={device_firmware1.id}'
        url_id_2 = f'{DEVICE_FIRMWARES_URL}?instance_id={device_firmware2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_device_firmware_filter_queryset_instance_id_invalid(self):
        """Test filter queryset device firmwares by invalid instance_id"""
        create_device_firmware()

        url = f'{DEVICE_FIRMWARES_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_device_firmware(self):
        """Test updating a device firmware with put"""
        device_firmware = create_device_firmware()
        device_model = create_device_model(name="test model")
        firmware = SimpleUploadedFile('test-firmware.txt', b"firmware test content")
        payload = {
            'firmware_version': 'Test device firmware',
            'firmware_note': 'device from future',
            'firmware': firmware,
            'device_model': device_model.id
        }
        device_firmware_url = f'{DEVICE_FIRMWARES_URL}?instance_id={device_firmware.id}'
        self.client.put(device_firmware_url, payload, format='multipart')

        device_firmware.refresh_from_db()
        self.assertEqual(device_firmware.firmware_version, payload['firmware_version'])
        self.assertEqual(device_firmware.firmware_note, payload['firmware_note'])
        firmware_name = os.path.splitext(str(firmware))[0]
        self.assertIn(firmware_name, str(device_firmware.firmware))
        self.assertEqual(device_firmware.device_model.id, payload['device_model'])

    def test_full_update_device_firmware_invalid(self):
        """Test updating device firmware with invalid put"""
        device_firmware = create_device_firmware()
        payload = {
            'firmware_version': '',
            'firmware_note': '',
            'firmware': '',
            'device_model': ''
        }

        device_firmware_url = f'{DEVICE_FIRMWARES_URL}?instance_id={device_firmware.id}'
        response = self.client.put(device_firmware_url, json.dumps(payload), content_type="application/json")

        firmware_version_error = response.data['firmware_version'][0]
        firmware_error = response.data['firmware'][0]
        device_model_error = response.data['device_model'][0]

        message_fv = 'This field may not be blank.'
        message_f = 'The submitted data was not a file. Check the encoding type on the form.'
        message_dm = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(firmware_version_error, message_fv)
        self.assertEqual(device_model_error, message_dm)
        self.assertEqual(firmware_error, message_f)

    def test_partial_update_device_firmware(self):
        """Test updating a device firmware with patch"""
        device_firmware = create_device_firmware()
        firmware=SimpleUploadedFile('test-firmware.txt', b"firmware test content")
        firmware_name = os.path.splitext(str(firmware))[0]

        payload = {
            'firmware_version': device_firmware.firmware_version,
            'firmware_note': device_firmware.firmware_note,
            'firmware': firmware,
            'device_model': device_firmware.device_model.id
        }

        device_firmware_url = f'{DEVICE_FIRMWARES_URL}?instance_id={device_firmware.id}'
        self.client.patch(device_firmware_url, payload, format='multipart')

        self.assertNotIn(firmware_name ,str(device_firmware.firmware))

        device_firmware.refresh_from_db()
        self.assertIn(firmware_name, str(device_firmware.firmware))
        self.assertEqual(device_firmware.firmware_note, payload['firmware_note'])
        self.assertEqual(device_firmware.firmware_version, payload['firmware_version'])
        self.assertEqual(device_firmware.device_model.id, payload['device_model'])

    def test_partial_update_device_firmware_invalid(self):
        """Test updating a device_firmware with patch invalid"""
        device_firmware = create_device_firmware()

        payload = {
            'firmware_version': device_firmware.firmware_version,
            'firmware_note': device_firmware.firmware_note,
            'firmware': '',
            'device_model': device_firmware.device_model.id
        }

        device_firmware_url = f'{DEVICE_FIRMWARES_URL}?instance_id={device_firmware.id}'
        response = self.client.patch(device_firmware_url, json.dumps(payload), content_type="application/json")

        firmware_error = (response.data['firmware'][0])
        message = "The submitted data was not a file. Check the encoding type on the form."

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(firmware_error, message)

    def test_update_device_firmware_without_instance_id(self):
        """Test updating device firmware when instance_id not provided"""
        device_firmware = create_device_firmware()

        payload = {
            'firmware_version': device_firmware.firmware_version,
            'firmware_note': device_firmware.firmware_note,
            'firmware': device_firmware.firmware,
            'device_model': device_firmware.device_model.id
        }
        url = DEVICE_FIRMWARES_URL
        response = self.client.patch(url, payload, format='multipart')
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_firmware(self):
        """Test delete device firmware"""
        device_firmware = create_device_firmware()

        device_firmware_url = f'{DEVICE_FIRMWARES_URL}?instance_id={device_firmware.id}'
        response = self.client.delete(device_firmware_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_device_firmware_without_instance_id(self):
        """Test delete device firmware when instance_id not provided"""
        url = DEVICE_FIRMWARES_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
