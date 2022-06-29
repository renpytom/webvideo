init -100 python:
    if renpy.emscripten:

        import emscripten
        emscripten.run_script("""
// This stores the video element if one is defined, or is None if no
// video element is active.
let video;

// This stores an element that is prompting the player to touch the screen
// to play the video.
let videoPrompt;

/**
 * Plays a video. This should be called with an object that has the
 * following fields:

 * `sources` - A list of URLs to try downloading the video from.
 * `loop` - True to loop, False not to loop.
 */

videoPlayPrompt = (message) => {
    videoPlayPromptHide();

    videoPrompt = document.createElement("div");
    videoPrompt.append(message);

    videoPrompt.style.position = "absolute";
    videoPrompt.style.bottom = "50%";
    videoPrompt.style.width = "100%";
    videoPrompt.style.textAlign = "center";

    videoPrompt.style.font = "24px sans-serif";
    videoPrompt.style.color = "white";
    videoPrompt.style.textAlign = "center";
    videoPrompt.style.textShadow = "0 0 2px black";

    document.body.append(videoPrompt);
};

videoPlayPromptHide = () => {
    if (videoPrompt) {
        videoPrompt.remove();
    }

    videoPrompt = null;
};


videoPlay = (properties) => {
    video = document.createElement("video");
    video.setAttribute("playsinline", "true");

    if (properties.loop) {
        video.setAttribute("loop", "true");
    }

    video.style.display = "block";
    video.style.position = "fixed";
    video.style.top = "0";
    video.style.left = "0";
    video.style.right = "0";

    video.style.margin = "0 auto";

    video.style.width = "100%";
    video.style.height = "100%";

    for (let i of properties.sources) {
        console.log("Video source: " + i);

        let source = document.createElement("source");
        source.setAttribute("src", i)
        video.append(source);
    }

    document.body.append(video);

    let unblockVideo = () => {
        if (video) {
            video.style.pointerEvents = "none";
        }
    };

    video.play().then(() => {
        setTimeout(unblockVideo, 1000);
    }).catch( (e) => {
        console.log("Video rejected: " + e);
        videoPlayPrompt(properties.prompt);
        video.style.pointerEvents = "auto";

        video.addEventListener("click", () => {
            console.log("Video click!");
            videoPlayPromptHide();
            setTimeout(unblockVideo, 1000);
            video.play();
        });
    });
};

/**
 * Stops the video.
 */
videoStop = () => {
    if (video) {
        video.remove();
    }

    video = undefined;

    videoPlayPromptHide();
};

/**
 * Returns 1 if the video is playing our about to play, 0 if it's ended or
 * an error has occurred.
 */
isVideoPlaying = () => {
    if (video == undefined) {
        return 0;
    }

    if (video.ended || video.error) {
        return 0;
    }

    return 1;
}
""")

        class WebVideoBehavior(renpy.Displayable):
            """
            This checks on a regular basis to see if the video has finished
            playing, and if it has, ends the interaction.
            """


            def render(self, width, height, st, at):
                return renpy.Render(0, 0)

            def event(self, ev, x, y, st):
                if not emscripten.run_script_int("isVideoPlaying()"):
                    return False
                else:
                    renpy.timeout(0.1)

        web_video_base = "."

        web_video_prompt = "Touch to play the video."

        def movie_cutscene(filename, delay=None, loops=0, stop_music=True):
            """
            A replacement for renpy.movie_cutscene that plays a video in
            the web browser.

            `filename`
                The name of the video file to play.

            `delay`
                Ignored.

            `loops`
                If -1, the video loops.

            `stop_music`
                If true, the music is stopped before the cutscene starts.
            """

            import json

            # This is a json object that's passed to videoPlay.
            properties = { }

            if loops == -1:
                properties["loop"] = True
            else:
                properties["loop"] = False

            # Determine the filename, and if different, the alternative filename.
            properties["sources"] = [ web_video_base + "/" + filename ]

            properties["prompt"] = __(web_video_prompt)

            alt_filename = filename.rpartition(".")[0] + ".mp4"
            if alt_filename != filename:
                properties["sources"].append( web_video_base + "/" + alt_filename )

            json_properties = json.dumps(properties)

            try:

                if stop_music:
                    renpy.music.set_pause(True, channel="music")

                emscripten.run_script("""videoPlay({})""".format(json_properties))

                renpy.show_screen("webvideo_blackout", _transient=True)

                ui.add(WebVideoBehavior())
                return renpy.pause()

            finally:
                emscripten.run_script("""videoStop()""")

                if stop_music:
                    renpy.music.set_pause(False, channel="music")

        renpy.movie_cutscene = movie_cutscene


screen webvideo_blackout():
    zorder 1000
    add "#000"
