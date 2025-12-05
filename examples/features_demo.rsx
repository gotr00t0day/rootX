; ============================================
; RootX Essential Features Demo Script
; ============================================
; This script demonstrates all the new mIRC-style
; features added to the RootX scripting engine
; ============================================

; ===========================================
; FILE I/O DEMONSTRATIONS
; ===========================================

; Add a quote to file
on TEXT:!addquote*:#:{
    if ($2-) {
        write quotes.txt $2-
        set %count = $lines(quotes.txt)
        msg $chan Quote #%count added by $nick!
    }
    else {
        msg $chan Usage: !addquote <text>
    }
}

; Read random quote
on TEXT:!quote:#:{
    if ($exists(quotes.txt)) {
        set %total = $lines(quotes.txt)
        if (%total > 0) {
            msg $chan Random Quote: $read(quotes.txt)
        }
        else {
            msg $chan No quotes yet! Use !addquote to add one
        }
    }
    else {
        msg $chan No quotes yet! Use !addquote to add one
    }
}

; Read specific quote by number
on TEXT:!quote*:#:{
    if ($2) {
        if ($exists(quotes.txt)) {
            set %line = $read(quotes.txt, $2)
            if (%line) {
                msg $chan Quote #$2: %line
            }
            else {
                msg $chan Quote #$2 not found
            }
        }
        else {
            msg $chan No quotes file exists
        }
    }
}

; Count quotes
on TEXT:!quotecount:#:{
    if ($exists(quotes.txt)) {
        msg $chan Total quotes: $lines(quotes.txt)
    }
    else {
        msg $chan No quotes yet!
    }
}

; Delete quotes file (admin only)
on TEXT:!clearquotes:#:{
    if ($level >= 500) {
        if ($exists(quotes.txt)) {
            remove quotes.txt
            msg $chan Quotes file cleared by $nick
        }
        else {
            msg $chan No quotes file to clear
        }
    }
    else {
        msg $chan Admin access required
    }
}

; ===========================================
; STRING TOKENIZATION DEMONSTRATIONS
; ===========================================

; Parse CSV data
on TEXT:!parse*:#:{
    ; Example: !parse apple,banana,orange
    if ($2) {
        set %data = $2
        set %count = $numtok(%data, 44)
        msg $chan Found %count items in list
        
        set %first = $gettok(%data, 1, 44)
        set %last = $gettok(%data, %count, 44)
        msg $chan First: %first | Last: %last
    }
    else {
        msg $chan Usage: !parse item1,item2,item3
    }
}

; Find item in list
on TEXT:!find*:#:{
    ; Example: !find apple,banana,orange banana
    if ($2 && $3) {
        set %list = $2
        set %search = $3
        set %pos = $findtok(%list, %search, 1, 44)
        
        if (%pos > 0) {
            msg $chan Found "%search" at position %pos
        }
        else {
            msg $chan "%search" not found in list
        }
    }
    else {
        msg $chan Usage: !find list,items searchterm
    }
}

; Add item to list
on TEXT:!additem*:#:{
    ; Example: !additem apple,banana,orange grape
    if ($2 && $3) {
        set %list = $2
        set %item = $3
        set %newlist = $addtok(%list, %item, 44)
        msg $chan New list: %newlist
    }
    else {
        msg $chan Usage: !additem currentlist newitem
    }
}

; Remove item from list
on TEXT:!remitem*:#:{
    ; Example: !remitem apple,banana,orange banana
    if ($2 && $3) {
        set %list = $2
        set %item = $3
        set %newlist = $remtok(%list, %item, 44)
        msg $chan New list: %newlist
    }
    else {
        msg $chan Usage: !remitem currentlist itemtoremove
    }
}

; Replace item in list
on TEXT:!replaceitem*:#:{
    ; Example: !replaceitem apple,banana,orange banana mango
    if ($2 && $3 && $4) {
        set %list = $2
        set %old = $3
        set %new = $4
        set %newlist = $reptok(%list, %old, %new, 44)
        msg $chan New list: %newlist
    }
    else {
        msg $chan Usage: !replaceitem list olditem newitem
    }
}

; ===========================================
; MATH OPERATION DEMONSTRATIONS
; ===========================================

; Calculator
on TEXT:!calc*:#:{
    if ($2-) {
        set %result = $calc($2-)
        msg $chan Result: $2- = %result
    }
    else {
        msg $chan Usage: !calc <expression>
        msg $chan Example: !calc 5 + 3 * 2
    }
}

; Round numbers
on TEXT:!round*:#:{
    if ($2 && $3) {
        set %rounded = $round($2, $3)
        msg $chan $2 rounded to $3 decimals: %rounded
    }
    else {
        msg $chan Usage: !round <number> <decimals>
    }
}

; Absolute value
on TEXT:!abs*:#:{
    if ($2) {
        msg $chan Absolute value of $2: $abs($2)
    }
}

; Square root
on TEXT:!sqrt*:#:{
    if ($2) {
        msg $chan Square root of $2: $sqrt($2)
    }
}

; Advanced math
on TEXT:!math*:#:{
    msg $chan === Math Examples ===
    msg $chan $calc(10 + 5) = $calc(10 + 5)
    msg $chan $calc(10 * 5) = $calc(10 * 5)
    msg $chan $calc(10 / 3) = $calc(10 / 3)
    msg $chan $round($calc(10 / 3), 2) = $round($calc(10 / 3), 2)
    msg $chan $sqrt(16) = $sqrt(16)
    msg $chan $abs(-42) = $abs(-42)
}

; ===========================================
; STRING FUNCTION DEMONSTRATIONS
; ===========================================

; Find position of substring
on TEXT:!pos*:#:{
    ; Example: !pos hello world world
    if ($2 && $3) {
        set %text = $2
        set %search = $3
        set %position = $pos(%text, %search)
        
        if (%position > 0) {
            msg $chan "%search" found at position %position in "%text"
        }
        else {
            msg $chan "%search" not found in "%text"
        }
    }
    else {
        msg $chan Usage: !pos <text> <search>
    }
}

; Replace text
on TEXT:!replace*:#:{
    ; Example: !replace hello old new
    if ($2 && $3 && $4) {
        set %result = $replace($2, $3, $4)
        msg $chan Result: %result
    }
    else {
        msg $chan Usage: !replace <text> <old> <new>
    }
}

; Remove text
on TEXT:!removetext*:#:{
    ; Example: !removetext helloworld world
    if ($2 && $3) {
        set %result = $remove($2, $3)
        msg $chan Result: %result
    }
    else {
        msg $chan Usage: !removetext <text> <remove>
    }
}

; Repeat text
on TEXT:!repeat*:#:{
    ; Example: !repeat LOL 5
    if ($2 && $3) {
        msg $chan $str($2, $3)
    }
    else {
        msg $chan Usage: !repeat <text> <count>
    }
}

; ASCII conversions
on TEXT:!ascii*:#:{
    if ($2) {
        set %char = $chr($2)
        msg $chan ASCII $2 = %char
    }
    else {
        msg $chan Usage: !ascii <number>
    }
}

on TEXT:!charcode*:#:{
    if ($2) {
        set %code = $asc($2)
        msg $chan Character $2 = ASCII %code
    }
    else {
        msg $chan Usage: !charcode <character>
    }
}

; ===========================================
; COMBINED FEATURE DEMONSTRATIONS
; ===========================================

; Advanced quote system with stats
on TEXT:!addadvquote*:#:{
    if ($2-) {
        ; Add quote to file
        write adv_quotes.txt $2-
        
        ; Track who added it
        set %count = $lines(adv_quotes.txt)
        write quote_authors.txt $nick
        
        ; Calculate statistics
        set %total = $lines(adv_quotes.txt)
        msg $chan Quote #%total added by $nick!
    }
}

on TEXT:!randomquote:#:{
    if ($exists(adv_quotes.txt)) {
        set %total = $lines(adv_quotes.txt)
        set %rand = $calc($rand(%total) + 1)
        set %quote = $read(adv_quotes.txt, %rand)
        set %author = $read(quote_authors.txt, %rand)
        msg $chan [Quote #%rand] %quote - added by %author
    }
}

; Statistics calculator
on TEXT:!average*:#:{
    ; Example: !average 10,20,30,40,50
    if ($2) {
        set %numbers = $2
        set %count = $numtok(%numbers, 44)
        set %sum = 0
        
        ; This is a simplified version - mIRC would use a loop
        ; For demonstration, assume 3 numbers
        set %n1 = $gettok(%numbers, 1, 44)
        set %n2 = $gettok(%numbers, 2, 44)
        set %n3 = $gettok(%numbers, 3, 44)
        
        set %sum = $calc(%n1 + %n2 + %n3)
        set %avg = $calc(%sum / 3)
        set %rounded = $round(%avg, 2)
        
        msg $chan Sum: %sum | Average: %rounded
    }
}

; Word manipulation
on TEXT:!shout*:#:{
    if ($2-) {
        set %loud = $upper($2-)
        set %repeated = $str(%loud, 3)
        msg $chan %repeated
    }
}

; List manager
on TEXT:!manageadmins*:#:{
    if ($level >= 500) {
        ; Read current admin list
        if ($exists(admin_list.txt)) {
            set %admins = $read(admin_list.txt, 1)
        }
        else {
            set %admins = 
        }
        
        if ($2 == add && $3) {
            set %admins = $addtok(%admins, $3, 44)
            remove admin_list.txt
            write admin_list.txt %admins
            msg $chan Added $3 to admin list
        }
        else if ($2 == remove && $3) {
            set %admins = $remtok(%admins, $3, 44)
            remove admin_list.txt
            write admin_list.txt %admins
            msg $chan Removed $3 from admin list
        }
        else if ($2 == list) {
            msg $chan Admins: %admins
        }
        else {
            msg $chan Usage: !manageadmins <add|remove|list> [nick]
        }
    }
}

; ===========================================
; HELP COMMAND
; ===========================================

on TEXT:!features:#:{
    msg $chan === RootX Essential Features Demo ===
    msg $chan FILE I/O: !addquote, !quote, !quotecount
    msg $chan TOKENS: !parse, !find, !additem, !remitem
    msg $chan MATH: !calc, !round, !abs, !sqrt, !average
    msg $chan STRINGS: !pos, !replace, !removetext, !repeat
    msg $chan ASCII: !ascii, !charcode
    msg $chan ADVANCED: !addadvquote, !randomquote, !manageadmins
    msg $chan Type any command for usage info!
}

alias /featureshelp {
    echo === RootX New Features ===
    echo File I/O: write, read, remove, $read(), $exists(), $lines()
    echo Tokens: $gettok(), $numtok(), $findtok(), $addtok(), $remtok()
    echo Math: $calc(), $round(), $abs(), $sqrt(), $floor(), $ceil()
    echo Strings: $pos(), $replace(), $remove(), $str(), $chr(), $asc()
    echo Type !features in a channel for interactive demo
}

; ===========================================
; BONUS: Practical Examples
; ===========================================

; Simple todo list
on TEXT:!todo*:#:{
    if ($2 == add && $3-) {
        write todo.txt [$nick] $3-
        msg $chan Todo added: $3-
    }
    else if ($2 == list) {
        if ($exists(todo.txt)) {
            set %count = $lines(todo.txt)
            msg $chan You have %count todos. Use !todo show <number>
        }
        else {
            msg $chan No todos yet
        }
    }
    else if ($2 == show && $3) {
        set %todo = $read(todo.txt, $3)
        msg $chan Todo #$3: %todo
    }
    else {
        msg $chan Usage: !todo <add|list|show> [text|number]
    }
}

; Roll multiple dice
on TEXT:!rolldice*:#:{
    if ($2) {
        set %dice = $2
        set %roll1 = $calc($rand(6) + 1)
        set %roll2 = $calc($rand(6) + 1)
        set %total = $calc(%roll1 + %roll2)
        msg $chan $nick rolled %dice dice: %roll1 + %roll2 = %total
    }
    else {
        set %roll = $calc($rand(6) + 1)
        msg $chan $nick rolled: %roll
    }
}

; Temperature converter
on TEXT:!temp*:#:{
    if ($2 && $3) {
        if ($3 == F) {
            ; Celsius to Fahrenheit
            set %f = $calc(($2 * 9/5) + 32)
            set %f = $round(%f, 1)
            msg $chan $2°C = %f°F
        }
        else if ($3 == C) {
            ; Fahrenheit to Celsius
            set %c = $calc(($2 - 32) * 5/9)
            set %c = $round(%c, 1)
            msg $chan $2°F = %c°C
        }
    }
    else {
        msg $chan Usage: !temp <value> <C|F>
    }
}

; String utilities
on TEXT:!strutil*:#:{
    msg $chan === String Utilities Demo ===
    set %test = hello world
    msg $chan Original: %test
    msg $chan Position of 'world': $pos(%test, world)
    msg $chan Uppercase: $upper(%test)
    msg $chan Replace 'world' with 'IRC': $replace(%test, world, IRC)
    msg $chan Remove 'world': $remove(%test, world)
    msg $chan Repeat 3 times: $str(Hi!, 3)
    msg $chan Length: $len(%test)
}

; CSV parser
on TEXT:!csv*:#:{
    ; Example: !csv Name,Age,City Alice,25,NYC
    if ($2 && $3) {
        set %headers = $2
        set %data = $3
        
        set %num_fields = $numtok(%headers, 44)
        msg $chan Parsing CSV with %num_fields fields...
        
        set %h1 = $gettok(%headers, 1, 44)
        set %d1 = $gettok(%data, 1, 44)
        msg $chan %h1: %d1
        
        set %h2 = $gettok(%headers, 2, 44)
        set %d2 = $gettok(%data, 2, 44)
        msg $chan %h2: %d2
        
        set %h3 = $gettok(%headers, 3, 44)
        set %d3 = $gettok(%data, 3, 44)
        msg $chan %h3: %d3
    }
}

; ===========================================
; COMMON ASCII CODES (for reference)
; ===========================================
; 32  = space
; 44  = comma (,)
; 46  = period (.)
; 58  = colon (:)
; 59  = semicolon (;)
; 124 = pipe (|)
; ===========================================

