import pytest
import requests
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.sql import text

"""
This test will perform a number of tests to validate the numerous validation
scenarios for user registration, focusing on requests with bad data integrity
and values and their output
"""
class TestUserValidations:
    @pytest.fixture()
    def cleanup(self):
        env_var = dotenv_values(".env")
        
        engine = create_engine(env_var['DB_URL_TESTING'])
        with engine.begin() as connection:
            connection.execute(text('DELETE FROM task_history;'))
            connection.execute(text('DELETE FROM task_comment;'))
            connection.execute(text('DELETE FROM task_assignees;'))
            connection.execute(text('DELETE FROM tasks;'))
            connection.execute(text('DELETE FROM users;'))

    def test_missing_fields(self, cleanup):
        url = "http://localhost:5000/register"
        new_user = {"namee": "", "emaill": "", "passwordd": ""}
        response = requests.post(url, json=new_user)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_NAME" in responseJson
        assert "MISSING_EMAIL" in responseJson
        assert "MISSING_PASSWORD" in responseJson
        
    def test_invalid_type_fields(self):
        url = "http://localhost:5000/register"
        new_user = {"name": 99, "email": 99, "password": "password"}
        response = requests.post(url, json=new_user)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "NAME_NOT_STRING" in responseJson
        assert "EMAIL_NOT_STRING" in responseJson
        
    def test_invalid_empty_fields(self):
        url = "http://localhost:5000/register"
        new_user = {"name": "", "email": "", "password": ""}
        response = requests.post(url, json=new_user)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "EMPTY_NAME" in responseJson
        assert "EMPTY_EMAIL" in responseJson
        assert "EMPTY_PASSWORD" in responseJson
        
    def test_invalid_email(self):
        url = "http://localhost:5000/register"
        new_user = {"name": "John Doe", "email": "j.doemail.com", "password": "password"}
        response = requests.post(url, json=new_user)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "INVALID_EMAIL" in responseJson
        
    def test_email_taken(self):
        url = "http://localhost:5000/register"
        new_user = {"name": "Pytest", "email": "user@test", "password": "123456"}
        response = requests.post(url, json=new_user)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        url = "http://localhost:5000/register"
        new_user = {"name": "Pytest", "email": "user@test", "password": "123456"}
        response = requests.post(url, json=new_user)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "EMAIL_ALREADY_TAKEN" in responseJson