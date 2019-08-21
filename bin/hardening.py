#!/usr/bin/python3

import logging
import os
import time
import jinja2 as j2
from pwd import getpwuid


# Find owner of a file
def get_owner(filename):
    return getpwuid(os.stat(filename).st_uid).pw_name

# Get the logs symlinked to stdout
def symlink_log(log_file):
        if not os.path.islink(log_file):
                if os.path.exists(log_file):
                        os.rename(log_file, f"{log_file}.{time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())}")
                os.symlink('/dev/stdout', log_file)

# generate config file, defaulting to run user and group, not root, and allowing to skip permission setting
def gen_cfg_no_chown(tmpl, target, env, user=None, group=None, mode=0o644, skip_set_perms=False):
    # ignore user and group
    logging.info(f"Generating {target} from template {tmpl} (no chown)")
    # Setup Jinja2 for templating
    jenv = j2.Environment(
        loader=j2.FileSystemLoader('/opt/atlassian/etc/'),
        autoescape=j2.select_autoescape(['xml']))
    cfg = jenv.get_template(tmpl).render(env)
    with open(target, 'w') as fd:
        fd.write(cfg)
    if get_owner(target) == 'root':
        logging.info(f"Owner of {target} is {get_owner(target)}; not attempting to change permissions")
    else:
        os.chmod(target, mode)

# Get the Jira logs out to stdout
def all_logs_to_stdout():
    logging.info(f"Generating symlinks to stdout for logs")
    logs_folder = f"{os.environ['JIRA_HOME']}/log"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    symlink_log(f"{logs_folder}/atlassian-greenhopper.log")
    symlink_log(f"{logs_folder}/atlassian-jira.log")
    symlink_log(f"{logs_folder}/atlassian-jira-security.log")