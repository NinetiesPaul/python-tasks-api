import pytest
import requests
from dotenv import dotenv_values

from app.app import app
"""
This test will perform a number of tests to validate the numerous validation
scenarios for task assignment, focusing on requests with bad data integrity
and values and their output
"""

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTasksValidationsOnAssignments:
    tokenBearer = ""
    taskId = 1
    
    @pytest.fixture()
    def authenticate(self, client):
        url = "http://localhost:5000/login"
        credentials = {
            "username": "user@test",
            "password": "123456"
        }
        response = client.post(url, json=credentials)
        responseJson = response.get_json()
        TestTasksValidationsOnAssignments.tokenBearer = responseJson['token']
        
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task for assignments validation tests",
            "type": "feature"
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        responseJson = response.get_json()["data"]
        TestTasksValidationsOnAssignments.taskId = responseJson['id']

    def test_missing_fields(self, authenticate, client):
        url = "http://localhost:5000/api/task/assign/" + str(TestTasksValidationsOnAssignments.taskId)
        new_task = {}
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_ASSIGNED_TO" in responseJson

    def test_invalid_fieds(self, client):
        url = "http://localhost:5000/api/task/assign/" + str(TestTasksValidationsOnAssignments.taskId)
        new_task = {
            "assigned_to": "a"
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "ASSIGNED_TO_NOT_INTEGER" in responseJson

    def test_task_not_found(self, client):
        url = "http://localhost:5000/api/task/assign/999"
        new_task = {
            "assigned_to": 1
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_NOT_FOUND" in responseJson

    def test_user_not_found(self, client):
        url = "http://localhost:5000/api/task/assign/" + str(TestTasksValidationsOnAssignments.taskId)
        new_task = {
            "assigned_to": 99
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "USER_NOT_FOUND" in responseJson

    def test_assignment_not_found(self, client):
        url = "http://localhost:5000/api/task/unassign/999"
        response = client.delete(url, headers={"Authorization": "Bearer " + TestTasksValidationsOnAssignments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "ASSIGNMENT_NOT_FOUND" in responseJson