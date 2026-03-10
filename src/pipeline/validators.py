from .models import Deal


class PhaseTransitionError(ValueError):
    """Raised when a deal cannot transition to the next phase due to missing prerequisites."""

    def __init__(self, message: str, phase: str, missing: list[str]):
        super().__init__(message)
        self.phase = phase
        self.missing = missing


def _validate_pricing(deal: Deal) -> list[str]:
    """PRICING requires a completed questionnaire."""
    missing = []
    if not hasattr(deal, "questionnaire"):
        missing.append("questionnaire")
    return missing


def _validate_presentation(deal: Deal) -> list[str]:
    """PRESENTATION requires at least one proposal."""
    missing = []
    if not deal.proposals.exists():
        missing.append("proposal")
    return missing


def _validate_contract(deal: Deal) -> list[str]:
    """CONTRACT requires an accepted proposal."""
    missing = []
    if not deal.proposals.filter(status="accepted").exists():
        missing.append("accepted_proposal")
    return missing


def _validate_planning(deal: Deal) -> list[str]:
    """PLANNING requires a signed contract."""
    missing = []
    if not hasattr(deal, "contract") or deal.contract.status != "signed":
        missing.append("signed_contract")
    return missing


def _validate_completed(deal: Deal) -> list[str]:
    """COMPLETED requires all milestones approved."""
    missing = []
    if hasattr(deal, "project"):
        project = deal.project
        total = project.milestones.count()
        approved = project.milestones.filter(status="approved").count()
        if total == 0 or approved < total:
            missing.append("approved_milestones")
    else:
        missing.append("project")
    return missing


# Map: target phase → validator function
_VALIDATORS: dict[str, callable] = {
    Deal.Phase.PRICING: _validate_pricing,
    Deal.Phase.PRESENTATION: _validate_presentation,
    Deal.Phase.CONTRACT: _validate_contract,
    Deal.Phase.PLANNING: _validate_planning,
    Deal.Phase.COMPLETED: _validate_completed,
}


def validate_transition(deal: Deal, next_phase: str) -> None:
    """Validate that a deal can transition to next_phase. Raises PhaseTransitionError if not."""
    validator = _VALIDATORS.get(next_phase)
    if validator is None:
        return

    missing = validator(deal)
    if missing:
        raise PhaseTransitionError(
            f"Nelze postoupit do fáze {next_phase}: chybí {', '.join(missing)}",
            phase=next_phase,
            missing=missing,
        )
