import pytest
import requests
from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.sql import text

"""
This test is responsible to register 2 users on the application and to test the GET /users/list request
"""
class TestSetUp:
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

    def test_register_user(self, cleanup):
        url = "http://localhost:5000/register"
        new_user = {"name": "Pytest", "email": "user@test", "password": "123456"}
        response = requests.post(url, json=new_user)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        assert isinstance(responseJson, object)
        assert isinstance(responseJson['id'], int)
        assert responseJson['name'] == "Pytest"
        assert responseJson['email'] == "user@test"
        
        url = "http://localhost:5000/register"
        new_user = {"name": "Pytest Second", "email": "userPytest@test", "password": "123456"}
        response = requests.post(url, json=new_user)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        assert isinstance(responseJson, object)
        assert isinstance(responseJson['id'], int)
        assert responseJson['name'] == "Pytest Second"
        assert responseJson['email'] == "userPytest@test"
    
    def test_list_all_users(self):
        url = "http://localhost:5000/api/users/list"
        response = requests.get(url)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        users = responseJson["users"]
        total = responseJson["total"]
        assert isinstance(total, int)
        assert total == 2
        assert isinstance(users[0], object)
        assert isinstance(users[1], object)