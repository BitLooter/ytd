#!/usr/bin/env python3

# Downloads a video from YouTube and relevant metadata - tags, subs,
# thumbnail, etc. More importantly, gets the highest quality DASH
# streams and muxes them together.
# Requires pafy (Python library), youtube-dl, MP4Box, and AtomicParsley.

import sys
import os
import shutil
import subprocess
import json
import tempfile
import urllib.request
import atexit
import pafy

TEMP_OUTPUT="tempout.mp4"
LANGUAGES={'bg':'bul','sk':'slo','mg':'mlg','ak':'aka','fy':'fry','ta':'tam','dz':'dzo','gu':'guj','nv':'nav','km':'khm','en':'eng','pl':'pol','ha':'hau','la':'lat','cv':'chv','sv':'swe','sd':'snd','yi':'yid','kj':'kua','ee':'ewe','zh':'chi','bs':'bos','mt':'mlt','pi':'pli','no':'nor','su':'sun','av':'ava','kk':'kaz','nr':'nbl','lu':'lub','lg':'lug','lb':'ltz','ku':'kur','ms':'may','hu':'hun','rw':'kin','et':'est','mh':'mah','sg':'sag','lo':'lao','tr':'tur','cu':'chu','kn':'kan','oc':'oci','yo':'yor','tg':'tgk','fr':'fre','es':'spa','dv':'div','se':'sme','nd':'nde','ga':'gle','kg':'kon','ja':'jpn','pa':'pan','ps':'pus','ks':'kas','kl':'kal','th':'tha','hy':'arm','fa':'per','br':'bre','rm':'roh','gn':'grn','hi':'hin','eo':'epo','mn':'mon','it':'ita','na':'nau','ff':'ful','uk':'ukr','ki':'kik','te':'tel','bm':'bam','is':'ice','as':'asm','co':'cos','am':'amh','pt':'por','ml':'mal','tn':'tsn','lt':'lit','ka':'geo','he':'heb','cr':'cre','eu':'baq','rn':'run','ug':'uig','kw':'cor','os':'oss','ia':'ina','gd':'gla','vo':'vol','kv':'kom','tk':'tuk','fj':'fij','xh':'xho','sq':'alb','vi':'vie','be':'bel','hz':'her','ae':'ave','sw':'swa','gv':'glv','ba':'bak','kr':'kau','de':'ger','bo':'tib','nn':'nno','li':'lim','or':'ori','az':'aze','my':'bur','bi':'bis','ur':'urd','qu':'que','ro':'rum','ln':'lin','ab':'abk','mr':'mar','an':'arg','si':'sin','sm':'smo','ve':'ven','ay':'aym','cs':'cze','ik':'ipk','ar':'ara','id':'ind','sn':'sna','fi':'fin','ne':'nep','to':'ton','iu':'iku','ru':'rus','wo':'wol','ti':'tir','ko':'kor','sa':'san','wa':'wln','io':'ido','ho':'hmo','ss':'ssw','nl':'dut','mi':'mao','ts':'tso','cy':'wel','ii':'iii','mk':'mac','aa':'aar','af':'afr','ky':'kir','ce':'che','ht':'hat','el':'gre','bh':'bih','sl':'slv','jv':'jav','ca':'cat','om':'orm','hr':'hrv','tt':'tat','ng':'ndo','tl':'tgl','st':'sot','ch':'cha','da':'dan','uz':'uzb','sc':'srd','ty':'tah','sr':'srp','bn':'ben','zu':'zul','tw':'twi','oj':'oji','lv':'lav','so':'som','za':'zha','ig':'ibo','fo':'fao','nb':'nob','gl':'glg','ie':'ile'}

def findBestVideoStream(streams):
    bestStream = streams[0]
    for stream in streams:
        if stream.extension == 'm4v' and not stream.threed:
            pixels = stream.dimensions[0] * stream.dimensions[1]
            if pixels > bestStream.dimensions[0] * bestStream.dimensions[1]:
                bestStream = stream
    return bestStream

def setup():
    # Make a temp directory to store the downloaded files
    tempdir = tempfile.mkdtemp(dir=".")
    os.chdir(os.path.join(os.getcwd(), tempdir))
    return tempdir

def cleanup(tempdir):
    os.chdir("..")
    shutil.rmtree(tempdir)

def getVideo(url):
    tempdir = setup()
    atexit.register(cleanup, tempdir)
    
    print("Getting video info...")
    vidInfo = pafy.new(url)
    videoId = vidInfo.videoid
    outputName = vidInfo.title + ".mp4"
    if os.path.exists(os.path.join("..", outputName)):
        overwriteResponse = input(vidInfo.title + " exists. Overwrite (y/N)? ")
        if overwriteResponse == "" or overwriteResponse[0].lower() != "y":
            print("Aborting download")
            sys.exit(1)

    videoStream = findBestVideoStream(vidInfo.videostreams)
    audioStream = vidInfo.getbestaudio(preftype='m4a')
    videoFile = videoId + ".mp4"
    audioFile = videoId + ".m4a"

    print("Downloading video... ({})".format(videoStream.resolution))
    videoStream.download(filepath=videoFile)
    print("\nDownloading audio... ({})".format(audioStream.bitrate))
    audioStream.download(filepath=audioFile)

    print("\nDownloading subtitles...")
    #TODO: Find a way to get subtitles without youtube-dl
    subprocess.call(["youtube-dl", '--all-subs', '--skip-download', videoId], stdout=subprocess.DEVNULL)

    files = os.listdir()

    subs = [f for f in files if f.endswith(".srt")]
    subMux = []
    for sub in subs:
        subLang = sub.split(".")[-2][:2]
        subLangLong = LANGUAGES[subLang]
        subInfo = "{}:lang={}".format(sub, subLangLong)
        subMux.append("-add")
        subMux.append(subInfo)

    thumbUrl = "https://i.ytimg.com/vi/{}/hqdefault.jpg".format(videoId)
    thumbFile = videoId + ".jpg"
    urllib.request.urlretrieve(thumbUrl, thumbFile)

    # Mux the streams together
    print("Muxing streams...")
    args = ["MP4Box",
        "-add", videoFile,
        "-add", audioFile,
        ] + subMux + [
        TEMP_OUTPUT]
    subprocess.call(args)

    # Add metadata
    date, time = vidInfo.published.split()
    publishDate = "{}T{}Z".format(date, time)
    metaargs = ["AtomicParsley", TEMP_OUTPUT,
        "--title", vidInfo.title,
        "--artist", vidInfo.author,
        "--year", publishDate,
        "--comment", vidInfo.watchv_url,
        "--description", vidInfo.description,
        "--copyright", vidInfo.username,
        "--artwork", videoId + ".jpg", "--overWrite"]
    subprocess.call(metaargs, stdout=subprocess.DEVNULL)
    
    os.rename(TEMP_OUTPUT, os.path.join("..", outputName))
    
    print(vidInfo.title + " finished downloading.")
    
    return vidInfo, outputName

if __name__ == "__main__":
    getVideo(sys.argv[1])
