import csv
import html


def GetParticipantsFromCSV(csvfile: str):
    participants = []
    with open(csvfile, encoding='utf-8') as csvFile:
        for row in csv.DictReader(csvFile):
            if row["Attendee Status"] != "Attending":
                continue
            try:
                firstName = html.escape(row["First Name"])
                familyName = html.escape(row["Surname"])
            except KeyError:
                full_name = row["Name"].split()
                firstName = html.escape(full_name[0])
                familyName = html.escape(" ".join(full_name[1:]))
            company = html.escape(row['Company'])
            ticketType = html.escape(row['Ticket Type'])
            jobTitle = html.escape(row['Job title'])
            print(f"{firstName} {familyName} from {company} at {ticketType} as {jobTitle}")
            participants.append({
                "first_name": firstName,
                "last_name": familyName,
                "company": company,
                "ticket_type": ticketType,
                "job_title": jobTitle
            })
    return participants


def resetParticipantsData():
    return []


def numberOfParticipants(participantsList):
    return len(participantsList)


def GetParticipantsFromJSON(jsonfile: str):
    raise Exception("method not supported for EventBrite")
