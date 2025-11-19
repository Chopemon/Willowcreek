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
                 output_dir: str = "static/generated_images"):
        self.base_url = base_url
        self.output_dir = output_dir
        self.client_id = str(uuid.uuid4())

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

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
                # Use custom workflow if provided
                prompt_data = workflow
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
                        print(f"[ComfyUI] Error queuing prompt: {response.status}")
                        return None

                    result = await response.json()
                    prompt_id = result.get("prompt_id")

                    if not prompt_id:
                        print("[ComfyUI] No prompt_id received")
                        return None

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

                            # Find the SaveImage node output
                            for node_id, node_output in outputs.items():
                                if "images" in node_output:
                                    images = node_output["images"]
                                    if images:
                                        # Download the first image
                                        image_info = images[0]
                                        filename = image_info.get("filename")
                                        subfolder = image_info.get("subfolder", "")

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
            params["type"] = "output"

            async with session.get(
                f"{self.base_url}/view",
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
