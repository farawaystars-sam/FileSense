import torch  # PyTorch library for deep learning
from transformers import CLIPProcessor, CLIPModel, pipeline  # Hugging Face Transformers for CLIP model
from PIL import Image  # PIL (Pillow) for image handling

# Initialize Models
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# CLIP for Image Classification
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def classify_image(file_path):
    """Classify an image file using CLIP."""
    image = Image.open(file_path).convert("RGB")
    inputs = clip_processor(text=["a photo of a dog", "a photo of a cat"], images=image, return_tensors="pt", padding=True).to(device)
    outputs = clip_model(**inputs)
    logits_per_image = outputs.logits_per_image  # Image-to-text similarity scores
    probs = logits_per_image.softmax(dim=1)  # Probabilities
    label = ["dog", "cat"][probs.argmax()]  # Choose the highest probability label
    return label