import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import talib
from typing import List, Tuple
import joblib
import os

class PatternDataset(Dataset):
    def __init__(self, features: np.ndarray, labels: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.labels = torch.LongTensor(labels)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]

class PatternCNN(nn.Module):
    def __init__(self, input_dim: int, num_classes: int = 4):
        super(PatternCNN, self).__init__()
        
        self.conv1 = nn.Conv1d(1, 64, kernel_size=5, padding=2)
        self.conv2 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(128, 256, kernel_size=3, padding=1)
        
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.dropout = nn.Dropout(0.5)
        
        self.fc1 = nn.Linear(256, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_classes)
        
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        # Reshape for 1D convolution
        x = x.unsqueeze(1)
        
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.relu(self.conv3(x))
        
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        
        x = self.dropout(x)
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        
        return x

def extract_features(ohlc_data: pd.DataFrame, window_size: int = 50) -> np.ndarray:
    """Extract technical features from OHLC data."""
    features = []
    
    high = ohlc_data['high'].values
    low = ohlc_data['low'].values
    close = ohlc_data['close'].values
    volume = ohlc_data['volume'].values
    
    # Price features (normalized)
    price_features = []
    for i in range(len(close)):
        if i >= window_size:
            window_close = close[i-window_size:i]
            window_high = high[i-window_size:i]
            window_low = low[i-window_size:i]
            window_volume = volume[i-window_size:i]
            
            # Normalize prices by the first price in the window
            base_price = window_close
            norm_close = window_close / base_price
            norm_high = window_high / base_price
            norm_low = window_low / base_price
            
            # Normalize volume by max volume in window
            max_volume = np.max(window_volume)
            norm_volume = window_volume / max_volume if max_volume > 0 else window_volume
            
            # Combine all features
            window_features = np.concatenate([
                norm_close,
                norm_high,
                norm_low,
                norm_volume
            ])
            
            price_features.append(window_features)
    
    return np.array(price_features)

def create_pattern_labels(ohlc_data: pd.DataFrame, lookback: int = 20, lookahead: int = 10) -> List[int]:
    """Create pattern labels based on future price movement."""
    labels = []
    close = ohlc_data['close'].values
    
    for i in range(len(close)):
        if i >= lookback and i < len(close) - lookahead:
            current_price = close[i]
            future_prices = close[i+1:i+1+lookahead]
            
            if len(future_prices) == 0:
                labels.append(0)  # No pattern
                continue
            
            max_future = np.max(future_prices)
            min_future = np.min(future_prices)
            
            upward_move = (max_future - current_price) / current_price
            downward_move = (current_price - min_future) / current_price
            
            # Pattern classification
            if upward_move > 0.05:  # Strong upward movement (>5%)
                if downward_move < 0.02:  # Limited downside
                    labels.append(1)  # Bullish pattern
                else:
                    labels.append(2)  # Volatile pattern
            elif downward_move > 0.05:  # Strong downward movement (>5%)
                labels.append(3)  # Bearish pattern
            else:
                labels.append(0)  # No clear pattern
        else:
            labels.append(0)  # No pattern (insufficient data)
    
    return labels

def train_pattern_model():
    """Train the pattern recognition model."""
    
    # Load training data
    print("Loading training data...")
    data_path = "datasets/historical_data/combined_data.csv"
    
    if not os.path.exists(data_path):
        print(f"Training data not found at {data_path}")
        print("Please run data collection script first")
        return
    
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Extract features and labels
    print("Extracting features...")
    features = extract_features(df, window_size=50)
    labels = create_pattern_labels(df, lookback=50, lookahead=10)
    
    # Align features and labels
    min_len = min(len(features), len(labels))
    features = features[-min_len:]
    labels = labels[-min_len:]
    
    if len(features) == 0:
        print("No features extracted. Please check your data.")
        return
    
    # Split data
    print(f"Dataset size: {len(features)} samples")
    print(f"Feature dimension: {features.shape[48]}")
    
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2, stratify=labels, random_state=42
    )
    
    # Create datasets
    train_dataset = PatternDataset(X_train, y_train)
    test_dataset = PatternDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Initialize model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    model = PatternCNN(input_dim=features.shape[48], num_classes=4).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
    
    # Training loop
    print("Starting training...")
    num_epochs = 50
    best_accuracy = 0.0
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        
        for batch_features, batch_labels in train_loader:
            batch_features = batch_features.to(device)
            batch_labels = batch_labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_features)
            loss = criterion(outputs, batch_labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        # Validation
        model.eval()
        all_predictions = []
        all_labels = []
        
        with torch.no_grad():
            for batch_features, batch_labels in test_loader:
                batch_features = batch_features.to(device)
                batch_labels = batch_labels.to(device)
                
                outputs = model(batch_features)
                predictions = torch.argmax(outputs, dim=1)
                
                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(batch_labels.cpu().numpy())
        
        accuracy = accuracy_score(all_labels, all_predictions)
        precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_predictions, average='weighted')
        
        print(f"Epoch {epoch+1}/{num_epochs}:")
        print(f"  Train Loss: {train_loss/len(train_loader):.4f}")
        print(f"  Test Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")
        
        # Save best model
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            torch.save({
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': accuracy,
                'epoch': epoch
            }, 'models/pattern_recognition_model.pth')
            print(f"  New best model saved with accuracy: {accuracy:.4f}")
        
        scheduler.step()
    
    print(f"\nTraining completed. Best accuracy: {best_accuracy:.4f}")

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    os.makedirs("models", exist_ok=True)
    os.makedirs("datasets/historical_data", exist_ok=True)
    
    train_pattern_model()
