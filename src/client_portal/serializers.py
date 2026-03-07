from rest_framework import serializers

from src.contracts.models import Contract, Payment
from src.pipeline.models import Deal
from src.pricing.models import Proposal
from src.projects.models import Milestone, Project


class PortalDealSerializer(serializers.ModelSerializer):
    phase_display = serializers.CharField(source="get_phase_display", read_only=True)

    class Meta:
        model = Deal
        fields = ("id", "client_company", "phase", "phase_display", "created_at")


class PortalProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ("id", "version", "items", "total_price", "deposit_amount", "demo_url", "demo_description", "valid_until", "status")


class PortalContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ("id", "generated_pdf", "status", "signed_at")


class PortalPaymentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source="get_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "type", "type_display", "amount", "due_date", "status", "status_display", "invoice_number")


class PortalMilestoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Milestone
        fields = ("id", "title", "description", "order", "status", "status_display", "demo_url", "due_date")


class PortalProjectSerializer(serializers.ModelSerializer):
    milestones = PortalMilestoneSerializer(many=True, read_only=True)
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ("id", "status", "start_date", "estimated_end_date", "milestones", "progress_percent")


class ClientFeedbackSerializer(serializers.Serializer):
    feedback = serializers.CharField()
