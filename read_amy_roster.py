from pypdf import PdfReader
from collections import defaultdict
import pprint

EARLIEST_TIME = "06:30"
LATEST_TIME = "06:00"


def format_to_24_hr(time: str) -> str:
    hour = time[:2]
    minute = time[2:]
    if hour == "12" or time >= EARLIEST_TIME:
        return time
    elif time <= LATEST_TIME:
        return str(int(hour) + 12) + minute
    raise ValueError(f"Time outside of expected working hours: {time}")


def line_segment_indices(line: str) -> list[tuple[int, str]]:
    output = []
    starting_i = 0
    current_segment = ""
    for i, c in enumerate(line):
        if c == " ":
            if current_segment:
                output.append((starting_i, current_segment))
                current_segment = ""
            continue

        if current_segment:
            current_segment += c
        else:
            starting_i = i
            current_segment = c

    if current_segment:
        output.append((starting_i, current_segment))
        current_segment = ""

    return output


def left_pad_time(time: str) -> str:
    if len(time) == 4:
        return "0" + time
    elif len(time) == 5:
        return time
    raise ValueError(f"Invalid time format: {time}")


def get_events_from_pdf(filepath: str) -> list[dict[str, str]]:
    reader = PdfReader(filepath)
    page = reader.pages[0]
    layout_text = page.extract_text(extraction_mode="layout")
    lines = layout_text.splitlines()

    title = lines[0]
    print(title)
    dates = lines[1]

    date_indices = line_segment_indices(dates)

    amy_line = next(filter(lambda line: "AMY" in line, lines))
    shift_indices = line_segment_indices(amy_line)

    date_shifts = defaultdict(list)
    for i, shift in shift_indices:
        if "-" not in shift:
            # must be valid shift format
            continue
        # find closest date based on position in string
        closest_date = min(date_indices, key=lambda tup: abs(tup[0] - i))[1]
        date_shifts[closest_date].append(shift)

    date_shifts: dict[str, list[str]] = dict(date_shifts)

    events = []  # keys: event_name (str), event_start (datetime), event_end (datetime)
    for date, times in date_shifts.items():
        date = date.replace(".", "-")

        for time in times:
            event_name = "Amy shift"

            if time.startswith("T-"):
                time = time.removeprefix("T-")
                event_name = "Amy training shift"

            if time.startswith("S-"):
                time = time.removeprefix("S-")
                event_name = "Amy supervising shift"

            start_time, end_time = time.split("-")

            # left pad with 0 to ensure string comparison works
            start_time = left_pad_time(start_time)
            end_time = left_pad_time(end_time)

            # convert to 24 hour
            start_time = format_to_24_hr(start_time)
            end_time = format_to_24_hr(end_time)

            # format to RFC 3339 -> YYYY-MM-DDTHH:MM:SSZ
            event_start = f"{date}T{start_time}:00+10:00"
            event_end = f"{date}T{end_time}:00+10:00"

            events.append(
                {
                    "event_name": event_name,
                    "event_start": event_start,
                    "event_end": event_end,
                }
            )

    return events
