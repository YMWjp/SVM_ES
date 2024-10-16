#!/usr/bin/env python
# coding: utf-8
'''
A function that downloads eg data from LHD server, which is provided by LHD
diagnostic team.

The typical usage is

>>> igetfile(diagname, shotenum, subshotnum, output_name)

Returns the output-filename.
To read the data, eg.loadtxt(output_filename)
can be used.
'''

from ftplib import FTP
import zipfile
import os
from optparse import OptionParser
import requests

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

def ftpGet(targetpath, outputpath):
    # import pdb; pdb.set_trace()
    ftp = FTP('egftp1.lhd.nifs.ac.jp')
    ftp.set_pasv(True)
    ftp.login()
    cmd = 'RETR %s' % targetpath
    fpo = open(outputpath, 'wb')
    ftp.retrbinary(cmd, fpo.write)
    fpo.close()
    ftp.quit()

def ftpGetFromHttp(shotNO, diagname, subshotNO=1, savename=''):
    # HTTPサーバーからデータを取得するURLを構築
    url = 'http://exp.lhd.nifs.ac.jp/opendata/LHD/webapi.fcgi?cmd=getfile&diag={0}&shotno={1}&subno={2}'.format(diagname, shotNO, subshotNO)
    response = requests.get(url)

    # HTTPリクエストが成功した場合
    if response.status_code == 200:
        # savenameが空の場合、デフォルトのファイル名を生成
        if savename == '':
            savename = '{0}@{1}.dat'.format(diagname, shotNO)
        else:
            savename = './egdata/{0}@{1}.dat'.format(diagname, shotNO)
        # テキストデータを指定されたファイル名で保存
        with open(savename, 'w') as f:
            f.write(response.text)
    else:
        # HTTPリクエストが失敗した場合、エラーを表示
        print(response.status_code)
        print(f'error in HTTP request: {diagname} {shotNO} {subshotNO}')
    
    # HTTPステータスコードを返す
    return response.status_code

def ftpList(targetpath):
    # import pdb; pdb.set_trace()
    ftp = FTP('egftp1.lhd.nifs.ac.jp')
    ftp.login()
    flist = ftp.nlst(targetpath)
    ftp.quit()
    return flist

def unzip(targetfile):
    zf = zipfile.ZipFile(targetfile, 'r')
    flist = []
    for target in zf.namelist():
        try:
            data = zf.read(target)
            fpo = open(target, 'wb')
            fpo.write(data)
            fpo.close()
            flist.append(target)
        except ValueError:
            data = None
    zf.close()
    os.remove(targetfile)
    return flist


def icheckfile(diagname, shotno, subshot):
    targetfolderpath = 'data/'
    targetfolderpath = targetfolderpath + diagname + '/'
    firstshotno = int(shotno / 1000) * 1000
    firstfolder = '%06d/' % firstshotno
    targetfolderpath = targetfolderpath + firstfolder
    secondfolder = '%06d/' % shotno
    targetfolderpath = targetfolderpath + secondfolder
    subfolder = '%06d' % subshot
    targetfolderpath = targetfolderpath + subfolder
    #print targetfolderpath
    filelist = ftpList(targetfolderpath)
    if 0 == len(filelist):
        return False
    return True

def igetfile(diagname, shotno, subshot, outputname):
    targetfolderpath = 'data/'
    targetfolderpath = targetfolderpath + diagname + '/'
    firstshotno = int(shotno / 1000) * 1000
    firstfolder = '%06d/' % firstshotno
    targetfolderpath = targetfolderpath + firstfolder
    secondfolder = '%06d/' % shotno
    targetfolderpath = targetfolderpath + secondfolder
    subfolder = '%06d' % subshot
    targetfolderpath = targetfolderpath + subfolder
    #print targetfolderpath
    # filelist = ftpList(targetfolderpath)
    ftpGetFromHttp(shotno, diagname, subshot, outputname)
    # if 0 == len(filelist):
    #     return None
    # for fn in filelist:


    #     if fn[-4:].upper() == '.ZIP':
    #         targetpath = fn
    #         targetfile = targetpath.split('/')[-1]
    #         print("igetfile")
    #         print(targetpath) # support python 3
    #         print(targetfile)
    #         ftpGet(targetpath, targetfile)
    #         files = unzip(targetfile)
    #         os.rename(files[0], outputname)


        # ftpGetFromHttp(shotno, diagname, subshot, outputname)
    return outputname

if __name__ == '__main__':
    #fpath = 'data/lhdcxs7_cvi/103000/103912/000001/lhdcxs7_ti@103912.dat.zip'
    parser = OptionParser()
    parser.add_option("-s", "--shot", dest="shotno",
            help = "Shot number", metavar="SHOTNO")
    parser.add_option("-m", "--sub", dest="subshotno",
            help = "Subshot number", metavar="SUBSHOTNO")
    parser.add_option("-d", "--diagname", dest="diagname",
            help = "Diagnostic name", metavar="DIAGNAME")
    parser.add_option("-o", "--output", dest="output",
            help = "Output filename", metavar="OUTPUT")
    (options, args) = parser.parse_args()
    shotno = options.shotno
    subshotno = options.subshotno
    diagname = options.diagname
    output = options.output
    try:
        sn = int(shotno)
    except ValueError:
        exit(-1)
    try:
        sub = int(subshotno)
    except ValueError:
        exit(-1)
    if not diagname:
        exit(-1)
    if not output:
        exit(-1)

    ret = igetfile(diagname, sn, sub, output)
    if ret is None:
        print('Error: there is no data for the shot.')
        exit(-1)
    exit(0)
