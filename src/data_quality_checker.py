#!/usr/bin/env python3
"""
Data Quality Checker using OpenAI Agent
This script loads Excel files and performs comprehensive data quality checks
using OpenAI's API to analyze missing values, data patterns, and quality issues.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import json
from openai import OpenAI
from dotenv import load_dotenv
import logging
import sys


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

    
# Load environment variables
load_dotenv()

class DataQualityChecker:
    """
    A class to perform data quality checks on Excel files using OpenAI agent.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the DataQualityChecker with OpenAI client.
        
        Args:
            api_key (str): OpenAI API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        logger.info("DataQualityChecker initialized successfully")
    
    def load_excel_sheet(self, file_path, sheet_name) -> pd.DataFrame:
        """
        Load an Excel file into a pandas DataFrame.
        
        Args: 
            file_path (str): Path to the Excel file
            sheet_name (str): Name of the sheet to load. If None, loads the first sheet.
            
        Returns:
            pd.DataFrame: Loaded Excel data
        """
        try:
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                df = pd.read_excel(file_path)
            
            logger.info(f"Successfully loaded Excel file: {file_path}")
            logger.info(f"Number of requirements: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading Excel file {file_path}: {str(e)}")
            raise
    
  
    def generate_prompt(self,df) -> str:
        base_prompt = f"""
            **Context**:  
            You are a **data quality expert** supervising the transformation of requirement rows (from a CSV/Excel doc) into Jira stories. Each row is one Jira story. The Excel contains both Jira-mappable fields and project/governance fields. Your job is to validate completeness, highlight blockers, and generate concise Jira-ready summaries.

            **Language**:  
            Respond in **concise, structured English** suitable for product managers. Keep responses short, clear, and formatted in bullet points or short paragraphs.

            **Explicitness**:  
            Check if the row has all **mandatory Jira mapping fields**:  
            - Requirement ID  
            - Requirement (short title)  
            - Description (full text)  
            - Priority  
            - Domain  
            - Epic Link  

            If all are present → generate a **short Jira summary**:  
            - Summary = [Requirement ID] + Title  
            - Priority = Jira priority mapping (P0 to P4)  
            - Epic Link = mapped epic name  
            - Domain/Sub-domain = Labels  

            If **any required fields are missing** → clearly list which ones are missing, and explain why the Jira story cannot be generated.  

            **Adaptability**:  
            - If optional but important fields (Client Approve, Requirement Status, BA Owner, Release Sprint) are missing, still proceed but add a note: *“Warning: [field] missing, may impact traceability/governance.”*  
            - If Description is unstructured, attempt to reformat into Jira-style:  
            - *As a [user], I want [feature], so that [goal]*  
            - Acceptance Criteria (bullets if available).  
            - If estimation fields (Baseline Estimation, QA Effort, etc.) are present, briefly note them but don’t block Jira creation.  

            **Role/Reasoning**:  
            Act as a **quality gatekeeper and summarizer**:  
            - Validate whether the row is Jira-ready.  
            - Provide Jira-style summary when valid.  
            - Flag blockers if mandatory fields are missing.  
            - Flag warnings for optional fields that are useful for PM/BA governance.  
            - Suggest next steps to fix missing/low-quality data.  
        """
        prompt_list = []
        for idx, row in df.iterrows():
            row_json = row.to_json()
            prompt = base_prompt + f"\n\nHere is the requirement row:\n{row_json}"
            prompt_list.append(prompt)
        return prompt_list
        
      
    
    def get_openai_analysis(self, prompt: str) -> str:
        """
        Get analysis from OpenAI agent.
        
        Args:
            prompt (str): The prompt to send to OpenAI
            
        Returns:
            str: OpenAI's analysis response
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data quality expert with extensive experience in data analysis and quality assessment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error getting OpenAI analysis: {str(e)}")
            raise
    
    def data_quality_check(self, df):
        # Process records individually for better reliability
        # But with optimized prompts and error handling
        # Limit to first 5 records for testing
        responses = []
        
        for idx, (_, row) in enumerate(df.iterrows()):
            # Only process first 5 records for testing
            if idx >= 5:
                break
            try:
                # Generate optimized single-record prompt
                prompt = self.generate_single_record_prompt(row, idx)
                
                # Get response with timeout
                response = self.get_openai_analysis(prompt)
                
                # Parse response
                result = {
                    'row_index': idx,
                    'analysis': response,
                    'summary': self._extract_summary_from_response(response),
                    'description': self._extract_description_from_response(response),
                    'is_valid': self._check_if_valid_from_response(response)
                }
                responses.append(result)
                
                # Add small delay to avoid rate limiting
                import time
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"Error processing record {idx}: {str(e)}")
                # Add fallback result
                responses.append({
                    'row_index': idx,
                    'analysis': f'Error processing: {str(e)}',
                    'summary': '',
                    'description': '',
                    'is_valid': True
                })
        
        return responses
    
    def generate_single_record_prompt(self, row, idx):
        """
        Generate an optimized prompt for a single record
        """
        prompt = f"""Analyze this requirement record and provide:

1. Data Quality Assessment (VALID/INVALID with brief reason)
2. Jira Summary (format: [Requirement ID] + concise title)
3. Standardized Description (format: As a [user], I want [feature], so that [goal])

Record {idx + 1}:
"""
        
        for col, value in row.items():
            if pd.notna(value):
                prompt += f"  {col}: {value}\n"
        
        prompt += """
Please provide your analysis in this exact format:
Quality: [VALID/INVALID] - [brief reason]
Summary: [Requirement ID] + [concise title]
Description: As a [user], I want [feature], so that [goal]
"""
        return prompt
    
    def generate_batch_prompt(self, batch_df, batch_start):
        """
        Generate a single prompt for a batch of records
        """
        prompt = f"""You are a data quality expert analyzing {len(batch_df)} requirement records. For each record, provide:

1. Data Quality Assessment
2. Jira Summary (format: [Requirement ID] + concise title)
3. Standardized Description (format: As a [user], I want [feature], so that [goal])

Records to analyze:
"""
        
        for idx, (_, row) in enumerate(batch_df.iterrows()):
            actual_idx = batch_start + idx
            prompt += f"\nRecord {actual_idx + 1}:\n"
            for col in batch_df.columns:
                value = row[col] if pd.notna(row[col]) else "N/A"
                prompt += f"  {col}: {value}\n"
        
        prompt += """
For each record, provide your analysis in this format:
Record X:
- Quality: [VALID/INVALID with reason]
- Summary: [Requirement ID] + concise title
- Description: As a [user], I want [feature], so that [goal]
- Additional Notes: [any other observations]

Please analyze all records and provide structured output.
"""
        return prompt
    
    def _parse_batch_response(self, response, batch_start, batch_end):
        """
        Parse batch response into individual record results
        """
        results = []
        lines = response.split('\n')
        current_record = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Record ') and ':' in line:
                # Extract record number
                try:
                    record_num = int(line.split()[1].split(':')[0]) - 1
                    if batch_start <= record_num < batch_end:
                        current_record = {
                            'row_index': record_num,
                            'analysis': '',
                            'summary': '',
                            'description': '',
                            'is_valid': True
                        }
                        results.append(current_record)
                except:
                    pass
            elif current_record and line.startswith('- Quality:'):
                current_record['analysis'] += line + '\n'
                current_record['is_valid'] = 'VALID' in line.upper()
            elif current_record and line.startswith('- Summary:'):
                current_record['summary'] = line.replace('- Summary:', '').strip()
            elif current_record and line.startswith('- Description:'):
                current_record['description'] = line.replace('- Description:', '').strip()
            elif current_record and line.startswith('- Additional Notes:'):
                current_record['analysis'] += line + '\n'
        
        # Ensure we have results for all records in the batch
        for i in range(batch_start, batch_end):
            if not any(r['row_index'] == i for r in results):
                results.append({
                    'row_index': i,
                    'analysis': 'No analysis provided',
                    'summary': '',
                    'description': '',
                    'is_valid': True
                })
        
        return results
    
    def _extract_summary_from_response(self, response: str) -> str:
        """
        Extract the generated summary from the LLM response
        """
        try:
            # Look for patterns like "Summary = [REQ-001] Title" or "Jira summary: [REQ-001] Title"
            import re
            
            # Try to find summary patterns
            patterns = [
                r'Summary\s*=\s*\[([^\]]+)\]\s*([^\n]+)',
                r'Jira\s+summary[:\s]*\[([^\]]+)\]\s*([^\n]+)',
                r'\[([^\]]+)\]\s*([^\n]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    req_id = match.group(1)
                    title = match.group(2).strip()
                    return f"[{req_id}] {title}"
            
            # If no pattern found, return empty string
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract summary from response: {str(e)}")
            return ""
    
    def _extract_description_from_response(self, response: str) -> str:
        """
        Extract the standardized description from the LLM response
        """
        try:
            import re
            
            # Look for standardized description patterns
            patterns = [
                r'As a \[([^\]]+)\], I want \[([^\]]+)\], so that \[([^\]]+)\](.*?)(?=\n\n|\n\*|$)',
                r'User Story[:\s]*As a \[([^\]]+)\], I want \[([^\]]+)\], so that \[([^\]]+)\](.*?)(?=\n\n|\n\*|$)',
                r'Description[:\s]*As a ([^,]+), I want ([^,]+), so that ([^,]+)(.*?)(?=\n\n|\n\*|$)',
                r'Description[:\s]*(.*?)(?=\n\n|\n\*|$)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
                if match:
                    if len(match.groups()) >= 3:
                        # User story format
                        user = match.group(1)
                        feature = match.group(2)
                        goal = match.group(3)
                        additional = match.group(4) if len(match.groups()) > 3 else ""
                        
                        description = f"As a {user}, I want {feature}, so that {goal}"
                        if additional.strip():
                            description += f"\n\n{additional.strip()}"
                        return description
                    else:
                        # Simple description format
                        return match.group(1).strip()
            
            # If no pattern found, return empty string
            return ""
            
        except Exception as e:
            logger.warning(f"Failed to extract description from response: {str(e)}")
            return ""
    
    def _check_if_valid_from_response(self, response: str) -> bool:
        """
        Check if the requirement is valid based on the LLM response
        """
        try:
            # Look for indicators that the requirement is valid
            valid_indicators = [
                "jira-ready",
                "all required fields present",
                "can be generated",
                "summary ="
            ]
            
            invalid_indicators = [
                "missing",
                "cannot be generated",
                "blocker",
                "required fields are missing"
            ]
            
            response_lower = response.lower()
            
            # Check for invalid indicators first
            for indicator in invalid_indicators:
                if indicator in response_lower:
                    return False
            
            # Check for valid indicators
            for indicator in valid_indicators:
                if indicator in response_lower:
                    return True
            
            # Default to valid if no clear indicators
            return True
            
        except Exception as e:
            logger.warning(f"Failed to check validity from response: {str(e)}")
            return True
    def save_analysis_report(self, results: Dict[str, Any], output_path: str = None) -> str:
        """
        Save the analysis results to a file.
        
        Args:
            results (Dict[str, Any]): Analysis results
            output_path (str): Path to save the report. If None, creates auto-generated name.
            
        Returns:
            str: Path to the saved report
        """
        if not output_path:
            base_name = os.path.splitext(os.path.basename(results['file_path']))[0]
            output_path = f"{base_name}_data_quality_report.txt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DATA QUALITY ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"File: {results['file_path']}\n")
            f.write(f"Sheet: {results['sheet_name']}\n")
            f.write(f"Analysis Date: {pd.Timestamp.now()}\n\n")
            
            f.write("OPENAI AGENT ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            f.write(results['openai_analysis'])
            f.write("\n\n")
            
            f.write("DETAILED STATISTICS:\n")
            f.write("-" * 40 + "\n")
            f.write(json.dumps(results['missing_analysis'], indent=2))
            f.write("\n\n")
            
            f.write("PATTERN ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            f.write(json.dumps(results['pattern_analysis'], indent=2))
        
        logger.info(f"Analysis report saved to: {output_path}")
        return output_path


def main():

    if len(sys.argv) < 2:
        print("Usage: python3 dataquality_checker.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    api_key = os.getenv("OPENAI_API_KEY")
    model = DataQualityChecker(api_key)
    print(f"📂 Loading file: {file_path}")

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = model.load_excel_sheet(file_path, "1. Requirements - Internal")
    print("✅ Loaded rows:", len(df))

    results = model.data_quality_check(df)

    for result in results:
        print("======== LLM Data Evaluation Response ========")
        print(result)
        print("==============================================")
        print()


if __name__ == "__main__":
    main()

