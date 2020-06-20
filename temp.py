import pandas as pd


def text_process_B(mess):

    name_list = ['Data', 'Scientist']
    nopunc = [char for char in mess if char in name_list]

    nopunc = ' '.join(nopunc)

    return nopunc.strip()


list_2 = ['Senior', 'Dat', 'Scientist)', 'Data', 'Scientist']

new = text_process_B(list_2)

print(new)
