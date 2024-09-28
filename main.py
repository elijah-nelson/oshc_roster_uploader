from read_amy_roster import get_events_from_pdf
from calendar_api import add_events
import pprint
import tkinter as tk
from tkinter import filedialog
from matthew_shearer_colours import get_shift_types

root = tk.Tk()
root.withdraw()

pdf_filepath = filedialog.askopenfilename()

if pdf_filepath == "":
    print("No pdf file given.")
    exit()

events = get_events_from_pdf(pdf_filepath)

shift_types = get_shift_types(pdf_filepath)

if len(events) != len(shift_types):
    print("Number of shifts doesn't match number of shift types!")
    print("Shift Types:")
    pprint.pprint(shift_types)
else:
    for event, type in zip(events, shift_types):
        event["event_name"] += f" ({type})"


print("Found the following events from the pdf:")
pprint.pprint(events)

print("Adding events to google calendar...")
add_events(events)
