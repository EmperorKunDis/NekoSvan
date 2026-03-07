from rest_framework import serializers

from .models import (
    Milestone,
    MilestoneTemplate,
    MilestoneTemplateItem,
    Project,
    ProjectComment,
    QAChecklist,
    TemplateComment,
)


class TemplateCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    resolved_by_name = serializers.CharField(
        source="resolved_by.get_full_name", read_only=True
    )

    class Meta:
        model = TemplateComment
        fields = (
            "id",
            "template",
            "template_item",
            "user",
            "user_name",
            "text",
            "is_resolved",
            "resolved_by",
            "resolved_by_name",
            "resolved_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
        )


class MilestoneTemplateItemSerializer(serializers.ModelSerializer):
    comments = TemplateCommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    unresolved_comments_count = serializers.SerializerMethodField()

    class Meta:
        model = MilestoneTemplateItem
        fields = (
            "id",
            "title",
            "description",
            "rich_description",
            "deliverables",
            "acceptance_criteria",
            "order",
            "estimated_hours",
            "comments",
            "comments_count",
            "unresolved_comments_count",
        )
        read_only_fields = ("id",)

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_unresolved_comments_count(self, obj):
        return obj.comments.filter(is_resolved=False).count()


class MilestoneTemplateSerializer(serializers.ModelSerializer):
    items = MilestoneTemplateItemSerializer(many=True, read_only=True)
    comments = TemplateCommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    unresolved_comments_count = serializers.SerializerMethodField()

    class Meta:
        model = MilestoneTemplate
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_unresolved_comments_count(self, obj):
        return obj.comments.filter(is_resolved=False).count()


class MilestoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    project_deal_id = serializers.IntegerField(source="project.deal_id", read_only=True)
    project_deal_company = serializers.CharField(source="project.deal.client_company", read_only=True)

    class Meta:
        model = Milestone
        fields = "__all__"
        read_only_fields = ("id", "dev_completed_at", "qa_approved_at", "client_approved_at", "created_at")


class ProjectSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    progress_percent = serializers.IntegerField(read_only=True)
    deal_company = serializers.CharField(source="deal.client_company", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class QAChecklistSerializer(serializers.ModelSerializer):
    is_complete = serializers.BooleanField(read_only=True)
    completion_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = QAChecklist
        fields = "__all__"
        read_only_fields = ("id", "completed_at", "created_at")


class ProjectCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = ProjectComment
        fields = "__all__"
        read_only_fields = ("id", "user", "created_at")
