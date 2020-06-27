import pandas as pd

files = []
files.append({'origin': 'Data/Classifing/training_set.xlsx', 'target': 'Data/Classifing/training_set_discretize.xlsx'})
files.append(
    {'origin': 'Data/Classifing/data_testing_set.xlsx', 'target': 'Data/Classifing/data_testing_set_discretize.xlsx'})


def dicretize(reader, column_index):
    data=[]

    variablefield = reader[columns[column_index]]
    media = sum(variablefield) / len(variablefield)
    for row in reader[columns[column_index]]:
            if row <= media:
                data.append('<=' + str(media))
            else:
                data.append('>' + str(media))
    reader[columns[column_index]] = data            

    """
    variablefield=[]
    classfield=[]
    for i in range(len(data_csv)):
        variablefield.append(data_csv[i][column_index])
        classfield.append(data_csv[i][-1])
    for i in range(len(variablefield)-1):
        for j in range(i+1,len(variablefield)):
            if variablefield[i]>variablefield[j]:
                value1=variablefield[i]
                class1=classfield[i]
                variablefield[i]=variablefield[j]
                classfield[i]=classfield[j]
                variablefield[j]=value1
                classfield[j]=class1

   # for i in range(len(variablefield)):
    #    print(variablefield[i], classfield[i])

    count=1
    i=0
    while i < len(variablefield)-1:
        auxI=i
        j=auxI+1
        distint=False
        while j<len(variablefield) and variablefield[auxI]==variablefield[j]:
            if classfield[auxI]!=classfield[j]:
                distint=True
            j+=1
        i=j
        if distint==True:
            for k in range(auxI,j):
                classfield[k]='c'+str(count)
            count+=1

    min=float('-inf')
    class1=None
    groups=[]
    for i in range(len(classfield)):
        if class1==None:
            class1=classfield[i]
        elif classfield[i]!=class1:
            groups.append({'min':min,'max':variablefield[i-1]})
            class1=classfield[i]
            min=variablefield[i-1]
    groups.append({'min': min, 'max': float('inf')})

    for row in reader[columns[column_index]]:
        for group in groups:
            if row> group['min'] and row <= group['max']:
                data.append('('+str(group['min'])+','+str(group['max'])+']')

    reader[columns[column_index]] = data
        """

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
