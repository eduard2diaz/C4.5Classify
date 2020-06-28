import pandas as pd
from functools import reduce
from util import util
files = []

spec_power_data_file = 'Data/Classifing/training_set_discretize.xlsx'

class C45:
    folder = 'Data/temp/'
    def __init__(self, file):
        util.cleanTempFolder(self.folder)
        self.leavecount = 0
        self.result = self.main(file)

    def shouldStop(self, attribute_summarize, total_instances):
        if attribute_summarize[-1]['total_disctint_values'] == 1 or total_instances <= 5:
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

    def main(self, file):
        reader = pd.read_excel(file, header=0)
        columns = reader.columns
        data_csv = reader._get_values
        attribute_summarize = []
        for column in columns:
            attribute_summarize.append(util.obtainMetrics(reader[column], column))

        total_instances = len(data_csv)
        if self.shouldStop(attribute_summarize, total_instances) == True or len(columns) == 1:
            index = self.obtainTagIndex(attribute_summarize[-1]['disctint_values_name'])
            error = self.obtainClassifyError(attribute_summarize[-1]['disctint_values_name'], index)
            tag = attribute_summarize[-1]['disctint_values_name'][index]['name']
            self.leavecount += 1
            return {'name': tag, 'error': error}

        attribute_summarize[-1]['entropy'] = util.fatherEntropy(attribute_summarize[-1]['disctint_values_name'])
        for i in range(len(columns) - 1):
            util.entropyPerValue(reader[columns[i]],reader[columns[-1]], i, attribute_summarize)
        for i in range(len(columns) - 1):
            attribute_summarize[i]['gain_split']=util.gainSplit(-1, i, attribute_summarize)
        for i in range(len(columns) - 1):
            attribute_summarize[i]['split_info']=util.splitInfo(-1, i, attribute_summarize)
        for i in range(len(columns) - 1):
            attribute_summarize[i]['gain_ratio']=util.gainRatio(i, attribute_summarize)
        result = util.rootFinder(self.folder, attribute_summarize, data_csv, columns)
        for i in range(0, len(result['childs'])):
            temp = self.main(result['childs'][i]['file'])
            if not 'error' in temp:
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
            string = string + ' ' + data['name']
        if 'label' in data:
            string = string + ' ' + data['label']
        if 'node' in data:
            self.getRulesRecursive(data['node'], string)
        if 'tag' in data:
            string = string + ' ====>' + str(data['tag']['name']) + ' Classify Error: ' + str(data['tag']['error'])
            print(string)
        if 'childs' in data:
            for obj in data['childs']:
                self.getRulesRecursive(obj, string)
    # Fin de metodos auxiliares


algorithm = C45(spec_power_data_file)
algorithm.getRules()
print("Total of leaves:", algorithm.leavecount)
