#!/usr/bin/python

import codecs
import sys
import xml.etree.ElementTree
from string import Template
from html import escape 

if len(sys.argv) != 2:
  print("Usage:")
  print("1. Open Jira")
  print("2. Select 'Issues' / 'Search for issues'")
  print("3. Add a 'Sprint' filter and select current sprint")
  print("4. Optionally filter 'Projects' and/or 'States'")
  print("5. Select 'XML' download in the upper right menu")
  print("6. python jira2board.py SearchRequest.xml")
  print("7. Open SearchRequest.xml.html in Firefox")
  print("8. Print on A4 / Landscape / Scale 100% / Color")
  sys.exit(1)

fni = sys.argv[1]
fno = fni + ".html"
  
def findTicket(tickets, key):
  for ticket in tickets:
    if ticket['key'] == key:
      return ticket
  return None

def findTicketsByType(tickets, type):
  tmp = []
  for ticket in tickets:
    if ticket['type'] == type:
      tmp.append(ticket)
  return tmp

def parse():
  tickets = []
  root = xml.etree.ElementTree.parse(fni).getroot()
  items = root.findall("./channel/item")
  for item in items:  
    ticket_key = item.find("./key").text
    ticket_type = item.find("./type").text
    ticket_summary = item.find("./summary").text

    ticket_parent_key = None
    tmp = item.findall("./customfields/customfield[@id='customfield_10008']/customfieldvalues/customfieldvalue")
    if tmp:
      ticket_parent_key = tmp[0].text

    tmp = item.findall("./subtasks/subtask")
    subs = []
    for sub in tmp:
      subs.append(sub.text)

    ticket = {
      'key': ticket_key,
      'type': ticket_type,
      'summary': ticket_summary,
      'parent_key': ticket_parent_key,
      'parent_type': None,
      'subs': subs,    
    }
    tickets.append(ticket)

  for ticket in tickets:
    if ticket['subs']:
      for sub in ticket['subs']:
        t = findTicket(tickets, sub)
        if t:
          t['parent_key'] = ticket['key']
  
  for ticket in tickets:
    if ticket['parent_key']: 
      t = findTicket(tickets, ticket['parent_key'])
      if t:
        ticket['parent_type'] = t['type']

  return tickets

def type2colortop(type):
  if type == 'Story':
    return {'fg': 'white', 'bg': '#10a009'}
  if type == 'Task':
    return {'fg': 'white', 'bg': '#0d75b1'}
  if type == 'Bug':
    return {'fg': 'white', 'bg': '#d51010'}
  if type == 'Sub-task':
    return {'fg': 'black', 'bg': '#f4ed23'}
  if type == 'Epic':
    return {'fg': 'white', 'bg': '#ae2ca6'}
  return {'fg': 'white', 'bg': '#10d5bb'}

def type2colorbtm(type):
  if type == 'Story':
    return {'fg': 'white', 'bg': '#10a009' }
  if type == 'Task':
    return {'fg': 'white', 'bg': '#0d75b1' }
  if type == 'Bug':
    return {'fg': 'white', 'bg': '#d51010' }
  if type == 'Sub-task':
    return {'fg': 'black', 'bg': '#f4ed23' }
  if type == 'Epic':
    return {'fg': 'white', 'bg': '#ae2ca6'}
  return {'fg': 'white', 'bg': 'gray' }

if __name__ == "__main__":
  tickets = parse()
  i = 0
  html = '<!DOCTYPE html>\n<html>\n<head><meta http-equiv="content-type" content="text/html; charset=UTF-8"><meta charset="utf-8"><title>jira2board</title></head>\n<body style="padding:0px; margin:0px;">\n'
  for ticket in tickets:
    if not i%9:
      html += '<div style="width:260mm; height:160mm; text-align:left;">\n'
    s = Template('<div style="width:82mm; height:5cm; outline: solid black 2px; display: inline-block; margin:5px; text-align:center;">\n<div style="height:12mm; max-height:12mm; overflow: hidden; font-size:1cm; background-color:$color_top_bg; outline: solid black 2px; color: $color_top_fg;">$text_top</div>\n<div style="height:30mm; max-height:30mm; overflow: hidden; font-size:6mm;">$text_mid</div>\n<div style="height:8mm;  max-height:8mm;  overflow: hidden; font-size:7mm; overflow: hidden; outline: solid black 2px; background-color: $color_btm_bg; color: $color_btm_fg;">$text_btm</div>\n</div>\n')
    color_top = type2colortop(ticket['type'])
    color_btm = type2colorbtm(ticket['parent_type'])
    html += s.substitute(color_top_fg=color_top['fg'], color_top_bg=color_top['bg'], color_btm_fg=color_btm['fg'], color_btm_bg=color_btm['bg'], text_top=ticket['key'], text_mid=escape(ticket['summary']), text_btm=ticket['parent_key'])
    i = i + 1
    if not i%9:
      html += '</div>\n<div style="display: block; page-break-before: always;"></div>\n'
  html += '\n</div>\n</body>\n</html>'

  f = codecs.open(fno, "w", "utf-8")
  f.write(html)
  f.close()

  print("Created {0} tickets in {1}".format(len(tickets), fno))
  print("Epic: {0}".format(len(findTicketsByType(tickets, 'Epic'))))
  print("Story: {0}".format(len(findTicketsByType(tickets, 'Story'))))
  print("Task: {0}".format(len(findTicketsByType(tickets, 'Task'))))
  print("Bug: {0}".format(len(findTicketsByType(tickets, 'Bug'))))
  print("Sub-task: {0}".format(len(findTicketsByType(tickets, 'Sub-task'))))
