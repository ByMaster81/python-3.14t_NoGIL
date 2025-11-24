import time
import threading
import sys
import math

# Bu aralıktaki asal sayıları bulacağız
RANGE_START = 10_000_000
RANGE_END   = 20_200_000 
THREAD_COUNT = 32

def is_prime(n):
    """Bir sayının asal olup olmadığını kontrol eden saf CPU fonksiyonu"""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def worker(start, end, results, index):
    count = 0
    for n in range(start, end):
        if is_prime(n):
            count += 1
    results[index] = count

def run_test(threads=1):
    results = [0] * threads
    step = (RANGE_END - RANGE_START) // threads
    thread_list = []
    
    print(f"  Hesap başlıyor... Thread: {threads}", flush=True)
    start_time = time.time()

    for i in range(threads):
      
        s = RANGE_START + (i * step)
        e = RANGE_START + ((i + 1) * step)
        t = threading.Thread(target=worker, args=(s, e, results, i))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()

    duration = time.time() - start_time
    total_primes = sum(results)
    print(f"   Süre: {duration:.4f} sn (Bulunan Asal: {total_primes})", flush=True)
    return duration

if __name__ == "__main__":
    try:
        gil = "KAPALI " if not sys._is_gil_enabled() else "AÇIK"
    except: gil = "AÇIK "
    
    print(f"--- TEST: ASAL SAYI BULMA (GIL: {gil}) ---")
    
    t1 = run_test(1)
    t2 = run_test(THREAD_COUNT)
    
    print(f"SONUÇ: {t1/t2:.2f}x Hızlanma")