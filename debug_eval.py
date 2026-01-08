
def safe_eval(expr, context):
    try:
        return eval(expr, {"__builtins__": {}}, context)
    except Exception as err:
        print(f"Eval failed: {err}")
        return False

uid = "22222222-2222-2222-2222-222222222222"
expr = f"{uid} == 'yes'"
context = {uid: 'yes'} # value is 'yes'

print(f"Expression: {expr}")
print(f"Context: {context}")
result = safe_eval(expr, context)
print(f"Result: {result}")

# Try with quoted key in expression?
expr_quoted = f"'{uid}' == 'yes'" # This compares literal string
print(f"Result quoted: {safe_eval(expr_quoted, context)}")
