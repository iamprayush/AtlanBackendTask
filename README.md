# Atlan Backend Task

## Problem Statement

**Atlan Collect** has a variety of long-running tasks that require time and resources on the servers. As it stands now, once we have triggered off a long-running task, there is no way to tap into it and pause/stop/terminate the task, upon realizing that an erroneous request went through from one of the clients (mostly web or pipeline).

### API Endpoints
- `POST /start/upload`
  - Starts a new file upload.
  - Parameters:
    - `file_path - string` Path of the file to upload
- `POST /stop`
  - Stops the job. (Does not terminate it, though)
  - Parameters:
    - `job_id - string` ID of the job to be stopped
- `POST /resume`
  - Resumes the job from where it was paused. (The job must be in a stopped state)
  - Parameters:
    - `job_id - string` ID of the job to be stopped
- `POST /terminate`
  - Terminates the job.
  - Parameters:
    - `job_id - string` ID of the job to be stopped
- `GET /list`
  - Lists all jobs.

### Tech stack used
- [Flask](!https://flask.palletsprojects.com/en/1.1.x/) (Python framework for creating the API endpoints)
- [python-rq](!https://python-rq.org/) (Python library for queueing jobs and processing them in the background with workers.)
- [Redis](!https://redis.io/) (Task Broker)

### Approach

Each new task is enqueued in the queue and only a single task runs at a time.
Each task has a status parameter that can take one of the following values:
  - **enqueued**: Waiting in the queue.
  - **running**: In progress.
  - **stopped**: Temporarily stopped via user query, but can be resumed.
  - **terminated**: Permanently stopped via user query, and cannot be resumed.
  - **finished**: 100% progress.

Each task also has a progress parameter that shows % completed and gets updated in real time.

### Files description

- `dummy_data/*`: 3 CSV Files with dummy data.
- `app.py`: Main file containing all API Endpoint handlers.
- `constants.py`: Constants file containing named strings and delay values.
- `utilities.py`: File containing helper functions.

### Dummy Data Structure

Dummy data CSVs contain the following attributes (created using [Faker](!https://github.com/joke2k/faker)):
- Name
- Email
- Favorite Color
- Phone number
- Country

There are 3 files:
- Large (100,000 records)
- Medium (10,000 records)
- Small (1,000 records)
