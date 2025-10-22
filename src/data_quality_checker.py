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
        prompts = self.generate_prompt(df)
        responses = []
        for prompt in prompts:
            response = self.get_openai_analysis(prompt)
            responses.append(response)
        return responses
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

