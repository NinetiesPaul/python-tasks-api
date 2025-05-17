import pytest
import requests
import MySQLdb
from dotenv import dotenv_values

"""
This test will perform a number of tests to validate the numerous validation
scenarios for task udpate, focusing on requests with bad data integrity
and values and their output
"""
class TestTasksValidationsOnUpdate:
    tokenBearer = ""
    taskId = 1
    
    @pytest.fixture()
    def authenticate(self):
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
            "description": "This is the task for task validations on update tests",
            "type": "feature"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnUpdate.tokenBearer})
        responseJson = response.json()["data"]
        TestTasksValidationsOnUpdate.taskId = responseJson['id']

    def test_empty_fields(self, authenticate):
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

    def test_task_not_found_no_update(self):
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

    def test_task_not_found_on_close(self):
        url = "http://localhost:5000/api/task/close/999"
        response = requests.put(url, headers={"Authorization": "Bearer " + TestTasksValidationsOnUpdate.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_NOT_FOUND" in responseJson