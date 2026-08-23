import inquirer

def question(message: str):
    questions = [
        inquirer.Text('question', message=message)
    ]
    return inquirer.prompt(questions)["question"]

def menu(options: tuple):
    options_display = []
    for i in options:
        options_display.append(f"{options.index(i)+1}. {i}")
    questions = [
        inquirer.List(
            'selection',
            message = "choose an option",
            choices = options_display
        )
    ]
    choice = int(inquirer.prompt(questions)['selection'][0])
    return choice
