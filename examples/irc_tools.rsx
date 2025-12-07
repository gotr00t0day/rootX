; IRC Security & Reconnaissance Tools
; Similar to spylog - useful tools for IRC security research

; ============================================
; 1. IP TRACKER - Track IPs across channels
; ============================================
; Usage: !iptrack <nickname>
; Shows all IPs and channels a user has been seen in
on TEXT:!iptrack*:#:{
    if ($2) {
        set %nick = $2
        set %found = 0
        set %results = ""
        
        ; Search through IP logs
        set %total = $lines(logs/ips.txt)
        set %i = 1
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if (%nick isin %line) {
                set %found = $calc(%found + 1)
                if (%found == 1) {
                    msg $chan IP Tracking for %nick:
                }
                notice $nick %line
            }
            set %i = $calc(%i + 1)
        }
        
        if (%found == 0) {
            msg $chan %nick not found in logs
        }
        else {
            msg $chan Found %found IP record(s) for %nick (sent via PM)
        }
    }
    else {
        msg $chan Usage: !iptrack <nickname>
    }
}

; ============================================
; 2. HOSTMASK ANALYZER - Analyze hostmasks
; ============================================
; Usage: !hostmask <nickname>
; Shows hostmask patterns and IP ranges
on TEXT:!hostmask*:#:{
    if ($2) {
        set %nick = $2
        set %hosts = ""
        set %ips = ""
        set %found = 0
        
        set %total = $lines(logs/ips.txt)
        set %i = 1
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if (%nick isin %line) {
                set %found = $calc(%found + 1)
                ; Extract IP if present
                if (IP: isin %line) {
                    set %ip = $mid(%line, $calc($pos(IP: , %line) + 4), 20)
                    if (%ip) {
                        set %ips = %ips $+ %ip $+ " "
                    }
                }
                ; Extract host
                if (Host: isin %line) {
                    set %host = $mid(%line, $calc($pos(Host: , %line) + 6), 50)
                    if (%host) {
                        set %hosts = %hosts $+ %host $+ " "
                    }
                }
            }
            set %i = $calc(%i + 1)
        }
        
        if (%found > 0) {
            msg $chan Hostmask Analysis for %nick:
            msg $chan IPs seen: %ips
            msg $chan Hosts: %hosts
        }
        else {
            msg $chan %nick not found
        }
    }
}

; ============================================
; 3. CHANNEL TRACKER - Track user across channels
; ============================================
; Usage: !channels <nickname>
; Shows all channels a user has been seen in
on TEXT:!channels*:#:{
    if ($2) {
        set %nick = $2
        set %channels = ""
        set %found = 0
        
        ; Search chat logs for channel mentions
        set %total = $lines(logs/chatlog.txt)
        set %i = 1
        
        while (%i <= %total) {
            set %line = $read(logs/chatlog.txt, %i)
            if (%nick isin %line) {
                set %found = $calc(%found + 1)
                ; Extract channel from log format
                if (# isin %line) {
                    set %chan = $mid(%line, $pos(#, %line), 30)
                    if (%chan && %chan !isin %channels) {
                        set %channels = %channels $+ %chan $+ " "
                    }
                }
            }
            set %i = $calc(%i + 1)
        }
        
        if (%found > 0) {
            msg $chan %nick seen in channels: %channels
        }
        else {
            msg $chan %nick not found in logs
        }
    }
}

; ============================================
; 4. IP RANGE SEARCH - Find all users in IP range
; ============================================
; Usage: !iprange <partial-ip>
; Example: !iprange 192.168.1
; Finds all users with IPs matching the range
on TEXT:!iprange*:#:{
    if ($2) {
        set %pattern = $2
        set %found = 0
        
        set %total = $lines(logs/ips.txt)
        set %i = 1
        
        msg $chan Searching for IPs matching: %pattern
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if (%pattern isin %line) {
                set %found = $calc(%found + 1)
                notice $nick %line
            }
            set %i = $calc(%i + 1)
        }
        
        if (%found == 0) {
            msg $chan No IPs found matching %pattern
        }
        else {
            msg $chan Found %found match(es) (sent via PM)
        }
    }
}

; ============================================
; 5. USER TIMELINE - Show user activity timeline
; ============================================
; Usage: !timeline <nickname>
; Shows when user was active (joins, messages)
on TEXT:!timeline*:#:{
    if ($2) {
        set %nick = $2
        set %found = 0
        set %count = 0
        
        set %total = $lines(logs/ips.txt)
        set %i = 1
        
        msg $chan Timeline for %nick:
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if (%nick isin %line) {
                set %found = $calc(%found + 1)
                set %count = $calc(%count + 1)
                if (%count <= 10) {
                    ; Extract timestamp
                    if ([ isin %line) {
                        set %time = $mid(%line, $pos([, %line), 10)
                        msg $chan %time - %line
                    }
                }
            }
            set %i = $calc(%i + 1)
        }
        
        if (%found > 10) {
            msg $chan ... and %calc(%found - 10) more entries
        }
        
        if (%found == 0) {
            msg $chan No activity found for %nick
        }
    }
}

; ============================================
; 6. BAN EVASION DETECTOR - Detect same IP different nicks
; ============================================
; Usage: !bancheck <ip-or-nick>
; Finds all nicks using same IP (potential ban evasion)
on TEXT:!bancheck*:#:{
    if ($2) {
        set %search = $2
        set %found = 0
        set %nicks = ""
        set %target_ip = ""
        
        ; First, find the IP if a nick was provided
        set %total = $lines(logs/ips.txt)
        set %i = 1
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if (%search isin %line) {
                if (IP: isin %line) {
                    set %target_ip = $mid(%line, $calc($pos(IP: , %line) + 4), 20)
                    break
                }
            }
            set %i = $calc(%i + 1)
        }
        
        ; If no IP found, assume search term is the IP
        if (!%target_ip) {
            set %target_ip = %search
        }
        
        ; Now find all nicks with this IP
        set %i = 1
        msg $chan Checking for ban evasion (IP: %target_ip)
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if (%target_ip isin %line) {
                ; Extract nick
                if (| isin %line) {
                    set %nick = $mid(%line, $calc($pos(|, %line) + 2), 20)
                    set %nick = $left(%nick, $calc($pos( |, %nick) - 1))
                    if (%nick && %nick !isin %nicks) {
                        set %nicks = %nicks $+ %nick $+ " "
                        set %found = $calc(%found + 1)
                    }
                }
            }
            set %i = $calc(%i + 1)
        }
        
        if (%found > 1) {
            msg $chan WARNING: %found different nicks found with same IP!
            msg $chan Nicks: %nicks
        }
        else if (%found == 1) {
            msg $chan Only 1 nick found for this IP
        }
        else {
            msg $chan No matches found
        }
    }
}

; ============================================
; 7. ACTIVITY MONITOR - Show most active users
; ============================================
; Usage: !topusers [number]
; Shows most active users in logs
on TEXT:!topusers*:#:{
    set %limit = $2
    if (!%limit) {
        set %limit = 10
    }
    
    msg $chan Analyzing activity (this may take a moment)...
    ; Note: This would require more complex parsing
    ; Simplified version - just show recent activity
    msg $chan Top %limit most recent active users:
    
    set %total = $lines(logs/ips.txt)
    set %i = $calc(%total - %limit)
    if (%i < 1) {
        set %i = 1
    }
    
    while (%i <= %total) {
        set %line = $read(logs/ips.txt, %i)
        if (| isin %line) {
            set %nick = $mid(%line, $calc($pos(|, %line) + 2), 20)
            set %nick = $left(%nick, $calc($pos( |, %nick) - 1))
            if (%nick) {
                msg $chan - %nick
            }
        }
        set %i = $calc(%i + 1)
    }
}

; ============================================
; 8. NETWORK MAP - Show connections between users
; ============================================
; Usage: !network <nickname>
; Shows users who share IP ranges (same network)
on TEXT:!network*:#:{
    if ($2) {
        set %nick = $2
        set %found = 0
        set %network = ""
        
        ; Find user's IP
        set %total = $lines(logs/ips.txt)
        set %i = 1
        set %user_ip = ""
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if (%nick isin %line && IP: isin %line) {
                set %user_ip = $mid(%line, $calc($pos(IP: , %line) + 4), 20)
                ; Extract first 3 octets for network range
                set %network_base = $left(%user_ip, $calc($pos(., %user_ip, 3) + 1))
                break
            }
            set %i = $calc(%i + 1)
        }
        
        if (%network_base) {
            msg $chan Network analysis for %nick (base: %network_base):
            set %i = 1
            
            while (%i <= %total) {
                set %line = $read(logs/ips.txt, %i)
                if (%network_base isin %line) {
                    if (| isin %line) {
                        set %other_nick = $mid(%line, $calc($pos(|, %line) + 2), 20)
                        set %other_nick = $left(%other_nick, $calc($pos( |, %other_nick) - 1))
                        if (%other_nick && %other_nick != %nick) {
                            if (%other_nick !isin %network) {
                                set %network = %network $+ %other_nick $+ " "
                                set %found = $calc(%found + 1)
                            }
                        }
                    }
                }
                set %i = $calc(%i + 1)
            }
            
            if (%found > 0) {
                msg $chan Found %found user(s) on same network: %network
            }
            else {
                msg $chan No other users found on same network
            }
        }
        else {
            msg $chan Could not find IP for %nick
        }
    }
}

