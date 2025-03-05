import torch  # PyTorch library for deep learning
from transformers import CLIPProcessor, CLIPModel, pipeline  # Hugging Face Transformers for CLIP model
from PIL import Image  # PIL (Pillow) for image handling

# Initialize Models
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# CLIP for Image Classification
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
folder_names = [
    "Animals",
    "Nature",
    "Landscapes",
    "Portraits",
    "Food",
    "Sports",
    "Vehicles",
    "Buildings",
    "Fashion",
    "Art",
    "Travel",
    "Events",
    "People",
    "Textures",
    "Objects",
    "Screenshots",
    "Memes",
    "Social Media",
    "Graphics",
    "Before and After"
]

def classify_image(file_path, class_labels):

    """Classify an image file using CLIP based on provided class labels."""
    try:
        # Load and preprocess the image
        image = Image.open(file_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image: {e}")
        return None

    # Prepare the text inputs using the class labels
    text_inputs = [f"a photo of a {label.lower()}" for label in class_labels]

    # Tokenize the image and text inputs
    inputs = clip_processor(text=text_inputs, images=image, return_tensors="pt", padding=True).to(device)  

    # Get the model outputs
    with torch.no_grad():
        outputs = clip_model(**inputs)
    # Extract image-to-text similarity scores
    logits_per_image = outputs.logits_per_image  # Shape: (1, num_class_labels)

    # Calculate probabilities
    probs = logits_per_image.softmax(dim=1)  # Shape: (1, num_class_labels)
    
    # Choose the highest probability label
    predicted_index = probs.argmax().item()

    label = class_labels[predicted_index]  # Get the corresponding class labe
    return label