import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import List, Dict
from src.parser import SourceSegment
from src.strategies.base import SplitStrategy
import random

class CodeSplitterModel(nn.Module):
    """
    A simple LSTM-based model to predict split points in code.
    """
    def __init__(self, vocab_size: int, embedding_dim: int, hidden_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Linear(hidden_dim * 2, 1) # Binary classification: Split or Not

    def forward(self, x):
        # x: [batch, seq_len]
        embedded = self.embedding(x)
        outputs, _ = self.lstm(embedded)
        # We want a prediction for the sequence (or per token, but let's say per line/segment representation)
        # For simplicity, let's assume we pool or take last state
        # But for "splitting", we usually want seq-to-seq labeling.
        # Let's assume we classify the whole segment as "needs split" or not.
        final_hidden = outputs[:, -1, :]
        prediction = torch.sigmoid(self.fc(final_hidden))
        return prediction

class NeuralStrategy(SplitStrategy):
    """Splits code based on a Neural Network classifier."""

    def __init__(self):
        # In a real scenario, we would load weights here.
        self.vocab_size = 1000
        self.model = CodeSplitterModel(self.vocab_size, 64, 128)
        self.model.eval() 

    def name(self) -> str:
        return "Neural Network Splitting"

    def apply(self, segment: SourceSegment) -> List[SourceSegment]:
        # 1. Preprocess code (tokenize) - Mocked
        # 2. Run inference
        # 3. Split based on result
        
        # Mock inference logic:
        # If the segment is long, the NN "detects" a split point.
        
        if len(segment.code) < 50:
            return [segment]
            
        with torch.no_grad():
            # Mock input tensor
            dummy_input = torch.randint(0, self.vocab_size, (1, 10)) 
            prob = self.model(dummy_input).item()
            
        # If probability is high, we force a split (mock logic: split in half)
        if prob > 0.5 or len(segment.code.splitlines()) > 15:
            lines = segment.code.splitlines()
            mid = len(lines) // 2
            
            part1_code = "\n".join(lines[:mid])
            part2_code = "\n".join(lines[mid:])
            
            seg1 = SourceSegment(
                id=f"{segment.id}_nn1",
                code=part1_code,
                start_line=segment.start_line,
                end_line=segment.start_line + mid - 1,
                tags=["neural_split"]
            )
            
            seg2 = SourceSegment(
                id=f"{segment.id}_nn2",
                code=part2_code,
                start_line=segment.start_line + mid,
                end_line=segment.end_line,
                tags=["neural_split"]
            )
            return [seg1, seg2]

        return [segment]
