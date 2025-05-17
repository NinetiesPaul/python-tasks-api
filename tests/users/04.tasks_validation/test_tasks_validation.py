import pytest
import requests
import MySQLdb
from dotenv import dotenv_values

"""
This test will perform a number of tests to validate the numerous validation
scenarios for task creation, focusing on requests with bad data integrity
and values and their output
"""
class TestTasksValidations:
    tokenBearer = ""

    @pytest.fixture()
    def authenticate(self):
        url = "http://localhost:5000/login"
        credentials = {
            "username": "user@test",
            "password": "123456"
        }
        response = requests.post(url, json=credentials)
        
        responseJson = response.json()
        TestTasksValidations.tokenBearer = responseJson['token']
        
    def test_missing_fields(self, authenticate):
        url = "http://localhost:5000/api/task/create"
        new_task = {}
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidations.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_TITLE" in responseJson
        assert "MISSING_DESCRIPTION" in responseJson
        assert "MISSING_TYPE" in responseJson
        
    def test_invalid_type_fields(self):
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": 99,
            "description": 99,
            "type": 99
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidations.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TITLE_NOT_STRING" in responseJson
        assert "DESCRIPTION_NOT_STRING" in responseJson
        assert "TYPE_NOT_STRING" in responseJson
        assert "INVALID_TYPE" in responseJson
        
    def test_invalid_empty_fields(self):
        url = "http://localhost:5000/api/task/create"
        new_task = {"title": "", "description": "", "type": ""}
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestTasksValidations.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "EMPTY_TITLE" in responseJson
        assert "EMPTY_DESCRIPTION" in responseJson
        assert "EMPTY_TYPE" in responseJson