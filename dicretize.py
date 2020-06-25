import pandas as pd

spec_power_data_file = 'Data/winequality-red3.xlsx'
spec_power_data_file2 = 'Data/winequality-red4.xlsx'

reader = pd.read_excel(spec_power_data_file, header=0)
columns = reader.columns
data_csv = reader._get_values

def dicretize(reader, column_index):
    variablefield = []
    classfield = []
    for i in reader[columns[column_index]]:
        variablefield.append(i)
    for i in reader[columns[-1]]:
        classfield.append(i)

    for i in range(len(variablefield) - 1):
        for j in range(i + 1, len(variablefield)):
            if variablefield[i] > variablefield[j]:
                aux1 = variablefield[i]
                aux2 = classfield[i]
                variablefield[i] = variablefield[j]
                classfield[i] = classfield[j]
                variablefield[j] = aux1
                classfield[j] = aux2

    antecesor = None
    nuevo = True
    min = float('-inf')
    max_antecesor=float('-inf')
    max = variablefield[0]
    grupos = []
    print(variablefield)
    print(classfield)
    for i in range(1, len(variablefield)):
        if classfield[i] == classfield[i - 1]:
            if variablefield[i] != variablefield[i - 1]:
                max_antecesor = (variablefield[i-1])
            max = (variablefield[i])
        else:
            if variablefield[i] == variablefield[i - 1]:
                max=max_antecesor
            grupos.append({'min': min, 'max': max})
            min=max
            max=variablefield[i]
    if len(grupos)>0:
        grupos.append({'min': grupos[-1]['max'], 'max': float('inf')})
    else:
        grupos.append({'min': float('-inf'), 'max': float('inf')})

    print(grupos)
    data=[]
    for row in reader[columns[column_index]]:
        for grupo in grupos:
            if row > grupo['min'] and row <= grupo['max']:
                data.append(str(grupo['min'])+"-"+str(grupo['max']))

    reader[columns[column_index]] = data
    reader.to_excel(spec_power_data_file2, index=False)

for i in range(len(columns) - 1):
    dicretize(reader, i)