import pandas as pd

files = []
files.append({'origin': 'Data/Classifing/training_set.xlsx', 'target': 'Data/Classifing/training_set_discretize.xlsx'})
files.append(
    {'origin': 'Data/Classifing/data_testing_set.xlsx', 'target': 'Data/Classifing/data_testing_set_discretize.xlsx'})


def dicretize(reader, column_index):
    variablefield = reader[columns[column_index]]
    data=[]

    media = sum(variablefield) / len(variablefield)
    for row in reader[columns[column_index]]:
            if row <= media:
                data.append('<=' + str(media))
            else:
                data.append('>' + str(media))
    reader[columns[column_index]] = data

for obj in files:
    reader = pd.read_excel(obj['origin'], header=0)
    columns = reader.columns
    data_csv = reader._get_values
    file = pd.DataFrame(data=data_csv, columns=columns)
    file.to_excel(obj['target'], index=False)
    reader = pd.read_excel(obj['target'], header=0)
    for i in range(len(columns) - 1):
        dicretize(reader, i)
    reader.to_excel(obj['target'], index=False)
