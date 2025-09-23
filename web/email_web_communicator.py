"""
Web Communicator for Email Scraper
Handles real-time communication between email scraper and web interface
"""

import json
import time
from typing import Dict, List, Any
from threading import Lock


class EmailWebCommunicator:
    """
    Web communicator for email scraping operations
    Provides real-time updates to web interface
    """
    
    def __init__(self):
        self.progress_data = {
            'status': 'idle',  # idle, running, completed, error
            'progress': 0,
            'message': 'Ready to start email extraction',
            'current_domain': '',
            'current_step': '',
            'found_emails': [],
            'statistics': {},
            'total_steps': 7,  # crawl, google_search, linkedin, directories, social, press, dedupe
            'current_step_number': 0
        }
        self.lock = Lock()
        self.results = []
        
    def reset(self):
        """Reset progress data for new extraction"""
        with self.lock:
            self.progress_data = {
                'status': 'idle',
                'progress': 0,
                'message': 'Ready to start email extraction',
                'current_domain': '',
                'current_step': '',
                'found_emails': [],
                'statistics': {},
                'total_steps': 7,
                'current_step_number': 0
            }
            self.results = []
    
    def start_extraction(self, domain: str):
        """Start email extraction process"""
        with self.lock:
            self.progress_data.update({
                'status': 'running',
                'progress': 0,
                'message': f'Starting email extraction for {domain}',
                'current_domain': domain,
                'current_step': 'Initializing',
                'current_step_number': 0
            })
    
    def update_step(self, step_name: str, step_number: int, message: str = ""):
        """Update current step and progress"""
        with self.lock:
            progress = (step_number / self.progress_data['total_steps']) * 100
            self.progress_data.update({
                'progress': min(progress, 95),  # Cap at 95% until completion
                'current_step': step_name,
                'current_step_number': step_number,
                'message': message or f'Step {step_number}/{self.progress_data["total_steps"]}: {step_name}'
            })
    
    def add_found_email(self, email_result):
        """Add a newly found email to the live results"""
        with self.lock:
            email_data = {
                'email': email_result.email,
                'type': email_result.email_type,
                'source': email_result.source_url,
                'confidence': round(email_result.confidence_score, 2),
                'method': email_result.extraction_method.replace('_', ' ').title()
            }
            self.progress_data['found_emails'].append(email_data)
    
    def update_statistics(self, stats: Dict):
        """Update extraction statistics"""
        with self.lock:
            self.progress_data['statistics'] = stats
    
    def set_completed(self, results: List, stats: Dict):
        """Mark extraction as completed"""
        with self.lock:
            self.results = results
            self.progress_data.update({
                'status': 'completed',
                'progress': 100,
                'message': f'Email extraction completed! Found {len(results)} emails for {self.progress_data["current_domain"]}',
                'statistics': stats
            })
    
    def set_error(self, error_message: str):
        """Mark extraction as failed"""
        with self.lock:
            self.progress_data.update({
                'status': 'error',
                'message': f'Error: {error_message}'
            })
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress data"""
        with self.lock:
            return self.progress_data.copy()
    
    def get_results(self) -> List:
        """Get extraction results"""
        with self.lock:
            return self.results.copy()
    
    def is_running(self) -> bool:
        """Check if extraction is currently running"""
        with self.lock:
            return self.progress_data['status'] == 'running'
    
    def is_completed(self) -> bool:
        """Check if extraction is completed"""
        with self.lock:
            return self.progress_data['status'] == 'completed'


# Global instance for web interface
email_web_comm = EmailWebCommunicator()