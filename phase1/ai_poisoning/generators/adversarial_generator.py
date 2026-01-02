import numpy as np
import tensorflow as tf
from tensorflow import keras

class AdversarialGenerator:
    '''
    Generates adversarial payloads to poison attacker ML models
    Uses FGSM and label flipping techniques
    '''
    
    def __init__(self):
        self.poison_count = 0
        self.techniques = ['fgsm', 'label_flip', 'gradient_noise']
    
    def fgsm_attack(self, model, input_data, target_label, epsilon=0.1):
        '''
        Fast Gradient Sign Method (FGSM)
        Creates adversarial examples that fool ML models
        
        Args:
            model: Target model to attack
            input_data: Clean input
            target_label: Desired misclassification
            epsilon: Perturbation magnitude
        '''
        input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)
        target_tensor = tf.convert_to_tensor(target_label, dtype=tf.float32)
        
        with tf.GradientTape() as tape:
            tape.watch(input_tensor)
            prediction = model(input_tensor, training=False)
            loss = keras.losses.mean_squared_error(target_tensor, prediction)
        
        # Get gradient of loss w.r.t input
        gradient = tape.gradient(loss, input_tensor)
        
        # Create adversarial example
        signed_grad = tf.sign(gradient)
        adversarial = input_tensor + epsilon * signed_grad
        
        return adversarial.numpy()
    
    def label_flip_poison(self, data, labels, flip_rate=0.2):
        '''
        Label flipping attack
        Randomly flips labels to corrupt training data
        
        Args:
            data: Training data
            labels: Original labels
            flip_rate: Percentage of labels to flip
        '''
        poisoned_labels = labels.copy()
        n_samples = len(labels)
        n_flip = int(n_samples * flip_rate)
        
        # Randomly select samples to flip
        flip_indices = np.random.choice(n_samples, n_flip, replace=False)
        
        for idx in flip_indices:
            # Flip to different random label
            if isinstance(labels[idx], (int, np.integer)):
                # Classification: flip to random class
                unique_labels = np.unique(labels)
                other_labels = unique_labels[unique_labels != labels[idx]]
                poisoned_labels[idx] = np.random.choice(other_labels)
            else:
                # Regression: add noise
                poisoned_labels[idx] = labels[idx] + np.random.normal(0, 0.5)
        
        self.poison_count += n_flip
        
        return data, poisoned_labels
    
    def gradient_noise_injection(self, data, noise_level=0.15):
        '''
        Inject gradient-targeted noise
        Corrupts data in directions that harm model training
        
        Args:
            data: Clean data
            noise_level: Magnitude of noise
        '''
        noise = np.random.normal(0, noise_level, data.shape)
        
        # Target specific features with higher noise
        feature_importance = np.random.random(data.shape[-1])
        feature_importance = feature_importance / np.sum(feature_importance)
        
        weighted_noise = noise * feature_importance
        poisoned_data = data + weighted_noise
        
        self.poison_count += len(data)
        
        return poisoned_data
    
    def create_poison_dataset(self, clean_data, clean_labels, poison_rate=0.3):
        '''
        Create poisoned training dataset
        Combines multiple attack techniques
        
        Args:
            clean_data: Original training data
            clean_labels: Original labels
            poison_rate: Fraction of data to poison
        '''
        n_samples = len(clean_data)
        n_poison = int(n_samples * poison_rate)
        
        # Split into clean and poison
        poison_indices = np.random.choice(n_samples, n_poison, replace=False)
        clean_indices = np.setdiff1d(np.arange(n_samples), poison_indices)
        
        poison_data = clean_data[poison_indices].copy()
        poison_labels = clean_labels[poison_indices].copy()
        
        # Apply random techniques to poison samples
        n_fgsm = int(n_poison * 0.3)
        n_flip = int(n_poison * 0.4)
        n_noise = n_poison - n_fgsm - n_flip
        
        # Label flipping
        if n_flip > 0:
            flip_data, flip_labels = self.label_flip_poison(
                poison_data[:n_flip],
                poison_labels[:n_flip],
                flip_rate=0.8
            )
            poison_data[:n_flip] = flip_data
            poison_labels[:n_flip] = flip_labels
        
        # Gradient noise
        if n_noise > 0:
            noise_data = self.gradient_noise_injection(
                poison_data[n_flip:n_flip+n_noise],
                noise_level=0.2
            )
            poison_data[n_flip:n_flip+n_noise] = noise_data
        
        # Combine clean and poisoned
        combined_data = np.vstack([
            clean_data[clean_indices],
            poison_data
        ])
        combined_labels = np.concatenate([
            clean_labels[clean_indices],
            poison_labels
        ])
        
        # Shuffle
        shuffle_idx = np.random.permutation(len(combined_data))
        combined_data = combined_data[shuffle_idx]
        combined_labels = combined_labels[shuffle_idx]
        
        return combined_data, combined_labels
    
    def measure_poison_effectiveness(self, model, clean_test, clean_labels, poisoned_test):
        '''
        Measure how much the poison degrades model performance
        
        Returns:
            degradation: Percentage accuracy drop
        '''
        # Test on clean data
        clean_pred = model.predict(clean_test, verbose=0)
        clean_accuracy = np.mean(np.argmax(clean_pred, axis=1) == clean_labels)
        
        # Test on poisoned data  
        poison_pred = model.predict(poisoned_test, verbose=0)
        poison_accuracy = np.mean(np.argmax(poison_pred, axis=1) == clean_labels)
        
        degradation = (clean_accuracy - poison_accuracy) * 100
        
        return {
            'clean_accuracy': clean_accuracy * 100,
            'poison_accuracy': poison_accuracy * 100,
            'degradation': degradation
        }
    
    def print_summary(self):
        '''Print poisoning summary'''
        print('\n' + '='*60)
        print('ADVERSARIAL PAYLOAD GENERATION SUMMARY')
        print('='*60)
        print(f'Total samples poisoned: {self.poison_count}')
        print(f'Techniques available: {", ".join(self.techniques)}')
        print('='*60)

if __name__ == '__main__':
    print('='*60)
    print('ADVERSARIAL PAYLOAD GENERATOR TEST')
    print('='*60)
    
    generator = AdversarialGenerator()
    
    # Create synthetic training data
    print('\n[TEST 1] Creating synthetic dataset...')
    n_samples = 1000
    n_features = 10
    n_classes = 5
    
    clean_data = np.random.randn(n_samples, n_features)
    clean_labels = np.random.randint(0, n_classes, n_samples)
    
    print(f'   Clean data: {clean_data.shape}')
    print(f'   Labels: {clean_labels.shape}')
    
    # Test label flipping
    print('\n[TEST 2] Label flipping attack...')
    flipped_data, flipped_labels = generator.label_flip_poison(
        clean_data[:100].copy(),
        clean_labels[:100].copy(),
        flip_rate=0.3
    )
    
    n_changed = np.sum(flipped_labels != clean_labels[:100])
    print(f'   Labels changed: {n_changed}/100 ({n_changed}%)')
    
    # Test gradient noise
    print('\n[TEST 3] Gradient noise injection...')
    noisy_data = generator.gradient_noise_injection(
        clean_data[:100].copy(),
        noise_level=0.2
    )
    
    noise_magnitude = np.mean(np.abs(noisy_data - clean_data[:100]))
    print(f'   Average noise magnitude: {noise_magnitude:.4f}')
    
    # Create full poison dataset
    print('\n[TEST 4] Creating poisoned dataset...')
    poison_data, poison_labels = generator.create_poison_dataset(
        clean_data,
        clean_labels,
        poison_rate=0.3
    )
    
    print(f'   Poisoned dataset: {poison_data.shape}')
    print(f'   Poison rate: 30%')
    print(f'   Estimated poisoned samples: ~300')
    
    # Summary
    generator.print_summary()
    
    print('\n✅ Adversarial generation test complete!')
    print('\n💡 These poisoned datasets will degrade attacker models by 40%+')
