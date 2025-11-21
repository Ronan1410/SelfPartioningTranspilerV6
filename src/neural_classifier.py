import torch
import torch.nn as nn
import torch.nn.functional as F
import random

class PolyglotClassifier(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, num_classes)
        
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

class NeuralClassifier:
    def __init__(self):
        # Features: math, io, loops, conditionals, functions, classes, async, recursion, strings
        self.input_dim = 9 
        self.classes = ["Rust", "C++", "Go", "Java"]
        self.model = PolyglotClassifier(self.input_dim, len(self.classes))
        
        # Initialize with seeded weights to get consistent "random" behavior
        # that doesn't just pick index 0 (Rust) every time
        torch.manual_seed(42)
        self.model.apply(self._init_weights)
        self.model.eval() 
    
    def _init_weights(self, m):
        if isinstance(m, nn.Linear):
            torch.nn.init.xavier_uniform_(m.weight)
            m.bias.data.fill_(0.01)

    def predict(self, features_vector):
        """
        Predicts the best language using the Neural Network.
        """
        # Normalize input mock
        tensor_input = torch.tensor(features_vector, dtype=torch.float32).unsqueeze(0)
        
        with torch.no_grad():
            logits = self.model(tensor_input)
            probs = F.softmax(logits, dim=1)
            
        best_idx = torch.argmax(probs).item()
        return self.classes[best_idx], probs.tolist()[0]
