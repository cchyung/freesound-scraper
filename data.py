# # code that deals with translating json into rows for the numpy array
import numpy as np
import datetime
import csv

# TODO: place this in its own constant file
MAX_TAGS = 10

# TODO: Add more of these as they pop up
TAGS_TO_IGNORE = {
    'a',
    'the',
    'best',
    'dumb',
    'needs',
    'work',
    'but',
    'made',
    'it',
    'its',
    'start',
    'good',
    'pprojects',
    'think'
}

# provides methods for processing JSON data from freesounds API and keeps it in a stored numpy array
class SampleData:
    def __init__(self):
        self.data_array = np.empty(([0, MAX_TAGS + 2]))


    def __pre_process_tags(self, tags):
        processed_tags = []

        for tag in tags:
            tag = tag.lower()
            tag = tag.replace('-', ' ')   # replace dashes with spaces
            if not tag in TAGS_TO_IGNORE:
                if not tag.isdigit() and not (tag == '808' or tag == '909' or tag == '707'):
                    processed_tags.append(tag)

        return processed_tags
        
    # returns how many samples are in the data array
    def size(self):
        return self.data_array.shape[0]
    
    # loads csv data into a numpy array
    def load_from_csv(self, file_name):
        with open(file_name,'r') as dest_f:
            data_iter = csv.reader(dest_f,
                                delimiter = ',',
                                quotechar = '"')
            data = [data for data in data_iter]
        self.data_array = np.asarray(data)

    # combines from another SampleData object ignoring duplicates
    def combine(self, data):
        self.data_array = np.unique(np.concatenate((self.data_array, data.data_array), axis=0), axis=0)

    def remove_unsuccessful(self, unsuccessful):
        self.data_array = np.delete(self.data_array, unsuccessful, axis=0)

    def remove_duplicates(self):
        self.data_array = np.unique(self.data_array, axis=0)

    # returns number of samples added
    def process_samples(self, results, query, samples_to_extract):
        if results is {}:
            return 0
        for idx, sound_file in enumerate(results):
            sample_id = sound_file['id']
            file_name = str(sample_id) + '.wav'   # generate file name based off query

            # TODO: check if sample id is unique before adding to data set
            
            file_info = np.array([sample_id, file_name], dtype='S128')
            processed_tags = self.__pre_process_tags(sound_file['tags'])
            tags = np.array(processed_tags[:MAX_TAGS])
            
            # break if you have processed enough samples
            if idx == samples_to_extract:
                break
            
            if len(tags) > 0:
                # pad missing tags with empty strings up to MAX_TAGS
                for i in range(MAX_TAGS - tags.shape[0]):
                    tags = np.append(tags, [''])

                features = np.concatenate((file_info, tags))
                self.data_array = np.append(self.data_array, [features], axis=0)
        return idx + 1

    # save csv file containing file name and descriptors
    def save_to_csv(self, file_name):
        file_with_ext = file_name + '.csv'
        print("saving data to file %s" % (file_with_ext, ))
        np.savetxt(file_with_ext, self.data_array, delimiter=",",fmt="%s")

    # save multiple csv files split up into separate files
    def save_to_csv_split(self, file_name, split_num):
        idx = 0
        while (idx)*split_num < self.data_array.shape[0]:
            indexed_file_name = f'%s-%i.csv' % (file_name, idx)
            print('saving data to %s' % (indexed_file_name,))
            i = idx*split_num
            j = (idx + 1)*split_num
            data_to_save = self.data_array[i:j]
            np.savetxt(indexed_file_name, data_to_save, delimiter=",",fmt="%s")
            idx = idx + 1
