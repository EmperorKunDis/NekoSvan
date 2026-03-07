from django.contrib import admin

from .models import Milestone, Project, ProjectComment, QAChecklist


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("deal", "status", "start_date", "estimated_end_date")
    list_filter = ("status",)
    inlines = [MilestoneInline]


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("project", "title", "order", "status", "due_date")
    list_filter = ("status",)


@admin.register(QAChecklist)
class QAChecklistAdmin(admin.ModelAdmin):
    list_display = ("project", "checked_by", "is_complete", "completed_at")
    readonly_fields = ("is_complete", "completion_percent")


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ("project", "milestone", "user", "created_at")
