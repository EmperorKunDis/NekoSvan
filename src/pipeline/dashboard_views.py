from django.db.models import Avg, Count, F
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.accounts.models import User
from src.contracts.models import Payment
from src.pipeline.models import Deal, DealActivity
from src.projects.models import Milestone


class DashboardView(APIView):
    """Role-based dashboard data aggregation."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role

        dispatch = {
            User.Role.ADAM: self._adam_dashboard,
            User.Role.VADIM: self._vadim_dashboard,
            User.Role.MARTIN: self._martin_dashboard,
            User.Role.NEKOSVAN: self._nekosvan_dashboard,
        }

        handler = dispatch.get(role)
        if not handler:
            return Response({"error": "No dashboard for this role"}, status=403)

        return Response(handler(user))

    def _adam_dashboard(self, user) -> dict:
        """Adam: pipeline overview, contracts waiting, unpaid payments."""
        phase_counts = dict(
            Deal.objects.filter(status=Deal.Status.ACTIVE)
            .values_list("phase")
            .annotate(count=Count("id"))
            .values_list("phase", "count")
        )

        unpaid_payments = Payment.objects.filter(
            status__in=[Payment.Status.PENDING, Payment.Status.OVERDUE]
        ).select_related("deal").values(
            "id", "deal__client_company", "type", "amount", "due_date", "status"
        )

        contracts_waiting = Deal.objects.filter(
            phase=Deal.Phase.CONTRACT, status=Deal.Status.ACTIVE
        ).values("id", "client_company", "phase_changed_at")

        # Revenue summary
        paid_total = Payment.objects.filter(status=Payment.Status.PAID).aggregate(
            total=Count("id"),
        )
        recent_leads = Deal.objects.filter(
            phase__in=[Deal.Phase.LEAD, Deal.Phase.QUALIFICATION],
            status=Deal.Status.ACTIVE,
        ).order_by("-created_at")[:5].values("id", "client_company", "client_email", "created_at")

        return {
            "role": "adam",
            "pipeline_overview": phase_counts,
            "total_active_deals": Deal.objects.filter(status=Deal.Status.ACTIVE).count(),
            "contracts_waiting": list(contracts_waiting),
            "unpaid_payments": list(unpaid_payments),
            "revenue_summary": {
                "paid_payments_count": paid_total["total"] or 0,
            },
            "recent_leads": list(recent_leads),
        }

    def _vadim_dashboard(self, user) -> dict:
        """Vadim: leads to call, proposals to present, client checkpoints."""
        leads_to_call = Deal.objects.filter(
            phase=Deal.Phase.QUALIFICATION,
            status=Deal.Status.ACTIVE,
            assigned_to=user,
        ).values("id", "client_company", "client_contact_name", "client_phone", "client_email", "phase_changed_at")

        proposals_to_present = Deal.objects.filter(
            phase=Deal.Phase.PRESENTATION,
            status=Deal.Status.ACTIVE,
            assigned_to=user,
        ).values("id", "client_company", "phase_changed_at")

        milestones_for_client = Milestone.objects.filter(
            status=Milestone.Status.CLIENT_REVIEW,
        ).select_related("project__deal").values(
            "id", "title", "project__deal__client_company", "demo_url"
        )

        upcoming_presentations = Deal.objects.filter(
            phase=Deal.Phase.PRESENTATION,
            status=Deal.Status.ACTIVE,
        ).order_by("phase_changed_at").values("id", "client_company", "phase_changed_at")[:5]

        return {
            "role": "vadim",
            "leads_to_call": list(leads_to_call),
            "proposals_to_present": list(proposals_to_present),
            "milestones_for_client_review": list(milestones_for_client),
            "upcoming_presentations": list(upcoming_presentations),
        }

    def _martin_dashboard(self, user) -> dict:
        """Martin: questionnaires to price, active projects, rejected milestones."""
        to_price = Deal.objects.filter(
            phase=Deal.Phase.PRICING,
            status=Deal.Status.ACTIVE,
            assigned_to=user,
        ).values("id", "client_company", "phase_changed_at")

        active_projects = Deal.objects.filter(
            phase=Deal.Phase.DEVELOPMENT,
            status=Deal.Status.ACTIVE,
        ).values("id", "client_company")

        rejected_milestones = Milestone.objects.filter(
            status=Milestone.Status.REJECTED,
        ).select_related("project__deal").values(
            "id", "title", "client_feedback", "project__deal__client_company"
        )

        planning_deals = Deal.objects.filter(
            phase=Deal.Phase.PLANNING,
            status=Deal.Status.ACTIVE,
            assigned_to=user,
        ).values("id", "client_company", "phase_changed_at")

        # Milestone progress
        total_milestones = Milestone.objects.filter(
            project__deal__status=Deal.Status.ACTIVE,
        ).count()
        approved_milestones = Milestone.objects.filter(
            project__deal__status=Deal.Status.ACTIVE,
            status=Milestone.Status.APPROVED,
        ).count()

        return {
            "role": "martin",
            "deals_to_price": list(to_price),
            "deals_in_planning": list(planning_deals),
            "active_projects": list(active_projects),
            "rejected_milestones": list(rejected_milestones),
            "milestone_progress": {
                "total": total_milestones,
                "approved": approved_milestones,
                "progress_pct": round(approved_milestones / total_milestones * 100, 1) if total_milestones else 0,
            },
        }

    def _nekosvan_dashboard(self, user) -> dict:
        """NekoSvan: QA review queue, active projects overview, stats."""
        qa_queue = Milestone.objects.filter(
            status=Milestone.Status.QA_REVIEW,
        ).select_related("project__deal").values(
            "id", "title", "demo_url", "dev_completed_at", "project__deal__client_company"
        )

        active_projects = (
            Deal.objects.filter(
                phase=Deal.Phase.DEVELOPMENT,
                status=Deal.Status.ACTIVE,
            )
            .values("id", "client_company")
        )

        # Stats
        total_deals = Deal.objects.count()
        completed_deals = Deal.objects.filter(phase=Deal.Phase.COMPLETED).count()
        active_deals = Deal.objects.filter(status=Deal.Status.ACTIVE).exclude(phase=Deal.Phase.COMPLETED).count()

        phase_distribution = dict(
            Deal.objects.filter(status=Deal.Status.ACTIVE)
            .values_list("phase")
            .annotate(count=Count("id"))
            .values_list("phase", "count")
        )

        # Average phase duration (days)
        avg_duration = (
            DealActivity.objects.filter(action__startswith="phase_changed:")
            .aggregate(avg=Avg(F("created_at") - F("deal__phase_changed_at")))
        )

        # Revision rate
        deals_with_revisions = Deal.objects.filter(revision_count__gt=0).count()
        revision_rate = round(deals_with_revisions / total_deals * 100, 1) if total_deals else 0

        # Monthly throughput (completed this month)
        now = timezone.now()
        monthly = Deal.objects.filter(
            phase=Deal.Phase.COMPLETED,
            updated_at__year=now.year,
            updated_at__month=now.month,
        ).count()

        return {
            "role": "nekosvan",
            "qa_review_queue": list(qa_queue),
            "active_projects": list(active_projects),
            "stats": {
                "total_deals": total_deals,
                "completed_deals": completed_deals,
                "active_deals": active_deals,
                "conversion_rate": round(completed_deals / total_deals * 100, 1) if total_deals else 0,
                "phase_distribution": phase_distribution,
                "avg_phase_duration_days": avg_duration["avg"].days if avg_duration.get("avg") else None,
                "revision_rate": revision_rate,
                "monthly_throughput": monthly,
            },
        }
