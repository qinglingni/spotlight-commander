#!/usr/bin/env python
# AUTHOR:  Dan Oblinger  <code@oblinger.us>
# CREATE:  2014-
# MODULE:  

import os
import re
import traceback

debug=False

KEY_REGEX = re.compile('^# ([^:]*):(.*)$')
APP_SRC_FOLDER = '/Applications/ll.app/Contents/MacOS'
TRAMPOLINE_FILE = '/tmp/ll_trampoline'

PATH = 'path'
ACTION = 'action'
TARGET = 'target'
IO = 'io'

# chrome  nstr   shell  run   console   script

def main():
    global debug
    argv = os.sys.argv
    print('### launcher.py called with: %s' % argv)
    if len(argv)>1 and argv[1]=='--debug':
        debug=True
        argv = argv[1:]
    a1 = argv[1] if len(argv)>1 else ''
    if a1=='--launch' or a1=='--now_in_console':
        return cmd_launch(argv)
    error("unknown command %r" % a1)

        
    

def cmd_launch(argv):
    now_in_console = argv[1]=='--now_in_console'
    keys = appkeys(argv[2])
    if (debug or keys.get(IO) in ['console', 'pinned']) and not now_in_console:
        print "Trampoline into console:  %s" % cap_to_str(keys)
        write_file(TRAMPOLINE_FILE, '#!/bin/sh\n%s/launcher.py %s --now_in_console "%s"\n' %
                   (APP_SRC_FOLDER, '--debug' if debug else '', keys[PATH]))
        os.system('chmod 755 "%s"' % TRAMPOLINE_FILE)
        os.system('open "%s"' % TRAMPOLINE_FILE)
        return
    if now_in_console and not debug:
        print '\033[0;0H\033[2J'
    else:
        for k,v in keys.iteritems():
            print "###   %s = %r" % (k,v)
    print '\n\n'

    try:   fn=globals()['type_%s' % keys['action']]
    except KeyError:
        error("Unknown action type '%s'" % keys.get('action'))
    try:
        fn(keys)
    except Exception, err:
        keys[IO]='pinned'
        print traceback.format_exc()
        #print sys.exc_info()[0]
    if keys.get(IO)=='pinned' or debug:
        os.sys.stdout.write('\n(press RETURN to exit)')
        raw_input()


def type_app(keys):
    os.system('open "%s"' % keys[TARGET])
def type_console(keys):
    print 'Triggering console'
    osa('tell application "Terminal" to do script "echo hello"')
def type_doc(keys):
    os.system('open "%s"' % keys[TARGET])
def type_edit(keys):
    os.system('open -e "%s"' % keys[TARGET])
def type_folder(keys):
    os.system('open "%s"' % keys[TARGET])
def type_nstr(keys):
    osa('tell application "growl" to activate')
    write_file('/ob/data/notester/mac/control.txt', 'GOTO\n%s' % keys[TARGET])
    osa('tell application "Notester" to activate')
def type_script(keys, prefix = ''):
    template = {'python':'/usr/bin/env python "%s"', 'sh':'/bin/sh "%s"'}.get(keys.get(TARGET))
    if not template: error("Unknown script interpreter.")
    os.system(prefix + (template % keys[PATH]))
def type_sh(keys):
    if 0!=os.system(keys[TARGET]):
        error('Shell Command Failed.')
def type_url(keys):
    os.system('open "%s"' % keys[TARGET])




def appkeys(file):
    keys = {PATH:os.path.join(os.getcwd(), file)}
    with open(file, 'r') as f:
        for line in f.readlines():
            result = re.search(KEY_REGEX, line)
            if result: keys[result.group(1).strip()] = result.group(2).strip()
    return keys

def error(err_str):
    raw_input("\nERROR: %s.  (hit return to exit)" % err_str)
    os.sys.exit(1)




def write_file(path, contents):
    with open(path,'w') as f:
        f.write(contents)


def cap_to_str(cap):
    """Returns string summary of a cap's parameters."""
    return 'P:%s  A:%s  T:%s' % (cap['path'], cap['action'], cap['target'])



# Executes multi-line applescript.  (cannot contain single quote (') character)
def osa(*lines):
    """Executes multi-line applescript script"""
    os.system("osascript %s" % ' '.join(["-e '%s'" % line for line in lines]))


# Runs apple script lines and captures output
def osa_fn(*lines):
    """Executes multi-line applescript script, and returns the captured output."""
    cmd = ['/usr/bin/osascript']
    for l in lines:        cmd.append('-e'); cmd.append(l)
    p = subprocess.Popen(cmd, bufsize=0, stdout=subprocess.PIPE, stderr = subprocess.PIPE)
    stdout,stderr = p.communicate()
    return stdout.rstrip()


main()