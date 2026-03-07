import datetime

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.accounts.permissions import ContractPermission, IsInternalUser, PaymentPermission
from src.notifications.services import notify_contract_signed, notify_payment_received
from src.pipeline import services as pipeline_services
from src.pipeline.models import Deal

from . import services
from .models import Contract, ContractTemplate, Payment
from .serializers import ContractSerializer, ContractTemplateSerializer, PaymentSerializer


class ContractTemplateViewSet(viewsets.ModelViewSet):
    queryset = ContractTemplate.objects.all()
    serializer_class = ContractTemplateSerializer
    permission_classes = [IsInternalUser, ContractPermission]


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.select_related("deal", "template_used").all()
    serializer_class = ContractSerializer
    permission_classes = [IsInternalUser, ContractPermission]
    filterset_fields = ("deal", "status")

    @action(detail=False, methods=["post"], url_path="generate/(?P<deal_id>[0-9]+)")
    def generate(self, request, deal_id=None):
        """Generate contract PDF for a deal."""
        try:
            deal = Deal.objects.get(id=deal_id)
        except Deal.DoesNotExist:
            return Response({"error": "Deal not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            contract = services.generate_contract_pdf(deal)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(ContractSerializer(contract).data)

    @action(detail=True, methods=["post"])
    def send_to_client(self, request, pk=None):
        """Mark contract as sent."""
        contract = self.get_object()
        contract.status = Contract.Status.SENT
        contract.save(update_fields=["status", "updated_at"])
        return Response(ContractSerializer(contract).data)

    @action(detail=True, methods=["post"])
    def mark_signed(self, request, pk=None):
        """Mark contract as signed by client and auto-create deposit payment."""
        contract = self.get_object()
        contract.status = Contract.Status.SIGNED
        contract.signed_at = timezone.now()
        contract.signed_by_client = True
        contract.save(update_fields=["status", "signed_at", "signed_by_client", "updated_at"])

        # Auto-create deposit payment from accepted proposal
        deal = contract.deal
        proposal = deal.proposals.filter(status="accepted").order_by("-version").first()
        if proposal and proposal.deposit_amount > 0:
            if not deal.payments.filter(type=Payment.PaymentType.DEPOSIT).exists():
                Payment.objects.create(
                    deal=deal,
                    type=Payment.PaymentType.DEPOSIT,
                    amount=proposal.deposit_amount,
                    due_date=timezone.now().date() + datetime.timedelta(days=14),
                    invoice_number=f"INV-{deal.id:04d}-DEP",
                )
        # Auto-create final payment
        if proposal and proposal.total_price > proposal.deposit_amount:
            if not deal.payments.filter(type=Payment.PaymentType.FINAL).exists():
                Payment.objects.create(
                    deal=deal,
                    type=Payment.PaymentType.FINAL,
                    amount=proposal.total_price - proposal.deposit_amount,
                    due_date=timezone.now().date() + datetime.timedelta(days=90),
                    invoice_number=f"INV-{deal.id:04d}-FIN",
                )

        notify_contract_signed(deal)
        return Response(ContractSerializer(contract).data)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("deal").all()
    serializer_class = PaymentSerializer
    permission_classes = [IsInternalUser, PaymentPermission]
    filterset_fields = ("deal", "type", "status")

    @action(detail=True, methods=["post"])
    def mark_paid(self, request, pk=None):
        """Mark payment as paid and advance deal if deposit."""
        payment = self.get_object()
        payment.status = Payment.Status.PAID
        payment.paid_at = timezone.now()
        payment.save(update_fields=["status", "paid_at"])

        notify_payment_received(payment)

        # If deposit is paid, advance deal to planning
        if payment.type == Payment.PaymentType.DEPOSIT:
            deal = payment.deal
            if deal.phase == Deal.Phase.CONTRACT:
                pipeline_services.advance_phase(
                    deal, request.user, note=f"Deposit payment received: {payment.amount} CZK"
                )

        return Response(PaymentSerializer(payment).data)
