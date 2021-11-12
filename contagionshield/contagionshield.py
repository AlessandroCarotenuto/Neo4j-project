import PySimpleGUI as sg
import pandas as pd
from py2neo import Graph

df = pd.read_csv("../db/public_places.csv", encoding='latin-1')
publicPlaces = df.Name
timeTable = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
             '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00']


def open_window():
    layout = [[sg.Text("New Window", key="new")]]
    window = sg.Window("Second Window", layout, modal=True)
    choice = None
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

    window.close()


# column where user can query manually
custom_query_column = [
    [
        sg.Text("Search for partecipants:", font="16"),
    ],
    [
        sg.In(key='-DATE-', size=(20, 1), default_text="2021-01-01"),
        sg.CalendarButton('Choose date', close_when_date_chosen=True, key="-CALENDAR-",
                          format='%Y-%m-%d', location=(0, 0))
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
            default_value="01:00"
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
            values=["Con chi vive Angelo Martini?", "Query 2", "Query 3"], size=(12, 1), expand_x=True, key="-QUERY-",
            default_value="Select a predefined query"
        ),
        sg.Button(button_text="Send Query", enable_events=True, key="-SEND-QUERY-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20),
            key="-QUERY-LIST-",
            horizontal_scroll=True
        )
    ],
    [
        sg.Button("Open Command Window", key="-OPEN-", size=41)
    ]
]

# full layout
layout = [
    [
        sg.Column(custom_query_column),
        sg.VSeparator(),
        sg.Column(pred_query_column),
    ]
]

window = sg.Window("ContagionShield", layout)

# init database
graph = Graph("bolt://localhost:7687", auth=("neo4j", "smbud"))

# event loop
while True:
    event, values = window.read()

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
            a4 = "NOT (p)-[:GOT]-> (:Vaccine)"

        query = "MATCH (p:Person)-[r:WENT_TO]-(pp:PublicPlace{name:'" + place + "'})" + a1 + a2 + "where " \
                "r.date_in.year =" + date[0] + " and r.date_in.month =" + date[1] + " and r.date_in.day =" + date[2] + \
                " and ((r.date_in.hour >=" + start_time[0] + " and r.date_out.hour <=" + end_time[0] + ") or (" \
                "r.date_in.hour <=" + start_time[0] + " and r.date_out.hour >=" + end_time[0] + "))" + a3 + a5 + a4 + \
                "return distinct p.name, p.surname, p.cf "
        data = graph.run(query).data()
        pretty_data = []
        i = 1
        for person in data:
            pretty_data.append(str(i) + ") Name: " + person["p.name"] +
                               " - Surname: " + person["p.surname"] +
                               " - CF: " + str(person["p.cf"]))
            i = i + 1
        window["-CUSTOM-LIST-"].update(pretty_data)
        if not data:
            sg.Popup('No result', keep_on_top=True)

    if event == "-SEND-QUERY-":
        print(values)
        if values["-QUERY-"] == "Con chi vive Angelo Martini?":
            data = graph.run("match(k{name:'Angelo', surname:'Martini' })-[:LIVES_IN*0..]-(h)<-[:LIVES_IN]-("
                             "p:Person) return p.name, p.surname, p.cf").data()
            pretty_data = []
            i = 1
            for person in data:
                pretty_data.append(str(i) + ") Name: " + person["p.name"] +
                                   " - Surname: " + person["p.surname"] +
                                   " - CF: " + str(person["p.cf"]))
                i = i + 1
            window["-QUERY-LIST-"].update(pretty_data)

    if event == "-OPEN-":
        open_window()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

window.close()
