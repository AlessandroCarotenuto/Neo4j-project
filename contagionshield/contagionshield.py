import PySimpleGUI as sg
from py2neo import Graph


def checkFields():
    if window["-DATE-"].get() == "" or window["-PLACE-"].get() == "":
        window["-CUSTOM-QUERY-"].update(disabled=True)
    else:
        window["-CUSTOM-QUERY-"].update(disabled=False)

# column where user can query manually
custom_query_column = [
    [
        sg.Text("Search for partecipants:", font="16"),
    ],
    [
        sg.Text("Date:"),
        sg.In(size=(25, 1), enable_events=True, key="-DATE-", default_text="03/11/2020 8:00"),
    ],
    [
        sg.Text("Name of the place:"),
        sg.In(size=(25, 1), enable_events=True, key="-PLACE-", default_text="Pizzeria da Mario"),
    ],
    [
        sg.Checkbox("Vaccinated/Tested", enable_events=True, key="-VACCINATED-"),
        sg.Button(button_text="Send Query", enable_events=True, key="-CUSTOM-QUERY-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20),
            key="-CUSTOM-LIST-"
        )
    ]
]

# column whit predefined queries
pred_query_column = [
    [
        sg.Image(source="../images/ContagionShield.png", size=(80, 80), expand_x=True)
    ],
    [
        sg.ButtonMenu(
            "Select a predefined query", expand_x=True, key="-QUERY-",
            menu_def=[["q1", "q2", "q3"], ["Query 1", "Query 2", "Query 3"]],
        )
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20),
            key="-QUERY-LIST-"
        )
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
    if event == "-DATE-":
        checkFields()

    if event == "-PLACE-":
        checkFields()

    if event == "-QUERY-":
        data = graph.run("MATCH (people:Person) RETURN people.name LIMIT 10").data()
        window["-QUERY-LIST-"].update(data)

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

window.close()
