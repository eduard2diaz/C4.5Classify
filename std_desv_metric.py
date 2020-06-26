import pandas as pd
import math
from functools import reduce

spec_power_data_file = 'Data/Classifing/training_set_discretize.xlsx'

reader = pd.read_excel(spec_power_data_file, header=0)
columns = reader.columns
data_csv = reader._get_values
attribute_summarize = []


def obtainMetrics(reader, column):
    disctint_values = []
    values_counter = []
    for value in reader[column]:
        if not value in disctint_values:
            disctint_values.append(value)
            values_counter.append(1)
        else:
            values_counter[disctint_values.index(value)] += 1
    if isinstance(reader[column][0], str):
        print("Name:", column, "Disctint:", len(disctint_values), 'disctint_values', disctint_values)
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
        print("Name:", column, "Min:", min, "Max:", max, "Mean:", mean, "Disctint:", len(disctint_values),
              'disctint_values', disctint_values, "StdDesv", stddesv)

    attribute_summarize.append({
        'name': column,
        'total_disctint_values': len(disctint_values),
        'disctint_values_name': list(
            map(lambda x: {'name': disctint_values[x], 'count': values_counter[x]}, range(len(disctint_values))))
    });


def fatherEntropy(reader, column_index):
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


def entropyPerValue(reader, column_index):
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


def gainSplit(reader, father_index, column_index):
    disctint_values = attribute_summarize[column_index]['disctint_values_name']
    father_entropy = attribute_summarize[father_index]['entropy']
    count_list = list(map(lambda x: x['count'], attribute_summarize[father_index]['disctint_values_name']))
    total = reduce(lambda a, b: a + b, count_list)
    sum = 0
    for obj in disctint_values:
        sum += (obj['count'] / total * obj['entropy'])
    attribute_summarize[column_index]['gain_split'] = father_entropy - sum


def splitInfo(reader, father_index, column_index):
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


def gainRatio(reader, column_index):
    gainsplit = attribute_summarize[column_index]['gain_split']
    splitinfo = attribute_summarize[column_index]['split_info']
    if splitinfo == 0:
        splitinfo = 1
    attribute_summarize[column_index]['gain_ratio'] = gainsplit / splitinfo

def rootFinder():
    print("\t\t\tSUMMARIZE")
    max_value=float('-inf')
    max_name=None
    for obj in attribute_summarize[:-1]:
        if obj['gain_ratio']>max_value:
            max_name=obj['name']
    print('Better Attribute:',max_name)

for column in columns:
    obtainMetrics(reader, column)
fatherEntropy(reader,-1)
for i in range(len(columns) - 1):
    entropyPerValue(reader, i)
for i in range(len(columns) - 1):
    gainSplit(reader, -1, i)
for i in range(len(columns) - 1):
    splitInfo(reader, -1, i)
for i in range(len(columns) - 1):
    gainRatio(reader, i)

rootFinder()
