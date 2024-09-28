import fitz  # PyMuPDF


def combine_adjacent_bboxes(drawing1, drawing2):
    # Check if the rectangles are aligned vertically
    if (
        abs(drawing1["rect"][0] - drawing2["rect"][0]) < 2
        and drawing1["rect"][1] <= drawing2["rect"][3]
        and drawing1["rect"][3] >= drawing2["rect"][1]
    ):
        # Combine the boxes
        combined_bbox = (
            min(drawing1["rect"][0], drawing2["rect"][0]),  # x0
            min(drawing1["rect"][1], drawing2["rect"][1]),  # y0
            max(drawing1["rect"][2], drawing2["rect"][2]),  # x1
            max(drawing1["rect"][3], drawing2["rect"][3]),  # y1
        )
        return combined_bbox
    # Check if the rectangles are aligned horizontally
    elif (
        abs(drawing1["rect"][1] - drawing2["rect"][1]) < 2
        and drawing1["rect"][0] <= drawing2["rect"][2]
        and drawing1["rect"][2] >= drawing2["rect"][0]
    ):
        # Combine the boxes
        combined_bbox = (
            min(drawing1["rect"][0], drawing2["rect"][0]),  # x0
            min(drawing1["rect"][1], drawing2["rect"][1]),  # y0
            max(drawing1["rect"][2], drawing2["rect"][2]),  # x1
            max(drawing1["rect"][3], drawing2["rect"][3]),  # y1
        )
        return combined_bbox
    return None


def get_text_to_bg_colour(
    filepath: str,
) -> list[tuple[str, tuple[float, float, float]]]:

    # Function to check if the text bbox is contained within the rectangle bbox
    def is_bbox_within(text_bbox, rect_bbox, tolerance=1):
        return (
            text_bbox[0] >= rect_bbox[0] - tolerance
            and text_bbox[1] >= rect_bbox[1] - tolerance
            and text_bbox[2] <= rect_bbox[2] + tolerance
            and text_bbox[3] <= rect_bbox[3] + tolerance
        )

    # Open the PDF
    doc = fitz.open(filepath)

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)  # Load the page

        # Get all drawing objects (rectangles and shapes) that could be backgrounds
        drawings = page.get_drawings()

        # Create a list to hold combined drawings
        combined_drawings = []

        # Combine adjacent boxes with the same color
        for drawing in drawings:
            if drawing["fill"]:
                # Check if the current drawing can be combined with any already combined drawing
                combined = False
                for combined_drawing in combined_drawings:
                    if drawing["fill"] == combined_drawing["fill"]:  # Same color
                        new_bbox = combine_adjacent_bboxes(combined_drawing, drawing)
                        if new_bbox:  # If boxes can be combined
                            combined_drawing["rect"] = (
                                new_bbox  # Update the combined drawing
                            )
                            combined = True
                            break
                if (
                    not combined
                ):  # If no combination was made, add the drawing as a new combined box
                    combined_drawings.append(
                        {"rect": drawing["rect"], "fill": drawing["fill"]}
                    )

        # Extract text with bounding box (bbox) and color information
        text_instances = page.get_text("dict")["blocks"]

        text_bg_colours = []
        # Iterate over text instances
        for block in text_instances:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"]
                    text_bbox = span["bbox"]  # Bounding box of the text

                    # Check for a matching background (rectangles) that overlaps with the text bbox
                    for combined_drawing in combined_drawings:
                        if is_bbox_within(text_bbox, combined_drawing["rect"]):
                            matched_bg_color = combined_drawing["fill"]
                            text_bg_colours.append((text, matched_bg_color))
                            break

    return text_bg_colours


SHIFT_TYPES = [
    "Top playground/Prep",
    "OSHC Building",
    "Breakfast/Kitchen",
    "Train",
    "Training",
    "Ouside Play",
    "Outside Play",  # futureproof typo fix
]


def get_shift_types(filepath: str) -> list[str]:

    text_bg_colours = get_text_to_bg_colour(filepath)

    # first get colours for Amy shifts
    i = 0
    while i < len(text_bg_colours) and "AMY" not in text_bg_colours[i][0]:
        i += 1

    i += 1
    shift_times_and_colours = []  # [(time, colour)]
    while (
        i < len(text_bg_colours)
        and "-" in text_bg_colours[i][0]
        and "*" not in text_bg_colours[i][0]
    ):
        text, bg_colour = text_bg_colours[i]
        shift_times_and_colours.append(
            (text.removeprefix("T-").removeprefix("S-"), bg_colour)
        )
        i += 1

    shift_type_colours = []  # (shift, colour)
    for text, bg_colour in text_bg_colours:
        if text in SHIFT_TYPES:
            shift_type_colours.append((text, bg_colour))

    out_shift_types = []
    for _, colour in shift_times_and_colours:

        shift_type = min(
            shift_type_colours,
            key=lambda tup: sum(abs(x - y) for x, y in zip(tup[1], colour)),
        )[0]

        out_shift_types.append(shift_type)

    return out_shift_types
