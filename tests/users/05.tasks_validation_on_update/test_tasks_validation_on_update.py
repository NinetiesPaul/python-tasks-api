import pytest
import requests
import MySQLdb
from dotenv import dotenv_values

class TestTasksValidationsOnUpdate:
    tokenBearer = ""
    taskId = 1
    
    @pytest.fixture()
    def cleanup(self):
        env_var = dotenv_values(".env")

        mydb = MySQLdb.connect(
            host=env_var['DB_TEST_HOST'],
            user=env_var['DB_TEST_USER'],
            password=env_var['DB_TEST_PASSWORD'],
            database=env_var['DB_TEST_DBNAME']
        )

        mycursor = mydb.cursor()

        mycursor.execute("""
            SET FOREIGN_KEY_CHECKS = 0;

            TRUNCATE users;
            TRUNCATE tasks;
            TRUNCATE task_assignees;
            TRUNCATE task_comment;
            TRUNCATE task_history;

            SET FOREIGN_KEY_CHECKS = 1;
        """) 
    
    def test_log_user_and_create_task(self, cleanup):
        url = "http://localhost:5000/register"
        new_user = {"name": "Pytest", "email": "user@test", "password": "123456"}
        requests.post(url, json=new_user)
        
        url = "http://localhost:5000/login"
        credentials = {
            "username": "user@test",
            "password": "123456"
        }
        response = requests.post(url, json=credentials)
        responseJson = response.json()
        TestTasksValidationsOnUpdate.tokenBearer = responseJson['token']
        
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task description",
            "type": "feature"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnUpdate.tokenBearer})
        responseJson = response.json()["data"]
        TestTasksValidationsOnUpdate.taskId = responseJson['id']

    def test_empty_fields(self):
        url = "http://localhost:5000/api/task/update/" + str(TestTasksValidationsOnUpdate.taskId)
        new_task = {
            "title": "",
            "description": "",
            "type": "",
            "status": ""
        }

        response = requests.put(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnUpdate.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "EMPTY_TITLE" in responseJson
        assert "EMPTY_DESCRIPTION" in responseJson
        assert "EMPTY_TYPE" in responseJson
        assert "EMPTY_STATUS" in responseJson

    def test_invalid_fieds(self):
        url = "http://localhost:5000/api/task/update/" + str(TestTasksValidationsOnUpdate.taskId)
        new_task = {
            "title": 0,
            "description": 0,
            "type": 0,
            "status": 0
        }
        response = requests.put(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnUpdate.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TITLE_NOT_STRING" in responseJson
        assert "DESCRIPTION_NOT_STRING" in responseJson
        assert "TYPE_NOT_STRING" in responseJson
        assert "INVALID_TYPE" in responseJson

    def test_invalid_fieds(self):
        url = "http://localhost:5000/api/task/update/999"
        new_task = {
            "title": "new title for error test"
        }
        response = requests.put(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnUpdate.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_NOT_FOUND" in responseJson