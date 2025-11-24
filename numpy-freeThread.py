
import os
import multiprocessing
import time

# --- AYARLAR ---
MATRIX_SIZE = 3000       # Matris boyutu 
REPEAT_COUNT = 3         # İşlem Tekrarı 
total_cores = multiprocessing.cpu_count()
my_model_count = 2

# Yük Dengeleme
threads_per_model = int(total_cores / my_model_count)
if threads_per_model < 1: threads_per_model = 1

print(f" [PARALEL] Makine: {total_cores} Çekirdek")
print(f" Konfigürasyon: Her modele {threads_per_model} çekirdek. Matris: {MATRIX_SIZE}x{MATRIX_SIZE}, Tekrar: {REPEAT_COUNT}")

# NumPy Ayarları
os.environ["OMP_NUM_THREADS"] = str(threads_per_model)
os.environ["OPENBLAS_NUM_THREADS"] = str(threads_per_model)
os.environ["MKL_NUM_THREADS"] = str(threads_per_model)

import numpy as np
import threading

def sub_model_A(data):
    print(f"   -> Model A (Inversion) çalışıyor... (x{REPEAT_COUNT})")
    result = None
    for _ in range(REPEAT_COUNT):
        # Matris Tersi almak 
        result = np.linalg.inv(data @ data.T)
    return result

def sub_model_B(data):
    print(f"   -> Model B (Eigenvalues) çalışıyor... (x{REPEAT_COUNT})")
    result = None
    for _ in range(REPEAT_COUNT):
        # Özdeğer hesabı
        result = np.linalg.eigvals(data)
    return result

def worker(model_func, data, results, index):
    results[index] = model_func(data)

if __name__ == "__main__":
    print(f" Veriler hazırlanıyor ({MATRIX_SIZE}x{MATRIX_SIZE})...")
    
    data_1 = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)
    data_2 = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)

    results = [None, None]
    
    print("\n PARALEL TEST BAŞLIYOR...")
    start_time = time.time()

    t1 = threading.Thread(target=worker, args=(sub_model_A, data_1, results, 0))
    t2 = threading.Thread(target=worker, args=(sub_model_B, data_2, results, 1))

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    duration = time.time() - start_time

    print("-" * 40)
    print(f" PARALEL SÜRE: {duration:.4f} saniye")
    print("-" * 40)

    import json
    import sys
    import platform
    import resource  # Works on linux only
    import datetime
    
    usage = resource.getrusage(resource.RUSAGE_SELF)
    peak_memory_mb = usage.ru_maxrss / 1024 #KB to MB

    system_data = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        
        # Performans Metrikleri
        "duration_seconds": duration,
        "peak_memory_mb": round(peak_memory_mb, 2),
        
        # Test Parametreleri
        "script_name": sys.argv[0],
        "matrix_size": MATRIX_SIZE,
        "repeat_count": REPEAT_COUNT,
        
        # Donanım Bilgisi
        "processor": platform.processor(),
        "machine": platform.machine(), # x86_64
        "cpu_count_logical": multiprocessing.cpu_count(),
        
        # Yazılım Ortamı
        "os_system": platform.system(), 
        "os_release": platform.release(), 
        "python_version": platform.python_version(),
        "python_build": platform.python_build(),
        "python_compiler": platform.python_compiler(), 
        
        # NumPy/Thread Ayarları
        "env_omp_threads": os.environ.get("OMP_NUM_THREADS", "Not Set"),
        "env_openblas_threads": os.environ.get("OPENBLAS_NUM_THREADS", "Not Set"),
        "env_mkl_threads": os.environ.get("MKL_NUM_THREADS", "Not Set"),
        
        # GIL Durumu
        "gil_enabled": sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True
    }

   
    json_filename = f"result_{sys.argv[0].split('.')[0]}.json"
    
    with open(json_filename, "w", encoding='utf-8') as f:
        json.dump(system_data, f, indent=4, ensure_ascii=False)
        
    print(f"\n Rapor '{json_filename}' dosyasına kaydedildi.")
    print(f"   Peak Memory: {peak_memory_mb:.2f} MB")
    print(f"   Kernel: {system_data['os_release']}")