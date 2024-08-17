# Ping0

## Requirements Linux

```
sudo apt install python3-pip
pip install pyinstaller
pip install requests
pip install tabulate
pip install numpy
pip install slugify

```

## Requirements Windows

```
winget install -e --id Python.Python.3.12
pip install --upgrade cx_Freeze
pip install requests
pip install tabulate
pip install numpy
pip install slugify
```

## Building Linux

    pyinstaller ping0.py --onefile

## Building Windows

    cxfreeze.exe build

## Usage with Speed Test servers
```
ping0.exe -s "Claro net"
```

## Export Speed Test results to CSV file
```
ping0.exe -s "Claro net" -e csv
```

## Usage with local txt file
```
ping0.exe -f datapacket.txt
```

## Usage with remote txt file
```
ping0.exe -u https://raw.githubusercontent.com/KILLME56k/ping0-hosts/master/datapacket.txt
```
