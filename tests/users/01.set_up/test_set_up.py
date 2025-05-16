import pytest
import requests
import MySQLdb
from dotenv import dotenv_values

class TestSetUp:
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
        
        #mydb.commit()

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