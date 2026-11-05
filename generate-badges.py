#!/usr/bin/env python3
# coding=utf-8
import argparse
import math
import os
import subprocess
import textwrap
import sys
import sys
import re
import shutil
import subprocess

BADGESIZE = "80x50"
DEFAULTBACKGROUND = "background_default.png"
BLANKS = 20
BADGES_PER_PAGE = 4
BADGES_TEMPLATE = "badges/4BadgesOnA4.svg"
# {1095794: 'Business', 1095795: 'Personal', 1095796: 'Student', 1095797: 'Sponsor', 1095798: 'Speaker', 1095799: 'Organization', 1095800: 'Community', 1095802: 'Keynote', 1095804: 'Donation'}

BADGES = {
    "Early Bird" : DEFAULTBACKGROUND,
    "Early Bird Special" : DEFAULTBACKGROUND,
    "Authors Thank You Ticket" : DEFAULTBACKGROUND,
    "Business" : DEFAULTBACKGROUND,
    "Personal" : "background_personal.png",
    "Student" : "background_student.png",
    "Business - Invoiced" : DEFAULTBACKGROUND,
    "Business discounted" : DEFAULTBACKGROUND,
    "Volunteers and board" : "background_organization.png",
    "Organization" : "background_organization.png",
    "Speakers" : "background_speaker.png",
    "Speaker" : "background_speaker.png",
    "Last call" : "background_lastcall.png",
    "Business 50%" : DEFAULTBACKGROUND,
    "Sponsors" : DEFAULTBACKGROUND,
    "Pyladies" : DEFAULTBACKGROUND,
    "Personal - invoiced" : "background_personal.png",
    "Wait list" : DEFAULTBACKGROUND
}

CARACTERS_LIMIT = 48 # more than that would get trimmed

OUTPUTDIR = "generated"

# it doesn't work...
os.environ["PYTHONIOENCODING"] = "utf-8"


def createDirs(directory):
    '''
    It creates the need directory if it isn't there yet.
    '''
    if not os.path.exists(directory):
        os.makedirs(directory)


def shellExec(command):
    return subprocess.check_output(command.split(), stderr=subprocess.STDOUT, shell=False)


class BadgePrinter:
    def __init__(self):
        with open("badges/4BadgesOnA4.svg", encoding="UTF-8") as fileDescr:
            self.badgesPage = fileDescr.read()

        createDirs(OUTPUTDIR)

    def generateBadges(self, participants, pageNumber, background=None):
        print(f"-= PageNumber: {pageNumber} =-")
        badgesPage = self.badgesPage
        mainBackground = None
        if background is not None:
            main_background = background
        position = 0
        print("participants:", participants)
        for entry in participants:
            first_name = entry["first_name"]
            last_name = entry["last_name"]
            company = entry["company"]
            ticket_type = entry["ticket_type"]
            job_title = entry["job_title"]

            if len(company) > 46:
                company = company[:45]+ "..."

            # To handle H&M issue
            company = re.sub('&', '&amp;', company)

            # shorten too wide entries
            for entry in [first_name, last_name, company, job_title]:
                if len(entry) > CARACTERS_LIMIT:
                    entry = entry[:CARACTERS_LIMIT]

            if (position % 2) == 0:
                print(f"\t{position} {first_name} {last_name}", end='')
            else:
                print(f"\t{position} {first_name} {last_name}")
            badgesPage = badgesPage.replace("person_{}_line_1".format(position + 1), first_name)
            badgesPage = badgesPage.replace("person_{}_line_2".format(position + 1), last_name)
            badgesPage = badgesPage.replace("person_{}_line_3".format(position + 1), job_title)
            badgesPage = badgesPage.replace("person_{}_line_4".format(position + 1), company)
            if mainBackground:
                background = mainBackground
                pass
            elif ticket_type not in BADGES:
                background = DEFAULTBACKGROUND
            else:
                background = BADGES[ticket_type]
            if not os.path.exists("badges/" + background):
                raise Exception(f"{background} not found")
            badgesPage = badgesPage.replace("background_{}.png".format(position + 1), background)
            cwd = os.path.abspath(os.path.curdir)
            badgesPage = badgesPage.replace("$PWD", cwd)
            position += 1

        svg = f"{OUTPUTDIR}/badge-{pageNumber}.svg"
        pdf = f"{OUTPUTDIR}/badge-{pageNumber}.pdf"
        with open(svg, "w", encoding="UTF-8") as output:
            output.write(badgesPage)
        print("Generating page:", pageNumber)
        shellExec(f"inkscape --pipe --export-dpi=600 --export-filename={pdf} {svg}")


def getBackGround(ticketCode):
    if ticketCode in BADGES:
        return BADGES[ticketCode]
    raise Exception(f"Unknown ticket code: {ticketCode}")


def groupBackGrounds(array_ticketCodes):
    result = []
    for ticketCode in array_ticketCodes:
        result.append(getBackGround(ticketCode))

    return result


def getUserDataFormatted(firstName=None, lastName=None, ticketType=None, company=None, jobTitle=None):
    if firstName is None:
        firstName = ""
    if lastName is None:
        lastName = ""
    if ticketType is None:
        ticketType = ""
    if company is None:
        company = ""
    if jobTitle is None:
        jobTitle = ""

    return {
        "first_name": firstName,
        "last_name": lastName,
        "company": company,
        "ticket_type": ticketType,
        "job_title": jobTitle
    }


def resetParticipantsData():
    return []


def numberOfParticipants(participantsList):
    return len(participantsList)


def main(args):
    if args.csvfile is None and args.jsonfile is None:
        raise Exception("it is missing both --csvfile and --jsonfile: at the least on should be used")
    module = None
    if args.type == "eventbrite":
        print("Selecting Eventbrite format")
        import eventbritelib
        module = eventbritelib
    elif args.type == "pretix":
        print("Selecting Pretix format")
        import pretixlib
        module = pretixlib
    else:
        raise Exception("Unknown --type. Use or\"eventbrite\" or \"pretix\".")

    if args.csvfile:
        print("Parsing csv file:", args.csvfile)
        participants = module.GetParticipantsFromCSV(args.csvfile)
    elif args.jsonfile:
        print("Parsing json file:", args.jsonfile)
        participants = module.GetParticipantsFromJSON(args.jsonfile)

    badge = BadgePrinter()
    # it ended in nr different than 4
    pages = 0
    for idx in range(0, len(participants), 4):
        print("idx:", idx)
        page_participants = []
        for idx2 in range(0, 4):
            print(" * idx2:", idx2)
            try:
                page_participants.append(participants[idx + idx2])
            except IndexError:
                page_participants.append(getUserDataFormatted())
        badge.generateBadges(page_participants, pages)
        pages += 1 

    # for dummy in range(4 - len(participants)):
    #     participants.append(getUserDataFormatted(ticketType="Business"))
    # badge.generateBadges(participants, pages)
    # pages += 1


    # generating blanks
    for bg in groupBackGrounds(["Business", "Student", "Speakers", "Volunteers and board", "Last call"]):
    # for bg in groupBackGrounds(["Last call"]):
        blanks = resetParticipantsData()
        for x in range(BLANKS):
            print("Blank: ", x)
            blanks.append(getUserDataFormatted())
            if len(blanks) >= BADGES_PER_PAGE:
                badge.generateBadges(blanks, pages, background=bg)
                blanks = resetParticipantsData()
                pages += 1
    pdfFiles = []
    for p in range(0, pages):
        pdfFiles.append(f"{OUTPUTDIR}/badge-{p}.pdf")
    #os.system("pdfunite %s all_badges.pdf" % " ".join(pdfFiles))
    # ghostscript just because there is no pdfunit in macos
    shellExec("gs -dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=generated/all_badges.pdf -dBATCH %s" % " ".join(pdfFiles))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create badges for PyCon Sweden 2022.')
    parser.add_argument('--csvfile', help='CSV file with input data.')
    parser.add_argument("--jsonfile", help='JSON exported from Pretix (only Pretix is supported)')
    parser.add_argument('--type', required=True, help="Use [eventbrite|pretix] to select the type of csv content.")

    args = parser.parse_args()
    main(args)
