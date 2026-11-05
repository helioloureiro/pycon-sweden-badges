import csv
import html
import json
import re


def GetParticipantsFromCSV(csvfile: str):
    participants = []
    with open(csvfile, encoding='utf-8') as csvFile:
        for row in csv.DictReader(csvFile):
            if row["Status"] != "paid":
                continue
            try:
                firstName = html.escape(row["Given name"])
                familyName = html.escape(row["Family name"])
            except KeyError:
                full_name = row["Name"].split()
                firstName = html.escape(full_name[0])
                familyName = html.escape(" ".join(full_name[1:]))
            company = html.escape(row['Company'])
            ## Job title is missing on the CSV
            # jobTitle = html.escape(row["Job"])
            jobTitle = ""
            payment = int(row["Order total"])
            # if payment > 2500:
            #     job_title = "Business"
            # elif payment == 700:
            #     job_title = "Student"
            ## sinc there is no differenciation on the ticket type, 
            ## send all as business
            ticketType = "Business"
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


def _normalizeTicketName(ticket: str) -> str:
    ticket = ticket.split()[0]
    return ticket


def GetParticipantsFromJSON(jsonfile: str) -> list[dict[str, str]]:
    participants = []

    with open(jsonfile) as fh:
        jf = json.load(fh)
    tickets = {}
    ticket_types = jf["event"]["items"]
    for t in ticket_types:
        ticket_id = t["id"]
        ticket_name = _normalizeTicketName(t["name"])
        if ticket_name in ("T-shirt", "AfterCon"):
            continue
        tickets[ticket_id] = ticket_name

    print(tickets)
    orders = jf["event"]["orders"]

    # participants.append({
    # "first_name": firstName,
    # "last_name": familyName,
    # "company": company,
    # "ticket_type": ticketType,
    # "job_title": jobTitle
    # })

    for o in orders:
        full_name = ""
        company = ""
        ticket_type = ""
        job_title = ""
        for p in o["positions"]:
            if "attendee_name" in p and p["attendee_name"] is not None:
                full_name = p["attendee_name"]
            for a in p["answers"]:
                if a["question"] == 294029:
                    company = a["answer"]
            if "item" in p:
                if p["item"] in tickets:
                    ticket_type = tickets[p["item"]]

        name_chunks = full_name.split()
        first_name = name_chunks[0].capitalize()
        last_name = name_chunks[-1].capitalize()
        print(first_name, last_name, company, ticket_type, job_title)
        participants.append({
            "first_name": first_name,
            "last_name": last_name,
            "company": company,
            "ticket_type": ticket_type,
            "job_title": job_title
        })
    return participants
