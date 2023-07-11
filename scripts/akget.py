#!/usr/bin/env python3 
import os, sys
import json
import tempfile
import datetime
import logging
import urllib.request
import hashlib
from rich.logging import RichHandler
import concurrent.futures
import importlib

# Set program version
__version__ = "x"


 

# Set database in JSON format for interoperability
databases_json = """{
 
  "greengenes": {
    "md5": "c66091696e1fcf35a7ac6b8fcb48bbef",
    "ver": "13.5",
    "outdir": "16S_Greengenes_k2db",
    "url": "https://genome-idx.s3.amazonaws.com/kraken/16S_Greengenes13.5_20200326.tgz",
    "desc": "Greengenes",
    "c": "McDonald 2012",
    "cite": "McDonald D, (2012) 'An improved Greengenes taxonomy with explicit ranks for ecological and evolutionary analyses of bacteria and archaea' 10.1038/ismej.2011.139 "
  },
  "kraken-silva-138": {
    "md5": "94ecb2c851f3e4f02335559d42013f0f",
    "outdir": "16S_SILVA138_k2db",
    "ver": "138",
    "desc": "SILVA release 138",
    "url": "https://genome-idx.s3.amazonaws.com/kraken/16S_Silva138_20200326.tgz",
    "c": "Quast 2013",
    "cite": "Quast C, Pruesse E, Yilmaz P, Gerken J, Schweer T, Yarza P, Peplies J, Glöckner FO (2013) The SILVA ribosomal RNA gene database project: improved data processing and web-based tools.  ucl. Acids Res. 41 (D1): D590-D596."
  },
  "kraken-silva-132": {
    "url": "https://genome-idx.s3.amazonaws.com/kraken/16S_Silva132_20200326.tgz",
    "outdir": "16S_SILVA132_k2db",
    "desc": "SILVA release 132",
    "md5": "0b6d8ed61e63210c1dc2ccdd373a9d5d",
    "ver": "132",
    "c": "Quast 2013",
    "cite": "Quast C, Pruesse E, Yilmaz P, Gerken J, Schweer T, Yarza P, Peplies J, Glöckner FO (2013) The SILVA ribosomal RNA gene database project: improved data processing and web-based tools.  ucl. Acids Res. 41 (D1): D590-D596."
  },
  "kraken-rdp-115": {
    "url": "https://genome-idx.s3.amazonaws.com/kraken/16S_RDP11.5_20200326.tgz",
    "outdir": "16S_RDP_k2db",
    "desc": "RDP release 11.5",
    "md5": "7381792a19064962741724eee188121e",
    "ver": "11.5",
    "c": "Cole 2014",
    "cite": "Cole JR, Wang Q, Fish JA, Chai B, McGarrell DM, Sun Y, Brown CT, Porras-Alfaro A, Kuske CR, Tiedje JM (2014)'Ribosomal Database Project: data and tools for high throughput rRNA analysis', NAR, 10.1093/nar/gkt1244"
  }
}"""
   


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
 
# check MD5 of a file
def check_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def main():
    

    # Download URL to FILEPATH destination
    def download(url, destdir, md5=None):
        destBasename = os.path.basename(url).split("?")[0]
        filepath = os.path.join(destdir, destBasename)
        #print("Downloading {} to {}".format(url, filepath))
        if md5 and os.path.exists(filepath) and md5 is not None:
            term_logger.info("{} found: checking integrity".format(destBasename), extra={"markup": True})
            if check_md5(filepath) == md5:
                term_logger.info(":white_check_mark: {} found and verified!".format(destBasename), extra={"markup": True})
                return filepath
            term_logger.info(":warning: File found but MD5 does not match", extra={"markup": True})

        try:
            term_logger.info(":checkered_flag: Downloading {}...".format(url, filepath), extra={"markup": True})
            urllib.request.urlretrieve(url, filepath)
            if md5:
                if check_md5(filepath) == md5:
                    term_logger.info(":white_check_mark: {} downloaded".format(destBasename), extra={"markup": True})
                else:
                    term_logger.error(":warning: {} downloaded but failed MD5 check".format(destBasename), extra={"markup": True})
                    return False
        except Exception as e:
            term_logger.error(":warning: Downloading {} to {} failed with exception {}".format(url, filepath, e), extra={"markup": True})
            return False
        
        # Expand
        if os.path.exists(filepath):
            try:
              cmd = 'tar -xzf "{}" -C "{}"'.format(filepath, destdir)
              os.system(cmd)
              term_logger.info(":white_check_mark: {} extracted".format(destBasename), extra={"markup": True})
            except Exception as e:
              term_logger.error(":warning: Extracting {} failed with exception {}".format(filepath, e), extra={"markup": True})
              return False
            
            # Remove tar.gz
            os.remove(filepath)
        return True

    def printProgramTitleBoxed(title):
        from rich.panel import Panel
        console.print()
        console.print(Panel("  [white]{title}[/]   ".format(title=title), style="cyan", title="Amplikraken"), justify="left")


    # User home directory
    default_outdir = os.path.join(os.path.expanduser("~"), "refs")

    # Timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    #   if exists default_outdir
    if os.path.exists(default_outdir):
        default_logfile = os.path.join(default_outdir, "amplikraken-getdb.log")
    else:  
        default_logfile = os.path.join(tempfile.gettempdir(), f"amplikraken-getdb-{timestamp}.log")


    import argparse
    from rich.console import Console
    from rich.table import Table
    console = Console()
    
    # Arguments
    parser = argparse.ArgumentParser(description="Download databases for Amplikraken")
    parser.add_argument("-d", "--database", help="Database code")
    parser.add_argument("-l", "--list", action="store_true", help="List databases")
    parser.add_argument("-q", "--query", help="Query string for databases, to be used with --list or alone (instead of --database)")
    parser.add_argument("-o", "--output-dir", dest="outdir", help="Output directory [default: %(default)s]", default=default_outdir)
    parser.add_argument("--full", action="store_true", help="Print full citation")
    parser.add_argument("--logfile", help="Log file  [default: %(default)s]", default=default_logfile)
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Increase verbosity")
    opts = parser.parse_args()

    #Amplikraken.printBox("amplikraken-getdb " + __version__)
    
    # Set logger 
    logging.basicConfig(filename=opts.logfile, filemode="a", format="%(asctime)s - %(levelname)s: %(name)s > %(message)s")
    term_logger = logging.getLogger(__name__)
    term_logger.setLevel(logging.INFO)
    term_logger.addHandler(RichHandler(console=console))

    # parse databases_json from JSON
    try:
        dbs = json.loads(databases_json)
    except Exception as e:
        term_logger.error("Error parsing databases.json: %s" % e)
        term_logger.error(databases_json)
        sys.exit(1)

    if opts.list:
        c = 0
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Code", style="bold", width=22)
        table.add_column("Description")
        #table.add_column("URL")
        table.add_column("Paper")

       
        
        # Print databases
        for db in dbs:
            if opts.query and (opts.query.lower() not in db.lower()):
                continue
            c += 1
            #console.print("[bold white on blue] {db:<20} [/] [green]({c})[/] {desc}\n   [italic]url[/]: {url}\n   [italic]cite[/]: {cite}\n".format(c=c, db=db, desc=dbs[db]["desc"], cite=dbs[db]["cite"], url=dbs[db]["url"])  )
            table.add_row(
                db,
                dbs[db]["desc"],
                #dbs[db]["url"],
                dbs[db]["cite"] if opts.full else dbs[db]["c"] if "c" in dbs[db] else "",
            )
        console.print(table)
        sys.exit(0)
    else:
        # Get databases
        term_logger.info("Downloading databases to {}".format(opts.outdir))
        term_logger.info("Logging to {}".format(opts.logfile))

        # Check output directory, try to make it
        if not os.path.exists(opts.outdir):
            try:
                os.makedirs(opts.outdir)
            except Exception as e:
                term_logger.error("Error creating output directory: %s" % e)
                sys.exit(1)

        if opts.query or opts.database:
            urls = {}
            for db in dbs:
                if (opts.query == "all") or (opts.database and db == opts.database) or (opts.query  and (opts.query.lower() in db.lower() )):
                    # check if database is already downloaded
                    dest_dir = os.path.join(opts.outdir,  dbs[db]["outdir"]) if "outdir" in dbs[db] else os.path.join(opts.outdir, db)
                    if os.path.isdir(dest_dir):
                        term_logger.info(":white_check_mark: Database {} already downloaded".format(db), extra={"markup": True})
                        continue
                    urls[ dbs[db]["url"] ] = dbs[db]["md5"]
            
            if not urls:
                term_logger.error("No databases to download!")
            else:
                # Concurrently download databases
                with console.status("[bold]Amplikraken[/] - Getting databases", spinner="point"):
                    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                        futures = [executor.submit(download, url, os.path.join(opts.outdir), urls[url]) for url in urls]

        else:
            # Print usage from argparse
            parser.print_help()
            eprint()
            eprint("\nUse --list to print a list of available databases (add --query STR to filter).")
            eprint("\nTo download, use --query STR to download multiple databases ('all' is  supported) or --database ID to download one.")
            sys.exit(0)

if __name__ == "__main__":
    main()