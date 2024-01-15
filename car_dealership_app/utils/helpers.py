from django.db import connection

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def prepare_data(result):
    column_names = []
    if (len(result) != 0):
        column_names = [desc for desc in result[0].keys()]
    data = (column_names, result)
    return data


def fetchall_and_prepare(cursor):
    columns = [col[0] for col in cursor.description]
    return prepare_data([dict(zip(columns, row)) for row in cursor.fetchall()])


def get_marki_pojazdow(cursor):
    cursor.execute("SELECT marka FROM marka;")
    return fetchall_and_prepare(cursor)


def get_marka_id(cursor, marka):
    get_marka_query = "SELECT marka_id FROM marka WHERE marka = %s;"
    cursor.execute(get_marka_query, (marka,))
    result = cursor.fetchone()
    id = result[0]
    return id
