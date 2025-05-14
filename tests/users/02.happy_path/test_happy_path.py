import requests

class TestHappyPath:
    tokenBearer = ""
    taskId = 1
    
    def test_log_user(self):
        url = "http://localhost:5000/login"
        credentials = {
            "username": "user@test",
            "password": "123456"
        }
        response = requests.post(url, json=credentials)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()
        TestHappyPath.tokenBearer = responseJson['token']

    def test_create_task(self):
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task description",
            "type": "feature"
        }
        response = requests.post(url, json=new_task, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        assert isinstance(responseJson, object)
        
        TestHappyPath.taskId = responseJson['id']
        
        expectedKeys = [ "closed_by", "closed_on", "created_by", "created_on", "description", "id", "status", "title", "type" ]
        assert expectedKeys == list(responseJson.keys())
        assert responseJson['closed_by'] == None
        assert responseJson['closed_on'] == None
        assert isinstance(responseJson['created_by'], object)
        assert responseJson['created_by']['name'] == "Pytest"
        assert responseJson['status'] == "open"
    
    def test_list_all_tasks(self):
        url = "http://localhost:5000/api/task/list"
        response = requests.get(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        total = responseJson['total']
        length = len(responseJson['tasks'])
        assert total == length
        
        expectedKeys = [ "assignees", "closed_by", "closed_on", "created_by", "created_on", "description", "id", "status", "title", "type" ]
        assert expectedKeys == list(responseJson['tasks'][0].keys())
    
    def test_view_task(self):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = requests.get(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()['data']
        
        expectedKeys = [ "assignees", "closed_by", "closed_on", "comments", "created_by", "created_on", "description", "history", "id", "status", "title", "type" ]
        assert expectedKeys == list(responseJson.keys())
    
    def test_update_task(self):
        url = "http://localhost:5000/api/task/update/" + str(TestHappyPath.taskId)
        update = {
            "type": "hotfix",
            "status": "in_qa"
        }
        response = requests.put(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer}, json=update)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        assert isinstance(responseJson, object)
        
        assert responseJson['type'] == "hotfix"
        assert responseJson['status'] == "in_qa"

    def test_history_updated(self):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = requests.get(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()['data']
        assert isinstance(responseJson, object)
        assert isinstance(responseJson['history'][0]['changed_by'], object)
        assert responseJson['history'][0]['changed_by']['name'] == "Pytest"
        assert responseJson['history'][0]['field'] == "type"
        assert responseJson['history'][0]['changed_from'] == "feature"
        assert responseJson['history'][0]['changed_to'] == "hotfix"
        
        assert responseJson['history'][1]['changed_by']['name'] == "Pytest"
        assert responseJson['history'][1]['field'] == "status"
        assert responseJson['history'][1]['changed_from'] == "open"
        assert responseJson['history'][1]['changed_to'] == "in_qa"