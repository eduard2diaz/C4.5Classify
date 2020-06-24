import pandas as pd
import math

spec_power_data_file = 'Data/winequality-red2.xlsx'
reader = pd.read_excel(spec_power_data_file, header=0)
columns = reader.columns
data_csv = reader._get_values

def obtainMetrics(reader, column):
    min = float('inf')
    max = float('-inf')
    sum = 0
    counter = 0
    disctint_values = []
    values_counter = []
    for value in reader[column]:
        sum += float(value)
        if value > max:
            max = value
        if value < min:
            min = value
        counter += 1;
        if not value in disctint_values:
            disctint_values.append(value)
            values_counter.append(1)
        else:
            values_counter[disctint_values.index(value)] += 1
    mean = sum / counter
    sum = 0
    for value in reader[column]:
        sum += ((value - mean) ** 2)
    stddesv = math.sqrt(sum / counter)
    print("Name:", column, "Min:", min, "Max:", max, "Mean:", mean, "Disctint:", len(disctint_values),
          'disctint_values',disctint_values, "StdDesv", stddesv)

    def fatherEntropy(reader, column):
        disctint_values = []
        values_counter = []
        counter = 0
        for value in reader[column]:
            counter += 1;
            if not value in disctint_values:
                disctint_values.append(value)
                values_counter.append(1)
            else:
                values_counter[disctint_values.index(value)] += 1
        sum = 0
        for index in range(len(disctint_values)):
            pi = values_counter[index] / counter
            print("Index", index, "Value", disctint_values[index], 'counter', values_counter[index], 'probability', pi)
            sum += (pi * math.log2(pi))
        return -1 * sum


    for column in columns:
        obtainMetrics(reader, column)
    father_entropy = fatherEntropy(reader, columns[-1])

    # print(columns[:-1])
