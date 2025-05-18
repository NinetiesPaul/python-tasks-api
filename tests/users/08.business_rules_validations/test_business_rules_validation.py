import pytest
import requests
from dotenv import dotenv_values

"""
This test will perform a number of tests to validate the numerous validation
scenarios for business rules of the application that deals with how certain
routines should and if they even could be performed
"""
class TestBusinessRulesValidation:
    tokenBearer = ""
    taskId = 1
    userId = 1
    
    @pytest.fixture()
    def authenticate(self):
        url = "http://localhost:5000/register"
        new_user = {"name": "New Pytest", "email": "new_user@test", "password": "123456"}
        response = requests.post(url, json=new_user)
        
        responseJson = response.json()["data"]
        TestBusinessRulesValidation.userId = responseJson['id']
        
        url = "http://localhost:5000/login"
        credentials = {
            "username": "new_user@test",
            "password": "123456"
        }
        response = requests.post(url, json=credentials)
        responseJson = response.json()
        TestBusinessRulesValidation.tokenBearer = responseJson['token']
        
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task for business rules validation tests",
            "type": "feature"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestBusinessRulesValidation.tokenBearer})
        responseJson = response.json()["data"]
        TestBusinessRulesValidation.taskId = responseJson['id']
        
        url = "http://localhost:5000/api/task/assign/" + str(TestBusinessRulesValidation.taskId)
        payload = {
            "assigned_to": TestBusinessRulesValidation.userId
        }
        response = requests.post(url, headers={"Authorization": "Bearer " + TestBusinessRulesValidation.tokenBearer}, json=payload)

    def test_reassign_to_user_fails(self, authenticate):
        url = "http://localhost:5000/api/task/assign/" + str(TestBusinessRulesValidation.taskId)
        payload = {
            "assigned_to": TestBusinessRulesValidation.userId
        }
        response = requests.post(url, json=payload, headers={"Authorization": "Bearer " + TestBusinessRulesValidation.tokenBearer})
        assert response.status_code == 202
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "USER_ALREADY_ASSIGNED" in responseJson

    def test_update_to_closed_fails(self):
        url = "http://localhost:5000/api/task/update/" + str(TestBusinessRulesValidation.taskId)
        update = {
            "status": "closed"
        }
        response = requests.put(url, headers={"Authorization": "Bearer " + TestBusinessRulesValidation.tokenBearer}, json=update)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "CAN_NOT_UPDATE_TO_CLOSE" in responseJson

    def test_close_task_already_closed_fails(self):
        url = "http://localhost:5000/api/task/close/" + str(TestBusinessRulesValidation.taskId)
        requests.put(url, headers={"Authorization": "Bearer " + TestBusinessRulesValidation.tokenBearer})
        
        response = requests.put(url, headers={"Authorization": "Bearer " + TestBusinessRulesValidation.tokenBearer})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_ALREADY_CLOSED" in responseJson

    def test_update_closed_task_fails(self):
        url = "http://localhost:5000/api/task/update/" + str(TestBusinessRulesValidation.taskId)
        update = {
            "status": "in_qa"
        }
        response = requests.put(url, headers={"Authorization": "Bearer " + TestBusinessRulesValidation.tokenBearer}, json=update)
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["message"]
        assert isinstance(responseJson, list)
        assert "TASK_CLOSED" in responseJson