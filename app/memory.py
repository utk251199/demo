from collections import defaultdict


MemoryTurn = dict[str, str]

_conversations: dict[str, list[MemoryTurn]] = defaultdict(list)


def get_history(session_id: str) -> list[MemoryTurn]:
    return _conversations[session_id]


def add_turn(session_id: str, role: str, text: str) -> None:
    history = _conversations[session_id]
    history.append({"role": role, "text": text})

    # Keep the demo memory small so prompts do not grow forever.
    if len(history) > 12:
        del history[:-12]


def clear_history(session_id: str) -> None:
    _conversations.pop(session_id, None)
