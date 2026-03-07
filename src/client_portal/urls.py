from django.urls import path

from . import views

urlpatterns = [
    path("<uuid:token>/", views.PortalDashboardView.as_view(), name="portal-dashboard"),
    path("<uuid:token>/proposal/accept/", views.PortalProposalAcceptView.as_view(), name="portal-proposal-accept"),
    path("<uuid:token>/proposal/reject/", views.PortalProposalRejectView.as_view(), name="portal-proposal-reject"),
    path(
        "<uuid:token>/milestone/<int:milestone_id>/approve/",
        views.PortalMilestoneApproveView.as_view(),
        name="portal-milestone-approve",
    ),
    path(
        "<uuid:token>/milestone/<int:milestone_id>/reject/",
        views.PortalMilestoneRejectView.as_view(),
        name="portal-milestone-reject",
    ),
    path(
        "<uuid:token>/contract/download/",
        views.PortalContractDownloadView.as_view(),
        name="portal-contract-download",
    ),
]
