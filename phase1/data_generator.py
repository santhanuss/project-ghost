import json
import random
import time
import math

def generate_mouse_data(num_events=5000, output_file='data/mouse_synthetic.jsonl'):
    print(f'[*] Generating {num_events} mouse events...')
    
    data = []
    base_time = time.time()
    x, y = 500, 500
    prev_time = base_time
    
    for i in range(num_events):
        # More realistic movement
        dx = random.gauss(0, 5)  # Smaller movements
        dy = random.gauss(0, 5)
        
        # Natural hand tremor
        tremor_x = 0.5 * math.sin(2 * math.pi * 10 * i * 0.016)
        tremor_y = 0.5 * math.cos(2 * math.pi * 10 * i * 0.016)
        
        x += dx + tremor_x
        y += dy + tremor_y
        
        x = max(0, min(1920, x))
        y = max(0, min(1080, y))
        
        # Realistic timing (60 Hz)
        current_time = prev_time + 0.016 + random.gauss(0, 0.002)
        interval = current_time - prev_time
        prev_time = current_time
        
        event = {
            'timestamp': current_time,
            'x': int(x),
            'y': int(y),
            'interval': interval,
            'type': 'move'
        }
        
        data.append(event)
        
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
    base_time = time.time()
    avg_flight_time = 0.15
    current_time = base_time
    
    for i in range(num_events):
        if random.random() < 0.9:
            flight_time = random.gauss(avg_flight_time, 0.05)
        else:
            flight_time = random.uniform(0.5, 2.0)
        
        flight_time = max(0.05, flight_time)
        current_time += flight_time
        
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
    print('\nGenerating realistic behavioral data...\n')
    
    mouse_count = generate_mouse_data(num_events=5000)
    key_count = generate_keyboard_data(num_events=2000)
    
    print('\n' + '='*60)
    print('GENERATION COMPLETE')
    print('='*60)
    print(f'Mouse events: {mouse_count}')
    print(f'Keyboard events: {key_count}')
    print('\nNext: Retrain model with better data')
    print('='*60)
