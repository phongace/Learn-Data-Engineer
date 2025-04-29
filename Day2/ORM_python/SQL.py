"""
SQL queries for employees and departments tables
This module contains various SQL queries to interact with employees and departments tables
"""

import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from tabulate import tabulate
import csv
from datetime import datetime

# Load environment variables
load_dotenv()


def get_db_connection():
    """
    Create a database connection using environment variables
    Returns:
        psycopg2.connection: Database connection object
    Raises:
        Exception: If connection fails
    """
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise


def execute_query(query, params=None):
    """
    Execute a SQL query and return results
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Query parameters. Defaults to None.
    Returns:
        list: Query results for SELECT queries
        int: Number of affected rows for other queries
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            results = cur.fetchall()
            return results
        else:
            conn.commit()
            return cur.rowcount
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        conn.rollback()
        raise
    finally:
        conn.close()


# Các câu truy vấn thống kê cơ bản
def get_department_stats():
    """Thống kê số lượng nhân viên theo phòng ban"""
    query = """
    SELECT 
        d.name as department_name,
        COUNT(e.id) as employee_count,
        MIN(e.hire_date) as earliest_hire,
        MAX(e.hire_date) as latest_hire
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id
    GROUP BY d.id, d.name
    ORDER BY employee_count DESC;
    """
    results = execute_query(query)
    print("\nThống kê theo phòng ban:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


def get_employee_list(department_name=None, limit=10):
    """Lấy danh sách nhân viên, có thể lọc theo phòng ban"""
    query = """
    SELECT 
        e.id,
        e.first_name,
        e.last_name,
        e.email,
        d.name as department_name,
        e.hire_date
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    """
    params = []
    if department_name:
        query += " WHERE d.name = %s"
        params.append(department_name)

    query += " ORDER BY e.hire_date DESC LIMIT %s"
    params.append(limit)

    results = execute_query(query, params)
    print(f"\nDanh sách {limit} nhân viên mới nhất:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


def search_employees(search_term):
    """Tìm kiếm nhân viên theo tên hoặc email"""
    query = """
    SELECT 
        e.id,
        e.first_name,
        e.last_name,
        e.email,
        d.name as department_name
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE 
        LOWER(e.first_name) LIKE LOWER(%s) OR
        LOWER(e.last_name) LIKE LOWER(%s) OR
        LOWER(e.email) LIKE LOWER(%s)
    ORDER BY e.last_name, e.first_name;
    """
    search_pattern = f"%{search_term}%"
    params = [search_pattern, search_pattern, search_pattern]
    results = execute_query(query, params)
    print(f"\nKết quả tìm kiếm cho '{search_term}':")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


def get_department_hierarchy():
    """Hiển thị cấu trúc phòng ban và số lượng nhân viên"""
    query = """
    SELECT 
        d.name as department,
        COUNT(e.id) as employee_count
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id
    GROUP BY d.id, d.name
    ORDER BY d.name;
    """
    results = execute_query(query)
    print("\nCấu trúc phòng ban:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


def get_employee_details(employee_id):
    """Lấy thông tin chi tiết của một nhân viên"""
    query = """
    SELECT 
        e.id,
        e.first_name,
        e.last_name,
        e.email,
        d.name as department_name,
        e.hire_date,
        e.created_at,
        e.updated_at
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE e.id = %s;
    """
    results = execute_query(query, [employee_id])
    if results:
        print(f"\nThông tin nhân viên ID={employee_id}:")
        print(tabulate(results, headers="keys", tablefmt="psql"))
    else:
        print(f"Không tìm thấy nhân viên với ID={employee_id}")
    return results


def add_employee(first_name, last_name, email, department_name):
    """Thêm nhân viên mới"""
    query = """
    WITH dept AS (
        SELECT id FROM departments WHERE name = %s
    )
    INSERT INTO employees (first_name, last_name, email, department_id)
    SELECT %s, %s, %s, id FROM dept
    RETURNING id;
    """
    try:
        results = execute_query(query, [department_name, first_name, last_name, email])
        print(f"Đã thêm nhân viên mới: {first_name} {last_name}")
        return results
    except Exception as e:
        print(f"Lỗi khi thêm nhân viên: {str(e)}")
        return None


def update_employee_department(employee_id, new_department_name):
    """Cập nhật phòng ban cho nhân viên"""
    query = """
    WITH dept AS (
        SELECT id FROM departments WHERE name = %s
    )
    UPDATE employees
    SET department_id = (SELECT id FROM dept)
    WHERE id = %s;
    """
    affected_rows = execute_query(query, [new_department_name, employee_id])
    if affected_rows:
        print(f"Đã cập nhật phòng ban cho nhân viên ID={employee_id}")
    else:
        print(f"Không tìm thấy nhân viên với ID={employee_id}")
    return affected_rows


def delete_employee(employee_id):
    """Xóa nhân viên"""
    query = "DELETE FROM employees WHERE id = %s;"
    affected_rows = execute_query(query, [employee_id])
    if affected_rows:
        print(f"Đã xóa nhân viên ID={employee_id}")
    else:
        print(f"Không tìm thấy nhân viên với ID={employee_id}")
    return affected_rows


# 1. Basic SELECT
def basic_select():
    """
    Basic SELECT query to retrieve all employees
    Demonstrates the simplest form of SELECT statement
    Returns:
        list: All employees with their details
    """
    query = """
    SELECT * FROM employees;
    """
    results = execute_query(query)
    print("\nAll employees:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 2. SELECT DISTINCT
def select_distinct_departments():
    """
    SELECT DISTINCT query to get unique department names
    Removes duplicate department names from the result
    Returns:
        list: Unique department names
    """
    query = """
    SELECT DISTINCT name FROM departments ORDER BY name;
    """
    results = execute_query(query)
    print("\nUnique department list:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 3. WHERE
def where_example(min_salary=50000):
    """
    WHERE clause example to filter employees
    Shows how to filter records based on conditions
    Args:
        min_salary (int): Minimum salary threshold
    Returns:
        list: Filtered employees
    """
    query = """
    SELECT first_name, last_name, email 
    FROM employees 
    WHERE department_id = 1;
    """
    results = execute_query(query)
    print("\nEngineering department employees:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 4. ORDER BY
def order_by_example():
    """
    ORDER BY example to sort employees
    Demonstrates sorting results by multiple columns
    Returns:
        list: Sorted employee list
    """
    query = """
    SELECT first_name, last_name, email 
    FROM employees 
    ORDER BY last_name ASC, first_name ASC;
    """
    results = execute_query(query)
    print("\nEmployees sorted by name:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 5. AND, OR, NOT
def complex_conditions():
    """
    Complex WHERE conditions using AND, OR, NOT
    Shows how to combine multiple conditions in WHERE clause
    Returns:
        list: Employees matching complex conditions
    """
    query = """
    SELECT e.first_name, e.last_name, d.name as department
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE (d.name = 'Engineering' OR d.name = 'Marketing')
    AND e.hire_date >= '2024-01-01';
    """
    results = execute_query(query)
    print("\nEngineering or Marketing employees hired since 2024:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 6. INSERT INTO
def insert_employee(first_name, last_name, email, department_id):
    """
    INSERT INTO example to add new employee
    Demonstrates inserting new records with RETURNING clause
    Args:
        first_name (str): Employee's first name
        last_name (str): Employee's last name
        email (str): Employee's email
        department_id (int): Department ID
    Returns:
        list: Newly inserted employee details
    """
    query = """
    INSERT INTO employees (first_name, last_name, email, department_id)
    VALUES (%s, %s, %s, %s)
    RETURNING id, first_name, last_name;
    """
    results = execute_query(query, [first_name, last_name, email, department_id])
    print(f"\nNew employee added:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 7. UPDATE
def update_employee_email(employee_id, new_email):
    """
    UPDATE example to modify employee email
    Shows how to update existing records with WHERE clause
    Args:
        employee_id (int): Employee ID to update
        new_email (str): New email address
    Returns:
        list: Updated employee details
    """
    query = """
    UPDATE employees 
    SET email = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id, first_name, last_name, email;
    """
    results = execute_query(query, [new_email, employee_id])
    print(f"\nEmployee email updated:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 8. DELETE
def delete_employee_by_id(employee_id):
    """
    DELETE example to remove employee
    Demonstrates deleting records with WHERE clause
    Args:
        employee_id (int): Employee ID to delete
    Returns:
        list: Deleted employee details
    """
    query = """
    DELETE FROM employees 
    WHERE id = %s
    RETURNING id, first_name, last_name;
    """
    results = execute_query(query, [employee_id])
    print(f"\nEmployee deleted:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 9. MIN/MAX
def get_employee_hire_dates():
    """
    MIN and MAX aggregate functions example
    Shows how to find minimum and maximum values
    Returns:
        list: Earliest and latest hire dates
    """
    query = """
    SELECT 
        MIN(hire_date) as earliest_hire,
        MAX(hire_date) as latest_hire
    FROM employees;
    """
    results = execute_query(query)
    print("\nHire date statistics:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 10. COUNT
def count_employees_by_department():
    """
    COUNT aggregate function with GROUP BY
    Demonstrates counting records with grouping
    Returns:
        list: Employee count per department
    """
    query = """
    SELECT d.name, COUNT(e.id) as employee_count
    FROM departments d
    LEFT JOIN employees e ON d.id = e.department_id
    GROUP BY d.name
    ORDER BY employee_count DESC;
    """
    results = execute_query(query)
    print("\nEmployee count by department:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 11. LIKE
def search_employees_like(pattern):
    """
    LIKE operator for pattern matching
    Shows how to search using wildcards
    Args:
        pattern (str): Search pattern
    Returns:
        list: Matching employees
    """
    query = """
    SELECT first_name, last_name, email
    FROM employees
    WHERE 
        first_name LIKE %s OR 
        last_name LIKE %s OR 
        email LIKE %s;
    """
    pattern = f"%{pattern}%"
    results = execute_query(query, [pattern, pattern, pattern])
    print(f"\nSearch results for '{pattern}':")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 12. IN
def get_employees_in_departments(department_names):
    """
    IN operator for multiple value matching
    Demonstrates filtering with a list of values
    Args:
        department_names (list): List of department names
    Returns:
        list: Employees in specified departments
    """
    placeholders = ",".join(["%s"] * len(department_names))
    query = f"""
    SELECT e.first_name, e.last_name, d.name as department
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    WHERE d.name IN ({placeholders})
    ORDER BY d.name, e.last_name;
    """
    results = execute_query(query, department_names)
    print(f"\nEmployees in departments {', '.join(department_names)}:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 13. BETWEEN
def get_employees_hired_between(start_date, end_date):
    """
    BETWEEN operator for range queries
    Shows how to filter records within a range
    Args:
        start_date (str): Start date in YYYY-MM-DD format
        end_date (str): End date in YYYY-MM-DD format
    Returns:
        list: Employees hired within date range
    """
    query = """
    SELECT first_name, last_name, hire_date
    FROM employees
    WHERE hire_date BETWEEN %s AND %s
    ORDER BY hire_date;
    """
    results = execute_query(query, [start_date, end_date])
    print(f"\nEmployees hired between {start_date} and {end_date}:")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# 14. Aliases
def use_aliases():
    """
    Table and column aliases example
    Demonstrates using aliases for readable results
    Returns:
        list: Employee list with aliased columns
    """
    query = """
    SELECT 
        e.first_name as "First Name",
        e.last_name as "Last Name",
        d.name as "Department"
    FROM employees e
    JOIN departments d ON e.department_id = d.id
    ORDER BY d.name, e.last_name;
    """
    results = execute_query(query)
    print("\nEmployee list (with aliases):")
    print(tabulate(results, headers="keys", tablefmt="psql"))
    return results


# Export functions
def export_table_to_csv(table_name, output_file):
    """
    Export a table to CSV file
    Args:
        table_name (str): Name of the table to export
        output_file (str): Path to save the CSV file
    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        # Get all data from table
        query = f"SELECT * FROM {table_name} ORDER BY id;"
        results = execute_query(query)

        if not results:
            print(f"No data found in table {table_name}")
            return False

        # Create directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)

        # Write to CSV
        with open(f"exports/{output_file}", "w", newline="") as f:
            # Get headers from first row
            headers = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=headers)

            # Write headers and data
            writer.writeheader()
            writer.writerows(results)

        print(f"\nExported {len(results)} rows to exports/{output_file}")
        return True

    except Exception as e:
        print(f"Error exporting {table_name}: {str(e)}")
        return False


def export_employees_to_csv():
    """
    Export employees table to CSV with additional department info
    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        # Get employees with department names
        query = """
        SELECT 
            e.id,
            e.first_name,
            e.last_name,
            e.email,
            d.name as department_name,
            e.hire_date,
            e.created_at,
            e.updated_at
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        ORDER BY e.id;
        """
        results = execute_query(query)

        if not results:
            print("No employees found")
            return False

        # Create directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employees_{timestamp}.csv"

        # Write to CSV
        with open(f"exports/{filename}", "w", newline="") as f:
            headers = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=headers)

            writer.writeheader()
            writer.writerows(results)

        print(f"\nExported {len(results)} employees to exports/{filename}")
        return True

    except Exception as e:
        print(f"Error exporting employees: {str(e)}")
        return False


def export_departments_with_stats():
    """
    Export departments table to CSV with employee statistics
    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        # Get departments with employee counts and other stats
        query = """
        SELECT 
            d.id,
            d.name,
            COUNT(e.id) as employee_count,
            MIN(e.hire_date) as earliest_hire,
            MAX(e.hire_date) as latest_hire,
            d.created_at,
            d.updated_at
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY d.id;
        """
        results = execute_query(query)

        if not results:
            print("No departments found")
            return False

        # Create directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"departments_{timestamp}.csv"

        # Write to CSV
        with open(f"exports/{filename}", "w", newline="") as f:
            headers = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=headers)

            writer.writeheader()
            writer.writerows(results)

        print(f"\nExported {len(results)} departments to exports/{filename}")
        return True

    except Exception as e:
        print(f"Error exporting departments: {str(e)}")
        return False


def export_employees_with_departments():
    """
    Export employees and departments data joined together into a single CSV file
    The output includes all employee details along with their department information

    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        # Get employees joined with departments
        query = """
        SELECT 
            e.id as employee_id,
            e.first_name,
            e.last_name,
            e.email,
            e.hire_date,
            d.id as department_id,
            d.name as department_name,
            -- Calculate department statistics
            COUNT(*) OVER (PARTITION BY d.id) as dept_employee_count,
            MIN(e.hire_date) OVER (PARTITION BY d.id) as dept_earliest_hire,
            MAX(e.hire_date) OVER (PARTITION BY d.id) as dept_latest_hire,
            -- Include creation and update timestamps
            e.created_at as employee_created_at,
            e.updated_at as employee_updated_at,
            d.created_at as department_created_at,
            d.updated_at as department_updated_at
        FROM employees e
        JOIN departments d ON e.department_id = d.id
        ORDER BY d.name, e.last_name, e.first_name;
        """
        results = execute_query(query)

        if not results:
            print("No data found")
            return False

        # Create directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employees-departments_{timestamp}.csv"

        # Write to CSV
        with open(f"exports/{filename}", "w", newline="") as f:
            headers = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=headers)

            writer.writeheader()
            writer.writerows(results)

        print(f"\nExported {len(results)} records to exports/{filename}")
        print("\nFile contains the following columns:")
        print("- Employee: ID, first name, last name, email, hire date")
        print("- Department: ID, name")
        print("- Department Stats: employee count, earliest & latest hire dates")
        print("- Timestamps: creation and update dates for both records")

        # Print sample of the data using tabulate
        print("\nSample of exported data (first 5 rows):")
        print(tabulate(results[:5], headers="keys", tablefmt="psql"))

        return True

    except Exception as e:
        print(f"Error exporting joined data: {str(e)}")
        return False


def export_department_summaries():
    """
    Export a summary of each department with employee statistics
    Creates a CSV with one row per department and aggregated employee data

    Returns:
        bool: True if export successful, False otherwise
    """
    try:
        query = """
        SELECT 
            d.id as department_id,
            d.name as department_name,
            COUNT(e.id) as total_employees,
            MIN(e.hire_date) as earliest_hire,
            MAX(e.hire_date) as latest_hire,
            -- Additional statistics
            COUNT(CASE WHEN e.hire_date >= NOW() - INTERVAL '1 year' THEN 1 END) as hired_last_year,
            COUNT(CASE WHEN e.hire_date >= NOW() - INTERVAL '1 month' THEN 1 END) as hired_last_month,
            -- Include department timestamps
            d.created_at,
            d.updated_at
        FROM departments d
        LEFT JOIN employees e ON d.id = e.department_id
        GROUP BY d.id, d.name
        ORDER BY d.name;
        """
        results = execute_query(query)

        if not results:
            print("No departments found")
            return False

        # Create directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"department-summaries_{timestamp}.csv"

        # Write to CSV
        with open(f"exports/{filename}", "w", newline="") as f:
            headers = results[0].keys()
            writer = csv.DictWriter(f, fieldnames=headers)

            writer.writeheader()
            writer.writerows(results)

        print(f"\nExported {len(results)} department summaries to exports/{filename}")
        print("\nSummary includes:")
        print("- Department details (ID, name)")
        print("- Total employee count")
        print("- Earliest and latest hire dates")
        print("- Recent hiring statistics (last month/year)")

        # Print the summary using tabulate
        print("\nDepartment Summaries:")
        print(tabulate(results, headers="keys", tablefmt="psql"))

        return True

    except Exception as e:
        print(f"Error exporting department summaries: {str(e)}")
        return False


def export_all_tables():
    """
    Export all data in various formats:
    1. Individual tables (employees.csv, departments.csv)
    2. Joined data (employees-departments.csv)
    3. Department summaries (department-summaries.csv)

    Returns:
        tuple: (bool, bool, bool) indicating success of each export
    """
    print("\nStarting comprehensive data export...")

    # Export individual tables
    employees_success = export_employees_to_csv()
    departments_success = export_departments_with_stats()

    # Export joined data
    joined_success = export_employees_with_departments()

    # Export department summaries
    summaries_success = export_department_summaries()

    # Print summary
    print("\nExport Summary:")
    print(f"Employees export: {'Success' if employees_success else 'Failed'}")
    print(f"Departments export: {'Success' if departments_success else 'Failed'}")
    print(f"Joined data export: {'Success' if joined_success else 'Failed'}")
    print(f"Department summaries: {'Success' if summaries_success else 'Failed'}")

    return employees_success, departments_success, joined_success, summaries_success


if __name__ == "__main__":
    # Ví dụ sử dụng các hàm
    print("1. Thống kê theo phòng ban:")
    get_department_stats()

    print("\n2. Danh sách nhân viên của phòng Engineering:")
    get_employee_list("Engineering", 5)

    print("\n3. Tìm kiếm nhân viên có chữ 'john':")
    search_employees("john")

    print("\n4. Cấu trúc phòng ban:")
    get_department_hierarchy()

    print("\n5. Chi tiết nhân viên ID=1:")
    get_employee_details(1)

    # Test các câu lệnh SQL
    print("\n1. SELECT cơ bản:")
    basic_select()

    print("\n2. SELECT DISTINCT:")
    select_distinct_departments()

    print("\n3. WHERE:")
    where_example()

    print("\n4. ORDER BY:")
    order_by_example()

    print("\n5. Complex conditions (AND, OR, NOT):")
    complex_conditions()

    print("\n6. COUNT:")
    count_employees_by_department()

    print("\n7. LIKE:")
    search_employees_like("john")

    print("\n8. IN:")
    get_employees_in_departments(["Engineering", "Marketing"])

    print("\n9. BETWEEN:")
    get_employees_hired_between("2024-01-01", "2024-12-31")

    print("\n10. Aliases:")
    use_aliases()

    print("\n11. Exporting tables to CSV:")
    export_all_tables()

    print("\n12. Export joined employees-departments data:")
    export_employees_with_departments()

    print("\n13. Export department summaries:")
    export_department_summaries()