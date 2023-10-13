from core.cluster.tests.__init__ import *

CLUSTERS_USERS_URL = reverse('clusters:clusters-users')


class PublicClustersUsersAPITest(TestCase):
    """Test the publicly available clusters users API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving clusters users"""
        response = self.client.get(CLUSTERS_USERS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClustersUsersAPITests(TestCase):
    """Test the authorized user clusters user API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@thefalcontech.com',
            'password123',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_clusters_users_list(self):
        """Test retrieving clusters"""
        create_cluster_user()
        create_cluster_user()
        response = self.client.get(CLUSTERS_USERS_URL)

        clusters = ClusterUser.custom_manager.get_queryset()
        serializer = ClusterUserSerializer(clusters, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_cluster_user(self):
        """Test  creating a new cluster user"""
        user = create_user()
        cluster = create_cluster()

        payload = {
            "user": user.id,
            "cluster": cluster.id,
        }

        response = self.client.post(CLUSTERS_USERS_URL, payload)
        cluster_user = ClusterUser.custom_manager.get(id=response.data['data']['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cluster_user.cluster, cluster)
        self.assertEqual(cluster_user.user, user)

    def test_create_cluster_user_invalid(self):
        """Test creating a new cluster user with invalid payload"""
        payload = {'user': ''}
        response = self.client.post(CLUSTERS_USERS_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clusters_users_filter_queryset_search_name(self):
        """Test filter queryset clusters by user_full_name, user_email"""
        cluster_user = create_cluster_user()
        ClusterUser.custom_manager.create(
            user=create_user(
                first_name="Anakin",
                last_name="Skywalker",
                email="skyy@gmail.com",
                password="Ivan123!"
                ),
            cluster=create_cluster(
                name="cluster2", 
                email='cluster2@cluster.com', 
                city='Zagreb',
                address='Sesame 3'
                )
        )

        url_name = f'{CLUSTERS_USERS_URL}?search_name={cluster_user.user.full_name}'
        url_email = f'{CLUSTERS_USERS_URL}?search_name={cluster_user.user.email[8:]}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        response_email = self.client.get(url_email)
        results_email = response_email.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(response_email.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 1)
        self.assertEqual(len(results_email), 2)
    
    def test_clusters_users_filter_queryset_search_name_invalid(self):
        """Test filter queryset clusters users by invalid search_name input"""
        create_cluster_user()
        url_name = f'{CLUSTERS_USERS_URL}?search_name=invalid1'
        url_email = f'{CLUSTERS_USERS_URL}?search_name=invalid1@cluster.com'

        response_name = self.client.get(url_name)
        response_email = self.client.get(url_email)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_email.status_code, status.HTTP_404_NOT_FOUND)

    def test_clusters_users_filter_queryset_instance_id(self):
        """Test filter queryset clusters users by instance_id"""
        cluster_user1 = create_cluster_user()
        cluster_user2 = ClusterUser.custom_manager.create(
            user=create_user(
                first_name="Anakin",
                last_name="Skywalker",
                email="skyy@gmail.com",
                password="Ivan123!"
                ),
            cluster=create_cluster(
                name="cluster2", 
                email='cluster2@cluster.com', 
                city='Zagreb',
                address='Sesame 3'
                )
        )

        url_id_1 = f'{CLUSTERS_USERS_URL}?instance_id={cluster_user1.id}'
        url_id_2 = f'{CLUSTERS_USERS_URL}?instance_id={cluster_user2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_clusters_users_filter_queryset_instance_id_invalid(self):
        """Test filter queryset clusters by invalid instance_id"""
        create_cluster_user()

        url = f'{CLUSTERS_USERS_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_cluster_user(self):
        """Test updating a cluster user with put"""
        cluster_user = create_cluster_user()
        user = create_user(
            first_name="Anakin",
            last_name="Skywalker",
            email="email2@gmail.com",
            password="Ivan123!"
        )
        cluster = create_cluster(
            name="cluster2", 
            email='cluster2@cluster.com', 
            city='Zagreb',
            address='Sesame 3'
        )
        payload = {
            "user": user.id,
            "cluster": cluster.id,
        }
        cluster_user_url = f'{CLUSTERS_USERS_URL}?instance_id={cluster_user.id}'

        self.client.put(cluster_user_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(cluster_user.user.full_name, user.full_name)

        cluster_user.refresh_from_db()

        self.assertEqual(cluster_user.user.full_name, user.full_name)
        self.assertEqual(cluster_user.user.email, user.email)
        self.assertEqual(cluster_user.cluster.name, cluster.name)
        self.assertEqual(cluster_user.cluster.email, cluster.email)
        self.assertEqual(cluster_user.cluster.address, cluster.address)

    def test_full_update_cluster_user_invalid(self):
        """Test updating cluster user with invalid put"""
        cluster_user = create_cluster_user()
        payload = {
            "user": "",
            "cluster": "",
        }
        cluster_user_url = f'{CLUSTERS_USERS_URL}?instance_id={cluster_user.id}'
        response = self.client.put(cluster_user_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['user'][0])
        address_error = (response.data['cluster'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message, address_error)

    def test_partial_update_cluster_user(self):
        """Test updating a cluster user with patch"""
        cluster_user = create_cluster_user()
        new_user = create_user(
            first_name="Anakin",
            last_name="Skywalker",
            email="email2@gmail.com",
            password="Ivan123!"
        )
        payload = {
            "user": new_user.id,
            "cluster": cluster_user.cluster.id,
        }
        cluster_user_url = f'{CLUSTERS_USERS_URL}?instance_id={cluster_user.id}'
        self.client.patch(cluster_user_url, json.dumps(payload), content_type="application/json")

        cluster_user.refresh_from_db()
        self.assertEqual(cluster_user.user.full_name, new_user.full_name)
        self.assertEqual(cluster_user.id, payload['cluster'])

    def test_partial_update_cluster_user_invalid(self):
        """Test updating a cluster user with patch"""
        cluster_user = create_cluster_user()
        payload = {
            "user": "",
            "cluster": ""
        }
        cluster_user_url = f'{CLUSTERS_USERS_URL}?instance_id={cluster_user.id}'
        response = self.client.patch(cluster_user_url, json.dumps(payload), content_type="application/json")

        name_error = (response.data['user'][0])
        address_error = (response.data['cluster'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(name_error, message, address_error)

    def test_update_cluster_user_without_instance_id(self):
        """Test updating cluster user when instance_id not provided"""
        user = create_user(
            first_name="Anakin",
            last_name="Skywalker",
            email="email2@gmail.com",
            password="Ivan123!"
        )
        cluster = create_cluster(
            name="cluster2", 
            email='cluster2@cluster.com', 
            city='Zagreb',
            address='Sesame 3'
        )
        payload = {
            "user": user.id,
            "cluster": cluster.id,
        }
        url = CLUSTERS_USERS_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_user(self):
        """Test delete cluster user"""
        cluster_user = create_cluster_user()

        cluster_user_url = f'{CLUSTERS_USERS_URL}?instance_id={cluster_user.id}'
        response = self.client.delete(cluster_user_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_user_without_instance_id(self):
        """Test delete cluster user when instance_id not provided"""
        url = CLUSTERS_USERS_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)