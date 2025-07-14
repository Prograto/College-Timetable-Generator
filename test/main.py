from timetable import settimetable

def dict_info(iterables):
    c,s=0,0
    for i in iterables:
        c+=1
        s += i[0]
    return [c,s]
def peroids_adjust(theory_subs_data,vacent_periods):
    def change_peroids_no(impno):
        for j in theory_subs_data.keys():
            if theory_subs_data[j][1]==impno:
                theory_subs_data[j][0]+=1
    for i in range(1,vacent_periods+1):
        change_peroids_no(i)
    return theory_subs_data

#Here data is {Subjects{subject:[importance,no of peroids]},Labs:{lab_name:[peroids,1 if it has theory subjects else 0]}
data = {"Subjects":{"java":[1,1],"pas":[1,2],"os":[1,3],"daa":[1,4],"mef":[1,5]},
        "Labs":{"iot":[3,0],"Java":[3,1],"os":[3,1],"ccna":[3,0]},
        "Speacial_subs":{"counciling":[1],"consistution":[1]}}
total_periods = 42
labs_info = dict_info(data["Labs"].values())
vacent_peroids = 42
print("The no of labs =",labs_info[0])
print("The sum of lab peroids per week =",labs_info[1])
vacent_peroids = vacent_peroids - labs_info[1]
print("The no of vecant peroids =",vacent_peroids)
speacial_subs_info = dict_info(data["Speacial_subs"].values())
print("The no of speacial_subs =",speacial_subs_info[0])
print("The sum of special peroids per week =",speacial_subs_info[1])
vacent_peroids = vacent_peroids - speacial_subs_info[1]
print("The no of vecant peroids =",vacent_peroids)
#logic for peroids
subjects_info = dict_info(data["Subjects"].values())
rought_peroids_theory = vacent_peroids // subjects_info[0]
vacent_peroids = vacent_peroids % subjects_info[0]
theory_subs_data = data["Subjects"]
subs_count = rought_peroids_theory
for i in theory_subs_data.keys():
    theory_subs_data[i][0] = subs_count
if(vacent_peroids):
    theory_subs_data = peroids_adjust(theory_subs_data,vacent_peroids)
print("No of Theory subjects:",theory_subs_data)
print("Printing the time table for the respective classes")
#CALLING FUNCTION FOR TIME TABLE MAKING
settimetable(data["Labs"],theory_subs_data)





