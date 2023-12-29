from diffusers import DiffusionPipeline
import torch
from PIL import Image
from typing import Any, Union
import numpy as np


class StableDiffusionGeneration:
    def __init__(self):
        self.base: DiffusionPipeline = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0",
            torch_dtype=torch.float16,
            variant="fp16",
            use_safetensors=True
        ).to("cuda")

        self.refiner: DiffusionPipeline = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0",
            text_encoder_2=self.base.text_encoder_2,
            vae=self.base.vae,
            torch_dtype=torch.float16,
            use_safetensors=True,
            variant="fp16",
        ).to("cuda")

    def generate_image(self, prompt: str, n_steps: int = 40, high_noise_frac: float = 0.8) -> Any:
        image = self.base(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_end=high_noise_frac,
            output_type="latent",
        ).images
        image = self.refiner(
            prompt=prompt,
            num_inference_steps=n_steps,
            denoising_start=high_noise_frac,
            image=image,
        ).images[0]
        return image

    def save_image(
        self,
        image: Union[torch.Tensor, np.ndarray, Image.Image],
        file_path: str
        ) -> None:
        if isinstance(image, torch.Tensor):
            image = Image.fromarray(image.cpu().numpy())
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        # if the image is already a PIL Image, no conversion is needed.
        image.save(file_path)
