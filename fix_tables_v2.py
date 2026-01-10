
import re

def get_visual_width(s):
    # For this task, we assume all characters are 1 width, 
    # except we've already replaced multi-byte ones with regular ones.
    return len(s)

def align_table(lines):
    rows = []
    for line in lines:
        line = line.strip()
        if not line: continue
        cells = [c.strip() for c in line.split('|')]
        if cells[0] == '': cells = cells[1:]
        if cells[-1] == '': cells = cells[:-1]
        rows.append(cells)
    
    if not rows: return lines
    
    num_cols = max(len(r) for r in rows)
    widths = [0] * num_cols
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
            
    new_lines = []
    for i, row in enumerate(rows):
        rendered_row = "|"
        for j in range(num_cols):
            content = row[j] if j < len(row) else ""
            if i == 1: # separator
                # Markdown requires at least 3 dashes
                w = max(widths[j], 3)
                rendered_row += " " + "-" * w + " |"
            else:
                rendered_row += " " + content.ljust(widths[j]) + " |"
        new_lines.append(rendered_row)
    return new_lines

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace special characters everywhere first
    content = content.replace('\u2011', '-')
    content = content.replace('\u202f', ' ')
    content = content.replace('\u2010', '-') # hyphen
    content = content.replace('\u2013', '-') # en dash
    content = content.replace('\u2014', '-') # em dash
    
    lines = content.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|') and i + 1 < len(lines) and '---' in lines[i+1]:
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            aligned = align_table(table_lines)
            new_lines.extend(aligned)
        else:
            new_lines.append(line)
            i += 1
            
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')

if __name__ == "__main__":
    fix_file('/home/programmer/Desktop/backend/future_plans/COMBINED_FRONTEND_SRS.md')
