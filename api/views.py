from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import KBEntry, QueryLog
from .permissions import IsAdminUser
from .serializers import LoginSerializer, RegisterSerializer


class RegisterView(APIView):
	authentication_classes = []
	permission_classes = []

	def post(self, request):
		serializer = RegisterSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = User.objects.create_user(
			username=serializer.validated_data['username'],
			password=serializer.validated_data['password'],
			email=serializer.validated_data['email'],
		)

		company = user.company
		company.company_name = serializer.validated_data['company_name']
		company.save(update_fields=['company_name'])

		access_token = str(RefreshToken.for_user(user).access_token)
		return Response(
			{
				'username': user.username,
				'company_name': company.company_name,
				'api_key': company.api_key,
				'access': access_token,
			},
			status=status.HTTP_201_CREATED,
		)


class LoginView(APIView):
	authentication_classes = []
	permission_classes = []

	def post(self, request):
		serializer = LoginSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)

		user = authenticate(
			request,
			username=serializer.validated_data['username'],
			password=serializer.validated_data['password'],
		)
		if user is None:
			return Response(
				{'detail': 'Invalid username or password.'},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		company = user.company
		access_token = str(RefreshToken.for_user(user).access_token)
		return Response(
			{
				'access': access_token,
				'company_name': company.company_name,
				'api_key': company.api_key,
			},
			status=status.HTTP_200_OK,
		)


class KBQueryView(APIView):
	def post(self, request):
		search_term = (request.data.get('search') or '').strip()
		if not search_term:
			return Response(
				{'detail': 'The search field is required and cannot be blank.'},
				status=status.HTTP_400_BAD_REQUEST,
			)

		company = request.user.company
		with transaction.atomic():
			queryset = KBEntry.objects.filter(
				Q(question__icontains=search_term) | Q(answer__icontains=search_term)
			)
			results = list(queryset.values('id', 'question', 'answer', 'category'))
			results_count = len(results)

			QueryLog.objects.create(
				company=company,
				search_term=search_term,
				results_count=results_count,
			)

		return Response(
			{
				'search': search_term,
				'count': results_count,
				'results': results,
			},
			status=status.HTTP_200_OK,
		)


class AdminUsageSummaryView(APIView):
	permission_classes = [IsAdminUser]

	def get(self, request):
		total_queries = QueryLog.objects.aggregate(total=Count('id'))['total'] or 0
		active_companies = QueryLog.objects.values('company').distinct().count()
		top_search_terms = list(
			QueryLog.objects.values('search_term')
			.annotate(count=Count('id'))
			.order_by('-count')[:5]
		)

		return Response(
			{
				'total_queries': total_queries,
				'active_companies': active_companies,
				'top_search_terms': top_search_terms,
			},
			status=status.HTTP_200_OK,
		)
