import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) # This is your Project Root


def whichslash():
    forward_or_backward = '\\'
    if os.name.find('ix') > -1:
        forward_or_backward = '/'
    return forward_or_backward


def isnixos():
    return os.name.find('ix') > -1


def introoutput():
    print(f"\n\nWelcome to the CSV parser utility for deduping historical events.\n")
    print(f"\n\nYour home path: {os.path.realpath(os.path.expanduser('~'))}\n")
    curr_os = '*NIX' if isnixos() else 'Windows'
    print(f'Looks like you\'re on a {curr_os} operating system. Please add a {whichslash()} to the end of your path.\n')


def userdirectoryinput():
    txt = input("Please type/paste the full file path here: ")
    if os.path.isdir(txt):
        if txt.strip()[-1:] == whichslash():
            return txt
        else:
            return userdirectoryinputerror(f'You forgot the {whichslash()}')
    else:
        return userdirectoryinputerror(f'Invalid directory: {txt}')


def userdirectoryinputerror(issue):
    print(f'\n{issue}\nPlease ensure that the directory path is valid and you have appended a \\ or / to the end.\n')
    return ''


def userfileinput(path):
    onlyfiles = [f for f in os.listdir(path)
                 if os.path.isfile(os.path.join(path, f)) and os.path.splitext(f)[1] == '.csv']
    print('\nValid CSV files in the directory are listed below: ')
    for idx, val in enumerate(onlyfiles):
        print("%d. %s" % (idx, val))
    txt = input(f"\nPlease type the corresponding number(s) to the file(s) you would like to parse. If multiple, sepearate with a comma: ")
    if len(txt.strip()) > 0:
        try:
            files_to_parse = [int(numeric_string) for numeric_string in txt.strip().split(",")]
            [onlyfiles[i] for i in files_to_parse]
            if len(files_to_parse) > 0:
                onlyfiles = [onlyfiles[i] for i in files_to_parse]
                return onlyfiles
        except (ValueError, IndexError, TypeError):
            userfileinputerror('You input an invalid value, try again.', path)
    else:
        userfileinputerror(f'Invalid file: {txt}', path)


def userfileinputerror(issue, path):
    print(f'\n{issue}\n')
    userfileinput(path)


def parsefile(file_path, file_name):
    full_file_path = file_path + file_name
    dfObj = pd.read_csv(full_file_path, delimiter=',', na_values=['no info', '.'])

    # then convert to just a plain old date
    dfObj['ts_new'] = pd.to_datetime(dfObj['ts']).dt.date

    # if these columns don't exist in the csv - I do not gracefully handle that exception
    duplicateRowsDF = dfObj[dfObj.duplicated(['campaign', 'ts_new', 'email'], keep='first')]
    print("There are " + str(len(duplicateRowsDF.index)) + " duplicated rows.")
    if len(duplicateRowsDF.index) > 0:
        txt = input("Do you wish to list all duped rows? [Y/N] ")
        if txt.strip() == "Y" or txt.strip() == "y":
            print("Duplicate Rows except first occurrence based on all columns are :")
            print(duplicateRowsDF[['campaign', 'ts', 'email']].to_string())

        txt = input("Do you want to drop the dupes? [Y/N] ")
        if txt.strip() == "Y" or txt.strip() == "y":
            print("Dropping duplicates...")
            duped = dfObj.drop_duplicates(['campaign', 'ts_new', 'email'], keep='first')
            print(duped.to_string())
            print('Output new deduped file to: ' + file_path + ' as the name: zaius_events_' + file_name)
            duped.to_csv(file_path + 'zaius_events_' + file_name, columns=['campaign', 'ts', 'email', 'action', 'type', 'source'],
                         encoding='utf-8', index=False)
        else:
            print("Not dropping dupes.")
    else:
        print('No dupes, skipping.')

if __name__ == '__main__':
    introoutput()
    file_path = ''
    while file_path == '' or file_path is None:
        file_path = userdirectoryinput()
    files = userfileinput(file_path)
    if len(files) == 1:
        parsefile(file_path, str(files[0]))
    elif len(files) > 1:
        print('parse list of files...')
        for file in files:
            print(f'\nCurrent file: {file}')
            parsefile(file_path, str(file))
    print('No more files to parse! Finished!')
