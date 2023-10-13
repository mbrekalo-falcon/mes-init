from core.cluster.tests.__init__ import *

CLUSTERS_URL = reverse('clusters:clusters-list')


def create_cluster(
    name="cluster1", 
    email='cluster1@cluster.com', 
    city='Zagreb',
    address='Avenue 1'
    ):
    """create and return a sample cluster"""
    return Cluster.custom_manager.create(name=name, address=address, email=email, city=city)


class PublicClusterAPITest(TestCase):
    """Test the publicly available cluster API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving clusters"""
        response = self.client.get(CLUSTERS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClustersAPITests(TestCase):
    """Test the authorized user clusters API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_clusters_list(self):
        """Test retrieving clusters"""
        create_cluster()
        create_cluster(
            name="cluster2",
            email='cluster2@cluster.com',
            city='Zagreb',
            address='Avenue 12'
        )

        response = self.client.get(CLUSTERS_URL)

        clusters = Cluster.custom_manager.get_queryset()
        serializer = ClusterSerializer(clusters, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_cluster(self):
        """Test  creating a new cluster"""
        payload = {
            'name': 'Test cluster',
            'address': 'Avenue 1',
            'email': 'test@cluster.com',
            'city': 'Zagreb',
            'country': 'Croatia'
        }

        self.client.post(CLUSTERS_URL, json.dumps(payload), content_type="application/json")

        exists = Cluster.custom_manager.get_queryset().filter(
            name=payload['name'],
            address=payload['address'],
            email=payload['email'],
            city=payload['city'],
            country=payload['country']
        ).exists()
        self.assertTrue(exists)
    
    def test_create_cluster_invalid(self):
        """Test creating a new cluster with invalid payload"""
        payload = {'name': ''}
        response = self.client.post(CLUSTERS_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(
            response.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_clusters_filter_queryset_search_name(self):
        """Test filter queryset clusters by name, email"""
        cluster1 = create_cluster()
        create_cluster(
            name="cluster2",
            email='cluster2@cluster.com',
            city='Zagreb', 
            address='Avenue 1'
        )

        url_name = f'{CLUSTERS_URL}?search_name={cluster1.name}'
        url_email = f'{CLUSTERS_URL}?search_name={cluster1.email[8:]}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        response_email = self.client.get(url_email)
        results_email = response_email.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(response_email.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 1)
        self.assertEqual(len(results_email), 2)
    
    def test_clusters_filter_queryset_search_name_invalid(self):
        """Test filter queryset clusters by invalid search_name input"""
        create_cluster()
        url_name = f'{CLUSTERS_URL}?search_name=invalid1'
        url_email = f'{CLUSTERS_URL}?search_name=invalid1@cluster.com'

        response_name = self.client.get(url_name)
        response_email = self.client.get(url_email)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_email.status_code, status.HTTP_404_NOT_FOUND)

    def test_clusters_filter_queryset_instance_id(self):
        """Test filter queryset clusters by instance_id"""
        cluster1 = create_cluster()
        cluster2 = create_cluster(
            name="cluster2",
            email='cluster2@cluster.com',
            city='Zagreb', 
            address='Avenue 1'
        )

        url_id_1 = f'{CLUSTERS_URL}?instance_id={cluster1.id}'
        url_id_2 = f'{CLUSTERS_URL}?instance_id={cluster2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_clusters_filter_queryset_instance_id_invalid(self):
        """Test filter queryset clusters by invalid instance_id"""
        create_cluster()

        url = f'{CLUSTERS_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_cluster(self):
        """Test updating a cluster with put"""
        cluster = create_cluster()
        payload = {
            "deleted": 'false',
            "name": "cluster2000",
            "address": "Kings Avenue 1",
            "city": "Paris",
            "postal_code": "12000",
            "country": "Croatia",
            "phone": "091091091",
            "email": "cluster2000@cluster.com"
        }
        cluster_url = f'{CLUSTERS_URL}?instance_id={cluster.id}'

        self.client.put(cluster_url, json.dumps(payload), content_type="application/json")

        cluster.refresh_from_db()
        self.assertEqual(cluster.name, payload['name'])
        self.assertEqual(cluster.address, payload['address'])
        self.assertEqual(cluster.city, payload['city'])
        self.assertEqual(cluster.postal_code, payload['postal_code'])
        self.assertEqual(cluster.country, payload['country'])
        self.assertEqual(cluster.phone, payload['phone'])
        self.assertEqual(cluster.email, payload['email'])

    def test_full_update_cluster_invalid(self):
        """Test updating cluster with invalid put"""
        cluster = create_cluster()
        payload = {
            "name": "",
            "address": "",
        }
        cluster_url = f'{CLUSTERS_URL}?instance_id={cluster.id}'
        response = self.client.put(cluster_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        address_error = (response.data['address'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message, address_error)

    def test_partial_update_cluster(self):
        """Test updating a cluster with patch"""
        cluster = create_cluster()
        payload = {
            "name": "cluster2000",
            "address": "Kings Avenue 1"
        }
        cluster_url = f'{CLUSTERS_URL}?instance_id={cluster.id}'
        self.client.patch(cluster_url, json.dumps(payload), content_type="application/json")

        cluster.refresh_from_db()
        self.assertEqual(cluster.name, payload['name'])
        self.assertEqual(cluster.address, payload['address'])

    def test_partial_update_cluster_invalid(self):
        """Test updating a cluster with patch"""
        cluster = create_cluster()
        payload = {
            "name": "",
            "address": ""
        }
        cluster_url = f'{CLUSTERS_URL}?instance_id={cluster.id}'
        response = self.client.patch(cluster_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['name'][0])
        address_error = (response.data['address'][0])
        message = 'This field may not be blank.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message, address_error)

    def test_update_cluster_without_instance_id(self):
        """Test updating cluster when instance_id not provided"""
        payload = {
            "name": "cluster2000",
            "address": "Kings Avenue 1"
        }
        url = CLUSTERS_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster(self):
        """Test delete cluster"""
        cluster = create_cluster()

        cluster_url = f'{CLUSTERS_URL}?instance_id={cluster.id}'
        response = self.client.delete(cluster_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_without_instance_id(self):
        """Test delete cluster when instance_id not provided"""
        url = CLUSTERS_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)