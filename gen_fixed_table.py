
import unicodedata

def get_visual_width(s):
    width = 0
    for char in s:
        if unicodedata.east_asian_width(char) in ('W', 'F'):
            width += 2
        else:
            width += 1
    return width

path = '/home/programmer/Desktop/backend/future_plans/COMBINED_FRONTEND_SRS.md'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

table_start_idx = 365 # Line 366
table_end_idx = 390   # Line 391

header = lines[table_start_idx].strip()
header_cells = [c.strip() for c in header.split('|')[1:-1]]
# Calculate target visual widths
target_widths = [get_visual_width(c) for c in header_cells]

new_table_lines = []

# Header
new_header = "|"
for i, cell in enumerate(header_cells):
    new_header += " " + cell.ljust(target_widths[i]) + " |"
new_table_lines.append(new_header + "\n")

# Separator
new_sep = "|"
for i, width in enumerate(target_widths):
    new_sep += " " + "-" * target_widths[i] + " |"
new_table_lines.append(new_sep + "\n")

# Data rows
for i in range(table_start_idx + 2, table_end_idx + 1):
    row = lines[i].strip()
    cells = [c.strip() for c in row.split('|')[1:-1]]
    new_row = "|"
    for j, cell in enumerate(cells):
        v_width = get_visual_width(cell)
        # Pad with spaces to match target visual width
        padding = target_widths[j] - v_width
        new_row += " " + cell + " " * padding + " |"
    new_table_lines.append(new_row + "\n")

# Output the block for replacement
print("".join(new_table_lines))
