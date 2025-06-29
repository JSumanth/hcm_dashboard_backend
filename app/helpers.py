def calculate_metrics(conn, department, start_date, end_date):
    with conn.cursor() as cur:
        # Total headcount
        cur.execute("""
            SELECT COUNT(*) FROM employees 
            WHERE department = %s AND role = 'Employee' AND is_active = TRUE
        """, (department,))
        headcount = cur.fetchone()[0]

        # Payroll cost
        cur.execute("""
            SELECT COALESCE(SUM(base_salary), 0) FROM payroll_records
            WHERE month BETWEEN %s AND %s AND employee_id IN (
                SELECT employee_id FROM employees WHERE department = %s
            )
        """, (start_date, end_date, department))
        payroll = cur.fetchone()[0]

        # Overtime hours
        cur.execute("""
            SELECT COALESCE(SUM(overtime_hours), 0) FROM payroll_records
            WHERE month BETWEEN %s AND %s AND employee_id IN (
                SELECT employee_id FROM employees WHERE department = %s
            )
        """, (start_date, end_date, department))
        overtime = cur.fetchone()[0]

    return {
        "headcount": headcount,
        "payroll_cost": float(payroll),
        "total_overtime_hours": float(overtime)
    }
