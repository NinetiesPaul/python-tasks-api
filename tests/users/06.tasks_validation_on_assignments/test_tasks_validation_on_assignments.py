import pytest
import requests
import MySQLdb
from dotenv import dotenv_values

class TestTasksValidationsOnAssignments:
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
        TestTasksValidationsOnAssignments.tokenBearer = responseJson['token']
        
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task description",
            "type": "feature"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        responseJson = response.json()["data"]
        TestTasksValidationsOnAssignments.taskId = responseJson['id']

    def test_missing_fields(self, ):
        url = "http://localhost:5000/api/task/assign/" + str(TestTasksValidationsOnAssignments.taskId)
        new_task = {}
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_ASSIGNED_TO" in responseJson

    def test_invalid_fieds(self):
        url = "http://localhost:5000/api/task/assign/" + str(TestTasksValidationsOnAssignments.taskId)
        new_task = {
            "assigned_to": "a"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "ASSIGNED_TO_NOT_INTEGER" in responseJson

    def test_task_not_found(self):
        url = "http://localhost:5000/api/task/assign/999"
        new_task = {
            "assigned_to": 1
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_NOT_FOUND" in responseJson

    def test_user_not_found(self):
        url = "http://localhost:5000/api/task/assign/" + str(TestTasksValidationsOnAssignments.taskId)
        new_task = {
            "assigned_to": 99
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "USER_NOT_FOUND" in responseJson

    def test_assignment_not_found(self):
        url = "http://localhost:5000/api/task/unassign/999"
        response = requests.delete(url, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "ASSIGNMENT_NOT_FOUND" in responseJson