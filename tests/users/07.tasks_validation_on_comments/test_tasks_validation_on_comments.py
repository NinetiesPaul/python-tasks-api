import pytest
import requests
from dotenv import dotenv_values

from app.app import app
"""
This test will perform a number of tests to validate the numerous validation
scenarios for task comments, focusing on requests with bad data integrity
and values and their output
"""

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTasksValidationsOnComments:
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
        TestTasksValidationsOnComments.tokenBearer = responseJson['token']
        
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task for comment validation tests",
            "type": "feature"
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        responseJson = response.get_json()["data"]
        TestTasksValidationsOnComments.taskId = responseJson['id']

    def test_missing_fields(self, authenticate, client):
        url = "http://localhost:5000/api/task/comment/" + str(TestTasksValidationsOnComments.taskId)
        new_task = {}
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_TEXT" in responseJson

    def test_invalid_fieds(self, client):
        url = "http://localhost:5000/api/task/comment/" + str(TestTasksValidationsOnComments.taskId)
        new_task = {
            "text": 99
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "TEXT_NOT_STRING" in responseJson

    def test_invalid_empty_fields(self, client):
        url = "http://localhost:5000/api/task/comment/" + str(TestTasksValidationsOnComments.taskId)
        new_task = {"text": ""}
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "EMPTY_TEXT" in responseJson
        
    def test_task_not_found(self, client):
        url = "http://localhost:5000/api/task/comment/999"
        new_task = {
            "text": "This is a comment text"
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_NOT_FOUND" in responseJson

    def test_comment_not_found(self, client):
        url = "http://localhost:5000/api/task/comment/999"
        new_task = {
            "text": "This is a comment text"
        }
        response = client.delete(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidationsOnComments.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"

        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "COMMENT_NOT_FOUND" in responseJson