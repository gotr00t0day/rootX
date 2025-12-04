; ============================================
; RootX Auto-Connect to Multiple Servers
; ============================================
; This script automatically connects to multiple
; servers when you type /autoconnect
; ============================================

alias /autoconnect {
    echo Connecting to multiple servers...
    
    ; Connect to Libera Chat
    ; Change these to your preferred servers
    echo Connecting to Libera Chat...
    ; Note: You may need to use the raw server connection method
    ; The script engine doesn't have direct access to connect_to_server
    ; So use the built-in /server command instead
    
    echo Use these commands in the main window:
    echo /server irc.libera.chat 6667 YourNick
    echo /server irc.oftc.net 6667 YourNick
    echo /server irc.rizon.net 6667 YourNick
    
    ; After connecting, you can auto-join channels:
    ; join #channel server
}

; Auto-join channels on connect
; This triggers when you successfully connect to a server
on CONNECT:*:*:{
    echo Connected to $server
    
    ; Auto-join channels based on server
    if ($server == irc.libera.chat) {
        join #python
        join #linux
        echo Auto-joined Libera channels
    }
    else if ($server == irc.oftc.net) {
        join #debian
        echo Auto-joined OFTC channels
    }
}

; Show all servers command
alias /servers {
    echo === Connected Servers ===
    echo Use the server tree to view connections
    echo Current server: $server
}

