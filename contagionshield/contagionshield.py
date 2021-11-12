import PySimpleGUI as sg
import pandas as pd
from py2neo import Graph

df = pd.read_csv("../db/public_places.csv", encoding='latin-1')
publicPlaces = df.Name
timeTable = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
             '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']


def pretty_people(result, name):
    new_data = []
    i = 1
    for person in result:
        new_data.append(str(i) + ") Name: " + person[name + ".name"] +
                        " - Surname: " + person[name + ".surname"] +
                        " - CF: " + str(person[name + ".cf"]))
        i = i + 1
    return new_data


# column where user can query manually
custom_query_column = [
    [
        sg.Text("Search for partecipants:", font="16"),
    ],
    [
        sg.In(key='-DATE-', size=(20, 1), default_text="2021-10-31"),
        sg.CalendarButton('Choose date', close_when_date_chosen=True, key="-CALENDAR-",
                          format='%Y-%m-%d')
    ],
    [
        sg.Text("Starting time:", font="10"),
        sg.OptionMenu(
            values=timeTable, size=(6, 1), expand_x=True, key="-START-TIME-",
            default_value="00:00"
        ),
        sg.Text("Ending time:", font="10"),
        sg.OptionMenu(
            values=timeTable, size=(6, 1), expand_x=True, key="-END-TIME-",
            default_value="23:00"
        ),
    ],
    [
        sg.Text("Select the place:", font="10"),
        sg.OptionMenu(
            values=publicPlaces, size=(12, 1), expand_x=True, key="-PLACE-",
            default_value=publicPlaces[0]
        ),
    ],
    [
        sg.Checkbox("Unvaccinated", enable_events=True, key="-UNVACCINATED-"),
        sg.Checkbox("Vaccinated", enable_events=True, key="-VACCINATED-"),
        sg.Checkbox("Tested Negative", enable_events=True, key="-TESTED-"),
        sg.Button(button_text="Send Query", enable_events=True, key="-CUSTOM-QUERY-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(55, 20),
            key="-CUSTOM-LIST-",
            horizontal_scroll=True
        )
    ]
]

# column whit predefined queries
pred_query_column = [
    [
        sg.Image(source="../images/ContagionShield.png", size=(80, 80), expand_x=True)
    ],
    [
        sg.OptionMenu(
            values=["People whose last test was positive", "Cohabitants of infected", "Infection Statistics",
                    "Vaccinated in last month", "People without Greenpass"], size=(12, 1),
            expand_x=True,
            key="-QUERY-",
            default_value="Select a predefined query",
        ),
        sg.Button(button_text="Send Query", enable_events=True, key="-SEND-QUERY-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20),
            key="-QUERY-LIST-",
            horizontal_scroll=True
        )
    ]
]

# column where user can use commands
commands_query_column = [
    [
        sg.Text("Create a meeting:", font="16"),
    ],
    [
        sg.In(key='-DATE-', size=(20, 1), default_text="2021-10-31"),
        sg.CalendarButton('Choose date', close_when_date_chosen=True, key="-CALENDAR-",
                          format='%Y-%m-%d')
    ],
    [
        sg.Text("Starting time:", font="10"),
        sg.OptionMenu(
            values=timeTable, size=(6, 1), expand_x=True, key="-START-TIME-",
            default_value="00:00"
        ),
        sg.Text("Ending time:", font="10"),
        sg.OptionMenu(
            values=timeTable, size=(6, 1), expand_x=True, key="-END-TIME-",
            default_value="23:00"
        ),
    ],
    [
        sg.Text("Select the place:", font="10"),
        sg.OptionMenu(
            values=publicPlaces, size=(12, 1), expand_x=True, key="-PLACE-",
            default_value=publicPlaces[0]
        ),
    ],
    [
        sg.Checkbox("Unvaccinated", enable_events=True, key="-UNVACCINATED-"),
        sg.Checkbox("Vaccinated", enable_events=True, key="-VACCINATED-"),
        sg.Checkbox("Tested Negative", enable_events=True, key="-TESTED-"),
        sg.Button(button_text="Send Query", enable_events=True, key="-CUSTOM-QUERY-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(55, 20),
            key="-CUSTOM-LIST-",
            horizontal_scroll=True
        )
    ]
]

# full layout
query_layout = [
    [
        sg.Column(custom_query_column),
        sg.VSeparator(),
        sg.Column(pred_query_column),
    ]
]

crud_layout = [
    [
        sg.Column(commands_query_column),
    ]
]

# Create actual layout using Columns and a row of Buttons
layout = [[sg.Column(query_layout, key='-COLQueries-'), sg.Column(crud_layout, visible=False, key='-COLCommands-')],
          [sg.Button('Queries'), sg.Button('Commands'), sg.Button('Exit')]]

window = sg.Window("ContagionShield", layout)
layout_page = "Queries"
# init database
graph = Graph("bolt://localhost:7687", auth=("neo4j", "smbud"))

# event loop
while True:
    event, values = window.read()

    if event == "-VACCINATED-":
        if values["-VACCINATED-"]:
            window["-UNVACCINATED-"].update(disabled=True)
        else:
            window["-UNVACCINATED-"].update(disabled=False)

    if event == "-UNVACCINATED-":
        if values["-UNVACCINATED-"]:
            window["-VACCINATED-"].update(disabled=True)
        else:
            window["-VACCINATED-"].update(disabled=False)

    if event == "-CUSTOM-QUERY-":
        date = window["-DATE-"].get().split("-")
        start_time = values["-START-TIME-"].split(":")
        end_time = values["-END-TIME-"].split(":")
        place = values["-PLACE-"]
        a1 = ""
        a2 = ""
        a3 = ""
        a4 = ""
        a5 = ""

        # ADESSO CONTA ANCHE LA DATA DEL VACCINO, SE HANNO FATTO IL VACCINO DOPO IL GIORNO IN CUI SONO ANDATI
        # AL PUBLIC PLACE CONTANO COME NON VACCINATI
        if values["-VACCINATED-"]:
            a1 = ", (p)-[k:GOT]->(v:Vaccine)"
            a5 = " and k.datetime < r.date_in "
        # DOVREBBE FUNZIONARE MA PER ORA NON CI SONO PERSONE NEL DB CHE SONO ANDATE IN UN PUBLIC PLACE
        # E CHE HANNO FATTO UN TEST POSITIVO ENTRO 48 ORE PRIMA
        if values["-TESTED-"]:
            a2 = ", (p)-[j:GOT_TESTED]->(t:Test)"
            a3 = "and j.result = 'Negative' and ((r.date_out - duration({hours: 48})) < j.datetime) and r.date_in > " \
                 "j.datetime "

        if values["-UNVACCINATED-"]:
            # FORSE FUNZIONA, DA PROVARE CON TANTI CASI
            # a4 = "optional match (p)-[k:GOT]->(v:Vaccine) where (k.datetime > r.date_in or k is null)"
            a4 = " AND NOT (p)-[:GOT]-> (:Vaccine)"

        query = "MATCH (p:Person)-[r:WENT_TO]-(pp:PublicPlace{name:\"" + place + "\"})" + a1 + a2 + "where " \
                                                                                                  "r.date_in.year =" + \
                date[0] + " and r.date_in.month =" + date[1] + " and r.date_in.day =" + date[2] + \
                " and ((r.date_in.hour >=" + start_time[0] + " and r.date_out.hour <=" + end_time[0] + ") or (" \
                                                                                                       "r.date_in" \
                                                                                                       ".hour <=" + \
                start_time[0] + " and r.date_out.hour >=" + end_time[0] + "))" + a3 + a5 + a4 + \
                " return distinct p.name, p.surname, p.cf "
        data = graph.run(query).data()
        pretty_data = pretty_people(data, "p")
        window["-CUSTOM-LIST-"].update(pretty_data)
        if not data:
            sg.Popup('No result', keep_on_top=True)

    if event == "-SEND-QUERY-":
        pretty_data = []
        base_query = "match (p:Person)-[r:GOT_TESTED]->(t:Test) with max(r.datetime) as lastTestDate,p match (p)-[" \
                     "r:GOT_TESTED{datetime:lastTestDate}]->(t) where r.result='Positive' with p as illPeople, " \
                     "r as rlast "
        if values["-QUERY-"] == "People whose last test was positive":
            query = base_query + "return illPeople.name, illPeople.surname, illPeople.cf "
            data = graph.run(query).data()
            pretty_data = pretty_people(data, "illPeople")
        if values["-QUERY-"] == "Cohabitants of infected":
            query = base_query + "match (p:Person)-[:LIVES_IN]->(h)<-[:LIVES_IN]-(illPeople) " \
                                 "return p.name, p.surname, p.cf"
            data = graph.run(query).data()
            pretty_data = pretty_people(data, "p")
        if values["-QUERY-"] == "Infection Statistics":
            query = "match (n:Person) with count(n) as TotalPeople match (n:Person)-[:GOT]->(v) with TotalPeople," \
                    "count(n) as totalVaccinatedPeople match(n)-[:GOT]->(v) where   date(n.birthdate)>date(" \
                    ")-duration({years:30}) and date(n.birthdate)<date()-duration({years:18}) with TotalPeople," \
                    "totalVaccinatedPeople,count(n) as range1830 match(n)-[:GOT]->(v) where   date(n.birthdate)>date(" \
                    ")-duration({years:45}) and date(n.birthdate)<date()-duration({years:30}) with range1830," \
                    "TotalPeople,totalVaccinatedPeople,count(n) as range3045 match(n)-[:GOT]->(v) where   date(" \
                    "n.birthdate)>date()-duration({years:60}) and date(n.birthdate)<date()-duration({years:45}) with " \
                    "range3045,range1830,TotalPeople,totalVaccinatedPeople,count(n) as range4560 match(n)-[:GOT]->(v) " \
                    "where   date(n.birthdate)>date()-duration({years:80}) and date(n.birthdate)<date()-duration({" \
                    "years:60}) with range4560,range3045,range1830,TotalPeople,totalVaccinatedPeople,count(n) as " \
                    "range6080 match(n)-[:GOT]->(v) where   date(n.birthdate)<date()-duration({years:80}) return " \
                    "TotalPeople,totalVaccinatedPeople,round(100*toFloat(totalVaccinatedPeople)/toFloat(" \
                    "TotalPeople)*100)/100 as totalVaccinatedPeoplePerc, range1830,round(100*toFloat(" \
                    "range1830)/toFloat(TotalPeople)*100)/100 as range1830Perc, range3045,round(100*toFloat(" \
                    "range3045)/toFloat(TotalPeople)*100)/100 as range3045Perc, range4560,round(100*toFloat(" \
                    "range4560)/toFloat(TotalPeople)*100)/100 as range4560Perc, range6080,round(100*toFloat(" \
                    "range6080)/toFloat(TotalPeople)*100)/100 as range6080Perc, count(n) as moreThan80," \
                    "round(100*toFloat(count(n))/toFloat(TotalPeople)*100)/100 as moreThan80Perc "
            data = graph.run(query).data()
            print(data)
            for attribute in data[0]:
                pretty_data.append(str(attribute) + ": " + str(data[0][attribute]))
        if values["-QUERY-"] == "Vaccinated in last month":
            query = "match (n:Person)-[r:GOT]->(v) where r.datetime>datetime()-duration({days:30}) return distinct " \
                    "n.name," \
                    "n.surname,n.cf"
            data = graph.run(query).data()
            pretty_data = pretty_people(data, "n")
        if values["-QUERY-"] == "People without Greenpass":
            query = "MATCH (p:Person) optional match (p)-[r:GOT_TESTED]->() WHERE r.datetime>datetime()-duration({" \
                    "hours:48}) with r,p where r is null with p as noTest match (noTest) where not (noTest)-[:GOT]->(" \
                    ") return noTest.name, noTest.surname, noTest.cf "
            data = graph.run(query).data()
            pretty_data = pretty_people(data, "noTest")

        window["-QUERY-LIST-"].update(pretty_data)

    if event == "Queries" or event == "Commands":
        window[f'-COL{layout_page}-'].update(visible=False)
        if event == "Commands":
            layout_page = "Commands"
        else:
            layout_page = "Queries"
        window[f'-COL{layout_page}-'].update(visible=True)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

window.close()
