## Tasks API in Python's Flask
A simple API using Python's Flask. It has some basic functions, like:

- User registration and authentication using JWT
- Perform CRUD operations of Tasks
- Some basics business rules enforced

My main goal is to showcase some concepts, such as:

- Migrations and model relationship
- Authentication configuration
- Routes definitions
- SOLID and KISS principles on a MVC architecture

The main tech behind it is Python's Flask framework, to showcase it's cleanliness and simplicity while maintaning a robust architecture. I'm also using some others libraries. For storaging, i'm using relational databases

## Environment setup
To run this application you must have installed on your environment:

* `Python` - For the main application (Ideally >= 3.1)
* `MySQL` (5.7 or greater) or `PostgreSQL` (15 or greater) - For storaging and accessing data

## Installation and Configuration
Once all required software is up and running, execute the following commands:

```
python -m venv venv
```
```
source venv/Scripts/activate
```
```
pip install -r requirements.txt
```
If no error is thrown, the basic environment is installed. Now you must generate the database and table, but before that you must have MySQL Server running and receiving connections. Once you make sure of that, run the following:
```
cp .env.example .env
```
Open the newly created .env file and on the ```DB_URL``` parameter replace the keywords on the {}'s for your database connection information.

Having done that, just save the file then go back to the prompt and run the following:
```
flask shell
```
```
from app import database
```
```
from models import *
```
```
database.create_all()
```
```
exit()
```
If there's no big red error messages screaming at you, then you are good to go. All you have to do now is run:
```
flask run
```
And you're ready to use the API!

## Tests
Before running the integration tests to validate the application's features, you must migrate the databases dedicated to tests. This depends on your `.env` configuration, if the ENVIRONMENT value isn't set the app will assume you're running in dev/prod enviroment. But if you need to run tests, set the `ENVIRONMENT` to `testing` and configure `DB_URL_TESTING` accordingly.

## Usage
### __Users__
#### User creation
```
curl --location 'http://localhost:5000/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "T. Soprano",
    "email": "t.soprano@mail.com",
    "password": "123456"
}'
```
#### User authentication
```
curl --location 'http://localhost:5000/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "t.soprano@mail.com",
    "password": "123456"
}'
```
### __Tasks__
The User Authetication endpoint will authenticate the user, and retrieve an authorization token to be used on all the tasks related requests. Copy it and place it on all ```{token}``` keyword on the following requests
#### Creating a new Task
```
curl --location 'http://localhost:5000/api/task/create' \
--header 'Authorization: Bearer {token}' \
--header 'Content-Type: application/json' \
--data '{
    "title": "This is a title",
    "description": "Here is a description",
    "type": "hotfix"
}'
```

#### Selecting a single Task
```
curl --location 'http://localhost:5000/api/task/view/{taskId}' \
--header 'Authorization: Bearer {token}'
```

#### Listing all Tasks
Replace ```{created_by}``` with a User Id  
Replace ```{status}``` with any of the following: new, in_qa, in_dev, blocked, closed  
Replace ```{type}``` with any of the following: feature, bugfix, hotfix  
```
curl --location 'http://localhost:5000/api/task/list?type={type}&status={status}' \
--header 'Authorization: Bearer {token}'
```

#### Updating a Task
```
curl --location --request PUT 'http://localhost:5000/api/task/update/{taskId}' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {token}' \
--data '{
    "status": "in_qa"
}'
```

#### Deleting a Task
```
curl --location --request DELETE 'http://localhost:5000/api/task/delete/{taskId}' \
--header 'Authorization: Bearer {token}'
```

#### Closing a Task
```
curl --location --request PUT 'http://localhost:5000/api/task/close/{taskId}' \
--header 'Authorization: Bearer {token}'
```
