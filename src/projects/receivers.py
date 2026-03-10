from src.pipeline.models import Deal


def auto_create_project(sender, deal, old_phase, new_phase, **kwargs):
    """Auto-create project when deal enters PLANNING phase."""
    if new_phase == Deal.Phase.PLANNING:
        from .services import create_project_from_deal

        create_project_from_deal(deal)
