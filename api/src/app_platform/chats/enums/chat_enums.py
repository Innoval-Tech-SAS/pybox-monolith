"""Tipo de chat (directo/grupo) y rol de un miembro dentro de un chat grupal."""

from enum import IntEnum


class ChatType(IntEnum):
    DIRECT = 0
    GROUP = 1


class MemberRole(IntEnum):
    MEMBER = 0
    ADMIN = 1
    OWNER = 2
