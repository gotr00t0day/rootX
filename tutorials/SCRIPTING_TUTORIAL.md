# 🚀 RootX Scripting Tutorial for Beginners

Welcome to RootX scripting! This tutorial will teach you how to automate your IRC experience with custom scripts.

## 📚 Table of Contents

1. [What is Scripting?](#what-is-scripting)
2. [Your First Script](#your-first-script)
3. [Understanding Events](#understanding-events)
4. [Understanding Aliases](#understanding-aliases)
5. [Working with Variables](#working-with-variables)
6. [Using Identifiers](#using-identifiers)
7. [Control Flow (If/Else)](#control-flow-ifelse)
8. [Practical Examples](#practical-examples)
9. [Troubleshooting](#troubleshooting)
10. [Practice Exercises](#practice-exercises)

---

## What is Scripting?

**Scripting** lets you automate actions in IRC. Think of it like setting up "rules":

- **"When someone says hello, reply with a greeting"**
- **"When I type /joke, send a random joke to the channel"**
- **"When someone joins, welcome them automatically"**

Scripts save you time and make your IRC experience more fun!

---

## Your First Script

Let's create your first script step by step.

### Step 1: Create a Script File

1. Navigate to: `/Users/c0d3ninja/rootX/scripts/`
2. Create a new file: `myfirst.rsx`
3. Open it in your text editor

### Step 2: Write a Simple Script

Copy this into your file:

```mirc
; My First Script
; This responds when someone says "hello"

on TEXT:*hello*:#:{
    msg $chan Hi there, $nick!
}
```

### Step 3: Load Your Script

In RootX, type:
```
/script reload
```

### Step 4: Test It!

1. Join a channel: `/join #test`
2. Ask someone to say "hello" (or say it yourself from another client)
3. Your bot should respond: `Hi there, YourNick!`

**🎉 Congratulations! You just wrote your first IRC script!**

---

## Understanding Events

**Events** are things that happen in IRC. Your scripts can "listen" for these events and react.

### Event Syntax

```mirc
on EVENT:match:target:{ 
    commands go here
}
```

- **EVENT** = What to listen for (TEXT, JOIN, PART, etc.)
- **match** = What pattern to match
- **target** = Where to listen (# = any channel, #specific = specific channel)

### Common Events

| Event | When It Happens | Example |
|-------|----------------|---------|
| `TEXT` | Someone sends a message | `on TEXT:*:#{...}` |
| `JOIN` | Someone joins a channel | `on JOIN:*:#{...}` |
| `PART` | Someone leaves a channel | `on PART:*:#{...}` |
| `QUIT` | Someone disconnects | `on QUIT:*:*:{...}` |
| `KICK` | Someone gets kicked | `on KICK:*:#{...}` |
| `NICK` | Someone changes nickname | `on NICK:*:*:{...}` |

### Pattern Matching

| Pattern | Matches | Example |
|---------|---------|---------|
| `*` | Anything | `on TEXT:*:#:` (all messages) |
| `*hello*` | Contains "hello" | "hello", "say hello", "hello!" |
| `!command` | Exact text | "!time", "!help" |
| `!help*` | Starts with "!help" | "!help", "!help me" |

### Examples

**Listen to all messages:**
```mirc
on TEXT:*:#:{
    echo Someone said: $text
}
```

**Listen for a specific command:**
```mirc
on TEXT:!ping:#:{
    msg $chan Pong!
}
```

**Welcome new users:**
```mirc
on JOIN:*:#:{
    msg $chan Welcome to $chan, $nick!
}
```

**Goodbye message:**
```mirc
on PART:*:#:{
    msg $chan Goodbye, $nick! Come back soon!
}
```

---

## Understanding Aliases

**Aliases** are custom commands you create. They're like shortcuts.

### Alias Syntax

```mirc
alias /commandname {
    commands go here
}
```

### Simple Example

Create a `/hello` command:

```mirc
alias /hello {
    msg $chan Hello everyone!
}
```

**Usage:** Type `/hello` in any channel.

### Alias with Parameters

Parameters are extra words you type after the command.

```mirc
alias /greet {
    msg $chan Hello $1!
}
```

- `$1` = first word after command
- `$2` = second word
- `$3` = third word, etc.

**Usage:**
```
/greet Alice    → Sends "Hello Alice!"
/greet Bob      → Sends "Hello Bob!"
```

### Multiple Parameters

```mirc
alias /say {
    msg $1 $2-
}
```

- `$1` = first parameter (target)
- `$2-` = everything from 2nd parameter onwards (message)

**Usage:**
```
/say Alice How are you?
→ Sends "How are you?" to Alice
```

---

## Working with Variables

**Variables** store information you can use later.

### Local Variables

Start with `%` - Only exist while script runs.

```mirc
on TEXT:!dice:#:{
    set %roll = $rand(6)
    msg $chan You rolled a %roll!
}
```

### Global Variables

Start with `%%` - Saved permanently.

```mirc
on TEXT:!setname*:#:{
    set %%myname = $2
    msg $chan I'll remember you as %%myname
}
```

**Global variables persist** even after `/script reload`!

### Using Variables

```mirc
; Set a variable
set %counter = 0

; Use it
msg $chan Counter is at %counter

; Modify it
set %counter = 5
```

---

## Using Identifiers

**Identifiers** give you information. They start with `$`.

### Essential Identifiers

| Identifier | What It Is | Example Value |
|------------|-----------|---------------|
| `$nick` | Who triggered the event | "Alice" |
| `$chan` | Current channel | "#linux" |
| `$me` | Your nickname | "MyBot" |
| `$text` | Full message text | "hello everyone" |
| `$1`, `$2`, `$3` | Word 1, 2, 3 from message | "hello", "everyone" |
| `$time` | Current time | "14:30:25" |
| `$date` | Current date | "2025-12-04" |

### Function Identifiers

| Function | What It Does | Example |
|----------|--------------|---------|
| `$rand(N)` | Random number 0 to N-1 | `$rand(6)` → 0-5 |
| `$len(text)` | Length of text | `$len(hello)` → 5 |
| `$upper(text)` | Uppercase | `$upper(hello)` → HELLO |
| `$lower(text)` | Lowercase | `$lower(HELLO)` → hello |

### Examples

**Show current time:**
```mirc
on TEXT:!time:#:{
    msg $chan The time is $time on $date
}
```

**Shout messages:**
```mirc
on TEXT:!shout*:#:{
    set %message = $upper($2-)
    msg $chan %message
}
```

**Random number:**
```mirc
on TEXT:!random:#:{
    msg $chan Random number: $rand(100)
}
```

---

## Control Flow (If/Else)

Make decisions in your scripts!

### Basic If

```mirc
if (condition) {
    do something
}
```

### If/Else

```mirc
if (condition) {
    do this
}
else {
    do that
}
```

### Conditions

| Condition | Meaning | Example |
|-----------|---------|---------|
| `==` | Equals | `if ($nick == Alice)` |
| `!=` | Not equals | `if ($nick != Bob)` |
| `>` | Greater than | `if (%count > 5)` |
| `<` | Less than | `if (%count < 10)` |
| `>=` | Greater or equal | `if (%score >= 100)` |
| `<=` | Less or equal | `if (%score <= 0)` |
| `isin` | Contains | `if (hello isin $text)` |

### Examples

**Don't greet yourself:**
```mirc
on JOIN:*:#:{
    if ($nick != $me) {
        msg $chan Welcome, $nick!
    }
}
```

**Different greetings for different people:**
```mirc
on JOIN:*:#:{
    if ($nick == Alice) {
        msg $chan Welcome back, Admin Alice!
    }
    else if ($nick == Bob) {
        msg $chan Hey Bob, long time no see!
    }
    else {
        msg $chan Welcome, $nick!
    }
}
```

**Only respond to specific users:**
```mirc
on TEXT:!admin:#:{
    if ($nick == Alice) {
        msg $chan Admin command executed!
    }
    else {
        msg $chan Sorry, you're not an admin.
    }
}
```

---

## Practical Examples

Let's build some useful scripts!

### Example 1: Auto-Responder

Automatically reply when someone mentions you:

```mirc
; Save as: autorespond.rsx

on TEXT:*:#:{
    if ($me isin $text) {
        if ($nick != $me) {
            msg $chan $nick: I'm here! What's up?
        }
    }
}
```

### Example 2: Fun Commands

Create entertaining commands:

```mirc
; Save as: fun.rsx

; Fortune cookie
on TEXT:!fortune:#:{
    set %num = $rand(5)
    if (%num == 0) {
        msg $chan 🥠 You will have a great day!
    }
    else if (%num == 1) {
        msg $chan 🥠 Good things come to those who wait.
    }
    else if (%num == 2) {
        msg $chan 🥠 Adventure awaits you!
    }
    else if (%num == 3) {
        msg $chan 🥠 Today is your lucky day!
    }
    else {
        msg $chan 🥠 A surprise is coming your way!
    }
}

; Magic 8-ball
on TEXT:!8ball*:#:{
    set %num = $rand(3)
    if (%num == 0) {
        msg $chan 🎱 Yes, definitely!
    }
    else if (%num == 1) {
        msg $chan 🎱 Ask again later.
    }
    else {
        msg $chan 🎱 Don't count on it.
    }
}

; Coin flip
on TEXT:!flip:#:{
    if ($rand(2) == 0) {
        msg $chan 🪙 Heads!
    }
    else {
        msg $chan 🪙 Tails!
    }
}
```

### Example 3: Information Bot

Provide helpful information:

```mirc
; Save as: infobot.rsx

on TEXT:!help:#:{
    msg $chan === Available Commands ===
    msg $chan !time - Show current time
    msg $chan !date - Show current date
    msg $chan !version - Show bot version
    msg $chan !uptime - How long I've been running
}

on TEXT:!time:#:{
    msg $chan Current time: $time
}

on TEXT:!date:#:{
    msg $chan Today's date: $date
}

on TEXT:!version:#:{
    msg $chan Running $version
}
```

### Example 4: Channel Logger

Log important events:

```mirc
; Save as: logger.rsx

on JOIN:*:#:{
    echo Channel $chan: $nick joined at $time
}

on PART:*:#:{
    echo Channel $chan: $nick left at $time
}

on TEXT:!log*:#:{
    echo $chan [$time] <$nick> $2-
}
```

### Example 5: Custom Greetings

Personalized welcomes:

```mirc
; Save as: greetings.rsx

on JOIN:*:#:{
    if ($nick == $me) {
        ; Don't greet ourselves
        halt
    }
    
    set %hour = $time
    
    if (morning isin %hour) {
        msg $chan Good morning, $nick!
    }
    else if (afternoon isin %hour) {
        msg $chan Good afternoon, $nick!
    }
    else {
        msg $chan Good evening, $nick!
    }
}
```

---

## Troubleshooting

### Common Errors and Solutions

#### **Error: "Script parsed successfully" but nothing happens**

**Problem:** Your event isn't triggering.

**Solutions:**
1. Check your pattern matching:
   ```mirc
   ; ❌ Wrong - too specific
   on TEXT:hello:#mychannel:{...}
   
   ; ✅ Right - matches any channel
   on TEXT:*hello*:#:{...}
   ```

2. Make sure you're in the right channel:
   ```mirc
   ; Only works in #test
   on TEXT:*:#test:{...}
   
   ; Works in any channel
   on TEXT:*:#:{...}
   ```

#### **Error: "Unknown command"**

**Problem:** Alias isn't loading.

**Solutions:**
1. Check alias syntax:
   ```mirc
   ; ❌ Wrong - missing /
   alias greet {...}
   
   ; ✅ Right
   alias /greet {...}
   ```

2. Reload scripts:
   ```
   /script reload
   ```

#### **Error: Variables aren't working**

**Problem:** Using wrong variable syntax.

**Solutions:**
```mirc
; ❌ Wrong - missing %
set myvar = 5

; ✅ Right - local variable
set %myvar = 5

; ✅ Right - global variable
set %%myvar = 5
```

#### **Error: Nothing is sent to channel**

**Problem:** Missing or wrong `msg` command.

**Solutions:**
```mirc
; ❌ Wrong - no target
msg Hello

; ❌ Wrong - wrong variable
msg %chan Hello

; ✅ Right - correct identifier
msg $chan Hello
```

### Debugging Tips

1. **Use echo to test:**
   ```mirc
   on TEXT:*test*:#:{
       echo Debug: $nick said $text
       msg $chan Response here
   }
   ```

2. **Check with /script list:**
   ```
   /script list
   ```
   Shows all loaded events and aliases.

3. **Test in steps:**
   ```mirc
   on TEXT:!test:#:{
       echo Step 1: Started
       set %var = hello
       echo Step 2: Variable set to %var
       msg $chan Done!
       echo Step 3: Message sent
   }
   ```

---

## Practice Exercises

Try these exercises to improve your skills!

### Exercise 1: Dice Game (Easy)

Create a dice rolling command that:
- Responds to `!roll`
- Rolls a number between 1-6
- Shows the result

<details>
<summary>Click to see solution</summary>

```mirc
on TEXT:!roll:#:{
    set %dice = $rand(6)
    set %dice = %dice + 1
    msg $chan $nick rolled a %dice!
}
```
</details>

### Exercise 2: Echo Bot (Easy)

Create an echo command that:
- Responds to `!echo <message>`
- Repeats back whatever the user types

<details>
<summary>Click to see solution</summary>

```mirc
on TEXT:!echo*:#:{
    msg $chan Echo: $2-
}
```
</details>

### Exercise 3: Seen Command (Medium)

Create a command that:
- Tracks when users join
- Responds to `!seen <nick>` with when they last joined

<details>
<summary>Click to see solution</summary>

```mirc
on JOIN:*:#:{
    set %%lastseen_ $+ $nick = $time on $date
}

on TEXT:!seen*:#:{
    if ($2) {
        set %lastseen = %%lastseen_ $+ $2
        if (%lastseen) {
            msg $chan $2 was last seen: %lastseen
        }
        else {
            msg $chan I haven't seen $2 yet.
        }
    }
}
```
</details>

### Exercise 4: Quiz Bot (Hard)

Create a simple quiz:
- Ask a question with `!quiz`
- Check answer with `!answer <text>`
- Keep score

<details>
<summary>Click to see solution</summary>

```mirc
on TEXT:!quiz:#:{
    set %quiz_question = What is 2+2?
    set %quiz_answer = 4
    msg $chan Question: %quiz_question
}

on TEXT:!answer*:#:{
    if ($2 == %quiz_answer) {
        msg $chan $nick: Correct!
        set %%score_ $+ $nick = %%score_ $+ $nick + 1
    }
    else {
        msg $chan $nick: Wrong! Try again.
    }
}

on TEXT:!score:#:{
    set %myscore = %%score_ $+ $nick
    msg $chan $nick: Your score is %myscore
}
```
</details>

---

## Next Steps

### Want to Learn More?

1. **Check example scripts:**
   - `scripts/sample.rsx` - Basic examples
   - `scripts/userlevels.rsx` - Advanced user management
   - `scripts/autoconnect.rsx` - Server automation

2. **Read advanced guides:**
   - `USER_LEVELS_GUIDE.md` - Permission system
   - `script_engine.py` - Full syntax reference (lines 1-111)

3. **Experiment!**
   - Modify existing scripts
   - Combine different features
   - Share your creations

### Quick Reference Card

```
EVENTS:    on EVENT:pattern:target:{...}
ALIASES:   alias /name {...}
VARIABLES: %local  %%global
IF/ELSE:   if (condition) {...} else {...}

COMMANDS:
  msg $chan message   - Send to channel
  echo message        - Display locally
  set %var = value    - Set variable
  halt                - Stop execution

IDENTIFIERS:
  $nick  $chan  $me   - People/places
  $text  $1  $2       - Message parts
  $time  $date        - Current time/date
  $rand(N)            - Random 0 to N-1
```

---

## Getting Help

- **In-app:** Type `/script help` for built-in help
- **Syntax:** Check the header of `script_engine.py` for full reference
- **Examples:** Look at the sample scripts in `scripts/` folder

**Happy Scripting! 🚀**

---

*Made with ❤️ for RootX IRC Client v2*

