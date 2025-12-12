"""
ComfyUI Client - Connects to ComfyUI server for image generation
Supports custom workflows and workflow switching
"""

import json
import uuid
import urllib.request
import urllib.parse
import os
import base64
import asyncio
import websocket
from typing import Dict, Any, Optional, List
from pathlib import Path


class ComfyUIClient:
    """
    Client for ComfyUI image generation server.
    Supports loading custom workflows and real-time generation.
    """

    def __init__(self, server_address: str = "127.0.0.1:8188"):
        self.server_address = server_address
        self.client_id = str(uuid.uuid4())
        self.workflows_dir = Path(__file__).parent.parent / "workflows"
        self.current_workflow: Optional[Dict] = None
        self.current_workflow_name: str = ""

    def is_server_available(self) -> bool:
        """Check if ComfyUI server is running."""
        try:
            url = f"http://{self.server_address}/system_stats"
            req = urllib.request.Request(url, method='GET')
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except Exception:
            return False

    def get_available_workflows(self) -> List[str]:
        """List all available workflow JSON files."""
        if not self.workflows_dir.exists():
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            return []

        workflows = []
        for f in self.workflows_dir.glob("*.json"):
            workflows.append(f.stem)  # filename without .json
        return sorted(workflows)

    def load_workflow(self, workflow_name: str) -> bool:
        """Load a workflow from the workflows directory."""
        workflow_path = self.workflows_dir / f"{workflow_name}.json"

        if not workflow_path.exists():
            print(f"[ComfyUI] Workflow not found: {workflow_path}")
            return False

        try:
            with open(workflow_path, 'r', encoding='utf-8') as f:
                self.current_workflow = json.load(f)
            self.current_workflow_name = workflow_name
            print(f"[ComfyUI] Loaded workflow: {workflow_name}")
            return True
        except json.JSONDecodeError as e:
            print(f"[ComfyUI] Invalid JSON in workflow: {e}")
            return False

    def set_workflow_from_json(self, workflow_json: Dict) -> None:
        """Set workflow directly from a JSON dict."""
        self.current_workflow = workflow_json
        self.current_workflow_name = "custom"

    def _find_node_by_class(self, class_type: str) -> Optional[str]:
        """Find a node ID by its class type."""
        if not self.current_workflow:
            return None
        for node_id, node_data in self.current_workflow.items():
            if node_data.get("class_type") == class_type:
                return node_id
        return None

    def _find_node_by_title(self, title: str) -> Optional[str]:
        """Find a node ID by its title (from _meta)."""
        if not self.current_workflow:
            return None
        for node_id, node_data in self.current_workflow.items():
            meta = node_data.get("_meta", {})
            if meta.get("title", "").lower() == title.lower():
                return node_id
        return None

    def update_prompt(self, prompt: str, negative_prompt: str = "") -> None:
        """Update the prompt in the current workflow."""
        if not self.current_workflow:
            return

        # Try common node types for prompts
        positive_types = ["CLIPTextEncode", "CLIPTextEncodeSDXL"]
        negative_types = ["CLIPTextEncode", "CLIPTextEncodeSDXL"]

        # Find positive prompt node (usually first one or titled "positive")
        pos_node = self._find_node_by_title("positive") or self._find_node_by_title("positive prompt")
        neg_node = self._find_node_by_title("negative") or self._find_node_by_title("negative prompt")

        # If not found by title, try to find by class type
        if not pos_node:
            for node_id, node_data in self.current_workflow.items():
                if node_data.get("class_type") in positive_types:
                    inputs = node_data.get("inputs", {})
                    if "text" in inputs:
                        pos_node = node_id
                        break

        if pos_node and pos_node in self.current_workflow:
            self.current_workflow[pos_node]["inputs"]["text"] = prompt

        if neg_node and neg_node in self.current_workflow and negative_prompt:
            self.current_workflow[neg_node]["inputs"]["text"] = negative_prompt

    def update_seed(self, seed: int = -1) -> None:
        """Update seed in the workflow. -1 for random."""
        if not self.current_workflow:
            return

        if seed == -1:
            import random
            seed = random.randint(0, 2**32 - 1)

        # Common sampler node types
        sampler_types = ["KSampler", "KSamplerAdvanced", "SamplerCustom"]

        for node_id, node_data in self.current_workflow.items():
            if node_data.get("class_type") in sampler_types:
                if "seed" in node_data.get("inputs", {}):
                    self.current_workflow[node_id]["inputs"]["seed"] = seed
                if "noise_seed" in node_data.get("inputs", {}):
                    self.current_workflow[node_id]["inputs"]["noise_seed"] = seed

    def update_dimensions(self, width: int, height: int) -> None:
        """Update image dimensions in the workflow."""
        if not self.current_workflow:
            return

        # Common latent image node types
        latent_types = ["EmptyLatentImage", "EmptySD3LatentImage"]

        for node_id, node_data in self.current_workflow.items():
            if node_data.get("class_type") in latent_types:
                inputs = node_data.get("inputs", {})
                if "width" in inputs:
                    self.current_workflow[node_id]["inputs"]["width"] = width
                if "height" in inputs:
                    self.current_workflow[node_id]["inputs"]["height"] = height

    def queue_prompt(self) -> Optional[str]:
        """Queue the current workflow for generation. Returns prompt_id."""
        if not self.current_workflow:
            print("[ComfyUI] No workflow loaded")
            return None

        payload = {
            "prompt": self.current_workflow,
            "client_id": self.client_id
        }

        data = json.dumps(payload).encode('utf-8')
        url = f"http://{self.server_address}/prompt"

        try:
            req = urllib.request.Request(url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('prompt_id')
        except Exception as e:
            print(f"[ComfyUI] Failed to queue prompt: {e}")
            return None

    def get_history(self, prompt_id: str) -> Optional[Dict]:
        """Get generation history for a prompt_id."""
        url = f"http://{self.server_address}/history/{prompt_id}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"[ComfyUI] Failed to get history: {e}")
            return None

    def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
        """Download a generated image from ComfyUI."""
        params = urllib.parse.urlencode({
            "filename": filename,
            "subfolder": subfolder,
            "type": folder_type
        })
        url = f"http://{self.server_address}/view?{params}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read()
        except Exception as e:
            print(f"[ComfyUI] Failed to get image: {e}")
            return None

    def generate_and_wait(self, prompt: str, negative_prompt: str = "",
                          seed: int = -1, timeout: int = 120) -> Optional[bytes]:
        """
        Generate an image and wait for completion.
        Returns the image bytes or None on failure.
        """
        if not self.current_workflow:
            print("[ComfyUI] No workflow loaded")
            return None

        if not self.is_server_available():
            print("[ComfyUI] Server not available")
            return None

        # Update workflow with parameters
        self.update_prompt(prompt, negative_prompt)
        self.update_seed(seed)

        # Queue the prompt
        prompt_id = self.queue_prompt()
        if not prompt_id:
            return None

        print(f"[ComfyUI] Queued prompt: {prompt_id}")

        # Connect via WebSocket to wait for completion
        ws_url = f"ws://{self.server_address}/ws?clientId={self.client_id}"

        try:
            ws = websocket.create_connection(ws_url, timeout=timeout)

            while True:
                msg = ws.recv()
                if isinstance(msg, str):
                    data = json.loads(msg)
                    msg_type = data.get("type")

                    if msg_type == "executing":
                        exec_data = data.get("data", {})
                        if exec_data.get("prompt_id") == prompt_id:
                            if exec_data.get("node") is None:
                                # Generation complete
                                print("[ComfyUI] Generation complete")
                                break

                    elif msg_type == "execution_error":
                        print(f"[ComfyUI] Execution error: {data}")
                        ws.close()
                        return None

            ws.close()

        except websocket.WebSocketTimeoutException:
            print("[ComfyUI] WebSocket timeout")
            return None
        except Exception as e:
            print(f"[ComfyUI] WebSocket error: {e}")
            return None

        # Get the generated image from history
        history = self.get_history(prompt_id)
        if not history or prompt_id not in history:
            print("[ComfyUI] No history found")
            return None

        outputs = history[prompt_id].get("outputs", {})

        # Find the output image
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                for image_info in node_output["images"]:
                    filename = image_info.get("filename")
                    subfolder = image_info.get("subfolder", "")
                    folder_type = image_info.get("type", "output")

                    image_data = self.get_image(filename, subfolder, folder_type)
                    if image_data:
                        return image_data

        print("[ComfyUI] No images in output")
        return None

    def generate_portrait(self, character_name: str, character_description: str,
                         scene_context: str = "", seed: int = -1) -> Optional[bytes]:
        """
        Generate a character portrait.
        Builds a prompt from character info.
        """
        # Build portrait prompt
        prompt_parts = [
            f"portrait of {character_name}",
            character_description,
        ]

        if scene_context:
            prompt_parts.append(f"in {scene_context}")

        prompt_parts.extend([
            "high quality",
            "detailed face",
            "professional lighting"
        ])

        prompt = ", ".join(prompt_parts)
        negative = "blurry, low quality, distorted, deformed, ugly, bad anatomy"

        return self.generate_and_wait(prompt, negative, seed)


# Singleton instance for easy access
_client: Optional[ComfyUIClient] = None

def get_comfyui_client(server_address: str = "127.0.0.1:8188") -> ComfyUIClient:
    """Get or create the ComfyUI client singleton."""
    global _client
    if _client is None:
        _client = ComfyUIClient(server_address)
    return _client


def generate_image_base64(prompt: str, workflow_name: str = "",
                          negative_prompt: str = "", seed: int = -1) -> Optional[str]:
    """
    Convenience function to generate an image and return as base64.
    """
    client = get_comfyui_client()

    if workflow_name:
        if not client.load_workflow(workflow_name):
            return None
    elif not client.current_workflow:
        # Try to load default workflow
        workflows = client.get_available_workflows()
        if workflows:
            client.load_workflow(workflows[0])
        else:
            print("[ComfyUI] No workflows available")
            return None

    image_bytes = client.generate_and_wait(prompt, negative_prompt, seed)

    if image_bytes:
        return base64.b64encode(image_bytes).decode('utf-8')
    return None
