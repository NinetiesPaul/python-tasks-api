import requests

class TestHappyPath:
    tokenBearer = ""
    taskId = 1
    userId = 1
    assignmentId = 1
    assignedToUser = ""
    commentId = 1
        
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
    
    def test_list_all_users(self):
        url = "http://localhost:5000/api/users/list"
        response = requests.get(url)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        users = responseJson["users"]
        TestHappyPath.userId = users[0]['id']
    
    def test_assign_task(self):
        url = "http://localhost:5000/api/task/assign/" + str(TestHappyPath.taskId)
        payload = {
            "assigned_to": TestHappyPath.userId
        }
        response = requests.post(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer}, json=payload)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        assert isinstance(responseJson, object)
        TestHappyPath.assignmentId = responseJson['id']
        
        assert TestHappyPath.userId == responseJson['assigned_to']['id']
        TestHappyPath.assignedToUserName = responseJson['assigned_to']['name']
    
    def test_history_updated_for_the_assignee(self):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = requests.get(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()['data']
        assert isinstance(responseJson, object)
        assert len(responseJson['assignees']) == 1
        assert isinstance(responseJson['assignees'][0], object)
        assert responseJson['history'][2]['field'] == "added_assignee"
        assert responseJson['history'][2]['changed_by']['name'] == "Pytest"
        assert responseJson['history'][2]['changed_to'] == "Pytest Second"
    
    def test_unassign_task(self):
        url = "http://localhost:5000/api/task/unassign/" + str(TestHappyPath.assignmentId)
        response = requests.delete(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        assert responseJson == None
    
    def test_history_updated_for_the_unassignee(self):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = requests.get(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()['data']
        assert isinstance(responseJson, object)
        assert len(responseJson['assignees']) == 0
        assert responseJson['history'][3]['field'] == "removed_assignee"
        assert responseJson['history'][3]['changed_by']['name'] == "Pytest"
        assert responseJson['history'][3]['changed_to'] == "Pytest Second"
    
    def test_create_comments_on_task(self):
        url = "http://localhost:5000/api/task/comment/" + str(TestHappyPath.taskId)
        payload = {
            "text": "First comment"
        }
        response = requests.post(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer}, json=payload)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()['data']
        assert isinstance(responseJson, object)
        assert responseJson['created_by']['name'] == "Pytest"
        
        TestHappyPath.commentId = responseJson['id']
        
        url = "http://localhost:5000/api/task/comment/" + str(TestHappyPath.taskId)
        payload = {
            "text": "Second comment"
        }
        response = requests.post(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer}, json=payload)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
    
    def test_delete_task_comment(self):
        url = "http://localhost:5000/api/task/comment/" + str(TestHappyPath.commentId)
        response = requests.delete(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()["data"]
        assert responseJson == None
    
    def test_task_has_one_comment(self):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = requests.get(url, headers={"Authorization": "Bearer " + TestHappyPath.tokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()['data']
        assert isinstance(responseJson, object)
        assert len(responseJson['comments']) == 1
        assert responseJson['comments'][0]['comment_text'] == "Second comment"
    
    def test_close_task(self):
        url = "http://localhost:5000/login"
        credentials = {
            "username": "userPytest@test",
            "password": "123456"
        }
        response = requests.post(url, json=credentials)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()
        newTokenBearer = responseJson['token']
        
        url = "http://localhost:5000/api/task/close/" + str(TestHappyPath.taskId)
        response = requests.put(url, headers={"Authorization": "Bearer " + newTokenBearer})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.json()['data']
        assert isinstance(responseJson, object)
        assert responseJson['created_by']['name'] == "Pytest"
        assert responseJson['closed_by']['name'] == "Pytest Second"