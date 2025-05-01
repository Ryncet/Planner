import subprocess
import webbrowser

redirect_url = "https://youtu.be/dQw4w9WgXcQ"
script = '''
try
    do shell script "echo Authenticated!" with administrator privileges
    return "authenticated"
on error errMsg number errNum
    return "failed"
end try
'''
try:
    result = subprocess.check_output(["osascript", "-e", script], text = True).strip()
    if result == "authenticated":
        print("✅ macOS authentication succesful")
        subprocess.run(['osascript',"-e", 'set volume output volume 100'])
        subprocess.run(["afplay", "gta-san-andreas-mission-complete-sound-hq.mp3"])
        subprocess.run(["python3","school_planner.py"])
        webbrowser.open(redirect_url)
    elif result == "failed":
        print("❌ macOS authentication failed.")
        subprocess.run(['osascript',"-e", 'set volume output volume 0'])
        subprocess.run(["afplay", "drumbeatintro.mp3"])
        webbrowser.open(redirect_url)
except subprocess.CalledProcessError:
    print("❌ macOS authentication failed.")
    subprocess.run(['osascript',"-e", 'set volume output volume 0'])
    subprocess.run(["afplay", "drumbeatintro.mp3"])
    webbrowser.open(redirect_url)
