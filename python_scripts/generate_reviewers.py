#!/usr/bin/env python
import subprocess
import math
import operator
import re

dir_for_halon_root = "/ws/pimentes/halon"

# Update halon to get new modules / reviewer files

print("Updating Halon Repository")

p = subprocess.Popen(["git", "-C", dir_for_halon_root, "pull"],
		     stdout=subprocess.PIPE,
		     stderr=subprocess.PIPE)

out, err = p.communicate()

print(out)

print("Done Updating Halon Repository")

# Run recursive find to gather all the paths to the reviewer files

print("Finding Reviewer Files")

p = subprocess.Popen(['find', dir_for_halon_root,'-name', 'REVIEWERS'], 
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)

out, err = p.communicate()

print(out)

print("Done Finding Reviewer Files")

# Take all the results from the find and put them into an array and remove empty directories

array_files = out.split("\n")
array_files.remove("")
array_names = []
names = []

# Take everything that doesn't come from the halon-test folder path and reassign

array_files_processed = []

for file in array_files:
    if "halon-test" not in file:
        array_files_processed.append(file)

array_files = array_files_processed

print(array_files)

array_len = len(array_files)

print("Generating Managers and Names")

for i in range(0, array_len):
    with open(array_files[i], "r") as file:
        temp_array_of_read_emails = file.readlines()
        if "\n" in temp_array_of_read_emails:
            temp_array_of_read_emails.remove("\n") # if there are "\n" values in the array remove them
        temp_array_of_read_emails = [f.replace("\n", "") for f in temp_array_of_read_emails] # if there are \n's at the end of the values in the string remove it
        names = []
        getManager = True
        for email in temp_array_of_read_emails:
            cmd = "/usr/bin/ldapsearch -x -h ldap.hp.com -S hpStatus -b ou=People,o=hp.com uid=" + email + " | grep ^cn: | awk -F: '{print $2}'"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            name = p.communicate()[0]
            name = name[:-1]
            if name == "":
                name = "ERROR WITH LDAP NAME LOOKUP"
            if getManager:
                manager_cmd = "/usr/bin/ldapsearch -x -h ldap.hp.com -S hpStatus -b ou=People,o=hp.com uid=" + email + " | grep manager: | awk -F: '{print $2}' | awk -F, '{print $1}' | awk -F= '{print $2}'"
                p = subprocess.Popen(manager_cmd, shell=True, stdout=subprocess.PIPE)
                manager_email = p.communicate()[0]
                manager_email = manager_email[:-1]
                manager_name_cmd = "/usr/bin/ldapsearch -x -h ldap.hp.com -S hpStatus -b ou=People,o=hp.com uid=" + manager_email + " | grep ^cn: | awk -F: '{print $2}'"
                p = subprocess.Popen(manager_name_cmd, shell=True, stdout=subprocess.PIPE)
                manager_name = p.communicate()[0]
                manager_name = manager_name[:-1]
                if manager_name == "":
                    manager_name = "ERROR WITH LDAP NAME LOOKUP"
                names.append("Manager: " + manager_name + "\nEmail: " + manager_email)
                getManager = False
            names.append("Name: " + name + "\nEmail: " + email)
        array_names.append(names)
        getManager = True
        file.close()

print("Done Generating Names")

# Crop all uncessary inf

array_files_shorthand = []

for file in array_files:
    search = re.search('[^/]+(?=/REVIEWERS)', file)
    result = search.group(0)
    array_files_shorthand.append(result)

array_files = array_files_shorthand

dictionary = dict(zip(array_files_shorthand, array_names))

sorted_list = sorted(dictionary.items(), key=operator.itemgetter(0))

html_output = ""

print("Generating HTML")

while sorted_list:
    pair = sorted_list.pop(0)
    html_output += """<div id="{} """.format(pair[0])
    for member in pair[1]:
    	html_output += """{}""".format(member.lower())
    html_output += """" class="grid-item"><div class="w3-card-8 w3-margin card"><h2 class="w3-center w3-text-white w3-padding" style="background-color: #5F7A76;">{}</h2><div class="w3-padding"><div class="w3-large" style="white-space: pre-line"><div class="w3-dropdown-hover w3-hover-khaki" style="width: 100%">{}<i class="material-icons" style="position: relative; bottom: 28px; float: right">perm_identity</i><div class="w3-dropdown-content w3-card-8 w3-padding w3-round">{}</div></div>""".format(pair[0], pair[1].pop(1) + "\n", pair[1].pop(0))
    for member in pair[1]:
    	html_output += """{}\n\n""".format(member)
    html_output += """</div></div></div></div>\n"""

print(html_output)

print("Done Generating HTML")

output_file = open("/var/www/html/halon_src_reviewers/resources/output.html", "w")

output_file.write(html_output)

output_file.close()
