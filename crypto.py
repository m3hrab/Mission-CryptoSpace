import random
import math

def extended_gcd(a, b):
    """Returns gcd and Bezout coefficients for ax + by = gcd(a, b)."""
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(e, phi):
    """Returns modular inverse of e modulo phi."""
    gcd, x, _ = extended_gcd(e, phi)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % phi + phi) % phi

def decrypt(ciphertext, d, n):
    """Decrypts RSA ciphertext using private key (d, n)."""
    return pow(ciphertext, d, n)

def solve(p, q, e, c):
    """Solves RSA puzzle to find plaintext M."""
    n = p * q
    phi = (p - 1) * (q - 1)
    d = mod_inverse(e, phi)
    return str(decrypt(c, d, n))

class PuzzleGenerator:
    def __init__(self):
        self.primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    def get_random_prime(self, exclude=None):
        primes = [p for p in self.primes if p != exclude] if exclude else self.primes
        return random.choice(primes)

    def generate_puzzle(self):
        while True:
            p = self.get_random_prime()
            q = self.get_random_prime(exclude=p)
            n = p * q
            phi = (p - 1) * (q - 1)
            e_candidates = [i for i in range(2, phi) if math.gcd(i, phi) == 1]
            if not e_candidates:
                continue
            e = random.choice(e_candidates)
            try:
                mod_inverse(e, phi)
                m = random.randint(10, n // 2)
                c = pow(m, e, n)
                return {'p': p, 'q': q, 'e': e, 'C': c, 'M_solution': str(m)}
            except ValueError:
                continue
            
    
# def solve(p, q, e, c):
#     """find plaintext M."""
#     n = p * q
#     phi = (p - 1) * (q - 1)
#     d = mod_inverse(e, phi)
#     m = decrypt(c, d, n)
#     return str(m)

    
# print(solve(41, 11, 313, 424))