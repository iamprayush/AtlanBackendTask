import csv
import constants
import os
import psycopg2
from rq.job import Job


def establish_connection():
    """Tries to establish a connection to the database using the config present in
    the constants file.

    Returns:
        A connection object or None if connection could not be established.
    """
    try:
        return psycopg2.connect(
            user=constants.USER_NAME,
            password=constants.PASSWORD,
            host=constants.HOST,
            dbname=constants.DATABASE_NAME,
            port=constants.PORT
        )
    except Exception as e:
        print('Could not establish a connection to the database. Error: %s' % e)


def create_table(table_name):
    """
    Creates a new table with the given table name and the following parameters:
    Name, Email, Favorite color, Phone number, Country

    Args:
        table_name - str: The name of the table.

    Returns:
        bool: Whether the table creation was successful or not.
    """
    connection = establish_connection()
    if not connection:
        return False

    successful = True
    cursor = connection.cursor()
    try:
        cursor.execute(
            '''CREATE TABLE {} (
                name TEXT NOT NULL PRIMARY KEY,
                email TEXT,
                fav_color TEXT,
                phone_number TEXT,
                country TEXT
            );'''.format(table_name))
        connection.commit()
    except Exception as e:
        print(e)
        successful = False

    cursor.close()
    connection.close()
    return successful


def validate_file_path(file_path):
    """Validates the given file path.

    Args:
        file_path - str: The path to be validated. 

    Returns:
        Tuple - (bool, str): (If the path is valid, If invalid,
        the error message to be displayed).
    """
    if not file_path:
        return False, 'Your request is missing/empty the "file_path" parameter.'
    if not isinstance(file_path, str):
        return False, 'The "job_id" parameter must be a string.'
    if not os.path.isfile(file_path):
        return False, 'Invalid file path: No such file exists.'
    if not file_path.lower().endswith('.csv'):
        return False, 'Invalid file path: File must be of type CSV.'
    return True, ''


def validate_job_id(job_id, redis_connection):
    """Validates the given job id.

    Args:
        job_id - str: The job id to be validated. 
        redis_connection: The redis connection in which the job id needs to be
            searched for.

    Returns:
        Tuple - (bool, str): (If the job id is valid, If invalid,
        the error message to be displayed).
    """
    if not job_id:
        return False, 'Your request is missing/empty the "job_id" parameter.'
    if not isinstance(job_id, str):
        return False, 'The "job_id" parameter must be a string.'
    try:
        Job.fetch(job_id, connection=redis_connection)
    except Exception:
        return False, 'Invalid job id: No such job exists.'

    return True, ''


def get_total_lines(file_path):
    """Gets the number of lines in the CSV file.

    Args:
        file_path - str: The path to the CSV file. 

    Returns:
        int: The number of lines in the CSV file.
    """
    no_of_lines = 0
    with open(file_path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        no_of_lines = len(list(reader))
    return no_of_lines


def get_lines_processed(progress, total_lines):
    """Gets the number of lines that have already been processed.
    NOTE: The progress will be the fraction of lines processed, in the simplest
    format, so we can't just take the numerator.

    Args:
        progress - Fraction: The fraction of lines that have already been processed.
        total_lines - int: The number of lines that need to be processed.

    Returns:
        int: The number of lines that have already been processed.
    """
    return progress.numerator * (total_lines // progress.denominator)
