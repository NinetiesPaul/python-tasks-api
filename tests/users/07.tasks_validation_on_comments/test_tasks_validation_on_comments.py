import pytest
import requests
import MySQLdb
from dotenv import dotenv_values

class TestTasksValidationsOnComments:
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
        TestTasksValidationsOnComments.tokenBearer = responseJson['token']
        
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task description",
            "type": "feature"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        responseJson = response.json()["data"]
        TestTasksValidationsOnComments.taskId = responseJson['id']

    def test_missing_fields(self, ):
        url = "http://localhost:5000/api/task/comment/" + str(TestTasksValidationsOnComments.taskId)
        new_task = {}
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_TEXT" in responseJson

    def test_invalid_fieds(self):
        url = "http://localhost:5000/api/task/comment/" + str(TestTasksValidationsOnComments.taskId)
        new_task = {
            "text": 99
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TEXT_NOT_STRING" in responseJson

    def test_invalid_empty_fields(self):
        url = "http://localhost:5000/api/task/comment/" + str(TestTasksValidationsOnComments.taskId)
        new_task = {"text": ""}
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "EMPTY_TEXT" in responseJson
        
    def test_task_not_found(self):
        url = "http://localhost:5000/api/task/comment/999"
        new_task = {
            "text": "This is a comment text"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_NOT_FOUND" in responseJson

    def test_comment_not_found(self):
        url = "http://localhost:5000/api/task/comment/999"
        new_task = {
            "text": "This is a comment text"
        }
        response = requests.delete(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "COMMENT_NOT_FOUND" in responseJson