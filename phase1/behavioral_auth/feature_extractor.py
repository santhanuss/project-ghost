import json
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler

class BehavioralFeatureExtractor:
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def load_data(self, filepath):
        data = []
        with open(filepath, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        return data
    
    def extract_mouse_features(self, mouse_data):
        movements = [d for d in mouse_data if d.get('type') == 'move']
        
        if len(movements) < 10:
            return np.zeros(5)
        
        # Use intervals instead of absolute positions
        intervals = np.array([d['interval'] for d in movements[:100]])
        
        # Simple statistical features from intervals
        features = np.array([
            np.mean(intervals),           # Avg interval
            np.std(intervals),            # Interval variance
            np.median(intervals),         # Median interval
            np.percentile(intervals, 75), # 75th percentile
            10.0 + np.random.normal(0, 0.3)  # Simulated tremor freq
        ])
        
        return features
    
    def extract_keyboard_features(self, key_data):
        if len(key_data) < 5:
            return np.zeros(4)
        
        flight_times = np.array([d['flight_time'] for d in key_data if d['flight_time'] > 0])
        
        if len(flight_times) < 2:
            return np.zeros(4)
        
        pauses = flight_times[flight_times > 1.0]
        pause_ratio = len(pauses) / len(flight_times) if len(flight_times) > 0 else 0
        
        features = np.array([
            np.mean(flight_times),
            np.std(flight_times),
            np.median(flight_times),
            pause_ratio
        ])
        
        return features
    
    def extract_combined_features(self, mouse_file, key_file):
        mouse_data = self.load_data(mouse_file)
        key_data = self.load_data(key_file)
        
        mouse_features = self.extract_mouse_features(mouse_data)
        key_features = self.extract_keyboard_features(key_data)
        
        all_features = np.concatenate([mouse_features, key_features])
        
        return all_features
    
    def create_training_dataset(self, data_dir='../data', window_size=10):
        data_dir = Path(data_dir)
        
        mouse_files = list(data_dir.glob('mouse_*.jsonl'))
        key_files = list(data_dir.glob('keys_*.jsonl'))
        
        if not mouse_files or not key_files:
            print('[!] No data files found in', data_dir)
            return None
        
        print(f'[*] Found data files:')
        print(f'    Mouse: {mouse_files[0].name}')
        print(f'    Keys: {key_files[0].name}')
        
        # Extract base features
        features = self.extract_combined_features(mouse_files[0], key_files[0])
        
        print(f'\n[*] Extracted {len(features)} features (BEFORE normalization):')
        print(f'    Mouse interval avg: {features[0]:.6f}')
        print(f'    Mouse interval std: {features[1]:.6f}')
        print(f'    Tremor freq: {features[4]:.2f} Hz')
        print(f'    Key flight time: {features[5]:.3f} sec')
        
        # Create 100 samples with variations
        all_samples = []
        for i in range(100):
            sample_features = features + np.random.normal(0, 0.01, size=features.shape)
            all_samples.append(sample_features)
        
        # Normalize ALL features together
        all_samples = np.array(all_samples)
        normalized = self.scaler.fit_transform(all_samples)
        
        print(f'\n[*] After normalization:')
        print(f'    Mean: {np.mean(normalized):.6f}')
        print(f'    Std: {np.std(normalized):.6f}')
        print(f'    Range: [{np.min(normalized):.2f}, {np.max(normalized):.2f}]')
        
        # Reshape for LSTM: (samples, timesteps, features)
        samples = []
        for norm_features in normalized:
            sample = np.repeat(norm_features[np.newaxis, :], window_size, axis=0)
            samples.append(sample)
        
        dataset = np.array(samples)
        
        print(f'\n[*] Created training dataset:')
        print(f'    Shape: {dataset.shape}')
        print(f'    (samples, timesteps, features)')
        
        # Save scaler for later use
        import pickle
        with open('../models/feature_scaler.pkl', 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f'[✓] Feature scaler saved')
        
        return dataset

if __name__ == '__main__':
    print('='*60)
    print('FEATURE EXTRACTION (NORMALIZED)')
    print('='*60)
    
    extractor = BehavioralFeatureExtractor()
    dataset = extractor.create_training_dataset()
    
    if dataset is not None:
        np.save('../data/training_dataset.npy', dataset)
        
        print(f'\n[✓] Dataset saved to data/training_dataset.npy')
        print(f'[✓] Ready for model training!')
        print(f'\nNext: py model_trainer.py')
    else:
        print('\n[!] Error: Could not create dataset')
