import constants
from flask import Flask, request, jsonify
from fractions import Fraction
import psycopg2
from redis import Redis
from rq import Queue, get_current_job
from rq.job import Job
import time
import utilities

app = Flask(__name__)
redis_connection = Redis()
queue = Queue(connection=redis_connection)

job_ids = []


def upload():
    job = get_current_job()

    if job.meta['status'] in (
            constants.STATUS_TERMINATED,
            constants.STATUS_STOPPED,
            constants.STATUS_FINISHED):
        return

    # Update status.
    if job.meta['status'] == constants.STATUS_ENQUEUED:
        job.meta['status'] = constants.STATUS_RUNNING
        job.save_meta()

    print('Uploading...')
    total_lines = utilities.get_total_lines(job.meta['file_path'])
    lines_processed = utilities.get_lines_processed(
        job.meta['progress'], total_lines)

    for i in range(lines_processed, total_lines):
        job = Job.fetch(job.id, connection=redis_connection)
        if job.meta['status'] in (
                constants.STATUS_TERMINATED,
                constants.STATUS_STOPPED,
                constants.STATUS_FINISHED):
            return

        print(i)
        job.meta['progress'] += Fraction(1, total_lines)
        job.save_meta()
        time.sleep(1)

    print('Uploaded!')
    job.meta['status'] = constants.STATUS_FINISHED


@app.route('/start/upload', methods=['POST'])
def start_upload():
    file_path = request.get_json().get('file_path')

    # Validating the file path.
    is_valid, error_message = utilities.validate_file_path(file_path)
    if not is_valid:
        return app.make_response((error_message, 400))

    # Generating the next job id and creating a table for it.
    job_id = str(len(job_ids) + 1)
    table_name = 'TABLE_' + job_id
    # table_created = utilities.create_table(table_name)
    # if not table_created:
    #     return app.make_response(('Could not create new table.', 500))

    # Connecting to the database.
    connection = utilities.establish_connection()
    if connection is None:
        return app.make_response(('Could not establish a connection to the database.', 500))

    # Queuing the new job.
    job_metadata = {
        'file_path': file_path,
        'table_name': table_name,
        'progress': Fraction(0, utilities.get_total_lines(file_path)),
        'status': constants.STATUS_ENQUEUED
    }
    job_object = queue.enqueue(
        upload, job_id=job_id, meta=job_metadata,
        result_ttl=constants.RESULT_TTL, ttl=constants.TTL, job_timeout=constants.TIMEOUT)
    job_ids.append(job_id)

    return app.make_response(('Success!!', 200))


@app.route('/terminate', methods=['POST'])
def terminate():
    job_id = request.get_json().get('job_id')

    # Validating the job id.
    is_valid, error_message = utilities.validate_job_id(
        job_id, redis_connection)
    if not is_valid:
        return app.make_response((error_message, 400))

    job = Job.fetch(job_id, connection=redis_connection)
    if job.meta['status'] == constants.STATUS_TERMINATED:
        return app.make_response(('The job has already been terminated.', 400))
    if job.meta['status'] == constants.STATUS_FINISHED:
        return app.make_response(('The job has finished running.', 400))

    job.meta['status'] = constants.STATUS_TERMINATED
    job.save_meta()
    job.cancel()    # Removes it from the queue.

    # TODO: Drop the table from the database.

    return app.make_response(('Job was successfully terminated!', 200))


@app.route('/stop', methods=['POST'])
def stop():
    job_id = request.get_json().get('job_id')

    # Validating the job id.
    is_valid, error_message = utilities.validate_job_id(
        job_id, redis_connection)
    if not is_valid:
        return app.make_response((error_message, 400))

    job = Job.fetch(job_id, connection=redis_connection)
    if job.meta['status'] == constants.STATUS_STOPPED:
        return app.make_response(('The job has already been stopped.', 400))
    if job.meta['status'] == constants.STATUS_TERMINATED:
        return app.make_response(('The job has been terminated and thus cannot be stopped.', 400))
    if job.meta['status'] == constants.STATUS_FINISHED:
        return app.make_response(('The job has finished running.', 400))

    job.meta['status'] = constants.STATUS_STOPPED
    job.save_meta()
    job.cancel()    # Removes it from the queue.

    return app.make_response(('Job was successfully stopped!', 200))


@app.route('/resume', methods=['POST'])
def resume():
    job_id = request.get_json().get('job_id')

    # Validating the job id.
    is_valid, error_message = utilities.validate_job_id(
        job_id, redis_connection)
    if not is_valid:
        return app.make_response((error_message, 400))

    job = Job.fetch(job_id, connection=redis_connection)
    if job.meta['status'] == constants.STATUS_TERMINATED:
        return app.make_response(('The job has been terminated and thus cannot be resumed.', 400))
    if job.meta['status'] in (constants.STATUS_RUNNING, constants.STATUS_ENQUEUED):
        return app.make_response(('The job is already running/enqueued.', 400))
    if job.meta['status'] == constants.STATUS_FINISHED:
        return app.make_response(('The job has finished running.', 400))

    # Adding the job back in the queue.
    job.meta['status'] = constants.STATUS_ENQUEUED
    job.save_meta()
    queue.enqueue(
        upload, job_id=job.id, meta=job.meta,
        result_ttl=constants.RESULT_TTL, ttl=constants.TTL, job_timeout=constants.TIMEOUT)

    return app.make_response(('Job was successfully resumed!', 200))


@app.route('/list', methods=['GET'])
def list_jobs():
    jobs_data = {}
    for job_id in job_ids:
        job_meta = Job.fetch(job_id, connection=redis_connection).meta
        jobs_data[job_id] = job_meta
        jobs_data[job_id]['progress'] = str(
            round(float(jobs_data[job_id]['progress']) * 100, 2)) + '%'
    jobs_data['queue_len'] = len(queue)
    return jobs_data


if __name__ == '__main__':
    app.run(debug=constants.DEBUG_MODE)
