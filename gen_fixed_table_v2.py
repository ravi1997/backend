
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

# We want the output to match the visual positions of the header's pipes
def get_pipe_visual_positions(line):
    line = line.rstrip('\n')
    pos = 0
    indices = []
    for char in line:
        if char == '|':
            indices.append(pos)
        pos += get_visual_width(char)
    return indices

target_pipe_positions = get_pipe_visual_positions(lines[table_start_idx])
col_count = len(target_pipe_positions) - 1

new_table_lines = []

# Row 0: Header (keep as is, or reconstruct)
new_table_lines.append(lines[table_start_idx])

# Row 1: Separator (match target positions)
sep_cells = lines[table_start_idx + 1].strip().split('|')[1:-1]
new_sep = "|"
for i in range(col_count):
    # current pipe at target_pipe_positions[i]
    # next pipe at target_pipe_positions[i+1]
    # width between them is gap - 1 (for the starting pipe)
    width = target_pipe_positions[i+1] - target_pipe_positions[i] - 1
    new_sep += " " + "-" * (width - 2) + " |"
    # Wait, simple: just dash-fill the gap
    # Actually, separator needs to be at least 3 dashes
    # Let's just do it simply
new_table_lines.append(new_sep + "\n") # Wait, I'll just use the old separator if it's already okay

# Restore separator if it was okay before I messed it up?
# Actually line 367 in step 38 was [0, 9, 54, 66, 139, 182, 202]
# Which matches the header.
# I'll just use those indices.

for idx in range(table_start_idx + 1, table_end_idx + 1):
    line = lines[idx].strip()
    cells = [c.strip() for c in line.split('|')[1:-1]]
    
    new_row = "|"
    for i in range(col_count):
        cell_content = cells[i] if i < len(cells) else ""
        # target width for this cell (including surrounding spaces)
        target_width = target_pipe_positions[i+1] - target_pipe_positions[i] - 1
        
        # We assume the style is "content" followed by spaces
        # with one space before the content.
        # " " + content + (spaces to fill target_width)
        
        # Wait, if target_width is 12 (like " Auth       ")
        # and content is "❌" (visual width 2)
        # We need " " (1) + "❌" (2) + "         " (9) = 12 columns.
        
        v_content = get_visual_width(cell_content)
        # Spaces to add: target_width - 1 (leading space) - v_content
        spaces_needed = target_width - 1 - v_content
        
        new_row += " " + cell_content + (" " * spaces_needed) + "|"
    new_table_lines.append(new_row + "\n")

# Output for replacement
print("".join(new_table_lines))
