from integrity_blockchain import IntegrityBlockchain
from pathlib import Path

print('='*60)
print('BLOCKCHAIN FILE AUDIT')
print('='*60)

# Load blockchain
blockchain = IntegrityBlockchain()
blockchain.load_chain('../logs/blockchain.json')

print('\n[1] Blockchain Status')
is_valid, message = blockchain.verify_chain()
print(f'    {message}')
print(f'    Total blocks: {len(blockchain.chain)}')

# Extract all tracked files
print('\n[2] All Tracked Files:\n')
tracked_files = {}

for block in blockchain.chain:
    if 'changes' in block.data:
        for change in block.data['changes']:
            filepath = change['filepath']
            if filepath not in tracked_files:
                tracked_files[filepath] = []
            tracked_files[filepath].append({
                'block': block.index,
                'type': change['type'],
                'hash': change['hash'],
                'time': change.get('timestamp_human', 'unknown')
            })

for filepath, changes in tracked_files.items():
    filename = Path(filepath).name
    print(f'📄 {filename}')
    print(f'   Path: {filepath}')
    print(f'   Changes: {len(changes)}')
    
    # Show last recorded hash
    last_change = changes[-1]
    print(f'   Last: {last_change["type"]} at {last_change["time"]}')
    print(f'   Hash: {last_change["hash"][:32]}...')
    
    # Check if file still exists and verify integrity
    if Path(filepath).exists() and last_change['hash'] != 'deleted':
        current_hash = blockchain.calculate_file_hash(filepath)
        if current_hash == last_change['hash']:
            print(f'   Status: ✅ VERIFIED (no tampering)')
        else:
            print(f'   Status: ⚠️  TAMPERED!')
            print(f'   Current: {current_hash[:32]}...')
    elif last_change['type'] == 'delete':
        print(f'   Status: 🗑️  Deleted (recorded)')
    else:
        print(f'   Status: ❓ File missing')
    
    print()

print('='*60)
print(f'Total files tracked: {len(tracked_files)}')
print('='*60)
