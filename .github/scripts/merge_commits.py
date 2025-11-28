import json
import re
from datetime import datetime, timedelta

# --- Configuration ---
# FIX: The file name is correctly set to 'commits.json'
COMMITS_FILE = './.github/data/commits.json' 
BASE_SVG_PATH = './snake_base.svg'
FINAL_SVG_PATH = './github-contribution-grid-snake.svg'
CONTRIBUTION_LEVEL_2_COLOR = '#0e4429' # Dark Green
GITHUB_GRAPH_DAYS = 365 # GitHub's graph length

def get_target_dates():
    """Load the list of dates for the back-dated commits."""
    with open(COMMITS_FILE, 'r') as f:
        return [datetime.strptime(d, '%Y-%m-%d').date() for d in json.load(f)]

def get_graph_start_date():
    """Determine the start date of the 365-day contribution graph."""
    return (datetime.now().date() - timedelta(days=GITHUB_GRAPH_DAYS))

def calculate_grid_position(target_date):
    """Calculates the column (x) and row (y) position for a given date."""
    # Find the day number from the start of the graph
    start_date = get_graph_start_date()
    day_number = (target_date - start_date).days
    
    # Calculate column (x) and row (y)
    column = day_number // 7 
    row = day_number % 7    
    
    # Simplified calculation for Platane SVG:
    x_coord = 13 + (column * 14)
    y_coord = 13 + (row * 14)

    return x_coord, y_coord

def generate_rect_svg(x, y, color):
    """Generates the SVG <rect> tag for a contribution mark."""
    # Standard rect size used by the Platane snake SVG
    return f'<rect width="10" height="10" x="{x}" y="{y}" fill="{color}" />'

def merge_svg_data():
    """Reads the base SVG and injects the fake commit rectangles."""
    with open(BASE_SVG_PATH, 'r') as f:
        svg_content = f.read()

    target_dates = get_target_dates()
    new_rects = ""
    
    # Find the closing tag for the contribution grid (<g>) where the rectangles are drawn
    closing_tag_match = re.search(r'</g>\s*</svg>', svg_content)
    if not closing_tag_match:
        # We need to make sure this error is fatal if the file wasn't created right
        print(f"Error: Could not find the SVG injection point in {BASE_SVG_PATH}.")
        return

    # Generate the SVG code for each fake commit
    for date in target_dates:
        # Check if the date is within the current 365-day graph window
        if date >= get_graph_start_date() and date <= datetime.now().date():
            x, y = calculate_grid_position(date)
            new_rects += generate_rect_svg(x, y, CONTRIBUTION_LEVEL_2_COLOR)

    # Inject the new rectangles into the SVG content
    injection_point = closing_tag_match.start()
    final_svg = svg_content[:injection_point] + new_rects + svg_content[injection_point:]

    # Save the merged SVG file
    # This step will succeed now that the 'dist' folder is guaranteed to exist
    with open(FINAL_SVG_PATH, 'w') as f:
        f.write(final_svg)

if __name__ == '__main__':
    merge_svg_data()
