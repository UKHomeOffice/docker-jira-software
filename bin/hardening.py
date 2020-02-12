#!/usr/bin/python3

import logging
import os
import time
import jinja2 as j2
from pwd import getpwuid

env = {k.lower(): v
       for k, v in os.environ.items()}


# Setup Jinja2 for templating
jenv = j2.Environment(
    loader=j2.FileSystemLoader('/opt/atlassian/etc/'),
    autoescape=j2.select_autoescape(['xml']))

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
def gen_cfg_no_chown(tmpl, target, user='root', group='root', mode=0o644, overwrite=True):
    if not overwrite and os.path.exists(target):
        logging.info(f"{target} exists; skipping.")
        return

    logging.info(f"Generating {target} from template {tmpl}")
    cfg = jenv.get_template(tmpl).render(env)
    try:
        with open(target, 'w') as fd:
            fd.write(cfg)
    except (OSError, PermissionError):
        logging.warning(f"Container not started as root. Bootstrapping skipped for '{target}'")
    # don't change the perms as running as non-privileged user already
    # else:
    #     set_perms(target, user, group, mode)

# Get the Jira logs out to stdout
def all_logs_to_stdout():
    logging.info(f"Generating symlinks to stdout for logs")
    logs_folder = f"{os.environ['JIRA_HOME']}/log"
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
    symlink_log(f"{logs_folder}/atlassian-greenhopper.log")
    symlink_log(f"{logs_folder}/atlassian-jira-apdex.log")
    symlink_log(f"{logs_folder}/atlassian-jira-incoming-mail.log")
    symlink_log(f"{logs_folder}/atlassian-jira-security.log")
    symlink_log(f"{logs_folder}/atlassian-jira-slow-queries.log")
    symlink_log(f"{logs_folder}/atlassian-servicedesk.log")
