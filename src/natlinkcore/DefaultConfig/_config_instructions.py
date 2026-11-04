"""module that is loaded when no config file is found elsewhere

It hits (most likely) when no python grammar files are found, but
directories for Natlink are specified.

"""
import os
import os.path
from natlinkcore import config

join, expanduser, getenv, normpath = os.path.join, os.path.expanduser, os.getenv, os.path.normpath
isfile, isdir = os.path.isfile, os.path.isdir
home = expanduser('~')

this_dir, this_filename = __file__.rsplit('\\', 1)

# here comes the essential warning message:

msg = '\n'.join(['',
    f'This is the file "{this_filename}" from directory "{this_dir}":',
    '',
    '*** You probably configured a directory for Natlink grammars, ***',
    '*** but put no grammar files yet in this directory. ***',
    '',
    'Please put at least one Natlink grammar file (a python file ending with ".py")',
    'into the directory you specified and restart Dragon.',
    ''] )
print(msg)



natlink_settingsdir = getenv("NATLINK_SETTINGSDIR")
natlink_userdir = getenv("NATLINK_USERDIR")

if natlink_settingsdir:
    natlink_settingsdir = normpath(natlink_settingsdir)
    natlink_settings_path = config.expand_path(natlink_settingsdir)
    if os.path.isdir(natlink_settings_path):
        if natlink_settingsdir == natlink_settings_path:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}"')
        else:
            print(f'You specified for NATLINK_SETTINGSDIR: "{natlink_settingsdir}", which expands to: "{natlink_settings_path}".')
            
if natlink_userdir:
    natlink_user_path = config.expand_path(natlink_userdir)
    
    if natlink_settingsdir:
        print(f'WARNING: You also specified NATLINK_USERDIR to "{natlink_userdir}", this setting is ignored.')
    else:
        print(f'WARNING: The setting of environment variable NATLINK_USERDIR (to "{natlink_userdir}") is obsolete,')
        print('please change this setting to NATLINK_SETTINGSDIR')
        
  
msg = '\n'.join(['',
'Please try to run the config program either in GUI or in CLI (Command Line Interface) mode by running',
'***"Configure Natlink via GUI"*** or ***"Configure Natlink via CLI"***',
'\tfrom the Windows Command Prompt.',
'',
'After all these steps, restart Dragon and good luck...', '', ''])

print(msg)
