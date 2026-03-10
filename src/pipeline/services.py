from django.utils import timezone

from src.accounts.models import User
from src.notifications.services import notify_deal_archived

from .models import Deal, DealActivity
from .signals import deal_archived, deal_phase_changed, deal_revision_requested

# Semantic role constants
ROLE_SALES = User.Role.VADIM
ROLE_PRICING = User.Role.MARTIN
ROLE_CONTRACTS = User.Role.ADAM
ROLE_PROJECT_MANAGEMENT = User.Role.MARTIN
ROLE_QA = User.Role.NEKOSVAN

# Phase transition rules: {current_phase: (next_phase, assigned_role)}
PHASE_TRANSITIONS: dict[str, tuple[str, str]] = {
    Deal.Phase.LEAD: (Deal.Phase.QUALIFICATION, ROLE_SALES),
    Deal.Phase.QUALIFICATION: (Deal.Phase.PRICING, ROLE_PRICING),
    Deal.Phase.PRICING: (Deal.Phase.PRESENTATION, ROLE_SALES),
    Deal.Phase.PRESENTATION: (Deal.Phase.CONTRACT, ROLE_CONTRACTS),
    Deal.Phase.CONTRACT: (Deal.Phase.PLANNING, ROLE_PROJECT_MANAGEMENT),
    Deal.Phase.PLANNING: (Deal.Phase.DEVELOPMENT, ROLE_PROJECT_MANAGEMENT),
    Deal.Phase.DEVELOPMENT: (Deal.Phase.COMPLETED, ROLE_QA),
}

# Reverse transition for revision
REVISION_TRANSITION: dict[str, tuple[str, str]] = {
    Deal.Phase.PRESENTATION: (Deal.Phase.PRICING, ROLE_PRICING),
}

MAX_REVISIONS = 3


def get_assignee_for_role(role: str) -> User | None:
    return User.objects.filter(role=role, is_active=True).first()


def advance_phase(deal: Deal, user: User, note: str = "", validate: bool = True) -> Deal:
    """Advance deal to the next phase in the pipeline."""
    if deal.phase not in PHASE_TRANSITIONS:
        raise ValueError(f"Cannot advance from phase '{deal.phase}'")

    next_phase, assigned_role = PHASE_TRANSITIONS[deal.phase]

    if validate:
        from .validators import validate_transition

        validate_transition(deal, next_phase)

    old_phase = deal.phase

    deal.phase = next_phase
    deal.assigned_to = get_assignee_for_role(assigned_role)
    deal.phase_changed_at = timezone.now()
    deal.save(update_fields=["phase", "assigned_to", "phase_changed_at", "updated_at"])

    DealActivity.objects.create(
        deal=deal,
        user=user,
        action=f"phase_changed:{old_phase}:{next_phase}",
        note=note,
    )

    # Emit signal — receivers handle notifications and project creation
    deal_phase_changed.send(
        sender=Deal,
        deal=deal,
        old_phase=old_phase,
        new_phase=next_phase,
        user=user,
        note=note,
    )

    return deal


def request_revision(deal: Deal, user: User, feedback: str) -> Deal:
    """Send deal back for pricing revision."""
    if deal.phase not in REVISION_TRANSITION:
        raise ValueError(f"Cannot request revision from phase '{deal.phase}'")

    deal.revision_count += 1

    if deal.revision_count >= MAX_REVISIONS:
        deal.status = Deal.Status.ARCHIVED
        deal.save(update_fields=["revision_count", "status", "updated_at"])
        DealActivity.objects.create(
            deal=deal,
            user=user,
            action="deal_archived:max_revisions",
            note=f"Max revisions ({MAX_REVISIONS}) reached. {feedback}",
        )
        reason = f"Max revisions ({MAX_REVISIONS}) reached"
        notify_deal_archived(deal, reason=reason)
        deal_archived.send(sender=Deal, deal=deal, reason=reason)
        return deal

    next_phase, assigned_role = REVISION_TRANSITION[deal.phase]
    old_phase = deal.phase

    deal.phase = next_phase
    deal.assigned_to = get_assignee_for_role(assigned_role)
    deal.phase_changed_at = timezone.now()
    deal.save(update_fields=["phase", "assigned_to", "phase_changed_at", "revision_count", "updated_at"])

    DealActivity.objects.create(
        deal=deal,
        user=user,
        action=f"revision_requested:{old_phase}:{next_phase}",
        note=feedback,
    )

    deal_revision_requested.send(sender=Deal, deal=deal, user=user, feedback=feedback)

    return deal


def log_activity(deal: Deal, user: User, action: str, note: str = "") -> DealActivity:
    """Log an activity on a deal."""
    return DealActivity.objects.create(deal=deal, user=user, action=action, note=note)
