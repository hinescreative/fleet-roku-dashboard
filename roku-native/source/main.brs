sub Main()
    ' Simple Fleet Dashboard starter
    ' This is a basic Roku SceneGraph channel
    ' Run it by zipping the fleet-dashboard folder contents and sideloading at http://10.0.0.73

    screen = CreateObject("roSGScreen")
    m.port = CreateObject("roMessagePort")
    screen.setMessagePort(m.port)

    scene = screen.CreateScene("MainScene")
    screen.show()

    ' Keep the app running and handle events
    while true
        msg = wait(0, m.port)
        if type(msg) = "roSGScreenEvent"
            if msg.isScreenClosed() then return
        end if
    end while
end sub