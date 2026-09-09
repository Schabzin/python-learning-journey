import numpy as np
import torch
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
import cv2

class ApperanceEmbedder:
    def __init__(self):
        weights = ResNet18_Weights.DEFAULT
        base_model = resnet18(weights=weights)

        self.model = torch.nn.Sequential(*list(base_model.children())[:-1])
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((128, 64)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def get_embedding(self, frame, bbox):
        x1, y1, x2, y2 = [int(v) for v in bbox]
        x1, y1 = max(0, x1), max(0, y1)
        crop = frame[y1:y2, x1:x2]

        if crop.size == 0:
            return np.zeros(512)

        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        tensor = self.transform(crop_rgb).unsqueeze(0)

        with torch.no_grad():
            embedding = self.model(tensor)

        return embedding.squeeze().numpy()

def cosine_distance(embedding_a, embedding_b):
    norm_a = np.linalg.norm(embedding_a)
    norm_b = np.linalg.norm(embedding_b)
    if norm_a == 0 or norm_b == 0:
        return 1.0
    similarity = np.dot(embedding_a, embedding_b) / (norm_a * norm_b)
    return 1.0 - similarity

if __name__ == "__main__":
    embedder = ApperanceEmbedder()
    frame_a = cv2.imread("cropped_test.jpg")
    frame_b = cv2.imread("annotated_test.jpg")

    if frame_a is None or frame_b is None:
        print("Could not load one of the images - check filenames/paths")
    else:
        h_a, w_a = frame_a.shape[:2]
        h_b, w_b = frame_b.shape[:2]

        box_a = (0, 0, w_a, h_a)
        box_b = (0, 0, w_b, h_b)
        

        emb_a = embedder.get_embedding(frame_a, box_a)
        emb_b = embedder.get_embedding(frame_b, box_b)

        distance = cosine_distance(emb_a, emb_b)
        print(f"cropped_test.jpg vs annotated_test.jpg distance: {distance:.4f}")

        self_distance = cosine_distance(emb_a, emb_a)
        print(f"cropped_test.jpg vs itself (should be ~0): {self_distance:.4f}")