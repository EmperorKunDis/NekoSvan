import django.dispatch

deal_phase_changed = django.dispatch.Signal()  # deal, old_phase, new_phase, user, note
deal_revision_requested = django.dispatch.Signal()  # deal, user, feedback
deal_archived = django.dispatch.Signal()  # deal, reason
