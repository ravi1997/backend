
import re

def align_markdown_table(lines):
    if not lines:
        return []
    
    # Split each line into cells
    table_data = []
    for line in lines:
        if line.strip().startswith('|'):
            cells = [cell.strip() for cell in line.strip().split('|')]
            # split('|') with start/end pipes gives ['' or ' ', cell1, cell2, ..., '' or ' ']
            if cells[0] == '': cells = cells[1:]
            if cells[-1] == '': cells = cells[:-1]
            table_data.append(cells)
        else:
            # Not a table line (shouldn't happen with correct input)
            return lines

    if not table_data:
        return lines

    # Determine max width for each column
    num_columns = max(len(row) for row in table_data)
    col_widths = [0] * num_columns
    for row in table_data:
        for i, cell in enumerate(row):
            # We need to account for visual width, but for now let's just use len()
            # and replace non-ascii characters that might confuse len()
            clean_cell = cell.replace('\u2011', '-').replace('\u202f', ' ')
            col_widths[i] = max(col_widths[i], len(clean_cell))

    # Reconstruct the table
    new_lines = []
    for i, row in enumerate(table_data):
        new_row = "| "
        for j in range(num_columns):
            cell_content = row[j] if j < len(row) else ""
            # Replace special characters for consistency
            cell_content = cell_content.replace('\u2011', '-').replace('\u202f', ' ')
            
            if i == 1: # The separator row
                new_row += "-" * col_widths[j]
            else:
                new_row += cell_content.ljust(col_widths[j])
            
            if j < num_columns - 1:
                new_row += " | "
            else:
                new_row += " |"
        new_lines.append(new_row)
    
    return new_lines

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|') and i + 1 < len(lines) and line.strip().count('|') >= 2 and lines[i+1].strip().startswith('|---'):
            # Start of a table
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            
            aligned_table = align_markdown_table(table_lines)
            for tl in aligned_table:
                new_lines.append(tl + "\n")
        else:
            new_lines.append(line)
            i += 1
            
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    process_file('/home/programmer/Desktop/backend/future_plans/COMBINED_FRONTEND_SRS.md')
