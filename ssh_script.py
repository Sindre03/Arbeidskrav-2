import time, sys, getpass
try:
    import serial #krever pip install pyserial
except:
    sys.exit("Mangler pyserial")

#Leser input-buffer fra seriellport
def read_all(ser, delay=0.3, show=True):
    time.sleep(delay)
    out = b""
    while ser.in_waiting:
        out += ser.read(ser.in_waiting)
        time.sleep(0.05)
    if show and out:
        try: 
            print(out.decode(errors="ignore"), end="")
        except: 
            pass
    return out

#Sender IOS-kommando
def send(ser, cmd, wait=0.5, show=True):
    if cmd is not None:
        ser.write((cmd + "\r").encode())
    return read_all(ser, delay=wait, show=show)

#samler nødvendige verdier
print("Cisco SSH setup via konsoll")
port = input("Seriellport (COM1): ").strip()
baud = input("Baud [9600]: ").strip() or "9600"
device = (input("Enhetstype (switch/router) [switch]: ").strip() or "switch").lower()

hostname = input("Hostname: ").strip()
domain = input("IP domain-name: ").strip()
username = input("Admin-bruker: ").strip()
user_secret = getpass.getpass("Passord til admin- bruker: ")
enable_secret = getpass.getpass("Enable secret (NYTT): ")
existing_enable = getpass.getpass("Eksisterende enable-pass (tom hvis ingen): " )

mgmt_if = input("Mgmt-interface (vlan1 / vlan10 / g0/0 osv): ").strip()
mgmt_ip = input("Mgmt IP (f.eks 192.168.10.99): ")
mgmt_mask = input("Mgmt subnetmaske (f.eks. 255.255.255.0): ").strip()
gateway = input("Default gateway [valgfri]: ").strip()

#Åpner Seriellport
print(f"\n[info] Åpner {port} @ {baud} 8N1 ...")
ser = serial.Serial(port, int(baud), timeout=1)
time.sleep(1.0)

#Skip initial config
for _ in range(3):
    send(ser, "", wait=0.4, show=False)
    buf = read_all(ser, delay=0.5, show=False)
    if b"initial configuration dialog" in buf or b"Would you like to enter the initial configuration dialog" in buf:
        send(ser, "no", wait=0.6)
        send(ser, "", wait=0.6)
        break

#Enable modus
buf = send(ser, "enable", wait=0.6)
if b"Password" in buf and existing_enable:
    send(ser, existing_enable, wait=0.8)

#grunnkonfig
send(ser, "terminal length 0", show=False)
send(ser, "configure terminal")
send(ser, f"hostname {hostname}")
send(ser, "no ip domain-lookup", show=False)
send(ser, "no ip domain lookup", show=False)
send(ser, f"ip domain-name {domain}", show=False)
send(ser, f"ip domain name {domain}", show=False)
send(ser, f"enable secret {enable_secret}")
send(ser, "service password-encryption")
send(ser, f"username {username} privilege 15 secret {user_secret}")

#SSH
send(ser, "ip ssh version 2")
send(ser, "crypto key generate rsa modulus 2048")
time.sleep(2)

#VTY linjer kun SSH
send(ser, "line vty 0 4")
send(ser, "login local")
send(ser, "transport input ssh")
send(ser, "exec-timeout 10 0")
send(ser, "exit")

#Management-interface
send(ser, f"interface {mgmt_if}")
send(ser, "description MGMT by script")
send(ser, f"ip address {mgmt_ip} {mgmt_mask}")
send(ser, "no shutdown")
send(ser, "exit")

#Gateway / default route
if device.startswith("sw") and gateway:
    send(ser, f"ip default-gateway {gateway}")
elif device.startswith("ro") and gateway:
    send(ser, f"ip route 0.0.0.0 0.0.0.0 {gateway}")

#Lagre
send(ser, "end")
send(ser, "write memory")
print("\n Ferdig! Test ping/SSH fra PC i samme nett.")
ser.close() 