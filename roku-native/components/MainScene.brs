sub init()
    m.top.backgroundURI = ""

    ' You can add more logic here later:
    ' - Fetch JSON from your fleet API
    ' - Update labels dynamically
    ' - Add buttons, lists, video, etc.
    ' Example: m.content1 = m.top.findNode("content1")

    print "Fleet Dashboard channel initialized"
end sub

function onKeyEvent(key as string, press as boolean) as boolean
    if press
        if key = "back"
            ' Handle back button if needed
            return true
        end if
    end if
    return false
end function