import subprocess
import re
import tempfile, os

class MovieDataExtractorFFmpeg(object):
    #Duration: 00:01:52.24, start: 0.000000, bitrate: 12026 kb/s
    RE_length = re.compile(r"Duration: (?P<length>\d+:\d+:\d+).+? bitrate: (?P<bitrate>\d+) kb/s")
    #Stream #0:1(eng): Video: h264 (Baseline) (avc1 / 0x31637661), yuv420p, 1280x720, 11957 kb/s, 29.91 fps, 29.92 tbr, 30k tbn, 60k tbc (default)
    RE_type = re.compile(r": Video: (?P<codec>\w+)[ ,].*?, (?P<resolution>\d+x\d+)[, ].*? (?P<fps>[\d\.]+) tbr")
    
    def __init__(self, ffmpeg_path):
        self.ffmpeg_path = ffmpeg_path
    
    def fix_filepath_enc(self, path):
        return path.encode("mbcs")
    
    def run_ffmpeg(self, cmdlist):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        cmds = [self.ffmpeg_path] + cmdlist
        try:
            info = subprocess.check_output(cmds, stderr=subprocess.STDOUT, startupinfo=startupinfo)
        except subprocess.CalledProcessError, e:
            info = e.output
        return info
    
    def get_thumb(self, path, seconds, size=170, show=False):
        #ffmpeg -ss 00:00:14.435 -i input.flv -f image2 -vframes 1 out.png
        #
        #https://trac.ffmpeg.org/wiki/How%20to%20take%20multiple%20screenshots%20to%20an%20image%20(tile,%20mosaic)
        #ffmpeg -ss 00:00:10 -i movie.avi -frames 1 -vf "select=not(mod(n\,1000)),scale=320:240,tile=2x3" out.png
        #
        #http://www.kayweb.com.au/blogs/Web-Development/Generating-screenshots-using-FFmpeg
        #http://nabe.kokidokom.net/2013/01/27/generating-screenshots-frame-extraction-with-ffmpeg/
        
        filename = tempfile.mktemp() + ".jpg"
        
        path = self.fix_filepath_enc(path)
        
        args = [
            "-ss", str(seconds), 
            "-i", path,
            "-f", "image2",
            "-vframes", "1",
            "-filter:v", 'scale=%s:-1' % size,
            filename
        ]
        result = self.run_ffmpeg(args)
        data = open(filename, "rb").read()
        os.unlink(filename)
        return data    
    
    def get_info(self, filepath):
        #
        # return dict: "seconds", "fps", "resolution", "codec", "bitrate"
        #

        filepath = self.fix_filepath_enc(filepath)

        d = {}
        data = self.run_ffmpeg(["-i", filepath])
        lines = data.split("\n")
        for line in lines:
            for rx in [self.RE_length, self.RE_type]:
                m = rx.search(line)
                if m:
                    d.update(m.groupdict())
        d["rawtext"] = data
        hh, mm, ss = d.get("length", "0:0:0").split(":")
        d["seconds"] = int(hh)* 3600 + int(mm) * 60 + int(ss)
        return d