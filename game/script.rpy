# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")

define web_video_base = "https://share.renpy.org"

label start:

    show bg washington
    show eileen happy

    e "Welcome to the web video test game. We can only show fullscreen cutscene-style videos. Click to play a movie once."

    $ renpy.movie_cutscene("oa4_launch.webm")

    e "We can also show a looping video. Click to see that, then click again to stop."

    $ renpy.movie_cutscene("oa4_launch.webm", loops=-1)

    e"And that's it. Thank you for checking this out."

    return
