import time
import threading
import random
import sys
import os
import json
import platform
import resource  # Linux
import datetime
import multiprocessing

TOTAL_POINTS = 200_000_000
THREAD_COUNT = 8


def calc_pi_part(n, results, index):
    inside = 0
    # Her thread kendi 'rng' (Random Number Generator) nesnesini oluşturuyor.
    rng = random.Random() 
    
    for _ in range(n):
        x = rng.random()
        y = rng.random()
        if x**2 + y**2 <= 1.0:
            inside += 1
    results[index] = inside

def run_test(n, threads=1):
    results = [0] * threads
    points_per_thread = n // threads
    thread_list = []

    print(f" Başlıyor... Nokta: {n:_}, Thread: {threads}")
    start_time = time.time()

    for i in range(threads):
        t = threading.Thread(target=calc_pi_part, args=(points_per_thread, results, i))
        thread_list.append(t)
        t.start()

    for t in thread_list:
        t.join()

    end_time = time.time()
    duration = end_time - start_time
    print(f"  Süre: {duration:.4f} sn")
    return duration

if __name__ == "__main__":
    print(f"Version: {sys.version.split()[0]}")
    gil_status_bool = True
    try:
        if not sys._is_gil_enabled():
            gil_msg = "KAPALI (Free-Threaded)"
            gil_status_bool = False
        else:
            gil_msg = "AÇIK (Standart)"
    except AttributeError:
        gil_msg = "AÇIK (Eski Sürüm)"
    print(f"GIL Durumu: {gil_msg}")
    
    print("-" * 30)
    
    # Test 1: Tek Thread
    t1 = run_test(TOTAL_POINTS, 1)
    
    # Test 2: Çoklu Thread
    t2 = run_test(TOTAL_POINTS, THREAD_COUNT)
    
    speedup = t1 / t2
    print(f"\n SONUÇ: {speedup:.2f}x Hızlanma")

    # JSON KAYIT BLOĞU (DİĞERLERİYLE UYUMLU) 
    usage = resource.getrusage(resource.RUSAGE_SELF)
    peak_memory_mb = usage.ru_maxrss / 1024 

    # 2. Veri Paketini Hazırla
    system_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "script_name": sys.argv[0],
        
        # Performans Metrikleri
        "duration_seconds": t2,       
        "duration_single_core": t1,   
        "speedup_x": round(speedup, 2),
        "peak_memory_mb": round(peak_memory_mb, 2),
        
        # Test Parametreleri
        "total_points": TOTAL_POINTS,
        "thread_count": THREAD_COUNT,
        
        # Sistem Bilgileri
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        
        # GIL Durumu
        "gil_enabled": gil_status_bool
    }

    
    script_base = sys.argv[0].split('.')[0]
    gil_tag = "nogil" if not gil_status_bool else "gil"
    file_timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_filename = f"result_{script_base}_{gil_tag}_{file_timestamp}.json"
    
    with open(json_filename, "w", encoding='utf-8') as f:
        json.dump(system_data, f, indent=4, ensure_ascii=False)
        
    print(f"\n [RAPOR] '{json_filename}' oluşturuldu.")