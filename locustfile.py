"""
Locust load testing file for SmartSupport Backend API.

Usage:
    locust -f locustfile.py --host=http://localhost:8000
    Then open http://localhost:8089 in your browser to start the test.
"""
import random
from locust import HttpUser, task, between
from app.core.config import settings

SUPPORT_TEXTS = [
    "I lost my card, please help me block it immediately.",
    "My internet connection is not working, I need assistance.",
    "I want to change my PIN number.",
    "I cannot access my account, please reset my password.",
    "My card was stolen, I need to report it urgently.",
]


class SmartSupportUser(HttpUser):
    """Locust user class for load testing SmartSupport Backend API."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Set up authentication headers when user starts."""
        self.api_key = settings.API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    @task(3)
    def health_check(self):
        """Health check endpoint - frequently accessed."""
        self.client.get("/")
    
    @task(1)
    def create_ticket(self):
        """Create a support ticket - simulates actual user behavior."""
        text = random.choice(SUPPORT_TEXTS)
        self.client.post(
            "/api/v1/tickets",
            json={"text": text},
            headers=self.headers
        )