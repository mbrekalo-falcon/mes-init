from core.cluster.tests.__init__ import *

USER_ROLES_URL = reverse('clusters:user-roles')


class PublicClusterUserRolesAPITest(TestCase):
    """Test the publicly available cluster user roles API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving cluster user roles"""
        response = self.client.get(USER_ROLES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClusterUserRolesAPITests(TestCase):
    """Test the authorized cluster user roles API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_cluster_user_roles_list(self):
        """Test retrieving cluster user roles"""
        create_cluster_user_role()
        create_cluster_user_role()

        response = self.client.get(USER_ROLES_URL)

        cluster_user_roles = ClusterUserRole.custom_manager.get_queryset()
        serializer = ClusterUserRoleSerializer(cluster_user_roles, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_cluster_user_role(self):
        """Test  creating a new cluster user role"""
        cluster_user = create_cluster_user()
        application_role = create_application_role()
        payload = {
            'cluster_user': cluster_user.id,
            'application_role': application_role.id,
        }

        response = self.client.post(USER_ROLES_URL, payload)
        cluster_user_role = ClusterUserRole.custom_manager.get(id=response.data['data']['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cluster_user_role.cluster_user, cluster_user)
        self.assertEqual(cluster_user_role.application_role, application_role)
    
    def test_create_cluster_user_role_invalid(self):
        """Test creating a new cluster user role with invalid payload"""
        payload = {'cluster_user': ''}
        response = self.client.post(USER_ROLES_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clusters_users_roles_filter_queryset_search_name(self):
        """Test filter queryset clusters user role by user_full_name, cluster_user_email or application_role_name"""
        cluster_user_role = create_cluster_user_role()
        application_role = create_application_role(name="Director", description='main')
        cluster_user = ClusterUser.custom_manager.create(
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
        ClusterUserRole.custom_manager.create(
            cluster_user=cluster_user,
            application_role=application_role
        )

        url_name = f'{USER_ROLES_URL}?search_name={cluster_user_role.cluster_user.user.full_name}'
        url_email = f'{USER_ROLES_URL}?search_name={cluster_user_role.cluster_user.user.email[8:]}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        response_email = self.client.get(url_email)
        results_email = response_email.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(response_email.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 1)
        self.assertEqual(len(results_email), 2)
    
    def test_clusters_users_filter_queryset_search_name_invalid(self):
        """Test filter queryset cluster user roles by invalid search_name input"""
        create_cluster_user_role()
        url_name = f'{USER_ROLES_URL}?search_name=invalid1'
        url_email = f'{USER_ROLES_URL}?search_name=invalid1@cluster.com'

        response_name = self.client.get(url_name)
        response_email = self.client.get(url_email)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_email.status_code, status.HTTP_404_NOT_FOUND)

    def test_clusters_user_roles_filter_queryset_instance_id(self):
        """Test filter queryset clusters users by instance_id"""
        cluster_user_role1 = create_cluster_user_role()
        application_role = create_application_role(name="Director", description='main')
        cluster_user = ClusterUser.custom_manager.create(
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
        cluster_user_role2 = ClusterUserRole.custom_manager.create(
            cluster_user=cluster_user,
            application_role=application_role
        )

        url_id_1 = f'{USER_ROLES_URL}?instance_id={cluster_user_role1.id}'
        url_id_2 = f'{USER_ROLES_URL}?instance_id={cluster_user_role2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_cluster_user_roles_filter_queryset_instance_id_invalid(self):
        """Test filter queryset cluster user roles by invalid instance_id"""
        create_cluster_user_role()

        url = f'{USER_ROLES_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_cluster_user_role(self):
        """Test updating a cluster user role with put"""
        cluster_user_role = create_cluster_user_role()
        application_role = create_application_role(name="Director", description='main')
        cluster_user = ClusterUser.custom_manager.create(
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
        payload = {
            "cluster_user": cluster_user.id,
            "application_role": application_role.id,
        }
        cluster_user_role_url = f'{USER_ROLES_URL}?instance_id={cluster_user_role.id}'

        self.client.put(cluster_user_role_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(cluster_user_role.cluster_user.user.full_name, cluster_user.user.full_name)

        cluster_user_role.refresh_from_db()

        self.assertEqual(cluster_user_role.cluster_user.user.full_name, cluster_user.user.full_name)
        self.assertEqual(cluster_user_role.cluster_user.user.email, cluster_user.user.email)
        self.assertEqual(cluster_user_role.application_role.name, application_role.name)
        self.assertEqual(cluster_user_role.application_role.description, application_role.description)

    def test_full_update_cluster_user_role_invalid(self):
        """Test updating cluster user role with invalid put"""
        cluster_user = create_cluster_user_role()
        payload = {
            "cluster_user": "",
            "application_role": "",
        }
        cluster_user_role_url = f'{USER_ROLES_URL}?instance_id={cluster_user.id}'
        response = self.client.put(cluster_user_role_url, json.dumps(payload), content_type="application/json")

        cluster_user_error = (response.data['cluster_user'][0])
        application_role_error = (response.data['application_role'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cluster_user_error, message, application_role_error)

    def test_partial_update_cluster_user_role(self):
        """Test updating a cluster user role with patch"""
        cluster_user_role = create_cluster_user_role()
        application_role = create_application_role(name="Director", description='main')

        payload = {
            "cluster_user": cluster_user_role.cluster_user.id,
            "application_role": application_role.id,
        }
        cluster_user_url = f'{USER_ROLES_URL}?instance_id={cluster_user_role.id}'
        self.client.patch(cluster_user_url, json.dumps(payload), content_type="application/json")

        cluster_user_role.refresh_from_db()
        self.assertEqual(cluster_user_role.application_role.name, application_role.name)
        self.assertEqual(cluster_user_role.application_role.description, application_role.description)
        self.assertEqual(cluster_user_role.id, payload['cluster_user'])

    def test_partial_update_cluster_user_role_invalid(self):
        """Test updating a cluster user role with patch"""
        cluster_user_role = create_cluster_user_role()
        payload = {
            "cluster_user": "",
            "application_role": ""
        }
        cluster_user_url = f'{USER_ROLES_URL}?instance_id={cluster_user_role.id}'
        response = self.client.patch(cluster_user_url, json.dumps(payload), content_type="application/json")

        cluster_user_error = (response.data['cluster_user'][0])
        application_role_error = (response.data['application_role'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cluster_user_error, message, application_role_error)

    def test_update_cluster_user_role_without_instance_id(self):
        """Test updating cluster user role when instance_id not provided"""
        cluster_user = create_cluster_user()
        application_role = create_application_role()
        payload = {
            "cluster_user": cluster_user.id,
            "application_role": application_role.id,
        }
        url = USER_ROLES_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_user_role(self):
        """Test delete cluster user role"""
        cluster_user_role = create_cluster_user_role()

        cluster_user_url = f'{USER_ROLES_URL}?instance_id={cluster_user_role.id}'
        response = self.client.delete(cluster_user_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_user_role_without_instance_id(self):
        """Test delete cluster user role when instance_id not provided"""
        url = USER_ROLES_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)