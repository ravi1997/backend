import math
import random
import datetime
import json
import re

# Allowed safe modules for custom scripts
ALLOWED_MODULES = {
    'math': math,
    'random': random,
    'datetime': datetime,
    'json': json,
    're': re
}

def execute_safe_script(script, input_data=None):
    """
    Executes a custom python script in a restricted environment.
    
    Args:
        script (str): The python script to execute.
        input_data (dict): Data to be accessible in the script as 'input'.
        
    Returns:
        dict: The local scope variables after execution.
        
    The script should set variables in the local scope to return data.
    Commonly, the script should set a 'result' variable.
    """
    if input_data is None:
        input_data = {}
    
    # 1. Define restricted globals
    # We remove __builtins__ to prevent access to open(), __import__(), etc.
    safe_globals = {
        "__builtins__": {
            "abs": abs,
            "all": all,
            "any": any,
            "bin": bin,
            "bool": bool,
            "chr": chr,
            "dict": dict,
            "divmod": divmod,
            "enumerate": enumerate,
            "filter": filter,
            "float": float,
            "format": format,
            "frozenset": frozenset,
            "getattr": getattr,
            "hasattr": hasattr,
            "hash": hash,
            "hex": hex,
            "int": int,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "iter": iter,
            "len": len,
            "list": list,
            "map": map,
            "max": max,
            "min": min,
            "next": next,
            "oct": oct,
            "ord": ord,
            "pow": pow,
            "range": range,
            "repr": repr,
            "reversed": reversed,
            "round": round,
            "set": set,
            "slice": slice,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
            "type": type,
            "zip": zip,
        },
        "input": input_data  # Inject input context
    }
    
    # 2. Add safe modules
    safe_globals.update(ALLOWED_MODULES)
    
    # 3. Define local scope to capture output
    local_scope = {}
    
    try:
        # 4. Execute script
        exec(script, safe_globals, local_scope)
        return local_scope
    except Exception as e:
        # Re-raise with clear message
        raise Exception(f"Script execution failed: {str(e)}")
