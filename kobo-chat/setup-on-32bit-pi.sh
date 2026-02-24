# For setup on my old Raspberry Pi 32-bit, which was failing on a compilation error due to new versions
# Make sure we're in our venv first!!!

python3 -m pip install --upgrade pip setuptools wheel
pip install "markupsafe<3.1" # This was the breaking version that we force to a working type
pip install -r requirements.txt
