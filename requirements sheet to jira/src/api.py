"""
Flask API endpoints for Peak3 Requirements Automation
Provides REST API for frontend integration
"""

import os
import base64
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

try:
    from convert import run as convert_run
    from utils import load_env, load_yaml_config
except ImportError:
    from convert import run as convert_run
    from utils import load_env, load_yaml_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_base64_file(base64_content, filename):
    """Save base64 content to temporary file"""
    try:
        # Decode base64 content
        file_content = base64.b64decode(base64_content)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=f'.{filename.split(".")[-1]}',
            dir=UPLOAD_FOLDER
        )
        temp_file.write(file_content)
        temp_file.close()
        
        return temp_file.name
    except Exception as e:
        logger.error(f"Error saving base64 file: {e}")
        raise

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Peak3 Requirements Automation API is running'
    })

@app.route('/api/process', methods=['POST'])
def process_requirements():
    """
    Process requirements file and create Jira tickets
    Expected payload:
    {
        "fileContent": "base64_encoded_file_content",
        "fileName": "requirements.xlsx",
        "jiraConfig": {
            "baseUrl": "https://company.atlassian.net",
            "email": "user@company.com",
            "apiToken": "ATATT3x...",
            "projectKey": "REQ"
        }
    }
    """
    try:
        # Load environment and configuration
        load_env()
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        file_content = data.get('fileContent')
        file_name = data.get('fileName', 'requirements.xlsx')
        jira_config = data.get('jiraConfig', {})
        
        if not file_content:
            return jsonify({
                'success': False,
                'error': 'No file content provided'
            }), 400
        
        logger.info(f"Processing file: {file_name}")
        
        # Save file from base64 content
        temp_file_path = save_base64_file(file_content, file_name)
        
        try:
            # Create temporary config file for this request
            config_data = {
                'excel': {
                    'sheet_name': "1. Requirements - Internal",
                    'columns': {
                        'requirement_id': "Requirement ID",
                        'requirement': "Requirement",
                        'description': "Description",
                        'priority': "Priority",
                        'domain': "Domain",
                        'sub_domain': "Sub-domain",
                        'requirement_type': "Requirement type"
                    }
                },
                'jira': {
                    'project_key': jira_config.get('projectKey', 'SCRUM'),
                    'priority_mapping': {
                        "P0": "Highest",
                        "P1": "High",
                        "P2": "Medium",
                        "P3": "Low",
                        "P4": "Lowest"
                    }
                }
            }
            
            # Save config to temporary file
            import yaml
            temp_config_path = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix='.yml',
                mode='w'
            )
            yaml.dump(config_data, temp_config_path)
            temp_config_path.close()
            
            # Set environment variables for this request
            original_env = {}
            env_vars = {
                'JIRA_BASE_URL': jira_config.get('baseUrl'),
                'JIRA_EMAIL': jira_config.get('email'),
                'JIRA_API_TOKEN': jira_config.get('apiToken'),
                'JIRA_PROJECT_KEY': jira_config.get('projectKey')
            }
            
            # Backup original env vars and set new ones
            for key, value in env_vars.items():
                if value:
                    original_env[key] = os.environ.get(key)
                    os.environ[key] = value
            
            try:
                # Run conversion (dry run first to validate)
                logger.info("Running dry run validation...")
                convert_run(
                    excel_path=temp_file_path,
                    config_path=temp_config_path.name,
                    dry_run=True
                )
                
                # Run actual conversion
                logger.info("Creating Jira tickets...")
                convert_run(
                    excel_path=temp_file_path,
                    config_path=temp_config_path.name,
                    dry_run=False
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Requirements processed and Jira tickets created successfully',
                    'fileName': file_name
                })
                
            finally:
                # Restore original environment variables
                for key, original_value in original_env.items():
                    if original_value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = original_value
                
                # Clean up temporary files
                try:
                    os.unlink(temp_file_path)
                    os.unlink(temp_config_path.name)
                except:
                    pass
                    
        except Exception as e:
            # Clean up temporary file on error
            try:
                os.unlink(temp_file_path)
            except:
                pass
            raise e
            
    except Exception as e:
        logger.error(f"Error processing requirements: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate_requirements():
    """
    Validate requirements file without creating Jira tickets
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        file_content = data.get('fileContent')
        file_name = data.get('fileName', 'requirements.xlsx')
        
        if not file_content:
            return jsonify({
                'success': False,
                'error': 'No file content provided'
            }), 400
        
        # Save file from base64 content
        temp_file_path = save_base64_file(file_content, file_name)
        
        try:
            # Create temporary config file
            config_data = {
                'excel': {
                    'sheet_name': "1. Requirements - Internal",
                    'columns': {
                        'requirement_id': "Requirement ID",
                        'requirement': "Requirement",
                        'description': "Description",
                        'priority': "Priority",
                        'domain': "Domain",
                        'sub_domain': "Sub-domain",
                        'requirement_type': "Requirement type"
                    }
                },
                'jira': {
                    'project_key': 'SCRUM',
                    'priority_mapping': {
                        "P0": "Highest",
                        "P1": "High",
                        "P2": "Medium",
                        "P3": "Low",
                        "P4": "Lowest"
                    }
                }
            }
            
            import yaml
            temp_config_path = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix='.yml',
                mode='w'
            )
            yaml.dump(config_data, temp_config_path)
            temp_config_path.close()
            
            # Run dry run to validate
            convert_run(
                excel_path=temp_file_path,
                config_path=temp_config_path.name,
                dry_run=True
            )
            
            return jsonify({
                'success': True,
                'message': 'File validation successful',
                'fileName': file_name
            })
            
        finally:
            # Clean up temporary files
            try:
                os.unlink(temp_file_path)
                os.unlink(temp_config_path.name)
            except:
                pass
                
    except Exception as e:
        logger.error(f"Error validating requirements: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
