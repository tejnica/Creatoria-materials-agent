import unittest
import json
import os

class TestN8nIntegration(unittest.TestCase):
    def setUp(self):
        self.workflow_file = "examples/n8n_workflow.json"

    def test_workflow_existence(self):
        """Test workflow file existence"""
        self.assertTrue(os.path.exists(self.workflow_file))

    def test_workflow_structure(self):
        """Test workflow structure"""
        with open(self.workflow_file, 'r') as f:
            workflow = json.load(f)

        # Check required fields
        self.assertIn("name", workflow)
        self.assertIn("nodes", workflow)
        self.assertIn("connections", workflow)

        # Check node types
        node_types = [node["type"] for node in workflow["nodes"]]
        self.assertIn("n8n-nodes-base.webhook", node_types)
        self.assertIn("n8n-nodes-base.httpRequest", node_types)
        self.assertIn("n8n-nodes-base.if", node_types)
        self.assertIn("n8n-nodes-base.set", node_types)

    def test_webhook_node(self):
        """Test webhook node settings"""
        with open(self.workflow_file, 'r') as f:
            workflow = json.load(f)

        webhook_node = next(node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.webhook")
        self.assertEqual(webhook_node["parameters"]["path"], "materials-webhook")

    def test_http_request_node(self):
        """Test HTTP request node settings"""
        with open(self.workflow_file, 'r') as f:
            workflow = json.load(f)

        http_node = next(node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.httpRequest")
        self.assertEqual(http_node["parameters"]["url"], "http://localhost:8000/materials-webhook")
        self.assertIn("bodyParameters", http_node["parameters"])

    def test_if_node(self):
        """Test IF node settings"""
        with open(self.workflow_file, 'r') as f:
            workflow = json.load(f)

        if_node = next(node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.if")
        self.assertIn("conditions", if_node["parameters"])
        self.assertIn("string", if_node["parameters"]["conditions"])

    def test_set_nodes(self):
        """Test Set nodes settings"""
        with open(self.workflow_file, 'r') as f:
            workflow = json.load(f)

        set_nodes = [node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.set"]
        self.assertEqual(len(set_nodes), 2)

        # Check error parameters
        error_node = next(node for node in set_nodes if "error" in node["parameters"])
        self.assertIn("error", error_node["parameters"])

        # Check success parameters
        success_node = next(node for node in set_nodes if "success" in node["parameters"])
        self.assertIn("success", success_node["parameters"])

    def test_connections(self):
        """Test node connections"""
        with open(self.workflow_file, 'r') as f:
            workflow = json.load(f)

        # Check webhook to HTTP request connection
        webhook_node = next(node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.webhook")
        http_node = next(node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.httpRequest")
        self.assertIn(webhook_node["id"], workflow["connections"])
        self.assertIn(http_node["id"], workflow["connections"][webhook_node["id"]])

        # Check HTTP request to IF connection
        if_node = next(node for node in workflow["nodes"] if node["type"] == "n8n-nodes-base.if")
        self.assertIn(http_node["id"], workflow["connections"])
        self.assertIn(if_node["id"], workflow["connections"][http_node["id"]])

if __name__ == '__main__':
    unittest.main() 