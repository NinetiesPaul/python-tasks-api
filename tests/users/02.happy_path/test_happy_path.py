import pytest
import requests
from app.app import app

"""
This test will perform a rundown of the entire task life cycle: create,
update, assignment and unassignment, comment creation and exclusion, and
task closing, while veryfing response's integrity, status and values 
"""

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
        
class TestHappyPath:
    token = ""
    secondToken = ""
    taskId = 1
    user = None
    assignmentId = 1
    commentId = 1
        
    def test_set_up(self, client):
        url = "http://localhost:5000/login"
        response = client.post(url, json={
            "username": "user@test",
            "password": "123456"
        })
        responseJson = response.get_json()
        TestHappyPath.token = responseJson['token']

        url = "http://localhost:5000/login"
        secondUserResponse = client.post(url, json={
            "username": "usertwo@test",
            "password": "123456"
        })
        secondResponseJson = secondUserResponse.get_json()
        TestHappyPath.secondToken = secondResponseJson['token']

    def test_create_task(self, client):
        url = "http://localhost:5000/api/task/create"
        new_task = {
            "title": "Task title",
            "description": "This is the task description",
            "type": "feature"
        }
        response = client.post(url, json=new_task, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["data"]
        assert isinstance(responseJson, object)
        
        TestHappyPath.taskId = responseJson['id']
        
        expectedKeys = [ "closed_by", "closed_on", "created_by", "created_on", "description", "id", "status", "title", "type" ]
        assert expectedKeys == list(responseJson.keys())
        assert responseJson['closed_by'] == None
        assert responseJson['closed_on'] == None
        assert isinstance(responseJson['created_by'], object)
        assert responseJson['created_by']['name'] == "Test User One"
        assert responseJson['status'] == "open"
    
    def test_list_all_tasks(self, client):
        url = "http://localhost:5000/api/task/list"
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["data"]
        total = responseJson['total']
        length = len(responseJson['tasks'])
        assert total == length
        
        expectedKeys = [ "assignees", "closed_by", "closed_on", "created_by", "created_on", "description", "id", "status", "title", "type" ]
        assert expectedKeys == list(responseJson['tasks'][0].keys())
    
    def test_view_task(self, client):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()['data']
        
        expectedKeys = [ "assignees", "closed_by", "closed_on", "comments", "created_by", "created_on", "description", "history", "id", "status", "title", "type" ]
        assert expectedKeys == list(responseJson.keys())
    
    def test_update_task(self, client):
        url = "http://localhost:5000/api/task/update/" + str(TestHappyPath.taskId)
        update = {
            "type": "hotfix",
            "status": "in_qa",
            "title": "New title",
            "description": "New description"
        }
        response = client.put(url, headers={"Authorization": "Bearer " + TestHappyPath.token}, json=update)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["data"]
        assert isinstance(responseJson, object)
        
        assert responseJson['type'] == "hotfix"
        assert responseJson['status'] == "in_qa"

    def test_history_updated(self, client):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()['data']
        assert isinstance(responseJson, object)
        assert isinstance(responseJson['history'][0]['changed_by'], object)
        
        history = responseJson['history']
        
        for entry in history:
            if entry['field'] == "type":
                assert entry['changed_from'] == "feature"
                assert entry['changed_to'] == "hotfix"
                
            if entry['field'] == "status":
                assert entry['changed_from'] == "open"
                assert entry['changed_to'] == "in_qa"
                
            if entry['field'] == "title":
                assert entry['changed_from'] == "Task title"
                assert entry['changed_to'] == "New title"
                
            if entry['field'] == "description":
                assert entry['changed_from'] == "This is the task description"
                assert entry['changed_to'] == "New description"
    
    def test_list_all_users(self, client):
        url = "http://localhost:5000/api/users/list"
        response = client.get(url)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["data"]
        users = responseJson["users"]
        TestHappyPath.user = users[0]
    
    def test_assign_task(self, client):
        url = "http://localhost:5000/api/task/assign/" + str(TestHappyPath.taskId)
        payload = {
            "assigned_to": TestHappyPath.user['id']
        }
        response = client.post(url, headers={"Authorization": "Bearer " + TestHappyPath.token}, json=payload)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["data"]
        assert isinstance(responseJson, object)
        TestHappyPath.assignmentId = responseJson['id']
        
        assert TestHappyPath.user['id'] == responseJson['assigned_to']['id']
    
    def test_history_updated_for_the_assignee(self, client):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()['data']
        assert isinstance(responseJson, object)
        assert len(responseJson['assignees']) == 1
        assert isinstance(responseJson['assignees'][0], object)
        
        history = responseJson['history']
        for entry in history:
            if entry['field'] == "added_assignee":
                assert entry['changed_to'] == TestHappyPath.user['name']
    
    def test_unassign_task(self, client):
        url = "http://localhost:5000/api/task/unassign/" + str(TestHappyPath.assignmentId)
        response = client.delete(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["data"]
        assert responseJson == None
    
    def test_history_updated_for_the_unassignee(self, client):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()['data']
        assert isinstance(responseJson, object)
        assert len(responseJson['assignees']) == 0
        
        history = responseJson['history']
        for entry in history:
            if entry['field'] == "removed_assignee":
                assert entry['changed_to'] == TestHappyPath.user['name']
    
    def test_create_comments_on_task(self, client):
        url = "http://localhost:5000/api/task/comment/" + str(TestHappyPath.taskId)
        payload = {
            "text": "First comment"
        }
        response = client.post(url, headers={"Authorization": "Bearer " + TestHappyPath.token}, json=payload)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()['data']
        assert isinstance(responseJson, object)
        assert responseJson['created_by']['name'] == "Test User One"
        
        TestHappyPath.commentId = responseJson['id']
        
        url = "http://localhost:5000/api/task/comment/" + str(TestHappyPath.taskId)
        payload = {
            "text": "Second comment"
        }
        response = client.post(url, headers={"Authorization": "Bearer " + TestHappyPath.token}, json=payload)
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
    
    def test_delete_task_comment(self, client):
        url = "http://localhost:5000/api/task/comment/" + str(TestHappyPath.commentId)
        response = client.delete(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["data"]
        assert responseJson == None
    
    def test_task_has_one_comment(self, client):
        url = "http://localhost:5000/api/task/view/" + str(TestHappyPath.taskId)
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.token})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()['data']
        assert isinstance(responseJson, object)
        assert len(responseJson['comments']) == 1
        assert responseJson['comments'][0]['comment_text'] == "Second comment"
    
    def test_close_task(self, client):      
        url = "http://localhost:5000/api/task/close/" + str(TestHappyPath.taskId)
        response = client.put(url, headers={"Authorization": "Bearer " + TestHappyPath.secondToken})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()['data']
        assert isinstance(responseJson, object)
        assert responseJson['created_by']['name'] == "Test User One"
        assert responseJson['closed_by']['name'] == "Test User Two"

    def test_list_tasks_filter_validation(self, client):      
        url = "http://localhost:5000/api/task/list?type=type&status=status&created_by=999999"
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.secondToken})
        assert response.status_code == 400
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "INVALID_TYPE" in responseJson
        assert "INVALID_STATUS" in responseJson
        assert "USER_NOT_FOUND" in responseJson

    def test_list_tasks_filter_by_created_by(self, client):      
        url = "http://localhost:5000/api/task/list?created_by=" + str(TestHappyPath.user['id'])
        response = client.get(url, headers={"Authorization": "Bearer " + TestHappyPath.secondToken})
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"

    def test_protected_url_requires_token(self, client):      
        url = "http://localhost:5000/api/task/list"
        response = client.get(url)
        assert response.status_code == 401
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "MISSING_TOKEN" in responseJson

    def test_protected_url_refuses_invalid_token(self, client):      
        url = "http://localhost:5000/api/task/list"
        response = client.get(url, headers={"Authorization": "Bearer some token"})
        assert response.status_code == 401
        assert response.headers["Content-Type"] == "application/json"
        
        responseJson = response.get_json()["message"]
        assert isinstance(responseJson, list)
        assert "INVALID_TOKEN" in responseJson