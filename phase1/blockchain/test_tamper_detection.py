from integrity_blockchain import IntegrityBlockchain
from pathlib import Path
import time

print('='*60)
print('BLOCKCHAIN TAMPER DETECTION DEMO')
print('='*60)

# Load existing blockchain
blockchain = IntegrityBlockchain()
blockchain.load_chain('../logs/blockchain.json')

print('\n[TEST 1] Verify blockchain integrity...')
is_valid, message = blockchain.verify_chain()
print(f'Result: {message}\n')

# Check file history
test_file = '../data/security_report.txt'
if Path(test_file).exists():
    print(f'[TEST 2] File history for security_report.txt...')
    history = blockchain.get_file_history(test_file)
    
    if history:
        print(f'Found {len(history)} entries:\n')
        for entry in history:
            print(f"  Block {entry['block']}: {entry['timestamp']}")
            print(f"    Type: {entry['type']}")
            print(f"    Hash: {entry['hash'][:32]}...")
    
    print(f'\n[TEST 3] Check current file integrity...')
    is_tampered, result = blockchain.detect_tampering(test_file)
    
    if is_tampered is None:
        print(f'  Status: {result}')
    elif is_tampered:
        print(f'  ⚠️  WARNING: {result}')
    else:
        print(f'  ✅ {result}')

# Show blockchain summary
print('\n[TEST 4] Blockchain summary...\n')
blockchain.print_summary()

print('✅ All tamper detection tests complete!')
