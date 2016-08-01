import subprocess
import math

dir_for_halon_root = "../../halon"

dir_for_output = "../website/resources/reviewers.txt"

p = subprocess.Popen(['find', dir_for_halon_root,'-name', 'REVIEWERS'], 
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)

out, err = p.communicate()

array_files = out.split("\n")
array_len = len(array_files)
array_names = {}

for i in range(0, array_len - 2):
    with open(array_files[i], "r") as file:
        array_names[i] = file.readlines()
        file.close()

array_files = [f.replace('../../', '') for f in array_files]
array_files = [f.replace('REVIEWERS', '') for f in array_files]

num_of_rows = int(math.ceil((array_len - 1) / 4.0))

html_output = ""

index = 0;

for i in range(0, num_of_rows):
    for j in range(0, 4):
        if ((i * 4) + j >= array_len - 2):
            continue
        if (j % 4 == 0):
            html_output += """<div class="w3-row">""" + "\n"
        html_output += """<div class="w3-col m3 {}">
        <div class="w3-card-8 w3-margin">
            <h3 class="w3-green w3-center">{}</h3>
                <div class="w3-padding">
                    <p style="white-space: pre-line">{}</p>
                </div>
            </div>
        </div>""".format(array_files[index], array_files[index], "".join(array_names[index]))
        index += 1
        if (j % 4 == 3):
            html_output += """</div>""" + "\n"
        

print(html_output)