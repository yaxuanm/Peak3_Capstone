"""
Standalone Flask API for Peak3 Requirements Automation
Provides REST API for frontend integration without relative imports
"""

import os
import base64
import tempfile
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Import modules directly
from convert import run as convert_run
from utils import load_env, load_yaml_config
from forge_integration import ForgeWorkflowProcessor

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

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')

@app.route('/demo')
def demo():
    """Serve the simple demo page"""
    return send_from_directory('static', 'simple_demo.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Serve static files (CSS, JS, etc.)"""
    return send_from_directory('static', filename)

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
        # Get request data first
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        file_content = data.get('fileContent')
        file_name = data.get('fileName', 'requirements.xlsx')
        jira_config = data.get('jiraConfig', {})
        
        # Debug: Log the received jira_config
        logger.info(f"Received jira_config: {jira_config}")
        
        # If no jira_config provided, use default values
        if not jira_config or not jira_config.get('baseUrl'):
            logger.info("No jira_config provided, using default values")
            jira_config = {
                'baseUrl': 'https://peak3capstone.atlassian.net',
                'email': 'yaxuanm@andrew.cmu.edu',
                'apiToken': 'ATATT3xFfGF0hrBZ3Jvlrd1NG2lPsiw4wESb2mGQFNGHmJo7ly2afE35yQVMChQ5OYOWZphEphEXzTTIM2QFKjjiee_wdGlmsr610Rwy2qLQ9j_z-By2keMbWMP4GWw0QnMTg00r0gKLjs6oOnQXQQwWEowQTp4UnLcUYTyOP_pW86FkXx9ezQ4=542CC2C0',
                'projectKey': 'SCRUM'
            }
        
        if not file_content:
            return jsonify({
                'success': False,
                'error': 'No file content provided'
            }), 400
        
        logger.info(f"Processing file: {file_name}")
        logger.info(f"Using Jira config: {jira_config.get('baseUrl')} - {jira_config.get('projectKey')}")
        
        # Set environment variables FIRST, before loading any config
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
                logger.info(f"Set {key} = {value[:20]}..." if len(str(value)) > 20 else f"Set {key} = {value}")
        
        # Load environment and configuration AFTER setting our values
        # Don't call load_env() here as it might override our manually set values
        # load_env()
        
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
                },
                'llm': {
                    'enable_quality_check': True,
                    'enable_smart_summary': True
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
            
            try:
                # Run conversion (dry run first to validate)
                logger.info("Running dry run validation...")
                convert_run(
                    excel_path=temp_file_path,
                    config_path=temp_config_path.name,
                    dry_run=True,
                    jira_config=jira_config
                )
                logger.info("Dry run validation completed successfully")
                
                # Run actual conversion
                logger.info("Creating Jira tickets...")
                convert_run(
                    excel_path=temp_file_path,
                    config_path=temp_config_path.name,
                    dry_run=False,
                    jira_config=jira_config
                )
                logger.info("Jira ticket creation completed successfully")
                
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

@app.route('/api/forge/process', methods=['POST'])
def forge_process_workflow():
    """
    Process workflow using original Forge frontend logic
    This endpoint replicates the original Forge resolver.processWorkflow function
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
        jira_config = data.get('jiraConfig', {})
        
        # Debug: Log the received jira_config
        logger.info(f"Received jira_config: {jira_config}")
        
        # If no jira_config provided, use default values
        if not jira_config or not jira_config.get('baseUrl'):
            logger.info("No jira_config provided, using default values")
            jira_config = {
                'baseUrl': 'https://peak3capstone.atlassian.net',
                'email': 'yaxuanm@andrew.cmu.edu',
                'apiToken': 'ATATT3xFfGF0hrBZ3Jvlrd1NG2lPsiw4wESb2mGQFNGHmJo7ly2afE35yQVMChQ5OYOWZphEphEXzTTIM2QFKjjiee_wdGlmsr610Rwy2qLQ9j_z-By2keMbWMP4GWw0QnMTg00r0gKLjs6oOnQXQQwWEowQTp4UnLcUYTyOP_pW86FkXx9ezQ4=542CC2C0',
                'projectKey': 'SCRUM'
            }
        
        if not file_content:
            return jsonify({
                'success': False,
                'error': 'No file content provided'
            }), 400
        
        logger.info(f"Processing workflow with Forge logic: {file_name}")
        
        # Create workflow processor
        processor = ForgeWorkflowProcessor()
        
        # Process workflow using original Forge logic
        result = processor.process_workflow({
            'fileContent': file_content,
            'fileName': file_name,
            'jiraConfig': jira_config
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in Forge workflow processing: {e}")
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
    # Create uploads directory if it doesn't exist
    os.makedirs('uploads', exist_ok=True)
    
    # Run the Flask app
    print("Starting Peak3 Requirements Automation Web Server...")
    print("Web Interface: http://localhost:5000")
    print("API Endpoints: http://localhost:5000/api/")
    print("Press Ctrl+C to stop the server")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
