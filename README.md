# Atlan Backend Task

## Problem Statement

**Atlan Collect** has a variety of long-running tasks that require time and resources on the servers. As it stands now, once we have triggered off a long-running task, there is no way to tap into it and pause/stop/terminate the task, upon realizing that an erroneous request went through from one of the clients (mostly web or pipeline).

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
