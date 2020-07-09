import pandas as pd
import random
from util import util
data_file = 'Data/winequality-red.xlsx'

class Subsets:
    def RandomSubSampling(self,iterations=1,tag_index=-1):
        util.cleanTempFolder('Data/Training/')

        reader = pd.read_excel(data_file, header=0)

        columns = reader.columns
        disctint_values = []
        values_counter = []
        total = 0
        for value in reader[columns[tag_index]]:
            total += 1
            if not value in disctint_values:
                disctint_values.append(value)
                values_counter.append(1)
            else:
                values_counter[disctint_values.index(value)] += 1
        #print("Tags Propotionality")
        #for i in range(len(disctint_values)):
        #    print("\tTag:", disctint_values[i], 'count:', values_counter[i], 'percentage:', values_counter[i] * 100 / total)
        #print("\tTotal instances", total)
        training_set_percent = 0.8
        training_set_total_instances = int(total * training_set_percent)
        for i in range(len(values_counter)):
            values_counter[i] = int(values_counter[i] * training_set_total_instances / total)
            #print("\tTag:", disctint_values[i], 'count:', values_counter[i], 'percentage:',
            #      values_counter[i] * 100 / training_set_total_instances)
        training_set_total_instances = sum(values_counter)
        test_set_total_instances = total - training_set_total_instances
        #print("Taining set total instances:", training_set_total_instances)
        #print("Test set total instances:", test_set_total_instances)

        values = reader._get_values
        files=[]
        for i in range(iterations):
            data_training_file = 'Data/Training/training_set'+str(i)+'.xlsx'
            data_testing_file = 'Data/Training/data_testing_set'+str(i)+'.xlsx'
            self.HoldOut(values,training_set_total_instances,test_set_total_instances,total,disctint_values,columns,values_counter,tag_index,data_training_file,data_testing_file,i)
            files.append({'training_file':data_training_file,'testing_file':data_testing_file})
        return files


    def HoldOut(self,values,training_set_total_instances,test_set_total_instances,total,disctint_values,columns,values_counter, tag_index,data_training_file,data_testing_file,iteration=1):
        data_testing = []
        data_training = []
        visited = []
        while training_set_total_instances > 0:
            rand = random.randint(0, total - 1)
            index = disctint_values.index(int(values[rand][tag_index]))
            if not rand in visited and values_counter[index] > 0:
                visited.append(rand)
                data_training.append(values[rand])
                training_set_total_instances -= 1

        while test_set_total_instances > 0:
            rand = random.randint(0, total - 1)
            if not rand in visited:
                visited.append(rand)
                data_testing.append(values[rand])
                test_set_total_instances -= 1

        df = pd.DataFrame(data=data_training, columns=columns)
        df.to_excel(data_training_file, index=False)
        df = pd.DataFrame(data=data_testing, columns=columns)
        df.to_excel(data_testing_file, index=False)


