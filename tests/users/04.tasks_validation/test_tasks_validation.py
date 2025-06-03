import pytest
import requests
from dotenv import dotenv_values

from app.app import app
"""
This test will perform a number of tests to validate the numerous validation
scenarios for task creation, focusing on requests with bad data integrity
and values and their output
"""

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestTasksValidations:
    tokenBearer = ""

    @pytest.fixture()
    def authenticate(self, client):
        url = "http://localhost:5000/login"
        credentials = {
            "username": "user@test",
            "password": "123456"
        }
        response = client.post(url, json=credentials)
        
        responseJson = response.get_json()
        TestTasksValidations.tokenBearer = responseJson['token']
        
    def test_missing_fields(self, authenticate, client):
        url = "http://localhost:5000/api/task/create"
        new_task = {}
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidations.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_TITLE" in responseJson
        assert "MISSING_DESCRIPTION" in responseJson
        assert "MISSING_TYPE" in responseJson
        
    def test_invalid_type_fields(self, client):
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": 99,
            "description": 99,
            "type": 99
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidations.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "TITLE_NOT_STRING" in responseJson
        assert "DESCRIPTION_NOT_STRING" in responseJson
        assert "TYPE_NOT_STRING" in responseJson
        assert "INVALID_TYPE" in responseJson
        
    def test_invalid_empty_fields(self, client):
        url = "http://localhost:5000/api/task/create"
        new_task = {"title": "", "description": "", "type": ""}
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidations.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "EMPTY_TITLE" in responseJson
        assert "EMPTY_DESCRIPTION" in responseJson
        assert "EMPTY_TYPE" in responseJson
        
    def test_invalid_empty_fields(self, client):
        url = "http://localhost:5000/api/task/view/999999"
        response = client.get(url, headers={"Authorization": "Bearer " + TestTasksValidations.tokenBearer})
        assert response.status_code == 404
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_NOT_FOUND" in responseJson