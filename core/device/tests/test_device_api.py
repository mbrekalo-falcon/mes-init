from core.device.tests.__init__ import *

DEVICES_URL = reverse("devices:devices-list")


class PublicDevicePermissionsAPITest(TestCase):
    """Test the publicly available device permission API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving device permission"""
        response = self.client.get(DEVICES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDevicePermissionsAPITests(TestCase):
    """Test the authorized device permissions roles API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "password123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_device_list(self):
        """Test retrieving device permissions"""
        create_device()
        create_device()

        response = self.client.get(DEVICES_URL)

        devices = Device.custom_manager.get_queryset()
        serializer = DeviceSerializer(devices, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(serializer.data, results)

    def test_create_device(self):
        """Test creating a new device"""
        device_model = create_device_model()
        firmware = create_device_firmware()
        payload = {
            "name": "test device",
            "identifier": "1234",
            "device_model": device_model.id,
            "firmware": firmware.id,
        }

        response = self.client.post(DEVICES_URL, payload)
        device = Device.custom_manager.get(id=response.data["data"]["id"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(device.device_model, device_model)
        self.assertEqual(device.firmware, firmware)
        self.assertEqual(device.name, payload["name"])
        self.assertEqual(device.identifier, payload["identifier"])

    def test_create_device_invalid(self):
        """Test creating a new device invalid"""
        payload = {"name": ""}
        response = self.client.post(DEVICES_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_device_filter_queryset_search_name(self):
        """Test filter queryset device by name"""
        device = create_device()
        create_device(name="new device")

        url_name = f"{DEVICES_URL}?search_name={device.name}"

        response_name = self.client.get(url_name)
        results_name = response_name.data["data"]["results"]

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_device_filter_queryset_search_name_invalid(self):
        """Test filter queryset device by invalid search_name input"""
        create_device()
        url_name = f"{DEVICES_URL}?search_name=invalid1"

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_devices_filter_queryset_instance_id(self):
        """Test filter queryset device by instance_id"""
        device1 = create_device()
        device2 = create_device(name="new device")

        url_id_1 = f"{DEVICES_URL}?instance_id={device1.id}"
        url_id_2 = f"{DEVICES_URL}?instance_id={device2.id}"

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data["data"]["results"][0]["id"]
        results_id_2 = response_id_2.data["data"]["results"][0]["id"]

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_device_filter_queryset_instance_id_invalid(self):
        """Test filter queryset device by invalid instance_id"""
        create_device()

        url = f"{DEVICES_URL}?instance_id=2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_device(self):
        """Test updating a device with put"""
        device = create_device()
        firmware=create_device_firmware()
        device_model=create_device_model()

        payload = {
            "name": "test device",
            "identifier": "1234",
            "device_model": device_model.id,
            "firmware": firmware.id,
        }
        device_url = f"{DEVICES_URL}?instance_id={device.id}"

        self.client.put(device_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device.firmware, firmware)

        device.refresh_from_db()

        self.assertEqual(device.firmware, firmware)
        self.assertEqual(device.device_model, device_model)
        self.assertEqual(device.name, payload["name"])
        self.assertEqual(device.identifier, payload["identifier"])

    def test_full_update_device_invalid(self):
        """Test updating device with invalid put"""
        device = create_device()
        payload = {
            "name": "",
            "identifier": "",
            "device_model": "",
            "firmware": ""
        }

        device_url = f"{DEVICES_URL}?instance_id={device.id}"
        response = self.client.put(device_url, json.dumps(payload), content_type="application/json")

        device_model_error = (response.data["device_model"][0])
        firmware_error = (response.data["firmware"][0])
        message_fd = "This field may not be null."
        name_error = (response.data["name"][0])
        identifier_error = (response.data["identifier"][0])
        message_ni = "This field may not be blank."

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(device_model_error, message_fd, firmware_error)
        self.assertEqual(name_error, identifier_error, message_ni)

    def test_partial_update_device(self):
        """Test updating a device with patch"""
        device = create_device()
        device_model=create_device_model(name="test model")

        payload = {
            "name": "my own devices",
            "identifier": device.identifier,
            "device_model": device_model.id,
            "firmware": device.firmware.id
        }
        device_url = f"{DEVICES_URL}?instance_id={device.id}"
        self.client.patch(device_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(device.device_model, device_model)

        device.refresh_from_db()
        self.assertEqual(device.device_model, device_model)
        self.assertEqual(device.name, payload["name"])

    def test_partial_update_device_invalid(self):
        """Test updating a device with patch invalid"""
        device = create_device()

        payload = {
            "name": "",
            "identifier": "",
            "device_model": device.device_model.id,
            "firmware": ""
        }
        device_url = f"{DEVICES_URL}?instance_id={device.id}"
        response = self.client.patch(device_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data["name"][0])
        identifier_error = (response.data["identifier"][0])
        message = "This field may not be blank."
        firmware_error = (response.data["firmware"][0])
        message_f = "This field may not be null."

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message, identifier_error)
        self.assertEqual(firmware_error, message_f)

    def test_update_device_without_instance_id(self):
        """Test updating device when instance_id not provided"""
        device = create_device()
        device_model=create_device_model(name="test model")

        payload = {
            "name": "my own devices",
            "identifier": device.identifier,
            "device_model": device_model.id,
            "firmware": device.firmware.id
        }

        url = DEVICES_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = "Please provide instance_id."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"], message)

    def test_delete_device(self):
        """Test delete device"""
        device = create_device()

        device_url = f"{DEVICES_URL}?instance_id={device.id}"

        response = self.client.delete(device_url)
        message = "Object deleted."

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], message)

    def test_device_without_instance_id(self):
        """Test delete device when instance_id not provided"""
        url = DEVICES_URL
        response = self.client.delete(url)
        message = "Please provide instance_id."

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"], message)
