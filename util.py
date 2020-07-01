import os
import math
import pandas as pd
from functools import reduce

file_index = 0

class util:

    def cleanTempFolder(folder):
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # elif os.path.isdir(file_path): shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    def getDistinctValues(data):
        disctint_values = []
        values_counter = []
        for value in data:
            if not value in disctint_values:
                disctint_values.append(value)
                values_counter.append(1)
            else:
                values_counter[disctint_values.index(value)] += 1
        return {'distinct_values': disctint_values, 'distinct_count': values_counter}

    def obtainMetrics(data, column):
        disctint = util.getDistinctValues(data)
        if not isinstance(data[0], str):
            min = float('inf')
            max = float('-inf')
            sum = 0
            counter = 0
            for value in data:
                sum += float(value)
                if value > max:
                    max = value
                if value < min:
                    min = value
                counter += 1;
            mean = sum / counter
            sum = 0
            for value in data:
                sum += ((value - mean) ** 2)
            stddesv = math.sqrt(sum / counter)
        # print("Name:", column, "Min:", min, "Max:", max, "Mean:", mean, "Disctint:", len(disctint['distinct_values']),
        #       'disctint_values', disctint['distinct_values'], "StdDesv", stddesv)

        return {
            'name': column,
            'total_disctint_values': len(disctint['distinct_values']),
            'disctint_values_name': list(
                map(lambda x: {'name': disctint['distinct_values'][x], 'count': disctint['distinct_count'][x]},
                    range(len(disctint['distinct_values']))))
        };

    def fatherEntropy(disctint_values):
        count_list = list(map(lambda x: x['count'], disctint_values))
        total = reduce(lambda a, b: a + b, count_list)
        sum = 0
        for obj in disctint_values:
            pi = obj['count'] / total
            # print("Value", obj['name'], 'counter', obj['count'], 'probability', pi)
            sum += (pi * math.log2(pi))
        entropy = -1 * sum
        return entropy

    def gainRatio(column_index, attribute_summarize):
        gainsplit = attribute_summarize[column_index]['gain_split']
        splitinfo = attribute_summarize[column_index]['split_info']
        if splitinfo == 0:
            splitinfo = 1
        return gainsplit / splitinfo

    def splitInfo(father_index, column_index, attribute_summarize):
        disctint_values = attribute_summarize[column_index]['disctint_values_name']
        father_entropy = attribute_summarize[father_index]['entropy']
        count_list = list(map(lambda x: x['count'], attribute_summarize[father_index]['disctint_values_name']))
        total = reduce(lambda a, b: a + b, count_list)
        sum = 0
        for obj in disctint_values:
            pi = obj['count'] / total
            if pi > 0:
                sum += (pi * math.log2(pi))
        return -1 * sum

    def gainSplit(father_index, column_index, attribute_summarize):
        disctint_values = attribute_summarize[column_index]['disctint_values_name']
        father_entropy = attribute_summarize[father_index]['entropy']
        count_list = list(map(lambda x: x['count'], attribute_summarize[father_index]['disctint_values_name']))
        total = reduce(lambda a, b: a + b, count_list)
        sum = 0
        for obj in disctint_values:
            #print(obj)
            sum += (obj['count'] / total * obj['entropy'])
        return father_entropy - sum

    def rootFinder(folder,attribute_summarize, data_csv, columns,cotaMinima):
        # print("\t\t\tSUMMARIZE")
        max_value = float('-inf')
        max_name = None
        max_index = -1
        for index in range(len(attribute_summarize) - 1):
            if attribute_summarize[index]['gain_ratio'] > max_value:
                max_value = attribute_summarize[index]['gain_ratio']
                max_name = attribute_summarize[index]['name']
                max_index = index
        # print('Better Attribute:',max_name)
        distinct_values = list(map(lambda x: x['name'], attribute_summarize[max_index]['disctint_values_name']))
        # print(attribute_summarize[max_index])
        result = {'name': max_name, 'childs': [],'stop':True}

        for value in distinct_values:
            global file_index
            file_index += 1
            data = []
            for obj in data_csv:
                if obj[max_index] == value:
                    data.append(obj)
            df = pd.DataFrame(data=data, columns=columns)
            df = df.drop([max_name], axis=1)
            file_path = folder + max_name + '_' + str(value) +'_' +str(file_index) + '.xlsx'
            df.to_excel(file_path, index=False)
            result['childs'].append({'label': str(value), 'file': file_path})
        return result

    def entropyPerValue(dataatributo, dataclase, column_index, attribute_summarize):
        disctint_values = list(map(lambda x: x['name'], attribute_summarize[column_index]['disctint_values_name']))
        class_values = list(map(lambda x: str(x['name']), attribute_summarize[-1]['disctint_values_name']))
        mtz = []
        for i in range(len(class_values)):
            mtz.append([0] * len(disctint_values))
        variablefield = dataatributo
        for i in range(len(variablefield)):
            column=disctint_values.index(variablefield[i])
            fila=class_values.index(str(dataclase[i]))
            mtz[fila][column] += 1
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


