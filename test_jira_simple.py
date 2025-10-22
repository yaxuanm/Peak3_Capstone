#!/usr/bin/env python3
"""
Simple Jira test to identify the exact API issue
"""

import requests
import base64
import json

def test_jira_apis():
    print("🔧 Testing Jira APIs")
    print("=" * 40)
    
    # Use the same config from your .env file
    base_url = "https://peak3capstone.atlassian.net"
    email = "yaxuanm@andrew.cmu.edu"
    api_token = "ATATT3xFfGF080Y_-4n1Bm9DggWLmtk29FpPx8rgRm2HFQ6eeCPJasGGlX1mjq5VEy8jbc86AxS7qHGx1LmfMfDilpAlS6WR11zjA0Vt7X7BDB-R7tkGdgr8vFID1WjXDBJ06wBek9d0h9_RCrasSiZFZvVTRkA4WpU3J4mp5Nuhb95ejTkkAM4=04742403"
    project_key = "SCRUM"
    
    # Create auth header
    auth_string = base64.b64encode(f"{email}:{api_token}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_string}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"Testing with:")
    print(f"  Base URL: {base_url}")
    print(f"  Email: {email}")
    print(f"  Project: {project_key}")
    print(f"  API Token: {api_token[:20]}...")
    print()
    
    # Test 1: Get user info
    print("🧪 Test 1: Get user info")
    try:
        response = requests.get(f"{base_url}/rest/api/3/myself", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user = response.json()
            print(f"✅ User: {user.get('displayName')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # Test 2: Get project info
    print("🧪 Test 2: Get project info")
    try:
        response = requests.get(f"{base_url}/rest/api/3/project/{project_key}", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            project = response.json()
            print(f"✅ Project: {project.get('name')}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # Test 3: Search API (the one causing 410 error)
    print("🧪 Test 3: Search API")
    try:
        jql = f'project = "{project_key}"'
        search_url = f"{base_url}/rest/api/3/search/jql?jql={jql}&maxResults=1"
        print(f"URL: {search_url}")
        
        response = requests.get(search_url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search successful: {data.get('total', 0)} issues found")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # Test 4: Create a simple test issue
    print("🧪 Test 4: Create test issue")
    try:
        test_issue = {
            "fields": {
                "project": {"key": project_key},
                "summary": "Test Issue - Peak3 Requirements Automation",
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "This is a test issue created by Peak3 Requirements Automation system."
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": "Task"}
            }
        }
        
        response = requests.post(
            f"{base_url}/rest/api/3/issue",
            headers=headers,
            json=test_issue
        )
        print(f"Status: {response.status_code}")
        
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
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print(f"\n🎯 Test completed!")

if __name__ == "__main__":
    test_jira_apis()
