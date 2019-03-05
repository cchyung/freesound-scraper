from data import SampleData

def change_data(data):
    data.remove_duplicates()


d = SampleData()
d.data_array = ([
    ['a', 'b', 'c'],
    ['a', 'b', 'c'],
    ['b', 'c', 'd']
])

change_data(d)

print(d.data_array)
