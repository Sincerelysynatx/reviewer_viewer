#!/usr/bin/env python
import subprocess
import math
import operator
import re
import pdb
import threading
from shutil import copyfile

global list_of_halon_modules
list_of_halon_modules = []

class Person:
    def __init__(self, email, name):
        self.email = email
        self.name = name

class Module:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.reviewers = []
        self.manager = Person("", "")

    def print_card(self):
        print(self.name + " " + self.path)
        print('\t' + "Manager of module manager: " + self.manager.name + " " + self.manager.email)
        for reviewer in self.reviewers:
            print('\t' + reviewer.name + " " + reviewer.email)

    def clean_self(self):
        self.reviewers = []


# Run find to gather all the paths to the reviewer files

def find_all_REVIEWER_files(directory):
    print("Finding REVIEWER Files")

    p = subprocess.Popen(['find', directory,'-name', 'REVIEWERS'],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)

    out, err = p.communicate()
    print("Done Finding REVIEWER Files")
    return out

# Take all the results from the find and put them into an array and remove empty directories

def create_list_from_bash_output(paths):
    array_files = paths.splitlines()
    for path in array_files:
        list_of_halon_modules.append(Module(get_name_of_module(path), path))
    #array_files.remove("")
    #print(array_files)
    return array_files

# Unused, was needed before
def remove_unwanted_paths(array_files, keywords):
    array_files_processed = []
    for file in array_files:
        for keyword in keywords:
            if keyword not in file:
                array_files_processed.append(file)
    # print(array_files_processed)
    return array_files_processed
    #for file in array_files:
    #    if keywords not in file:
    #        array_files_processed.append(file)

#

def generate_managers_and_reviewer_names():
    print("Generating reviewer names and managers")
    for i, module in enumerate(list_of_halon_modules):
        with open(module.path, "r") as file:
            temp_list_of_emails_from_REVIEWER_file = file.readlines()
            if "\n" in temp_list_of_emails_from_REVIEWER_file:
                temp_list_of_emails_from_REVIEWER_file.remove("\n") # if there are "\n" values in the array remove them
            temp_list_of_emails_from_REVIEWER_file = [f.replace("\n", "") for f in temp_list_of_emails_from_REVIEWER_file] # if there are \n's ?at the end of the values in the string remove it
            should_get_manager = True
            for email in temp_list_of_emails_from_REVIEWER_file:
                name = get_name_from_email(email)
                if should_get_manager:
                    module.manager.email = get_manager_email(email)
                    module.manager.name  = get_name_from_email(module.manager.email)
                    should_get_manager = False
                module.reviewers.append(Person(email, name))
            should_get_manager = True
            file.close()
    print("Done Generating Names")

# Use ldap search to get the name of the user who owns the provided email

def get_name_from_email(email):
    cmd  = "/usr/bin/ldapsearch -x -h ldap.hp.com -S hpStatus -b ou=People,o=hp.com uid=" + email + " | grep ^cn: | awk -F: '{print $2}'"
    p    = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    name = p.communicate()[0]
    name = name[:-1]

    if name == "":
        name = "ERROR WITH LDAP NAME LOOKUP"

    return name

# Use ldap search to get the email of the manager who owns the provided email

def get_manager_email(email):

    #use subprocess to call ldap search to get the manager of the user who owns the email
    manager_cmd = "/usr/bin/ldapsearch -x -h ldap.hp.com -S hpStatus -b ou=People,o=hp.com uid=" + email + " | grep manager: | awk -F: '{print $2}' | awk -F, '{print $1}' | awk -F= '{print $2}'"
    p           = subprocess.Popen(manager_cmd, shell=True, stdout=subprocess.PIPE)

    manager_email = p.communicate()[0]
    manager_email = manager_email[:-1]

    return manager_email

#Use regex to get the name of the folder that contains the reviewer file

def get_name_of_module(path):
    search = re.search('[^/]+(?=/REVIEWERS)', path)
    return search.group(0)

def remove_cookie_cutters():
    list_of_bad_indicies = []
    # pdb.set_trace()
    for i, module in enumerate(list_of_halon_modules):
        # pdb.set_trace()
        if "{{ cookiecutter.daemon_name }}" in module.name:
            list_of_bad_indicies.append(i)
            print("Index {}".format(i))
            print("Module {}".format(module.name))
        list_of_bad_reviewers_indicies = []
        for i, reviewer in enumerate(module.reviewers):
            if "{{cookiecutter.reviewer}}" in reviewer.email:
                list_of_bad_reviewers_indicies.append(i)
        for index in list_of_bad_reviewers_indicies:
            del module.reviewers[index]
    # pdb.set_trace()
    for index in list_of_bad_indicies:
        del list_of_halon_modules[index]

# Module HTML Structure

"""
<div id="hpe-mcastfwd-switchd-plugin
        kchavesr@hpe.com  kattia chaves ramirez
        acorvil@hpe.com  arturo jesus corrales
        villalobosbyron.rojas@hpe.com  byron josue rojas
        valverdejavier.albornoz@hpe.com  javier
        albornozrodrigo.j.hernandez@hpe.com  rodrigo jose hernandez cordoba" class="grid-item" style="position: absolute; left: 16px; top: 0.15px;">

    <div class="w3-card-8 w3-margin card">
        <h2 class="w3-center w3-text-white w3-padding" style="background-color: #5F7A76;">hpe-mcastfwd-switchd-plugin</h2>
        <div class="w3-padding"><div class="w3-large" style="white-space: pre-line">
            <div class="w3-dropdown-hover w3-hover-khaki" style="width: 100%">
                Name: Arturo Jesus Corrales Villalobos
                Email: acorvil@hpe.com
                <i class="material-icons" style="position: relative; bottom: 28px; float: right">perm_identity</i>
                <div class="w3-dropdown-content w3-card-8 w3-padding w3-round">
                    Name: Kattia Chaves Ramirez
                    Email: kchavesr@hpe.com
                </div>
            </div>

            Name: Byron Josue Rojas Valverde
            Email: byron.rojas@hpe.com

            Name: Javier Albornoz
            Email: javier.albornoz@hpe.com

            Name: Rodrigo Jose Hernandez Cordoba
            Email: rodrigo.j.hernandez@hpe.com
            </div>
        </div>
    </div>
</div>
"""

# Generates and populates the structure above to be rendered by the website

# Name of module group is used for selection purposes

def generate_html(dir_for_temp_output_file, name_of_module_group):
    html_output = ""

    #iterate through modules and generate the html for each module
    for module in list_of_halon_modules:
        if (len(module.reviewers) == 0):
            continue
        html_output += """<div id="{} {} {} {} """.format(name_of_module_group, module.name.lower(), module.manager.email.lower(), module.manager.name.lower())
        for reviewer in module.reviewers:
            html_output += """{} {}""".format(reviewer.email.lower(), reviewer.name.lower())
        html_output += """" class="grid-item"><div class="w3-card-8 w3-margin card"><h2 class="w3-center w3-text-white w3-padding" style="background-color: #5F7A76;">{}</h2><div class="w3-padding"><div class="w3-large" style="white-space: pre-line"><div class="w3-dropdown-hover w3-hover-khaki" style="width: 100%">Name:{}\nEmail: {}\n<i class="material-icons" style="position: relative; bottom: 28px; float: right">perm_identity</i><div class="w3-dropdown-content w3-card-8 w3-padding w3-round">Name:{}\nEmail: {}</div></div>\n""".format(module.name, module.reviewers[0].name, module.reviewers[0].email, module.manager.name, module.manager.email)
        for reviewer in module.reviewers: # skip the first card as it was already added to the template
            if reviewer.email is module.reviewers[0].email:
                continue
            html_output += """Name:{}\nEmail: {}\n\n""".format(reviewer.name, reviewer.email)
        html_output += """</div></div></div></div>\n"""

    output_file = open(dir_for_temp_output_file, "a")
    output_file.write(html_output)
    output_file.close()

def clean_module_list():
    for module in list_of_halon_modules:
        module.clean_self()
        del module

def run_main_program(starting_directory, tag_associated_with_directory):
    paths = find_all_REVIEWER_files(starting_directory)
    list_of_files = create_list_from_bash_output(paths)
    generate_managers_and_reviewer_names()
    remove_cookie_cutters()
    # for card in list_of_halon_modules:
    #     card.print_card()
    generate_html(dir_for_temp_output_file, tag_associated_with_directory);

dir_for_output_file = "/users/pimentes/Desktop/reviewer/website/resources/output.html"#"/ws/web/reviewer_viewer/website/resources/output.html"
dir_for_temp_output_file = "/users/pimentes/Desktop/reviewer/website/resources/output_temp.html" #"/ws/web/reviewer_viewer/website/resources/output_temp.html"

open(dir_for_temp_output_file, 'w').close()

run_main_program("/ws/pimentes/halon-temp/halon/halon-src", "halon-src") #"/ws/web/halon/halon-src/"
clean_module_list()
run_main_program("/ws/pimentes/halon-temp/halon/halon-test", "halon-test") #"/ws/web/halon/halon-test/"

open(dir_for_output_file, 'w').close()

copyfile(dir_for_temp_output_file, dir_for_output_file)
