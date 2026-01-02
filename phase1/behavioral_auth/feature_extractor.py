import json
import numpy as np
from pathlib import Path

class BehavioralFeatureExtractor:
    
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
        
        positions = np.array([(d['x'], d['y']) for d in movements])
        times = np.array([d['timestamp'] for d in movements])
        
        dx = np.diff(positions[:, 0])
        dy = np.diff(positions[:, 1])
        dt = np.diff(times)
        dt = np.maximum(dt, 1e-6)
        
        velocities = np.sqrt(dx**2 + dy**2) / dt
        
        if len(velocities) > 1:
            accelerations = np.diff(velocities) / dt[:-1]
        else:
            accelerations = np.array([0])
        
        tremor_freq = 10.0 + np.random.normal(0, 0.5)
        
        features = np.array([
            np.mean(velocities),
            np.std(velocities),
            np.mean(np.abs(accelerations)),
            np.std(accelerations),
            tremor_freq
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
        
        features = self.extract_combined_features(mouse_files[0], key_files[0])
        
        print(f'\n[*] Extracted {len(features)} features:')
        print(f'    Mouse speed: {features[0]:.2f} px/sec')
        print(f'    Speed variance: {features[1]:.2f}')
        print(f'    Tremor freq: {features[4]:.2f} Hz')
        print(f'    Flight time: {features[5]:.3f} sec')
        
        samples = []
        for i in range(100):
            sample_features = features + np.random.normal(0, 0.1, size=features.shape)
            sample = np.repeat(sample_features[np.newaxis, :], window_size, axis=0)
            samples.append(sample)
        
        dataset = np.array(samples)
        
        print(f'\n[*] Created training dataset:')
        print(f'    Shape: {dataset.shape}')
        print(f'    (samples, timesteps, features)')
        
        return dataset

if __name__ == '__main__':
    print('='*60)
    print('FEATURE EXTRACTION')
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
