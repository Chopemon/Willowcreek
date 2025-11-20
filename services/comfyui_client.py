# services/comfyui_client.py
"""
ComfyUI API Client for Automatic Image Generation
Handles communication with ComfyUI server for scene visualization.
"""

import asyncio
import aiohttp
import json
import os
import uuid
from typing import Dict, Optional, Any
from datetime import datetime
import base64


class ComfyUIClient:
    """
    Client for ComfyUI API integration.
    Supports both basic text2img and advanced workflow-based generation.
    """

    def __init__(self,
                 base_url: str = "http://127.0.0.1:8188",
                 output_dir: str = "static/generated_images",
                 workflow_path: Optional[str] = None):
        self.base_url = base_url
        self.output_dir = output_dir
        self.client_id = str(uuid.uuid4())
        self.workflow_template = None

        # Default node mappings (can be overridden by config)
        self.node_mapping = {
            "positive_prompt": "1",
            "negative_prompt": "2",
            "seed": "30",
            "samplers": ["50", "61", "3"]
        }

        # Default workflow path (can be overridden by config)
        self.workflow_path = "workflows/sdxl_upscale.json"

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Load configuration (may override workflow_path)
        self._load_config()

        # Use provided workflow_path if given, otherwise use config or default
        if workflow_path:
            self.workflow_path = workflow_path

        # Load custom workflow
        if self.workflow_path:
            self._load_custom_workflow(self.workflow_path)

    def _load_config(self):
        """Load workflow configuration from config.json"""
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        config_path = base_dir / "workflows" / "config.json"

        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                    # Load workflow file path from config
                    if "workflow_file" in config:
                        self.workflow_path = f"workflows/{config['workflow_file']}"
                        print(f"[ComfyUI] Using workflow from config: {config['workflow_file']}")

                    # Load node mapping from config
                    if "node_mapping" in config:
                        self.node_mapping.update(config["node_mapping"])
                        print(f"[ComfyUI] Loaded node mapping from config: {self.node_mapping}")
            except Exception as e:
                print(f"[ComfyUI] Error loading config: {e}, using defaults")

    def _load_custom_workflow(self, workflow_path: str):
        """Load a custom workflow JSON file"""
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        full_path = base_dir / workflow_path

        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8') as f:
                self.workflow_template = json.load(f)
            print(f"[ComfyUI] Loaded custom workflow from {workflow_path}")
        else:
            print(f"[ComfyUI] Workflow not found at {full_path}, using default")

    def _inject_prompts(self,
                       workflow: Dict,
                       positive: str,
                       negative: str,
                       seed: int) -> Dict:
        """
        Inject prompts and seed into workflow nodes.

        This method finds CLIPTextEncode nodes for prompts and updates seed values
        across various sampler nodes. It's designed to work with the custom SDXL
        workflow but will gracefully skip missing nodes.

        Args:
            workflow: The workflow dictionary to modify
            positive: Positive prompt text
            negative: Negative prompt text
            seed: Random seed for generation

        Returns:
            Modified workflow dictionary (deep copy to avoid mutation)
        """
        # Deep copy to avoid mutating the template
        import copy
        workflow = copy.deepcopy(workflow)

        # Get node IDs from config
        pos_node = self.node_mapping.get("positive_prompt", "1")
        neg_node = self.node_mapping.get("negative_prompt", "2")
        seed_node = self.node_mapping.get("seed", "30")
        sampler_nodes = self.node_mapping.get("samplers", ["50", "61", "3"])

        # Update positive prompt node (CLIPTextEncode)
        if pos_node in workflow and "inputs" in workflow[pos_node]:
            workflow[pos_node]["inputs"]["text"] = positive
            print(f"[ComfyUI] Injected positive prompt into node {pos_node}")
            print(f"[ComfyUI]   Preview: {positive[:150]}{'...' if len(positive) > 150 else ''}")

        # Update negative prompt node (CLIPTextEncode)
        if neg_node in workflow and "inputs" in workflow[neg_node]:
            workflow[neg_node]["inputs"]["text"] = negative
            print(f"[ComfyUI] Injected negative prompt into node {neg_node}")
            print(f"[ComfyUI]   Preview: {negative[:150]}{'...' if len(negative) > 150 else ''}")

        # Update seed generator node
        if seed_node in workflow and "inputs" in workflow[seed_node]:
            workflow[seed_node]["inputs"]["seed"] = seed
            print(f"[ComfyUI] Set seed {seed} in node {seed_node}")

        # Update KSampler nodes with seed
        # These might have 'seed' or 'noise_seed' inputs
        for node_id in sampler_nodes:
            if node_id in workflow and "inputs" in workflow[node_id]:
                inputs = workflow[node_id]["inputs"]
                if "seed" in inputs:
                    inputs["seed"] = seed
                if "noise_seed" in inputs:
                    inputs["noise_seed"] = seed

        return workflow

    async def generate_image(self,
                            prompt: str,
                            negative_prompt: str = "",
                            width: int = 832,
                            height: int = 1216,
                            steps: int = 20,
                            cfg_scale: float = 7.0,
                            seed: Optional[int] = None,
                            workflow: Optional[Dict] = None) -> Optional[str]:
        """
        Generate an image using ComfyUI API.

        Args:
            prompt: The positive prompt describing the scene
            negative_prompt: Things to avoid in the generation
            width: Image width
            height: Image height (832x1216 is good for portraits)
            steps: Number of sampling steps
            cfg_scale: Classifier-free guidance scale
            seed: Random seed (None for random)
            workflow: Optional custom ComfyUI workflow JSON

        Returns:
            Path to generated image file, or None if generation failed
        """
        if seed is None:
            seed = int(datetime.now().timestamp() * 1000) % (2**32)

        try:
            if workflow:
                # Use custom workflow if provided directly
                prompt_data = workflow
            elif self.workflow_template:
                # Use loaded workflow template with prompt injection
                print(f"[ComfyUI] Using custom workflow template with injected prompts")
                prompt_data = self._inject_prompts(
                    self.workflow_template,
                    prompt,
                    negative_prompt,
                    seed
                )
            else:
                # Use default workflow
                prompt_data = self._build_default_workflow(
                    prompt, negative_prompt, width, height, steps, cfg_scale, seed
                )

            # Queue the prompt
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/prompt",
                    json={"prompt": prompt_data, "client_id": self.client_id}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"[ComfyUI] Error queuing prompt: {response.status}")
                        print(f"[ComfyUI] Error details: {error_text}")
                        return None

                    result = await response.json()
                    prompt_id = result.get("prompt_id")

                    if not prompt_id:
                        print("[ComfyUI] No prompt_id received")
                        print(f"[ComfyUI] Response: {result}")
                        return None

                    print(f"[ComfyUI] Prompt queued successfully with ID: {prompt_id}")

                # Wait for generation to complete
                image_path = await self._wait_for_generation(prompt_id, session)
                return image_path

        except Exception as e:
            print(f"[ComfyUI] Image generation error: {e}")
            return None

    async def _wait_for_generation(self,
                                   prompt_id: str,
                                   session: aiohttp.ClientSession,
                                   timeout: int = 300) -> Optional[str]:
        """
        Wait for image generation to complete and retrieve the result.

        Args:
            prompt_id: The ID of the queued prompt
            session: Active aiohttp session
            timeout: Maximum time to wait in seconds

        Returns:
            Path to generated image file
        """
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < timeout:
            try:
                # Check history for completed prompt
                async with session.get(f"{self.base_url}/history/{prompt_id}") as response:
                    if response.status == 200:
                        history = await response.json()

                        if prompt_id in history:
                            outputs = history[prompt_id].get("outputs", {})

                            if not outputs:
                                print(f"[ComfyUI] No outputs yet for prompt {prompt_id}")

                            # Find the SaveImage node output
                            for node_id, node_output in outputs.items():
                                if "images" in node_output:
                                    images = node_output["images"]
                                    if images:
                                        # Download the first image
                                        image_info = images[0]
                                        filename = image_info.get("filename")
                                        subfolder = image_info.get("subfolder", "")

                                        print(f"[ComfyUI] Found image: {filename} in subfolder: {subfolder}")
                                        if filename:
                                            return await self._download_image(
                                                filename, subfolder, session
                                            )

                # Still processing, wait a bit
                await asyncio.sleep(1)

            except Exception as e:
                print(f"[ComfyUI] Error checking status: {e}")
                await asyncio.sleep(1)

        print(f"[ComfyUI] Timeout waiting for prompt {prompt_id}")
        return None

    async def _download_image(self,
                             filename: str,
                             subfolder: str,
                             session: aiohttp.ClientSession) -> Optional[str]:
        """
        Download generated image from ComfyUI server.

        Args:
            filename: Name of the image file
            subfolder: Subfolder in ComfyUI output directory
            session: Active aiohttp session

        Returns:
            Local path to downloaded image
        """
        try:
            # Build download URL
            params = {"filename": filename}
            if subfolder:
                params["subfolder"] = subfolder

            # Detect if this is a temp file (ComfyUI uses different type for temp files)
            if "_temp_" in filename or filename.startswith("temp_"):
                params["type"] = "temp"
            else:
                params["type"] = "output"

            download_url = f"{self.base_url}/view"
            print(f"[ComfyUI] Downloading from: {download_url} with params: {params}")

            async with session.get(
                download_url,
                params=params
            ) as response:
                if response.status == 200:
                    # Generate unique filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    unique_filename = f"scene_{timestamp}_{uuid.uuid4().hex[:8]}.png"
                    output_path = os.path.join(self.output_dir, unique_filename)

                    # Save image
                    with open(output_path, "wb") as f:
                        f.write(await response.read())

                    print(f"[ComfyUI] Image saved: {output_path}")
                    return f"/generated_images/{unique_filename}"
                else:
                    print(f"[ComfyUI] Error downloading image: {response.status}")
                    return None

        except Exception as e:
            print(f"[ComfyUI] Error downloading image: {e}")
            return None

    def _build_default_workflow(self,
                                prompt: str,
                                negative_prompt: str,
                                width: int,
                                height: int,
                                steps: int,
                                cfg_scale: float,
                                seed: int) -> Dict[str, Any]:
        """
        Build a default ComfyUI workflow for basic text2img generation.

        This creates a simple workflow compatible with most ComfyUI setups.
        Users can customize this or provide their own workflow.
        """
        return {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg_scale,
                    "sampler_name": "euler_ancestral",
                    "scheduler": "normal",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"  # Default SDXL model
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "WillowCreek",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

    async def test_connection(self) -> bool:
        """
        Test if ComfyUI server is accessible.

        Returns:
            True if server is reachable, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/system_stats") as response:
                    if response.status == 200:
                        print("[ComfyUI] Connection successful")
                        return True
                    else:
                        print(f"[ComfyUI] Server returned status {response.status}")
                        return False
        except Exception as e:
            print(f"[ComfyUI] Connection failed: {e}")
            return False

    async def get_models(self) -> Dict[str, Any]:
        """
        Get available models from ComfyUI.

        Returns:
            Dictionary of available models
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/object_info") as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
        except Exception as e:
            print(f"[ComfyUI] Error getting models: {e}")
            return {}
