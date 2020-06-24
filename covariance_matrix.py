import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

data_file = './Data/winequality-red.xlsx'
covariance_matrix_data_file = 'Data/covarianceMatrix.xlsx'
reader = pd.read_excel(data_file, header=0)
columns = reader.columns
# print(reader.tail(8)) retorna las ultimas 8 filas
#Aplicamos a los datos una transformación de normalización de forma que su media sea igual a 0, y su varianza=1
data_csv=reader._get_values
data=pd.DataFrame(data=data_csv,columns=columns)
data=data.drop(['quality'],axis=1)
data = StandardScaler().fit_transform(data)
df=pd.DataFrame(data)#Como ves a la matriz de datos se le calcula la transpuesta
covariance_matrix = df.cov()
"""La covariana es una medida de cuan fuertemente los atributos varian entre si. La covarianza de un
atributo consigo mismo es siempre 1"""
#print("Matriz de covarianza")
#print(covariance_matrix)
df = pd.DataFrame(covariance_matrix)
df.to_excel(covariance_matrix_data_file, index=False)
eigen_values, eigen_vectors = np.linalg.eig(covariance_matrix)
"""Los vectores prpios estan ordenados para que el i-esimo vector propio corresponda
 al i-esimo mayor valor propio"""
print('Autovectores \n%s' %eigen_vectors)
print('\nAutovalores \n%s' %eigen_values)