from django.contrib.auth.models import User
from rest_framework.test import APIClient

from api.models import Company, QueryLog

username = 'acmecorp_demo'
password = 'securepass123'

User.objects.filter(username=username).delete()

client = APIClient()
register_payload = {
    'username': username,
    'password': password,
    'company_name': 'Acme Corp',
    'email': 'dev@acmecorp.com',
}
register_response = client.post('/api/auth/register/', register_payload, format='json')
print('REGISTER_STATUS', register_response.status_code)
print('REGISTER_HAS_ACCESS', 'access' in register_response.data)
print('REGISTER_HAS_API_KEY', bool(register_response.data.get('api_key')))

company = Company.objects.get(user__username=username)
print('COMPANY_AUTO_CREATED', company is not None)
print('COMPANY_NAME', company.company_name)
print('COMPANY_API_KEY_LEN', len(company.api_key))

login_response = client.post('/api/auth/login/', {'username': username, 'password': password}, format='json')
print('LOGIN_STATUS', login_response.status_code)
access = login_response.data['access']

no_token_query = client.post('/api/kb/query/', {'search': 'select_related'}, format='json')
print('QUERY_NO_TOKEN_STATUS', no_token_query.status_code)

client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
query_response = client.post('/api/kb/query/', {'search': 'select_related'}, format='json')
print('QUERY_WITH_TOKEN_STATUS', query_response.status_code)
print('QUERY_RESULT_COUNT', query_response.data.get('count'))

admin_as_client = client.get('/api/admin/usage-summary/')
print('ADMIN_WITH_CLIENT_STATUS', admin_as_client.status_code)

company.role = Company.Role.ADMIN
company.save(update_fields=['role'])

client.credentials()
admin_login = client.post('/api/auth/login/', {'username': username, 'password': password}, format='json')
admin_access = admin_login.data['access']
client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_access}')
admin_ok = client.get('/api/admin/usage-summary/')
print('ADMIN_WITH_ADMIN_STATUS', admin_ok.status_code)
print('ADMIN_PAYLOAD_KEYS', sorted(admin_ok.data.keys()))
print('QUERYLOG_COUNT', QueryLog.objects.filter(company=company).count())
