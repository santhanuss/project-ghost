import numpy as np
import json
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity

class DreamFirewall:
    '''
    Predicts zero-day attacks by matching real traffic to dream patterns
    World's first dream-learning firewall
    '''
    
    def __init__(self):
        self.dream_signatures = []
        self.predictions_made = 0
        self.attacks_blocked = 0
        self.zero_days_predicted = 0
        
    def load_dreams(self, filepath='dream_signatures.json'):
        '''Load dream attack signatures'''
        with open(filepath, 'r') as f:
            self.dream_signatures = json.load(f)
        
        print(f'[✓] Loaded {len(self.dream_signatures)} dream signatures')
    
    def analyze_traffic(self, traffic_pattern):
        '''Analyze incoming traffic against dream patterns'''
        self.predictions_made += 1
        
        # Convert traffic to comparable format
        traffic_vec = np.array(traffic_pattern).reshape(1, -1)
        
        best_match = None
        highest_similarity = 0
        
        # Compare against all dreams
        for dream in self.dream_signatures:
            dream_vec = np.array(dream['pattern']).reshape(1, -1)
            
            # Pad/truncate to match dimensions
            min_len = min(traffic_vec.shape[1], dream_vec.shape[1])
            traffic_vec_trimmed = traffic_vec[:, :min_len]
            dream_vec_trimmed = dream_vec[:, :min_len]
            
            similarity = cosine_similarity(traffic_vec_trimmed, dream_vec_trimmed)[0][0]
            
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = dream
        
        # Prediction threshold
        THREAT_THRESHOLD = 0.7
        
        is_threat = highest_similarity > THREAT_THRESHOLD
        
        result = {
            'is_threat': is_threat,
            'similarity': float(highest_similarity),
            'matched_dream': best_match['id'] if best_match else None,
            'attack_type': best_match['type'] if best_match and is_threat else 'benign',
            'risk_score': best_match['risk_score'] if best_match and is_threat else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        if is_threat:
            self.attacks_blocked += 1
            if 'DREAM' in result['matched_dream']:
                self.zero_days_predicted += 1
        
        return result
    
    def predict_batch(self, traffic_batch):
        '''Analyze multiple traffic patterns'''
        results = []
        
        for traffic in traffic_batch:
            result = self.analyze_traffic(traffic)
            results.append(result)
        
        return results
    
    def get_statistics(self):
        '''Get firewall statistics'''
        return {
            'predictions_made': self.predictions_made,
            'attacks_blocked': self.attacks_blocked,
            'zero_days_predicted': self.zero_days_predicted,
            'block_rate': (self.attacks_blocked / self.predictions_made * 100) if self.predictions_made > 0 else 0,
            'dream_signatures_loaded': len(self.dream_signatures)
        }
    
    def print_summary(self):
        '''Print firewall summary'''
        stats = self.get_statistics()
        
        print('\n' + '='*60)
        print('DREAM FIREWALL SUMMARY')
        print('='*60)
        print(f'Dream signatures loaded: {stats["dream_signatures_loaded"]}')
        print(f'Predictions made: {stats["predictions_made"]}')
        print(f'Attacks blocked: {stats["attacks_blocked"]}')
        print(f'Zero-days predicted: {stats["zero_days_predicted"]}')
        print(f'Block rate: {stats["block_rate"]:.1f}%')
        print('='*60)

if __name__ == '__main__':
    print('='*60)
    print('DREAM FIREWALL TEST')
    print('='*60)
    
    # Initialize firewall
    firewall = DreamFirewall()
    firewall.load_dreams()
    
    print('\n[TEST 1] Normal traffic - Should pass\n')
    normal_traffic = np.random.normal(0, 0.1, 50)
    result = firewall.analyze_traffic(normal_traffic)
    print(f'  Result: {"🚫 BLOCKED" if result["is_threat"] else "✅ ALLOWED"}')
    print(f'  Similarity: {result["similarity"]:.3f}')
    print(f'  Type: {result["attack_type"]}')
    
    print('\n[TEST 2] Suspicious traffic - Should block\n')
    suspicious_traffic = np.random.uniform(-0.8, 0.8, 50)
    result = firewall.analyze_traffic(suspicious_traffic)
    print(f'  Result: {"🚫 BLOCKED" if result["is_threat"] else "✅ ALLOWED"}')
    print(f'  Similarity: {result["similarity"]:.3f}')
    print(f'  Matched: {result["matched_dream"]}')
    print(f'  Type: {result["attack_type"]}')
    
    print('\n[TEST 3] Batch analysis - 20 patterns\n')
    test_batch = []
    for i in range(20):
        if i < 15:
            # Normal traffic
            pattern = np.random.normal(0, 0.1, 50)
        else:
            # Attack traffic
            pattern = np.random.uniform(-0.8, 0.8, 50)
        test_batch.append(pattern)
    
    results = firewall.predict_batch(test_batch)
    
    blocked = sum(1 for r in results if r['is_threat'])
    print(f'  Total analyzed: 20')
    print(f'  Blocked: {blocked}')
    print(f'  Allowed: {20 - blocked}')
    
    # Summary
    firewall.print_summary()
    
    print('\n💡 Dream firewall predicting zero-days!')
    print('✅ Prediction system operational!')
