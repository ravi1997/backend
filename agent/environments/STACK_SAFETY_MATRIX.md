# Stack Safety Matrix

Defines commands that are flagged as "Dangerous" based on the tech stack. The agent must check this matrix before proposing a `run_command` action.

## Universal Rules (All Stacks)

| Command Pattern | Risk | LOCAL | CI | PROD |
| :--- | :--- | :--- | :--- | :--- |
| `rm -rf /` (or root) | **Catastrophic** | **BLOCK** | **BLOCK** | **BLOCK** |
| `rm -rf *` (CWD) | High | Confirm | Allow | **BLOCK** |
| `git reset --hard` | High | Confirm | Allow | **BLOCK** |
| `git clean -fdx` | High | Confirm | Allow | **BLOCK** |
| `shutdown`, `reboot` | High | Confirm | **BLOCK** | **BLOCK** |
| `chmod -R 777` | Security | Warn | Allow | **BLOCK** |

## Protocol: Safety Check
Before running *any* command in PROD or CI check:
1.  Is it in the **Universal Block List**? -> **STOP**.
2.  Is it in the **Stack Block List**? -> **STOP**.
3.  Does it modify persistent state (DB, Filesystem)?
    -   **PROD**: **STOP**. Require explicit user override.
    -   **CI**: Allow only if targeting temp/artifact dirs.

---

## Stack-Specific Matrices

### Python
| Command | Reason | LOCAL | CI | PROD |
| :--- | :--- | :--- | :--- | :--- |
| `pip install <pkg>` | Mutates Global Env | Allow (venv) | Allow | **BLOCK** |
| `pip uninstall -y` | Destructive | Allow | Allow | **BLOCK** |
| `manage.py migrate` | Schema Change | Allow | **BLOCK** | **BLOCK** |
| `flask db upgrade` | Schema Change | Allow | **BLOCK** | **BLOCK** |

### Node.js / Javascript
| Command | Reason | LOCAL | CI | PROD |
| :--- | :--- | :--- | :--- | :--- |
| `npm install` (no arg) | Updates lockfile? | Allow | **BLOCK** (`ci` only) | **BLOCK** |
| `npm update` | Updates versions | Allow | **BLOCK** | **BLOCK** |
| `rm -rf node_modules` | Performance | Allow | Allow | **BLOCK** |
| `pm2 delete` | Downtime | Allow | **BLOCK** | **BLOCK** |

### Docker / Kubernetes
| Command | Reason | LOCAL | CI | PROD |
| :--- | :--- | :--- | :--- | :--- |
| `docker system prune` | Deletes cache | Warn | Allow | **BLOCK** |
| `docker stop $(docker ps -q)` | Stops All | Warn | **BLOCK** | **BLOCK** |
| `kubectl delete namespace` | Destructive | **BLOCK** | **BLOCK** | **BLOCK** |
| `kubectl apply ...` | Config Change | Allow | Allow | **BLOCK** (Requires Review) |

### Databases (Postgres/MySQL)
| Command | Reason | LOCAL | CI | PROD |
| :--- | :--- | :--- | :--- | :--- |
| `DROP TABLE` | Data Loss | Warn | Allow | **BLOCK** |
| `TRUNCATE` | Data Loss | Warn | Allow | **BLOCK** |
| `pg_restore` | Overwrite | Warn | Allow | **BLOCK** |
