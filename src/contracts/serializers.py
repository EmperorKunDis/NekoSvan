from rest_framework import serializers

from .models import Contract, ContractTemplate, Payment


class ContractTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractTemplate
        fields = "__all__"


class ContractSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Contract
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PaymentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    deal_company = serializers.CharField(source="deal.client_company", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ("id", "created_at")
