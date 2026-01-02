import numpy as np
import time
from collections import defaultdict
from datetime import datetime

class AIReconDetector:
    '''
    Detects AI reconnaissance attempts
    Identifies when ML models are probing the system
    '''
    
    def __init__(self, threshold=10, time_window=60):
        self.threshold = threshold  # Suspicious requests per time window
        self.time_window = time_window  # Seconds
        self.request_log = defaultdict(list)
        self.suspicious_patterns = []
        self.detection_count = 0
    
    def log_request(self, source_ip, request_type, features):
        '''
        Log incoming request for analysis
        
        Args:
            source_ip: Source IP address
            request_type: Type of request (login, api, file_access)
            features: Request features for analysis
        '''
        timestamp = time.time()
        
        request = {
            'timestamp': timestamp,
            'type': request_type,
            'features': features,
            'ip': source_ip
        }
        
        self.request_log[source_ip].append(request)
        
        # Clean old requests outside time window
        cutoff_time = timestamp - self.time_window
        self.request_log[source_ip] = [
            r for r in self.request_log[source_ip] 
            if r['timestamp'] > cutoff_time
        ]
        
        # Check for reconnaissance
        is_recon = self.detect_reconnaissance(source_ip)
        
        return is_recon
    
    def detect_reconnaissance(self, source_ip):
        '''Detect if source is performing AI reconnaissance'''
        
        recent_requests = self.request_log[source_ip]
        
        if len(recent_requests) < 5:
            return False
        
        # Pattern 1: High frequency requests
        if len(recent_requests) > self.threshold:
            self.record_detection(source_ip, 'high_frequency', len(recent_requests))
            return True
        
        # Pattern 2: Sequential feature probing
        request_types = [r['type'] for r in recent_requests[-10:]]
        unique_types = len(set(request_types))
        
        if unique_types >= 5:  # Probing multiple endpoints
            self.record_detection(source_ip, 'endpoint_scanning', unique_types)
            return True
        
        # Pattern 3: Automated timing patterns
        if len(recent_requests) >= 5:
            intervals = []
            for i in range(1, min(6, len(recent_requests))):
                interval = recent_requests[i]['timestamp'] - recent_requests[i-1]['timestamp']
                intervals.append(interval)
            
            # If intervals are too consistent (automated)
            if len(intervals) > 2:
                std_dev = np.std(intervals)
                if std_dev < 0.1:  # Very consistent timing = bot
                    self.record_detection(source_ip, 'automated_timing', std_dev)
                    return True
        
        # Pattern 4: Feature boundary probing
        if self.detect_boundary_probing(recent_requests):
            self.record_detection(source_ip, 'boundary_probing', len(recent_requests))
            return True
        
        return False
    
    def detect_boundary_probing(self, requests):
        '''Detect if attacker is probing model boundaries'''
        
        if len(requests) < 5:
            return False
        
        # Check if features span wide ranges (probing)
        feature_ranges = defaultdict(list)
        
        for request in requests[-10:]:
            for key, value in request['features'].items():
                if isinstance(value, (int, float)):
                    feature_ranges[key].append(value)
        
        # If any feature has very wide range, it's probing
        for feature, values in feature_ranges.items():
            if len(values) >= 3:
                range_span = max(values) - min(values)
                mean_val = np.mean(values)
                
                if mean_val != 0 and range_span / abs(mean_val) > 5:
                    return True
        
        return False
    
    def record_detection(self, source_ip, pattern_type, confidence):
        '''Record a reconnaissance detection'''
        
        detection = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_ip': source_ip,
            'pattern': pattern_type,
            'confidence': confidence,
            'request_count': len(self.request_log[source_ip])
        }
        
        self.suspicious_patterns.append(detection)
        self.detection_count += 1
        
        print(f'\n🚨 AI RECONNAISSANCE DETECTED!')
        print(f'   Source: {source_ip}')
        print(f'   Pattern: {pattern_type}')
        print(f'   Confidence: {confidence}')
        print(f'   Requests: {detection["request_count"]} in last {self.time_window}s')
    
    def get_statistics(self):
        '''Get detection statistics'''
        
        total_sources = len(self.request_log)
        total_requests = sum(len(reqs) for reqs in self.request_log.values())
        
        pattern_counts = defaultdict(int)
        for detection in self.suspicious_patterns:
            pattern_counts[detection['pattern']] += 1
        
        return {
            'total_sources': total_sources,
            'total_requests': total_requests,
            'detections': self.detection_count,
            'patterns': dict(pattern_counts),
            'detection_rate': self.detection_count / total_sources if total_sources > 0 else 0
        }
    
    def print_summary(self):
        '''Print detection summary'''
        
        stats = self.get_statistics()
        
        print('\n' + '='*60)
        print('AI RECONNAISSANCE DETECTION SUMMARY')
        print('='*60)
        print(f'Total sources monitored: {stats["total_sources"]}')
        print(f'Total requests: {stats["total_requests"]}')
        print(f'Reconnaissance detected: {stats["detections"]}')
        print(f'Detection rate: {stats["detection_rate"]*100:.1f}%')
        
        if stats['patterns']:
            print('\nDetection patterns:')
            for pattern, count in stats['patterns'].items():
                print(f'  {pattern}: {count}')
        
        if self.suspicious_patterns:
            print(f'\nRecent detections:')
            for detection in self.suspicious_patterns[-5:]:
                print(f'  {detection["timestamp"]} - {detection["source_ip"]}')
                print(f'    Pattern: {detection["pattern"]}')
        
        print('='*60)

if __name__ == '__main__':
    print('='*60)
    print('AI RECONNAISSANCE DETECTOR TEST')
    print('='*60)
    
    detector = AIReconDetector(threshold=10, time_window=30)
    
    print('\n[TEST 1] Simulating normal user behavior...\n')
    
    # Normal user - slow, varied requests
    for i in range(5):
        detector.log_request(
            '192.168.1.100',
            'login',
            {'username_length': 8, 'password_attempts': 1}
        )
        time.sleep(0.5)
    
    print('\n[TEST 2] Simulating AI reconnaissance attack...\n')
    
    # Attacker - rapid, systematic probing
    attack_ip = '10.0.0.50'
    
    # High frequency requests
    for i in range(15):
        detector.log_request(
            attack_ip,
            f'endpoint_{i % 6}',
            {'param': i * 10, 'value': i * 100}
        )
        time.sleep(0.05)  # Very fast, automated timing
    
    print('\n[TEST 3] Simulating boundary probing...\n')
    
    # Boundary probing attack
    probe_ip = '10.0.0.51'
    
    for i in range(8):
        detector.log_request(
            probe_ip,
            'api_call',
            {
                'age': -100 + (i * 50),  # Wide range probing
                'amount': 1 + (i * 1000)  # Boundary testing
            }
        )
        time.sleep(0.1)
    
    # Show results
    detector.print_summary()
    
    print('\n✅ Reconnaissance detection test complete!')
