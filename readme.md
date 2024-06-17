# Ping0

## Requirements Linux

```
sudo apt install python3-pip
pip install pyinstaller
pip install requests
pip install tabulate
pip install slugify
pip install numpy
```

## Requirements Windows

```
winget install -e --id Python.Python.3.12
pip install pyinstaller
pip install requests
pip install tabulate
pip install slugify
pip install numpy
pip install cffi
```

## Building Linux

    pyinstaller ping0.py --onefile

## Building Windows

    pyinstaller.exe --onefile -F -i "icon.ico" ping0.py

## Usage
```
ping0.exe -s "Claro net"
```
