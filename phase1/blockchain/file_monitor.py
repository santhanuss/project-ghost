import time
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from integrity_blockchain import IntegrityBlockchain

class FileIntegrityMonitor(FileSystemEventHandler):
    '''Monitor file system and record changes to blockchain'''
    
    def __init__(self, blockchain, watch_path='.'):
        self.blockchain = blockchain
        self.watch_path = Path(watch_path).resolve()
        print(f'[*] Monitoring: {self.watch_path}')
        
        # Ignore these patterns
        self.ignore_patterns = [
            '__pycache__',
            '.git',
            '*.pyc',
            'blockchain.json',
            '*.log'
        ]
    
    def should_ignore(self, path):
        '''Check if file should be ignored'''
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
        return False
    
    def on_created(self, event):
        '''Handle file creation'''
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        print(f'\n[CREATE] {Path(event.src_path).name}')
        self.blockchain.add_file_change(event.src_path, 'create')
    
    def on_modified(self, event):
        '''Handle file modification'''
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        print(f'\n[MODIFY] {Path(event.src_path).name}')
        self.blockchain.add_file_change(event.src_path, 'modify')
    
    def on_deleted(self, event):
        '''Handle file deletion'''
        if event.is_directory or self.should_ignore(event.src_path):
            return
        
        print(f'\n[DELETE] {Path(event.src_path).name}')
        self.blockchain.add_file_change(event.src_path, 'delete')

def monitor_directory(watch_path='.', duration=60):
    '''
    Monitor directory for file changes
    
    Args:
        watch_path: Directory to monitor
        duration: How long to monitor (seconds)
    '''
    print('='*60)
    print('FILE INTEGRITY MONITOR')
    print('='*60)
    
    # Create or load blockchain
    blockchain = IntegrityBlockchain(difficulty=2)
    
    # Try to load existing chain
    blockchain_file = '../logs/blockchain.json'
    if Path(blockchain_file).exists():
        print(f'\n[*] Loading existing blockchain...')
        blockchain.load_chain(blockchain_file)
        is_valid, message = blockchain.verify_chain()
        print(f'    {message}')
    
    # Create monitor
    event_handler = FileIntegrityMonitor(blockchain, watch_path)
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=False)
    
    print(f'\n[✓] File monitoring started')
    print(f'    Watching: {Path(watch_path).resolve()}')
    print(f'    Duration: {duration} seconds')
    print(f'\n[*] Try creating, modifying, or deleting files...')
    print('[*] Press Ctrl+C to stop early\n')
    
    observer.start()
    
    try:
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(1)
            
            # Show countdown every 10 seconds
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                remaining = duration - elapsed
                print(f'[{elapsed}s] Still monitoring... ({remaining}s remaining)')
    
    except KeyboardInterrupt:
        print('\n[!] Monitoring stopped by user')
    
    observer.stop()
    observer.join()
    
    # Commit any pending changes
    if blockchain.pending_changes:
        print('\n[*] Committing final changes...')
        blockchain.commit_pending_changes()
    
    # Save blockchain
    print('\n[*] Saving blockchain...')
    blockchain.save_chain(blockchain_file)
    
    # Show summary
    blockchain.print_summary()
    
    return blockchain

if __name__ == '__main__':
    import sys
    
    # Get watch path from command line or use current directory
    watch_path = sys.argv[1] if len(sys.argv) > 1 else '../data'
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    # Create watch directory if it doesn't exist
    Path(watch_path).mkdir(parents=True, exist_ok=True)
    
    print(f'\nWill monitor: {Path(watch_path).resolve()}')
    print(f'Duration: {duration} seconds\n')
    
    blockchain = monitor_directory(watch_path, duration)
    
    print('\n✅ Monitoring complete!')
    print(f'   Total blocks: {len(blockchain.chain)}')
    print(f'   Files tracked: {len([c for b in blockchain.chain for c in b.data.get("changes", [])])}')
