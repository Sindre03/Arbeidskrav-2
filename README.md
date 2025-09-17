# Arbeidskrav 2 Automatisering

Dette repoet inneholder et python script som etter opp SSH på en cisco switch eller router

## Krav
- Python3
- pyserial
- konsollkabel

## Bruk
Koble konsollkabel fra pc til enhet
COM-port er vanligvis COM1. kan være  COM3 / COM4
I powershell:
endre lokasjon til script mappen (kommando: cd)
kjør script filen (kommando:python .\ssh_script.py)

fyll inn:
COM-port
baud (f.eks. 9600)
enhetstype (switch/router)
hostname
domain name
admin username
passord
enable secret
mgmt interface
mgmt IP
mgmt subnetmask
default gateway

## Koble til SSH
endre IP på pc til et i samme subnet som MGMT IP
I powershell:
ssh <username>@<mgmt IP>
skriv inn passord
