
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

# Table starts at line 366 (index 365) and ends at line 391 (index 390)
table_start = 365
table_end = 391

header_line = lines[table_start].rstrip()
# Calculate target visual widths from header
header_cells = header_line.split('|')
# header_cells[0] is empty, header_cells[1] is ' Method ', etc.
# We want to keep the same visual column positions.

def get_row_visual_info(line):
    line = line.rstrip()
    if not line.startswith('|'): return None
    cells = line.split('|')
    if cells[0] == '': cells = cells[1:]
    if cells[-1] == '': cells = cells[:-1]
    return cells

header_data = get_row_visual_info(header_line)
target_widths = [get_visual_width(cell) for cell in header_data]

new_lines = lines[:]
for i in range(table_start + 1, table_end + 1):
    row_data = get_row_visual_info(lines[i])
    if not row_data: continue
    
    if i == table_start + 1: # separator
        # For separator, we match the visual width with dashes
        new_row = "|"
        for j, width in enumerate(target_widths):
            # separators are usually |---|
            # we need to maintain character alignment too if possible, 
            # but visual is priority for this error.
            # Actually, most linters want character alignment for the separator '-' too.
            # But here the problem is emojis in other rows.
            new_row += "-" * width + "|" # This might be too simple, let's keep it as is if it matches
            # Wait, let's just use the current separator but ensure it's correct width
            pass
        # Actually, let's just rebuild the whole table rows to be visually aligned.
        pass

    # Rebuild the row
    new_cells = []
    for j, cell in enumerate(row_data):
        cell_content = cell.strip()
        current_v_width = get_visual_width(cell_content)
        # We need a leading and trailing space if possible, or just match target_width
        # target_width includes the leading/trailing spaces from the header cells.
        # Header cell was " Method " (width 8). 
        # Target width is 8.
        # content "POST" (width 4).
        # We want " POST   " (width 8).
        
        # Calculate padding
        padding_needed = target_widths[j] - current_v_width
        if padding_needed < 0:
            # Column is too narrow for content! We should expand target_widths.
            # But for this task, we want to match line 368 specifically.
            pass
        
        # Most markdown tables use " " + content + " " + extra_spaces
        # Let's just do ljust with spaces.
        padded_content = " " + cell_content + " " + " " * (target_widths[j] - current_v_width - 2)
        # Wait, if target_width is 12 and current is 2, and we have 1 space before, 1 after, 
        # then we need 12 - 2 - 2 = 8 spaces.
        # If target_width is 8 and current is 4, we need 8-4-2 = 2 spaces.
        new_cells.append(padded_content)
    
    new_lines[i] = "|" + "|".join(new_cells) + "|\n"

# Wait, the above logic is a bit brittle. Let's just fix the "Auth" column spaces manually or 
# use a more robust logic.

# Let's try a simpler fix: for each line in the table, 
# if it has an emoji in the 3rd column (Auth), remove one space from it.

for i in range(table_start + 2, table_end + 1): # Start from data rows
    line = lines[i]
    cells = line.split('|')
    if len(cells) > 3:
        auth_cell = cells[3]
        if any(unicodedata.east_asian_width(c) in ('W', 'F') for c in auth_cell):
            # Remove one space
            if auth_cell.endswith(' '):
                cells[3] = auth_cell[:-1]
                new_lines[i] = '|'.join(cells)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
