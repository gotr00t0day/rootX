; ============================================
; Simple List Example - Easy to Understand
; ============================================
;
; This is a beginner-friendly example showing
; how to use lists in RootX scripting.
;
; Try these commands:
;   !add <item>    - Add item to shopping list
;   !list          - Show all items
;   !remove <item> - Remove item from list
;   !clear         - Clear shopping list
;
; ============================================

; Add item to shopping list
on TEXT:!add*:#:{
    if ($2) {
        ; Check if item already exists
        if ($list(@shopping,exists,$2) == True) {
            msg $chan $2 is already on the list!
        }
        else {
            ; Add the item
            listadd @shopping $2
            
            ; Get new count
            set %count = $list(@shopping,count)
            
            msg $chan Added $2 to shopping list! (Total: %count items)
        }
    }
    else {
        msg $chan Usage: !add <item>
        msg $chan Example: !add Milk
    }
}

; Show all items in the shopping list
on TEXT:!list:#:{
    ; Get count of items
    set %count = $list(@shopping,count)
    
    ; Check if list is empty
    if (%count == 0) {
        msg $chan Shopping list is empty! Add items with !add <item>
    }
    else {
        msg $chan === Shopping List (%count items) ===
        
        ; Use for loop to show each item
        set %i = 1
        for (%item in @shopping) {
            msg $chan %i. %item
            set %i = $calc(%i + 1)
        }
    }
}

; Remove item from shopping list
on TEXT:!remove*:#:{
    if ($2) {
        ; Check if item exists before removing
        if ($list(@shopping,exists,$2) == True) {
            listdel @shopping $2
            
            set %count = $list(@shopping,count)
            msg $chan Removed $2 from list! (%count items remaining)
        }
        else {
            msg $chan $2 is not on the shopping list!
        }
    }
    else {
        msg $chan Usage: !remove <item>
        msg $chan Example: !remove Milk
    }
}

; Clear the entire shopping list
on TEXT:!clear:#:{
    set %count = $list(@shopping,count)
    
    if (%count == 0) {
        msg $chan Shopping list is already empty!
    }
    else {
        listclear @shopping
        msg $chan Shopping list cleared! (Removed %count items)
    }
}

; Show help
on TEXT:!shophelp:#:{
    msg $chan === Shopping List Commands ===
    msg $chan !add <item> - Add item to list
    msg $chan !list - Show all items
    msg $chan !remove <item> - Remove item
    msg $chan !clear - Clear entire list
    msg $chan Example: !add Bread
}

