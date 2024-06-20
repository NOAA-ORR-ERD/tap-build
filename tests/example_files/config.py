"""
Simple file to use for testing the config loader

you can make a yaml file that matches this with:

config = SourceFileLoader("config", "example_files/config.py").load_module()
DATA = {key:val for key,val in vars(config).items() if not key.startswith("_")}
yaml.dump(DATA, open('config.yaml', 'w'))

"""

one_value = 3.1459

a_list_of_strings = ["this", "that", "the_other"]

Seasons = [['AllYear', [1,2,3,4,5,6,7,8,9,10,11,12]],
           ['Summer', [6,7,8,9,10,11]],
           ['Winter', [12,1,2,3,4,5]],
           ]

a_tuple_of_numbers = (3, 4, 5, 6)

