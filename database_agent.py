import json


class DatabaseAgent:

    def __init__(self):
        self.connection = None

    def connect_mysql(
        self,
        host,
        user,
        password,
        database
    ):

        import mysql.connector

        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        return self.connection.is_connected()

    def connect_sqlserver(
        self,
        server,
        database,
        username,
        password
    ):

        import pyodbc

        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )

        self.connection = pyodbc.connect(
            connection_string
        )

        return True

    def execute_query(
        self,
        query
    ):

        if not self.connection:

            raise Exception(
                "Database connection not established."
            )

        cursor = self.connection.cursor()

        cursor.execute(query)

        columns = [
            column[0]
            for column in cursor.description
        ]

        rows = cursor.fetchall()

        results = []

        for row in rows:

            results.append(
                dict(
                    zip(
                        columns,
                        row
                    )
                )
            )

        cursor.close()

        return results

    def validate_record(
        self,
        query,
        expected_values
    ):

        records = self.execute_query(
            query
        )

        if not records:

            return {
                "status": "FAILED",
                "message": "No records found."
            }

        actual = records[0]

        mismatches = {}

        for key, value in expected_values.items():

            if str(actual.get(key)) != str(value):

                mismatches[key] = {
                    "expected": value,
                    "actual": actual.get(key)
                }

        if mismatches:

            return {
                "status": "FAILED",
                "mismatches": mismatches
            }

        return {
            "status": "PASSED",
            "record": actual
        }

    def close_connection(self):

        if self.connection:

            self.connection.close()

            self.connection = None