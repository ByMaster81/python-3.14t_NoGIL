import json
import subprocess
import os
import time

CONFIG_FILE = "test-plan.json"

def run_single_job(job):
    script = job["script"]
    python_cmd = job["python_exec"]
    gil_val = job["gil_setting"]
    desc = job["description"]

    print(f"\nBETİK BAŞLATILIYOR: {desc}")
    print(f"    Komut: {python_cmd} -X gil={gil_val} {script}")   
    command = [python_cmd, "-X", f"gil={gil_val}", script]
    try:
        subprocess.run(command, check=True)
        print(f"   {script} tamamlandı. (Rapor dosyası klasörde oluştu)")
    
    except FileNotFoundError:
        print(f"   HATA: '{python_cmd}' komutu bulunamadı!")
    except subprocess.CalledProcessError:
        print(f"   HATA: '{script}' çalışırken hata verdi!")

if __name__ == "__main__":
    

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except FileNotFoundError:
        print(f" HATA: '{CONFIG_FILE}' dosyası bulunamadı!")
        exit()

 
    for job in jobs:
        run_single_job(job)
        time.sleep(1) 
        
    print("\n  TÜM LİSTE ÇALIŞTIRILDI. Sonuç dosyalarını (result_*.json) kontrol edebilirsiniz.")