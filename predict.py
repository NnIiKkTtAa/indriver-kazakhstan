import torch
import torch.nn as nn
from PIL import Image
import torchvision.transforms as transforms
import random

# --- Константы ---
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
CLEANLINESS_CLASSES = ['чистый', 'грязный']
DAMAGE_CLASSES = ['целый', 'битый']

# --- Упрощенная модель ---
class SimpleCarModel(nn.Module):
    def __init__(self, num_clean_classes=2, num_damage_classes=2):
        super(SimpleCarModel, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.clean_classifier = nn.Linear(64, num_clean_classes)
        self.damage_classifier = nn.Linear(64, num_damage_classes)
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        clean_out = self.clean_classifier(x)
        damage_out = self.damage_classifier(x)
        return clean_out, damage_out

# --- Упрощенные трансформы ---
def get_transforms():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

# --- Упрощенная загрузка модели ---
def get_model(pretrained=False):
    return SimpleCarModel()

def predict(image_path):
    """
    Упрощенная функция предсказания для демонстрации.
    Возвращает результаты в формате, который ожидает app.py
    """
    try:
        # Создаем простую модель (в реальности нужно загружать веса)
        model = get_model(pretrained=False)
        model.to(DEVICE)
        model.eval()

        # Подготовка изображения
        transform = get_transforms()
        image = Image.open(image_path).convert('RGB')
        image_tensor = transform(image)
        image_tensor = image_tensor.unsqueeze(0).to(DEVICE)

        # Имитация предсказания (в демо-режиме)
        # В реальном приложении здесь должно быть torch.no_grad() и forward
        with torch.no_grad():
            clean_probs = torch.softmax(torch.randn(1, 2), dim=1)
            damage_probs = torch.softmax(torch.randn(1, 2), dim=1)
        
        clean_idx = torch.argmax(clean_probs, dim=1)
        damage_idx = torch.argmax(damage_probs, dim=1)

        result = {
            'cleanliness': {
                'class': CLEANLINESS_CLASSES[clean_idx.item()],
                'confidence': clean_probs[0][clean_idx.item()].item()
            },
            'damage': {
                'class': DAMAGE_CLASSES[damage_idx.item()],
                'confidence': damage_probs[0][damage_idx.item()].item()
            },
            'cleanliness_probs': clean_probs.cpu().numpy().tolist(),
            'damage_probs': damage_probs.cpu().numpy().tolist()
        }
        
    except Exception as e:
        print(f"Ошибка при предсказании: {e}")
        # Возвращаем случайные результаты для демонстрации
        clean_conf = random.uniform(0.6, 0.9)
        damage_conf = random.uniform(0.7, 0.95)
        
        result = {
            'cleanliness': {
                'class': 'чистый',
                'confidence': clean_conf
            },
            'damage': {
                'class': 'целый',
                'confidence': damage_conf
            },
            'cleanliness_probs': [[clean_conf, 1 - clean_conf]],
            'damage_probs': [[damage_conf, 1 - damage_conf]]
        }
    
    return result

# Функция для тестирования (необязательна для основного приложения)
def test_prediction():
    """Тестовая функция для проверки работы predict"""
    try:
        # Создаем тестовое изображение
        test_image = Image.new('RGB', (300, 300), color='red')
        test_image.save('test_image.jpg')
        
        prediction = predict('test_image.jpg')
        
        print("\n--- Результат анализа ---")
        print(f"Состояние чистоты: {prediction['cleanliness']['class']} (уверенность: {prediction['cleanliness']['confidence']:.2%})")
        print(f"Состояние целостности: {prediction['damage']['class']} (уверенность: {prediction['damage']['confidence']:.2%})")
        
        # Удаляем тестовое изображение
        import os
        if os.path.exists('test_image.jpg'):
            os.remove('test_image.jpg')
            
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

if __name__ == '__main__':
    # Для тестирования
    import sys
    if len(sys.argv) > 1:
        prediction = predict(sys.argv[1])
        print("\n--- Результат анализа ---")
        print(f"Состояние чистоты: {prediction['cleanliness']['class']} (уверенность: {prediction['cleanliness']['confidence']:.2%})")
        print(f"Состояние целостности: {prediction['damage']['class']} (уверенность: {prediction['damage']['confidence']:.2%})")
    else:
        # Автоматическое тестирование
        test_prediction()