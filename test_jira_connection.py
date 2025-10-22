#!/usr/bin/env python3
"""
Test Jira connection and permissions
"""

import requests
import base64
import json

def test_jira_connection():
    # Get Jira configuration from user
    print("🔧 Jira Connection Test")
    print("=" * 50)
    
    base_url = input("Jira Base URL (e.g., https://peak3capstone.atlassian.net): ").strip()
    email = input("Email: ").strip()
    api_token = input("API Token: ").strip()
    project_key = input("Project Key (e.g., PEAK3): ").strip()
    
    if not all([base_url, email, api_token, project_key]):
        print("❌ All fields are required!")
        return
    
    # Test 1: Basic authentication
    print("\n🧪 Test 1: Basic Authentication")
    auth_string = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Test user info
        response = requests.get(f"{base_url}/rest/api/3/myself", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Authentication successful!")
            print(f"   User: {user_info.get('displayName')} ({user_info.get('emailAddress')})")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 2: Project access
    print(f"\n🧪 Test 2: Project Access ({project_key})")
    try:
        response = requests.get(f"{base_url}/rest/api/3/project/{project_key}", headers=headers)
        if response.status_code == 200:
            project_info = response.json()
            print(f"✅ Project access successful!")
            print(f"   Project: {project_info.get('name')} ({project_info.get('key')})")
        else:
            print(f"❌ Project access failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Project access error: {e}")
        return
    
    # Test 3: Create issue permission
    print(f"\n🧪 Test 3: Create Issue Permission")
    test_issue = {
        "fields": {
            "project": {"key": project_key},
            "summary": "Test Issue - Peak3 Requirements Automation",
            "description": "This is a test issue created by Peak3 Requirements Automation system.",
            "issuetype": {"name": "Task"}
        }
    }
    
    try:
        response = requests.post(
            f"{base_url}/rest/api/3/issue",
            headers=headers,
            json=test_issue
        )
        if response.status_code == 201:
            issue_info = response.json()
            print(f"✅ Create issue permission successful!")
            print(f"   Created issue: {issue_info.get('key')}")
            print(f"   Issue URL: {base_url}/browse/{issue_info.get('key')}")
            
            # Clean up - delete the test issue
            print(f"\n🧹 Cleaning up test issue...")
            delete_response = requests.delete(
                f"{base_url}/rest/api/3/issue/{issue_info.get('key')}",
                headers=headers
            )
            if delete_response.status_code == 204:
                print(f"✅ Test issue deleted successfully")
            else:
                print(f"⚠️  Could not delete test issue: {delete_response.status_code}")
                
        else:
            print(f"❌ Create issue permission failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Create issue error: {e}")
    
    print(f"\n🎯 Summary:")
    print(f"   Base URL: {base_url}")
    print(f"   Email: {email}")
    print(f"   Project: {project_key}")
    print(f"   API Token: {api_token[:10]}...")

if __name__ == "__main__":
    test_jira_connection()
