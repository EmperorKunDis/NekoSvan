from .services import notify_phase_change


def notify_on_phase_change(sender, deal, **kwargs):
    """Notify assigned user about deal phase change."""
    notify_phase_change(deal)
