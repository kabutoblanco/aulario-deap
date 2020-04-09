import array
import csv
import json
import numpy as np
import math
import time
import random
from time import time as tm

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Carga de archivos de asignaturas y salones
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
with open("PIS_ASIGNATURAS.json", "r", encoding='utf-8') as tsp_data:
    courses = json.load(tsp_data)

courses = courses["Hoja1"]

intensity = sum(int(e["CREDITOS"]) for e in courses)

with open("salones_FIET.json", "r", encoding='utf-8') as tsp_data:
    classrooms = json.load(tsp_data)

classrooms = classrooms["Hoja1"]

log = ""
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Definición de arrays de días y jornadas de estudio
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
days = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes"]
hours = [
    "07:00 - 09:00", "09:00 - 11:00", "11:00 - 13:00", "14:00 - 16:00",
    "16:00 - 18:00"
]
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Definición de constantes como la longitud del individuo SIZE
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
LEN_DAYS = len(days)
LEN_HOURS = len(hours)
LEN_CLASSROOMS = len(classrooms)

SIZE_COURSE = 3

SIZE = SIZE_COURSE * intensity

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Definición de la función fitness, individuo y población
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
creator.create("FitnessMax", base.Fitness, weights=(-1.0, ))
creator.create("Individual",
               array.array,
               typecode='d',
               fitness=creator.FitnessMax)


def generateIND(icls, size):
    ind = icls([0] * size)
    for i in range(int(size / SIZE_COURSE)):
        ind[i * SIZE_COURSE] = random.randint(0, LEN_DAYS - 1)
        ind[i * SIZE_COURSE + 1] = random.randint(0, LEN_HOURS - 1)
        ind[i * SIZE_COURSE + 2] = random.randint(0, LEN_CLASSROOMS - 1)
    return ind


toolbox = base.Toolbox()
toolbox.register("individual", generateIND, creator.Individual, SIZE)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Definición la función de evaluación
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


def evaluation(individual):
    log = "Las numeración de las restricciones corresponden a las descritas en el articulo\n"
    r = 0
    cont = 0

    checks_global = []
    checks_proffesor = []
    checks_semester = []

    for i in range(len(courses)):
        num_hours = int(courses[i]["CREDITOS"])
        checks_local = []
        for j in range(num_hours):
            subseq = individual[cont * SIZE_COURSE: cont *
                                SIZE_COURSE + SIZE_COURSE]

            cont += 1
            ind_day = int(subseq[0])
            ind_hour = int(subseq[1])
            ind_classroom = int(subseq[2])

            for chack_local in checks_local:
                # Restricción fuerte: RF1. Las clases de una misma asignatura no puede cruzarse ni en horario ni salón
                if ind_day == chack_local["day"] and ind_hour == chack_local["hour"] and ind_classroom == chack_local["classroom"]:
                    r += 1000
                    log += "RF1: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(classrooms[ind_classroom]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
                # Restricción fuerte: RF2. Las clases de una misma asignatura no puede cruzarse en horario
                if ind_day == chack_local["day"] and ind_hour == chack_local["hour"]:
                    r += 1000
                    log += "RF1: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(classrooms[ind_classroom]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
                # Restricción fuerte: RF3. Las clases de una misma asignatura no puede tener 2 jornadas en el día
                if ind_day == chack_local["day"]:
                    r += 1000
                    log += "RF3: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(classrooms[ind_classroom]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
            is_global = (ind_day, ind_hour,
                         ind_classroom) not in checks_global
            is_proffesor = (ind_day, ind_hour,
                            courses[i]["CODPRO"]) not in checks_proffesor
            # Restricción fuerte: RF4. Las clases no pueden estar en el mismo horario ni salon
            if not is_global:
                r += 1000
                log += "RF1: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(classrooms[ind_classroom]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
            # Restricción fuerte: RF5. El profesor no es omnipresente
            if not is_proffesor:
                r += 1000
                log += "RF2: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(courses[i]["PROFESOR"]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
            is_semester = False
            if len(checks_local) == 0:
                # Restricción debil: RD1. Evitar cruce en asignaturas de al menos un grupo de semestres adyacentes
                is_semester = (ind_day, ind_hour, int(
                    courses[i]["ASIGNATURA"]) + 1) not in checks_semester
                if not is_semester:
                    r += 30
                    log += "RD7: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
                is_semester = (ind_day, ind_hour, int(
                    courses[i]["ASIGNATURA"]) - 1) not in checks_semester
                if not is_semester:
                    r += 30
                    log += "RD7: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
                # Restricción fuerte: RF6. Garantizar que al menos una grupo de una asignatura de un semestre, no se repita
                is_semester = False
                is_semester = (ind_day, ind_hour, int(
                    courses[i]["ASIGNATURA"])) not in checks_semester
                if not is_semester:
                    r += 1000
                    log += "RF4: " + str(days[ind_day]) + " - " + str(hours[ind_hour]) + " - " + str(courses[i]["NOMBRE"]) + "\n"
            # Restricción fuerte: RF7. Las asignaturas practicas solo pueden dictarse en laboratorios
            if (courses[i]["TIPO"] == "TEO" and classrooms[ind_classroom]["TIPO"] != "SALON") or (courses[i]["TIPO"] == "LAB" and classrooms[ind_classroom]["TIPO"] != "LAB"):
                r += 1000
                log += "RF5: " + str(courses[i]["NOMBRE"]) + " - " + str(classrooms[ind_classroom]["TIPO"]) + "\n"
            # Restricción debil: RD2. Las asignaturas practicas de 7 semestre en adelante solo pueden dictarse en la sala 4
            if courses[i]["TIPO"] == "LAB" and int(courses[i]["ASIGNATURA"]) > 6 and classrooms[ind_classroom]["CODIGO"] != "Sala 4":
                r += 30
                log += "RD6: " + str(courses[i]["NOMBRE"]) + " - " + str(courses[i]["ASIGNATURA"]) + " - " + str(classrooms[ind_classroom]["CODIGO"]) + "\n"

            checks_local.append({
                "day": ind_day,
                "hour": ind_hour,
                "classroom": ind_classroom
            })
            if is_global:
                checks_global.append((
                    ind_day,
                    ind_hour,
                    ind_classroom
                ))
            if is_proffesor:
                checks_proffesor.append((
                    ind_day,
                    ind_hour,
                    courses[i]["CODPRO"]
                ))
            if is_semester:
                checks_proffesor.append((
                    ind_day,
                    ind_hour,
                    int(courses[i]["ASIGNATURA"])
                ))

    return r,
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Definición la funciones de impresión, en formato csv y html, respectivamente
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

def printer_log():
    name = "log_{}_{}.txt".format(
        time.strftime("%d_%m_%y"), time.strftime("%H:%M"))
    hs = open("./schedules/"+name, 'w')
    hs.write(log)

def printer_csv(individual):
    cont = 0
    section = [["Materia", "Semestre", *days, "Profesor"]]
    for i in range(len(courses)):
        num_hours = int(courses[i]["CREDITOS"])
        vector1 = [" "] * (LEN_DAYS + 2)
        vector1[0] = int(courses[i]["ASIGNATURA"])
        for j in range(num_hours):
            subseq = individual[cont * SIZE_COURSE: cont *
                                SIZE_COURSE + SIZE_COURSE]
            cont += 1
            ind_day = int(subseq[0])
            ind_hour = int(subseq[1])
            ind_classroom = int(subseq[2])
            l = 0
            for k in days:
                if k == days[ind_day]:
                    vector1[l + 1] = "{} {} {}".format(
                        hours[ind_hour], classrooms[ind_classroom]["TIPO"], classrooms[ind_classroom]["CODIGO"])
                    break
                l = l + 1
        vector1[len(vector1) - 1] = courses[i]["PROFESOR"]
        print1 = ["{} {}".format(courses[i]["NOMBRE"],
                                 courses[i]["GRUPO"]), *vector1]
        section.append(print1)
    with open("./schedules/schedules_{}_{}.csv".format(time.strftime("%d_%m_%y"), time.strftime("%H:%M")), 'w', newline='') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
        writer.writerows(section)


def printer_html(individual):
    name = "schedules_{}_{}.html".format(
        time.strftime("%d_%m_%y"), time.strftime("%H:%M"))
    html = ""
    html += "<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><meta http-equiv='X-UA-Compatible' content='ie=edge'><link rel='stylesheet' href='./styles/style.css'><title>"+name+"</title></head><body>"
    for p in range(len(classrooms)):
        html += "<div class='schedule-container'>"
        html += "<div class='schedule-title'><span>" + \
            str(classrooms[p]["TIPO"])+" " + \
            str(classrooms[p]["CODIGO"])+"</span></div>"
        html += "<div class='table-responsive'><div class='schedule-table'><table>"
        html += "<thead><tr>"
        html += "<th>Hora</th>"
        for j in days:
            html += "<th>"+str(j)+"</th>"
        html += "</thead></tr>"
        html += "<tbody>"
        cont = 0
        row_table = ["<td class='non-select'><span>" +
                     str(e)+"</span></td>" for e in hours]
        row_journals = [["<td class='shedule'></td>"]
                        * len(days) for i in hours]
        for i in range(len(courses)):
            num_hours = int(courses[i]["CREDITOS"])
            for j in range(num_hours):
                subseq = individual[cont *
                                    SIZE_COURSE: cont * SIZE_COURSE + SIZE_COURSE]
                cont += 1
                ind_day = int(subseq[0])
                ind_hour = int(subseq[1])
                ind_classroom = int(subseq[2])
                if ind_classroom == p:
                    row_journals[ind_hour][ind_day] = "<td class='shedule red'><span>" + \
                        str(courses[i]["NOMBRE"] + " " +
                            courses[i]["GRUPO"])+"</span></td>"
        for k in range(len(row_table)):
            html += "<tr>"+row_table[k]+"".join(str(e)
                                                for e in row_journals[k])+"</tr>"
        html += "</tbody>"
        html += "</table></div></div>"
        html += "</div>"
    html += "</body></html>"
    hs = open("./schedules/"+name, 'w')
    hs.write(html)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =

# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Definición la funciones de cruzamiento y mutación, respectivamente
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


def cxCourses(ind1, ind2):
    '''
        Esta función se basa en el la función cxOnePoint, la variante consiste en definir "int(len(courses) / 25" 
        al azar que represente un corte en cualquier segmento valido de asignatura
    '''
    for i in range(int(len(courses) / 25)):

        point = random.randint(0, intensity) * SIZE_COURSE

        ind1[point:], ind2[point:] = ind2[point:], ind1[point:]

    return ind1, ind2


def mutCourses(individual, indpb):
    '''
        Esta función se basa en el la función mutFlipBit, la variante consiste iterar el individuo segun el tamaño
        de los cursos, posterior, se sortea con la probalidad de indpb el cambio de variable del salón y con un nu
        evo sorteo las variables de día y jornada
    '''
    for i in range(0, len(individual), SIZE_COURSE):
        if random.random() < indpb:
            if random.random() < indpb:
                individual[i] = random.randint(0, LEN_DAYS - 1)
            if random.random() < indpb:
                individual[i + 1] = random.randint(0, LEN_HOURS - 1)
            individual[i + 2] = random.randint(0, LEN_CLASSROOMS - 1)

    return individual,
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
# Registro de los métodos anteriores definidos y el la función de selección
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
toolbox.register("evaluate", evaluation)
toolbox.register("mate", cxCourses)
toolbox.register("mutate", mutCourses, indpb=0.01)
toolbox.register("select", tools.selTournament, tournsize=3)
# = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =


def main():
    random.seed(random.random)

    start_time = tm()
    pop = toolbox.population(n=SIZE*2)
    hof = tools.HallOfFame(3)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min)
    stats.register("max", np.max)

    pop, log = algorithms.eaSimple(pop,
                                   toolbox,
                                   cxpb=0.7,
                                   mutpb=0.2,
                                   ngen=150,
                                   stats=stats,
                                   halloffame=hof,
                                   verbose=True)
    end_time = tm()
    print("Time eval: {} min".format(((end_time - start_time) / 60)))    
    printer_csv(hof[0])
    printer_html(hof[0])
    evaluation(hof[0])
    # printer_log()
    return pop, log, hof


if __name__ == "__main__":
    main()
