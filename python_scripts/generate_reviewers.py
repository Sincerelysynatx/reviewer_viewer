import subprocess
import math
import operator

dir_for_halon_root = "../../halon"

dir_for_output = "../website/resources/reviewers.txt"

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
        for email in temp_array_of_read_emails:
            cmd = "ypcat passwd | grep " + email + " | awk -F: '{print $5}' | awk -F, '{print $1}'"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = p.communicate()[0]
            out.rstrip()
            if out == "":
                out = "ERROR WITH LOOKUP IN YPCAT\n"
            names.append("Name: " + out + "Email: " + email)
        array_names.append(names)
        file.close()

# Format the string for display
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
    <div class="w3-padding"><p class="w3-large" style="white-space: pre-line">{}</p></div></div>
    </div>""".format(module, "".join(members).lower(), module, "\n\n".join(members)) + "\n"

print(html_output)