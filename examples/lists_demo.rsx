; ============================================
; Lists Demo - RootX Scripting
; ============================================
;
; This script demonstrates the new list/array functionality
; in RootX scripting language.
;
; Author: RootX
; ============================================

; ============================================
; EXAMPLE 1: Basic List Operations
; ============================================
; Command: !listdemo
on TEXT:!listdemo:#:{
    echo === List Demo Started ===
    
    ; Create a list and add items
    listclear @demo
    listadd @demo Apple
    listadd @demo Banana
    listadd @demo Cherry
    listadd @demo Date
    
    ; Show count
    set %count = $list(@demo,count)
    echo List has %count items
    msg $chan List has %count items
    
    ; Show individual items
    echo Item 0: $list(@demo,0)
    echo Item 1: $list(@demo,1)
    echo Item 2: $list(@demo,2)
    msg $chan First item: $list(@demo,0), Last item: $list(@demo,3)
    
    echo === List Demo Complete ===
}

; ============================================
; EXAMPLE 2: For Loop - Iterate Over List
; ============================================
; Command: !fruits
on TEXT:!fruits:#:{
    ; Clear and populate fruits list
    listclear @fruits
    listadd @fruits Apple
    listadd @fruits Banana
    listadd @fruits Cherry
    listadd @fruits Grape
    listadd @fruits Orange
    
    msg $chan === Fruit List ===
    
    ; Iterate and display each fruit
    for (%fruit in @fruits) {
        msg $chan - %fruit
    }
    
    set %total = $list(@fruits,count)
    msg $chan Total fruits: %total
}

; ============================================
; EXAMPLE 3: User List Management
; ============================================
; Add user to a list: !adduser <name>
on TEXT:!adduser*:#:{
    if ($2) {
        ; Check if user already exists
        if ($list(@users,exists,$2) == True) {
            msg $chan $2 is already in the user list!
        }
        else {
            listadd @users $2
            set %count = $list(@users,count)
            msg $chan Added $2 to the list! Total users: %count
        }
    }
    else {
        msg $chan Usage: !adduser <name>
    }
}

; Remove user from list: !deluser <name>
on TEXT:!deluser*:#:{
    if ($2) {
        if ($list(@users,exists,$2) == True) {
            listdel @users $2
            set %count = $list(@users,count)
            msg $chan Removed $2 from the list. Total users: %count
        }
        else {
            msg $chan $2 is not in the user list.
        }
    }
    else {
        msg $chan Usage: !deluser <name>
    }
}

; Show all users: !users
on TEXT:!users:#:{
    set %count = $list(@users,count)
    
    if (%count == 0) {
        msg $chan User list is empty!
    }
    else {
        msg $chan === User List (%count users) ===
        for (%user in @users) {
            msg $chan - %user
        }
    }
}

; Clear all users: !clearusers
on TEXT:!clearusers:#:{
    listclear @users
    msg $chan User list cleared!
}

; ============================================
; EXAMPLE 4: Word Filter with Lists
; ============================================
; Add a banned word: !ban <word>
on TEXT:!ban*:#:{
    if ($islevel($nick,100) == True) {
        if ($2) {
            listadd @@badwords $2
            set %count = $list(@@badwords,count)
            msg $chan Added "$2" to filter. Total: %count words
        }
    }
    else {
        msg $chan $nick You need operator level (100+) to use this command.
    }
}

; Check messages for banned words
on TEXT:*:#:{
    if ($nick != $me) {
        ; Check each word in the message
        set %word1 = $1
        set %word2 = $2
        set %word3 = $3
        
        ; Check if any word is in the banned list
        if ($list(@@badwords,exists,%word1) == True) {
            msg $chan $nick Please don't use that word!
        }
    }
}

; ============================================
; EXAMPLE 5: Quote System
; ============================================
; Add a quote: !addquote <text>
on TEXT:!addquote*:#:{
    if ($2-) {
        listadd @@quotes $2-
        set %count = $list(@@quotes,count)
        msg $chan Quote added! (Total: %count quotes)
    }
    else {
        msg $chan Usage: !addquote <your quote here>
    }
}

; Get random quote: !quote
on TEXT:!quote:#:{
    set %count = $list(@@quotes,count)
    
    if (%count == 0) {
        msg $chan No quotes available! Add one with !addquote
    }
    else {
        ; Get random index
        set %idx = $rand(%count)
        set %quote = $list(@@quotes,%idx)
        msg $chan Quote #%idx: %quote
    }
}

; Show all quotes: !quotes
on TEXT:!quotes:#:{
    set %count = $list(@@quotes,count)
    
    if (%count == 0) {
        msg $chan No quotes available!
    }
    else {
        msg $chan === Quote List (%count quotes) ===
        set %i = 0
        for (%quote in @@quotes) {
            msg $chan %i. %quote
            set %i = $calc(%i + 1)
        }
    }
}

; ============================================
; EXAMPLE 6: Todo List
; ============================================
; Add todo: !todo add <task>
on TEXT:!todo add*:#:{
    if ($3-) {
        listadd @todos $3-
        set %count = $list(@todos,count)
        msg $chan $nick Todo added! You have %count tasks.
    }
    else {
        msg $chan Usage: !todo add <your task>
    }
}

; List todos: !todo list
on TEXT:!todo list:#:{
    set %count = $list(@todos,count)
    
    if (%count == 0) {
        msg $chan $nick You have no todos!
    }
    else {
        msg $chan === Your Todos (%count tasks) ===
        set %i = 0
        for (%task in @todos) {
            msg $chan %i. %task
            set %i = $calc(%i + 1)
        }
    }
}

; Complete todo: !todo done <index>
on TEXT:!todo done*:#:{
    if ($3) {
        set %idx = $3
        set %count = $list(@todos,count)
        
        ; Check if index is valid
        if (%idx >= 0) {
            if (%idx < %count) {
                set %task = $list(@todos,%idx)
                listdel @todos %idx
                msg $chan $nick Completed: %task
            }
            else {
                msg $chan $nick Invalid index! Use !todo list to see your tasks.
            }
        }
    }
    else {
        msg $chan Usage: !todo done <index>
    }
}

; Clear all todos: !todo clear
on TEXT:!todo clear:#:{
    listclear @todos
    msg $chan $nick All todos cleared!
}

; ============================================
; EXAMPLE 7: Vote/Poll System
; ============================================
; Start a poll: !poll <question>
on TEXT:!poll*:#:{
    if ($2-) {
        set %%poll_question = $2-
        listclear @@votes
        msg $chan === POLL STARTED ===
        msg $chan Question: %%poll_question
        msg $chan Vote with: !vote <your answer>
        msg $chan End with: !pollend
    }
    else {
        msg $chan Usage: !poll <your question>
    }
}

; Cast a vote: !vote <answer>
on TEXT:!vote*:#:{
    if ($2-) {
        listadd @@votes $nick: $2-
        msg $chan $nick Your vote has been recorded!
    }
    else {
        msg $chan Usage: !vote <your answer>
    }
}

; End poll and show results: !pollend
on TEXT:!pollend:#:{
    set %count = $list(@@votes,count)
    
    if (%count == 0) {
        msg $chan No votes recorded!
    }
    else {
        msg $chan === POLL RESULTS ===
        msg $chan Question: %%poll_question
        msg $chan Total votes: %count
        msg $chan === Votes ===
        for (%vote in @@votes) {
            msg $chan - %vote
        }
    }
    
    listclear @@votes
    set %%poll_question = 
}

; ============================================
; HELP COMMAND
; ============================================
on TEXT:!listhelp:#:{
    msg $chan === List Commands Demo ===
    msg $chan !listdemo - Basic list demo
    msg $chan !fruits - Show fruit list with for loop
    msg $chan !adduser <name> - Add user to list
    msg $chan !deluser <name> - Remove user from list
    msg $chan !users - Show all users
    msg $chan !addquote <text> - Add a quote
    msg $chan !quote - Get random quote
    msg $chan !quotes - List all quotes
    msg $chan !todo add/list/done/clear - Todo list
    msg $chan !poll <q> / !vote <a> / !pollend - Polls
}

