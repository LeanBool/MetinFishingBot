Demo video of downloading and using the bot: https://www.viddler.com/rsopR9

Note: Untested on Windows

Note: this script takes control of your cursor and keyboard while active to be stealthy, it might require root privileges on linux.

Uses https://github.com/TimLeitch/Screen-Region-Capture-Tool for selection of screen region. Slightly modified to work on linux.

Uses font from DejaVu Fonts https://dejavu-fonts.github.io/Download.html


## Playing Metin (including private servers with custom launchers) on Linux 
- Install Steam
- Install ProtonGE https://github.com/GloriousEggroll/proton-ge-custom?tab=readme-ov-file#installation
- In Steam click "Add a non-steam game to your library" and select the Metin patcher executable.
- Right click on the newly added executable in your Steam library, click on Properties and under Compatibility check the box saying "force the use of a specific compatibility tool". Select the Proton-GE Version you installed (named GE-ProtonXX-XX).
- Et voilà, you can now launch Metin through your Steam client.


## Setup fishing bot:
```git clone https://github.com/LeanBool/MetinFishingBot.git && cd MetinFishingBot && ./run.sh```


## Usage:
- Start script ./run.sh
- Start fishing and press q to open a drag-and-drop selection overlay
- Select the area the bot is supposed to see, make sure no gui elements of the fishing panel (except for the circle) are included
- Press q again and select the clickable area (the fishing circle)
- To quit: press q
