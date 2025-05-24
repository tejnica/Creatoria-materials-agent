import unittest
import os
import subprocess
import time
import requests

class TestDocker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up Docker container for testing"""
        # Build Docker image
        subprocess.run(["docker", "build", "-t", "creatoria-agent", "."])
        
        # Run container
        subprocess.run([
            "docker", "run", "-d",
            "--name", "creatoria-agent-test",
            "-p", "8000:8000",
            "creatoria-agent"
        ])
        
        # Wait for server to start
        time.sleep(5)

    @classmethod
    def tearDownClass(cls):
        """Clean up Docker container after testing"""
        # Stop and remove container
        subprocess.run(["docker", "stop", "creatoria-agent-test"])
        subprocess.run(["docker", "rm", "creatoria-agent-test"])

    def test_dockerfile_existence(self):
        """Test Dockerfile existence"""
        self.assertTrue(os.path.exists("Dockerfile"))

    def test_dockerfile_content(self):
        """Test Dockerfile content"""
        with open("Dockerfile", "r") as f:
            content = f.read()
            
            # Check base image
            self.assertIn("FROM python:3.9-slim", content)
            
            # Check installation commands
            self.assertIn("RUN pip install", content)
            
            # Check application start command
            self.assertIn("CMD [\"python\", \"main.py\"]", content)

    def test_container_status(self):
        """Test container status"""
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=creatoria-agent-test"],
            capture_output=True,
            text=True
        )
        self.assertIn("creatoria-agent-test", result.stdout)

    def test_health_endpoint(self):
        """Test health endpoint"""
        response = requests.get("http://localhost:8000/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_webhook_functionality(self):
        """Test webhook functionality"""
        data = {
            "query": "pressure_drop < 100 Pa/m",
            "category": "pipes"
        }
        response = requests.post(
            "http://localhost:8000/materials-webhook",
            json=data
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())
        self.assertIn("materials", response.json())

    def test_log_check(self):
        """Test container logs"""
        result = subprocess.run(
            ["docker", "logs", "creatoria-agent-test"],
            capture_output=True,
            text=True
        )
        self.assertIn("Application startup complete", result.stdout)

    def test_environment_variables(self):
        """Test environment variables"""
        result = subprocess.run(
            ["docker", "exec", "creatoria-agent-test", "env"],
            capture_output=True,
            text=True
        )
        self.assertIn("PYTHONPATH", result.stdout)

if __name__ == '__main__':
    unittest.main() 