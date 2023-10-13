from core.cluster.tests.__init__ import *

MODULE_PERMISSIONS_URL = reverse('clusters:user-module-permissions')


class PublicClusterUserModulePermissionsAPITest(TestCase):
    """Test the publicly available cluster user module permission API"""

    def setUp(self):
        self.client = APIClient()
    
    def test_login_required(self):
        """Test that login is required for retrieving cluster user module permission"""
        response = self.client.get(MODULE_PERMISSIONS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateClusterUserModulePermissionsAPITests(TestCase):
    """Test the authorized cluster user module permissions roles API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@gmail.com',
            'password123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_cluster_user_module_permissions_list(self):
        """Test retrieving cluster user module permissions"""
        create_cluster_user_module_permission()
        create_cluster_user_module_permission()

        response = self.client.get(MODULE_PERMISSIONS_URL)

        cluster_user_module_permissions = ClusterUserModulePermission.custom_manager.get_queryset()
        serializer = ClusterUserModulePermissionSerializer(cluster_user_module_permissions, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['data']['results']
        self.assertEqual(serializer.data, results)

    def test_create_cluster_user_module_permission(self):
        """Test  creating a new cluster user module permission"""
        cluster_user_role = create_cluster_user_role()
        application_module = create_application_module()
        payload = {
            'cluster_user_role': cluster_user_role.id,
            'application_module': application_module.id,
        }

        response = self.client.post(MODULE_PERMISSIONS_URL, payload)
        cluster_user_module_permission = ClusterUserModulePermission.custom_manager.get(id=response.data['data']['id'])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(cluster_user_module_permission.cluster_user_role, cluster_user_role)
        self.assertEqual(cluster_user_module_permission.application_module, application_module)
    
    def test_create_cluster_user_module_permission_invalid(self):
        """Test creating a new cluster user module permission invalid"""
        payload = {'cluster_user_role': ''}
        response = self.client.post(MODULE_PERMISSIONS_URL, json.dumps(payload), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_clusters_user_module_permissions_filter_queryset_search_name(self):
        """Test filter queryset cluster user module permissions by application_module_name"""
        create_cluster_user_module_permission()
        application_module = create_application_module(name="application module")
        cluster_user_role = create_cluster_user_role()
        ClusterUserModulePermission.custom_manager.create(
            cluster_user_role=cluster_user_role,
            application_module=application_module
        )

        url_name = f'{MODULE_PERMISSIONS_URL}?search_name={application_module.name}'

        response_name = self.client.get(url_name)
        results_name = response_name.data['data']['results']

        self.assertEqual(response_name.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_name), 2)
    
    def test_clusters_user_module_permissions_filter_queryset_search_name_invalid(self):
        """Test filter queryset cluster user module permission by invalid search_name input"""
        create_cluster_user_role()
        url_name = f'{MODULE_PERMISSIONS_URL}?search_name=invalid1'

        response_name = self.client.get(url_name)

        self.assertEqual(response_name.status_code, status.HTTP_404_NOT_FOUND)

    def test_clusters_user_module_permissions_filter_queryset_instance_id(self):
        """Test filter queryset clusters user module permissions by instance_id"""
        cluster_user_module_permission1 = create_cluster_user_module_permission()
        application_module = create_application_module(name="Module 8")
        cluster_user_role = create_cluster_user_role()

        cluster_user_module_permission2 = ClusterUserModulePermission.custom_manager.create(
            cluster_user_role=cluster_user_role,
            application_module=application_module
        )

        url_id_1 = f'{MODULE_PERMISSIONS_URL}?instance_id={cluster_user_module_permission1.id}'
        url_id_2 = f'{MODULE_PERMISSIONS_URL}?instance_id={cluster_user_module_permission2.id}'

        response_id_1 = self.client.get(url_id_1)
        response_id_2 = self.client.get(url_id_2)

        results_id_1 = response_id_1.data['data']['results'][0]['id']
        results_id_2 = response_id_2.data['data']['results'][0]['id']

        self.assertEqual(response_id_1.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_1, 1)
        self.assertEqual(response_id_2.status_code, status.HTTP_200_OK)
        self.assertEqual(results_id_2, 2)

    def test_cluster_user_module_permission_filter_queryset_instance_id_invalid(self):
        """Test filter queryset cluster user module permission by invalid instance_id"""
        create_cluster_user_module_permission()

        url = f'{MODULE_PERMISSIONS_URL}?instance_id=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_full_update_cluster_user_module_permission(self):
        """Test updating a cluster user module permission with put"""
        cluster_user_module_permission = create_cluster_user_module_permission()
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
        cluster_user_role = ClusterUserRole.custom_manager.create(
            cluster_user=cluster_user, application_role=application_role
        )
        application_module = create_application_module(name='module8')

        payload = {
            "cluster_user_role": cluster_user_role.id,
            "application_module": application_module.id,
        }
        cluster_user_module_permission_url = f'{MODULE_PERMISSIONS_URL}?instance_id={cluster_user_module_permission.id}'

        self.client.put(cluster_user_module_permission_url, json.dumps(payload), content_type="application/json")

        self.assertNotEqual(
            cluster_user_module_permission.cluster_user_role.cluster_user.user.full_name,
            cluster_user_role.cluster_user.user.full_name
        )

        cluster_user_module_permission.refresh_from_db()

        self.assertEqual(
            cluster_user_module_permission.cluster_user_role.cluster_user.user.full_name, 
            cluster_user_role.cluster_user.user.full_name
        )
        self.assertEqual(
            cluster_user_module_permission.cluster_user_role.cluster_user.user.email, 
            cluster_user_role.cluster_user.user.email
        )
        self.assertEqual(
            cluster_user_module_permission.application_module.name, 
            application_module.name
        )

    def test_full_update_cluster_user_module_permission_invalid(self):
        """Test updating cluster user module permission with invalid put"""
        cluster_user_module_permission = create_cluster_user_module_permission()
        payload = {
            "cluster_user_role": "",
            "application_module": "",
        }
        cluster_user_module_permission_url = f'{MODULE_PERMISSIONS_URL}?instance_id={cluster_user_module_permission.id}'
        response = self.client.put(cluster_user_module_permission_url, json.dumps(payload), content_type="application/json")

        cluster_user_role_error = (response.data['cluster_user_role'][0])
        application_module_error = (response.data['application_module'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cluster_user_role_error, message, application_module_error)

    def test_partial_update_cluster_user_module_permission(self):
        """Test updating a cluster user module permission with patch"""
        cluster_user_module_permission = create_cluster_user_module_permission()
        application_module = create_application_module(name='module8')

        payload = {
            "cluster_user_role": cluster_user_module_permission.cluster_user_role.id,
            "application_module": application_module.id,
        }
        cluster_user_module_permission_url = f'{MODULE_PERMISSIONS_URL}?instance_id={cluster_user_module_permission.id}'
        self.client.patch(cluster_user_module_permission_url, json.dumps(payload), content_type="application/json")

        cluster_user_module_permission.refresh_from_db()
        self.assertEqual(
            cluster_user_module_permission.application_module.name, 
            application_module.name
        )
        self.assertEqual(cluster_user_module_permission.application_module.id, payload['application_module'])

    def test_partial_update_cluster_user_module_permission_invalid(self):
        """Test updating a cluster user module permission with patch invalid"""
        cluster_user_module_permission = create_cluster_user_module_permission()
        payload = {
            "cluster_user_role": "",
            "application_module": ""
        }
        cluster_user_module_permission_url = f'{MODULE_PERMISSIONS_URL}?instance_id={cluster_user_module_permission.id}'
        response = self.client.patch(cluster_user_module_permission_url, json.dumps(payload), content_type="application/json")

        cluster_user_role_error = (response.data['cluster_user_role'][0])
        application_module_error = (response.data['application_module'][0])
        message = 'This field may not be null.'

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(cluster_user_role_error, message, application_module_error)

    def test_update_cluster_user_module_permission_without_instance_id(self):
        """Test updating cluster user module permission when instance_id not provided"""
        cluster_user_module_permission = create_cluster_user_module_permission()
        application_module = create_application_module()
        payload = {
            "cluster_user_role": cluster_user_module_permission.cluster_user_role.id,
            "application_module": application_module.id,
        }
        url = MODULE_PERMISSIONS_URL
        response = self.client.patch(url, json.dumps(payload), content_type="application/json")
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_user_module_permission(self):
        """Test delete cluster user module permission"""
        cluster_user_module_permission = create_cluster_user_module_permission()

        cluster_user_module_permission_url = f'{MODULE_PERMISSIONS_URL}?instance_id={cluster_user_module_permission.id}'
        response = self.client.delete(cluster_user_module_permission_url)
        message = 'Object deleted.'

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], message)

    def test_delete_cluster_user_module_permission_without_instance_id(self):
        """Test delete cluster user module permission when instance_id not provided"""
        url = MODULE_PERMISSIONS_URL
        response = self.client.delete(url)
        message = 'Please provide instance_id.'

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], message)
