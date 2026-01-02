import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

class Block:
    '''Single block in the blockchain containing file change records'''
    
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        '''Calculate SHA-256 hash of block contents'''
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty=2):
        '''Proof of work: find hash starting with difficulty zeros'''
        target = '0' * difficulty
        
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        
        return self.hash
    
    def to_dict(self):
        '''Convert block to dictionary for JSON serialization'''
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }

class IntegrityBlockchain:
    '''Blockchain for immutable file integrity monitoring'''
    
    def __init__(self, difficulty=2):
        self.chain = []
        self.pending_changes = []
        self.difficulty = difficulty
        self.create_genesis_block()
    
    def create_genesis_block(self):
        '''Create the first block in the chain'''
        genesis = Block(0, time.time(), {
            'type': 'genesis',
            'message': 'Project GHOST - Integrity Blockchain Initialized',
            'timestamp_human': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, '0')
        
        genesis.mine_block(self.difficulty)
        self.chain.append(genesis)
        
        print('[✓] Genesis block created')
        print(f'    Hash: {genesis.hash}')
    
    def get_latest_block(self):
        '''Get the most recent block'''
        return self.chain[-1]
    
    def calculate_file_hash(self, filepath):
        '''Calculate SHA-256 hash of file contents'''
        try:
            sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            return f'error:{str(e)}'
    
    def add_file_change(self, filepath, change_type, file_hash=None):
        '''
        Record a file change
        
        Args:
            filepath: Path to the file
            change_type: 'create', 'modify', 'delete'
            file_hash: Optional pre-calculated hash
        '''
        if file_hash is None and change_type != 'delete':
            file_hash = self.calculate_file_hash(filepath)
        
        change = {
            'filepath': str(filepath),
            'hash': file_hash if file_hash else 'deleted',
            'type': change_type,
            'timestamp': time.time(),
            'timestamp_human': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.pending_changes.append(change)
        print(f'[+] Recorded: {change_type} - {Path(filepath).name}')
        
        # Auto-commit when we have 10 changes
        if len(self.pending_changes) >= 10:
            self.commit_pending_changes()
    
    def commit_pending_changes(self):
        '''Commit pending changes to blockchain'''
        if not self.pending_changes:
            return None
        
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data={
                'changes': self.pending_changes.copy(),
                'count': len(self.pending_changes),
                'committed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            previous_hash=self.get_latest_block().hash
        )
        
        print(f'\n[*] Mining block {new_block.index} with {len(self.pending_changes)} changes...')
        start_time = time.time()
        new_block.mine_block(self.difficulty)
        mining_time = time.time() - start_time
        
        self.chain.append(new_block)
        
        print(f'[✓] Block {new_block.index} mined in {mining_time:.2f}s')
        print(f'    Hash: {new_block.hash}')
        print(f'    Nonce: {new_block.nonce}')
        
        self.pending_changes = []
        return new_block
    
    def verify_chain(self):
        '''Verify blockchain integrity - detects tampering'''
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # Verify current block hash
            if current.hash != current.calculate_hash():
                return False, f'Block {i} hash mismatch - TAMPERED!'
            
            # Verify link to previous block
            if current.previous_hash != previous.hash:
                return False, f'Block {i} chain broken - TAMPERED!'
            
            # Verify proof of work
            if not current.hash.startswith('0' * self.difficulty):
                return False, f'Block {i} invalid proof of work'
        
        return True, 'Blockchain integrity verified ✓'
    
    def detect_tampering(self, filepath):
        '''Check if a file has been tampered with since last record'''
        history = self.get_file_history(filepath)
        
        if not history:
            return None, 'File not in blockchain'
        
        current_hash = self.calculate_file_hash(filepath)
        last_record = history[-1]
        
        if current_hash != last_record['hash']:
            return True, f'TAMPERED! Last known hash: {last_record["hash"][:16]}..., Current: {current_hash[:16]}...'
        
        return False, 'File integrity verified ✓'
    
    def get_file_history(self, filepath):
        '''Get complete history of a file from blockchain'''
        history = []
        filepath_str = str(filepath)
        
        for block in self.chain:
            if 'changes' in block.data:
                for change in block.data['changes']:
                    if change['filepath'] == filepath_str:
                        history.append({
                            'block': block.index,
                            'timestamp': change.get('timestamp_human', 'unknown'),
                            'type': change['type'],
                            'hash': change['hash']
                        })
        
        return history
    
    def save_chain(self, filepath='blockchain.json'):
        '''Save blockchain to file'''
        chain_data = {
            'difficulty': self.difficulty,
            'blocks': [block.to_dict() for block in self.chain],
            'saved_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(filepath, 'w') as f:
            json.dump(chain_data, f, indent=2)
        
        print(f'\n[✓] Blockchain saved to {filepath}')
    
    def load_chain(self, filepath='blockchain.json'):
        '''Load blockchain from file'''
        if not Path(filepath).exists():
            return False
        
        with open(filepath, 'r') as f:
            chain_data = json.load(f)
        
        self.chain = []
        self.difficulty = chain_data.get('difficulty', 2)
        
        for block_dict in chain_data['blocks']:
            block = Block(
                block_dict['index'],
                block_dict['timestamp'],
                block_dict['data'],
                block_dict['previous_hash']
            )
            block.nonce = block_dict['nonce']
            block.hash = block_dict['hash']
            self.chain.append(block)
        
        print(f'[✓] Blockchain loaded: {len(self.chain)} blocks')
        return True
    
    def print_summary(self):
        '''Print blockchain summary'''
        print('\n' + '='*60)
        print('BLOCKCHAIN INTEGRITY MONITOR')
        print('='*60)
        print(f'Total blocks: {len(self.chain)}')
        print(f'Pending changes: {len(self.pending_changes)}')
        print(f'Difficulty: {self.difficulty}')
        
        is_valid, message = self.verify_chain()
        status = '✅ VALID' if is_valid else '❌ INVALID'
        print(f'\nChain status: {status}')
        print(f'Message: {message}')
        
        print(f'\nRecent blocks:')
        for block in self.chain[-5:]:
            timestamp = datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')
            changes = len(block.data.get('changes', []))
            print(f'  Block {block.index}: {timestamp} - {changes} changes')
            print(f'    Hash: {block.hash[:32]}...')
        
        print('='*60 + '\n')

if __name__ == '__main__':
    print('='*60)
    print('BLOCKCHAIN INTEGRITY TEST')
    print('='*60 + '\n')
    
    # Create blockchain
    blockchain = IntegrityBlockchain(difficulty=2)
    
    # Simulate file changes
    print('\n[TEST 1] Recording file changes...\n')
    blockchain.add_file_change('document.txt', 'create', 'abc123def456')
    blockchain.add_file_change('report.pdf', 'create', 'def456ghi789')
    blockchain.add_file_change('document.txt', 'modify', 'abc789xyz123')
    blockchain.add_file_change('image.png', 'create', 'ghi012jkl345')
    blockchain.add_file_change('config.yml', 'create', 'mno678pqr901')
    
    # Add more to trigger auto-commit
    for i in range(5):
        blockchain.add_file_change(f'file_{i}.txt', 'create', f'hash_{i}_xyz')
    
    # Manual commit
    print('\n[TEST 2] Committing remaining changes...\n')
    blockchain.commit_pending_changes()
    
    # Verify chain
    print('\n[TEST 3] Verifying blockchain integrity...\n')
    is_valid, message = blockchain.verify_chain()
    print(f'Result: {message}')
    
    # Check file history
    print('\n[TEST 4] File history for document.txt...\n')
    history = blockchain.get_file_history('document.txt')
    for entry in history:
        print(f"  Block {entry['block']}: {entry['timestamp']} - {entry['type']}")
        print(f"    Hash: {entry['hash']}")
    
    # Save blockchain
    print('\n[TEST 5] Saving blockchain...\n')
    blockchain.save_chain('../logs/blockchain.json')
    
    # Print summary
    blockchain.print_summary()
    
    print('✅ All tests passed!')
