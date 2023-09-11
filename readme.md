## Tasks API in Python's Flask
A simple API using Python's Flask. It has some basic functions, like:

- User registration and authentication using JWT
- Perform CRUD operations of Tasks
- Some basics business rules enforced

My main goal is to showcase some of Symfony's features like:

- Migrations and model relationship
- Authentication configuration
- Routes definitions
- SOLID and KISS principles on a MVC architecture

The main tech behind it is Python's Flask framework, to showcase it's cleanliness and simplicity while maintaning a robust architecture. I'm also using some others libraries. For storaging, i'm using MySQL relational database

## Environment setup
To run this application you must have installed on your environment:

* `Python` - For the main application 
* `MySQL` - For storaging and accessing data

## Installation and Configuration
Once all required software is up and running, execute the following commands:

```
py -3 -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
If no error is thrown, the basic environment is installed. Now you must generate the database and table, but before that you must have MySQL Server running and receiving connections. Once you make sure of that, run the following:
```
cp .env.example .env
```
Open the newly created .env file and on the ```DB_URL``` parameter replace the keywords on the {}'s for your database connection information. Having done that, just save the file
then go back to the prompt and run the following:
```
flask shell
from app import mysql
from models import tasks, users
mysql.create_all()
exit()
```
If there's no big red error messages screaming at you, then you are good to go. All you have to do now is run:
```
flask run
```
And you're ready to use the API!

## Usage
Before managing Tasks, you must register some users:
#### __User registration__
```
curl --location 'http://localhost:5000/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "t.soprano@mail.com",
    "password": "123456"
}'
```
#### __User authentication__
```
curl --location 'http://localhost:5000/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "username": "t.soprano@mail.com",
    "password": "123456"
}'
```
That endpoint will log on and authenticate the user, and retrieve an authorization token to be used on all the tasks related requests. Copy it and place it on all ```{token}``` keyword on the following requests
#### __Task creation__
- Allowed types are: feature, bugfix, hotfix
```
curl --location 'http://localhost:5000/task' \
--header 'Authorization: Bearer {token}' \
--header 'Content-Type: application/json' \
--data '{
    "title": "This is a title",
    "description": "Here is a description",
    "type": "hotfix"
}'
```

#### __Task selection__
- You can use ```type``` and ```status``` as query parameters for filtering. If no parameters is passed, all tasks are retrieved
```
curl --location 'http://localhost:5000/tasks' \
--header 'Authorization: Bearer {token}'
```

#### __Task update__
- Replace ```{token_id}``` with a Token Id
- You can not close a task on this request. Use the ```PUT /close``` endpoint
- Allowed statuses are: open, closed, in_dev, blocked, in_qa
```
curl --location --request PUT 'http://localhost:5000/task/{token_id}' \
--header 'Authorization: Bearer {token}' \
--header 'Content-Type: application/json' \
--data '{
    "title": "a new title",
    "type": "bugfix",
    "status": "closed"
}'
```

#### __Task deletion__
- Replace ```{token_id}``` with a Token Id
```
curl --location --request DELETE 'http://localhost:5000/task/{token_id}' \
--header 'Authorization: Bearer {token}'
```

#### __Task closing__
- Replace ```{token_id}``` with a Token Id
```
curl --location --request PUT 'http://localhost:5000/task/{token_id}/close' \
--header 'Authorization: Bearer {token}'
```
