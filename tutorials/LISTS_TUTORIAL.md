# 📋 RootX Lists Tutorial

Welcome to the RootX Lists (Arrays) tutorial! Lists allow you to store multiple values and iterate over them, making your scripts much more powerful.

## 📚 Table of Contents

1. [What are Lists?](#what-are-lists)
2. [Creating and Adding to Lists](#creating-and-adding-to-lists)
3. [Accessing List Items](#accessing-list-items)
4. [Removing Items](#removing-items)
5. [Iterating with For Loops](#iterating-with-for-loops)
6. [List Identifiers](#list-identifiers)
7. [Local vs Global Lists](#local-vs-global-lists)
8. [Practical Examples](#practical-examples)
9. [Best Practices](#best-practices)

---

## What are Lists?

**Lists** (also called arrays) are containers that can hold multiple values. Think of them like a shopping list or a collection of items.

### Why Use Lists?

- Store multiple related values
- Keep track of users, quotes, todos, etc.
- Process collections of data
- Build more complex features

### List Syntax

```mirc
@listname      - Local list (temporary)
@@listname     - Global list (persistent)
```

Local lists are cleared when scripts reload. Global lists persist across script reloads.

---

## Creating and Adding to Lists

### Adding Items to a List

Use the `listadd` command:

```mirc
listadd @mylist Item1
listadd @mylist Item2
listadd @mylist Item3
```

**Example: Building a Fruit List**

```mirc
on TEXT:!makefruits:#:{
    listadd @fruits Apple
    listadd @fruits Banana
    listadd @fruits Cherry
    msg $chan Created fruit list!
}
```

### Adding Dynamic Content

You can add variables and identifiers:

```mirc
on JOIN:#:{
    listadd @joiners $nick
    msg $chan Welcome $nick! You're visitor number $list(@joiners,count)
}
```

---

## Accessing List Items

### Get Item by Index

Lists use **zero-based indexing** (first item is 0):

```mirc
$list(@listname,0)   ; First item
$list(@listname,1)   ; Second item
$list(@listname,2)   ; Third item
```

**Example:**

```mirc
on TEXT:!first:#:{
    set %first = $list(@fruits,0)
    msg $chan First fruit: %first
}
```

### Get Count of Items

```mirc
$list(@listname,count)
```

**Example:**

```mirc
on TEXT:!count:#:{
    set %total = $list(@fruits,count)
    msg $chan We have %total fruits
}
```

### Check if Item Exists

```mirc
$list(@listname,exists,value)
```

Returns `True` or `False`.

**Example:**

```mirc
on TEXT:!check*:#:{
    if ($list(@fruits,exists,$2) == True) {
        msg $chan Yes, we have $2!
    }
    else {
        msg $chan No, we don't have $2.
    }
}
```

### Find Index of Item

```mirc
$list(@listname,find,value)
```

Returns the index or `-1` if not found.

**Example:**

```mirc
on TEXT:!findpos*:#:{
    set %pos = $list(@fruits,find,$2)
    if (%pos >= 0) {
        msg $chan $2 is at position %pos
    }
    else {
        msg $chan $2 not found in list
    }
}
```

---

## Removing Items

### Remove by Index

```mirc
listdel @listname 0    ; Remove first item
listdel @listname 2    ; Remove third item
```

### Remove by Value

```mirc
listdel @listname Apple    ; Remove "Apple" from list
```

**Example:**

```mirc
on TEXT:!remove*:#:{
    if ($2) {
        listdel @fruits $2
        msg $chan Removed $2 from the list
    }
}
```

### Clear All Items

```mirc
listclear @listname
```

**Example:**

```mirc
on TEXT:!clearall:#:{
    listclear @fruits
    msg $chan List cleared!
}
```

### Insert at Specific Position

```mirc
listinsert @listname 0 First    ; Insert at beginning
listinsert @listname 2 Middle   ; Insert at index 2
```

---

## Iterating with For Loops

This is where lists become really powerful! Use `for` loops to process each item.

### Basic For Loop Syntax

```mirc
for (%variable in @listname) {
    ; commands here
    ; %variable contains current item
}
```

### Example: Display All Items

```mirc
on TEXT:!showall:#:{
    for (%fruit in @fruits) {
        msg $chan - %fruit
    }
}
```

### Example: Process Each Item

```mirc
on TEXT:!greetall:#:{
    for (%person in @users) {
        msg $chan Hello %person, how are you?
    }
}
```

### Example: With Counter

```mirc
on TEXT:!numbered:#:{
    set %i = 0
    for (%item in @mylist) {
        msg $chan %i. %item
        set %i = $calc(%i + 1)
    }
}
```

---

## List Identifiers

### Complete Reference

| Identifier | Description | Returns |
|------------|-------------|---------|
| `$list(@list,N)` | Get item at index N | String or empty |
| `$list(@list,count)` | Get number of items | Integer |
| `$list(@list,find,value)` | Find index of value | Integer (-1 if not found) |
| `$list(@list,exists,value)` | Check if exists | `True` or `False` |

### Usage Examples

```mirc
; Get specific items
echo $list(@fruits,0)          ; First
echo $list(@fruits,1)          ; Second

; Check count
if ($list(@fruits,count) > 0) {
    echo List has items!
}

; Check existence before adding
if ($list(@users,exists,Bob) != True) {
    listadd @users Bob
}

; Find position
set %pos = $list(@words,find,hello)
if (%pos >= 0) {
    echo Found at position %pos
}
```

---

## Local vs Global Lists

### Local Lists (@list)

- Use single `@` prefix
- Temporary (cleared on script reload)
- Good for temporary data

```mirc
listadd @temp_users $nick
```

### Global Lists (@@list)

- Use double `@@` prefix
- Persistent (saved across reloads)
- Good for permanent data

```mirc
listadd @@quotes $1-
```

### When to Use Each

**Use Local Lists for:**
- Temporary tracking
- Session-specific data
- Data that should reset

**Use Global Lists for:**
- Quotes, facts, database items
- User preferences
- Anything that should persist

---

## Practical Examples

### Example 1: Quote System

```mirc
; Add quote
on TEXT:!addquote*:#:{
    if ($2-) {
        listadd @@quotes $2-
        set %count = $list(@@quotes,count)
        msg $chan Quote #%count added!
    }
}

; Random quote
on TEXT:!quote:#:{
    set %count = $list(@@quotes,count)
    if (%count > 0) {
        set %idx = $rand(%count)
        set %quote = $list(@@quotes,%idx)
        msg $chan Quote #%idx: %quote
    }
}

; List all quotes
on TEXT:!quotes:#:{
    set %count = $list(@@quotes,count)
    msg $chan === %count Quotes ===
    set %i = 0
    for (%q in @@quotes) {
        msg $chan %i. %q
        set %i = $calc(%i + 1)
    }
}
```

### Example 2: User Tracking

```mirc
; Track who joins
on JOIN:#:{
    if ($list(@recent,exists,$nick) != True) {
        listadd @recent $nick
        msg $chan Welcome $nick! New user detected.
    }
}

; Show recent joiners
on TEXT:!recent:#:{
    msg $chan Recent joins:
    for (%user in @recent) {
        msg $chan - %user
    }
}
```

### Example 3: Todo List

```mirc
; Add todo
on TEXT:!todo add*:#:{
    if ($3-) {
        listadd @todos $3-
        set %num = $list(@todos,count)
        msg $chan $nick Todo added! (%num total)
    }
}

; List todos
on TEXT:!todo list:#:{
    set %count = $list(@todos,count)
    if (%count == 0) {
        msg $chan No todos!
    }
    else {
        msg $chan === Your Todos ===
        set %i = 0
        for (%task in @todos) {
            msg $chan %i. %task
            set %i = $calc(%i + 1)
        }
    }
}

; Complete todo
on TEXT:!todo done*:#:{
    if ($3) {
        set %idx = $3
        set %task = $list(@todos,%idx)
        if (%task) {
            listdel @todos %idx
            msg $chan $nick Completed: %task
        }
    }
}

; Clear todos
on TEXT:!todo clear:#:{
    listclear @todos
    msg $chan All todos cleared!
}
```

### Example 4: Word Filter

```mirc
; Add banned word (ops only)
on TEXT:!ban*:#:{
    if ($islevel($nick,100) == True) {
        if ($2) {
            listadd @@badwords $lower($2)
            msg $chan Added $2 to filter
        }
    }
}

; Check messages
on TEXT:*:#:{
    if ($nick != $me) {
        ; Check each word
        for (%word in @message_words) {
            if ($list(@@badwords,exists,$lower(%word)) == True) {
                msg $chan $nick Please watch your language!
                halt
            }
        }
    }
}
```

### Example 5: Poll System

```mirc
; Start poll
on TEXT:!poll*:#:{
    if ($2-) {
        set %%poll_question = $2-
        listclear @@poll_votes
        msg $chan === POLL: %%poll_question ===
        msg $chan Vote with: !vote <your answer>
    }
}

; Cast vote
on TEXT:!vote*:#:{
    if ($2-) {
        listadd @@poll_votes $nick: $2-
        msg $chan Vote recorded!
    }
}

; Show results
on TEXT:!results:#:{
    set %count = $list(@@poll_votes,count)
    msg $chan === Poll Results (%count votes) ===
    msg $chan Question: %%poll_question
    for (%vote in @@poll_votes) {
        msg $chan - %vote
    }
}
```

---

## Best Practices

### 1. Always Check Count Before Accessing

```mirc
; GOOD
if ($list(@mylist,count) > 0) {
    set %first = $list(@mylist,0)
}

; BAD - might get empty string
set %first = $list(@mylist,0)
```

### 2. Use Descriptive Names

```mirc
; GOOD
@user_quotes
@banned_words
@active_users

; BAD
@list1
@data
@stuff
```

### 3. Clear Lists When Done

```mirc
; Clean up temporary lists
on TEXT:!done:#:{
    listclear @temp_data
    msg $chan Done and cleaned up!
}
```

### 4. Use Global Lists for Persistence

```mirc
; Data you want to keep
listadd @@quotes $text
listadd @@user_settings $setting

; Temporary data
listadd @current_session $nick
```

### 5. Validate Input

```mirc
on TEXT:!add*:#:{
    if ($2) {
        ; Check not already in list
        if ($list(@items,exists,$2) != True) {
            listadd @items $2
            msg $chan Added!
        }
        else {
            msg $chan Already in list!
        }
    }
    else {
        msg $chan Usage: !add <item>
    }
}
```

### 6. Use For Loops for Bulk Operations

```mirc
; Process all items efficiently
for (%user in @users) {
    ; Do something with each user
    notice %user Welcome back!
}
```

---

## Quick Reference Card

```mirc
COMMANDS:
  listadd @list <value>           Add item
  listdel @list <index|value>     Remove item
  listclear @list                 Clear all
  listinsert @list <idx> <value>  Insert at position

IDENTIFIERS:
  $list(@list,N)                  Get item at index N
  $list(@list,count)              Get count
  $list(@list,find,value)         Find index
  $list(@list,exists,value)       Check if exists

CONTROL:
  for (%var in @list) { }         Iterate over items

PREFIXES:
  @listname    - Local (temporary)
  @@listname   - Global (persistent)
```

---

## Practice Exercises

### Exercise 1: Color List
Create a script that:
1. Stores a list of colors
2. Adds colors with `!addcolor <color>`
3. Shows a random color with `!randomcolor`
4. Lists all colors with `!colors`

### Exercise 2: High Scores
Create a high score system:
1. Add scores with `!score <name> <points>`
2. Show all scores with `!scores`
3. Find a user's score with `!myscore`

### Exercise 3: Reminder System
Build a reminder system:
1. Add reminders with `!remind <text>`
2. List reminders with `!reminders`
3. Remove reminder by index with `!done <index>`

---

## Troubleshooting

### Issue: List is Empty

```mirc
; Check if list exists and has items
set %count = $list(@mylist,count)
if (%count == 0) {
    echo List is empty!
}
```

### Issue: Can't Find Item

```mirc
; Use exists to check first
if ($list(@mylist,exists,value) == True) {
    echo Found it!
}
else {
    echo Not found
}
```

### Issue: Index Out of Range

```mirc
; Always validate index
set %count = $list(@mylist,count)
if (%idx >= 0) {
    if (%idx < %count) {
        set %item = $list(@mylist,%idx)
    }
}
```

---

## Summary

**Key Takeaways:**

✅ Lists store multiple values  
✅ Use `@` for local, `@@` for global  
✅ Add with `listadd`, remove with `listdel`  
✅ Access with `$list(@name,N)`  
✅ Iterate with `for (%var in @list)`  
✅ Check count before accessing  
✅ Use descriptive names  

**You now have the power to:**
- Build quote systems
- Track users
- Create polls
- Manage todos
- Filter words
- And much more!

Happy scripting! 🚀

