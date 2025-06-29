create_dashboard_query = """
INSERT INTO dashboards (
    dashboard_id, title, created_by, department, start_date, end_date
) VALUES (%s, %s, %s, %s, %s, %s)
"""

insert_dashboard_metrics_query = """
INSERT INTO dashboard_metrics (
    dashboard_id, metric_name, metric_value
) VALUES (%s, %s, %s)
"""

get_dashboard_metadata = """
SELECT title, department, start_date, end_date
FROM dashboards
WHERE dashboard_id = %s
"""

get_dashboard_metrics = """
SELECT metric_name, metric_value
FROM dashboard_metrics
WHERE dashboard_id = %s
"""

get_dashboard_shared_managers = """
SELECT e.employee_id, e.name, e.email
FROM dashboard_shares ds
JOIN employees e ON e.employee_id = ds.manager_id
WHERE ds.dashboard_id = %s
"""

insert_dashboard_share = """
INSERT INTO dashboard_shares (
    dashboard_id, manager_id
) VALUES (%s, %s)
"""

get_shared_managers = """
SELECT e.employee_id, e.name, e.email
FROM dashboard_shares ds
JOIN employees e ON e.employee_id = ds.manager_id
WHERE ds.dashboard_id = %s
"""