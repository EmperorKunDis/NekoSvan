from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Company, User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "name", "legal_name", "ico", "dic", "address", "email", "phone")


class UserSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.get_name_display", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "company",
            "company_name",
            "phone",
            "is_master",
            "bio",
            "avatar",
        )
        read_only_fields = ("id", "is_master")


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer pro úpravu vlastního profilu."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "bio",
            "avatar",
        )
        read_only_fields = ("id", "username")


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pro změnu hesla."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value: str) -> str:
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Nesprávné staré heslo.")
        return value

    def validate_new_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Hesla se neshodují."}
            )
        return attrs

    def save(self) -> User:
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class TeamMemberSerializer(serializers.ModelSerializer):
    """Serializer pro zobrazení členů týmu."""

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "bio",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields


class TeamMemberCreateSerializer(serializers.ModelSerializer):
    """Serializer pro vytváření členů týmu."""

    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "password",
        )
        read_only_fields = ("id",)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def create(self, validated_data: dict) -> User:
        master = self.context["request"].user
        password = validated_data.pop("password")

        user = User(
            **validated_data,
            role=master.role,  # Stejná role jako master
            company=master.company,
            created_by=master,
            is_master=False,  # Nový člen není master
        )
        user.set_password(password)
        user.save()
        return user
