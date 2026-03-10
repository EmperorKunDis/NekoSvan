import json
import time

from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Notification


class NotificationSSEView(APIView):
    """SSE endpoint for real-time notifications."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        def event_stream():
            last_id = 0
            while True:
                notifications = Notification.objects.filter(
                    user=request.user,
                    read=False,
                    id__gt=last_id,
                ).order_by("id")[:10]

                for notification in notifications:
                    data = json.dumps({
                        "id": notification.id,
                        "title": notification.title,
                        "message": notification.message,
                        "link": notification.link,
                        "deal_id": notification.deal_id,
                        "created_at": notification.created_at.isoformat(),
                    })
                    yield f"data: {data}\n\n"
                    last_id = notification.id

                # Unread count update
                unread = Notification.objects.filter(user=request.user, read=False).count()
                yield f"event: unread_count\ndata: {json.dumps({'unread_count': unread})}\n\n"

                # Heartbeat every 5 seconds
                time.sleep(5)
                yield ": heartbeat\n\n"

        response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response
