from django.shortcuts import render
import json, requests, datetime
url = "https://www.admtl.com/en/admtldata/api/flight?type=departure&sort=field_planned&direction=ASC&rule=24h"

wanted = ['id', 'type', 'flight','time', 'company', 'compagny_without_accent','destination', 'gate']

displayWanted = ["ID", "DEPARTURE/ARRIVAL", "FLIGHT","TIME","COMPANY","DESTINATION","GATE"]

modelTime = "%Y %b. %d %H:%M"

today = datetime.datetime.now()

def displayingFlights(request):
    flights = convertingFlightsToList()
    flights = filteringFlightsForToday(flights)
    flights.sort(key = sortingCriteria)
    context = {
        'flights' :flights,
        'categories' : displayWanted
    }
    return render(request, 'displayTable.html', context)

def convertingFlightsToList() :
    values=[]
    response = requests.get(url)
    data = response.json()["data"]

    for flights in data :
        flight = {}
        for categorie in wanted :
            if categorie == "time" :
                if changingTimeString(flights["revised_date"],flights["revised_hour"]) == "Nothing" :
                    flight[categorie] = changingTimeString(flights["planned_date"],flights["planned_hour"])
                else :
                    flight[categorie] = changingTimeString(flights["revised_date"],flights["revised_hour"]) 
            elif categorie == 'compagny_without_accent' :
                flight['company'] += f" - ({flights[categorie].strip()})" 
            elif flights[categorie] :
                flight[categorie] =  flights[categorie].strip() 
            else : 
                flight[categorie] =  f"None"
        values.append(flight)
    
    return values

def changingTimeString(date,hour) :
    if not hour or not date :
        return 'Nothing'
    month,day = date.split(" ")
    if len(day) == 1 : day = "0" + day
    year = datetime.datetime.now().year
    return f"{year} {month} {day} {hour}"

def getValueGate(gate):
    if "A" <= gate[-1] <= "Z" :
        return gate[:-1]
    return gate

def filteringFlightsForToday(flights):
    count = 1
    deleted = []
    for i,flight in enumerate(flights) :
        time = datetime.datetime.strptime(flight["time"], modelTime)
        gate = getValueGate(flight["gate"])
        if "None" in flight.values() :
            deleted.append(i)
        elif time.day != today.day or time.month != today.month or time.year != today.year :
            deleted.append(i)
        elif int(gate) < 62 or int(gate) > 68 :
            deleted.append(i)
        else :
            flight["num"] = count
            count += 1
    for i in deleted[::-1] :
        flights.pop(i)
    return flights

def sortingCriteria(a) :
    return datetime.datetime.strptime(a["time"], modelTime)