import sys
from dataclasses import dataclass
from pathlib import Path

from app.aiml import Kernel
import re

QUIT_PATTERN = re.compile("^\s*([qQ])\s*$")
PROJECT_HOME = Path(__file__).resolve().parent.parent
AIML_ALICE = 'alice'
AIML_STANDARD = 'standard'
BOT_SPECS = {
    AIML_ALICE : (AIML_ALICE, 'Alice', 'LOAD ALICE'),
    AIML_STANDARD: (AIML_STANDARD, 'Stan', 'LOAD AIML B')
}


all_bots = dict()

def load_bot(aiml_name):
    aiml,name,commands = BOT_SPECS[aiml_name]
    bot = Bot(aiml_name=aiml, name=name, commands=commands)
    return bot


def init_bots():
    if not all_bots:
        for spec_name in BOT_SPECS.keys():
            all_bots[spec_name] = load_bot(spec_name)
        print("Bots initialized", file=sys.stderr)


def get_bot_choices():
    tuples = []
    if all_bots:
        for aiml_name in all_bots.keys():
            bot = all_bots[aiml_name]
            tuples.append((aiml_name, bot.name))
        return tuples
    else:
        __fail("Bots not initialized")


def get_bot(aiml_name):
    if all_bots:
        if aiml_name in all_bots:
            return all_bots[aiml_name]
        else:
            __fail(f"Don't have a bot named {aiml_name}")
    else:
        __fail("Bots not initialized")


def aiml_path(aiml_name):
    bot_dir = PROJECT_HOME / 'aiml' / 'botdata' / aiml_name
    if not bot_dir.exists():
        __fail(f"Cannot find the bot dir at {bot_dir}")
    return bot_dir


def brain_path(name):
    brains_dir = PROJECT_HOME / 'saved_brains'
    if not brains_dir.exists():
        brains_dir.mkdir()
    brain_file = brains_dir / f'{name}.brn'
    return brain_file


def load_brain_or_learn(name, kernel, aiml_name, commands):
    brain_file = brain_path(name)
    if not brain_file.exists():
        bot_dir = aiml_path(aiml_name=aiml_name)
        startup_file = bot_dir / "startup.xml"
        if not startup_file.exists():
            __fail(f"Cannot find a learning startup file at {startup_file}")
        kernel.bootstrap(learnFiles="startup.xml", commands=commands, chdir=bot_dir)
        kernel.saveBrain(brain_file)
    else:
        kernel.bootstrap(brainFile=brain_file, commands=commands)


def save_brain(name, kernel):
    brain_file = brain_path(name)
    kernel.saveBrain(brain_file)


class Bot:
    def __init__(self, name, aiml_name="standard", commands="LOAD AIML B", verbose=False):
        self.verbose = verbose
        self.name = name
        self.aiml_name = aiml_name
        self.kernel = Kernel()
        self.kernel.verbose(verbose)
        print(f"Initializing Kernel for {aiml_name}")
        load_brain_or_learn(name, self.kernel, aiml_name, commands)

    def respond(self, message="askquestion"):
        msg = message.strip()
        response = self.kernel.respond(msg)
        self.__verbose(response)
        return response

    # Tell the bot who it's talking to
    def set_correspondent_name(self, my_name):
        self.kernel.setPredicate('name', my_name)

    def quit(self):
        save_brain(self.aiml_name, self.kernel)



    def __verbose(self, msg, obj=None):
        if self.verbose:
            print(f'{self.name}: {msg}')
            if obj is not None:
                print(obj)


# call from a command line tool
def command_line(aiml_name):
    bot = Bot(aiml_name)
    done = False
    response = 'say something'
    while done is False:
        print(f'{bot.name}: {response}')
        user_input = input('You: ').strip()
        if re.search(QUIT_PATTERN, user_input):
            bot.quit()
            done = True
        else:
            response = bot.respond(user_input)


def __fail(msg, obj=None):
    print(f"FATAL ERROR: {msg}", file=sys.stderr)
    if obj is not None:
        # if isinstance(msg, pd.DataFrame):
        #     print("Dataframe:")
        print(obj, file=sys.stderr)
    sys.exit(2)


def get_all_bots():
    return all_bots