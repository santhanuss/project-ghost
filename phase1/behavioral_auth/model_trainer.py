import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import json
from pathlib import Path

class BehavioralAuthModel:
    
    def __init__(self, timesteps=10, features=9):
        self.timesteps = timesteps
        self.features = features
        self.model = None
        self.baseline = None
    
    def build_model(self):
        print('\n[*] Building model architecture...')
        
        inputs = keras.Input(shape=(self.timesteps, self.features), name='input')
        
        x = layers.LSTM(64, return_sequences=True, name='encoder_lstm1')(inputs)
        x = layers.Dropout(0.2, name='encoder_dropout1')(x)
        encoded = layers.LSTM(32, return_sequences=False, name='encoder_lstm2')(x)
        
        x = layers.RepeatVector(self.timesteps, name='decoder_repeat')(encoded)
        x = layers.LSTM(32, return_sequences=True, name='decoder_lstm1')(x)
        x = layers.Dropout(0.2, name='decoder_dropout1')(x)
        x = layers.LSTM(64, return_sequences=True, name='decoder_lstm2')(x)
        
        outputs = layers.TimeDistributed(
            layers.Dense(self.features, name='output_dense'),
            name='output'
        )(x)
        
        self.model = keras.Model(inputs, outputs, name='BehavioralAuth')
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )
        
        print('[✓] Model built successfully')
        total_params = self.model.count_params()
        print(f'    Total parameters: {total_params:,}')
        
        return self.model
    
    def train(self, training_data, epochs=30, batch_size=16):
        print('\n' + '='*60)
        print('TRAINING BEHAVIORAL AUTHENTICATION MODEL')
        print('='*60)
        print(f'\nDataset shape: {training_data.shape}')
        print(f'Training samples: {len(training_data)}')
        print(f'Epochs: {epochs}')
        print('\nThis will take 2-3 minutes...\n')
        
        if self.model is None:
            self.build_model()
        
        history = self.model.fit(
            training_data,
            training_data,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        print('\n[*] Calculating baseline error...')
        reconstructed = self.model.predict(training_data, verbose=0)
        errors = np.mean(np.abs(training_data - reconstructed), axis=(1, 2))
        
        self.baseline = {
            'mean_error': float(np.mean(errors)),
            'std_error': float(np.std(errors)),
            'threshold': float(np.mean(errors) + 2 * np.std(errors))
        }
        
        print('\n' + '='*60)
        print('TRAINING COMPLETE!')
        print('='*60)
        print('Baseline Reconstruction Error:')
        mean_err = self.baseline['mean_error']
        std_err = self.baseline['std_error']
        print(f'  Mean: {mean_err:.6f}')
        print(f'  Std:  {std_err:.6f}')
        
        return history
    
    def authenticate(self, sample, threshold_multiplier=0.03):
        if self.model is None or self.baseline is None:
            raise ValueError('Model not trained!')
        
        reconstructed = self.model.predict(sample, verbose=0)
        error = np.mean(np.abs(sample - reconstructed))
        
        expected = self.baseline['mean_error']
        deviation = abs(error - expected) / expected
        
        is_authentic = deviation < threshold_multiplier
        
        return is_authentic, deviation
    
    def save(self, filepath='../models/behavioral_auth'):
        Path('../models').mkdir(exist_ok=True)
        
        model_path = f'{filepath}_model.keras'
        baseline_path = f'{filepath}_baseline.json'
        
        self.model.save(model_path)
        
        with open(baseline_path, 'w') as f:
            json.dump(self.baseline, f, indent=2)
        
        print(f'\n[✓] Model saved:')
        print(f'    {model_path}')
        print(f'    {baseline_path}')

if __name__ == '__main__':
    print('='*60)
    print('PROJECT GHOST - PHASE 1')
    print('Behavioral Biometric Authentication')
    print('='*60)
    
    print('\n[1/4] Loading training data...')
    
    dataset_path = Path('../data/training_dataset.npy')
    
    if not dataset_path.exists():
        print('[!] Error: training_dataset.npy not found')
        print('[!] Run feature_extractor.py first')
        exit(1)
    
    dataset = np.load(dataset_path)
    print(f'[✓] Loaded dataset: {dataset.shape}')
    
    print('\n[2/4] Building and training model...')
    
    model = BehavioralAuthModel(timesteps=10, features=9)
    history = model.train(dataset, epochs=30, batch_size=16)
    
    print('\n[3/4] Saving model...')
    model.save('../models/behavioral_auth')
    
    print('\n[4/4] Testing authentication...')
    
    normal_sample = dataset[0:1]
    is_auth, deviation = model.authenticate(normal_sample)
    
    print(f'\nTest 1 - Normal behavior:')
    print(f'  ✅ Authenticated: {is_auth}')
    print(f'  📊 Deviation: {deviation*100:.2f}%')
    
    anomaly = normal_sample.copy()
    anomaly += np.random.normal(0, 0.5, anomaly.shape)
    is_auth, deviation = model.authenticate(anomaly)
    
    print(f'\nTest 2 - Anomalous behavior:')
    print(f'  ❌ Authenticated: {is_auth}')
    print(f'  📊 Deviation: {deviation*100:.2f}%')
    
    print('\n' + '='*60)
    print('🎉 PHASE 1 - LAYER 2 COMPLETE!')
    print('='*60)
    print('\nWhat you built:')
    print('  ✅ LSTM neural network')
    print('  ✅ Behavioral authentication')
    print('  ✅ Model saved and ready')
    print('\nFiles created:')
    print('  📄 models/behavioral_auth_model.keras')
    print('  📄 models/behavioral_auth_baseline.json')
    print('='*60)
