import json
import random
import time
import math

def generate_mouse_data(num_events=5000, output_file='data/mouse_synthetic.jsonl'):
    print(f'[*] Generating {num_events} mouse events...')
    
    data = []
    base_time = time.time()
    x, y = 500.0, 500.0
    prev_time = base_time
    
    for i in range(num_events):
        # Realistic small movements (5-20 pixels)
        dx = random.gauss(0, 8)
        dy = random.gauss(0, 8)
        
        # Natural hand tremor (8-12 Hz, very subtle)
        tremor_x = 0.3 * math.sin(2 * math.pi * 10 * i * 0.016)
        tremor_y = 0.3 * math.cos(2 * math.pi * 10 * i * 0.016)
        
        x += dx + tremor_x
        y += dy + tremor_y
        
        # Keep on screen
        x = max(0, min(1920, x))
        y = max(0, min(1080, y))
        
        # Realistic timing: ~60 Hz (16ms intervals)
        interval = 0.016 + random.gauss(0, 0.003)
        interval = max(0.010, min(0.025, interval))  # Between 10-25ms
        
        current_time = prev_time + interval
        prev_time = current_time
        
        event = {
            'timestamp': current_time,
            'x': int(x),
            'y': int(y),
            'interval': interval,
            'type': 'move'
        }
        
        data.append(event)
        
        # Occasional clicks
        if random.random() < 0.05:
            click_event = {
                'timestamp': current_time,
                'x': int(x),
                'y': int(y),
                'button': 'Button.left',
                'pressed': True,
                'type': 'click'
            }
            data.append(click_event)
    
    with open(output_file, 'w') as f:
        for event in data:
            f.write(json.dumps(event) + '\n')
    
    print(f'[✓] Mouse data saved to {output_file}')
    return len(data)

def generate_keyboard_data(num_events=2000, output_file='data/keys_synthetic.jsonl'):
    print(f'[*] Generating {num_events} keyboard events...')
    
    data = []
    current_time = time.time()
    
    # Realistic typing speed: 60 WPM = ~200ms per keystroke
    avg_flight_time = 0.20
    
    for i in range(num_events):
        # 90% normal typing, 10% pauses (thinking)
        if random.random() < 0.9:
            # Normal typing with variation
            flight_time = random.gauss(avg_flight_time, 0.08)
            flight_time = max(0.05, min(0.6, flight_time))
        else:
            # Cognitive pause
            flight_time = random.uniform(0.8, 3.0)
        
        current_time += flight_time
        
        # Random key
        keys = 'abcdefghijklmnopqrstuvwxyz '
        key = random.choice(keys)
        
        event = {
            'timestamp': current_time,
            'key': key,
            'flight_time': flight_time,
            'type': 'press'
        }
        
        data.append(event)
    
    with open(output_file, 'w') as f:
        for event in data:
            f.write(json.dumps(event) + '\n')
    
    print(f'[✓] Keyboard data saved to {output_file}')
    return len(data)

if __name__ == '__main__':
    print('='*60)
    print('IMPROVED SYNTHETIC DATA GENERATOR')
    print('='*60)
    print('\nGenerating realistic behavioral data...')
    print('(Fixed: realistic speeds and timings)\n')
    
    mouse_count = generate_mouse_data(num_events=5000)
    key_count = generate_keyboard_data(num_events=2000)
    
    print('\n' + '='*60)
    print('GENERATION COMPLETE')
    print('='*60)
    print(f'Mouse events: {mouse_count}')
    print(f'Keyboard events: {key_count}')
    print('\nNext: Extract features and retrain')
    print('='*60)
