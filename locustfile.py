"""
Locust load testing file for SmartSupport Backend API.

Usage:
    locust -f locustfile.py --host=http://localhost:8000

    Then open http://localhost:8089 in your browser to start the test.
"""
import random
from locust import HttpUser, task, between
from app.core.config import settings

# Sample support ticket texts for realistic load testing
SUPPORT_TEXTS = [
    "I lost my card, please help me block it immediately.",
    "My internet connection is not working, I need assistance.",
    "I want to change my PIN number.",
    "I cannot access my account, please reset my password.",
    "My card was stolen, I need to report it urgently.",
    "I need to check my account balance.",
    "I want to transfer money to another account.",
    "My payment was declined, what should I do?",
    "I need help with my mobile banking app.",
    "I forgot my password and cannot log in.",
    "I want to update my personal information.",
    "My card is not working at the ATM.",
    "I need to increase my transaction limit.",
    "I want to close my account.",
    "I received a suspicious email, is it legitimate?",
    "My card was swallowed by the ATM machine.",
    "I need to report a fraudulent transaction.",
    "I want to activate my new card.",
    "I cannot make online payments, please help.",
    "I need information about exchange rates.",
]


class SmartSupportUser(HttpUser):
    """
    Locust user class for load testing SmartSupport Backend API.
    
    Simulates user behavior:
    - Health checks (more frequent)
    - Creating support tickets (less frequent)
    """
    
    # Wait time between tasks: random between 1 and 3 seconds
    wait_time = between(1, 3)
    
    # Base URL will be set via --host flag when running locust
    # Example: locust -f locustfile.py --host=http://localhost:8000
    
    def on_start(self):
        """
        Called when a simulated user starts.
        Sets up authentication headers.
        """
        # Get API key from settings (or use default for testing)
        self.api_key = settings.API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    @task(3)  # Higher weight: 3x more likely to be called
    def health_check(self):
        """
        Health check endpoint - frequently accessed.
        Weight: 3 (called 3x more often than create_ticket)
        """
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed with status {response.status_code}")
    
    @task(1)  # Lower weight: called less frequently
    def create_ticket(self):
        """
        Create a support ticket - simulates actual user behavior.
        Weight: 1 (called less frequently than health checks)
        """
        # Randomly select a support text
        text = random.choice(SUPPORT_TEXTS)
        
        payload = {
            "text": text
        }
        
        with self.client.post(
            "/api/v1/tickets",
            json=payload,
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 202:  # Accepted (async task)
                # Verify response structure
                try:
                    data = response.json()
                    if "task_id" in data and "status" in data:
                        response.success()
                    else:
                        response.failure("Invalid response structure")
                except Exception as e:
                    response.failure(f"Failed to parse response: {str(e)}")
            elif response.status_code == 429:  # Rate limited
                # Rate limiting is expected under high load
                response.success()  # Don't count rate limits as failures
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

