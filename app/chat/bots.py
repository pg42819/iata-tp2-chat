import sys
from dataclasses import dataclass
from pathlib import Path

from app.aiml import Kernel
import re

QUIT_PATTERN = re.compile("^\s*([qQ])\s*$")
PROJECT_HOME = Path(__file__).resolve().parent.parent
AIML_ALICE = 'alice'
AIML_STANDARD = 'standard'
AIML_SUGGEST = 'suggestbot'
SUGGEST_BOT_FILE = "suggestions.aiml"
BOT_SPECS = {
    AIML_ALICE : (AIML_ALICE, 'Alice', 'LOAD ALICE'),
    AIML_STANDARD: (AIML_STANDARD, 'Stan', 'LOAD AIML B')
}


all_bots = dict()

def load_bot(aiml_name):
    aiml,name,commands = BOT_SPECS[aiml_name]
    bot = Bot(aiml_name=aiml, name=name, commands=commands)
    return bot


def load_custom_bot(aiml_name, aiml_file_path, name="SuggestBot"):
    bot = Bot(aiml_name=aiml_name, name=name, commands=None, aiml_file=aiml_file_path, custom=True)
    return bot



def init_bots():
    global all_bots
    if not all_bots:
        for spec_name in BOT_SPECS.keys():
            all_bots[spec_name] = load_bot(spec_name)
        all_bots[AIML_SUGGEST] = load_custom_bot(aiml_name=AIML_SUGGEST,
                                                 aiml_file_path=str(data_path(SUGGEST_BOT_FILE)),
                                                 name="SuggestBot")
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


def data_path(aiml_name):
    aiml_file = PROJECT_HOME / 'data' / aiml_name
    if not aiml_file.exists():
        __fail(f"Cannot find the bot dir at {aiml_file}")
    return aiml_file


def brain_path(name):
    brains_dir = PROJECT_HOME / 'saved_brains'
    if not brains_dir.exists():
        brains_dir.mkdir()
    brain_file = brains_dir / f'{name}.brn'
    return brain_file


def load_brain_or_learn(name, kernel, aiml_name, commands, aiml_file=None):
    brain_file = brain_path(name)
    if not brain_file.exists():
        if aiml_file is None:
            # use a builtin aiml bot (alice or standard)
            bot_dir = aiml_path(aiml_name=aiml_name)
            startup_file = bot_dir / "startup.xml"
            if not startup_file.exists():
                __fail(f"Cannot find a learning startup file at {startup_file}")
            else:
                kernel.bootstrap(learnFiles="startup.xml", commands=commands, chdir=bot_dir)
        else:
            # specific file so load it
            kernel.bootstrap(learnFiles=aiml_file, commands=commands)
        kernel.saveBrain(brain_file)
    else:
        kernel.bootstrap(brainFile=brain_file, commands=commands)


def save_brain(name, kernel):
    brain_file = brain_path(name)
    kernel.saveBrain(brain_file)


class Bot:
    """
    Bot class encapsulates anu Aiml BOT for use in the tp2 chat application
    """
    def __init__(self, name, aiml_name, commands, aiml_file=None, verbose=False, custom=False):
        self.verbose = verbose
        self.custom = custom
        self.name = name
        self.aiml_name = aiml_name
        self.kernel = Kernel()
        self.kernel.verbose(verbose)
        print(f"Initializing Kernel for {aiml_name}")
        load_brain_or_learn(name, self.kernel, aiml_name, commands, aiml_file)

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
    bot = load_bot(aiml_name)
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
