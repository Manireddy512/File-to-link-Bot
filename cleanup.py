import os, time

UPLOAD_DIR = "uploads"
AGE_LIMIT = 7 * 24 * 60 * 60  # 7 days

now = time.time()

for f in os.listdir(UPLOAD_DIR):
    file_path = os.path.join(UPLOAD_DIR, f)
    if os.path.isfile(file_path):
        if now - os.path.getmtime(file_path) > AGE_LIMIT:
            os.remove(file_path)
            print("Deleted old file:", f)
