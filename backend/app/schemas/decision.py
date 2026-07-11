from enum import Enum


class Decision(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    SANITIZE = "SANITIZE"
    MODIFY = "MODIFY"
    ESCALATE = "ESCALATE"
    HUMAN_APPROVAL = "HUMAN_APPROVAL"