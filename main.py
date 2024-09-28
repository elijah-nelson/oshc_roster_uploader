from read_amy_roster import get_events_from_pdf
from calendar_api import add_events
import pprint
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

pdf_filepath = filedialog.askopenfilename()

if pdf_filepath == "":
    print("No pdf file given.")
    exit()

events = get_events_from_pdf(pdf_filepath)

print("Found the following events from the pdf:")
pprint.pprint(events)

print("Adding events to google calendar...")
add_events(events)
