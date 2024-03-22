import datetime
import time
import tiktoken

links = {"resume": "[NOT UPLOADED YET]",
"linkedin": "https://www.linkedin.com/in/parth-khanna-47870b25b/",
"email": "khanna.parth@outlook.com",
}

data = f"""
You are to answer questions from the user. If the questions are about programming or involve Parth in them, use the following context to answer them. Do not make anything up about Parth.

Context:
Parth's full name is Parth Khanna.
He is currently a 2nd year attending University of California: Santa Cruz.
He is experienced in various programming languages such as Python, C, Java, Javascript, CSS, and Swift.
His LinkedIn can be found at {links['linkedin']}.
His email is {links['email']}.
Some of his projects include:
 - Competitive robotics design prior to college through VexRobotics and RobotC
 - Google Developers Club schedule project which aims to transfer students' class schedules for a term automatically to their Google Calendar through the use of headless browser automation and Google APIs/Services such as Google Calendar API and OAuth2.
 - Personal Portfolio which is built on the foundation of Javascript, React, HTML, CSS and is elegantly tied together through the power of Three.js.
"""

data_short = f"""
You are to answer all user questions within a 150 words max response. When involving programming or Parth, use the context to answer. Here's relevant context:
Parth Khanna:

2nd year at University of California: Santa Cruz
Proficient in Python, C, Java, Javascript, CSS, Swift
LinkedIn: {links['linkedin']}
Email: {links['email']}
Projects:
VexRobotics: Competitive robotics design pre-college
Google Developers Club: Automates class schedules to Google Calendar via headless browser automation and Google APIs/services
Personal Portfolio: Utilizes Javascript, React, HTML, CSS, and Three.js.
"""


'''dates = {
    currDate: time.ctime()
}'''

def count_tokens(text, model='cl100k_base'):
    if model in tiktoken.list_encoding_names():
        encoding = tiktoken.get_encoding(model)
        return len(encoding.encode(text=text))
    else:
        return "Invalid Model Specified"