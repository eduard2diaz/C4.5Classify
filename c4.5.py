import pandas as pd
from functools import reduce
from util import util
from Tree import Tree

files = []

spec_power_data_file = 'Data/Classifing/training_set_discretize.xlsx'
test_file = 'Data/Classifing/data_testing_set.xlsx'

class C45:
    folder = 'Data/temp/'

    def __init__(self, file):
        util.cleanTempFolder(self.folder)
        self.tree=Tree()

        reader = pd.read_excel(file, header=0)
        self.total_instances=len(reader._get_values)
        self.result = self.main(file,None)

    def shouldStop(self, attribute_summarize,columns):
        if columns==1 or attribute_summarize[-1]['total_disctint_values'] == 1:
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

    def main(self, file,padreArbol):
        reader = pd.read_excel(file, header=0)
        columns = reader.columns
        data_csv = reader._get_values
        attribute_summarize = []
        for column in columns:
            attribute_summarize.append(util.obtainMetrics(reader[column], column))

        if self.shouldStop(attribute_summarize,len(columns)) == True:
            index = self.obtainTagIndex(attribute_summarize[-1]['disctint_values_name'])
            clasifyerror_value = self.obtainClassifyError(attribute_summarize[-1]['disctint_values_name'], index)
            toterror = self.obtainTotalError(attribute_summarize[-1]['disctint_values_name'], index)
            tag = attribute_summarize[-1]['disctint_values_name'][index]['name']
            nodo={'tag_name': tag, 'classify_error': clasifyerror_value, 'resumen_clases': attribute_summarize[-1]['disctint_values_name']}
            if padreArbol == None:
                self.tree.add(nodo)
            else:
                padreArbol.add(nodo)
        else:
            attribute_summarize[-1]['entropy'] = util.fatherEntropy(attribute_summarize[-1]['disctint_values_name'])
            for i in range(len(columns) - 1):
                util.entropyPerValue(reader[columns[i]], reader[columns[-1]], i, attribute_summarize)
            for i in range(len(columns) - 1):
                attribute_summarize[i]['gain_split'] = util.gainSplit(-1, i, attribute_summarize)
            for i in range(len(columns) - 1):
                attribute_summarize[i]['split_info'] = util.splitInfo(-1, i, attribute_summarize)
            for i in range(len(columns) - 1):
                attribute_summarize[i]['gain_ratio'] = util.gainRatio(i, attribute_summarize)

            result = util.rootFinder(self.folder, attribute_summarize, data_csv, columns)

            if padreArbol==None:
                self.tree.add(result)
            else:
                padreArbol.add(result)
            nodo=self.tree.find(result)
            for i in range(0, len(result['childs'])):
                self.main(result['childs'][i]['file'],nodo)

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

    def trainingError(self):
        return self.errorTotal()/self.total_instances

    def generalizationErrorCalculo(self,error_entrenamiento, cant_hojas):
        return error_entrenamiento + 0.5 * (cant_hojas / self.total_instances)

    def generalizationError(self):
        return self.generalizationErrorCalculo(self.trainingError(),self.getCantidadHojas())

    def getRules(self):
        algorithm.tree.getRules()

    def getCantidadHojas(self):
        return algorithm.tree.cantidadHojas()

    def errorTotal(self,excepcion=None):
        if self.tree.root==None:
            return 0
        return self.errorTotalAux(self.tree.root,excepcion)

    def errorTotalAux(self,nodo,excepcion):
        if nodo == excepcion:
            return 0
        suma = 0
        if nodo.esHoja():
            max=float('-inf')
            for obj in nodo.data['resumen_clases']:
                if obj['count']>max:
                    if max!=float('-inf'):
                        suma+=max
                    max=obj['count']
                else:
                    suma += obj['count']
            return suma

        for hijo in nodo.childs:
            suma+=self.errorTotalAux(hijo,excepcion)
        return suma

    def postPoda(self):
        if self.tree.root!=None and not self.tree.root.esHoja():
            self.postPodaAux(self.tree.root)

    def postPodaAux(self,nodo):
        for hijo in nodo.childs:
            if not hijo.esHoja():
                self.postPodaAux(hijo)
        clases=[]
        valores=[]
        for hijo in nodo.childs:
            if not hijo.esHoja():
                return None
            for tags in hijo.data['resumen_clases']:
                if not tags['name'] in clases:
                    clases.append(tags['name'])
                    valores.append(tags['count'])
                else:
                    id=clases.index(tags['name'])
                    valores[id]+=tags['count']

        suma=0
        max = float('-inf')
        union=[]
        idTag=-1
        for i in range(len(valores)):
            if valores[i] > max:
                if max != float('-inf'):
                    suma += max
                max = valores[i]
                idTag=i
            else:
                suma += valores[i]
            union.append({'name':clases[i],'count':valores[i]})
        tag=clases[idTag]
        error_classificacion=self.obtainClassifyError(union,idTag)
        error_generalizacion=self.generalizationError()
        error_withoutme=self.errorTotal(nodo)
        cant_hijos=nodo.getCantidadHijo()
        nuevo_error=self.generalizationErrorCalculo((error_withoutme+suma)/self.total_instances,self.getCantidadHojas()-cant_hijos)
        if nuevo_error<error_generalizacion:
            nodo.childs.clear()
            nodo.data={'tag_name':tag,'classify_error':error_classificacion,'resumen_clases':union}

    def validationError(self,file,nodo):
        reader = pd.read_excel(file, header=0)
        columns = reader.columns
        columns_list = columns.tolist()
        data_csv = reader._get_values
        total_instances=len(data_csv)
        total_errors=0
        for i in range(total_instances):
            obj=data_csv[i]
            print(obj)
            expected_class=obj[-1]
            prediced_class=self.predictClass(obj,columns_list,nodo)
            if expected_class!=prediced_class:
                total_errors+=1
                print(i+2,"se esperaba",expected_class,'y se recibio', prediced_class)
        print('Total de errores de validacion',total_errors,'('+str(total_instances)+')')
        return total_errors/total_instances

    def predictClass(self,obj,columns, nodo):
        if nodo.esHoja():
            return nodo.data['tag_name']

        name=nodo.data['name']
        indice=columns.index(name)
        value=obj[indice]
        for i in range(len(nodo.data['childs'])):
            label=nodo.data['childs'][i]['label']
            if '>' in label and value>float(label[1:]):
                return self.predictClass(obj,columns,nodo.childs[i])
            elif '<' in label and value <= float(label[2:]):
                return self.predictClass(obj,columns,nodo.childs[i])

    # Fin de metodos auxiliares

algorithm = C45(spec_power_data_file)
print("Antes de la Poda: Total of leaves:", algorithm.getCantidadHojas())
algorithm.postPoda()
#algorithm.getRules()
print("PostPoda: Total of leaves:", algorithm.getCantidadHojas())
print('Error de entrenamiento',algorithm.trainingError())
print('Error de generalizacion',algorithm.generalizationError())
print('Altura',algorithm.tree.altura())
print('Error de validacion', algorithm.validationError(test_file,algorithm.tree.root))



