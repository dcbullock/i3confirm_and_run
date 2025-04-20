#!/usr/bin/env python3

import sys
import os
import subprocess
import tkinter
from tkinter import messagebox
import configparser
import argparse


my_name,ext = os.path.basename(sys.argv[0]).rsplit(os.path.extsep, 1)
if ext:
    default_config_file = f'./{my_name}.conf'
else:
    default_config_file = f"~/.config/{my_name}/config"
default_config_data = \
f"""
# config file for {my_name}


# Command keys form the argument list
#  the command string is run using current PATH
[Command]
exit                = i3-msg exit
suspend             = systemctl suspend
reboot              = systemctl reboot
power               = systemctl poweroff

# If a message is provided for a key, then a confirmation (yes/no)
#  dialog box is presented to the user.  If no message, then the
#  command string is run without confirmation.
[Message]
exit                = Exit i3?
reboot              = Reboot?
power               = Power off?

# Optional.  If set to true here, then the command string is printed
#  on the terminal instead of being run and 'Dry Run' is added to the
#  confirmation dialog title. Default is False.
[Devel]
dry_run             = false
"""
default_config = configparser.ConfigParser()
default_config.read_string(default_config_data)
config = configparser.ConfigParser()


root = tkinter.Tk()
root.withdraw()
root.tk.call('tk', 'scaling', 2.0)


def usage():
    actions = '|'.join(list(config['Command'].keys()))
    print(f'usage: {my_name} {actions}')
    my_exit(1)


def config_help():
    print(\
f"""
A config file is required.

The default location is:
{default_config_file}

To write an example file, move any existing config file out of the way and
select 'Yes' when prompted to create the path and write a new config file.
""")
    my_exit(1)


def my_exit(rc):
    root.destroy()
    exit(rc)


def setup():
    global config
    configfile_options = ['-f', '--configfile']

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(configfile_options[0],
                        configfile_options[1],
                        default=default_config_file,
                        help='Specify alternate config file. '
                             '(default: %(default)s)')
    args, remaining_args = parser.parse_known_args()

    if args.configfile:
        configfile = args.configfile
    else:
        configfile = default_config_file

    try:
        configfile = os.path.expanduser(configfile)
    except Exception as e:
        print(e)
        my_exit()

    try:
        config_length = len(config.read(configfile))
    except Exception as e:
        config_length = 0

    if config_length == 0:
        answer = messagebox.askyesno('Config Error' + configfile,
                                             'Error reading config file.\n'
                                             'Write a new one?\n'
                                             'path: "' + configfile + '"',
                                             default=messagebox.NO)
        if answer:
            # write out the config on error after prompting the user
            try:
                configdir = os.path.dirname(configfile)
                if configdir:
                    if os.path.exists(configdir) == False:
                        os.makedirs(configdir)

                with open(configfile,'x') as fp:
                    fp.write(default_config_data)
                config = default_config
            except Exception as e:
                print()
                print(e)
                config_help()
        else:
            config_help()

    if 'Devel' not in config.sections():
        config['Devel'] = {'dry_run': False}

    parser = argparse.ArgumentParser(
            prog=my_name,
            description='Optionally prompt for confirmation and run a command.',
            epilog='\n')


    parser.add_argument('-c', '--command',
                        choices=list(config['Command'].keys()),
                        required=True)
    parser.add_argument('-n', '--dry-run', action='store_true',
                        default=config['Devel'].getboolean('dry_run'),
                        help='Display command only. (default: %(default)s)')
    parser.add_argument(configfile_options[0],
                        configfile_options[1],
                        default=default_config_file,
                        help='Specify alternate config file. '
                             '(default: %(default)s)')

    return parser.parse_args(remaining_args)



def session_ctrl(args):    
    title = "System Control"
    if args.dry_run:
        title += ' - Dry Run'

    try:
        command = config['Command'][args.command].split()
    except:
        config_help()

    try:
        message = config['Message'][args.command]
    except:
        message = None
    
    if message:
        answer = messagebox.askyesno(title,
                                             message,
                                             default=messagebox.NO)
    else:
        answer = True
    
    if answer == True:
        if args.dry_run:
            print(command)
        else:
            subprocess.run(command);
    else:
        my_exit(1)


if __name__=="__main__":
    args = setup()
    session_ctrl(args)
