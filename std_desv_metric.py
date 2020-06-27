import pandas as pd
import math
from functools import reduce
import os, shutil

files=[]
file_index=0
leavecount=0
spec_power_data_file = 'Data/Classifing/training_set_discretize.xlsx'
folder= 'Data/temp/'

def cleanTempFolder():
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
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
        global file_index
        file_index+=1
        data=[]
        for obj in data_csv:
            if obj[max_index]==value:
                data.append(obj)

        df = pd.DataFrame(data=data, columns=columns)
        df = df.drop([max_name], axis=1)
        file_path=folder+max_name+'_'+str(value)+str(file_index)+'.xlsx'
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

def obtainTagIndex(tags):
    tagCounter=float('-inf')
    tagIndex=-1
    for ind in range(len(tags)):
        if tags[ind]['count']>tagCounter:
            tagCounter=tags[ind]['count']
            tagIndex=ind
    return tagIndex

def obtainClassifyError(tags,index):
    count_list = list(map(lambda x: x['count'], tags))
    total = reduce(lambda a, b: a + b, count_list)
    return 1 - tags[index]['count'] / total

def byGODHELPME(file):
    reader = pd.read_excel(file, header=0)
    columns = reader.columns
    data_csv = reader._get_values
    attribute_summarize = []
    for column in columns:
        obtainMetrics(reader, column,attribute_summarize)

    total_instances=len(data_csv)
    if shouldStop(attribute_summarize,total_instances)==True or len(columns)==1:
        index=obtainTagIndex(attribute_summarize[-1]['disctint_values_name'])
        error=obtainClassifyError(attribute_summarize[-1]['disctint_values_name'],index)
        tag=attribute_summarize[-1]['disctint_values_name'][index]['name']
        global leavecount
        leavecount+=1
        return {'name':tag,'error':error}

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
        if not 'error' in temp:
            result['childs'][i]['node']=temp
        else:
            result['childs'][i]['tag'] = temp
    return result

def getTree(data):
    i = 0
    getTreeRecursive(data,i)

def getTreeRecursive(data,ind):
    if 'name' in data:
        print(('\t'*ind)+data['name'])
    if 'label' in data:
        print(('\t'*(ind+1))+data['label'])
    if 'node' in data:
        getTreeRecursive(data['node'],ind+1)
    if 'tag' in data:
        print(('\t'*(ind+2))+'TAG: '+str(data['tag']['name']))
    if 'childs' in data:
        for obj in data['childs']:
           getTreeRecursive(obj,ind+1)

def getRules(data):
    string=""
    getRulesRecursive(data,string)

def getRulesRecursive(data,string):
    if 'name' in data:
        string=string+' '+data['name']
    if 'label' in data:
        string = string + ' ' + data['label']
    if 'node' in data:
        getRulesRecursive(data['node'],string)
    if 'tag' in data:
        string = string + ' ====>' + str(data['tag']['name'])+' Classify Error: '+str(data['tag']['error'])
        print(string)
    if 'childs' in data:
        for obj in data['childs']:
            getRulesRecursive(obj,string)

cleanTempFolder()
result=byGODHELPME(spec_power_data_file)
#getRules(result)
print("Total of leaves:",leavecount)