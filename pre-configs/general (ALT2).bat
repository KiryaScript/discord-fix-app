::[Bat To Exe Converter]
::
::YAwzoRdxOk+EWAjk
::fBw5plQjdG8=
::YAwzuBVtJxjWCl3EqQJgSA==
::ZR4luwNxJguZRRnk
::Yhs/ulQjdF+5
::cxAkpRVqdFKZSjk=
::cBs/ulQjdF+5
::ZR41oxFsdFKZSDk=
::eBoioBt6dFKZSDk=
::cRo6pxp7LAbNWATEpCI=
::egkzugNsPRvcWATEpCI=
::dAsiuh18IRvcCxnZtBJQ
::cRYluBh/LU+EWAnk
::YxY4rhs+aU+IeA==
::cxY6rQJ7JhzQF1fEqQJnZkoaHmQ=
::ZQ05rAF9IBncCkqN+0xwdVsFAlTi
::ZQ05rAF9IAHYFVzEqQI3LRVRXgWOfCObKoFOoYg=
::eg0/rx1wNQPfEVWB+kM9LVsJDAOHMm6oB7l8
::fBEirQZwNQPfEVWB+kM9LVsJDGQ=
::cRolqwZ3JBvQF1fEqQKA2KuP/egz3ttvt1WsNVgrXgg3ev3P5D+Okz8CmgRZkDCjNfQHxHedDDrqRnvdvf7ooKJ/3t9U
::dhA7uBVwLU+EWH2B4ks7HD51YWQ=
::YQ03rBFzNR3SWATElA==
::dhAmsQZ3MwfNWATE0EcmIRBgaSWvXA==
::ZQ0/vhVqMQ3MEVWAtB9wSA==
::Zg8zqx1/OA3MEVWAtB9wSA==
::dhA7pRFwIByZRRnk
::Zh4grVQjdCyDJGyX8VAjFBBdXg2OAES0A5EO4f7+086IoVgQUewra7P806CmNeIv7kz3dpk/0jdckdNBDQtIQheza084qHtMtWy5MMKSth3gRgjBx2cESSw6gnvV7A==
::YB416Ek+ZW8=
::
::
::978f952a14a936cc963da21a135fa983
@echo off
chcp 65001 >nul
:: 65001 - UTF-8

cd /d "%~dp0..\"
set BIN=%~dp0..\bin\

set LIST_TITLE=general_ALT2
set LIST_PATH=%~dp0..\lists\list-ultimate.txt
set DISCORD_IPSET_PATH=%~dp0..\lists\ipset-discord.txt
set CLOUDFLARE_IPSET_PATH=%~dp0..\lists\ipset-cloudflare.txt

start "%LIST_TITLE%" /min "%BIN%winws.exe" --wf-tcp=80,443 --wf-udp=443,50000-50100 ^
--filter-udp=443 --hostlist="%LIST_PATH%" --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic="%BIN%quic_initial_www_google_com.bin" --new ^
--filter-udp=50000-50100 --ipset="%DISCORD_IPSET_PATH%" --dpi-desync=fake --dpi-desync-any-protocol --dpi-desync-cutoff=d3 --dpi-desync-repeats=6 --new ^
--filter-tcp=80 --hostlist="%LIST_PATH%" --dpi-desync=fake,split2 --dpi-desync-autottl=2 --dpi-desync-fooling=md5sig --new ^
--filter-tcp=443 --hostlist="%LIST_PATH%" --dpi-desync=split2 --dpi-desync-split-seqovl=652 --dpi-desync-split-pos=2 --dpi-desync-split-seqovl-pattern="%BIN%tls_clienthello_www_google_com.bin" --new ^
--filter-udp=443 --ipset="%CLOUDFLARE_IPSET_PATH%" --dpi-desync=fake --dpi-desync-repeats=6 --dpi-desync-fake-quic="%BIN%quic_initial_www_google_com.bin" --new ^
--filter-tcp=80 --ipset="%CLOUDFLARE_IPSET_PATH%" --dpi-desync=fake,split2 --dpi-desync-autottl=2 --dpi-desync-fooling=md5sig --new ^
--filter-tcp=443 --ipset="%CLOUDFLARE_IPSET_PATH%" --dpi-desync=split2 --dpi-desync-split-seqovl=652 --dpi-desync-split-pos=2 --dpi-desync-split-seqovl-pattern="%BIN%tls_clienthello_www_google_com.bin"