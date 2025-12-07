; Private Message Handler
; Demonstrates the MSG event for private messages

; Auto-reply to private messages containing "help"
on MSG:*help*:?:{
    msg $nick Hi $nick! I received your message: $text
    msg $nick Available commands: !info, !version
}

; Respond to !info in private messages
on MSG:!info*:?:{
    msg $nick Bot Information:
    msg $nick - Running RootX IRC Client
    msg $nick - Script Engine: Active
    msg $nick - Your address: $address
}

; Respond to !info in channels
on TEXT:!info*:#:{
    msg $chan Bot Information: Running RootX IRC Client - Script Engine Active
}

; Respond to !version in private messages
on MSG:!version*:?:{
    msg $nick RootX Version: $version
}

; Respond to !version in channels
on TEXT:!version*:#:{
    msg $chan RootX Version: $version
}

; Log all private messages (optional)
on MSG:*:?:{
    echo [PM] $nick said: $text
}

