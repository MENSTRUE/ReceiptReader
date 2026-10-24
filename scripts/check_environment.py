import sys, shutil
print('Python:', sys.version.split()[0])
print('Tesseract:', shutil.which('tesseract') or 'NOT FOUND — install system binary')
