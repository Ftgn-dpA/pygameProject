import pickle


with open('../level_data/data', 'rb') as data:
    grid = pickle.load(data)
    print(grid)
