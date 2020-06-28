import pandas as pd
from util import util
import numpy as np

files = []
files.append({'origin': 'Data/Classifing/training_set.xlsx', 'target': 'Data/Classifing/training_set_discretize.xlsx'})
#files.append(
#    {'origin': 'Data/Classifing/data_testing_set.xlsx', 'target': 'Data/Classifing/data_testing_set_discretize.xlsx'})

def auxiliar(variablefield,posibles_puntos_corte):
    aux = []
    for j in range(len(variablefield)):
        if variablefield[j] <= posibles_puntos_corte:
            aux.append('<=' + str(posibles_puntos_corte))
        else:
            aux.append('>' + str(posibles_puntos_corte))
    return aux


def makeCut(reader,data_csv,attribute_summarize,columns, column_index):
    variablefield = []
    classfield = []
    data=[]
    for i in range(len(data_csv)):
        variablefield.append(data_csv[i][column_index])
        classfield.append(data_csv[i][-1])

    #Burblesort
    for i in range(len(variablefield) - 1):
        for j in range(i + 1, len(variablefield)):
            if variablefield[i] > variablefield[j]:
                value1 = variablefield[i]
                class1 = classfield[i]
                variablefield[i] = variablefield[j]
                classfield[i] = classfield[j]
                variablefield[j] = value1
                classfield[j] = class1

    posibles_puntos_corte=[]
    for i in range(len(variablefield) - 1):
        if classfield[i]!=classfield[i+1]:
            cut=(variablefield[i]+variablefield[i+1])/2
            if not cut in posibles_puntos_corte:
                posibles_puntos_corte.append(cut)
                #print('Elemento1',variablefield[i],'Elemento2',variablefield[i+1],cut)

    max_value=float('-inf')
    max_index=-1
    for i in range(len(posibles_puntos_corte)):
        aux=auxiliar(variablefield,posibles_puntos_corte[i])

        union=np.array([
            aux, classfield
        ]).T
        new_columns=['field','class']
        df=pd.DataFrame(data=union,columns=new_columns)
        temp_summarize = []
        for column in new_columns:
            temp_summarize.append(util.obtainMetrics(df[column], column))

        temp_summarize[-1]['entropy'] = util.fatherEntropy(temp_summarize[-1]['disctint_values_name'])
        util.entropyPerValue(aux,classfield, 0, temp_summarize)
        temp_summarize[0]['gain_split']=util.gainSplit(-1, 0, temp_summarize)
        temp_summarize[0]['split_info']=util.splitInfo(-1, 0, temp_summarize)
        temp_summarize[0]['gain_ratio']=util.gainRatio(0, temp_summarize)
        if(temp_summarize[0]['gain_ratio']>max_value):
            max_value=temp_summarize[0]['gain_ratio']
            max_index = i

    #print('Campo',columns[column_index])
    #for obj in posibles_puntos_corte:
    #    print(obj)
    #print('Resultado: indice',max_index,'punto',posibles_puntos_corte[max_index])

    for row in reader[columns[column_index]]:
        if row <= posibles_puntos_corte[max_index]:
            data.append('<=' + str(posibles_puntos_corte[max_index]))
        else:
            data.append('>' + str(posibles_puntos_corte[max_index]))
    reader[columns[column_index]] = data
    """
    METODO 1: utiliza para discretizar la media, lo cual no ser'ia un problema si no existiese
    el riesgo de que dicha discretizaci'on se realice de forma incorrecta si existen en el
    conjunto de datos valores atípicos(Un valor atípico es una observación extrañamente grande
    o pequeña. Los valores atípicos pueden tener un efecto desproporcionado en los resultados
    estadísticos, como la media, lo que puede conducir a interpretaciones engañosas.)
     
    data = []
    variablefield = reader[columns[column_index]]
    media = sum(variablefield) / len(variablefield)
    for row in reader[columns[column_index]]:
            if row <= media:
                data.append('<=' + str(media))
            else:
                data.append('>' + str(media))
    reader[columns[column_index]] = data            
    """

    """
    Metodo 2 divide los rangos de forma tal que posean la misma cantidad de elementos
    factors = reader[columns[column_index]]
    rangos=pd.qcut(factors, 5)
    valores=rangos.value_counts()
    data=[]
    for row in reader[columns[column_index]]:
        for rango in rangos:
            if row in rango:
                data.append(str(rango))
                break

    reader[columns[column_index]] = data
    """

    """
    Metodo 3 divide los rangos de forma tal que posean la misma longitud
    factors = reader[columns[column_index]]
    rangos=pd.cut(factors, 5)
    valores=rangos.value_counts()
    data=[]
    for row in reader[columns[column_index]]:
        for rango in rangos:
            if row in rango:
                data.append(str(rango))
                break

    reader[columns[column_index]] = data
    """

    """
    MÉTODO 4: agrupa los valores sucesivos que pertenecen a un misma clase en una sola etiqueta,
    el unico inconveniente de esto es que al trabajar con datos continuos pueden surgir una 
    considerable cantidad de etiquetas
    
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
    attribute_summarize=[]
    for column in columns:
        attribute_summarize.append(util.obtainMetrics(reader[column],column))
    for i in range(len(columns) - 1):
        makeCut(reader,data_csv,attribute_summarize,columns, i)
    reader.to_excel(obj['target'], index=False)
