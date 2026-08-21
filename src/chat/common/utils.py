import inquirer

def question(message):
    questions = [
        inquirer.Text('question', message=message)
    ]
    return inquirer.prompt(questions)["question"]

def menu(options: tuple):
    questions = [
        inquirer.List(
            'selection',
            message = "choose an option",
            choices = options
        )
    ]
    choice = int(inquirer.prompt(questions)['selection'][0])
    return choice
