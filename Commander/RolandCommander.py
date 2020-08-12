# initialize bot commands
def initiate_command_sequence(client):
    client.load_extension("Storyteller")


def check_command(command_input):
    # if command is empty, stop the process, otherwise let it go through
    if command_input:
        return True
    return False

