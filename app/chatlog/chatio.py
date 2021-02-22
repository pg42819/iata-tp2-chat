from datetime import datetime
from pathlib import Path
import pandas as pd
from lxml import etree
import xml.dom.minidom
import os
import xml.sax.saxutils as saxutils
DATE_FORMAT = "%Y %m %d"
TIME_FORMAT = "%H:%M:%S"
DATE_COMMA_TIME_FORMAT = f'{DATE_FORMAT},{TIME_FORMAT}'
DATA_DIR = "data"
LOG_DIR = "logs"
AIML_DIR = "aiml"
CHAT_LOG_COLS = 'date,time,user,message'
SUGGEST_FILE = "suggestions"
SUGGEST_COLS = 'pattern,suggestion'


def find_file(name, suffix, dir_name=LOG_DIR, start_fresh=False):
    app_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = app_dir / DATA_DIR / dir_name
    if not data_dir.exists():
        data_dir.mkdir()
    filename = f'{name}{suffix}'
    file = data_dir / filename
    return file


def find_csv_file(name, columns, dir_name=LOG_DIR, suffix=".csv", start_fresh=False):
    csv_file = find_file(name, suffix=suffix, dir_name=dir_name, start_fresh=start_fresh)
    if not csv_file.exists() or start_fresh:
        f = open(str(csv_file), "w")
        header = f'{columns}\n'
        f.write(header)
        f.close()
    return csv_file


def find_chatlog(room, start_fresh=False):
    return find_csv_file(name=room, columns=CHAT_LOG_COLS, start_fresh=start_fresh)


def log_chat(room, user, message):
    log_file = find_chatlog(room)
    f = open(str(log_file), "a")
    now = datetime.now()
    date_time = now.strftime(DATE_COMMA_TIME_FORMAT)
    message = str(message).replace(',', ';') # replace comma in case it message up csv
    log_line = f'{date_time},{str(user)},{message}'
    f.write(log_line + '\n')
    f.close()


def load_conversation(room, start_fresh=False):
    log_file = str(find_chatlog(room, start_fresh))
    mydateparser = lambda x: pd.datetime.strptime(x, TIME_FORMAT)
    log = pd.read_csv(log_file, parse_dates=['time'], date_parser=mydateparser)
    return log


def find_suggest_file(start_fresh):
    return find_csv_file(name=SUGGEST_FILE, columns=SUGGEST_COLS, start_fresh=start_fresh)


def to_aiml_template(message: str, srai):
    template = message.replace("*", "<star/>")
    if srai:
        template = f"<srai>{template}</srai>"
    return template


def add_suggestion(pattern, message, srai=True, start_fresh=False):
    template = to_aiml_template(message, srai)
    add_suggestion_csv(pattern, template, start_fresh)
    add_suggestion_aiml(pattern, template, start_fresh)

def add_suggestion_csv(pattern, message, start_fresh=False):
    csv_file = find_suggest_file(start_fresh)
    f = open(str(csv_file), "a")
    # replace comma in case it message up csv
    message = str(message).replace(',', ';')
    # patterns are uppercase, messages not
    pattern = str(pattern).upper()
    csv_line = f'{pattern},{message}'
    f.write(csv_line + '\n')
    f.close()


def load_suggestions(start_fresh=False):
    csv_file = str(find_suggest_file(start_fresh))
    suggestions = pd.read_csv(csv_file)
    return suggestions


def get_suggestion_for(pattern):
    suggestion = None
    pattern = str(pattern).upper()
    df = load_suggestions()
    row = df.loc[df['pattern'] == pattern]
    if not row.empty:
        suggestion = row['suggestion']
    return suggestion


def get_suggestion_aiml_file(start_fresh=False):
    aiml_file = find_file(name="suggestions", suffix=".aiml", dir_name=LOG_DIR)
    if not aiml_file.exists() or start_fresh:
        new_aiml_file(aiml_file)
    return str(aiml_file)


def new_aiml_file(filepath):
    root = etree.Element("aiml", version="1.0")
    save_xml(root, filepath)


def add_suggestion_aiml(pattern, template, start_fresh=False):
    """ Add a category to aiml file like this
    <category>
        <pattern>WHO IS *</pattern>
        <template><star/> is a bot on Pandorabots.</template>
    </category>
    <category><pattern>WHAT ARE CATEGORY * CLIENTS</pattern>
        <template><srai>What is  IS CATEGORY <star/></srai></template>
    </category>
    """
    aiml_file = get_suggestion_aiml_file(start_fresh)
    aiml = load_xml(aiml_file)
    category = etree.SubElement(aiml, "category")
    pattern = etree.SubElement(category, "pattern").text = pattern
    template = etree.SubElement(category, "template").text = template
    save_xml(aiml, aiml_file)


def save_xml(root, file_path):
    xml_string = xml.dom.minidom.parseString(
        etree.tostring(root, encoding="ISO-8859-1", xml_declaration=True)).toprettyxml()
    xml_string = os.linesep.join([s for s in xml_string.splitlines() if s.strip()])  # remove the weird newline issue
    xml_string = saxutils.unescape(xml_string)
    print(f"Saving XML:\n{xml_string}")
    with open(file_path, "w") as file_out:
        file_out.write(xml_string)


def load_xml(file_path):
    tree = etree.parse(file_path)
    root = tree.getroot()
    return root


def pretty_print_xml_given_file(input_xml, output_xml):
    """
    Useful for when you want to reformat an already existing xml file
    """
    tree = etree.parse(input_xml)
    root = tree.getroot()
    save_xml(root, output_xml)