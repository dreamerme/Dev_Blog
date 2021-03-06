#!/usr/local/bin/python
#conding: utf-8

import sys
import os
import re
from fabric.api import *
import datetime
from Config.config import config as conf

conf = conf.site_config()

@task
def deploy():
    execute(lessc)
    execute(compress)
    execute(backup_database)

@task
def test():
    local("python ./runserver.py --port=8000")

@task
def build():
    admins = conf['db'].admins
    kid = conf['db'].kid
    admin = {'user': conf['username'], 'password': conf['password'], 'site_start':datetime.datetime.now().strftime("%Y-%m-%d")}
    admins.save(admin)
    print "Default Admin add Success!"
    kid.save({'k': 0})
    print "Auto uuid add Success!"

@task
def compress():
    execute(compress_all_js)
    execute(compress_css)

@task
def compress_all_js():
    compress_js('frontend')
    compress_js('backend')
    compress_js('404')

@task
def compress_js(debug_files):
    js_files = []

    target  = open('static/js/'+debug_files+'.js', "r")
    p = re.compile("document.*src=\'/(.*?)\'.*")
    for line in target:
        m = p.match(line)
        if m:
            js_files.append(m.group(1))
    target.close()

    local("rm -f static/js/%s.min*.js" % debug_files)

    compressed_file = "static/js/%s.min.js" % debug_files
    for f in js_files:
        local(
            'java -jar yuicompressor.jar --charset utf-8 --type js %s >> %s' %
            (f, compressed_file))

@task
def compress_css():
    css_files = ['frontend', 'backend', '404']

    local("rm -f static/css/*.min*.css")

    for f in css_files:
        local(
            'java -jar yuicompressor.jar --charset utf-8 --type css %s >> %s' %
            ('static/css/'+f+'.css', 'static/css/'+f+'.min.css'))

@task
def lessc():
    local("lessc static/less/frontend.less > static/css/frontend.css")
    local("lessc static/less/backend.less > static/css/backend.css")
    local("lessc static/less/404.less > static/css/404.css")


@task
def update():
    local("git pull")
    execute(deploy)

@task
def backup_database():
    local("sudo rm -rf ~/mongobak")
    local("mongodump -d %s -o ~/mongobak" % conf['dbname'])
    local("tar -czvPf ~/%s%s.tar.gz ~/mongobak/*" % (conf['dbname'], datetime.datetime.now().strftime("%Y%m%d%H%M%S")))

@task
def count_line():
    count = 0
    fcount = 0
    for root,dirs,files in os.walk(os.getcwd()):
        for f in files:
            # Check the sub directorys
            fname = (root + '/'+ f).lower()
            ext = f[f.rindex('.'):]
            try:
                if(exts.index(ext) >= 0):
                    fcount += 1
                    c = read_line_count(fname)
                    count += c
            except:
                pass

    print 'file count:%d' % fcount
    print 'count:%d' % count

exts = ['.py']
def read_line_count(fname):
    count = 0
    with open(fname, 'r') as f:
        for file_line in f:
            count += 1
        return count
