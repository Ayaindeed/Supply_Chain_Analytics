import sys

# Ensure our mounted project paths are importable inside Airflow containers
for p in ["/opt/airflow", "/opt/airflow/scripts"]:
    if p not in sys.path:
        sys.path.insert(0, p)
