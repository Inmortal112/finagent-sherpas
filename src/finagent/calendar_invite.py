"""The chosen first step, as two events in the family's own calendar (an .ics file, iCalendar, RFC 5545).

- Tomorrow, 10:00: "First step: add more life insurance", with the one or two practical actions to start it.
- Day 3, 10:00: "Look at your home again", with the link back to their page, where the check-in waits.

Times are "floating" (no time zone): 10:00 wherever the family is. Fixed words, the step's own title and its first
moves: no figures and no model. An iPhone opens the file with "Add to Calendar"; so do Google and Outlook.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from finagent import house
from finagent.sessions import CHECK_IN_AFTER_DAYS

START_HOUR = 10


def build(session: dict, first_day: date, page_url: str | None = None) -> str | None:
    """The calendar file for this session's chosen step, or None when no step has been chosen."""
    decision = session.get("decision")
    if not decision:
        return None
    step = decision.get("plain_title") or decision["title"]
    moves = house.first_moves(decision["title"])
    back = first_day + timedelta(days=CHECK_IN_AFTER_DAYS - 1)   # chosen today, first step tomorrow, check-in on day 3
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    uid = session["session_id"]

    first = _event(f"{uid}-first-step@under-one-roof", stamp, first_day, 30,
                   f"First step: {_lower_first(step)}",
                   "\n".join([*(f"- {move}" for move in moves),
                              "A few minutes is enough. You do not have to finish it in one go."]),
                   page_url, alarm_minutes=15)
    check = _event(f"{uid}-check-in@under-one-roof", stamp, back, 15,
                   "Look at your home again",
                   f"A few days ago you chose a first step: {_lower_first(step)}. "
                   "Open your home and tell it whether you have started."
                   + (f"\n{page_url}" if page_url else ""),
                   page_url, alarm_minutes=0)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Under One Roof//Family plan//EN", "CALSCALE:GREGORIAN",
             "METHOD:PUBLISH", *first, *check, "END:VCALENDAR"]
    return "".join(_fold(line) + "\r\n" for line in lines)


def _event(uid: str, stamp: str, day: date, minutes: int, summary: str, description: str,
           url: str | None, alarm_minutes: int) -> list[str]:
    start = datetime(day.year, day.month, day.day, START_HOUR)
    end = start + timedelta(minutes=minutes)
    lines = ["BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{stamp}",
             f"DTSTART:{start:%Y%m%dT%H%M%S}", f"DTEND:{end:%Y%m%dT%H%M%S}",
             f"SUMMARY:{_escape(summary)}", f"DESCRIPTION:{_escape(description)}"]
    if url:
        lines.append(f"URL:{url}")
    lines += ["BEGIN:VALARM", "ACTION:DISPLAY", f"DESCRIPTION:{_escape(summary)}",
              f"TRIGGER:-PT{alarm_minutes}M", "END:VALARM", "END:VEVENT"]
    return lines


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\r\n", "\n").replace("\n", "\\n")


def _fold(line: str) -> str:
    """Lines longer than 75 bytes continue on the next line after a space (the standard asks for it)."""
    out, current = [], b""
    for char in line:
        encoded = char.encode("utf-8")
        if len(current) + len(encoded) > (75 if not out else 74):
            out.append(current.decode("utf-8"))
            current = b""
        current += encoded
    out.append(current.decode("utf-8"))
    return "\r\n ".join(out)


def _lower_first(text: str) -> str:
    return text[:1].lower() + text[1:] if text[:2] != text[:2].upper() else text
