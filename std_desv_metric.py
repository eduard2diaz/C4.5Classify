import pandas as pd
import math
from functools import reduce
import random

files=[]

file_index=0
spec_power_data_file = 'Data/Classifing/training_set_discretize.xlsx'
#spec_power_data_file = 'Data/Classifing/test.xlsx'
folder= 'Data/temp/'

def disctint_values(reader, column):
    disctint_values = []
    values_counter = []
    for value in reader[column]:
        if not value in disctint_values:
            disctint_values.append(value)
            values_counter.append(1)
        else:
            values_counter[disctint_values.index(value)] += 1
    return {'distinct_values':disctint_values,'distinct_count':values_counter}

def obtainMetrics(reader, column,attribute_summarize):
    disctint=disctint_values(reader,column)
    if isinstance(reader[column][0], str):
        print()
        #print("Name:", column, "Disctint:", len(disctint['distinct_values']), 'disctint_values', disctint['distinct_values'])
    else:
        min = float('inf')
        max = float('-inf')
        sum = 0
        counter = 0
        for value in reader[column]:
            sum += float(value)
            if value > max:
                max = value
            if value < min:
                min = value
            counter += 1;
        mean = sum / counter
        sum = 0
        for value in reader[column]:
            sum += ((value - mean) ** 2)
        stddesv = math.sqrt(sum / counter)
       # print("Name:", column, "Min:", min, "Max:", max, "Mean:", mean, "Disctint:", len(disctint['distinct_values']),
       #       'disctint_values', disctint['distinct_values'], "StdDesv", stddesv)

    attribute_summarize.append({
        'name': column,
        'total_disctint_values': len(disctint['distinct_values']),
        'disctint_values_name': list(
            map(lambda x: {'name': disctint['distinct_values'][x], 'count': disctint['distinct_count'][x]}, range(len(disctint['distinct_values']))))
    });

def fatherEntropy(reader, column_index,attribute_summarize):
    disctint_values = attribute_summarize[column_index]['disctint_values_name']
    count_list = list(map(lambda x: x['count'], disctint_values))
    total = reduce(lambda a, b: a + b, count_list)
    sum = 0
    for obj in disctint_values:
        pi = obj['count'] / total
        # print("Value", obj['name'], 'counter', obj['count'], 'probability', pi)
        sum += (pi * math.log2(pi))
    entropy = -1 * sum
    attribute_summarize[column_index]['entropy'] = entropy
    return entropy

def entropyPerValue(reader, column_index,columns,attribute_summarize):
    disctint_values = list(map(lambda x: x['name'], attribute_summarize[column_index]['disctint_values_name']))
    class_values = list(map(lambda x: x['name'], attribute_summarize[-1]['disctint_values_name']))
    mtz = []
    for i in range(len(class_values)):
        mtz.append([0] * len(disctint_values))
    variablefield = reader[columns[column_index]]
    classfield = reader[columns[-1]]
    for i in range(len(variablefield)):
        mtz[class_values.index(classfield[i])][disctint_values.index(variablefield[i])] += 1
    for i in range(len(disctint_values)):
        total = 0
        for j in range(len(class_values)):
            total += mtz[j][i]
        sum = 0
        for j in range(len(class_values)):
            pi = mtz[j][i] / total
            if pi > 0:
                sum += (pi * math.log2(pi))
        attribute_summarize[column_index]['disctint_values_name'][i]['entropy'] = -1 * sum

def gainSplit(reader, father_index, column_index,attribute_summarize):
    disctint_values = attribute_summarize[column_index]['disctint_values_name']
    father_entropy = attribute_summarize[father_index]['entropy']
    count_list = list(map(lambda x: x['count'], attribute_summarize[father_index]['disctint_values_name']))
    total = reduce(lambda a, b: a + b, count_list)
    sum = 0
    for obj in disctint_values:
        sum += (obj['count'] / total * obj['entropy'])
    attribute_summarize[column_index]['gain_split'] = father_entropy - sum

def splitInfo(reader, father_index, column_index,attribute_summarize):
    disctint_values = attribute_summarize[column_index]['disctint_values_name']
    father_entropy = attribute_summarize[father_index]['entropy']
    count_list = list(map(lambda x: x['count'], attribute_summarize[father_index]['disctint_values_name']))
    total = reduce(lambda a, b: a + b, count_list)
    sum = 0
    for obj in disctint_values:
        pi = obj['count'] / total
        if pi > 0:
            sum += (pi * math.log2(pi))
    attribute_summarize[column_index]['split_info'] = -1 * sum

def gainRatio(reader, column_index,attribute_summarize):
    gainsplit = attribute_summarize[column_index]['gain_split']
    splitinfo = attribute_summarize[column_index]['split_info']
    if splitinfo == 0:
        splitinfo = 1
    attribute_summarize[column_index]['gain_ratio'] = gainsplit / splitinfo

def rootFinder(reader,attribute_summarize,data_csv,columns):
    #print("\t\t\tSUMMARIZE")
    max_value=float('-inf')
    max_name=None
    max_index=-1
    for index in range(len(attribute_summarize)-1):
        if attribute_summarize[index]['gain_ratio']>max_value:
            max_value=attribute_summarize[index]['gain_ratio']
            max_name=attribute_summarize[index]['name']
            max_index=index
   # print('Better Attribute:',max_name)
    distinct_values = list(map(lambda x: x['name'], attribute_summarize[max_index]['disctint_values_name']))
    #print(attribute_summarize[max_index])
    result={'name':max_name,'childs':[]}
    for value in distinct_values:
        data=[]
        for obj in data_csv:
            if obj[max_index]==value:
                data.append(obj)

        df = pd.DataFrame(data=data, columns=columns)
        df = df.drop([max_name], axis=1)
        file_path=folder+max_name+'_'+str(value)+str(random.randint(0,300000))+'.xlsx'
        df.to_excel(file_path, index=False)
        result['childs'].append({'label':str(value),'file':file_path})
    return result

def shouldStop(attribute_summarize,total_instances):
    if attribute_summarize[-1]['total_disctint_values']==1 or total_instances<=5:
        return True
    for i in range(len(attribute_summarize)-1):
        if attribute_summarize[i]['total_disctint_values']>1:
            return False
    return True

def obtainTag(tags):
    tagCounter=float('-inf')
    tagName=None
    for obj in tags:
        if obj['count']>tagCounter:
            tagCounter=obj['count']
            tagName=obj['name']
    return tagName

def byGODHELPME(file):
    reader = pd.read_excel(file, header=0)
    columns = reader.columns
    data_csv = reader._get_values
    attribute_summarize = []
    for column in columns:
        obtainMetrics(reader, column,attribute_summarize)

    total_instances=len(data_csv)
    if shouldStop(attribute_summarize,total_instances)==True or len(columns)==1:
        return obtainTag(attribute_summarize[-1]['disctint_values_name'])

    fatherEntropy(reader,-1,attribute_summarize)
    for i in range(len(columns) - 1):
        entropyPerValue(reader, i,columns,attribute_summarize)
    for i in range(len(columns) - 1):
        gainSplit(reader, -1, i,attribute_summarize)
    for i in range(len(columns) - 1):
        splitInfo(reader, -1, i,attribute_summarize)
    for i in range(len(columns) - 1):
        gainRatio(reader, i,attribute_summarize)
    result=rootFinder(reader,attribute_summarize,data_csv,columns)
    for i in range(0,len(result['childs'])):
        temp=byGODHELPME(result['childs'][i]['file'])
        if isinstance(temp,list) or isinstance(temp,dict):
            result['childs'][i]['node']=temp
        else:
            result['childs'][i]['tag'] = temp
    return result

i=0
cadena=""
def dibujarArbol(data,ind,cadena):
    if 'name' in data:
        #print(('\t'*ind)+data['name'])
        cadena=cadena+' '+data['name']
    if 'label' in data:
        #print(('\t'*(ind+1))+data['label'])
        cadena = cadena + ' ' + data['label']
    if 'node' in data:
        dibujarArbol(data['node'],ind+1,cadena)
    if 'tag' in data:
        #print(('\t'*(ind+2))+'TAG: '+str(data['tag']))
        cadena = cadena + ' ====>' + str(data['tag'])
        print(cadena)
    if 'childs' in data:
        for obj in data['childs']:
            dibujarArbol(obj,ind+1,cadena)
result=byGODHELPME(spec_power_data_file)
dibujarArbol(result,i,cadena)
print("Total de hojas", totalHojas)
