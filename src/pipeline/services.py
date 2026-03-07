from django.utils import timezone

from src.accounts.models import User
from src.notifications.services import notify_deal_archived, notify_phase_change

from .models import Deal, DealActivity

# Phase transition rules: {current_phase: (next_phase, assigned_role)}
PHASE_TRANSITIONS: dict[str, tuple[str, str]] = {
    Deal.Phase.LEAD: (Deal.Phase.QUALIFICATION, User.Role.VADIM),
    Deal.Phase.QUALIFICATION: (Deal.Phase.PRICING, User.Role.MARTIN),
    Deal.Phase.PRICING: (Deal.Phase.PRESENTATION, User.Role.VADIM),
    Deal.Phase.PRESENTATION: (Deal.Phase.CONTRACT, User.Role.ADAM),
    Deal.Phase.CONTRACT: (Deal.Phase.PLANNING, User.Role.MARTIN),
    Deal.Phase.PLANNING: (Deal.Phase.DEVELOPMENT, User.Role.MARTIN),
    Deal.Phase.DEVELOPMENT: (Deal.Phase.COMPLETED, User.Role.NEKOSVAN),
}

# Reverse transition for revision
REVISION_TRANSITION: dict[str, tuple[str, str]] = {
    Deal.Phase.PRESENTATION: (Deal.Phase.PRICING, User.Role.MARTIN),
}

MAX_REVISIONS = 3


def get_assignee_for_role(role: str) -> User | None:
    return User.objects.filter(role=role, is_active=True).first()


def advance_phase(deal: Deal, user: User, note: str = "") -> Deal:
    """Advance deal to the next phase in the pipeline."""
    if deal.phase not in PHASE_TRANSITIONS:
        raise ValueError(f"Cannot advance from phase '{deal.phase}'")

    next_phase, assigned_role = PHASE_TRANSITIONS[deal.phase]
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

    # Notify assigned user about phase change
    notify_phase_change(deal)

    # Auto-create project when entering PLANNING phase
    if next_phase == Deal.Phase.PLANNING:
        from src.projects.services import create_project_from_deal

        create_project_from_deal(deal)

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
        notify_deal_archived(deal, reason=f"Max revisions ({MAX_REVISIONS}) reached")
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

    return deal


def log_activity(deal: Deal, user: User, action: str, note: str = "") -> DealActivity:
    """Log an activity on a deal."""
    return DealActivity.objects.create(deal=deal, user=user, action=action, note=note)
