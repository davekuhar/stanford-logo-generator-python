import sys
import zipfile
import io
import re
import cgi
import pathlib
import subprocess
import wordninja
import textwrap
from shutil import rmtree
from tempfile import mkdtemp, TemporaryFile
from time import gmtime, strftime
# from urllib.parse import parse_qs
import logging
from logging.handlers import RotatingFileHandler
import flask
from flask import request, jsonify

# Following variable is when user enter just first input.
SOURCE_SVG_LIST_1_LINE = [
  "stanford-line1-1.svg",
  "stanford-line1-1-black.svg",
  "stanford-line1-1-white.svg",
  "stanford-line1-2.svg",
  "stanford-line1-2-black.svg",
  "stanford-line1-2-white.svg",
  "stanford-line1-3.svg",
  "stanford-line1-3-black.svg",
  "stanford-line1-3-white.svg",
  "stanford-line1-5.svg",
  "stanford-line1-5-black.svg",
  "stanford-line1-5-white.svg",
]

# Following variable is when user enters both first input.
SOURCE_SVG_LIST_2_LINE = [

  "stanford-line2-1.svg",
  "stanford-line2-1-black.svg",
  "stanford-line2-1-white.svg",
  "stanford-line2-2.svg",
  "stanford-line2-2-black.svg",
  "stanford-line2-2-white.svg",
  "stanford-line2-3.svg",
  "stanford-line2-3-black.svg",
  "stanford-line2-3-white.svg",
  "stanford-line2-4.svg",
  "stanford-line2-4-black.svg",
  "stanford-line2-4-white.svg",
  "stanford-line2-5.svg",
  "stanford-line2-5-black.svg",
  "stanford-line2-5-white.svg",
  "stanford-line2-6.svg",
  "stanford-line2-6-black.svg",
  "stanford-line2-6-white.svg",
  "stanford-line2-8.svg",
  "stanford-line2-8-black.svg",
  "stanford-line2-8-white.svg",
  "stanford-line2-10.svg",
  "stanford-line2-10-black.svg",
  "stanford-line2-10-white.svg",

]
SOURCE_SVG_LIST_3_LINE = [
  "stanford-line3-1.svg",
  "stanford-line3-1-black.svg",
  "stanford-line3-1-white.svg",
  "stanford-line3-2.svg",
  "stanford-line3-2-black.svg",
  "stanford-line3-2-white.svg",
#   "stanford-line3-3.svg",
]

SOURCE_SVG_PATH = './assets/'
MASTER_OUT_SVG = 'master.svg'

ZIP_FILE = 'standford-logo-suite.zip'
ID_FILE = 'id.txt'
LOG_FILE = '/tmp/logos.txt'

IMAGEMAGICK = '/usr/bin/convert'
INKSCAPE = '/usr/bin/inkscape'

# initialize INKSCAPE and X
subprocess.run([INKSCAPE, '--without-gui'])


def out_path(tempdir, filename, new_extension=None):
  """
  :param tempdir: path to tempdir
  :param filename: name of the file
  :param extension: new extension to place on the file
  :return: tempdir/filename
  """
  # Strip and replace the extension if a new one was provided
  if new_extension is not None:
    new_filename = re.sub('\..*$', '.'+new_extension, filename)
  else:
    new_filename = filename
  return tempdir + '/' + new_filename


log_file=open(LOG_FILE, mode='a', encoding='utf-8')

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Stanford Logo Generator</h1>'''

@app.route('/api/v1/', methods=['POST'])
def create():
    p1 = cgi.escape(request.json['p1'].strip()) 
    p2 = request.json['p2'].strip() 
    p3 = cgi.escape(request.json['p3'].strip()) 
    line_number = request.json['line_number']
    logo_number = request.json['logo_number']


    # If something was entered on line 2 but not line 1, flip it to line 1
    # if len(p1) == 0 and len(p2) > 0:
    #     p1 = p2
    #     p2 = ''
    #     p3 = ''

    # replace text in the SVGs one by one
    TEMPDIR = mkdtemp(suffix='', prefix='output', dir='/tmp')

    # only generate 1-line or 2-line images, based on whether 2nd line has
    # anything on it
    if len(p1) > 0:
        SOURCE_SVG_LIST = SOURCE_SVG_LIST_1_LINE
    if len(p2) > 0:
        SOURCE_SVG_LIST = SOURCE_SVG_LIST_2_LINE
    if len(p3) > 0:
        SOURCE_SVG_LIST = SOURCE_SVG_LIST_3_LINE


    # Load each master in turn, impose text on it, and generate all the output files
    processes = []
    output_files = []
    for source_svg_file in SOURCE_SVG_LIST:
        # print(source_svg_file, file=sys.stdout)
        with open(SOURCE_SVG_PATH+source_svg_file, mode='r', encoding='utf-8') as file:
            source_svg_document = file.read()
        app.logger.info("loaded {}. Size: {}".format(source_svg_file, len(source_svg_file)))

        lines1 = p1.split("\n")
        lines2 = p2.split("\n")
        lines3 = p3.split("\n")
        text1 = ""
        text2 = ""
        text3 = ""

        if len(lines1) > 1:
            for i, line in enumerate(lines1):
                if i == 0:
                    text1 += '<tspan x="0">{}</tspan>'.format(line)
                else:
                    text1 += '<tspan x="0" y="18">{}</tspan>'.format(line)
        else:
            text1 = '<tspan x="0" y="18">{}</tspan>'.format(lines1[0])

        if len(lines2) > 1:
            for i, line in enumerate(lines2):
                if i == 0:
                    text2 += '<tspan x="0">{}</tspan>'.format(line)
                else:
                    text2 += '<tspan x="0" y="18">{}</tspan>'.format(line)
        else:
            text2 = '<tspan x="0" y="12">{}</tspan>'.format(lines2[0])

        if len(lines3) > 1:
            for i, line in enumerate(lines3):
                if i == 0:
                    text3 += '<tspan x="0">{}</tspan>'.format(line)
                else:
                    text3 += '<tspan x="0" y="18">{}</tspan>'.format(line)
        else:
            text3 = '<tspan x="0" y="18">{}</tspan>'.format(lines3[0])

        # p1 = text1
        # p2 = text2
        # p3 = text3
        if (str(line_number) == "2" and str(logo_number) == "10") or (str(line_number) != "3" and str(logo_number) == "2") or (str(line_number) == "3" and str(logo_number) == "2"):
            revised_svg_document = source_svg_document
        else:
            revised_svg_document = source_svg_document.replace('%PLACEHOLDER1%', p1)

        app.logger.info("line_number: {} logo_number: {}".format(line_number, logo_number))

        if (str(line_number) == "2" and str(logo_number) == "5") or (str(line_number) == "2" and str(logo_number) == "3"):
            # words = wordninja.split(p2)
            # first_line, second_line = ' '.join(words[:len(words)//2]), ' '.join(words[len(words)//2:])

            width = len(p2)//2
            text = p2
            wrapper = textwrap.TextWrapper(width=width)
            word_list = wrapper.wrap(text=text)
            first_line = cgi.escape(word_list[0]) 
            second_line = cgi.escape(' '.join(word_list[1:]))            

            revised_svg_document = revised_svg_document.replace('%PLACEHOLDER2%', first_line)
            revised_svg_document = revised_svg_document.replace('%PLACEHOLDER3%', second_line)
        elif str(line_number) == "2" and str(logo_number) == "10":
            if len(p2) > 0:
                # words = wordninja.split(p2)
                # first_line, second_line = ' '.join(words[:len(words)//2]), ' '.join(words[len(words)//2:])

                width = len(p2)//2
                text = p2
                wrapper = textwrap.TextWrapper(width=width)
                word_list = wrapper.wrap(text=text)
                first_line = cgi.escape(word_list[0]) 
                second_line = cgi.escape(' '.join(word_list[1:]))
                
                revised_svg_document = revised_svg_document.replace('%PLACEHOLDER1%', first_line)
                revised_svg_document = revised_svg_document.replace('%PLACEHOLDER2%', second_line)
            else:
                first_line, second_line = p1, p2
                revised_svg_document = revised_svg_document.replace('%PLACEHOLDER1%', first_line)
                revised_svg_document = revised_svg_document.replace('%PLACEHOLDER2%', second_line)
        elif str(line_number) == "3" and str(logo_number) == "1":
            # words = wordninja.split(p2)
            # first_line, second_line = ' '.join(words[:len(words)//2]), ' '.join(words[len(words)//2:])

            width = len(p2)//2
            text = p2
            wrapper = textwrap.TextWrapper(width=width)
            word_list = wrapper.wrap(text=text)
            first_line = cgi.escape(word_list[0]) 
            second_line = cgi.escape(' '.join(word_list[1:]))

            revised_svg_document = revised_svg_document.replace('%PLACEHOLDER2_1%', first_line)
            revised_svg_document = revised_svg_document.replace('%PLACEHOLDER2_2%', second_line)
        elif str(line_number) == "3" and str(logo_number) == "2":
            # words = wordninja.split(p2)
            # first_line, second_line = ' '.join(words[:len(words)//2]), ' '.join(words[len(words)//2:])

            width = len(p2)//2
            text = p2
            wrapper = textwrap.TextWrapper(width=width)
            word_list = wrapper.wrap(text=text)
            first_line = cgi.escape(word_list[0]) 
            second_line = cgi.escape(' '.join(word_list[1:]))

            revised_svg_document = revised_svg_document.replace('%PLACEHOLDER1%', first_line)
            revised_svg_document = revised_svg_document.replace('%PLACEHOLDER2%', second_line)
        else:
            if (str(line_number) == "2" and str(logo_number) == "2") or (str(line_number) == "1" and str(logo_number) == "2"):
                revised_svg_document = revised_svg_document.replace('%PLACEHOLDER1%', p1)
            revised_svg_document = revised_svg_document.replace('%PLACEHOLDER2%', p2)
        revised_svg_document = revised_svg_document.replace('%PLACEHOLDER3%', p3)
        master_svg_file = out_path(TEMPDIR, source_svg_file, 'mastersvg')
        open(master_svg_file, mode='w', encoding='utf-8').write(revised_svg_document)

        png_file = out_path(TEMPDIR, source_svg_file, 'png')

        # generate PNG
        f = TemporaryFile(dir='/tmp')
        p = subprocess.Popen([INKSCAPE, '--without-gui', '--file=' + master_svg_file, '--export-text-to-path',
                            '--export-dpi=600', '--export-background-opacity=0', '--export-png=' + png_file], stdout=f)
        processes.append((p, f))
        output_files.append(png_file)

    
    # wait for all PNG processes to finish, and dump all their outputs into the log file
    for p,f in processes:
        p.wait()
        f.seek(0)
        f.close()

    # Load each png file in turn, and generate other formats
    processes = []
    for source_svg_file in SOURCE_SVG_LIST:
        png_file = out_path(TEMPDIR, source_svg_file, 'png')
        jpg_file = out_path(TEMPDIR, source_svg_file, 'jpg')

        # generate JPG from PNG (and select background color to replace transparency)
        f = TemporaryFile(dir='/tmp')
        master_svg_file = out_path(TEMPDIR, source_svg_file, 'mastersvg')
        if 'white' in master_svg_file:
            background = 'black'
        else:
            background = 'white'
        
        if 'white' in master_svg_file or 'black' in master_svg_file:
            pass
        else:
            p = subprocess.Popen([IMAGEMAGICK, png_file, '-transparent-color', background, '-background', background,
                                '-flatten', 'jpg:', jpg_file], stdout=f)
        
            processes.append((p, f))
            output_files.append(jpg_file)

    # wait for all processes to finish, and dump all their outputs into the log file
    for p,f in processes:
        p.wait()
        f.seek(0)
        f.close()


    # EPS
    processes = []
    for source_svg_file in SOURCE_SVG_LIST:
        png_file = out_path(TEMPDIR, source_svg_file, 'png')
        eps_file = out_path(TEMPDIR, source_svg_file, 'eps')

        # generate EPS
        f = TemporaryFile(dir='/tmp')
        master_svg_file = out_path(TEMPDIR, source_svg_file, 'mastersvg')
        # p = subprocess.Popen([INKSCAPE,  '--without-gui', '--file=' + master_svg_file, '--export-text-to-path', 
        #                     '--export-ignore-filters', '--export-ps-level=3', '-E '+ eps_file], stdout=f)
        p = subprocess.Popen([INKSCAPE, '--without-gui', '--file=' + master_svg_file, '--export-text-to-path',
                            '--export-eps=' + eps_file], stdout=f)

        processes.append((p, f))
        output_files.append(eps_file)

    
    # wait for all EPS processes to finish, and dump all their outputs into the log file
    for p,f in processes:
        p.wait()
        f.seek(0)
        f.close()

    # SVG
    processes = []
    for source_svg_file in SOURCE_SVG_LIST:
        svg_file = out_path(TEMPDIR, source_svg_file, 'svg')

        # generate svg
        f = TemporaryFile(dir='/tmp')
        master_svg_file = out_path(TEMPDIR, source_svg_file, 'mastersvg')
        if 'white' in master_svg_file or 'black' in master_svg_file:
            pass
        else:
            p = subprocess.Popen([INKSCAPE, '--without-gui', '--file=' + master_svg_file, '--export-text-to-path',
                                '--export-plain-svg=' + svg_file], stdout=f)
            processes.append((p, f))
            output_files.append(svg_file)

    
    # wait for all EPS processes to finish, and dump all their outputs into the log file
    for p,f in processes:
        p.wait()
        f.seek(0)
        f.close()


    app.logger.info(output_files)
    
    zf = zipfile.ZipFile(out_path(TEMPDIR, ZIP_FILE), mode='w', compression=zipfile.ZIP_STORED)

    if logo_number and logo_number != "" and line_number != "":
        # output_files = [f for f in output_files if f.endswith('{}-{}.png'.format(line_number, logo_number)) or f.endswith('{}-{}.jpg'.format(line_number, logo_number)) or f.endswith('{}-{}.eps'.format(line_number, logo_number)) or f.endswith('{}-{}.svg'.format(line_number, logo_number))]
        output_files = [f for f in output_files if '{}-{}'.format(line_number,logo_number) in f]
    # zip them all together
    for output_file in output_files:
        zip_arc_name = '/' + re.sub('^.*\/', '', output_file)
        print("arcname = {}".format(zip_arc_name))
        try:
            zf.write(output_file, arcname=zip_arc_name)
        except:
            pass
    zf.close()

    with open(out_path(TEMPDIR, ZIP_FILE), mode='rb') as file:
        zf = file.read()

    rmtree(TEMPDIR)


    data = io.BytesIO(zf)
    data.seek(0)

    return flask.send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='standford-logo-suite.zip'
    )

if __name__ == "__main__":
    handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')

