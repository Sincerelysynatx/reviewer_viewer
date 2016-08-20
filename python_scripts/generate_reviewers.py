import subprocess
import math
import operator

dir_for_halon_root = "../../halon"

p = subprocess.Popen(['find', dir_for_halon_root,'-name', 'REVIEWERS'], 
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)

out, err = p.communicate()

array_files = out.split("\n")
array_len = len(array_files)
array_names = []
names = []
for i in range(0, array_len - 1):
    with open(array_files[i], "r") as file:
        temp_array_of_read_emails = file.readlines()
        if "\n" in temp_array_of_read_emails:
            temp_array_of_read_emails.remove("\n")
        temp_array_of_read_emails = [f.replace("\n", "") for f in temp_array_of_read_emails]
        names = []
        getManager = True
        for email in temp_array_of_read_emails:
            cmd = "ldap " + email + " | grep ^cn: | awk -F: '{print $2}'"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            name = p.communicate()[0]
            name.rstrip()
            if name == "":
                name = "ERROR WITH LOOKUP IN YPCAT\n"
            if getManager:
                manager_cmd = "ldap " + email + " | grep manager: | awk -F: '{print $2}' | awk -F, '{print $1}' | awk -F= '{print $2}'"
                p = subprocess.Popen(manager_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                manager_email = p.communicate()[0]
                manager_email.replace("\n", "")
                manager_email = manager_email[:-1]
                manager_name_cmd = "ldap " + manager_email + " | grep ^cn: | awk -F: '{print $2}'"
                p = subprocess.Popen(manager_name_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                manager_name = p.communicate()[0]
                manager_name.replace("\n", "")
                if manager_name == "":
                    manager_name = "ERROR WITH LOOKUP IN YPCAT\n"
                names.append("Manager: " + manager_name + "Email: " + manager_email)
                getManager = False
            names.append("Name: " + name + "Email: " + email)
        array_names.append(names)
        getManager = True
        file.close()

# Format the module string for display
array_files = [f.replace('../../', '') for f in array_files]
array_files = [f.replace('halon-src/', '') for f in array_files]
array_files = [f.replace('REVIEWERS', '') for f in array_files]
array_files = [f.replace('halon/', '') for f in array_files]
array_files = [f.replace('/', '') for f in array_files]

for n, i in enumerate(array_files):
    if i == "":
        array_files[n] = "halon"

dictionary = dict(zip(array_files, array_names))

sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(0))

html_output = ""

for module, members in sorted_dictionary:
    html_output += """<div id="{} {}" class="grid-item">
    <div class="w3-card-8 w3-margin card"><h2 class="w3-center w3-text-white w3-padding" style="background-color: #5F7A76;">{}</h2>
    <div class="w3-padding"><div class="w3-large" style="white-space: pre-line">{}</div></div></div>
    </div>""".format(module, "".join(members).lower(), module, "\n\n".join(members)) + "\n"

print(html_output)
