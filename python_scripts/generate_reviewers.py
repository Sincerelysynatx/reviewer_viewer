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
            cmd = "ypcat passwd | grep " + email + " | awk -F: '{ print $5}' | awk -F, '{ print $1}'"
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out = p.communicate()[0]
            out.rstrip()
            names.append("Name: " + out + " email: " + email + "\n\n")
        array_names.append(names)
        file.close()

# Format the string for 
array_files = [f.replace('../../', '') for f in array_files]
array_files = [f.replace('halon-src/', '') for f in array_files]
array_files = [f.replace('REVIEWERS', '') for f in array_files]

dictionary = dict(zip(array_files, array_names))

sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(0))

html_output = ""

size_of_cols = (array_len - 1) / 4

remainder = (array_len - 1) % 4

for i in range(0, 3):
    html_output += """<div id="col_{}" class="w3-third">""".format(i) + "\n"
    for j in range(0, size_of_cols):
        current = sorted_dictionary.pop()
        html_output += """<div id="{} {}" class="">
    <div class="w3-card-8 w3-margin">
        <h3 class="w3-green w3-center">{}</h3>
        <div class="w3-padding">
            <p style="white-space: pre-line">{}</p>
        </div>
    </div>
    </div>""".format(module, "".join(members), module, "".join(members)) + "\n"
    if (remainder > 0):
       html_output += """    <div id="item_remainder"></div>\n"""
       remainder -= 1
    html_output += """</div>\n"""

index = 0

#for module, members in sorted_dictionary:
#    html_output += """<div id="{} {}" class="w3-third">
#    <div class="w3-card-8 w3-margin card"><h2 class="w3-green w3-center w3-padding">{}</h2>
#    <div class="w3-padding"><p class="w3-large" style="white-space: pre-line">{}</p></div></div>
#    </div>""".format(module, "".join(members), module, "".join(members)) + "\n"
#    index += 1

print(html_output)