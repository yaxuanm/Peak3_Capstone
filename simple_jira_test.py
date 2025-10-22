#!/usr/bin/env python3
"""
Simple Jira connection test to identify the exact issue
"""

import requests
import base64
import json

def test_jira_simple():
    print("🔧 Simple Jira Test")
    print("=" * 40)
    
    # Use the same config from your frontend
    base_url = "https://peak3capstone.atlassian.net"
    email = input("Email: ").strip()
    api_token = input("API Token: ").strip()
    project_key = input("Project Key (e.g., PEAK3): ").strip()
    
    if not all([email, api_token, project_key]):
        print("❌ All fields are required!")
        return
    
    # Create auth header
    auth_string = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"\n🧪 Testing basic connection...")
    
    # Test 1: Get user info
    try:
        response = requests.get(f"{base_url}/rest/api/3/myself", headers=headers)
        print(f"User info: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User: {user.get('displayName')}")
        else:
            print(f"❌ User info failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 2: Get project info
    try:
        response = requests.get(f"{base_url}/rest/api/3/project/{project_key}", headers=headers)
        print(f"Project info: {response.status_code}")
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Project: {project.get('name')}")
        else:
            print(f"❌ Project info failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Project error: {e}")
        return
    
    # Test 3: Search API (the one causing 410 error)
    try:
        jql = f'project = "{project_key}"'
        search_url = f"{base_url}/rest/api/3/search?jql={jql}&maxResults=1"
        print(f"\n🔍 Testing search API...")
        print(f"URL: {search_url}")
        
        response = requests.get(search_url, headers=headers)
        print(f"Search result: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful: {data.get('total', 0)} issues found")
        else:
            print(f"❌ Search failed: {response.text}")
            return
    except Exception as e:
        print(f"❌ Search error: {e}")
        return
    
    # Test 4: Create a simple test issue
    try:
        test_issue = {
            "fields": {
                "project": {"key": project_key},
                "summary": "Test Issue - Peak3 Requirements Automation",
                "description": "This is a test issue created by Peak3 Requirements Automation system.",
                "issuetype": {"name": "Task"}
            }
        }
        
        print(f"\n🎫 Testing issue creation...")
        response = requests.post(
            f"{base_url}/rest/api/3/issue",
            headers=headers,
            json=test_issue
        )
        print(f"Create issue: {response.status_code}")
        
        if response.status_code == 201:
            issue = response.json()
            print(f"✅ Issue created: {issue.get('key')}")
            print(f"   URL: {base_url}/browse/{issue.get('key')}")
            
            # Clean up
            print(f"\n🧹 Cleaning up...")
            delete_response = requests.delete(
                f"{base_url}/rest/api/3/issue/{issue.get('key')}",
                headers=headers
            )
            if delete_response.status_code == 204:
                print(f"✅ Test issue deleted")
            else:
                print(f"⚠️  Could not delete: {delete_response.status_code}")
        else:
            print(f"❌ Create issue failed: {response.text}")
    except Exception as e:
        print(f"❌ Create issue error: {e}")
    
    print(f"\n🎯 Test completed!")

if __name__ == "__main__":
    test_jira_simple()
