import pandas as pd
from functools import reduce
from util import util
files = []

spec_power_data_file = 'Data/Classifing/training_set_discretize.xlsx'


class C45:
    folder = 'Data/temp/'
    MINPARENT = 2
    MINLEAF=2

    def __init__(self, file):
        util.cleanTempFolder(self.folder)
        self.leavecount = 0
        self.total_error = 0

        reader = pd.read_excel(file, header=0)
        self.total_instances=len(reader._get_values)
        self.result = self.main(file)

    def shouldStop(self, attribute_summarize, total_instances,columns,stop_child_signal):
        if stop_child_signal==True or columns==1 or attribute_summarize[-1]['total_disctint_values'] == 1 or total_instances <self.MINPARENT:
            return True
        for i in range(len(attribute_summarize) - 1):
            if attribute_summarize[i]['total_disctint_values'] > 1:
                return False
        return True

    def obtainTagIndex(self, tags):
        tagCounter = float('-inf')
        tagIndex = -1
        for ind in range(len(tags)):
            if tags[ind]['count'] > tagCounter:
                tagCounter = tags[ind]['count']
                tagIndex = ind
        return tagIndex

    def obtainClassifyError(self, tags, index):
        count_list = list(map(lambda x: x['count'], tags))
        total = reduce(lambda a, b: a + b, count_list)
        return 1 - tags[index]['count'] / total

    def obtainTotalError(self, tags, index):
        total=0
        for i in range(len(tags)):
            if i!=index:
                total+=tags[i]['count']
        return total

    def main(self, file):
        reader = pd.read_excel(file, header=0)
        columns = reader.columns
        data_csv = reader._get_values
        attribute_summarize = []
        for column in columns:
            attribute_summarize.append(util.obtainMetrics(reader[column], column))

        total_instances = len(data_csv)

        attribute_summarize[-1]['entropy'] = util.fatherEntropy(attribute_summarize[-1]['disctint_values_name'])
        for i in range(len(columns) - 1):
            util.entropyPerValue(reader[columns[i]], reader[columns[-1]], i, attribute_summarize)
        for i in range(len(columns) - 1):
            attribute_summarize[i]['gain_split'] = util.gainSplit(-1, i, attribute_summarize)
        for i in range(len(columns) - 1):
            attribute_summarize[i]['split_info'] = util.splitInfo(-1, i, attribute_summarize)
        for i in range(len(columns) - 1):
            attribute_summarize[i]['gain_ratio'] = util.gainRatio(i, attribute_summarize)

        result = util.rootFinder(self.folder, attribute_summarize, data_csv, columns, self.MINLEAF)

        if self.shouldStop(attribute_summarize, total_instances,len(columns),result['stop']) == True:
            index = self.obtainTagIndex(attribute_summarize[-1]['disctint_values_name'])
            clasifyerror_value = self.obtainClassifyError(attribute_summarize[-1]['disctint_values_name'], index)
            toterror = self.obtainTotalError(attribute_summarize[-1]['disctint_values_name'], index)
            tag = attribute_summarize[-1]['disctint_values_name'][index]['name']
            self.leavecount += 1
            self.total_error += toterror
            return {'tag_name': tag, 'classify_error': clasifyerror_value,'total_error':toterror}

        for i in range(0, len(result['childs'])):
            temp = self.main(result['childs'][i]['file'])
            if not 'classify_error' in temp:
                result['childs'][i]['node'] = temp
            else:
                result['childs'][i]['tag'] = temp
        return result

    # Inicio de metodos auxiliares
    def getTree(self):
        i = 0
        self.getTreeRecursive(self.result, i)

    def getTreeRecursive(self, data, ind):
        if 'name' in data:
            print(('\t' * ind) + data['name'])
        if 'label' in data:
            print(('\t' * (ind + 1)) + data['label'])
        if 'node' in data:
            self.getTreeRecursive(data['node'], ind + 1)
        if 'tag' in data:
            print(('\t' * (ind + 2)) + 'TAG: ' + str(data['tag']['name']))
        if 'childs' in data:
            for obj in data['childs']:
                self.getTreeRecursive(obj, ind + 1)

    def getRules(self):
        string = ""
        self.getRulesRecursive(self.result, string)

    def getRulesRecursive(self, data, string):
        if 'name' in data:
            string = string + ' ' + str(data['name'])
        if 'label' in data:
            string = string + ' ' + data['label']
        if 'node' in data:
            self.getRulesRecursive(data['node'], string)

        if 'tag_name' in data:
            string = string + ' ====>' + str(data['tag_name']) + ' Classify Error: ' +\
                     str(data['classify_error'])+ ' Total Error: ' + str(data['total_error'])
            print(string)
        elif 'tag' in data:
            string = string + ' ====>' + str(data['tag']['tag_name']) + ' Classify Error: ' +\
                     str(data['tag']['classify_error'])+ ' Total Error: ' + str(data['tag']['total_error'])
            print(string)

        if 'childs' in data:
            for obj in data['childs']:
                self.getRulesRecursive(obj, string)

    def trainingError(self):
        return self.total_error/self.total_instances

    def generalizationError(self):
        return self.trainingError()+self.leavecount/self.total_instances
    # Fin de metodos auxiliares


algorithm = C45(spec_power_data_file)
algorithm.getRules()
print("Total of leaves:", algorithm.leavecount)
print('Error de entrenamiento',algorithm.trainingError())
print('Error de generalizacion',algorithm.generalizationError())
