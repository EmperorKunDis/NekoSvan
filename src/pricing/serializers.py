from rest_framework import serializers

from .models import PricingMatrix, PricingModifier, Proposal


class PricingMatrixSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingMatrix
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PricingModifierSerializer(serializers.ModelSerializer):
    modifier_type_display = serializers.CharField(source="get_modifier_type_display", read_only=True)

    class Meta:
        model = PricingModifier
        fields = "__all__"
        read_only_fields = ("id",)


class ProposalSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Proposal
        fields = "__all__"
        read_only_fields = ("id", "created_by", "created_at", "updated_at")
