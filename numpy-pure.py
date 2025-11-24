import os
import multiprocessing
import time


MATRIX_SIZE = 3000
REPEAT_COUNT = 3
total_cores = multiprocessing.cpu_count()

print(f" [SIRALI] Makine: {total_cores} Çekirdek")
print(f" Konfigürasyon: Modeller sırayla tüm gücü kullanacak.")


os.environ["OMP_NUM_THREADS"] = str(total_cores)
os.environ["OPENBLAS_NUM_THREADS"] = str(total_cores)
os.environ["MKL_NUM_THREADS"] = str(total_cores)

import numpy as np

def sub_model_A(data):
    print(f"   -> Model A çalışıyor... (x{REPEAT_COUNT})")
    result = None
    for _ in range(REPEAT_COUNT):
        result = np.linalg.inv(data @ data.T)
    return result

def sub_model_B(data):
    print(f"   -> Model B çalışıyor... (x{REPEAT_COUNT})")
    result = None
    for _ in range(REPEAT_COUNT):
        result = np.linalg.eigvals(data)
    return result

if __name__ == "__main__":
    print(f" Veriler hazırlanıyor ({MATRIX_SIZE}x{MATRIX_SIZE})...")
    data_1 = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)
    data_2 = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)

    print("\n SIRALI TEST BAŞLIYOR...")
    start_time = time.time()

    sub_model_A(data_1)
    sub_model_B(data_2)

    duration = time.time() - start_time

    print("-" * 40)
    print(f" SIRALI SÜRE: {duration:.4f} saniye")
    print("-" * 40)

    import json
    import sys
    import platform
    import resource  # Linux'ta RAM ölçümü için
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
    