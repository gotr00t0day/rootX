; ============================================
; Lists Test Script - Quick Functionality Test
; ============================================
;
; Simple test script to verify list functionality
; Type: !testlists
;
; ============================================

on TEXT:!testlists:#:{
    echo ====================================
    echo Testing List Functionality
    echo ====================================
    
    ; Test 1: Create and add items
    echo Test 1: Adding items to list...
    listclear @test
    listadd @test Apple
    listadd @test Banana
    listadd @test Cherry
    listadd @test Date
    echo Added 4 items
    
    ; Test 2: Count items
    echo Test 2: Counting items...
    set %count = $list(@test,count)
    echo Count: %count items
    msg $chan Test: List has %count items
    
    ; Test 3: Access items by index
    echo Test 3: Accessing items by index...
    set %item0 = $list(@test,0)
    set %item1 = $list(@test,1)
    set %item2 = $list(@test,2)
    set %item3 = $list(@test,3)
    echo Item[0] = %item0
    echo Item[1] = %item1
    echo Item[2] = %item2
    echo Item[3] = %item3
    msg $chan Items: %item0, %item1, %item2, %item3
    
    ; Test 4: Check if item exists
    echo Test 4: Checking if items exist...
    if ($list(@test,exists,Banana) == True) {
        echo Banana exists - PASS
        msg $chan ✓ Banana found in list
    }
    else {
        echo Banana not found - FAIL
        msg $chan ✗ Banana not found (ERROR)
    }
    
    if ($list(@test,exists,Orange) == True) {
        echo Orange exists - FAIL
        msg $chan ✗ Orange found (ERROR)
    }
    else {
        echo Orange not found - PASS
        msg $chan ✓ Orange not in list (correct)
    }
    
    ; Test 5: Find index
    echo Test 5: Finding item index...
    set %pos = $list(@test,find,Cherry)
    echo Cherry is at position %pos
    msg $chan Cherry is at index %pos
    
    ; Test 6: For loop iteration
    echo Test 6: Testing for loop...
    msg $chan === Iterating with for loop ===
    for (%fruit in @test) {
        msg $chan - %fruit
        echo Looped: %fruit
    }
    
    ; Test 7: Delete item
    echo Test 7: Deleting item...
    listdel @test 1
    set %newcount = $list(@test,count)
    echo After delete, count = %newcount
    msg $chan After deleting index 1, count = %newcount
    
    ; Test 8: List remaining items
    echo Test 8: Listing remaining items...
    msg $chan Remaining items:
    for (%item in @test) {
        msg $chan - %item
    }
    
    ; Test 9: Insert item
    echo Test 9: Inserting item at index 1...
    listinsert @test 1 Blueberry
    set %inserted = $list(@test,1)
    echo Item at index 1 is now: %inserted
    msg $chan Inserted Blueberry at index 1
    
    ; Test 10: Clear list
    echo Test 10: Clearing list...
    listclear @test
    set %finalcount = $list(@test,count)
    echo After clear, count = %finalcount
    msg $chan After clear, count = %finalcount
    
    echo ====================================
    echo All tests complete!
    echo ====================================
    msg $chan === All list tests completed! ===
}

; Quick test with simple iteration
on TEXT:!quicktest:#:{
    listclear @nums
    listadd @nums One
    listadd @nums Two
    listadd @nums Three
    
    msg $chan Quick test - iterating:
    for (%num in @nums) {
        msg $chan Number: %num
    }
}

