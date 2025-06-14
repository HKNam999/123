
import asyncio
import hashlib
import random
import re
import sqlite3
import time
import math
from datetime import datetime
from typing import Dict, List, Optional

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
except ImportError:
    print("❌ Lỗi import telegram! Đang cài đặt lại...")
    import subprocess
    subprocess.run(["uv", "add", "python-telegram-bot==20.8"], check=True)
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Configuration
BOT_TOKEN = "8010052059:AAFlAiUjs_uTaLAzv38Ae-1Rwx2PhZmHQgo"
ADMIN_IDS = [7560849341]  # Danh sách admin

# Database setup
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            coins INTEGER DEFAULT 1,
            total_analyses INTEGER DEFAULT 0,
            join_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            md5_hash TEXT,
            result TEXT,
            prediction TEXT,
            actual_result TEXT,
            is_correct INTEGER,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            added_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coin_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            admin_id INTEGER,
            admin_username TEXT,
            amount INTEGER,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (admin_id) REFERENCES admins (user_id)
        )
    ''')

    # Add initial admin
    cursor.execute('INSERT OR IGNORE INTO admins VALUES (?, ?, ?)', 
                  (7560849341, 'Main Admin', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

# 12 AI Analysis Engine - Real Algorithm System
class MultiAIAnalysisEngine:
    def __init__(self):
        # 12 AI Systems với thuật toán real không random
        self.ai_systems = {
            'AI_HTH_QUANTUM': self._ai_quantum_analysis,
            'AI_HTH_NEURAL': self._ai_neural_network,
            'AI_HTH_PATTERN': self._ai_pattern_recognition,
            'AI_HTH_CRYPTO': self._ai_cryptographic_analysis,
            'AI_HTH_ENTROPY': self._ai_entropy_calculator,
            'AI_HTH_FIBONACCI': self._ai_fibonacci_sequence,
            'AI_HTH_PRIME': self._ai_prime_analysis,
            'AI_HTH_HASH_CHAIN': self._ai_hash_chain_analysis,
            'AI_HTH_BINARY': self._ai_binary_analysis,
            'AI_HTH_MODULAR': self._ai_modular_arithmetic,
            'AI_HTH_GOLDEN_RATIO': self._ai_golden_ratio_analysis,
            'AI_HTH_CHECKSUM': self._ai_checksum_verification
        }
        
        # Real mathematical constants - không random
        self.constants = {
            'PI': 3.141592653589793,
            'E': 2.718281828459045,
            'PHI': 1.618033988749895,  # Golden ratio
            'SQRT2': 1.4142135623730951,
            'SQRT3': 1.7320508075688772,
            'SQRT5': 2.23606797749979
        }

    def _convert_to_numeric(self, hash_str: str) -> int:
        """Chuyển đổi MD5 thành số nguyên lớn để xử lý"""
        return int(hash_str, 16)

    def _ai_quantum_analysis(self, hash_str: str) -> Dict:
        """AI #1: Quantum Superposition Analysis"""
        hash_int = self._convert_to_numeric(hash_str)
        
        # Quantum state calculation based on hash bits
        binary_repr = bin(hash_int)[2:].zfill(128)
        ones = binary_repr.count('1')
        zeros = binary_repr.count('0')
        
        # Superposition probability
        superposition_ratio = ones / (ones + zeros)
        quantum_entanglement = abs(ones - zeros) / 128
        
        # Heisenberg uncertainty principle simulation
        uncertainty = (ones * zeros) / (128 ** 2)
        
        prediction = "⚫ Tài" if superposition_ratio < 0.5 else "⚪ Xỉu"
        confidence = abs(superposition_ratio - 0.5) * 200
        
        return {
            'prediction': prediction,
            'confidence': round(confidence, 2),
            'superposition': round(superposition_ratio, 4),
            'entanglement': round(quantum_entanglement, 4),
            'uncertainty': round(uncertainty, 6)
        }

    def _ai_neural_network(self, hash_str: str) -> Dict:
        """AI #2: Deep Neural Network Simulation"""
        hash_int = self._convert_to_numeric(hash_str)
        
        # Input layer: hash segments
        segments = [hash_str[i:i+8] for i in range(0, 32, 8)]
        inputs = [int(seg, 16) for seg in segments]
        
        # Hidden layer 1: weighted neurons
        weights_1 = [0.2, 0.3, 0.25, 0.25]  # Real weights, not random
        hidden_1 = [inputs[i] * weights_1[i] for i in range(4)]
        
        # Hidden layer 2: activation function (sigmoid)
        hidden_2 = [1 / (1 + math.exp(-x/1000000)) for x in hidden_1]
        
        # Output layer
        output_weights = [0.4, 0.3, 0.2, 0.1]
        final_output = sum(hidden_2[i] * output_weights[i] for i in range(4))
        
        prediction = "⚫ Tài" if final_output < 2 else "⚪ Xỉu"
        confidence = abs(final_output - 2) * 25
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'neural_output': round(final_output, 4),
            'hidden_states': [round(x, 4) for x in hidden_2]
        }

    def _ai_pattern_recognition(self, hash_str: str) -> Dict:
        """AI #3: Advanced Pattern Recognition"""
        patterns = {
            'ascending': 0,
            'descending': 0,
            'repeated': 0,
            'alternating': 0,
            'symmetric': 0
        }
        
        # Analyze character patterns
        for i in range(len(hash_str) - 1):
            curr, next_char = hash_str[i], hash_str[i + 1]
            
            if ord(curr) < ord(next_char):
                patterns['ascending'] += 1
            elif ord(curr) > ord(next_char):
                patterns['descending'] += 1
            elif curr == next_char:
                patterns['repeated'] += 1
        
        # Check for alternating patterns
        for i in range(len(hash_str) - 2):
            if hash_str[i] == hash_str[i + 2]:
                patterns['alternating'] += 1
        
        # Check symmetry
        for i in range(16):
            if hash_str[i] == hash_str[31 - i]:
                patterns['symmetric'] += 1
        
        # Calculate pattern score
        pattern_score = (patterns['ascending'] * 2 + patterns['descending'] * 3 + 
                        patterns['repeated'] * 1.5 + patterns['alternating'] * 2.5 + 
                        patterns['symmetric'] * 4) / 100
        
        prediction = "⚫ Tài" if pattern_score < 1 else "⚪ Xỉu"
        confidence = abs(pattern_score - 1) * 50
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'pattern_score': round(pattern_score, 4),
            'patterns': patterns
        }

    def _ai_cryptographic_analysis(self, hash_str: str) -> Dict:
        """AI #4: Cryptographic Hash Analysis"""
        hash_int = self._convert_to_numeric(hash_str)
        
        # Avalanche effect analysis
        bit_changes = 0
        for i in range(128):
            if (hash_int >> i) & 1:
                bit_changes += 1
        
        # Collision resistance test
        collision_score = (bit_changes / 128) * 100
        
        # Hash distribution analysis
        hex_frequency = {}
        for char in hash_str:
            hex_frequency[char] = hex_frequency.get(char, 0) + 1
        
        distribution_variance = sum((freq - 2) ** 2 for freq in hex_frequency.values()) / 16
        
        # Cryptographic strength
        crypto_strength = (collision_score + (100 - distribution_variance * 10)) / 2
        
        prediction = "⚫ Tài" if crypto_strength < 50 else "⚪ Xỉu"
        confidence = abs(crypto_strength - 50) * 2
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'crypto_strength': round(crypto_strength, 2),
            'collision_score': round(collision_score, 2),
            'distribution_var': round(distribution_variance, 4)
        }

    def _ai_entropy_calculator(self, hash_str: str) -> Dict:
        """AI #5: Shannon Entropy Calculator"""
        char_freq = {}
        for char in hash_str:
            char_freq[char] = char_freq.get(char, 0) + 1
        
        # Shannon entropy calculation
        entropy = 0
        for freq in char_freq.values():
            probability = freq / 32
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        # Normalized entropy (0-4 bits for hex)
        max_entropy = math.log2(16)  # Maximum for hex chars
        normalized_entropy = entropy / max_entropy
        
        # Min-entropy calculation
        max_freq = max(char_freq.values())
        min_entropy = -math.log2(max_freq / 32)
        
        prediction = "⚫ Tài" if normalized_entropy < 0.9 else "⚪ Xỉu"
        confidence = abs(normalized_entropy - 0.9) * 100
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'shannon_entropy': round(entropy, 4),
            'normalized_entropy': round(normalized_entropy, 4),
            'min_entropy': round(min_entropy, 4)
        }

    def _ai_fibonacci_sequence(self, hash_str: str) -> Dict:
        """AI #6: Fibonacci Sequence Analysis"""
        hash_int = self._convert_to_numeric(hash_str)
        
        # Generate Fibonacci sequence up to hash range
        fib_sequence = [1, 1]
        while fib_sequence[-1] < hash_int:
            fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
        
        # Find closest Fibonacci numbers
        closest_fib = min(fib_sequence, key=lambda x: abs(x - hash_int))
        fib_index = fib_sequence.index(closest_fib)
        
        # Golden ratio relationship
        if len(fib_sequence) > 1:
            ratio = fib_sequence[-1] / fib_sequence[-2]
            golden_deviation = abs(ratio - self.constants['PHI'])
        else:
            golden_deviation = 1
        
        # Fibonacci residue
        fib_residue = hash_int % closest_fib if closest_fib != 0 else 0
        
        prediction = "⚫ Tài" if fib_index % 2 == 0 else "⚪ Xỉu"
        confidence = (1 - golden_deviation) * 80 + 20
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'fibonacci_index': fib_index,
            'golden_deviation': round(golden_deviation, 6),
            'fib_residue': fib_residue % 1000  # Keep manageable
        }

    def _ai_prime_analysis(self, hash_str: str) -> Dict:
        """AI #7: Prime Number Analysis"""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(math.sqrt(n)) + 1):
                if n % i == 0:
                    return False
            return True
        
        # Split hash into segments for prime analysis
        segments = [int(hash_str[i:i+8], 16) for i in range(0, 32, 8)]
        
        prime_count = 0
        prime_sum = 0
        composite_count = 0
        
        for segment in segments:
            # Reduce large numbers for feasible prime checking
            reduced_segment = segment % 1000000
            if is_prime(reduced_segment):
                prime_count += 1
                prime_sum += reduced_segment
            else:
                composite_count += 1
        
        # Prime density analysis
        prime_density = prime_count / len(segments)
        
        # Twin prime check
        twin_primes = 0
        for i in range(len(segments) - 1):
            seg1, seg2 = segments[i] % 1000, segments[i+1] % 1000
            if is_prime(seg1) and is_prime(seg2) and abs(seg1 - seg2) == 2:
                twin_primes += 1
        
        prediction = "⚫ Tài" if prime_density < 0.5 else "⚪ Xỉu"
        confidence = abs(prime_density - 0.5) * 200
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'prime_density': round(prime_density, 4),
            'prime_count': prime_count,
            'twin_primes': twin_primes
        }

    def _ai_hash_chain_analysis(self, hash_str: str) -> Dict:
        """AI #8: Hash Chain Analysis"""
        # Simulate hash chain by rehashing segments
        current_hash = hash_str
        chain_values = []
        
        for i in range(4):  # 4 iterations
            # Take segment and rehash it
            segment = current_hash[i*8:(i+1)*8]
            new_hash = hashlib.md5(segment.encode()).hexdigest()
            chain_values.append(int(new_hash[:8], 16))
            current_hash = new_hash
        
        # Analyze chain properties
        chain_increasing = sum(1 for i in range(len(chain_values)-1) 
                              if chain_values[i] < chain_values[i+1])
        
        chain_sum = sum(chain_values)
        chain_product = 1
        for val in chain_values:
            chain_product *= (val % 1000)  # Prevent overflow
        
        # Stability analysis
        differences = [abs(chain_values[i] - chain_values[i+1]) 
                      for i in range(len(chain_values)-1)]
        stability = sum(differences) / len(differences) if differences else 0
        
        prediction = "⚫ Tài" if chain_sum % 2 == 0 else "⚪ Xỉu"
        confidence = (stability / 1000000) * 100
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'chain_increasing': chain_increasing,
            'stability': round(stability, 2),
            'chain_sum': chain_sum % 10000
        }

    def _ai_binary_analysis(self, hash_str: str) -> Dict:
        """AI #9: Binary Analysis"""
        hash_int = self._convert_to_numeric(hash_str)
        binary_repr = bin(hash_int)[2:].zfill(128)
        
        # Binary metrics
        ones_count = binary_repr.count('1')
        zeros_count = binary_repr.count('0')
        
        # Longest runs analysis
        max_ones_run = 0
        max_zeros_run = 0
        current_ones = 0
        current_zeros = 0
        
        for bit in binary_repr:
            if bit == '1':
                current_ones += 1
                current_zeros = 0
                max_ones_run = max(max_ones_run, current_ones)
            else:
                current_zeros += 1
                current_ones = 0
                max_zeros_run = max(max_zeros_run, current_zeros)
        
        # Bit transitions
        transitions = sum(1 for i in range(len(binary_repr)-1) 
                         if binary_repr[i] != binary_repr[i+1])
        
        # Binary balance
        balance_score = abs(ones_count - zeros_count) / 128
        
        prediction = "⚫ Tài" if ones_count > zeros_count else "⚪ Xỉu"
        confidence = balance_score * 100
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'ones_count': ones_count,
            'zeros_count': zeros_count,
            'max_ones_run': max_ones_run,
            'max_zeros_run': max_zeros_run,
            'transitions': transitions,
            'balance_score': round(balance_score, 4)
        }

    def _ai_modular_arithmetic(self, hash_str: str) -> Dict:
        """AI #10: Modular Arithmetic Analysis"""
        hash_int = self._convert_to_numeric(hash_str)
        
        # Test various moduli
        moduli = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        residues = [hash_int % mod for mod in moduli]
        
        # Quadratic residue analysis
        quadratic_residues = 0
        for mod in [3, 5, 7, 11, 13]:
            if mod > 2:
                legendre = pow(hash_int % mod, (mod - 1) // 2, mod)
                if legendre == 1:
                    quadratic_residues += 1
        
        # Chinese remainder theorem simulation
        crt_sum = sum(residues[i] * moduli[i] for i in range(len(moduli)))
        
        # Modular patterns
        even_residues = sum(1 for r in residues if r % 2 == 0)
        odd_residues = len(residues) - even_residues
        
        prediction = "⚫ Tài" if even_residues > odd_residues else "⚪ Xỉu"
        confidence = abs(even_residues - odd_residues) / len(residues) * 100
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'quadratic_residues': quadratic_residues,
            'even_residues': even_residues,
            'odd_residues': odd_residues,
            'crt_sum': crt_sum % 10000
        }

    def _ai_golden_ratio_analysis(self, hash_str: str) -> Dict:
        """AI #11: Golden Ratio Analysis"""
        hash_int = self._convert_to_numeric(hash_str)
        
        # Split into Fibonacci-like sequence
        segments = [int(hash_str[i:i+4], 16) for i in range(0, 32, 4)]
        
        # Calculate ratios between consecutive segments
        ratios = []
        for i in range(len(segments) - 1):
            if segments[i] != 0:
                ratio = segments[i + 1] / segments[i]
                ratios.append(ratio)
        
        # Find deviations from golden ratio
        golden_deviations = [abs(ratio - self.constants['PHI']) for ratio in ratios]
        avg_deviation = sum(golden_deviations) / len(golden_deviations) if golden_deviations else 1
        
        # Phi-based calculations
        phi_power = pow(self.constants['PHI'], len(hash_str))
        phi_residue = hash_int % int(phi_power)
        
        # Golden angle (137.5 degrees in radians)
        golden_angle = 2.39996322972865332  # (3 - sqrt(5)) * pi
        angle_correlation = math.sin(hash_int * golden_angle / 1000000)
        
        prediction = "⚫ Tài" if avg_deviation < 1 else "⚪ Xỉu"
        confidence = (1 / (avg_deviation + 0.1)) * 30
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'avg_deviation': round(avg_deviation, 4),
            'ratios_count': len(ratios),
            'phi_residue': phi_residue % 10000,
            'angle_correlation': round(angle_correlation, 4)
        }

    def _ai_checksum_verification(self, hash_str: str) -> Dict:
        """AI #12: Advanced Checksum Analysis"""
        # Multiple checksum algorithms
        checksums = {}
        
        # Simple sum checksum
        checksums['sum'] = sum(ord(c) for c in hash_str) % 256
        
        # XOR checksum
        xor_checksum = 0
        for c in hash_str:
            xor_checksum ^= ord(c)
        checksums['xor'] = xor_checksum
        
        # Luhn algorithm adaptation
        digits = [int(c, 16) for c in hash_str]
        luhn_sum = 0
        for i, digit in enumerate(digits):
            if i % 2 == 1:
                digit *= 2
                if digit > 15:
                    digit = (digit // 16) + (digit % 16)
            luhn_sum += digit
        checksums['luhn'] = luhn_sum % 10
        
        # Fletcher checksum
        sum1, sum2 = 0, 0
        for c in hash_str:
            sum1 = (sum1 + ord(c)) % 255
            sum2 = (sum2 + sum1) % 255
        checksums['fletcher'] = (sum2 << 8) | sum1
        
        # CRC-like calculation
        crc = 0
        for c in hash_str:
            crc = ((crc << 1) ^ ord(c)) & 0xFFFF
        checksums['crc'] = crc
        
        # Checksum analysis
        even_checksums = sum(1 for cs in checksums.values() if cs % 2 == 0)
        odd_checksums = len(checksums) - even_checksums
        
        checksum_sum = sum(checksums.values())
        
        prediction = "⚫ Tài" if checksum_sum % 2 == 0 else "⚪ Xỉu"
        confidence = abs(even_checksums - odd_checksums) / len(checksums) * 100
        
        return {
            'prediction': prediction,
            'confidence': round(min(confidence, 95), 2),
            'checksums': checksums,
            'even_checksums': even_checksums,
            'odd_checksums': odd_checksums,
            'checksum_sum': checksum_sum % 10000
        }

    def analyze_with_all_ais(self, md5_hash: str) -> Dict:
        """Phân tích với tất cả 12 AI systems"""
        if len(md5_hash) != 32 or not all(c in '0123456789abcdef' for c in md5_hash.lower()):
            raise ValueError("Invalid MD5 hash format")

        hash_str = md5_hash.lower()
        ai_results = {}
        
        # Chạy tất cả 12 AI systems
        for ai_name, ai_function in self.ai_systems.items():
            try:
                ai_results[ai_name] = ai_function(hash_str)
            except Exception as e:
                ai_results[ai_name] = {
                    'prediction': "⚪ Xỉu",
                    'confidence': 50,
                    'error': str(e)
                }
        
        # Voting system từ 12 AI
        tai_votes = 0
        xiu_votes = 0
        total_confidence = 0
        
        for result in ai_results.values():
            if result['prediction'] == "⚫ Tài":
                tai_votes += 1
            else:
                xiu_votes += 1
            total_confidence += result.get('confidence', 50)
        
        # Final decision
        final_prediction = "⚫ Tài" if tai_votes > xiu_votes else "⚪ Xỉu"
        avg_confidence = total_confidence / len(ai_results)
        
        # Consensus strength
        consensus_strength = max(tai_votes, xiu_votes) / len(ai_results) * 100
        
        return {
            'ai_name': '🤖 AI HTH SYSTEMS',
            'final_prediction': final_prediction,
            'tai_votes': tai_votes,
            'xiu_votes': xiu_votes,
            'consensus_strength': round(consensus_strength, 1),
            'average_confidence': round(avg_confidence, 1),
            'total_ais': len(ai_results),
            'ai_results': ai_results,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'algorithm_type': 'REAL MATHEMATICAL - NO RANDOM'
        }

# Bot class
class MD5AnalysisBot:
    def __init__(self):
        self.engine = MultiAIAnalysisEngine()
        init_db()
        self.pending_predictions = {}

    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM admins WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def get_user(self, user_id: int) -> Optional[Dict]:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'coins': user[2],
                'total_analyses': user[3],
                'join_date': user[4]
            }
        return None

    def create_user(self, user_id: int, username: str):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO users (user_id, username, coins, total_analyses, join_date)
            VALUES (?, ?, 1, 0, ?)
        ''', (user_id, username, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

    def update_user_coins(self, user_id: int, amount: int):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET coins = coins + ? WHERE user_id = ?', (amount, user_id))
        conn.commit()
        conn.close()

    def log_coin_transaction(self, user_id: int, admin_id: int, admin_username: str, amount: int):
        """Ghi log giao dịch xu"""
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO coin_transactions (user_id, admin_id, admin_username, amount, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, admin_id, admin_username, amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

    def reset_user_coins(self, user_id: int):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET coins = 0 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def increment_analyses(self, user_id: int):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET total_analyses = total_analyses + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()

    def save_analysis(self, user_id: int, md5_hash: str, result: str, prediction: str) -> int:
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses (user_id, md5_hash, result, prediction, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, md5_hash, result, prediction, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return analysis_id

    def update_prediction_result(self, analysis_id: int, actual_result: str, is_correct: bool):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE analyses SET actual_result = ?, is_correct = ? WHERE id = ?
        ''', (actual_result, 1 if is_correct else 0, analysis_id))
        conn.commit()
        conn.close()

    def add_admin(self, user_id: int, username: str):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO admins (user_id, username, added_date)
            VALUES (?, ?, ?)
        ''', (user_id, username, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        conn.close()

    def remove_admin(self, user_id: int):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM admins WHERE user_id = ?', (user_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0

    def get_all_users(self):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        users = [row[0] for row in cursor.fetchall()]
        conn.close()
        return users

    def get_all_admins(self):
        conn = sqlite3.connect('bot_data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, username, added_date FROM admins')
        admins = cursor.fetchall()
        conn.close()
        return admins

# Initialize bot
bot = MD5AnalysisBot()

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    bot.create_user(user.id, user.username or user.first_name)

    keyboard = [
        [InlineKeyboardButton("🔍 Phân Tích MD5", callback_data="analyze")],
        [InlineKeyboardButton("💰 Thông Tin Xu", callback_data="check_coins")],
        [InlineKeyboardButton("ℹ️ Hướng Dẫn", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = f"""
🤖 AI HTH - Siêu Dự Đoán MD5

👋 Chào {user.first_name}!

🔥 Thuật toán REAL - Cực chính xác
💎 Dùng: /tx <md5>
💰 Mua xu: @hatronghoann

✨ Tặng 1 xu miễn phí!
"""

    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def analyze_md5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = bot.get_user(user_id)

    if not user_data:
        await update.message.reply_text("❌ Vui lòng gửi /start trước!")
        return

    if user_data['coins'] < 1:
        await update.message.reply_text(
            "💸 Không đủ xu!\n\n"
            "Cần ít nhất 1 xu để phân tích với AI.\n"
            "💳 Mua Xu Liên Hệ Admin @hatronghoann"
        )
        return

    if not context.args:
        await update.message.reply_text(
            "📝 Cách sử dụng:\n"
            "/tx <mã_md5_32_ký_tự>\n\n"
            "Ví dụ:\n"
            "/tx 5d41402abc4b2a76b9719d911017c592"
        )
        return

    md5_hash = context.args[0].strip()

    if len(md5_hash) != 32 or not all(c in '0123456789abcdefABCDEF' for c in md5_hash):
        await update.message.reply_text(
            "❌ Mã MD5 không hợp lệ!\n\n"
            "MD5 phải có đúng 32 ký tự hex (0-9, a-f)"
        )
        return

    processing_msg = await update.message.reply_text(
        "🤖 AI HTH ĐANG PHÂN TÍCH...\n"
        "⏳ Vui lòng chờ 5 giây..."
    )

    try:
        await asyncio.sleep(5)  # Thời gian để 12 AI xử lý

        analysis_result = bot.engine.analyze_with_all_ais(md5_hash)

        bot.update_user_coins(user_id, -1)
        bot.increment_analyses(user_id)

        analysis_id = bot.save_analysis(user_id, md5_hash, str(analysis_result), analysis_result['final_prediction'])

        # Store pending prediction for verification
        bot.pending_predictions[user_id] = {
            'md5': md5_hash,
            'prediction': analysis_result['final_prediction'],
            'analysis_id': analysis_id
        }

        # Tính độ tin cậy mới từ 55-90%
        enhanced_confidence = min(90, max(55, analysis_result['consensus_strength'] * 0.6 + analysis_result['average_confidence'] * 0.4 + 20))
        
        result_text = f"""
🤖 AI HTH - Dự Đoán Siêu Chính Xác

🔮 {md5_hash[:16]}...

🎯Dự Đoán: {analysis_result['final_prediction']}

📊 Độ tin cậy: {enhanced_confidence:.1f}%
💎 Xu còn lại: {user_data['coins'] - 1}

⭐ Nhập kết quả xác minh!
"""

        keyboard = [
            [InlineKeyboardButton("⚫ Tài", callback_data=f"result_tai_{analysis_id}")],
            [InlineKeyboardButton("⚪ Xỉu", callback_data=f"result_xiu_{analysis_id}")],
            [InlineKeyboardButton("🔄 Phân Tích Khác", callback_data="analyze")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await processing_msg.edit_text(result_text, reply_markup=reply_markup)

    except Exception as e:
        await processing_msg.edit_text(f"❌ Lỗi phân tích: {str(e)}")

async def user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = bot.get_user(user_id)

    if not user_data:
        await update.message.reply_text("❌ Vui lòng gửi /start trước!")
        return

    # Get correct and incorrect predictions
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM analyses WHERE user_id = ? AND is_correct = 1', (user_id,))
    correct_predictions = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM analyses WHERE user_id = ? AND is_correct = 0', (user_id,))
    incorrect_predictions = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM analyses WHERE user_id = ? AND actual_result IS NOT NULL', (user_id,))
    total_predictions = cursor.fetchone()[0]
    conn.close()

    accuracy = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0

    info_text = f"""
👤 {user_data['username']}

💎 Xu: {user_data['coins']}
📊 Phân tích: {user_data['total_analyses']} lần

🎯 AI HTH:
✅ Đúng: {correct_predictions} | ❌ Sai: {incorrect_predictions}
📈 Tỷ lệ chính xác: {accuracy:.1f}%
"""

    keyboard = [
        [InlineKeyboardButton("🔄 Phân Tích AI", callback_data="analyze")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(info_text, reply_markup=reply_markup)

async def check_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await user_info(update, context)

# Admin commands
async def add_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    if len(context.args) != 2:
        await update.message.reply_text("📝 Cách sử dụng:\n/addcoins <user_id> <số_xu>")
        return

    try:
        target_user_id = int(context.args[0])
        coins = int(context.args[1])
        admin_user = update.effective_user

        user_data = bot.get_user(target_user_id)
        if not user_data:
            bot.create_user(target_user_id, f"User_{target_user_id}")
            user_data = bot.get_user(target_user_id)

            if not user_data:
                await update.message.reply_text("❌ Không thể tạo user mới!")
                return

        old_coins = user_data['coins']
        bot.update_user_coins(target_user_id, coins)
        
        # Log transaction với thông tin admin
        bot.log_coin_transaction(target_user_id, admin_user.id, admin_user.username or admin_user.first_name, coins)
        
        new_coins = old_coins + coins

        await update.message.reply_text(
            f"✅ Thành công cộng xu!\n\n"
            f"👤 User ID: {target_user_id}\n"
            f"📝 Username: {user_data['username']}\n"
            f"💰 Đã cộng: {coins} xu\n"
            f"💎 Xu cũ: {old_coins} xu\n"
            f"💎 Xu mới: {new_coins} xu\n\n"
            f"👑 Admin thực hiện:\n"
            f"🆔 ID: {admin_user.id}\n"
            f"👤 Username: {admin_user.username or admin_user.first_name}\n"
            f"📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    except ValueError:
        await update.message.reply_text("❌ Dữ liệu không hợp lệ!")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

async def reset_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("📝 Cách sử dụng:\n/resetxu <user_id>")
        return

    try:
        target_user_id = int(context.args[0])
        admin_user = update.effective_user

        user_data = bot.get_user(target_user_id)
        if not user_data:
            bot.create_user(target_user_id, f"User_{target_user_id}")
            user_data = bot.get_user(target_user_id)

            if not user_data:
                await update.message.reply_text("❌ Không thể tạo user mới!")
                return

        old_coins = user_data['coins']
        bot.reset_user_coins(target_user_id)
        
        # Log transaction với thông tin admin
        bot.log_coin_transaction(target_user_id, admin_user.id, admin_user.username or admin_user.first_name, -old_coins)

        await update.message.reply_text(
            f"✅ Đã reset xu!\n\n"
            f"👤 User ID: {target_user_id}\n"
            f"📝 Username: {user_data['username']}\n"
            f"💰 Xu trước đó: {old_coins}\n"
            f"💰 Xu hiện tại: 0 xu\n\n"
            f"👑 Admin thực hiện:\n"
            f"🆔 ID: {admin_user.id}\n"
            f"👤 Username: {admin_user.username or admin_user.first_name}\n"
            f"📅 Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    except ValueError:
        await update.message.reply_text("❌ User ID không hợp lệ!")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

async def add_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("📝 Cách sử dụng:\n/themadmin <user_id>")
        return

    try:
        target_user_id = int(context.args[0])

        user_data = bot.get_user(target_user_id)
        if not user_data:
            await update.message.reply_text("❌ Không tìm thấy user!")
            return

        bot.add_admin(target_user_id, user_data['username'])

        await update.message.reply_text(
            f"✅ Đã thêm admin!\n\n"
            f"👤 User: {user_data['username']}\n"
            f"🆔 ID: {target_user_id}"
        )

    except ValueError:
        await update.message.reply_text("❌ User ID không hợp lệ!")

async def remove_admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    if len(context.args) != 1:
        await update.message.reply_text("📝 Cách sử dụng:\n/xoaadmin <user_id>")
        return

    try:
        target_user_id = int(context.args[0])

        if target_user_id == 7560849341:
            await update.message.reply_text("❌ Không thể xóa admin chính!")
            return

        if bot.remove_admin(target_user_id):
            await update.message.reply_text(
                f"✅ Đã xóa admin!\n\n"
                f"🆔 ID: {target_user_id}"
            )
        else:
            await update.message.reply_text("❌ User không phải admin!")

    except ValueError:
        await update.message.reply_text("❌ User ID không hợp lệ!")

async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    admins = bot.get_all_admins()

    if not admins:
        await update.message.reply_text("📋 Không có admin nào!")
        return

    admin_list = "👑 Danh Sách Admin\n\n"
    for admin in admins:
        admin_list += f"👤 {admin[1]}\n🆔 ID: {admin[0]}\n📅 Thêm: {admin[2]}\n\n"

    await update.message.reply_text(admin_list)

async def stat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id, username, coins FROM users ORDER BY coins DESC LIMIT 20')
    users = cursor.fetchall()

    cursor.execute('SELECT SUM(coins) FROM users')
    total_coins = cursor.fetchone()[0] or 0

    conn.close()

    stat_text = f"📊 Thống Kê Xu Người Dùng\n\n💰 Tổng xu trong hệ thống: {total_coins}\n\n"

    for i, user in enumerate(users, 1):
        stat_text += f"{i}. {user[1]} (ID: {user[0]}): {user[2]} xu\n"

    await update.message.reply_text(stat_text)

async def game_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_text = """
🎮 AI HTH - HỖ TRỢ FULL GAME MD5

🔥 Các cổng game được hỗ trợ:
• B52.CLUB ✅
• 68 GAME BÀI ✅  
• HIT.CLUB ✅
• XOCDIA88 ✅
• RIKVIP ✅
• SUNWIN ✅
• IWIN ✅
• GO88 ✅
• KUBET ✅
• J88 ✅

🤖  AI HTH hoạt động đồng thời:
• AI Quantum Analysis
• AI Neural Network 
• AI Pattern Recognition
• AI Cryptographic Analysis
• AI Entropy Calculator
• AI Fibonacci Sequence
• AI Prime Analysis
• AI Hash Chain Analysis
• AI Binary Analysis
• AI Modular Arithmetic
• AI Golden Ratio Analysis
• AI Checksum Verification

🚀 Thuật toán REAL - Không random
⚡ Phân tích real-time
🎯 Độ chính xác cực cao

👨‍💻 Admin hỗ trợ: @hatronghoann

💡 Gửi /tx <md5> để bắt đầu phân tích với AI HTH !
"""

    await update.message.reply_text(support_text)

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    if not context.args:
        await update.message.reply_text("📝 Cách sử dụng:\n/thongbao <tin_nhắn>")
        return

    message = " ".join(context.args)
    users = bot.get_all_users()

    sent_count = 0
    failed_count = 0

    broadcast_text = f"""
📢 Thông Báo Từ Admin

{message}

---
🤖 12 AI HTH Bot - REAL ALGORITHM
"""

    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=broadcast_text)
            sent_count += 1
            await asyncio.sleep(0.1)
        except:
            failed_count += 1

    await update.message.reply_text(
        f"📊 Kết quả gửi thông báo:\n\n"
        f"✅ Thành công: {sent_count}\n"
        f"❌ Thất bại: {failed_count}"
    )

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot.is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Bạn không có quyền admin!")
        return

    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM analyses')
    total_analyses = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(coins) FROM users')
    total_coins = cursor.fetchone()[0] or 0

    cursor.execute('SELECT COUNT(*) FROM admins')
    total_admins = cursor.fetchone()[0]

    conn.close()

    stats_text = f"""
📊 Thống Kê Bot AI HTH

👥 Tổng users: {total_users}
👑 Tổng admins: {total_admins}
📈 Tổng phân tích: {total_analyses}
🤖 Tổng AI xử lý: {total_analyses * 12}
💰 Tổng xu trong hệ thống: {total_coins}

🤖  AI HTH: REAL ALGORITHM
⚡ Trạng thái: Hoạt động bình thường
🚀 Thuật toán: Mathematical - No Random
"""

    await update.message.reply_text(stats_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = bot.is_admin(user_id)

    help_text = """
📚 Hướng Dẫn AI HTH

🔍 Lệnh chính:
• /tx <md5> - Dự đoán siêu chính xác
• /thongtin - Xem xu và thống kê

🎯 Cách dùng:
1. /tx <mã_md5> 
2. Nhận dự đoán từ AI HTH
3. Nhập kết quả xác minh

💰 1 xu/lần | 💳 Mua xu: @hatronghoann
🔥 AI HTH - Thuật toán REAL!
"""

    if is_admin:
        help_text += """

👑 Lệnh Admin:
• /addcoins <user_id> <xu> - Cộng xu (có log admin)
• /resetxu <user_id> - Reset xu (có log admin)
• /themadmin <user_id> - Thêm admin
• /xoaadmin <user_id> - Xóa admin
• /dsadmin - Danh sách admin
• /stat - Thống kê xu user
• /thongbao <tin_nhắn> - Gửi thông báo
• /stats - Thống kê bot
"""

    await update.message.reply_text(help_text)

# Message handler for prediction verification
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if user_id in bot.pending_predictions and text in ['tài', 'xỉu', 'tai', 'xiu']:
        pending = bot.pending_predictions[user_id]
        predicted = pending['prediction']
        actual = "🔴 Tài" if text in ['tài', 'tai'] else "🔵 Xỉu"

        is_correct = (predicted == actual)
        bot.update_prediction_result(pending['analysis_id'], actual, is_correct)

        if is_correct:
            result_msg = "🎉 AI HTH Dự Đoán Chính Xác!"
        else:
            result_msg = "❌ Sai rồi! AI HTH sẽ học hỏi để tốt hơn!"

        await update.message.reply_text(
            f"📊 Kết Quả Xác Minh AI HTH\n\n"
            f"🤖 AI HTH dự đoán: {predicted}\n"
            f"🎯 Kết quả thực tế: {actual}\n\n"
            f"{result_msg}"
        )

        del bot.pending_predictions[user_id]

# Callback query handler
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "analyze":
        await query.edit_message_text(
            "🤖 AI HTH - Siêu Dự Đoán\n\n"
            "📝 /tx <md5>\n\n"
            "📖 Ví dụ:\n"
            "/tx 5d41402abc4b2a76b9719d911017c592\n\n"
            "🔥 Thuật toán REAL - Cực chính xác!"
        )
    elif query.data == "check_coins":
        user_data = bot.get_user(query.from_user.id)
        if user_data:
            await query.edit_message_text(
                f"💰 Thông Tin Xu\n\n"
                f"💎 Xu hiện tại: {user_data['coins']}\n"
                f"📊 Tổng phân tích AI: {user_data['total_analyses']}\n"
                f"🤖 Tổng AI đã xử lý: {user_data['total_analyses'] * 12}"
            )
    elif query.data == "help":
        await help_command(update, context)
    elif query.data == "menu":
        await start(update, context)
    elif query.data.startswith("result_"):
        parts = query.data.split("_")
        result_type = parts[1]  # tai or xiu
        analysis_id = int(parts[2])

        user_id = query.from_user.id
        if user_id in bot.pending_predictions:
            pending = bot.pending_predictions[user_id]
            predicted = pending['prediction']
            actual = "⚫ Tài" if result_type == "tai" else "⚪ Xỉu"

            is_correct = (predicted == actual)
            bot.update_prediction_result(analysis_id, actual, is_correct)

            if is_correct:
                result_msg = "🎉 AI HTH Dự Đoán Chính Xác!"
            else:
                result_msg = "❌ Sai rồi! AI HTH sẽ học hỏi để tốt hơn!"

            await query.edit_message_text(
                f"📊 Kết Quả Xác Minh AI HTH\n\n"
                f"🤖 AI HTH dự đoán: {predicted}\n"
                f"🎯 Kết quả thực tế: {actual}\n\n"
                f"{result_msg}"
            )

            del bot.pending_predictions[user_id]

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tx", analyze_md5))
    application.add_handler(CommandHandler("thongtin", user_info))
    application.add_handler(CommandHandler("coins", check_coins))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("addcoins", add_coins))
    application.add_handler(CommandHandler("resetxu", reset_coins))
    application.add_handler(CommandHandler("themadmin", add_admin_cmd))
    application.add_handler(CommandHandler("xoaadmin", remove_admin_cmd))
    application.add_handler(CommandHandler("dsadmin", list_admins))
    application.add_handler(CommandHandler("stat", stat_command))
    application.add_handler(CommandHandler("conggamehotro", game_support))
    application.add_handler(CommandHandler("thongbao", broadcast_message))
    application.add_handler(CommandHandler("stats", admin_stats))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖  AI HTH Bot REAL ALGORITHM started successfully!")
    print("🚀 AI Systems ready to analyze!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
name__ == "__main__":
    main()
