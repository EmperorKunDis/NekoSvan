from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from src.accounts.permissions import IsInternalUser, IsMartinRole, MilestoneActionPermission

from . import services
from .models import (
    Milestone,
    MilestoneTemplate,
    MilestoneTemplateItem,
    Project,
    ProjectComment,
    QAChecklist,
    TemplateComment,
)
from .serializers import (
    MilestoneSerializer,
    MilestoneTemplateItemSerializer,
    MilestoneTemplateSerializer,
    ProjectCommentSerializer,
    ProjectSerializer,
    QAChecklistSerializer,
    TemplateCommentSerializer,
)


class MilestoneTemplateViewSet(viewsets.ModelViewSet):
    """Milestone templates management — Martin can edit, others read-only."""

    queryset = MilestoneTemplate.objects.filter(is_active=True).prefetch_related(
        "items", "items__comments", "comments"
    )
    serializer_class = MilestoneTemplateSerializer
    permission_classes = [IsInternalUser, IsMartinRole]
    filterset_fields = ("category", "is_default", "is_active")

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        """Add a new item to the template."""
        template = self.get_object()
        ser = MilestoneTemplateItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        item = ser.save(template=template)
        return Response(MilestoneTemplateItemSerializer(item).data)

    @action(detail=True, methods=["get", "post"])
    def comments(self, request, pk=None):
        """Manage comments on template."""
        template = self.get_object()

        if request.method == "GET":
            comments = template.comments.select_related("user", "resolved_by")
            return Response(TemplateCommentSerializer(comments, many=True).data)

        # POST - add comment
        ser = TemplateCommentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        comment = TemplateComment.objects.create(
            template=template,
            template_item_id=request.data.get("template_item"),
            user=request.user,
            text=ser.validated_data["text"],
        )
        return Response(
            TemplateCommentSerializer(comment).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["patch"], url_path="items/(?P<item_id>[0-9]+)")
    def update_item(self, request, pk=None, item_id=None):
        """Update a specific template item."""
        template = self.get_object()
        try:
            item = template.items.get(id=item_id)
        except MilestoneTemplateItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        ser = MilestoneTemplateItemSerializer(item, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(MilestoneTemplateItemSerializer(item).data)

    @action(detail=True, methods=["delete"], url_path="items/(?P<item_id>[0-9]+)/delete")
    def delete_item(self, request, pk=None, item_id=None):
        """Delete a template item."""
        template = self.get_object()
        try:
            item = template.items.get(id=item_id)
        except MilestoneTemplateItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response({"status": "deleted"})


class TemplateCommentViewSet(viewsets.ModelViewSet):
    """Template comments management."""

    queryset = TemplateComment.objects.select_related(
        "template", "template_item", "user", "resolved_by"
    )
    serializer_class = TemplateCommentSerializer
    permission_classes = [IsInternalUser]
    filterset_fields = ("template", "template_item", "is_resolved")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        """Mark comment as resolved."""
        comment = self.get_object()
        comment.is_resolved = True
        comment.resolved_by = request.user
        comment.resolved_at = timezone.now()
        comment.save(update_fields=["is_resolved", "resolved_by", "resolved_at"])
        return Response(TemplateCommentSerializer(comment).data)

    @action(detail=True, methods=["post"])
    def unresolve(self, request, pk=None):
        """Mark comment as unresolved."""
        comment = self.get_object()
        comment.is_resolved = False
        comment.resolved_by = None
        comment.resolved_at = None
        comment.save(update_fields=["is_resolved", "resolved_by", "resolved_at"])
        return Response(TemplateCommentSerializer(comment).data)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related("deal").prefetch_related("milestones").all()
    serializer_class = ProjectSerializer
    permission_classes = [IsInternalUser]
    filterset_fields = ("deal", "status")

    @action(detail=False, methods=["post"], url_path="create-from-deal/(?P<deal_id>[0-9]+)")
    def create_from_deal(self, request, deal_id=None):
        """Create a project with milestones from a deal."""
        from src.pipeline.models import Deal

        try:
            deal = Deal.objects.get(id=deal_id)
        except Deal.DoesNotExist:
            return Response({"error": "Deal not found"}, status=404)

        project = services.create_project_from_deal(deal)
        return Response(ProjectSerializer(project).data)


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.select_related("project", "project__deal").all()
    serializer_class = MilestoneSerializer
    permission_classes = [IsInternalUser, MilestoneActionPermission]
    filterset_fields = ("project", "status")
    ordering_fields = ("order", "due_date")

    @action(detail=True, methods=["post"])
    def dev_complete(self, request, pk=None):
        milestone = self.get_object()
        demo_url = request.data.get("demo_url", "")
        milestone = services.mark_milestone_dev_complete(milestone, demo_url)
        return Response(MilestoneSerializer(milestone).data)

    @action(detail=True, methods=["post"])
    def qa_approve(self, request, pk=None):
        milestone = self.get_object()
        milestone = services.qa_approve_milestone(milestone)
        return Response(MilestoneSerializer(milestone).data)

    @action(detail=True, methods=["post"])
    def qa_reject(self, request, pk=None):
        milestone = self.get_object()
        feedback = request.data.get("feedback", "")
        milestone = services.qa_reject_milestone(milestone, feedback)
        return Response(MilestoneSerializer(milestone).data)

    @action(detail=True, methods=["post"])
    def client_approve(self, request, pk=None):
        milestone = self.get_object()
        milestone = services.client_approve_milestone(milestone)
        return Response(MilestoneSerializer(milestone).data)

    @action(detail=True, methods=["post"])
    def client_reject(self, request, pk=None):
        milestone = self.get_object()
        feedback = request.data.get("feedback", "")
        milestone = services.client_reject_milestone(milestone, feedback)
        return Response(MilestoneSerializer(milestone).data)


class QAChecklistViewSet(viewsets.ModelViewSet):
    queryset = QAChecklist.objects.select_related("project", "checked_by").all()
    serializer_class = QAChecklistSerializer
    permission_classes = [IsInternalUser]
    filterset_fields = ("project",)

    def perform_create(self, serializer):
        serializer.save(checked_by=self.request.user)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark QA checklist as complete (all items must be checked)."""
        checklist = self.get_object()
        if not checklist.is_complete:
            return Response(
                {"error": "Not all checklist items are checked"},
                status=400,
            )
        checklist.completed_at = timezone.now()
        checklist.save(update_fields=["completed_at"])
        return Response(QAChecklistSerializer(checklist).data)


class ProjectCommentViewSet(viewsets.ModelViewSet):
    queryset = ProjectComment.objects.select_related("project", "milestone", "user").all()
    serializer_class = ProjectCommentSerializer
    permission_classes = [IsInternalUser]
    filterset_fields = ("project", "milestone")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
