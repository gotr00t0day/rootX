# 📋 Lists Feature - RootX Scripting

## Overview

The Lists (Arrays) feature adds powerful container functionality to RootX scripting, allowing you to store and manipulate collections of data.

## Quick Start

### Basic Usage

```mirc
; Create a list and add items
listadd @fruits Apple
listadd @fruits Banana
listadd @fruits Cherry

; Get count
set %count = $list(@fruits,count)
echo We have %count fruits

; Access items
echo First: $list(@fruits,0)
echo Second: $list(@fruits,1)

; Iterate over all items
for (%fruit in @fruits) {
    echo - %fruit
}
```

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `listadd @list <value>` | Add item to end of list | `listadd @names Bob` |
| `listdel @list <index\|value>` | Remove item by index or value | `listdel @names 0` |
| `listclear @list` | Remove all items | `listclear @names` |
| `listinsert @list <idx> <val>` | Insert at specific position | `listinsert @names 1 Alice` |

## Identifiers

| Identifier | Description | Returns |
|------------|-------------|---------|
| `$list(@list,N)` | Get item at index N (0-based) | String |
| `$list(@list,count)` | Get number of items | Integer |
| `$list(@list,find,value)` | Find index of value | Integer (-1 if not found) |
| `$list(@list,exists,value)` | Check if value exists | `True` or `False` |

## For Loops

Iterate over all items in a list:

```mirc
for (%variable in @listname) {
    ; Commands here
    ; %variable contains current item
}
```

### Example

```mirc
for (%user in @users) {
    msg $chan Hello %user!
}
```

## Local vs Global Lists

### Local Lists (`@listname`)
- Single `@` prefix
- Temporary (cleared on script reload)
- Use for session-specific data

### Global Lists (`@@listname`)
- Double `@@` prefix
- Persistent (saved across reloads)
- Use for permanent data (quotes, settings, etc.)

## Example Use Cases

### 1. Quote System
```mirc
on TEXT:!addquote*:#:{
    listadd @@quotes $2-
    msg $chan Quote added!
}

on TEXT:!quote:#:{
    set %count = $list(@@quotes,count)
    set %idx = $rand(%count)
    msg $chan $list(@@quotes,%idx)
}
```

### 2. User Tracker
```mirc
on JOIN:#:{
    listadd @recent $nick
    msg $chan Welcome $nick!
}

on TEXT:!recent:#:{
    for (%user in @recent) {
        msg $chan - %user
    }
}
```

### 3. Todo List
```mirc
on TEXT:!todo add*:#:{
    listadd @todos $3-
    msg $chan Todo added!
}

on TEXT:!todos:#:{
    set %i = 0
    for (%task in @todos) {
        msg $chan %i. %task
        set %i = $calc(%i + 1)
    }
}
```

### 4. Poll System
```mirc
on TEXT:!poll*:#:{
    listclear @@votes
    set %%question = $2-
    msg $chan Vote with: !vote <answer>
}

on TEXT:!vote*:#:{
    listadd @@votes $nick: $2-
    msg $chan Vote recorded!
}
```

## Files Included

### Documentation
- `/tutorials/LISTS_TUTORIAL.md` - Comprehensive tutorial
- `/LISTS_FEATURE.md` - This file (quick reference)

### Example Scripts
- `/scripts/lists_demo.rsx` - Full-featured demos of all list capabilities
- `/scripts/lists_test.rsx` - Test script to verify functionality

## Testing

Load and test the lists feature:

1. Reload scripts: `/script reload`
2. Run test: Type `!testlists` in a channel
3. Try demos: Type `!listhelp` for available demo commands

## Implementation Details

### Changes to script_engine.py

1. **Storage**: Added `local_lists` and `global_lists` dictionaries
2. **Commands**: Implemented `listadd`, `listdel`, `listclear`, `listinsert`
3. **Identifiers**: Added `$list()` function with get, count, find, exists
4. **Control Flow**: Implemented `for (%var in @list)` loop
5. **Documentation**: Updated inline documentation

### Key Functions

- `_cmd_listadd()` - Add item to list
- `_cmd_listdel()` - Remove item from list
- `_cmd_listclear()` - Clear all items
- `_cmd_listinsert()` - Insert item at position
- `_func_list_get()` - Get item by index
- `_func_list_count()` - Get list count
- `_func_list_find()` - Find item index
- `_func_list_exists()` - Check if item exists
- `_handle_for()` - For loop iteration

## Best Practices

1. ✅ **Check count before accessing**
   ```mirc
   if ($list(@list,count) > 0) {
       set %first = $list(@list,0)
   }
   ```

2. ✅ **Use descriptive names**
   ```mirc
   @user_quotes  ; Good
   @data        ; Bad
   ```

3. ✅ **Use global lists for persistence**
   ```mirc
   listadd @@quotes $text    ; Persists
   listadd @session $nick    ; Temporary
   ```

4. ✅ **Validate input**
   ```mirc
   if ($list(@users,exists,$nick) != True) {
       listadd @users $nick
   }
   ```

5. ✅ **Clean up when done**
   ```mirc
   listclear @temp_data
   ```

## Advanced Tips

### Numbered List Display
```mirc
set %i = 0
for (%item in @list) {
    msg $chan %i. %item
    set %i = $calc(%i + 1)
}
```

### Check Before Adding
```mirc
if ($list(@users,exists,$nick) != True) {
    listadd @users $nick
}
```

### Find and Remove
```mirc
set %pos = $list(@badwords,find,$word)
if (%pos >= 0) {
    listdel @badwords %pos
}
```

### Conditional Iteration
```mirc
for (%user in @users) {
    if ($islevel(%user,100) == True) {
        notice %user Admin message
    }
}
```

## Troubleshooting

### Problem: List not persisting
**Solution**: Use `@@` for global lists, not `@`

### Problem: Item not found
**Solution**: Use `$list(@list,exists,value)` to check first

### Problem: Index out of range
**Solution**: Check count before accessing
```mirc
set %count = $list(@list,count)
if (%idx < %count) {
    set %item = $list(@list,%idx)
}
```

## Performance Notes

- Lists are stored in memory (Python lists)
- For loops have a safety limit of 10,000 iterations
- Global lists persist in script memory (not yet saved to disk)
- Accessing items by index is O(1) - very fast
- Finding items is O(n) - slower for large lists

## Future Enhancements

Potential future additions:
- Save global lists to disk
- Sort lists
- Slice operations
- List comprehensions
- Multi-dimensional lists

## Summary

The lists feature provides:
- ✅ Dynamic arrays with add/remove operations
- ✅ For loop iteration
- ✅ Index-based and value-based access
- ✅ Local and global persistence
- ✅ Find, exists, count operations
- ✅ Insert at specific positions

This enables building sophisticated features like:
- Quote/fact systems
- User tracking
- Todo lists
- Poll systems
- Word filters
- And much more!

---

**Happy Scripting!** 🚀

For detailed documentation, see `/tutorials/LISTS_TUTORIAL.md`

