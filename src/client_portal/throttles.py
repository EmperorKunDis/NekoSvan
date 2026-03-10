from rest_framework.throttling import AnonRateThrottle


class PortalReadThrottle(AnonRateThrottle):
    scope = "portal_read"


class PortalWriteThrottle(AnonRateThrottle):
    scope = "portal_write"
