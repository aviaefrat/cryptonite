from overrides import overrides

from transformers import AutoTokenizer
from allennlp.training.metrics.metric import Metric

import torch


@Metric.register('t5-tokenizer-em')
class T5TokenizerEM(Metric):

    def __init__(self, tokenizer_name):
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self._correct_count = 0.0
        self._total_count = 0.0

    @overrides
    def __call__(self,
                 predicted_ids: torch.Tensor,
                 gold_ids: torch.Tensor):
        predicted_ids, gold_ids = self.detach_tensors(predicted_ids, gold_ids)

        # make sure the batch sizes are the same size
        batch_size_prediction = predicted_ids.size()[0]
        batch_size_gold = gold_ids.size()[0]
        if batch_size_prediction != batch_size_gold:
            raise ValueError(
                f"unequal batch size. "
                f"gold batch size: {batch_size_gold}, prediction batch size: {batch_size_prediction}"
            )
        for i in range(len(predicted_ids)):
            if torch.equal(predicted_ids[i], gold_ids[i]):
                self._correct_count += 1
            self._total_count += 1

    def get_metric(self, reset: bool = False):
        """
        # Returns

        The accumulated accuracy.
        """
        if self._total_count > 0:
            accuracy = self._correct_count / self._total_count
        else:
            accuracy = 0.0
        if reset:
            self.reset()
        return accuracy

    @overrides
    def reset(self):
        self._correct_count = 0.0
        self._total_count = 0.0
