; ========================================
; SpyLog v1.0
; ========================================

; Description: Spy on a IRC channel, log texts and ips among other things
; Author: c0d3Ninja
;
; ========================================


on JOIN:*:#:{
    write logs/join.log [$time] $server $nick ($address) JOIN $chan
}

on TEXT:*:#:{
    if ($nick != $me) {
        write logs/chatlog.log [$time] $server $chan $nick ($address): $text
    }
}

; Log ip addresses and hosts
on JOIN:*:#:{
    if ($nick != $me) {
        if ($ip) {
            ; Check for duplicates
            if ($read(ips.txt, w, *$ip*)) {
                return
            }
            write logs/ips.txt [$time] $nick | IP: $ip | Host: $host | Address: $address
        }
    }
}

; Check for a specific user information in the logs
on TEXT:!spylog*:#:{
    if ($2) {
        msg $chan Searching for $2...
        set %total = $lines(logs/ips.txt)
        set %i = 1
        set %found = 0
        
        while (%i <= %total) {
            set %line = $read(logs/ips.txt, %i)
            if ($2 isin %line) {
                notice $nick %line
                set %found = $calc(%found + 1)
            }
            set %i = $calc(%i + 1)
        }
        
        if (%found == 0) {
            msg $chan $2 not found in logs
        }
        else {
            msg $chan Found %found result(s) for $2
        }
    }
    else {
        msg $chan Usage: !spylog <username>
    }
}