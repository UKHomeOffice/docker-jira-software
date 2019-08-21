#!/usr/bin/python3

import sys
import os
import shutil
import logging
import jinja2 as j2
import uuid
import base64
# UKHOMEOFFICE: additional imports
import time


######################################################################
# Utils

logging.basicConfig(level=logging.DEBUG)

def set_perms(path, user, group, mode):
    shutil.chown(path, user=user, group=group)
    os.chmod(path, mode)

# Setup Jinja2 for templating
jenv = j2.Environment(
    loader=j2.FileSystemLoader('/opt/atlassian/etc/'),
    autoescape=j2.select_autoescape(['xml']))

# UKHOMEOFFICE: change default user and group from root and allow to skip permission setting
def gen_cfg(tmpl, target, env, user=None, group=None, mode=0o644, skip_set_perms=False):
    if not user:
        user = env['run_user']
    if not group:
         group = env['run_group']
    logging.info(f"Generating {target} from template {tmpl}")
    cfg = jenv.get_template(tmpl).render(env)
    with open(target, 'w') as fd:
        fd.write(cfg)
    if not skip_set_perms:
        set_perms(target, user, group, mode)

# UKHOMEOFFICE: Get the logs symlinked to stdout
def symlink_log(log_file):
        if not os.path.islink(log_file):
                if os.path.exists(log_file):
                        os.rename(log_file, f"{log_file}.{time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())}")
                os.symlink('/dev/stdout', log_file)


######################################################################
# Setup inputs and outputs

# Import all ATL_* and Dockerfile environment variables. We lower-case
# these for compatability with Ansible template convention. We also
# support CATALINA variables from older versions of the Docker images
# for backwards compatability, if the new version is not set.
env = {k.lower(): v
       for k, v in os.environ.items()}

env['uuid'] = uuid.uuid4().hex
with open('/etc/container_id') as fd:
    lcid = fd.read()
    if lcid != '':
        env['local_container_id'] = lcid


######################################################################
# Generate all configuration files for Jira

gen_cfg('server.xml.j2',
        f"{env['jira_install_dir']}/conf/server.xml", env)

gen_cfg('dbconfig.xml.j2',
        f"{env['jira_home']}/dbconfig.xml", env)

# UKHOMEOFFICE: Skip setting permissions
gen_cfg(tmpl='container_id.j2',
        target='/etc/container_id', env=env, skip_set_perms=True)

if env.get('clustered') == 'true':
    gen_cfg('cluster.properties.j2',
            f"{env['jira_home']}/cluster.properties", env)


######################################################################
# UKHOMEOFFICE: Get the Jira logs out to stdout

logs_folder = f"{env['jira_home']}/log"
if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
symlink_log(f"{logs_folder}/atlassian-greenhopper.log")
symlink_log(f"{logs_folder}/atlassian-jira.log")
symlink_log(f"{logs_folder}/atlassian-jira-security.log")


######################################################################
# Start Jira as the correct user

start_cmd = f"{env['jira_install_dir']}/bin/start-jira.sh"
if os.getuid() == 0:
    logging.info(f"User is currently root. Will change directory ownership to {env['run_user']} then downgrade permissions")
    set_perms(env['jira_home'], env['run_user'], env['run_group'], 0o700)

    cmd = '/bin/su'
    start_cmd = ' '.join([start_cmd] + sys.argv[1:])
    args = [cmd, env['run_user'], '-c', start_cmd]
else:
    cmd = start_cmd
    args = [start_cmd] + sys.argv[1:]

logging.info(f"Running Jira with command '{cmd}', arguments {args}")
os.execv(cmd, args)