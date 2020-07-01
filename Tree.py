class TreeNode:
    def __init__(self, value):
        self.childs =[]
        self.data = value;

    def add(self, val):
        self.childs.append(TreeNode(val))

    def esHoja(self):
        return len(self.childs)==0

    def info(self):
        if 'tag_name' in self.data:
            cadena=str(self.data['tag_name'])+' Classify Error: '+str(self.data['classify_error'])
            return cadena
        return self.data['name']

    def getCantidadHijo(self):
        if self.esHoja():
            return 0
        suma=0
        for obj in self.childs:
            suma +=1+obj.getCantidadHijo()
        return suma

class Tree:
    def __init__(self):
        self.root = None

    def getRoot(self):
        return self.root

    def add(self, val):
        if(self.root == None):
            self.root = TreeNode(val)
        else:
            self.root._add(val)

    def find(self, val):
        if(self.root != None):
            return self._find(val, self.root)
        else:
            return None

    def _find(self, val, node):
        if(val == node.data):
            return node
        elif len(node.childs)==0:
            return None

        for obj in node.childs:
            result=self._find(val, obj)
            if result!=None:
                return result
        return None


    def deleteTree(self):
        # garbage collector will do this for us.
        self.root = None

    def printTree(self):
        if(self.root != None):
            self._printTree(self.root)

    def _printTree(self, node):
        if(node != None):
            print(node.data)
            for obj in node.childs:
                self._printTree(obj)

    def getRules(self):
        cadena=""
        regla=[]
        if(self.root != None):
            self.getRulesAux(self.root,cadena,regla)
        for obj in regla:
            print(obj)
        print(len(regla))

    def getRulesAux(self, node,cadena, regla):
        if(node != None):
            if(node.esHoja()):
                regla.append(cadena+str(node.info()))
            cadena+=str(node.info())
            for i in range(len(node.childs)):

                self.getRulesAux(node.childs[i],cadena+str(node.data['childs'][i]['label']+' '),regla)

    def cantidadHojas(self):
        if self.root==None:
            return 0
        return self.cantidadHojasAux(self.root)

    def cantidadHojasAux(self,nodo):
        if nodo.esHoja():
            return 1
        else:
            sum=0
            for obj in nodo.childs:
                sum+=self.cantidadHojasAux(obj)
        return sum