from overrides import overrides
from typing import Dict, Iterable
import json
import pickle

from allennlp.data.dataset_readers import DatasetReader
from allennlp.data.fields import Field, MetadataField, TextField
from allennlp.data.instance import Instance
from allennlp.data.token_indexers.pretrained_transformer_indexer import PretrainedTransformerIndexer
from allennlp.data.tokenizers.pretrained_transformer_tokenizer import PretrainedTransformerTokenizer


@DatasetReader.register('cryptic-crossword')
class CrypticCrosswordReader(DatasetReader):

    def __init__(self,
                 hf_pretrained_tokenizer: str,
                 cache_directory: str = 'data/cache',
                 clue_prefix="cryptic crossword clue: ",
                 ):
        super().__init__(cache_directory=cache_directory)
        self.clue_prefix = clue_prefix
        self.tokenizer = PretrainedTransformerTokenizer(hf_pretrained_tokenizer)
        self.token_indexers = {"tokens": PretrainedTransformerIndexer(hf_pretrained_tokenizer)}

    @overrides
    def _read(self, file_path: str) -> Iterable[Instance]:

        with open(file_path) as jsonl_file:
            dataset_list = list(jsonl_file)

        for example in dataset_list:
            yield self.text_to_instance(json.loads(example))

    def text_to_instance(self, example) -> Instance:

        fields: Dict[str, Field] = {}

        original_clue = example['clue']
        answer = example.get('answer')

        clue = f"{self.clue_prefix}{original_clue}"
        clue_tokens = self.tokenizer.tokenize(clue)
        fields['clue'] = TextField(clue_tokens, self.token_indexers)

        if answer is not None:
            answer_tokens = self.tokenizer.tokenize(answer)
            fields['answer'] = TextField(answer_tokens, self.token_indexers)

        enumeration = example['enumeration']

        publisher = example['publisher']
        crossword_id = example['crossword_id']
        number = example['number']
        orientation = example['orientation']
        id_ = f"{publisher}-{crossword_id}-{number}{orientation}"

        date = example['date']
        quick = example['quick']

        fields['metadata'] = MetadataField({'clue': original_clue,
                                            'answer': answer,
                                            'enumeration': enumeration,
                                            'publisher': publisher,
                                            'date': date,
                                            'quick': quick,
                                            'id': id_
                                            })
        return Instance(fields)

    @overrides
    def _instances_from_cache_file(self, cache_filename: str) -> Iterable[Instance]:
        print('reading instances from', cache_filename)
        with open(cache_filename, 'rb') as cache_file:
            instances = pickle.load(cache_file)
            for instance in instances:
                yield instance

    @overrides
    def _instances_to_cache_file(self, cache_filename, instances) -> None:
        print('writing instance to', cache_filename)
        with open(cache_filename, 'wb') as cache_file:
            pickle.dump(instances, cache_file)
