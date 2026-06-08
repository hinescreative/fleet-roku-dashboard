#!/bin/zsh
cd ~/roku-experiments
./fleet
# The fleet script already starts the server and preps the TV.
# After this, the user still needs to manually start Screen Mirroring on the Mac to the Roku.
# This .command file gives a double-clickable "button" on the Desktop.
open -a "Safari" "http://localhost:8080" 2>/dev/null || open "http://localhost:8080"
echo "Dashboard at http://localhost:8080 - now AirPlay/Screen Mirror from Control Center to your Roku TV."
read -p "Press Enter to close this window..."
