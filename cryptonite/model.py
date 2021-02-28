from typing import Dict

import torch

from allennlp.data import Vocabulary
from allennlp.data.fields import MetadataField
from allennlp.models import Model

from transformers import T5ForConditionalGeneration

from cryptonite.metrics import T5TokenizerEM


@Model.register('cryptic-crossword')
class CrypticCrosswordsModel(Model):

    def __init__(self,
                 vocab: Vocabulary,
                 hf_pretrained_model: str
                 ):
        super().__init__(vocab)
        self.hf_pretrained_model = T5ForConditionalGeneration.from_pretrained(hf_pretrained_model)
        self.t5_tokenizer_em = T5TokenizerEM(hf_pretrained_model)
        self.prediction_only = False

    def forward(self,
                clue: Dict[str, Dict[str, torch.Tensor]],
                answer: Dict[str, Dict[str, torch.Tensor]] = None,
                metadata: MetadataField = None) -> Dict[str, torch.Tensor]:
        output_dict = dict()
        clue_ids = clue['tokens']['token_ids']

        if answer is not None:
            answer_ids = answer['tokens']['token_ids']

            if self.training:
                forward_train_result = self.hf_pretrained_model(input_ids=clue_ids, labels=answer_ids)
                loss = forward_train_result['loss']
                logits = forward_train_result['logits']
                output_dict['loss'] = loss
                output_dict['decoder_logits'] = logits

                # metrics
                predicted_ids = torch.argmax(logits, dim=-1)
                self.t5_tokenizer_em(predicted_ids, answer_ids)

            else:
                with torch.no_grad():
                    if not self.prediction_only:
                        forward_val_result = self.hf_pretrained_model(input_ids=clue_ids, labels=answer_ids)
                        loss = forward_val_result['loss']
                        output_dict['loss'] = loss
                        logits = forward_val_result['logits']
                        predicted_ids = torch.argmax(logits, dim=-1)
                        self.t5_tokenizer_em(predicted_ids, answer_ids)

                    else:  # todo check if this logic should be implemented via a predictor class
                        generated_result = self.hf_pretrained_model.generate(input_ids=clue_ids, num_beams=5)

                        output_dict['clue'] = []
                        output_dict['answer'] = []
                        output_dict['prediction'] = []
                        output_dict['enumeration'] = []
                        output_dict['publisher'] = []
                        output_dict['id'] = []

                        for i in range(len(clue_ids)):

                            enumeration = metadata[i]['enumeration']
                            output_dict['clue'].append(metadata[i]['clue'].replace(f" {enumeration}", ""))
                            # todo the above ugliness makes make reconsider not creating the
                            #  enumerated versions in the reader by using a flag.
                            #  see the current `original clue` usage in the reader

                            output_dict['enumeration'].append(enumeration)
                            output_dict['answer'].append(metadata[i]['answer'])

                            prediction = self.t5_tokenizer_em.tokenizer.decode(generated_result[i])
                            prediction = prediction.replace("<pad>", "").lstrip()
                            output_dict['prediction'].append(prediction)

                            output_dict['publisher'].append(metadata[i]['publisher'])
                            output_dict['id'].append(metadata[i]['id'])

        return output_dict

    def get_metrics(self, reset: bool = False) -> Dict[str, float]:
        if self.training:
            return {
                "t5_tokenizer_em": self.t5_tokenizer_em.get_metric(reset)
            }
        else:
            return {
                "t5_tokenizer_em": self.t5_tokenizer_em.get_metric(reset)
            }
