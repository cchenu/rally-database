"""Container for `PostgreSQL` class to interact with a PostgreSQL database."""

from abc import ABC, abstractmethod
from typing import Any, Literal

import psycopg


class SQLInterface(ABC):
    """Interface for SQL communcation."""

    @abstractmethod
    def execute(
        self, query: str, params: list[Any] | None = None
    ) -> list[Any]:
        """
        Execute a SQL query.

        Parameters
        ----------
        query : str
            SQL query to execute.
        params : list[Any], optional
            Values to substitute into the query, by default None.

        Returns
        -------
        list[Any]
            Query result. If the query is a SELECT statement, it returns the
            fetched rows. For other queries, it returns an empty list.
        """
        raise NotImplementedError

    @abstractmethod
    def read(
        self,
        table: str,
        columns: str | list[str] | None = None,
        condition_data: dict[str, Any] | None = None,
        number_values: int | None = None,
        return_type: Literal["list", "dict", "list[dict]"] = "list[dict]",
    ) -> list[dict[str, Any]] | dict[str, list[Any]] | list[tuple[Any] | Any]:
        """
        Read data from the database.

        The query's shape is (each condition is separated by a AND):
        SELECT columns FROM table
        WHERE condition_data.keys()=condition_data.values()
        LIMIT number_values;

        Parameters
        ----------
        table : str
            Table name.
        columns : str | list[str], optional
            List of column names to select or just one column name. By default
            None, which selects all columns.
        condition_data : dict[str, Any], optional
            Dictionary with conditions that lines must meet to be read. By
            default None.
        number_values : int, optional
            Maximum number of rows to return, by default None, which selects
            all rows.
        return_type : Literal["list", "dict", "list[dict], optional
            Format of the returned data, by default "list[dict]".

        Returns
        -------
        list[dict[str, Any] | tuple[Any] | Any] | dict[str, list[Any]]
            Queried data in the specified format. If return_type is
            "list[dict]" it returns a list of dict, where each dict is a line,
            with columns as keys. If return_type is "list", it returns a list
            of lists with data in same order as columns. If return_type is
            "dict",  it returns a dictionary with column names as keys and
            lists of values as values.
        """
        raise NotImplementedError

    @abstractmethod
    def write(
        self, table: str, data: list[dict[str, Any]] | dict[str, Any]
    ) -> None:
        """
        Write new lines to the specified table.

        The query's shape is:
        INSERT INTO table (data[0].keys())
        VALUES (data[0].values()), (data[1].values());

        Parameters
        ----------
        table : str
            Table name.
        data : list[dict[str, Any]] | dict[str, Any]
            List of lines to write. For each dict, keys are column names and
            values are values to write. If data is a dict, it writes a single
            line.

        Raises
        ------
        ValueError
            If all dictionaries do not have the same keys.
        """
        raise NotImplementedError

    @abstractmethod
    def update(
        self,
        table: str,
        update_data: dict[str, Any],
        condition_data: dict[str, Any] | None = None,
    ) -> None:
        """
        Update rows in a table.

        The query's shape is:
        UPDATE table SET update_data.keys()=update_data.values() WHERE
        condition_data.keys()=condition_data.values();

        Parameters
        ----------
        table : str
            Table name.
        update_data : dict[str, Any]
            New data.
        condition_data : dict[str, Any], optional
            Data to filter updated rows, by default None.
        """
        raise NotImplementedError

    @abstractmethod
    def create_table(
        self,
        table_name: str,
        columns_names: list[str],
        columns_type: list[str],
    ) -> None:
        """
        Create a new table.

        Not implemented, inputs can be changed.
        """
        raise NotImplementedError

    @abstractmethod
    def delete_rows(self, table: str, condition_data: dict[str, Any]) -> None:
        """
        Delete rows of a given table based on specified conditions.

        To delete all rows, use `delete_all` method.

        Parameters
        ----------
        table : str
            Table name.
        condition_data : dict[str, Any]
            Conditions to filter rows to delete.
        """
        raise NotImplementedError

    def delete_all(self, table: str) -> None:
        """
        Delete all rows of a given table.

        To select only specific rows, use `delete_rows` method.

        Parameters
        ----------
        table : str
            Table name.
        """
        raise NotImplementedError

    def __del__(self) -> None:
        """Ensure the connection is closed when the object is deleted."""
        raise NotImplementedError


class PostgreSQL(SQLInterface):
    """
    Class to read and write data from and to a PostgreSQL database.

    Attributes
    ----------
    hostname : str
        Hostname of the database server.
    db_name : str
        Name of the database.
    username : str
        Username to connect to the database.
    password : str
        Password to connect to the database.
    port : int
        Port number of the database server.
    conn : psycopg2.extensions.connection
        Connection object to the database.
    cursor : psycopg2.extensions.cursor
        Cursor object to execute SQL queries.
    """

    def __init__(
        self,
        hostname: str,
        db_name: str,
        username: str,
        password: str,
        port: int,
    ) -> None:
        self.hostname = hostname
        self.db_name = db_name
        self.username = username
        self.password = password
        self.port = port

        self.conn = psycopg.connect(
            host=self.hostname,
            dbname=self.db_name,
            user=self.username,
            password=self.password,
            port=self.port,
        )

        self.cursor = self.conn.cursor()

    def execute(  # noqa: D102
        self, query: str, params: list[Any] | None = None
    ) -> list[Any]:
        try:
            self.cursor.execute(query, params)
            if query.lower().startswith("select"):
                return list(self.cursor.fetchall())
            self.conn.commit()
        except:
            self.conn.rollback()
            raise
        return []

    def read(  # noqa: D102
        self,
        table: str,
        columns: str | list[str] | None = None,
        condition_data: dict[str, Any] | None = None,
        number_values: int | None = None,
        return_type: Literal["list", "dict", "list[dict]"] = "list[dict]",
    ) -> list[dict[str, Any]] | dict[str, list[Any]] | list[tuple[Any] | Any]:
        if columns is None:
            columns_str = "*"
        elif isinstance(columns, list):
            columns_str = ", ".join(columns)
        else:
            columns_str = columns

        query = f"SELECT {columns_str} FROM {table}"

        parameters: list[Any] = []
        if condition_data:
            query += " WHERE"
            condition_columns, parameters = (
                list(condition_data.keys()),
                list(condition_data.values()),
            )

            query += " AND ".join(
                f"{column}=%s" for column in condition_columns
            )

        if number_values is not None:
            query += f" LIMIT {number_values}"

        query += ";"

        data = self.execute(query, parameters)

        if return_type == "list":
            if columns is not None and (
                isinstance(columns, str) or len(columns) == 1
            ):
                return [row[0] for row in data]
            return data

        columns_list = [desc[0] for desc in self.cursor.description or []]

        if return_type == "list[dict]":
            data_list: list[dict[str, Any]] = []
            for row in data:
                data_dict: dict[str, Any] = dict(
                    zip(columns_list, row, strict=True)
                )
                data_list.append(data_dict)
            return data_list

        data_dict = {}

        for idx, key in enumerate(columns_list):
            data_dict[key] = [row[idx] for row in data]

        return data_dict

    def write(  # noqa: D102
        self, table: str, data: list[dict[str, Any]] | dict[str, Any]
    ) -> None:
        if isinstance(data, dict):
            data = [data]

        query_empty = f"INSERT INTO {table}"

        columns = data[0].keys()
        if any(d.keys() != columns for d in data):
            msg = "All dictionaries must have the same keys."
            raise ValueError(msg)

        columns_str = ", ".join(columns)
        query_empty += f" ({columns_str})"

        # We add max 10 000 items by request
        max_insert = 10000
        for idx in range(0, len(data), max_insert):
            data_request = data[idx : idx + max_insert]

            line_place = ", ".join(["%s"] * len(columns))
            values_place = ", ".join([f"({line_place})"] * len(data_request))
            query = query_empty + f" VALUES {values_place};"

            items = [
                value for values in data_request for value in values.values()
            ]
            self.execute(query, items)

    def update(  # noqa: D102
        self,
        table: str,
        update_data: dict[str, Any],
        condition_data: dict[str, Any] | None = None,
    ) -> None:
        params_execute = list(update_data.values())
        query = f"UPDATE {table} SET"

        query += ", ".join(f"{key}=%s" for key in update_data)

        if condition_data:
            query += " WHERE"

            columns = list(condition_data.keys())
            query += " AND ".join(f"{column}=%s" for column in columns)

            params_execute += list(condition_data.values())

        self.execute(query, params_execute)

    def create_table(  # noqa: D102
        self,
        table_name: str,
        columns_names: list[str],
        columns_type: list[str],
    ) -> None:
        pass

    def delete_rows(  # noqa: D102
        self, table: str, condition_data: dict[str, Any]
    ) -> None:
        query = f"DELETE FROM {table}"

        query += " WHERE"

        columns = list(condition_data.keys())
        query += " AND ".join(f"{column}=%s" for column in columns)

        query += ";"

        self.execute(query, list(condition_data.values()))

    def delete_all(self, table: str) -> None:  # noqa: D102
        self.execute(f"DELETE FROM {table};")

    def __del__(self) -> None:  # noqa: D105
        if hasattr(self, "conn"):
            self.conn.close()
