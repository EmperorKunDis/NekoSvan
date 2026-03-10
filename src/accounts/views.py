from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from rest_framework import serializers as drf_serializers
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Company, User
from .serializers import (
    ChangePasswordSerializer,
    CompanySerializer,
    ProfileSerializer,
    TeamMemberCreateSerializer,
    TeamMemberSerializer,
    UserSerializer,
)


class LoginSerializer(drf_serializers.Serializer):
    username = drf_serializers.CharField()
    password = drf_serializers.CharField()


class LoginView(APIView):
    """Session login endpoint."""

    permission_classes = [AllowAny]

    def post(self, request):
        ser = LoginSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = authenticate(
            request,
            username=ser.validated_data["username"],
            password=ser.validated_data["password"],
        )
        if user is None:
            return Response({"error": "Neplatné přihlašovací údaje"}, status=400)
        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutView(APIView):
    """Session logout endpoint."""

    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({"status": "logged_out"})


class CsrfTokenView(APIView):
    """Return CSRF token — call this before login."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("company").all()
    serializer_class = UserSerializer
    filterset_fields = ("role", "company")
    search_fields = ("username", "first_name", "last_name", "email")

    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class ProfileView(APIView):
    """Správa vlastního profilu."""

    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        """Získání profilu."""
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Úprava profilu."""
        serializer = ProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """Změna hesla."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "password_changed"})


class TeamView(APIView):
    """Správa týmu (pro mastery)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Seznam členů týmu."""
        user = request.user
        if not user.is_master:
            return Response(
                {"error": "Nemáte oprávnění zobrazit tým."},
                status=status.HTTP_403_FORBIDDEN,
            )
        members = user.get_team_members()
        serializer = TeamMemberSerializer(members, many=True)
        return Response(
            {
                "is_master": True,
                "role": user.role,
                "role_display": user.get_role_display(),
                "members": serializer.data,
            }
        )

    def post(self, request):
        """Vytvoření nového člena týmu."""
        user = request.user
        if not user.can_create_team_member():
            return Response(
                {"error": "Nemáte oprávnění vytvářet členy týmu."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = TeamMemberCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_member = serializer.save()
        return Response(
            TeamMemberSerializer(new_member).data, status=status.HTTP_201_CREATED
        )


class TeamMemberDetailView(APIView):
    """Detail člena týmu (pro mastery)."""

    permission_classes = [IsAuthenticated]

    def get_member(self, request, pk: int):
        """Získání člena týmu s ověřením oprávnění."""
        user = request.user
        if not user.is_master:
            return None, Response(
                {"error": "Nemáte oprávnění."}, status=status.HTTP_403_FORBIDDEN
            )
        try:
            member = User.objects.get(pk=pk, role=user.role)
            if member.pk == user.pk:
                return None, Response(
                    {"error": "Nelze upravovat sebe."}, status=status.HTTP_400_BAD_REQUEST
                )
            return member, None
        except User.DoesNotExist:
            return None, Response(
                {"error": "Člen nenalezen."}, status=status.HTTP_404_NOT_FOUND
            )

    def get(self, request, pk: int):
        """Detail člena."""
        member, error = self.get_member(request, pk)
        if error:
            return error
        return Response(TeamMemberSerializer(member).data)

    def patch(self, request, pk: int):
        """Úprava člena."""
        member, error = self.get_member(request, pk)
        if error:
            return error
        serializer = ProfileSerializer(member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(TeamMemberSerializer(member).data)

    def delete(self, request, pk: int):
        """Deaktivace člena."""
        member, error = self.get_member(request, pk)
        if error:
            return error
        member.is_active = False
        member.save()
        return Response({"status": "deactivated"})
