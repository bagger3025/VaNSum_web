from fastNLP.core.instance import Instance
from time import time
from datetime import timedelta
from fastNLP.core.dataset import DataSet

from fastNLP.io.loader import JsonLoader
from fastNLP.io.data_bundle import DataBundle
from fastNLP.io.pipe.pipe import Pipe

class MatchSumLoader(JsonLoader):
    
    def __init__(self, sep_id, pad_id, max_len=180):
        self.fields = {'text_id': 'text_id',
                'candidate_id': 'candidate_id',
                'summary_id': 'summary_id'
                }
        super(MatchSumLoader, self).__init__(fields=self.fields)
        
        self.max_len = max_len
        self.sep_id = [sep_id]
        self.pad_id = pad_id

    def _load(self, data):
        dataset = DataSet()
        for ele in data:
            dat = {key: val for key, val in ele.items() if key in self.fields}
            dataset.append(Instance(**dat))
        return dataset
    
    def load(self, datas):
        
        def truncate_candidate_id(instance, max_len):
            candidate_id = []
            for i in range(len(instance['candidate_id'])):
                if len(instance['candidate_id'][i]) > max_len:
                    cur_id = instance['candidate_id'][i][:(max_len - 1)]
                    cur_id += self.sep_id
                else:
                    cur_id = instance['candidate_id'][i]
                candidate_id.append(cur_id)
            return candidate_id

        print('Start loading datasets !!!')
        start = time()

        # load datasets
        datasets = {}
        for name in datas:
            datasets[name] = self._load(datas[name])
            
            if name == 'train':
                datasets[name].apply(lambda ins: truncate_candidate_id(ins, self.max_len), new_field_name='candidate_id')
            
            # set input and target
            datasets[name].set_input('text_id', 'candidate_id', 'summary_id')
        
            # set padding value
            datasets[name].set_pad_val('text_id', self.pad_id)
            datasets[name].set_pad_val('candidate_id', self.pad_id)
            datasets[name].set_pad_val('summary_id', self.pad_id)
            
        print('Finished in {}'.format(timedelta(seconds=time()-start)))

        return DataBundle(datasets=datasets)

class MatchSumPipe(Pipe):

    def __init__(self, sep_id, pad_id):
        super(MatchSumPipe, self).__init__()
        self.sep_id = sep_id
        self.pad_id = pad_id
        
    def process_from_file(self, datas):
        data_bundle = MatchSumLoader(self.sep_id, self.pad_id).load(datas)
        return data_bundle

