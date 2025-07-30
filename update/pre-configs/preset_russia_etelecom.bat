@echo off
chcp 65001 >nul
:: 65001 - UTF-8

cd /d "%~dp0..\"
set BIN=%~dp0..\bin\

set LIST_TITLE=ZAPRET: preset_russia (http,https,quic)
set LIST_PATH=%~dp0..\lists\list-ultimate.txt
set GMODE_FLAG_FILE=%BIN%gmode.flag
set DISCORD_IPSET_PATH=%~dp0..\lists\ipset-discord.txt

if exist "%GMODE_FLAG_FILE%" (
    set "GModeStatus=enabled"
    set "GModeRange=1024-65535"
) else (
    set "GModeStatus=disabled"
    set "GModeRange=0"
)

start "%LIST_TITLE%" /min "%BIN%winws.exe" ^
--wf-tcp=80,443 --wf-udp=443,50000-50099,%GModeRange% ^
--wf-l3=ipv4 --wf-tcp=443 --dpi-desync=fake,split --dpi-desync-ttl=10 --dpi-desync-fake-tls=0x00000000